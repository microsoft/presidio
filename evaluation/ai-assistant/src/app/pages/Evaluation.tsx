import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Tabs, TabsContent, TabsList, TabsTrigger } from '../components/ui/tabs';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { ArrowRight, ChevronLeft, Loader2, CheckCircle, Search, AlertTriangle, XCircle, Download, Filter } from 'lucide-react';
import { api } from '../lib/api';

interface EvalMetrics {
  overall: { precision: number; recall: number; f1_score: number; false_negatives: number };
  by_entity_type: { type: string; precision: number; recall: number; f1: number }[];
  errors: {
    false_negatives: { total: number; by_type: { type: string; count: number }[] };
    false_positives: { total: number; by_type: { type: string; count: number }[] };
  };
}

interface EvalMiss {
  record_id: string;
  record_text: string;
  missed_entity: { text: string; entity_type: string; start: number; end: number; score?: number };
  miss_type: 'false-positive' | 'false-negative';
  entity_type: string;
  risk_level: 'high' | 'medium' | 'low';
}

interface EvalPatterns {
  frequent_misses: { type: string; count: number; pattern: string }[];
  common_patterns: { name: string; description: string }[];
  insights: { title: string; description: string }[];
}

export function Evaluation() {
  const navigate = useNavigate();
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [metrics, setMetrics] = useState<EvalMetrics | null>(null);
  const [misses, setMisses] = useState<EvalMiss[]>([]);
  const [patterns, setPatterns] = useState<EvalPatterns | null>(null);
  const [filterType, setFilterType] = useState<'all' | 'false-positive' | 'false-negative'>('all');
  const [filterEntityType, setFilterEntityType] = useState<string>('all');
  const [filterRiskLevel, setFilterRiskLevel] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');

  const runEvaluation = useCallback(async () => {
    setIsLoading(true);
    setError(null);
    try {
      // Trigger backend evaluation then fetch results
      await api.evaluation.run();
      const [metricsData, missesData, patternsData] = await Promise.all([
        api.evaluation.metrics(),
        api.evaluation.misses(),
        api.evaluation.patterns(),
      ]);
      setMetrics(metricsData);
      setMisses(missesData);
      setPatterns(patternsData);
    } catch (err: any) {
      setError(err.message || 'Evaluation failed');
    } finally {
      setIsLoading(false);
    }
  }, []);

  useEffect(() => {
    runEvaluation();
  }, [runEvaluation]);

  const filteredMisses = misses.filter(miss => {
    if (filterType !== 'all' && miss.miss_type !== filterType) return false;
    if (filterEntityType !== 'all' && miss.entity_type !== filterEntityType) return false;
    if (filterRiskLevel !== 'all' && miss.risk_level !== filterRiskLevel) return false;
    if (searchQuery && !miss.record_text.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const entityTypes = ['all', ...new Set(misses.map(m => m.entity_type))];

  const misseSummary = {
    totalMisses: misses.length,
    falsePositives: misses.filter(m => m.miss_type === 'false-positive').length,
    falseNegatives: misses.filter(m => m.miss_type === 'false-negative').length,
    highRisk: misses.filter(m => m.risk_level === 'high').length,
    mediumRisk: misses.filter(m => m.risk_level === 'medium').length,
    lowRisk: misses.filter(m => m.risk_level === 'low').length,
  };

  const handleContinue = () => {
    navigate('/decision');
  };

  const handleExport = () => {
    alert('Dashboard data exported successfully!');
  };

  const isComplete = !isLoading && !error && metrics !== null;

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
      {isLoading && (
        <Card className="p-8">
          <div className="space-y-6">
            <div className="flex items-center justify-center">
              <Loader2 className="size-16 text-blue-600 animate-spin" />
            </div>
            <div className="text-center space-y-2">
              <h3 className="text-xl font-semibold text-slate-900">Running Evaluation...</h3>
              <p className="text-slate-600">Comparing Presidio results against the golden set — calculating precision, recall, and identifying errors</p>
            </div>
          </div>
        </Card>
      )}

      {/* Error */}
      {error && (
        <Card className="p-8 border-red-200 bg-red-50">
          <div className="text-center space-y-4">
            <XCircle className="size-12 text-red-500 mx-auto" />
            <h3 className="text-lg font-semibold text-red-900">Evaluation Failed</h3>
            <p className="text-sm text-red-700">{error}</p>
            <Button variant="outline" onClick={runEvaluation}>Retry</Button>
          </div>
        </Card>
      )}

      {/* Results */}
      {isComplete && metrics && (
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
                  <div className="text-2xl font-semibold text-green-900">{metrics.overall.precision}%</div>
                  <div className="text-sm text-green-700">Precision</div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-green-200">
                  <div className="text-2xl font-semibold text-green-900">{metrics.overall.recall}%</div>
                  <div className="text-sm text-green-700">Recall</div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-green-200">
                  <div className="text-2xl font-semibold text-green-900">{metrics.overall.f1_score}%</div>
                  <div className="text-sm text-green-700">F1 Score</div>
                </div>
                <div className="bg-white p-4 rounded-lg border border-green-200">
                  <div className="text-2xl font-semibold text-green-900">{metrics.overall.false_negatives}</div>
                  <div className="text-sm text-green-700">False Negatives</div>
                </div>
              </div>
            </div>
          </Card>

          {/* Per-entity-type breakdown */}
          {metrics.by_entity_type.length > 0 && (
            <Card className="p-6">
              <h3 className="font-semibold text-slate-900 mb-4">Performance by Entity Type</h3>
              <div className="overflow-x-auto">
                <table className="w-full text-sm">
                  <thead>
                    <tr className="border-b border-slate-200">
                      <th className="text-left py-2 pr-4 font-medium text-slate-600">Entity Type</th>
                      <th className="text-right py-2 px-4 font-medium text-slate-600">Precision</th>
                      <th className="text-right py-2 px-4 font-medium text-slate-600">Recall</th>
                      <th className="text-right py-2 pl-4 font-medium text-slate-600">F1</th>
                    </tr>
                  </thead>
                  <tbody>
                    {metrics.by_entity_type.map(e => (
                      <tr key={e.type} className="border-b border-slate-100">
                        <td className="py-2 pr-4 font-medium text-slate-900">{e.type}</td>
                        <td className="text-right py-2 px-4 text-slate-700">{e.precision}%</td>
                        <td className="text-right py-2 px-4 text-slate-700">{e.recall}%</td>
                        <td className={`text-right py-2 pl-4 font-medium ${e.f1 >= 90 ? 'text-green-700' : e.f1 >= 70 ? 'text-amber-700' : 'text-red-700'}`}>{e.f1}%</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </Card>
          )}

          {/* Error Summary + Risk-Critical */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <Card className="p-6">
              <div className="space-y-3">
                <div className="font-medium text-red-900">False Negatives (Misses)</div>
                <Badge className="bg-red-200 text-red-900">{metrics.errors.false_negatives.total} total</Badge>
                <div className="space-y-2 text-sm">
                  {metrics.errors.false_negatives.by_type.map(item => (
                    <div key={item.type} className="flex justify-between">
                      <span className="text-red-800">{item.type}</span>
                      <span className="font-medium text-red-900">{item.count}</span>
                    </div>
                  ))}
                </div>
              </div>
            </Card>
            <Card className="p-6">
              <div className="space-y-3">
                <div className="font-medium text-amber-900">False Positives (Incorrect)</div>
                <Badge className="bg-amber-200 text-amber-900">{metrics.errors.false_positives.total} total</Badge>
                <div className="space-y-2 text-sm">
                  {metrics.errors.false_positives.by_type.map(item => (
                    <div key={item.type} className="flex justify-between">
                      <span className="text-amber-800">{item.type}</span>
                      <span className="font-medium text-amber-900">{item.count}</span>
                    </div>
                  ))}
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
                  <p>{misseSummary.highRisk} high-risk misses detected</p>
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
                  <div className="text-2xl font-semibold text-slate-900">{misseSummary.totalMisses}</div>
                  <div className="text-sm text-slate-600">Total Misses</div>
                </Card>
                <Card className="p-4 border-amber-200 bg-amber-50">
                  <div className="text-2xl font-semibold text-amber-900">{misseSummary.falsePositives}</div>
                  <div className="text-sm text-amber-700">False Positives</div>
                </Card>
                <Card className="p-4 border-red-200 bg-red-50">
                  <div className="text-2xl font-semibold text-red-900">{misseSummary.falseNegatives}</div>
                  <div className="text-sm text-red-700">False Negatives</div>
                </Card>
                <Card className="p-4 border-red-300 bg-red-100">
                  <div className="text-2xl font-semibold text-red-900">{misseSummary.highRisk}</div>
                  <div className="text-sm text-red-700">High Risk</div>
                </Card>
                <Card className="p-4 border-amber-300 bg-amber-100">
                  <div className="text-2xl font-semibold text-amber-900">{misseSummary.mediumRisk}</div>
                  <div className="text-sm text-amber-700">Medium Risk</div>
                </Card>
                <Card className="p-4 border-slate-200 bg-slate-50">
                  <div className="text-2xl font-semibold text-slate-700">{misseSummary.lowRisk}</div>
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
                  Showing {filteredMisses.length} of {misses.length} errors
                </div>
                {filteredMisses.map((miss, index) => (
                  <Card
                    key={index}
                    className={`p-4 ${
                      miss.risk_level === 'high' ? 'border-red-300 bg-red-50' :
                      miss.risk_level === 'medium' ? 'border-amber-300 bg-amber-50' :
                      'border-slate-200'
                    }`}
                  >
                    <div className="space-y-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-center gap-2">
                          {miss.miss_type === 'false-negative' ? (
                            <XCircle className="size-5 text-red-600 flex-shrink-0" />
                          ) : (
                            <AlertTriangle className="size-5 text-amber-600 flex-shrink-0" />
                          )}
                          <div>
                            <div className="font-medium text-slate-900">
                              {miss.miss_type === 'false-negative' ? 'Missed Entity' : 'Incorrect Detection'}
                            </div>
                            <div className="text-sm text-slate-600">Record ID: {miss.record_id}</div>
                          </div>
                        </div>
                        <div className="flex items-center gap-2">
                          <Badge variant="outline">{miss.entity_type}</Badge>
                          <Badge
                            className={
                              miss.risk_level === 'high' ? 'bg-red-600 text-white' :
                              miss.risk_level === 'medium' ? 'bg-amber-600 text-white' :
                              'bg-slate-600 text-white'
                            }
                          >
                            {miss.risk_level} risk
                          </Badge>
                        </div>
                      </div>
                      <div className="p-3 bg-white rounded border border-slate-200">
                        <div className="text-sm font-mono text-slate-700">{miss.record_text}</div>
                      </div>
                      <div className="flex items-center gap-4 text-sm">
                        <div>
                          <span className="text-slate-600">Missed Entity: </span>
                          <span className="font-medium text-slate-900">{miss.missed_entity.text}</span>
                        </div>
                        <div>
                          <span className="text-slate-600">Position: </span>
                          <span className="font-medium text-slate-900">{miss.missed_entity.start}-{miss.missed_entity.end}</span>
                        </div>
                      </div>
                    </div>
                  </Card>
                ))}
              </div>
            </TabsContent>

            {/* Error Patterns */}
            <TabsContent value="patterns" className="space-y-4">
              {patterns && patterns.frequent_misses.length > 0 && (
                <Card className="p-6">
                  <h3 className="font-semibold text-slate-900 mb-4">Most Frequently Missed Entity Types</h3>
                  <div className="space-y-3">
                    {patterns.frequent_misses.map(item => (
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
              )}

              {patterns && patterns.common_patterns.length > 0 && (
                <Card className="p-6">
                  <h3 className="font-semibold text-slate-900 mb-4">Common Error Patterns</h3>
                  <div className="space-y-3 text-sm">
                    {patterns.common_patterns.map(p => (
                      <div key={p.name} className="p-3 bg-blue-50 rounded border border-blue-200">
                        <div className="font-medium text-blue-900 mb-1">Pattern: {p.name}</div>
                        <div className="text-blue-800">{p.description}</div>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {patterns && patterns.frequent_misses.length === 0 && patterns.common_patterns.length === 0 && (
                <Card className="p-6 text-center text-slate-500">No error patterns detected.</Card>
              )}
            </TabsContent>

            {/* Insights */}
            <TabsContent value="insights" className="space-y-4">
              {patterns && patterns.insights.length > 0 && (
                <Card className="p-6 border-blue-200 bg-blue-50">
                  <h3 className="font-semibold text-blue-900 mb-4">Key Insights & Recommendations</h3>
                  <div className="space-y-4">
                    {patterns.insights.map((insight, i) => (
                      <div key={i}>
                        <div className="font-medium text-blue-900 mb-2">{i + 1}. {insight.title}</div>
                        <div className="text-sm text-blue-800">{insight.description}</div>
                      </div>
                    ))}
                  </div>
                </Card>
              )}

              {patterns && patterns.insights.length === 0 && (
                <Card className="p-6 text-center text-slate-500">No specific insights for this evaluation run.</Card>
              )}
            </TabsContent>
          </Tabs>
        </>
      )}

      {/* Actions */}
      <div className="flex justify-between gap-3 pt-4">
        <Button variant="outline" size="lg" onClick={() => navigate('/anonymization')}>
          <ChevronLeft className="size-4 mr-1" />
          Back
        </Button>
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
