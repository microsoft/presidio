import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Slider } from '../components/ui/slider';
import { ArrowRight, Layers, Info, RefreshCw, Loader2 } from 'lucide-react';
import { api } from '../lib/api';
import type { SetupConfig } from '../types';

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
  const [loading, setLoading] = useState(false);

  const handleContinue = async () => {
    if (!setupConfig?.datasetId) return;
    setLoading(true);
    try {
      await api.sampling.configure(setupConfig.datasetId, sampleSize);
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

          <div className="p-4 bg-blue-50 rounded-lg border border-blue-200">
            <div className="font-medium text-blue-900 mb-2">Random Sampling</div>
            <div className="text-sm text-blue-800">
              Records are randomly selected using <code className="px-1 py-0.5 bg-blue-100 rounded text-xs">pandas.DataFrame.sample()</code> with a fixed seed for reproducibility.
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
              <span className="font-medium text-blue-900 ml-2">Random (pandas)</span>
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
