import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { ArrowRight, Loader2, CheckCircle, BarChart3, TrendingUp, TrendingDown } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';

const metricsData = [
  { name: 'Precision', value: 94, color: '#3b82f6' },
  { name: 'Recall', value: 88, color: '#10b981' },
  { name: 'F1 Score', value: 91, color: '#8b5cf6' },
];

const entityTypeData = [
  { type: 'PERSON', precision: 96, recall: 92, f1: 94 },
  { type: 'EMAIL', precision: 98, recall: 95, f1: 96 },
  { type: 'PHONE', precision: 93, recall: 89, f1: 91 },
  { type: 'SSN', precision: 97, recall: 84, f1: 90 },
  { type: 'CREDIT_CARD', precision: 71, recall: 65, f1: 68 },
  { type: 'MEDICAL_RECORD', precision: 89, recall: 81, f1: 85 },
];

export function Evaluation() {
  const navigate = useNavigate();
  const [progress, setProgress] = useState(0);
  const [isComplete, setIsComplete] = useState(false);

  useEffect(() => {
    const interval = setInterval(() => {
      setProgress((prev) => {
        if (prev >= 100) {
          clearInterval(interval);
          setIsComplete(true);
          return 100;
        }
        return prev + 3;
      });
    }, 60);

    return () => clearInterval(interval);
  }, []);

  const handleContinue = () => {
    navigate('/dashboard');
  };

  return (
    <div className="max-w-6xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">Evaluation</h2>
        <p className="text-slate-600">
          Comparing Presidio output against the validated golden set to produce evaluation metrics.
        </p>
      </div>

      {/* Processing Status */}
      {!isComplete && (
        <Card className="p-8">
          <div className="space-y-6">
            <div className="flex items-center justify-center">
              <Loader2 className="size-16 text-blue-600 animate-spin" />
            </div>

            <div className="text-center space-y-2">
              <h3 className="text-xl font-semibold text-slate-900">Running Presidio Evaluator...</h3>
              <p className="text-slate-600">Calculating precision, recall, and identifying error patterns</p>
            </div>

            <div className="space-y-2">
              <div className="flex justify-between text-sm text-slate-600">
                <span>Progress</span>
                <span>{progress}%</span>
              </div>
              <Progress value={progress} className="h-3" />
            </div>
          </div>
        </Card>
      )}

      {/* Results */}
      {isComplete && (
        <>
          {/* Overall Metrics */}
          <Card className="p-6 border-green-200 bg-green-50">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="size-5 text-green-700" />
                <h3 className="font-semibold text-green-900">Evaluation Complete</h3>
              </div>

              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="bg-white p-4 rounded-lg border border-green-200">
                  <div className="text-2xl font-semibold text-green-900">94%</div>
                  <div className="text-sm text-green-700">Precision</div>
                  <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
                    <TrendingUp className="size-3" />
                    <span>+3% from last run</span>
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-green-200">
                  <div className="text-2xl font-semibold text-green-900">88%</div>
                  <div className="text-sm text-green-700">Recall</div>
                  <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
                    <TrendingUp className="size-3" />
                    <span>+7% from last run</span>
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-green-200">
                  <div className="text-2xl font-semibold text-green-900">91%</div>
                  <div className="text-sm text-green-700">F1 Score</div>
                  <div className="flex items-center gap-1 text-xs text-green-600 mt-1">
                    <TrendingUp className="size-3" />
                    <span>+5% from last run</span>
                  </div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-green-200">
                  <div className="text-2xl font-semibold text-green-900">40</div>
                  <div className="text-sm text-green-700">False Negatives</div>
                  <div className="flex items-center gap-1 text-xs text-red-600 mt-1">
                    <TrendingDown className="size-3" />
                    <span>-24 from last run</span>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Metrics Chart */}
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <BarChart3 className="size-5 text-blue-600" />
                <h3 className="font-semibold text-slate-900">Overall Metrics</h3>
              </div>

              <ResponsiveContainer width="100%" height={300}>
                <BarChart data={metricsData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="name" />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Entity Type Breakdown */}
          <Card className="p-6">
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900">Performance by Entity Type</h3>

              <ResponsiveContainer width="100%" height={300}>
                <LineChart data={entityTypeData}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="type" angle={-45} textAnchor="end" height={80} />
                  <YAxis domain={[0, 100]} />
                  <Tooltip />
                  <Legend />
                  <Line type="monotone" dataKey="precision" stroke="#3b82f6" strokeWidth={2} />
                  <Line type="monotone" dataKey="recall" stroke="#10b981" strokeWidth={2} />
                  <Line type="monotone" dataKey="f1" stroke="#8b5cf6" strokeWidth={2} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </Card>

          {/* Error Summary */}
          <Card className="p-6">
            <div className="space-y-4">
              <h3 className="font-semibold text-slate-900">Error Summary</h3>

              <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
                <div className="p-4 bg-red-50 rounded-lg border border-red-200">
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-medium text-red-900">False Negatives (Misses)</div>
                    <Badge className="bg-red-200 text-red-900">40 total</Badge>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-red-800">CREDIT_CARD</span>
                      <span className="font-medium text-red-900">12 misses</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-red-800">MEDICAL_CONDITION</span>
                      <span className="font-medium text-red-900">9 misses</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-red-800">SSN</span>
                      <span className="font-medium text-red-900">8 misses</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-red-800">Other types</span>
                      <span className="font-medium text-red-900">11 misses</span>
                    </div>
                  </div>
                </div>

                <div className="p-4 bg-amber-50 rounded-lg border border-amber-200">
                  <div className="flex items-center justify-between mb-3">
                    <div className="font-medium text-amber-900">False Positives (Incorrect)</div>
                    <Badge className="bg-amber-200 text-amber-900">19 total</Badge>
                  </div>
                  <div className="space-y-2 text-sm">
                    <div className="flex justify-between">
                      <span className="text-amber-800">DATE patterns</span>
                      <span className="font-medium text-amber-900">7 incorrect</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-amber-800">PERSON names</span>
                      <span className="font-medium text-amber-900">5 incorrect</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-amber-800">PHONE_NUMBER</span>
                      <span className="font-medium text-amber-900">4 incorrect</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-amber-800">Other types</span>
                      <span className="font-medium text-amber-900">3 incorrect</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </Card>

          {/* Risk-Critical Misses */}
          <Card className="p-6 border-red-300 bg-red-50">
            <div className="space-y-3">
              <div className="flex items-center gap-2">
                <Badge className="bg-red-600 text-white">High Priority</Badge>
                <h3 className="font-semibold text-red-900">Risk-Critical Misses</h3>
              </div>
              <div className="text-sm text-red-800">
                <p>18 high-risk false negatives detected (PHI, financial data, SSN):</p>
                <ul className="list-disc list-inside mt-2 space-y-1">
                  <li>12 Credit card numbers (partial matches, low confidence scores)</li>
                  <li>6 SSN variations (non-standard formatting)</li>
                </ul>
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
          View Interactive Dashboard
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
