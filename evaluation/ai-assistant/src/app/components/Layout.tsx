import { Outlet, useLocation, useNavigate } from 'react-router';
import { Shield, ChevronLeft } from 'lucide-react';
import { Button } from './ui/button';
import { Progress } from './ui/progress';

const steps = [
  { path: '/', label: 'Setup' },
  { path: '/anonymization', label: 'Analysis' },
  { path: '/human-review', label: 'Human Review' },
  { path: '/evaluation', label: 'Evaluation' },
  { path: '/decision', label: 'Insights' },
];

export function Layout() {
  const location = useLocation();
  const navigate = useNavigate();
  
  const currentStepIndex = steps.findIndex(step => step.path === location.pathname);
  const progress = currentStepIndex >= 0 ? ((currentStepIndex + 1) / steps.length) * 100 : 0;
  const canGoBack = currentStepIndex > 0;

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100">
      {/* Header */}
      <header className="bg-white border-b border-slate-200 sticky top-0 z-10">
        <div className="max-w-7xl mx-auto px-6 py-4">
          <div className="flex items-center justify-between">
            <div className="flex items-center gap-3">
              <Shield className="size-8 text-blue-600" />
              <div>
                <h1 className="font-semibold text-slate-900">Presidio Evaluation Flow</h1>
                <p className="text-sm text-slate-600">Human-in-the-loop PII detection evaluation</p>
              </div>
            </div>
            {canGoBack && (
              <Button
                variant="ghost"
                size="sm"
                onClick={() => navigate(steps[currentStepIndex - 1].path)}
              >
                <ChevronLeft className="size-4 mr-1" />
                Back
              </Button>
            )}
          </div>
        </div>

        {/* Progress bar */}
        <div className="max-w-7xl mx-auto px-6 pb-4">
          <div className="flex items-center gap-3 mb-2">
            <span className="text-sm text-slate-600">
              Step {currentStepIndex + 1} of {steps.length}
            </span>
            <span className="text-sm font-medium text-slate-900">
              {steps[currentStepIndex]?.label || 'Unknown'}
            </span>
          </div>
          <Progress value={progress} className="h-2" />
        </div>

        {/* Step indicators */}
        <div className="max-w-7xl mx-auto px-6 pb-4">
          <div className="flex items-center justify-between">
            {steps.map((step, index) => (
              <div
                key={step.path}
                className="flex flex-col items-center gap-1 flex-1"
              >
                <div
                  className={`size-2 rounded-full transition-colors ${
                    index <= currentStepIndex
                      ? 'bg-blue-600'
                      : 'bg-slate-300'
                  }`}
                />
                <span
                  className={`text-xs text-center ${
                    index === currentStepIndex
                      ? 'font-medium text-slate-900'
                      : 'text-slate-500'
                  }`}
                >
                  {step.label}
                </span>
              </div>
            ))}
          </div>
        </div>
      </header>

      {/* Main content */}
      <main className="max-w-7xl mx-auto px-6 py-8">
        <Outlet />
      </main>
    </div>
  );
}
