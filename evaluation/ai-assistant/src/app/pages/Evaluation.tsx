import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowRight, Loader2, CheckCircle, BarChart3, TrendingUp, TrendingDown, Search, AlertTriangle, XCircle, Download, Filter } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, LineChart, Line } from 'recharts';
import { mockEntityMisses } from '../lib/mockData';

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
  const [filterType, setFilterType] = useState<'all' | 'false-positive' | 'false-negative'>('all');
  const [filterEntityType, setFilterEntityType] = useState<string>('all');
  const [filterRiskLevel, setFilterRiskLevel] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

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

  const filteredMisses = mockEntityMisses.filter(miss => {
    if (filterType !== 'all' && miss.missType !== filterType) return false;
    if (filterEntityType !== 'all' && miss.entityType !== filterEntityType) return false;
    if (filterRiskLevel !== 'all' && miss.riskLevel !== filterRiskLevel) return false;
    if (searchQuery && !miss.recordText.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const entityTypes = ['all', ...new Set(mockEntityMisses.map(m => m.entityType))];

  const missesummary = {
    totalMisses: mockEntityMisses.length,
    falsePositives: mockEntityMisses.filter(m => m.missType === 'false-positive').length,
    falseNegatives: mockEntityMisses.filter(m => m.missType === 'false-negative').length,
    highRisk: mockEntityMisses.filter(m => m.riskLevel === 'high').length,
    mediumRisk: mockEntityMisses.filter(m => m.riskLevel === 'medium').length,
    lowRisk: mockEntityMisses.filter(m => m.riskLevel === 'low').length,
  };

  const handleContinue = () => {
    navigate('/decision');
  };

  const handleExport = () => {
    alert('Dashboard data exported successfully!');
  };

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900 mb-2">Evaluation Dashboard</h2>
          <p className="text-slate-600">
            Comparing detection output against the validated golden set — metrics, error analysis, and recommendations.
          </p>
        </div>
        {isComplete && (
          <Button variant="outline" onClick={handleExport}>
            <Download className="size-4 mr-2" />
            Export
          </Button>
        )}
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

          {/* Charts */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <Card className="p-6">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <BarChart3 className="size-5 text-blue-600" />
                  <h3 className="font-semibold text-slate-900">Overall Metrics</h3>
                </div>
                <ResponsiveContainer width="100%" height={260}>
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

            <Card className="p-6">
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900">Performance by Entity Type</h3>
                <ResponsiveContainer width="100%" height={260}>
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
          </div>

          {/* Error Summary + Risk-Critical */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-6">
              <div className="space-y-3">
                <div className="font-medium text-red-900">False Negatives (Misses)</div>
                <Badge className="bg-red-200 text-red-900">40 total</Badge>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-red-800">CREDIT_CARD</span><span className="font-medium text-red-900">12</span></div>
                  <div className="flex justify-between"><span className="text-red-800">MEDICAL_CONDITION</span><span className="font-medium text-red-900">9</span></div>
                  <div className="flex justify-between"><span className="text-red-800">SSN</span><span className="font-medium text-red-900">8</span></div>
                  <div className="flex justify-between"><span className="text-red-800">Other</span><span className="font-medium text-red-900">11</span></div>
                </div>
              </div>
            </Card>
            <Card className="p-6">
              <div className="space-y-3">
                <div className="font-medium text-amber-900">False Positives (Incorrect)</div>
                <Badge className="bg-amber-200 text-amber-900">19 total</Badge>
                <div className="space-y-2 text-sm">
                  <div className="flex justify-between"><span className="text-amber-800">DATE patterns</span><span className="font-medium text-amber-900">7</span></div>
                  <div className="flex justify-between"><span className="text-amber-800">PERSON names</span><span className="font-medium text-amber-900">5</span></div>
                  <div className="flex justify-between"><span className="text-amber-800">PHONE_NUMBER</span><span className="font-medium text-amber-900">4</span></div>
                  <div className="flex justify-between"><span className="text-amber-800">Other</span><span className="font-medium text-amber-900">3</span></div>
                </div>
              </div>
            </Card>
            <Card className="p-6 border-red-300 bg-red-50">
              <div className="space-y-3">
                <div className="flex items-center gap-2">
                  <Badge className="bg-red-600 text-white">High Priority</Badge>
                  <span className="font-semibold text-red-900 text-sm">Risk-Critical</span>
                </div>
                <div className="text-sm text-red-800">
                  <p>18 high-risk false negatives:</p>
                  <ul className="list-disc list-inside mt-2 space-y-1">
                    <li>12 Credit card numbers</li>
                    <li>6 SSN variations</li>
                  </ul>
                </div>
              </div>
            </Card>
          </div>

          {/* Dashboard Tabs — Error Explorer, Patterns, Insights */}
          <Tabs defaultValue="misses" className="space-y-6">
            <TabsList className="grid w-full grid-cols-3">
              <TabsTrigger value="misses">Error Explorer</TabsTrigger>
              <TabsTrigger value="patterns">Error Patterns</TabsTrigger>
              <TabsTrigger value="insights">Insights</TabsTrigger>
            </TabsList>

            {/* Error Explorer */}
            <TabsContent value="misses" className="space-y-4">
              {/* Summary Cards */}
              <div className="grid grid-cols-2 md:grid-cols-6 gap-4">
                <Card className="p-4">
                  <div className="text-2xl font-semibold text-slate-900">{missesummary.totalMisses}</div>
                  <div className="text-sm text-slate-600">Total Misses</div>
                </Card>
                <Card className="p-4 border-amber-200 bg-amber-50">
                  <div className="text-2xl font-semibold text-amber-900">{missesummary.falsePositives}</div>
                  <div className="text-sm text-amber-700">False Positives</div>
                </Card>
                <Card className="p-4 border-red-200 bg-red-50">
                  <div className="text-2xl font-semibold text-red-900">{missesummary.falseNegatives}</div>
                  <div className="text-sm text-red-700">False Negatives</div>
                </Card>
                <Card className="p-4 border-red-300 bg-red-100">
                  <div className="text-2xl font-semibold text-red-900">{missesummary.highRisk}</div>
                  <div className="text-sm text-red-700">High Risk</div>
                </Card>
                <Card className="p-4 border-amber-300 bg-amber-100">
                  <div className="text-2xl font-semibold text-amber-900">{missesummary.mediumRisk}</div>
                  <div className="text-sm text-amber-700">Medium Risk</div>
                </Card>
                <Card className="p-4 border-slate-200 bg-slate-50">
                  <div className="text-2xl font-semibold text-slate-700">{missesummary.lowRisk}</div>
                  <div className="text-sm text-slate-600">Low Risk</div>
                </Card>
              </div>

              {/* Filters */}
              <Card className="p-4">
                <div className="flex items-center gap-3">
                  <Filter className="size-4 text-slate-600" />
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-4 gap-3">
                    <div className="relative">
                      <Search className="size-4 absolute left-3 top-1/2 -translate-y-1/2 text-slate-400" />
                      <Input
                        placeholder="Search record text..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="pl-9"
                      />
                    </div>
                    <Select value={filterType} onValueChange={(val) => setFilterType(val as any)}>
                      <SelectTrigger><SelectValue placeholder="Miss Type" /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Types</SelectItem>
                        <SelectItem value="false-positive">False Positives</SelectItem>
                        <SelectItem value="false-negative">False Negatives</SelectItem>
                      </SelectContent>
                    </Select>
                    <Select value={filterEntityType} onValueChange={setFilterEntityType}>
                      <SelectTrigger><SelectValue placeholder="Entity Type" /></SelectTrigger>
                      <SelectContent>
                        {entityTypes.map(type => (
                          <SelectItem key={type} value={type}>
                            {type === 'all' ? 'All Entities' : type}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                    <Select value={filterRiskLevel} onValueChange={setFilterRiskLevel}>
                      <SelectTrigger><SelectValue placeholder="Risk Level" /></SelectTrigger>
                      <SelectContent>
                        <SelectItem value="all">All Risk Levels</SelectItem>
                        <SelectItem value="high">High Risk</SelectItem>
                        <SelectItem value="medium">Medium Risk</SelectItem>
                        <SelectItem value="low">Low Risk</SelectItem>
                      </SelectContent>
                    </Select>
                  </div>
                </div>
              </Card>

              {/* Misses List */}
              <div className="space-y-3">
                <div className="text-sm text-slate-600">
                  Showing {filteredMisses.length} of {mockEntityMisses.length} errors
                </div>
                {filteredMisses.map((miss, index) => (
                  <Card
                    key={index}
                    className={`p-4 ${
                      miss.riskLevel === 'high' ? 'border-red-300 bg-red-50' :
                      miss.riskLevel === 'medium' ? 'border-amber-300 bg-amber-50' :
                      'border-slate-200'
                    }`}
                  >
                    <div className="space-y-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-center gap-2">
                          {miss.missType === 'false-negative' ? (
                            <XCircle className="size-5 text-red-600 flex-shrink-0" />
                          ) : (
                            <AlertTriangle className="size-5 text-amber-600 flex-shrink-0" />
                          )}
                          <div>
                            <div className="font-medium text-slate-900">
                              {miss.missType === 'false-negative' ? 'Missed Entity' : 'Incorrect Detection'}
                            </div>
                            <div className="text-sm text-slate-600">Record ID: {miss.recordId}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{miss.entityType}</Badge>
                          <Badge
                            className={
                              miss.riskLevel === 'high' ? 'bg-red-600 text-white' :
                              miss.riskLevel === 'medium' ? 'bg-amber-600 text-white' :
                              'bg-slate-600 text-white'
                            }
                          >
                            {miss.riskLevel} risk
                          </Badge>
                        </div>
                      </div>
                      <div className="p-3 bg-white rounded border border-slate-200">
                        <div className="text-sm font-mono text-slate-700">{miss.recordText}</div>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <div>
                          <span className="text-slate-600">Missed Entity: </span>
                          <span className="font-medium text-slate-900">{miss.missedEntity.text}</span>
                        </div>
                        <div>
                          <span className="text-slate-600">Position: </span>
                          <span className="font-medium text-slate-900">{miss.missedEntity.start}-{miss.missedEntity.end}</span>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Error Patterns */}
            <TabsContent value="patterns" className="space-y-4">
              <Card className="p-6">
                <h3 className="font-semibold text-slate-900 mb-4">Most Frequently Missed Entity Types</h3>
                <div className="space-y-3">
                  {[
                    { type: 'CREDIT_CARD', count: 12, pattern: 'Partial card numbers, low confidence scores' },
                    { type: 'MEDICAL_CONDITION', count: 9, pattern: 'Medical terminology not in baseline recognizers' },
                    { type: 'SSN', count: 8, pattern: 'Non-standard formatting (spaces instead of dashes)' },
                    { type: 'INSURANCE_POLICY', count: 6, pattern: 'Custom format not covered by patterns' },
                  ].map(item => (
                    <div key={item.type} className="p-4 bg-slate-50 rounded-lg border border-slate-200">
                      <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-3">
                          <Badge variant="outline">{item.type}</Badge>
                          <span className="text-sm font-medium text-slate-900">{item.count} occurrences</span>
                        </div>
                      </div>
                      <div className="text-sm text-slate-600">{item.pattern}</div>
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="font-semibold text-slate-900 mb-4">Common Error Patterns</h3>
                <div className="space-y-3 text-sm">
                  <div className="p-3 bg-blue-50 rounded border border-blue-200">
                    <div className="font-medium text-blue-900 mb-1">Pattern: Low Confidence Threshold</div>
                    <div className="text-blue-800">Credit card patterns are being detected but filtered out due to confidence scores below threshold (typically 0.65-0.75)</div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded border border-blue-200">
                    <div className="font-medium text-blue-900 mb-1">Pattern: Format Variations</div>
                    <div className="text-blue-800">SSN and phone numbers with non-standard separators (spaces, periods) are being missed</div>
                  </div>
                  <div className="p-3 bg-blue-50 rounded border border-blue-200">
                    <div className="font-medium text-blue-900 mb-1">Pattern: Domain-Specific Terms</div>
                    <div className="text-blue-800">Medical conditions and insurance policy numbers require custom recognizers for your domain</div>
                  </div>
                </div>
              </Card>
            </TabsContent>

            {/* Insights */}
            <TabsContent value="insights" className="space-y-4">
              <Card className="p-6 border-blue-200 bg-blue-50">
                <h3 className="font-semibold text-blue-900 mb-4">Key Insights & Recommendations</h3>
                <div className="space-y-4">
                  <div>
                    <div className="font-medium text-blue-900 mb-2">1. Adjust Confidence Thresholds</div>
                    <div className="text-sm text-blue-800">
                      Consider lowering the confidence threshold for CREDIT_CARD entities from 0.70 to 0.60.
                      This would capture 12 additional credit card numbers that are currently being missed.
                    </div>
                  </div>
                  <div>
                    <div className="font-medium text-blue-900 mb-2">2. Add Custom Recognizers</div>
                    <div className="text-sm text-blue-800">
                      Create domain-specific recognizers for MEDICAL_CONDITION (9 misses) and INSURANCE_POLICY (6 misses)
                      to better handle your healthcare dataset.
                    </div>
                  </div>
                  <div>
                    <div className="font-medium text-blue-900 mb-2">3. Expand Pattern Variations</div>
                    <div className="text-sm text-blue-800">
                      Update SSN and PHONE_NUMBER patterns to handle alternative separators (spaces, periods, no separators).
                      This addresses 8 SSN misses.
                    </div>
                  </div>
                  <div>
                    <div className="font-medium text-blue-900 mb-2">4. Strong Areas</div>
                    <div className="text-sm text-blue-800">
                      EMAIL (98% precision, 95% recall) and PERSON (96% precision, 92% recall) recognizers are performing
                      well and don't require tuning.
                    </div>
                  </div>
                </div>
              </Card>

              <Card className="p-6">
                <h3 className="font-semibold text-slate-900 mb-4">Impact Analysis</h3>
                <div className="text-sm text-slate-700 space-y-3">
                  <p>Implementing the recommended changes would potentially:</p>
                  <ul className="list-disc list-inside space-y-2 ml-2">
                    <li><span className="font-medium">Increase recall from 88% to 94%</span> — capturing 27 additional PII entities</li>
                    <li><span className="font-medium">Reduce high-risk misses from 18 to 6</span> — better protection for sensitive data</li>
                    <li><span className="font-medium">Improve F1 score from 91% to 94%</span> — better overall balance</li>
                    <li><span className="font-medium">Minor precision trade-off</span> — may introduce 3-5 additional false positives</li>
                  </ul>
                </div>
              </Card>
            </TabsContent>
          </Tabs>
        </>
      )}

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4">
        <Button
          size="lg"
          onClick={handleContinue}
          disabled={!isComplete}
        >
          View Insights
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
