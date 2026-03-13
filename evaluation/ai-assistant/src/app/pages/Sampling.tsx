import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Slider } from '../components/ui/slider';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { ArrowRight, Layers, Info, RefreshCw, Loader2, Shuffle, Ruler, Brain } from 'lucide-react';
import { api } from '../lib/api';
import type { SetupConfig } from '../types';

type SamplingMethod = 'random' | 'length' | 'semantic';

const METHODS: { value: SamplingMethod; label: string; description: string; icon: typeof Shuffle }[] = [
  {
    value: 'random',
    label: 'Random Sampling',
    description: 'Uniformly random selection using pandas with a fixed seed for reproducibility.',
    icon: Shuffle,
  },
  {
    value: 'length',
    label: 'Length-Based Sampling',
    description: 'Stratified by text length (short / medium / long) so every length bucket is represented equally.',
    icon: Ruler,
  },
];

export function Sampling() {
  const navigate = useNavigate();

  const setupConfig = useMemo<SetupConfig | null>(() => {
    try {
      const raw = sessionStorage.getItem('setupConfig');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }, []);

  const datasetRecordCount = useMemo(() => {
    try {
      const raw = sessionStorage.getItem('datasetRecordCount');
      return raw ? parseInt(raw, 10) : 1000;
    } catch {
      return 1000;
    }
  }, []);

  const maxSampleSize = Math.min(datasetRecordCount, 2000);
  const defaultSize = Math.min(Math.round(maxSampleSize * 0.5), maxSampleSize);

  const [sampleSize, setSampleSize] = useState(defaultSize);
  const [samplingMethod, setSamplingMethod] = useState<SamplingMethod>('random');
  const [loading, setLoading] = useState(false);

  const handleContinue = async () => {
    if (!setupConfig?.datasetId) return;
    setLoading(true);
    try {
      const timeout = setTimeout(() => navigate('/anonymization'), 8000);
      await api.sampling.configure(setupConfig.datasetId, sampleSize, samplingMethod);
      clearTimeout(timeout);
      navigate('/anonymization');
    } catch {
      navigate('/anonymization');
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">Sampling Configuration</h2>
        <p className="text-slate-600">
          Configure how many records to sample from your dataset for evaluation.
        </p>
      </div>

      {/* Sample Size */}
      <Card className="p-6">
        <div className="space-y-6">
          <div className="flex items-center gap-2 mb-4">
            <Layers className="size-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900">Sample Size</h3>
          </div>

          <div className="space-y-4">
            <div className="flex items-center justify-between">
              <Label>Number of Records</Label>
              <span className="text-2xl font-semibold text-blue-600">{sampleSize}</span>
            </div>

            <Slider
              value={[sampleSize]}
              onValueChange={(val) => setSampleSize(val[0])}
              min={1}
              max={maxSampleSize}
              step={Math.max(1, Math.round(maxSampleSize / 100))}
              className="py-4"
            />

            <div className="flex justify-between text-sm text-slate-600">
              <span>1 record</span>
              <span>{maxSampleSize.toLocaleString()} records</span>
            </div>
          </div>

          <Alert>
            <Info className="size-4" />
            <AlertDescription>
              <div className="text-sm">
                Larger samples provide more accurate evaluation metrics but require more manual review time. Choose a size that balances statistical confidence with your available review capacity.
              </div>
            </AlertDescription>
          </Alert>
        </div>
      </Card>

      {/* Sampling Method */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <RefreshCw className="size-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900">Sampling Method</h3>
          </div>

          <RadioGroup
            value={samplingMethod}
            onValueChange={(v) => setSamplingMethod(v as SamplingMethod)}
            className="space-y-3"
          >
            {METHODS.map(({ value, label, description, icon: Icon }) => (
              <label
                key={value}
                htmlFor={`method-${value}`}
                className={`flex items-start gap-4 p-4 rounded-lg border cursor-pointer transition-colors ${
                  samplingMethod === value
                    ? 'border-blue-400 bg-blue-50'
                    : 'border-slate-200 hover:border-slate-300'
                }`}
              >
                <RadioGroupItem value={value} id={`method-${value}`} className="mt-1" />
                <div className="flex-1">
                  <div className="flex items-center gap-2">
                    <Icon className={`size-4 ${samplingMethod === value ? 'text-blue-600' : 'text-slate-500'}`} />
                    <span className="font-medium text-slate-900">{label}</span>
                  </div>
                  <p className="text-sm text-slate-600 mt-1">{description}</p>
                </div>
              </label>
            ))}
          </RadioGroup>

          {/* Semantic — coming soon */}
          <div className="flex items-start gap-4 p-4 rounded-lg border border-slate-200 opacity-50 pointer-events-none">
            <div className="size-4 mt-1 rounded-full border border-slate-300" />
            <div className="flex-1">
              <div className="flex items-center gap-2">
                <Brain className="size-4 text-slate-400" />
                <span className="font-medium text-slate-400">Semantic Diversity Sampling</span>
                <span className="text-xs text-slate-400 bg-slate-100 px-2 py-0.5 rounded">Coming soon</span>
              </div>
              <p className="text-sm text-slate-400 mt-1">
                TF-IDF vectorization + greedy max-min distance to maximise topical diversity in the sample.
              </p>
            </div>
          </div>
        </div>
      </Card>

      {/* Iteration Context */}
      <Card className="p-6 bg-slate-50 border-slate-300">
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <Info className="size-5 text-slate-600" />
            <h3 className="font-semibold text-slate-900">Iteration & Comparison</h3>
          </div>
          <div className="text-sm text-slate-700 space-y-2">
            <p>
              Since sampling is an iterative process, each run will be tracked and comparable. You'll be able to:
            </p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li>Compare metrics across different configuration versions</li>
              <li>Review what improved or regressed between runs</li>
              <li>Rollback to previous configurations if needed</li>
              <li>Build a history of tuning decisions for audit purposes</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Summary */}
      <Card className="p-6 border-blue-200 bg-blue-50">
        <div className="space-y-2">
          <div className="font-medium text-blue-900">Sample Summary</div>
          <div className="grid grid-cols-2 gap-4 text-sm">
            <div>
              <span className="text-blue-700">Dataset:</span>
              <span className="font-medium text-blue-900 ml-2">{datasetRecordCount.toLocaleString()} total records</span>
            </div>
            <div>
              <span className="text-blue-700">Sample Size:</span>
              <span className="font-medium text-blue-900 ml-2">{sampleSize} records</span>
            </div>
            <div>
              <span className="text-blue-700">Method:</span>
              <span className="font-medium text-blue-900 ml-2">{METHODS.find(m => m.value === samplingMethod)?.label}</span>
            </div>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4">
        <Button size="lg" onClick={handleContinue} disabled={loading}>
          {loading && <Loader2 className="size-4 mr-2 animate-spin" />}
          Generate Sample & Continue
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
