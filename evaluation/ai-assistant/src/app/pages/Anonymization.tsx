import { useState, useEffect, useMemo, useCallback, useRef } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowRight, Shield, Brain, CheckCircle, Loader2, AlertTriangle, ChevronLeft, Clock, Hash, Tag, Zap } from 'lucide-react';
import { api } from '../lib/api';
import type { SetupConfig } from '../types';

type EnginePhase = 'waiting' | 'configuring' | 'running' | 'done' | 'error' | 'skipped';

interface EntityTypeSummary {
  type: string;
  count: number;
}

export function Anonymization() {
  const navigate = useNavigate();
  const startedRef = useRef(false);

  const setupConfig = useMemo<SetupConfig | null>(() => {
    try {
      const raw = sessionStorage.getItem('setupConfig');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }, []);

  const [hasFinalEntities, setHasFinalEntities] = useState(setupConfig?.hasFinalEntities ?? false);

  useEffect(() => {
    const dsId = setupConfig?.datasetId;
    if (!dsId) return;
    api.datasets.get(dsId).then((ds: any) => {
      const fresh = ds?.has_final_entities ?? false;
      setHasFinalEntities(fresh);
      if (setupConfig) {
        const updated = { ...setupConfig, hasFinalEntities: fresh };
        sessionStorage.setItem('setupConfig', JSON.stringify(updated));
      }
    }).catch(() => {});
  }, [setupConfig?.datasetId]);

  const runPresidio = setupConfig?.runPresidio ?? false;
  const runLlm = setupConfig?.runLlm ?? false;
  const selectedConfig = setupConfig?.presidioConfigName ?? 'default_spacy';
  const selectedModel = setupConfig?.llmModel ?? 'gpt-5.4';

  // Presidio state
  const [presidioPhase, setPresidioPhase] = useState<EnginePhase>(runPresidio ? 'waiting' : 'skipped');
  const [presidioProgress, setPresidioProgress] = useState(0);
  const [presidioTotal, setPresidioTotal] = useState(0);
  const [presidioError, setPresidioError] = useState<string | null>(null);
  const [presidioEntityCount, setPresidioEntityCount] = useState(0);
  const [presidioElapsedMs, setPresidioElapsedMs] = useState<number | null>(null);
  const [presidioEntityTypes, setPresidioEntityTypes] = useState<EntityTypeSummary[]>([]);

  // LLM state
  const [llmPhase, setLlmPhase] = useState<EnginePhase>(runLlm ? 'waiting' : 'skipped');
  const [llmProgress, setLlmProgress] = useState(0);
  const [llmTotal, setLlmTotal] = useState(0);
  const [llmError, setLlmError] = useState<string | null>(null);
  const [llmEntityCount, setLlmEntityCount] = useState(0);
  const [llmElapsedMs, setLlmElapsedMs] = useState<number | null>(null);
  const [llmEntityTypes, setLlmEntityTypes] = useState<EntityTypeSummary[]>([]);

  // New entity types not in golden set (detected on second config)
  const [newEntityTypes, setNewEntityTypes] = useState<string[]>([]);

  const computeEntityTypes = (results: Record<string, any[]>): EntityTypeSummary[] => {
    const counts: Record<string, number> = {};
    for (const entities of Object.values(results)) {
      for (const ent of entities) {
        const t = ent.entity_type || 'UNKNOWN';
        counts[t] = (counts[t] || 0) + 1;
      }
    }
    return Object.entries(counts)
      .map(([type, count]) => ({ type, count }))
      .sort((a, b) => b.count - a.count);
  };

  // Poll Presidio while configuring or running
  useEffect(() => {
    if (presidioPhase !== 'configuring' && presidioPhase !== 'running') return;
    const interval = setInterval(async () => {
      try {
        const s = await api.presidio.status();
        if (presidioPhase === 'configuring') {
          if (s.configured) {
            const datasetId = setupConfig?.datasetId;
            if (!datasetId) {
              setPresidioError('No dataset selected.');
              setPresidioPhase('error');
              return;
            }
            try {
              const res = await api.presidio.analyze(datasetId);
              setPresidioTotal(res.total);
              setPresidioProgress(0);
              setPresidioPhase('running');
            } catch (err: any) {
              setPresidioError(err.message ?? 'Failed to start Presidio analysis');
              setPresidioPhase('error');
            }
          } else if (s.error) {
            setPresidioError(s.error);
            setPresidioPhase('error');
          }
        } else {
          setPresidioProgress(s.progress);
          setPresidioTotal(s.total);
          if (s.error) {
            setPresidioError(s.error);
            setPresidioPhase('error');
          } else if (!s.running && s.progress >= s.total && s.total > 0) {
            setPresidioEntityCount(s.entity_count);
            setPresidioElapsedMs(s.elapsed_ms ?? null);
            setPresidioPhase('done');
            const dsId = setupConfig?.datasetId;
            if (dsId) api.review.saveConfigResults(dsId).catch(() => {});
            try {
              const results = await api.presidio.results();
              setPresidioEntityTypes(computeEntityTypes(results));
            } catch { /* ignore */ }
          }
        }
      } catch { /* keep polling */ }
    }, 3000);
    return () => clearInterval(interval);
  }, [presidioPhase]);

  // Poll LLM while running
  useEffect(() => {
    if (llmPhase !== 'running') return;
    const interval = setInterval(async () => {
      try {
        const s = await api.llm.status();
        setLlmProgress(s.progress);
        setLlmTotal(s.total);
        if (s.error) {
          setLlmError(s.error);
          setLlmPhase('error');
        } else if (!s.running && s.progress >= s.total && s.total > 0) {
          setLlmEntityCount(s.entity_count);
          setLlmElapsedMs(s.elapsed_ms ?? null);
          setLlmPhase('done');
          try {
            const results = await api.llm.results();
            setLlmEntityTypes(computeEntityTypes(results));
          } catch { /* ignore */ }
        }
      } catch { /* keep polling */ }
    }, 3000);
    return () => clearInterval(interval);
  }, [llmPhase]);

  // Auto-start both engines on mount
  const startEngines = useCallback(async () => {
    if (startedRef.current) return;
    startedRef.current = true;

    if (runPresidio) {
      try {
        // Always start fresh: disconnect any previous session
        await api.presidio.disconnect().catch(() => {});
        setPresidioPhase('configuring');
        const configPath = setupConfig?.presidioConfigPath || undefined;
        await api.presidio.configure(selectedConfig, configPath);
      } catch (err: any) {
        setPresidioError(err.message ?? 'Failed to start Presidio');
        setPresidioPhase('error');
      }
    }

    if (runLlm) {
      try {
        const settings = await api.llm.settings();
        if (!settings.env_ready) {
          setLlmError('Azure OpenAI is not configured. Go back to Setup.');
          setLlmPhase('error');
        } else {
          // Always start fresh: disconnect any previous session
          await api.llm.disconnect().catch(() => {});
          setLlmPhase('configuring');
          try {
            await api.llm.configure(selectedModel);
            const datasetId = setupConfig?.datasetId;
            if (!datasetId) {
              setLlmError('No dataset selected.');
              setLlmPhase('error');
              return;
            }
            const res = await api.llm.analyze(datasetId);
            setLlmTotal(res.total);
            setLlmProgress(0);
            setLlmPhase('running');
          } catch (err: any) {
            setLlmError(err.message ?? 'Failed to start LLM analysis');
            setLlmPhase('error');
          }
        }
      } catch (err: any) {
        setLlmError(err.message ?? 'Failed to connect to LLM');
        setLlmPhase('error');
      }
    }
  }, [runPresidio, runLlm, setupConfig, selectedConfig, selectedModel]);

  useEffect(() => {
    startEngines();
  }, [startEngines]);

  const presidioProgressPct = presidioTotal > 0 ? Math.round((presidioProgress / presidioTotal) * 100) : 0;
  const llmProgressPct = llmTotal > 0 ? Math.round((llmProgress / llmTotal) * 100) : 0;

  const allDone =
    (presidioPhase === 'done' || presidioPhase === 'skipped') &&
    (llmPhase === 'done' || llmPhase === 'skipped');

  const anyRunning =
    presidioPhase === 'waiting' || presidioPhase === 'configuring' || presidioPhase === 'running' ||
    llmPhase === 'waiting' || llmPhase === 'configuring' || llmPhase === 'running';

  // Detect new entity types not present in golden set (second config flow)
  useEffect(() => {
    if (!allDone || !hasFinalEntities) return;
    const dsId = setupConfig?.datasetId;
    if (!dsId) return;
    const analysisTypes = new Set([
      ...presidioEntityTypes.map(e => e.type),
      ...llmEntityTypes.map(e => e.type),
    ]);
    if (analysisTypes.size === 0) return;

    api.datasets.records(dsId).then((records: any[]) => {
      const goldenTypes = new Set<string>();
      for (const rec of records) {
        const finals = rec.final_entities ?? rec.finalEntities ?? [];
        for (const ent of finals) {
          goldenTypes.add(ent.entity_type || ent.type || 'UNKNOWN');
        }
      }
      const newTypes = [...analysisTypes].filter(t => !goldenTypes.has(t));
      setNewEntityTypes(newTypes);
    }).catch(() => {});
  }, [allDone, hasFinalEntities, presidioEntityTypes, llmEntityTypes, setupConfig?.datasetId]);

  const handleContinue = () => {
    navigate('/human-review');
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">PII Detection Analysis</h2>
        <p className="text-slate-600">
          {anyRunning
            ? 'Running PII detection engines on your dataset…'
            : allDone
              ? 'Analysis complete. Review the results below.'
              : 'Preparing analysis…'}
        </p>
      </div>

      {/* Presidio Card */}
      {runPresidio && (
        <Card className="p-6 border-blue-200">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="size-6 text-blue-600" />
                <div>
                  <h3 className="font-semibold text-slate-900">Presidio Analyzer</h3>
                  <p className="text-sm text-slate-500">Config: {selectedConfig}</p>
                </div>
              </div>
              {presidioPhase === 'done' && (
                <span className="flex items-center gap-1 text-xs text-green-700 bg-green-50 px-2 py-1 rounded">
                  <CheckCircle className="size-3" /> Complete
                </span>
              )}
              {presidioPhase === 'error' && (
                <span className="flex items-center gap-1 text-xs text-red-700 bg-red-50 px-2 py-1 rounded">
                  <AlertTriangle className="size-3" /> Error
                </span>
              )}
            </div>

            {(presidioPhase === 'waiting' || presidioPhase === 'configuring') && (
              <div className="space-y-2">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Loader2 className="size-4 animate-spin" />
                  {presidioPhase === 'waiting' ? 'Starting…' : 'Initializing Presidio analyzer…'}
                </div>
                <p className="text-xs text-slate-400">Loading the NLP model — this might take a while on first run.</p>
              </div>
            )}

            {presidioPhase === 'running' && (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm text-slate-600">
                  <span className="flex items-center gap-2">
                    <Loader2 className="size-4 animate-spin" />
                    Analysing records…
                  </span>
                  <span>{presidioProgress} / {presidioTotal}</span>
                </div>
                <Progress value={presidioProgressPct} className="h-2" />
              </div>
            )}

            {presidioPhase === 'error' && presidioError && (
              <Alert className="border-red-200 bg-red-50">
                <AlertTriangle className="size-4 text-red-600" />
                <AlertDescription className="text-sm text-red-800">{presidioError}</AlertDescription>
              </Alert>
            )}

            {presidioPhase === 'done' && (() => {
              const maxTypeCount = presidioEntityTypes.length > 0 ? presidioEntityTypes[0].count : 1;
              const rps = presidioElapsedMs && presidioElapsedMs > 0 ? (presidioTotal / (presidioElapsedMs / 1000)).toFixed(1) : null;
              return (
                <div className="space-y-4">
                  <div className="grid grid-cols-4 gap-3">
                    <div className="bg-blue-50 rounded-lg p-3 text-center">
                      <Hash className="size-4 text-blue-400 mx-auto mb-1" />
                      <p className="text-2xl font-bold text-blue-700">{presidioTotal.toLocaleString()}</p>
                      <p className="text-xs text-blue-500">Records</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3 text-center">
                      <Tag className="size-4 text-blue-400 mx-auto mb-1" />
                      <p className="text-2xl font-bold text-blue-700">{presidioEntityCount.toLocaleString()}</p>
                      <p className="text-xs text-blue-500">Entities</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3 text-center">
                      <Clock className="size-4 text-blue-400 mx-auto mb-1" />
                      <p className="text-2xl font-bold text-blue-700">
                        {presidioElapsedMs != null ? `${(presidioElapsedMs / 1000).toFixed(1)}s` : '—'}
                      </p>
                      <p className="text-xs text-blue-500">Duration</p>
                    </div>
                    <div className="bg-blue-50 rounded-lg p-3 text-center">
                      <Zap className="size-4 text-blue-400 mx-auto mb-1" />
                      <p className="text-2xl font-bold text-blue-700">{rps ?? '—'}</p>
                      <p className="text-xs text-blue-500">Rec / sec</p>
                    </div>
                  </div>
                  {presidioEntityTypes.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-slate-500 mb-2">Entity breakdown</p>
                      <div className="space-y-1.5">
                        {presidioEntityTypes.map(({ type, count }) => (
                          <div key={type} className="flex items-center gap-2 text-xs">
                            <span className="w-28 truncate text-slate-600 font-medium">{type}</span>
                            <div className="flex-1 bg-blue-100 rounded-full h-2 overflow-hidden">
                              <div className="bg-blue-500 h-full rounded-full transition-all" style={{ width: `${(count / maxTypeCount) * 100}%` }} />
                            </div>
                            <span className="w-8 text-right text-slate-500 tabular-nums">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })()}
          </div>
        </Card>
      )}

      {/* LLM Card */}
      {runLlm && (
        <Card className="p-6 border-purple-200">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Brain className="size-6 text-purple-600" />
                <div>
                  <h3 className="font-semibold text-slate-900">Presidio LLM Recognizer</h3>
                  <p className="text-sm text-slate-500">Model: {selectedModel}</p>
                </div>
              </div>
              {llmPhase === 'done' && (
                <span className="flex items-center gap-1 text-xs text-green-700 bg-green-50 px-2 py-1 rounded">
                  <CheckCircle className="size-3" /> Complete
                </span>
              )}
              {llmPhase === 'error' && (
                <span className="flex items-center gap-1 text-xs text-red-700 bg-red-50 px-2 py-1 rounded">
                  <AlertTriangle className="size-3" /> Error
                </span>
              )}
            </div>

            {(llmPhase === 'waiting' || llmPhase === 'configuring') && (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Loader2 className="size-4 animate-spin" />
                {llmPhase === 'waiting' ? 'Starting…' : 'Connecting to Azure OpenAI…'}
              </div>
            )}

            {llmPhase === 'running' && (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm text-slate-600">
                  <span className="flex items-center gap-2">
                    <Loader2 className="size-4 animate-spin" />
                    Analysing records…
                  </span>
                  <span>{llmProgress} / {llmTotal}</span>
                </div>
                <Progress value={llmProgressPct} className="h-2" />
              </div>
            )}

            {llmPhase === 'error' && llmError && (
              <Alert className="border-red-200 bg-red-50">
                <AlertTriangle className="size-4 text-red-600" />
                <AlertDescription className="text-sm text-red-800">{llmError}</AlertDescription>
              </Alert>
            )}

            {llmPhase === 'done' && (() => {
              const maxTypeCount = llmEntityTypes.length > 0 ? llmEntityTypes[0].count : 1;
              const rps = llmElapsedMs && llmElapsedMs > 0 ? (llmTotal / (llmElapsedMs / 1000)).toFixed(1) : null;
              return (
                <div className="space-y-4">
                  <div className="grid grid-cols-4 gap-3">
                    <div className="bg-purple-50 rounded-lg p-3 text-center">
                      <Hash className="size-4 text-purple-400 mx-auto mb-1" />
                      <p className="text-2xl font-bold text-purple-700">{llmTotal.toLocaleString()}</p>
                      <p className="text-xs text-purple-500">Records</p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-3 text-center">
                      <Tag className="size-4 text-purple-400 mx-auto mb-1" />
                      <p className="text-2xl font-bold text-purple-700">{llmEntityCount.toLocaleString()}</p>
                      <p className="text-xs text-purple-500">Entities</p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-3 text-center">
                      <Clock className="size-4 text-purple-400 mx-auto mb-1" />
                      <p className="text-2xl font-bold text-purple-700">
                        {llmElapsedMs != null ? `${(llmElapsedMs / 1000).toFixed(1)}s` : '—'}
                      </p>
                      <p className="text-xs text-purple-500">Duration</p>
                    </div>
                    <div className="bg-purple-50 rounded-lg p-3 text-center">
                      <Zap className="size-4 text-purple-400 mx-auto mb-1" />
                      <p className="text-2xl font-bold text-purple-700">{rps ?? '—'}</p>
                      <p className="text-xs text-purple-500">Rec / sec</p>
                    </div>
                  </div>
                  {llmEntityTypes.length > 0 && (
                    <div>
                      <p className="text-xs font-medium text-slate-500 mb-2">Entity breakdown</p>
                      <div className="space-y-1.5">
                        {llmEntityTypes.map(({ type, count }) => (
                          <div key={type} className="flex items-center gap-2 text-xs">
                            <span className="w-28 truncate text-slate-600 font-medium">{type}</span>
                            <div className="flex-1 bg-purple-100 rounded-full h-2 overflow-hidden">
                              <div className="bg-purple-500 h-full rounded-full transition-all" style={{ width: `${(count / maxTypeCount) * 100}%` }} />
                            </div>
                            <span className="w-8 text-right text-slate-500 tabular-nums">{count}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              );
            })()}
          </div>
        </Card>
      )}

      {/* Actions */}
      <div className="flex flex-col items-end gap-3 pt-4">
        {allDone && hasFinalEntities && (
          <Alert className={`w-full ${newEntityTypes.length > 0 ? 'border-orange-300 bg-orange-50' : 'border-amber-200 bg-amber-50'}`}>
            {newEntityTypes.length > 0 ? (
              <AlertTriangle className="size-4 text-orange-600" />
            ) : (
              <CheckCircle className="size-4 text-amber-600" />
            )}
            <AlertDescription>
              <div className="text-sm text-amber-900">
                {newEntityTypes.length > 0 ? (
                  <>
                    <span className="font-medium">New entity types detected:</span>{' '}
                    <span className="font-mono">{newEntityTypes.join(', ')}</span>.
                    <br />
                    These types were not in your previous golden set. Go to Human Review to resolve them before running evaluation.
                  </>
                ) : (
                  <>
                    <span className="font-medium">Existing reviewed entities found:</span> This dataset already includes human-approved final entities from a previous review.
                    You can go directly to Evaluation to test this configuration against that saved reference set, or go back through Human Review to revise it.
                  </>
                )}
              </div>
            </AlertDescription>
          </Alert>
        )}
        <div className="flex gap-3">
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate('/')}
          >
            <ChevronLeft className="size-4 mr-1" />
            Back
          </Button>
          {allDone && hasFinalEntities && (
            <Button
              size="lg"
              variant={newEntityTypes.length > 0 ? 'default' : 'outline'}
              onClick={handleContinue}
            >
              Continue to Human Review
              <ArrowRight className="size-4 ml-2" />
            </Button>
          )}
          {allDone && hasFinalEntities ? (
            <Button
              size="lg"
              variant={newEntityTypes.length > 0 ? 'outline' : 'default'}
              onClick={() => navigate('/evaluation')}
            >
              Continue to Evaluation
              <ArrowRight className="size-4 ml-2" />
            </Button>
          ) : (
            <Button
              size="lg"
              onClick={handleContinue}
              disabled={!allDone}
            >
              Continue to Human Review
              <ArrowRight className="size-4 ml-2" />
            </Button>
          )}
        </div>
      </div>
    </div>
  );
}
