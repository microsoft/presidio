import { useNavigate } from 'react-router';
import { ArrowRight, CheckCircle2, ClipboardCheck, FlaskConical, Shield, Upload } from 'lucide-react';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';

const flowSteps = [
  {
    title: 'Setup your dataset',
    description: 'Choose or upload the dataset, confirm the text column, and decide whether to run Presidio, the LLM judge, or both.',
    icon: Upload,
  },
  {
    title: 'Run detection engines',
    description: 'Execute the selected configurations and compare what each engine detects before any human correction is applied.',
    icon: FlaskConical,
  },
  {
    title: 'Review and validate',
    description: 'Confirm, reject, or adjust detections to create the golden set the evaluation will use as the trusted reference.',
    icon: ClipboardCheck,
  },
  {
    title: 'Evaluate and export',
    description: 'Inspect the error summary, review recommendations, and export the dataset plus the configurations you tested.',
    icon: CheckCircle2,
  },
];

export function Welcome() {
  const navigate = useNavigate();

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <Card className="p-8 border-blue-200 bg-gradient-to-br from-white to-blue-50">
        <div className="space-y-5">
          <div className="inline-flex items-center gap-2 rounded-full border border-blue-200 bg-blue-100 px-3 py-1 text-sm font-medium text-blue-800">
            <Shield className="size-4" />
            Guided Evaluation Workflow
          </div>
          <div className="space-y-3">
            <h2 className="text-3xl font-semibold text-slate-900">Welcome to the Presidio Evaluation Flow</h2>
            <p className="max-w-3xl text-slate-700">
              This workflow helps you compare Presidio and LLM-based PII detection against a human-validated golden set.
              It is designed for iterative tuning: run configurations, review the detections, then inspect the evaluation output.
            </p>
          </div>
          <div className="grid gap-3 md:grid-cols-2">
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="font-medium text-slate-900">What we assume</div>
              <p className="mt-2 text-sm text-slate-600">
                Your dataset has a text field that contains the content to analyze. Human review decisions are treated as the source of truth for evaluation.
              </p>
            </div>
            <div className="rounded-xl border border-slate-200 bg-white p-4">
              <div className="font-medium text-slate-900">What is expected from you</div>
              <p className="mt-2 text-sm text-slate-600">
                Upload or select a dataset, run the engines you care about, and carefully confirm or correct detections during Human Review.
              </p>
            </div>
          </div>
        </div>
      </Card>

      <div className="grid gap-4 md:grid-cols-2">
        {flowSteps.map((step) => {
          const Icon = step.icon;
          return (
            <Card key={step.title} className="p-5">
              <div className="flex items-start gap-3">
                <div className="rounded-lg bg-slate-100 p-2 text-slate-700">
                  <Icon className="size-5" />
                </div>
                <div className="space-y-1">
                  <div className="font-medium text-slate-900">{step.title}</div>
                  <p className="text-sm text-slate-600">{step.description}</p>
                </div>
              </div>
            </Card>
          );
        })}
      </div>

      <div className="flex justify-end pt-2">
        <Button size="lg" onClick={() => navigate('/setup')}>
          Start Setup
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}