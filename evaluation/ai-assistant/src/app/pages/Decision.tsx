import { useState } from 'react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Textarea } from '../components/ui/textarea';
import { Label } from '../components/ui/label';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { CheckCircle, RefreshCw, AlertTriangle, Save, Play, FileText } from 'lucide-react';
import { toast } from 'sonner';
import { useNavigate } from 'react-router';

type DecisionType = 'approve' | 'iterate' | null;

export function Decision() {
  const navigate = useNavigate();
  const [decision, setDecision] = useState<DecisionType>(null);
  const [notes, setNotes] = useState('');
  const [selectedImprovements, setSelectedImprovements] = useState<string[]>([]);

  const improvements = [
    { id: 'threshold', label: 'Lower CREDIT_CARD confidence threshold to 0.60', impact: '+12 detections' },
    { id: 'medical', label: 'Add MEDICAL_CONDITION custom recognizer', impact: '+9 detections' },
    { id: 'ssn', label: 'Expand SSN pattern variations', impact: '+8 detections' },
    { id: 'insurance', label: 'Add INSURANCE_POLICY recognizer', impact: '+6 detections' },
  ];

  const toggleImprovement = (id: string) => {
    setSelectedImprovements(prev =>
      prev.includes(id) ? prev.filter(i => i !== id) : [...prev, id]
    );
  };

  const handleApprove = () => {
    toast.success('Configuration approved! Ready for full dataset anonymization.');
  };

  const handleIterate = () => {
    if (selectedImprovements.length === 0) {
      toast.error('Please select at least one improvement to implement');
      return;
    }
    toast.success(`Iteration started with ${selectedImprovements.length} improvements. Returning to sampling...`);
    setTimeout(() => navigate('/sampling'), 1500);
  };

  const handleSaveArtifacts = () => {
    toast.success('Evaluation artifacts saved for audit and compliance');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">Decision Point</h2>
        <p className="text-slate-600">
          Review the evaluation summary and decide whether to proceed or iterate for improvement.
        </p>
      </div>

      {/* Evaluation Summary */}
      <Card className="p-6 bg-slate-50 border-slate-300">
        <div className="space-y-4">
          <h3 className="font-semibold text-slate-900">Evaluation Summary</h3>

          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-white rounded-lg border border-slate-200">
              <div className="text-sm text-slate-600 mb-1">Precision</div>
              <div className="text-2xl font-semibold text-slate-900">94%</div>
              <Badge className="mt-2 bg-green-100 text-green-800 border-green-300">Good</Badge>
            </div>
            <div className="p-4 bg-white rounded-lg border border-slate-200">
              <div className="text-sm text-slate-600 mb-1">Recall</div>
              <div className="text-2xl font-semibold text-slate-900">88%</div>
              <Badge className="mt-2 bg-amber-100 text-amber-800 border-amber-300">Room for improvement</Badge>
            </div>
            <div className="p-4 bg-white rounded-lg border border-slate-200">
              <div className="text-sm text-slate-600 mb-1">F1 Score</div>
              <div className="text-2xl font-semibold text-slate-900">91%</div>
              <Badge className="mt-2 bg-green-100 text-green-800 border-green-300">Good</Badge>
            </div>
          </div>

          <Alert className="border-red-200 bg-red-50">
            <AlertTriangle className="size-4 text-red-600" />
            <AlertDescription>
              <div className="space-y-1">
                <div className="font-medium text-red-900">High-Risk Misses Detected</div>
                <div className="text-sm text-red-800">
                  18 critical false negatives identified (12 credit cards, 6 SSNs). Consider iteration to improve recall.
                </div>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      </Card>

      {/* Decision Options */}
      <Card className="p-6">
        <div className="space-y-4">
          <h3 className="font-semibold text-slate-900">Your Decision</h3>

          <RadioGroup value={decision || ''} onValueChange={(val) => setDecision(val as DecisionType)}>
            {/* Approve Option */}
            <div className={`p-4 rounded-lg border-2 transition-all ${
              decision === 'approve' ? 'border-green-500 bg-green-50' : 'border-slate-200 hover:border-green-300'
            }`}>
              <div className="flex items-start space-x-3">
                <RadioGroupItem value="approve" id="approve" className="mt-1" />
                <div className="flex-1">
                  <Label htmlFor="approve" className="cursor-pointer">
                    <div className="flex items-center gap-2 mb-2">
                      <CheckCircle className="size-5 text-green-600" />
                      <span className="font-medium text-slate-900">Good Enough - Proceed</span>
                    </div>
                    <div className="text-sm text-slate-700 space-y-1">
                      <p>Current configuration meets acceptance criteria. Proceed to full dataset anonymization.</p>
                      {decision === 'approve' && (
                        <div className="mt-3 p-3 bg-white rounded border border-green-200">
                          <div className="text-xs text-green-900 space-y-1">
                            <p className="font-medium">Next steps:</p>
                            <ul className="list-disc list-inside ml-2">
                              <li>Configuration will be saved and versioned</li>
                              <li>Golden set will be stored for future reference</li>
                              <li>Full dataset anonymization can begin (manual process)</li>
                              <li>Evaluation artifacts saved for audit</li>
                            </ul>
                          </div>
                        </div>
                      )}
                    </div>
                  </Label>
                </div>
              </div>
            </div>

            {/* Iterate Option */}
            <div className={`p-4 rounded-lg border-2 transition-all ${
              decision === 'iterate' ? 'border-blue-500 bg-blue-50' : 'border-slate-200 hover:border-blue-300'
            }`}>
              <div className="flex items-start space-x-3">
                <RadioGroupItem value="iterate" id="iterate" className="mt-1" />
                <div className="flex-1">
                  <Label htmlFor="iterate" className="cursor-pointer">
                    <div className="flex items-center gap-2 mb-2">
                      <RefreshCw className="size-5 text-blue-600" />
                      <span className="font-medium text-slate-900">Needs Improvement - Iterate</span>
                    </div>
                    <div className="text-sm text-slate-700 space-y-1">
                      <p>Configuration requires tuning. Select improvements and run another evaluation cycle.</p>
                      {decision === 'iterate' && (
                        <div className="mt-3 p-3 bg-white rounded border border-blue-200 space-y-3">
                          <div className="text-sm font-medium text-blue-900">Select improvements to implement:</div>
                          <div className="space-y-2">
                            {improvements.map(improvement => (
                              <div
                                key={improvement.id}
                                className={`p-3 rounded border cursor-pointer transition-colors ${
                                  selectedImprovements.includes(improvement.id)
                                    ? 'bg-blue-100 border-blue-400'
                                    : 'bg-slate-50 border-slate-300 hover:border-blue-300'
                                }`}
                                onClick={() => toggleImprovement(improvement.id)}
                              >
                                <div className="flex items-center gap-2">
                                  <input
                                    type="checkbox"
                                    checked={selectedImprovements.includes(improvement.id)}
                                    onChange={() => toggleImprovement(improvement.id)}
                                    className="rounded"
                                  />
                                  <div className="flex-1">
                                    <div className="text-sm font-medium text-slate-900">{improvement.label}</div>
                                    <div className="text-xs text-slate-600">{improvement.impact}</div>
                                  </div>
                                </div>
                              </div>
                            ))}
                          </div>
                          {selectedImprovements.length > 0 && (
                            <div className="text-xs text-blue-800 p-2 bg-blue-100 rounded">
                              Selected {selectedImprovements.length} improvement{selectedImprovements.length > 1 ? 's' : ''}.
                              This will update the Presidio configuration and loop back to sampling.
                            </div>
                          )}
                        </div>
                      )}
                    </div>
                  </Label>
                </div>
              </div>
            </div>
          </RadioGroup>
        </div>
      </Card>

      {/* Decision Notes */}
      <Card className="p-6">
        <div className="space-y-3">
          <Label>Decision Notes (for audit trail)</Label>
          <Textarea
            placeholder="Document your decision reasoning, risk assessment, and any additional context..."
            value={notes}
            onChange={(e) => setNotes(e.target.value)}
            rows={4}
          />
          <p className="text-sm text-slate-600">
            These notes will be saved with the evaluation artifacts for compliance and future reference.
          </p>
        </div>
      </Card>

      {/* Outputs & Artifacts */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <FileText className="size-5 text-blue-600" />
            <h3 className="font-semibold text-blue-900">Output & Reusable Artifacts</h3>
          </div>
          <div className="text-sm text-blue-800 space-y-2">
            <p>The following artifacts will be generated:</p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li><span className="font-medium">Approved Presidio Configuration</span> - Version-controlled config ready for deployment</li>
              <li><span className="font-medium">Golden Dataset</span> - Human-validated labels for future tuning or ML training</li>
              <li><span className="font-medium">Evaluation Report</span> - Metrics, charts, and error analysis</li>
              <li><span className="font-medium">Audit Trail</span> - Complete history of decisions, iterations, and rationale</li>
              <li><span className="font-medium">Iteration History</span> - Comparison across all evaluation runs</li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4">
        <Button variant="outline" onClick={handleSaveArtifacts}>
          <Save className="size-4 mr-2" />
          Save Artifacts
        </Button>

        <div className="flex gap-3">
          {decision === 'approve' && (
            <Button size="lg" onClick={handleApprove}>
              <CheckCircle className="size-4 mr-2" />
              Approve & Finalize
            </Button>
          )}
          {decision === 'iterate' && (
            <Button size="lg" onClick={handleIterate} disabled={selectedImprovements.length === 0}>
              <RefreshCw className="size-4 mr-2" />
              Start Iteration
            </Button>
          )}
          {!decision && (
            <Button size="lg" disabled>
              <Play className="size-4 mr-2" />
              Make a Decision
            </Button>
          )}
        </div>
      </div>

      {/* Iteration Context Note */}
      {decision === 'iterate' && (
        <Alert>
          <RefreshCw className="size-4" />
          <AlertDescription>
            <div className="text-sm">
              The system will update Presidio configuration with selected improvements, generate a new sample
              (using stratified random sampling), and run the complete evaluation flow again. Previous results
              will be saved for comparison.
            </div>
          </AlertDescription>
        </Alert>
      )}
    </div>
  );
}
