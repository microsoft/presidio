import { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { ArrowRight, Shield, Sparkles, CheckCircle, Loader2, AlertTriangle, Unplug, Plus, Trash2, ChevronLeft } from 'lucide-react';
import { api } from '../lib/api';
import { FileDropzone } from '../components/FileDropzone';
import type { SetupConfig } from '../types';

type LlmStep = 'loading' | 'env_missing' | 'idle' | 'configuring' | 'configured' | 'running' | 'done' | 'error';
type PresidioStep = 'loading' | 'idle' | 'configuring' | 'configured' | 'running' | 'done' | 'error';

interface ModelChoice {
  id: string;
  label: string;
  provider: string;
}

export function Anonymization() {
  const navigate = useNavigate();

  const setupConfig = useMemo<SetupConfig | null>(() => {
    try {
      const raw = sessionStorage.getItem('setupConfig');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }, []);

  const [hasFinalEntities, setHasFinalEntities] = useState(setupConfig?.hasFinalEntities ?? false);

  // Refresh hasFinalEntities from backend on mount (it may have changed after human review)
  useEffect(() => {
    const dsId = setupConfig?.datasetId;
    if (!dsId) return;
    api.datasets.get(dsId).then((ds: any) => {
      const fresh = ds?.has_final_entities ?? false;
      setHasFinalEntities(fresh);
      // Update sessionStorage so downstream pages see the latest value
      if (setupConfig) {
        const updated = { ...setupConfig, hasFinalEntities: fresh };
        sessionStorage.setItem('setupConfig', JSON.stringify(updated));
      }
    }).catch(() => {});
  }, [setupConfig?.datasetId]);

  const datasetRecordCount = useMemo(() => {
    try {
      const raw = sessionStorage.getItem('datasetRecordCount');
      return raw ? parseInt(raw, 10) : null;
    } catch {
      return null;
    }
  }, []);

  // LLM Judge state
  const [llmStep, setLlmStep] = useState<LlmStep>('loading');
  const [models, setModels] = useState<ModelChoice[]>([]);
  const [selectedModel, setSelectedModel] = useState('gpt-5.4');
  const [llmProgress, setLlmProgress] = useState(0);
  const [llmTotal, setLlmTotal] = useState(0);
  const [llmError, setLlmError] = useState<string | null>(null);
  const [llmEntityCount, setLlmEntityCount] = useState(0);
  const [llmElapsedMs, setLlmElapsedMs] = useState<number | null>(null);

  // Presidio state
  const [presidioStep, setPresidioStep] = useState<PresidioStep>('loading');
  const [presidioProgress, setPresidioProgress] = useState(0);
  const [presidioTotal, setPresidioTotal] = useState(0);
  const [presidioError, setPresidioError] = useState<string | null>(null);
  const [presidioEntityCount, setPresidioEntityCount] = useState(0);
  const [presidioElapsedMs, setPresidioElapsedMs] = useState<number | null>(null);

  // Named configs
  const [savedConfigs, setSavedConfigs] = useState<{ name: string; path: string | null }[]>([]);
  const [selectedConfig, setSelectedConfig] = useState('default_spacy');
  const [showAddConfig, setShowAddConfig] = useState(false);
  const [newConfigName, setNewConfigName] = useState('');
  const [newConfigFile, setNewConfigFile] = useState<File | null>(null);
  const [newConfigPath, setNewConfigPath] = useState('');
  const [newConfigInputMode, setNewConfigInputMode] = useState<'file' | 'path'>('file');
  const [activeConfigName, setActiveConfigName] = useState<string | null>(null);

  // Load models + env status + saved configs on mount
  useEffect(() => {
    Promise.all([api.llm.models(), api.llm.settings(), api.llm.status(), api.presidio.configs()]).then(
      ([modelList, settings, status, configs]) => {
        setModels(modelList);
        setSelectedModel(settings.deployment_name || 'gpt-4o');
        setSavedConfigs(configs);

        if (status.running) {
          setLlmStep('running');
          setLlmProgress(status.progress);
          setLlmTotal(status.total);
        } else if (status.entity_count > 0) {
          setLlmEntityCount(status.entity_count);
          setLlmElapsedMs(status.elapsed_ms ?? null);
          setLlmStep('done');
          setLlmTotal(status.total);
          setLlmProgress(status.total);
        } else if (settings.configured) {
          setLlmStep('configured');
        } else if (!settings.env_ready) {
          setLlmStep('env_missing');
        } else {
          setLlmStep('idle');
        }
      },
    ).catch(() => setLlmStep('env_missing'));
  }, []);

  // Poll LLM progress while running
  useEffect(() => {
    if (llmStep !== 'running') return;
    const interval = setInterval(async () => {
      try {
        const s = await api.llm.status();
        setLlmProgress(s.progress);
        setLlmTotal(s.total);
        if (s.error) {
          setLlmError(s.error);
          setLlmStep('error');
        } else if (!s.running && s.progress >= s.total && s.total > 0) {
          setLlmEntityCount(s.entity_count);
          setLlmElapsedMs(s.elapsed_ms ?? null);
          setLlmStep('done');
        }
      } catch {
        // keep polling
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [llmStep]);

  // Presidio: check status on mount
  useEffect(() => {
    api.presidio.status().then((s) => {
      if (s.config_name) setActiveConfigName(s.config_name);
      if (s.running) {
        setPresidioStep('running');
        setPresidioProgress(s.progress);
        setPresidioTotal(s.total);
      } else if (s.loading) {
        setPresidioStep('configuring');
      } else if (s.configured && s.progress > 0 && s.progress >= s.total && s.total > 0) {
        setPresidioStep('done');
        setPresidioProgress(s.progress);
        setPresidioTotal(s.total);
        setPresidioEntityCount(s.entity_count);
        setPresidioElapsedMs(s.elapsed_ms ?? null);
      } else if (s.configured) {
        setPresidioStep('configured');
      } else if (s.error) {
        setPresidioError(s.error);
        setPresidioStep('error');
      } else {
        setPresidioStep('idle');
      }
    }).catch(() => {
      setPresidioStep('idle');
    });
  }, []);

  // Poll Presidio status while configuring (model loading) or running (analysis)
  useEffect(() => {
    if (presidioStep !== 'running' && presidioStep !== 'configuring') return;
    const interval = setInterval(async () => {
      try {
        const s = await api.presidio.status();
        if (presidioStep === 'configuring') {
          if (s.configured) {
            setPresidioStep('configured');
          } else if (s.error) {
            setPresidioError(s.error);
            setPresidioStep('error');
          }
        } else {
          setPresidioProgress(s.progress);
          setPresidioTotal(s.total);
          if (s.error) {
            setPresidioError(s.error);
            setPresidioStep('error');
          } else if (!s.running && s.progress >= s.total && s.total > 0) {
            setPresidioEntityCount(s.entity_count);
            setPresidioElapsedMs(s.elapsed_ms ?? null);
            setPresidioStep('done');
            // Persist config columns to CSV
            const dsId = setupConfig?.datasetId;
            if (dsId) api.review.saveConfigResults(dsId).catch(() => {});
          }
        }
      } catch {
        // keep polling
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [presidioStep]);

  const handlePresidioConfigure = useCallback(async () => {
    setPresidioStep('configuring');
    setPresidioError(null);
    try {
      const config = savedConfigs.find((c) => c.name === selectedConfig);
      const configPath = config?.path || undefined;
      setActiveConfigName(selectedConfig);
      await api.presidio.configure(selectedConfig, configPath);
      // Backend returns immediately — polling will detect when model is ready
    } catch (err: any) {
      setPresidioError(err.message ?? 'Failed to configure Presidio');
      setPresidioStep('error');
    }
  }, [selectedConfig, savedConfigs]);

  const handlePresidioRun = useCallback(async () => {
    setPresidioError(null);
    const datasetId = setupConfig?.datasetId;
    if (!datasetId) {
      setPresidioError('No dataset selected. Go back to Setup.');
      return;
    }
    try {
      const res = await api.presidio.analyze(datasetId);
      setPresidioTotal(res.total);
      setPresidioProgress(0);
      setPresidioStep('running');
    } catch (err: any) {
      setPresidioError(err.message ?? 'Failed to start analysis');
      setPresidioStep('configured');
    }
  }, [setupConfig]);

  const handlePresidioDisconnect = useCallback(async () => {
    try {
      await api.presidio.disconnect();
      setPresidioStep('idle');
      setPresidioError(null);
      setPresidioProgress(0);
      setPresidioTotal(0);
      setPresidioEntityCount(0);
      setPresidioElapsedMs(null);
      setActiveConfigName(null);
    } catch (err: any) {
      setPresidioError(err.message ?? 'Failed to disconnect');
    }
  }, []);

  const handleConfigure = useCallback(async () => {
    setLlmStep('configuring');
    setLlmError(null);
    try {
      await api.llm.configure(selectedModel);
      setLlmStep('configured');
    } catch (err: any) {
      setLlmError(err.message ?? 'Configuration failed');
      setLlmStep('error');
    }
  }, [selectedModel]);

  const handleRunAnalysis = useCallback(async () => {
    setLlmError(null);
    const datasetId = setupConfig?.datasetId;
    if (!datasetId) {
      setLlmError('No dataset selected. Go back to Setup.');
      return;
    }
    try {
      const res = await api.llm.analyze(datasetId);
      setLlmTotal(res.total);
      setLlmProgress(0);
      setLlmStep('running');
    } catch (err: any) {
      setLlmError(err.message ?? 'Failed to start analysis');
      setLlmStep('configured');
    }
  }, [setupConfig]);

  const handleDisconnect = useCallback(async () => {
    try {
      await api.llm.disconnect();
      setLlmStep('idle');
      setLlmError(null);
      setLlmProgress(0);
      setLlmTotal(0);
      setLlmEntityCount(0);
      setLlmElapsedMs(null);
    } catch (err: any) {
      setLlmError(err.message ?? 'Failed to disconnect');
    }
  }, []);

  const handleSaveConfig = useCallback(async () => {
    const name = newConfigName.trim();
    if (!name) return;
    if (newConfigInputMode === 'file' && !newConfigFile) return;
    if (newConfigInputMode === 'path' && !newConfigPath.trim()) return;
    try {
      let res;
      if (newConfigInputMode === 'path') {
        res = await api.presidio.saveConfig(name, newConfigPath.trim());
      } else {
        res = await api.presidio.uploadConfig(newConfigFile!, name);
      }
      setSavedConfigs(res.configs);
      setSelectedConfig(name);
      setNewConfigName('');
      setNewConfigFile(null);
      setNewConfigPath('');
      setShowAddConfig(false);
    } catch (err: any) {
      setPresidioError(err.message ?? 'Failed to save config');
    }
  }, [newConfigName, newConfigFile, newConfigInputMode, newConfigPath]);

  const handleDeleteConfig = useCallback(async (name: string) => {
    try {
      const res = await api.presidio.deleteConfig(name);
      setSavedConfigs(res.configs);
      if (selectedConfig === name) setSelectedConfig('default_spacy');
    } catch (err: any) {
      setPresidioError(err.message ?? 'Failed to delete config');
    }
  }, [selectedConfig]);

  const handleContinue = () => {
    navigate('/human-review');
  };

  const progressPct = llmTotal > 0 ? Math.round((llmProgress / llmTotal) * 100) : 0;
  const presidioProgressPct = presidioTotal > 0 ? Math.round((presidioProgress / presidioTotal) * 100) : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">PII Detection Analysis</h2>
        <p className="text-slate-600">
          Configure and run PII detection engines to identify entities in your dataset.
        </p>
      </div>

      {/* Side-by-Side Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Presidio Analyzer */}
        <Card className="p-6 border-blue-200">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="size-6 text-blue-600" />
                <div>
                  <h3 className="font-semibold text-slate-900">Presidio Analysis</h3>
                  <p className="text-sm text-slate-500">Rule-based & NLP detection</p>
                </div>
              </div>
              {presidioStep === 'done' && (
                <span className="flex items-center gap-1 text-xs text-green-700 bg-green-50 px-2 py-1 rounded">
                  <CheckCircle className="size-3" /> Complete
                </span>
              )}
              {presidioStep === 'configured' && (
                <span className="flex items-center gap-1 text-xs text-blue-700 bg-blue-50 px-2 py-1 rounded">
                  Ready
                </span>
              )}
            </div>

            {presidioStep === 'loading' && (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Loader2 className="size-4 animate-spin" /> Loading…
              </div>
            )}

            {presidioStep === 'configuring' && (
              <div className="space-y-1">
                <div className="flex items-center gap-2 text-sm text-slate-500">
                  <Loader2 className="size-4 animate-spin" /> Initializing Presidio analyzer…
                </div>
                <p className="text-xs text-slate-400">Loading the NLP model — this might take a while on first run.</p>
              </div>
            )}

            {(presidioStep === 'idle' || presidioStep === 'error') && (
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <Label className="text-xs font-medium">Configuration</Label>
                  <div className="flex gap-2">
                    <Select value={selectedConfig} onValueChange={setSelectedConfig}>
                      <SelectTrigger className="flex-1">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {savedConfigs.map((c) => (
                          <SelectItem key={c.name} value={c.name}>
                            {c.name}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Button size="icon" variant="outline" onClick={() => setShowAddConfig(!showAddConfig)} title="Add new config">
                      <Plus className="size-4" />
                    </Button>
                    {selectedConfig !== 'default_spacy' && (
                      <Button size="icon" variant="outline" onClick={() => handleDeleteConfig(selectedConfig)} title="Delete config">
                        <Trash2 className="size-4" />
                      </Button>
                    )}
                  </div>
                </div>

                {showAddConfig && (
                  <div className="space-y-2 border rounded-md p-3 bg-slate-50">
                    <Label className="text-xs font-medium">New Configuration</Label>
                    <Input
                      placeholder="Config name (e.g. transformer-stanford)"
                      value={newConfigName}
                      onChange={(e) => {
                        const v = e.target.value;
                        if (v === '' || /^[A-Za-z0-9][A-Za-z0-9 _.\-]*$/.test(v)) setNewConfigName(v);
                      }}
                      className="text-sm"
                    />
                    <p className="text-xs text-slate-400">Letters, numbers, hyphens, underscores, and dots only.</p>
                    <div className="flex items-center justify-between mb-1">
                      <Label className="text-xs font-medium">YAML File</Label>
                      <button
                        type="button"
                        className="text-xs text-blue-600 hover:underline"
                        onClick={() => { setNewConfigInputMode(newConfigInputMode === 'file' ? 'path' : 'file'); setNewConfigFile(null); setNewConfigPath(''); }}
                      >
                        {newConfigInputMode === 'file' ? 'Enter file path instead' : 'Upload file instead'}
                      </button>
                    </div>
                    {newConfigInputMode === 'file' ? (
                      <FileDropzone
                        accept=".yml,.yaml"
                        label="Drop YAML config file here or click to browse"
                        onFile={setNewConfigFile}
                      />
                    ) : (
                      <Input
                        placeholder="/path/to/config.yml"
                        value={newConfigPath}
                        onChange={(e) => setNewConfigPath(e.target.value)}
                        className="text-sm"
                      />
                    )}
                    <div className="flex gap-2">
                      <Button size="sm" variant="outline" onClick={() => { setShowAddConfig(false); setNewConfigName(''); setNewConfigFile(null); setNewConfigPath(''); }} className="flex-1">
                        Cancel
                      </Button>
                      <Button size="sm" onClick={handleSaveConfig} disabled={!newConfigName.trim() || (newConfigInputMode === 'file' ? !newConfigFile : !newConfigPath.trim())} className="flex-1">
                        Save Config
                      </Button>
                    </div>
                  </div>
                )}

                {presidioError && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertTriangle className="size-4 text-red-600" />
                    <AlertDescription className="text-sm text-red-800">{presidioError}</AlertDescription>
                  </Alert>
                )}

                <Button
                  size="sm"
                  onClick={handlePresidioConfigure}
                  className="w-full"
                >
                  Initialize Presidio
                </Button>
              </div>
            )}

            {presidioStep === 'configured' && (
              <div className="space-y-3">
                <p className="text-sm text-slate-600">
                  Presidio initialized with <strong>{activeConfigName || 'default config'}</strong>.
                  {datasetRecordCount != null && (
                    <> Will analyse <strong>{datasetRecordCount.toLocaleString()}</strong> records.</>
                  )}
                </p>
                {presidioError && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertTriangle className="size-4 text-red-600" />
                    <AlertDescription className="text-sm text-red-800">{presidioError}</AlertDescription>
                  </Alert>
                )}
                <div className="flex gap-2">
                  <Button size="sm" onClick={handlePresidioRun} className="flex-1">
                    <Shield className="size-4 mr-2" />
                    Run Presidio Analysis
                  </Button>
                  <Button size="sm" variant="outline" onClick={handlePresidioDisconnect}>
                    <Unplug className="size-4 mr-1" />
                    Reset
                  </Button>
                </div>
              </div>
            )}

            {presidioStep === 'running' && (
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

            {presidioStep === 'done' && (
              <div className="space-y-3">
                <p className="text-sm text-green-700">
                  Presidio analysis complete — {presidioTotal} records processed, <strong>{presidioEntityCount.toLocaleString()} entities</strong> detected.
                  {presidioElapsedMs != null && (
                    <span className="ml-1 text-slate-500">
                      Detection time: <strong>{(presidioElapsedMs / 1000).toFixed(2)} seconds</strong>
                    </span>
                  )}
                </p>
                {activeConfigName && (
                  <p className="text-xs text-slate-500">Config: {activeConfigName}</p>
                )}
                <Button size="sm" variant="outline" onClick={handlePresidioDisconnect}>
                  <Unplug className="size-4 mr-1" />
                  Reset & Reconfigure
                </Button>
              </div>
            )}
          </div>
        </Card>

        {/* LLM Judge */}
        <Card className="p-6 border-purple-200">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="size-6 text-purple-600" />
                <div>
                  <h3 className="font-semibold text-slate-900">LLM as a Judge</h3>
                  <p className="text-sm text-slate-500">Azure OpenAI via LangExtract</p>
                </div>
              </div>
              {llmStep === 'done' && (
                <span className="flex items-center gap-1 text-xs text-green-700 bg-green-50 px-2 py-1 rounded">
                  <CheckCircle className="size-3" /> Complete
                </span>
              )}
              {llmStep === 'configured' && (
                <span className="flex items-center gap-1 text-xs text-blue-700 bg-blue-50 px-2 py-1 rounded">
                  Ready
                </span>
              )}
            </div>

            {/* Step: loading */}
            {llmStep === 'loading' && (
              <div className="flex items-center gap-2 text-sm text-slate-500">
                <Loader2 className="size-4 animate-spin" /> Loading configuration…
              </div>
            )}

            {/* Step: .env not configured */}
            {llmStep === 'env_missing' && (
              <Alert className="border-amber-200 bg-amber-50">
                <AlertTriangle className="size-4 text-amber-600" />
                <AlertDescription>
                  <p className="text-sm text-amber-900">
                    <strong>Azure OpenAI endpoint is required.</strong>{' '}
                    Add it to the <code className="bg-amber-100 px-1 rounded text-xs">backend/.env</code> file:
                  </p>
                  <pre className="mt-2 text-xs bg-amber-100/60 rounded p-2 text-amber-900 font-mono">
{`PRESIDIO_EVAL_AZURE_ENDPOINT=https://your-resource.openai.azure.com

# Option A — API key auth:
PRESIDIO_EVAL_AZURE_API_KEY=your-api-key-here

# Option B — leave API key empty to use
# DefaultAzureCredential (managed identity / az login)`}
                  </pre>
                  <p className="text-xs text-amber-700 mt-2">
                    Then restart the backend server. See <code className="bg-amber-100 px-1 rounded">.env.example</code> for reference.
                  </p>
                </AlertDescription>
              </Alert>
            )}

            {/* Step: idle / error — choose deployment and connect */}
            {(llmStep === 'idle' || llmStep === 'error' || llmStep === 'configuring') && (
              <div className="space-y-3">
                <div className="space-y-1.5">
                  <Label htmlFor="deployment-select" className="text-xs font-medium">Model Deployment</Label>
                  <Select value={selectedModel} onValueChange={setSelectedModel} disabled={llmStep === 'configuring'}>
                    <SelectTrigger id="deployment-select">
                      <SelectValue placeholder="Select a model" />
                    </SelectTrigger>
                    <SelectContent>
                      {models.map((m) => (
                        <SelectItem key={m.id} value={m.id}>
                          {m.label} <span className="text-slate-400 ml-1">— {m.provider}</span>
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>

                {llmError && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertTriangle className="size-4 text-red-600" />
                    <AlertDescription className="text-sm text-red-800">{llmError}</AlertDescription>
                  </Alert>
                )}

                <Button
                  size="sm"
                  onClick={handleConfigure}
                  disabled={llmStep === 'configuring'}
                  className="w-full"
                >
                  {llmStep === 'configuring' ? (
                    <><Loader2 className="size-4 mr-2 animate-spin" /> Connecting…</>
                  ) : (
                    'Connect to Azure OpenAI'
                  )}
                </Button>
              </div>
            )}

            {/* Step: configured — ready to run */}
            {llmStep === 'configured' && (
              <div className="space-y-3">
                <p className="text-sm text-slate-600">
                  Connected with <strong>{selectedModel}</strong>.
                  {datasetRecordCount != null && (
                    <> Will analyse <strong>{datasetRecordCount.toLocaleString()}</strong> records from the dataset.</>
                  )}
                </p>
                {llmError && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertTriangle className="size-4 text-red-600" />
                    <AlertDescription className="text-sm text-red-800">{llmError}</AlertDescription>
                  </Alert>
                )}
                <div className="flex gap-2">
                  <Button size="sm" onClick={handleRunAnalysis} className="flex-1">
                    <Sparkles className="size-4 mr-2" />
                    Run LLM Analysis
                  </Button>
                  <Button size="sm" variant="outline" onClick={handleDisconnect}>
                    <Unplug className="size-4 mr-1" />
                    Disconnect
                  </Button>
                </div>
              </div>
            )}

            {/* Step: running */}
            {llmStep === 'running' && (
              <div className="space-y-3">
                <div className="flex items-center justify-between text-sm text-slate-600">
                  <span className="flex items-center gap-2">
                    <Loader2 className="size-4 animate-spin" />
                    Analysing records…
                  </span>
                  <span>{llmProgress} / {llmTotal}</span>
                </div>
                <Progress value={progressPct} className="h-2" />
              </div>
            )}

            {/* Step: complete */}
            {llmStep === 'done' && (
              <div className="space-y-3">
                <p className="text-sm text-green-700">
                  LLM analysis complete — {llmTotal} records processed, <strong>{llmEntityCount.toLocaleString()} entities</strong> detected.
                  {llmElapsedMs != null && (
                    <span className="ml-1 text-slate-500">
                      Detection time: <strong>{(llmElapsedMs / 1000).toFixed(2)} seconds</strong>
                    </span>
                  )}
                </p>
                <p className="text-xs text-slate-500">Model: {selectedModel}</p>
                <Button size="sm" variant="outline" onClick={handleDisconnect}>
                  <Unplug className="size-4 mr-1" />
                  Disconnect & Change Model
                </Button>
              </div>
            )}
          </div>
        </Card>
      </div>

      {/* Actions */}
      <div className="flex flex-col items-end gap-3 pt-4">
        {hasFinalEntities && (
          <Alert className="border-amber-200 bg-amber-50 w-full">
            <CheckCircle className="size-4 text-amber-600" />
            <AlertDescription>
              <div className="text-sm text-amber-900">
                <span className="font-medium">Existing reviewed entities found:</span> This dataset already includes human-approved final entities from a previous review.
                You can go directly to Evaluation to test this configuration against that saved reference set, or go back through Human Review to revise it.
              </div>
            </AlertDescription>
          </Alert>
        )}
        <div className="flex gap-3">
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate('/setup')}
          >
            <ChevronLeft className="size-4 mr-1" />
            Back
          </Button>
          {hasFinalEntities && (
            <Button
              size="lg"
              variant="outline"
              onClick={handleContinue}
            >
              Continue to Human Review
              <ArrowRight className="size-4 ml-2" />
            </Button>
          )}
          {hasFinalEntities ? (
            <Button
              size="lg"
              onClick={() => navigate('/evaluation')}
            >
              Continue to Evaluation
              <ArrowRight className="size-4 ml-2" />
            </Button>
          ) : (
            <Button
              size="lg"
              onClick={handleContinue}
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
