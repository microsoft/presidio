import { useState, useEffect, useMemo, useCallback } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '../components/ui/select';
import { ArrowRight, Shield, Sparkles, Database, CheckCircle, Loader2, AlertTriangle, Unplug } from 'lucide-react';
import { api } from '../lib/api';
import type { SetupConfig } from '../types';

type LlmStep = 'loading' | 'env_missing' | 'idle' | 'configuring' | 'configured' | 'running' | 'done' | 'error';

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

  const hasDatasetEntities = setupConfig?.hasDatasetEntities ?? false;

  // LLM Judge state
  const [llmStep, setLlmStep] = useState<LlmStep>('loading');
  const [models, setModels] = useState<ModelChoice[]>([]);
  const [selectedModel, setSelectedModel] = useState('gpt-5.4');
  const [llmProgress, setLlmProgress] = useState(0);
  const [llmTotal, setLlmTotal] = useState(0);
  const [llmError, setLlmError] = useState<string | null>(null);

  // Load models + env status on mount
  useEffect(() => {
    Promise.all([api.llm.models(), api.llm.settings(), api.llm.status()]).then(
      ([modelList, settings, status]) => {
        setModels(modelList);
        setSelectedModel(settings.deployment_name || 'gpt-4o');

        if (status.running) {
          setLlmStep('running');
          setLlmProgress(status.progress);
          setLlmTotal(status.total);
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

  // Poll progress while running
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
          setLlmStep('done');
        }
      } catch {
        // keep polling
      }
    }, 1000);
    return () => clearInterval(interval);
  }, [llmStep]);

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
    try {
      const res = await api.llm.analyze();
      setLlmTotal(res.total);
      setLlmProgress(0);
      setLlmStep('running');
    } catch (err: any) {
      setLlmError(err.message ?? 'Failed to start analysis');
      // Stay in configured state so user can retry
      setLlmStep('configured');
    }
  }, []);

  const handleDisconnect = useCallback(async () => {
    try {
      await api.llm.disconnect();
      setLlmStep('idle');
      setLlmError(null);
      setLlmProgress(0);
      setLlmTotal(0);
    } catch (err: any) {
      setLlmError(err.message ?? 'Failed to disconnect');
    }
  }, []);

  const handleContinue = () => {
    navigate('/human-review');
  };

  const progressPct = llmTotal > 0 ? Math.round((llmProgress / llmTotal) * 100) : 0;

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">PII Detection Analysis</h2>
        <p className="text-slate-600">
          Configure and run PII detection engines. The LLM Judge uses Azure OpenAI via LangExtract to identify entities.
        </p>
      </div>

      {/* Dataset entities notice */}
      {hasDatasetEntities && (
        <Alert className="border-green-200 bg-green-50">
          <Database className="size-4 text-green-600" />
          <AlertDescription>
            <div className="space-y-1">
              <div className="font-medium text-green-900">Dataset Entities Available</div>
              <div className="text-sm text-green-800">
                Pre-identified entities from the uploaded dataset will be included in the human review step.
              </div>
            </div>
          </AlertDescription>
        </Alert>
      )}

      {/* Side-by-Side Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Presidio Processing — coming soon */}
        <Card className="p-6 opacity-50 pointer-events-none">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Shield className="size-6 text-slate-400" />
                <div>
                  <h3 className="font-semibold text-slate-400">Presidio Analysis</h3>
                  <p className="text-sm text-slate-400">Baseline PII detection</p>
                </div>
              </div>
              <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">Coming soon</span>
            </div>
            <p className="text-sm text-slate-400">
              Run Presidio's rule-based and NLP detection to identify PII entities with precise character spans and confidence scores.
            </p>
          </div>
        </Card>

        {/* LLM Judge — active */}
        <Card className="p-6 border-purple-200">
          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="size-6 text-purple-600" />
                <div>
                  <h3 className="font-semibold text-slate-900">LLM Judge</h3>
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
                  LLM analysis complete — {llmTotal} records processed with <strong>{selectedModel}</strong>.
                </p>
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
      <div className="flex justify-end gap-3 pt-4">
        <Button
          size="lg"
          onClick={handleContinue}
        >
          Continue to Human Review
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
