import { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowRight, Loader2, CheckCircle, Shield, Sparkles, AlertTriangle, Database } from 'lucide-react';
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

  const runPresidio = setupConfig?.runPresidio ?? true;
  const runLlm = setupConfig?.runLlm ?? true;
  const hasDatasetEntities = setupConfig?.hasDatasetEntities ?? false;

  const [presidioProgress, setPresidioProgress] = useState(runPresidio ? 0 : 100);
  const [llmProgress, setLlmProgress] = useState(runLlm ? 0 : 100);
  const [presidioComplete, setPresidioComplete] = useState(!runPresidio);
  const [llmComplete, setLlmComplete] = useState(!runLlm);

  const isComplete = presidioComplete && llmComplete;

  useEffect(() => {
    if (!runPresidio && !runLlm) return; // nothing to simulate

    if (runPresidio) {
      const presidioInterval = setInterval(() => {
        setPresidioProgress((prev) => {
          if (prev >= 100) {
            clearInterval(presidioInterval);
            setPresidioComplete(true);
            return 100;
          }
          return prev + 2;
        });
      }, 50);
      return () => clearInterval(presidioInterval);
    }
  }, [runPresidio]);

  useEffect(() => {
    if (!runLlm) return;
    const timer = setTimeout(() => {
      const llmInterval = setInterval(() => {
        setLlmProgress((prev) => {
          if (prev >= 100) {
            clearInterval(llmInterval);
            setLlmComplete(true);
            return 100;
          }
          return prev + 1.5;
        });
      }, 80);
    }, runPresidio ? 500 : 0);
    return () => clearTimeout(timer);
  }, [runLlm, runPresidio]);

  const handleContinue = () => {
    navigate('/human-review');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">PII Detection Analysis</h2>
        <p className="text-slate-600">
          {runPresidio && runLlm
            ? 'Running Presidio and LLM analysis in parallel to detect PII entities across sampled records.'
            : runPresidio
              ? 'Running Presidio analysis to detect PII entities across sampled records.'
              : runLlm
                ? 'Running LLM analysis to detect PII entities across sampled records.'
                : 'Using dataset-provided entities. No additional detection selected.'}
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

      {/* Important Notice */}
      {runLlm && (
      <Alert className="border-amber-200 bg-amber-50">
        <AlertTriangle className="size-4 text-amber-600" />
        <AlertDescription>
          <div className="space-y-1">
            <div className="font-medium text-amber-900">LLM is Assistive Only</div>
            <div className="text-sm text-amber-800">
              The AI Judge may miss entities or lack exact character spans. Its suggestions will be 
              combined with Presidio results for human review - it does not have final authority.
            </div>
          </div>
        </AlertDescription>
      </Alert>
      )}

      {/* Side-by-Side Processing */}
      {(runPresidio || runLlm) ? (
      <div className={`grid grid-cols-1 ${runPresidio && runLlm ? 'md:grid-cols-2' : ''} gap-6`}>
        {/* Presidio Processing */}
        {runPresidio && (
        <Card className="p-6">
          <div className="space-y-6">
            <div className="flex items-center gap-2">
              <Shield className="size-6 text-blue-600" />
              <div>
                <h3 className="font-semibold text-slate-900">Presidio Anonymization</h3>
                <p className="text-sm text-slate-600">Baseline configuration v1.2</p>
              </div>
            </div>

            <div className="flex items-center justify-center py-8">
              {!presidioComplete ? (
                <Loader2 className="size-16 text-blue-600 animate-spin" />
              ) : (
                <CheckCircle className="size-16 text-green-600" />
              )}
            </div>

            <div className="text-center space-y-2">
              <p className="font-medium text-slate-900">
                {!presidioComplete ? 'Processing Records...' : 'Complete'}
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm text-slate-600">
                <span>Progress</span>
                <span>{presidioProgress}%</span>
              </div>
              <Progress value={presidioProgress} className="h-3" />
            </div>

            {presidioComplete && (
              <div className="space-y-3 pt-4 border-t">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-xl font-semibold text-blue-900">500</div>
                    <div className="text-xs text-blue-700">Records</div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-xl font-semibold text-blue-900">1,247</div>
                    <div className="text-xs text-blue-700">Entities</div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-xl font-semibold text-blue-900">12</div>
                    <div className="text-xs text-blue-700">Types</div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded-lg">
                    <div className="text-xl font-semibold text-blue-900">91%</div>
                    <div className="text-xs text-blue-700">Avg. Conf.</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>
        )}

        {/* LLM Processing */}
        {runLlm && (
        <Card className="p-6">
          <div className="space-y-6">
            <div className="flex items-center gap-2">
              <Sparkles className="size-6 text-purple-600" />
              <div>
                <h3 className="font-semibold text-slate-900">LLM-based PII Judging</h3>
                <p className="text-sm text-slate-600">Azure OpenAI - GPT-4</p>
              </div>
            </div>

            <div className="flex items-center justify-center py-8">
              {!llmComplete ? (
                <Loader2 className="size-16 text-purple-600 animate-spin" />
              ) : (
                <CheckCircle className="size-16 text-green-600" />
              )}
            </div>

            <div className="text-center space-y-2">
              <p className="font-medium text-slate-900">
                {!llmComplete ? 'AI Judge Analyzing...' : 'Complete'}
              </p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm text-slate-600">
                <span>Progress</span>
                <span>{llmProgress}%</span>
              </div>
              <Progress value={llmProgress} className="h-3" />
            </div>

            {llmComplete && (
              <div className="space-y-3 pt-4 border-t">
                <div className="grid grid-cols-2 gap-3">
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <div className="text-xl font-semibold text-purple-900">500</div>
                    <div className="text-xs text-purple-700">Records</div>
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <div className="text-xl font-semibold text-purple-900">1,312</div>
                    <div className="text-xs text-purple-700">Entities</div>
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <div className="text-xl font-semibold text-purple-900">65</div>
                    <div className="text-xs text-purple-700">Additional</div>
                  </div>
                  <div className="p-3 bg-purple-50 rounded-lg">
                    <div className="text-xl font-semibold text-purple-900">87%</div>
                    <div className="text-xs text-purple-700">Avg. Conf.</div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </Card>
        )}
      </div>
      ) : (
        <Card className="p-6 border-green-200 bg-green-50">
          <div className="flex items-center gap-3">
            <CheckCircle className="size-6 text-green-600" />
            <div>
              <h3 className="font-semibold text-green-900">No additional detection needed</h3>
              <p className="text-sm text-green-800 mt-1">
                Proceeding with dataset-provided entities only. Continue to human review.
              </p>
            </div>
          </div>
        </Card>
      )}

      {/* Combined Results */}
      {isComplete && (
        <>
          <Card className="p-6 border-green-200 bg-green-50">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="size-5 text-green-700" />
                <h3 className="font-semibold text-green-900">Analysis Complete - Ready for Human Review</h3>
              </div>

              <div className="space-y-2">
                <div className="text-sm font-medium text-green-900">Comparison Summary:</div>
                <div className="flex flex-wrap gap-2">
                  <Badge variant="outline" className="bg-white text-green-800 border-green-300">
                    ✓ 1,182 Matches
                  </Badge>
                  <Badge variant="outline" className="bg-amber-50 text-amber-800 border-amber-300">
                    ⚠ 47 Conflicts
                  </Badge>
                  <Badge variant="outline" className="bg-blue-50 text-blue-800 border-blue-300">
                    + 65 LLM-only
                  </Badge>
                  <Badge variant="outline" className="bg-purple-50 text-purple-800 border-purple-300">
                    − 18 Presidio-only
                  </Badge>
                </div>
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900">Detected Entity Types</h3>
              <div className="flex flex-wrap gap-2">
                {['PERSON', 'EMAIL', 'PHONE_NUMBER', 'SSN', 'CREDIT_CARD', 'DATE_OF_BIRTH', 
                  'MEDICAL_RECORD', 'IP_ADDRESS', 'EMPLOYEE_ID', 'ADDRESS', 'ORGANIZATION', 'DATE'].map(type => (
                  <Badge key={type} variant="secondary" className="bg-slate-100 text-slate-800">
                    {type}
                  </Badge>
                ))}
              </div>
            </div>
          </Card>

          <Card className="p-6">
            <div className="space-y-3">
              <h3 className="font-semibold text-slate-900">Output Generated</h3>
              <div className="grid md:grid-cols-2 gap-4 text-sm text-slate-700">
                <div className="space-y-2">
                  <div className="font-medium text-slate-900">Presidio Output:</div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="size-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <div>Detected entities with precise character positions</div>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="size-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <div>Anonymized text with PII replaced</div>
                  </div>
                  <div className="flex items-start gap-2">
                    <CheckCircle className="size-4 text-green-600 mt-0.5 flex-shrink-0" />
                    <div>Confidence scores for each detection</div>
                  </div>
                </div>
                <div className="space-y-2">
                  <div className="font-medium text-slate-900">LLM Output:</div>
                  <div className="flex items-start gap-2">
                    <Sparkles className="size-4 text-purple-600 mt-0.5 flex-shrink-0" />
                    <div>Suggested entities and types</div>
                  </div>
                  <div className="flex items-start gap-2">
                    <Sparkles className="size-4 text-purple-600 mt-0.5 flex-shrink-0" />
                    <div>Additional detections for review</div>
                  </div>
                  <div className="flex items-start gap-2">
                    <AlertTriangle className="size-4 text-amber-600 mt-0.5 flex-shrink-0" />
                    <div>Approximate spans (may need correction)</div>
                  </div>
                </div>
              </div>
            </div>
          </Card>
        </>
      )}

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4">
        <Button
          size="lg"
          onClick={handleContinue}
          disabled={!isComplete}
        >
          Continue to Human Review
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
