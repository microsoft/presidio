import { useMemo } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowRight, Shield, Sparkles, Database } from 'lucide-react';
import type { SetupConfig } from '../types';

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

  const handleContinue = () => {
    navigate('/human-review');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">PII Detection Analysis</h2>
        <p className="text-slate-600">
          Automated PII detection engines will run here once implemented.
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

      {/* Side-by-Side Cards — greyed out / coming soon */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* Presidio Processing — not implemented */}
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

        {/* LLM Processing — not implemented */}
        <Card className="p-6 opacity-50 pointer-events-none">
          <div className="space-y-6">
            <div className="flex items-center justify-between">
              <div className="flex items-center gap-2">
                <Sparkles className="size-6 text-slate-400" />
                <div>
                  <h3 className="font-semibold text-slate-400">LLM Judge</h3>
                  <p className="text-sm text-slate-400">AI-assisted entity detection</p>
                </div>
              </div>
              <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">Coming soon</span>
            </div>

            <p className="text-sm text-slate-400">
              Use an LLM to suggest additional PII entities and validate detections. Results will be combined with Presidio output for human review.
            </p>
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
