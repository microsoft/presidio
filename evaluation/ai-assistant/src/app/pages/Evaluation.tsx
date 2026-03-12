<<<<<<< HEAD
import { useState, useEffect, useCallback } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
=======
import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router';
import { Bar, BarChart, CartesianGrid, Legend, ResponsiveContainer, Tooltip, XAxis, YAxis } from 'recharts';
import { Alert, AlertDescription } from '../components/ui/alert';
>>>>>>> ronshakutai/presidio-evaluation-repo
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Checkbox } from '../components/ui/checkbox';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
<<<<<<< HEAD
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
=======
import { AlertTriangle, ArrowRight, BarChart3, CheckCircle, ChevronLeft, Filter, Loader2, Search, XCircle } from 'lucide-react';
import { api } from '../lib/api';

type MissType = 'all' | 'false-positive' | 'false-negative';

type Summary = {
  available_configs: string[];
  selected_configs: string[];
  default_config: string | null;
  per_config: Array<{
    config_name: string;
    overall: {
      precision: number;
      recall: number;
      f1_score: number;
      true_positives: number;
      false_positives: number;
      false_negatives: number;
    };
    misses: Array<{
      record_id: string;
      record_text: string;
      missed_entity: {
        text: string;
        entity_type: string;
        start: number;
        end: number;
      };
      miss_type: 'false-positive' | 'false-negative';
      entity_type: string;
      risk_level: 'high' | 'medium' | 'low';
    }>;
    summary: {
      total_misses: number;
      false_positives: number;
      false_negatives: number;
      high_risk: number;
      medium_risk: number;
      low_risk: number;
    };
  }>;
};

const metricColors = ['#2563eb', '#059669', '#7c3aed', '#ea580c', '#dc2626', '#0f172a'];

export function Evaluation() {
  const navigate = useNavigate();

  const setupConfig = useMemo(() => {
    try {
      const raw = sessionStorage.getItem('setupConfig');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }, []);

  const datasetId = setupConfig?.datasetId as string | undefined;

  const [summary, setSummary] = useState<Summary | null>(null);
  const [availableConfigs, setAvailableConfigs] = useState<string[]>([]);
  const [selectedConfigs, setSelectedConfigs] = useState<string[]>([]);
  const [bootstrapped, setBootstrapped] = useState(false);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const [filterType, setFilterType] = useState<MissType>('all');
>>>>>>> ronshakutai/presidio-evaluation-repo
  const [filterEntityType, setFilterEntityType] = useState<string>('all');
  const [filterRiskLevel, setFilterRiskLevel] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeErrorConfig, setActiveErrorConfig] = useState<string>('');

<<<<<<< HEAD
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
=======
  useEffect(() => {
    if (!datasetId) {
      setError('No dataset selected. Go back to Setup.');
      setLoading(false);
      return;
    }

    let cancelled = false;
    setLoading(true);

    api.evaluation.summary(datasetId)
      .then((data: Summary) => {
        if (cancelled) return;
        setSummary(data);
        setAvailableConfigs(data.available_configs || []);
        setSelectedConfigs(data.selected_configs || []);
        setActiveErrorConfig((current) => current || data.selected_configs?.[0] || data.default_config || '');
        setBootstrapped(true);
        setError(null);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setError(err.message || 'Failed to load evaluation results');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [datasetId]);

  useEffect(() => {
    if (!datasetId || !bootstrapped) return;

    let cancelled = false;
    setLoading(true);

    api.evaluation.summary(datasetId, selectedConfigs)
      .then((data: Summary) => {
        if (cancelled) return;
        setSummary(data);
        setAvailableConfigs(data.available_configs || []);
        setActiveErrorConfig((current) => {
          if (current && data.selected_configs.includes(current)) return current;
          return data.selected_configs?.[0] || data.default_config || '';
        });
        setError(null);
      })
      .catch((err: Error) => {
        if (cancelled) return;
        setError(err.message || 'Failed to refresh evaluation results');
      })
      .finally(() => {
        if (!cancelled) setLoading(false);
      });

    return () => {
      cancelled = true;
    };
  }, [bootstrapped, datasetId, selectedConfigs.join('|')]);

  const activeConfigResult = useMemo(
    () => summary?.per_config.find((item) => item.config_name === activeErrorConfig) ?? summary?.per_config[0] ?? null,
    [activeErrorConfig, summary],
  );

  const filteredMisses = useMemo(() => {
    const misses = activeConfigResult?.misses || [];
    return misses.filter((miss) => {
      if (filterType !== 'all' && miss.miss_type !== filterType) return false;
      if (filterEntityType !== 'all' && miss.entity_type !== filterEntityType) return false;
      if (filterRiskLevel !== 'all' && miss.risk_level !== filterRiskLevel) return false;
      if (searchQuery && !miss.record_text.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  }, [activeConfigResult, filterEntityType, filterRiskLevel, filterType, searchQuery]);

  const entityTypes = useMemo(() => {
    const types = new Set((activeConfigResult?.misses || []).map((miss) => miss.entity_type));
    return ['all', ...Array.from(types).sort()];
  }, [activeConfigResult]);

  const metricChartData = useMemo(() => {
    const metrics = [
      ['Precision', 'precision'],
      ['Recall', 'recall'],
      ['F1 Score', 'f1_score'],
      ['True Positives', 'true_positives'],
      ['False Positives', 'false_positives'],
      ['False Negatives', 'false_negatives'],
    ] as const;

    return metrics.map(([label, key]) => {
      const row: Record<string, string | number> = { metric: label };
      summary?.per_config.forEach((config) => {
        row[config.config_name] = config.overall[key];
      });
      return row;
    });
  }, [summary]);

  const toggleConfig = (configName: string, checked: boolean) => {
    setSelectedConfigs((current) => {
      if (checked) return Array.from(new Set([...current, configName]));
      return current.filter((name) => name !== configName);
    });
>>>>>>> ronshakutai/presidio-evaluation-repo
  };

  const handleContinue = () => {
    navigate('/decision');
  };

  if (loading && !summary) {
    return (
      <div className="max-w-7xl mx-auto py-20 flex items-center justify-center gap-3 text-slate-600">
        <Loader2 className="size-6 animate-spin text-blue-600" />
        Loading evaluation results...
      </div>
    );
  }

  if (error && !summary) {
    return (
      <div className="max-w-7xl mx-auto space-y-6">
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-800">{error}</AlertDescription>
        </Alert>
        <div className="flex justify-between gap-3 pt-4">
          <Button variant="outline" size="lg" onClick={() => navigate('/anonymization')}>
            <ChevronLeft className="size-4 mr-1" />
            Back
          </Button>
        </div>
      </div>
    );
  }

  const isComplete = !isLoading && !error && metrics !== null;

  return (
    <div className="max-w-7xl mx-auto space-y-6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-900 mb-2">Evaluation Dashboard</h2>
          <p className="text-slate-600">
            Compare the selected config outputs against the reviewed final entities from your latest dataset run.
          </p>
        </div>
      </div>

<<<<<<< HEAD
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
=======
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="size-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900">Configs Included in This Evaluation</h3>
>>>>>>> ronshakutai/presidio-evaluation-repo
          </div>
          <p className="text-sm text-slate-600">
            The latest run is selected by default. Enable additional configs to evaluate their combined coverage against the reviewed reference set.
          </p>
          <div className="grid gap-3 md:grid-cols-2 lg:grid-cols-3">
            {availableConfigs.map((configName) => {
              const checked = selectedConfigs.includes(configName);
              const isDefault = summary?.default_config === configName;
              return (
                <label
                  key={configName}
                  className={`flex items-start gap-3 rounded-lg border p-4 cursor-pointer transition-colors ${checked ? 'border-blue-300 bg-blue-50' : 'border-slate-200 bg-white'}`}
                >
                  <Checkbox checked={checked} onCheckedChange={(value) => toggleConfig(configName, !!value)} className="mt-0.5" />
                  <div className="min-w-0">
                    <div className="flex items-center gap-2">
                      <span className="font-medium text-slate-900">{configName}</span>
                      {isDefault && <Badge className="bg-slate-900 text-white">Last run</Badge>}
                    </div>
                    <div className="text-xs text-slate-600 mt-1">
                      {checked ? 'Included in the current evaluation' : 'Excluded from the current evaluation'}
                    </div>
                  </div>
                </label>
              );
            })}
          </div>
          {availableConfigs.length === 0 && (
            <Alert className="border-amber-200 bg-amber-50">
              <AlertDescription className="text-amber-800">
                No saved Presidio config results were found for this dataset yet.
              </AlertDescription>
            </Alert>
          )}
        </div>
      </Card>

      {error && summary && (
        <Alert className="border-amber-200 bg-amber-50">
          <AlertDescription className="text-amber-800">{error}</AlertDescription>
        </Alert>
      )}

<<<<<<< HEAD
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
=======
      {summary && (
>>>>>>> ronshakutai/presidio-evaluation-repo
        <>
          <Card className="p-6 border-green-200 bg-green-50">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="size-5 text-green-700" />
                <h3 className="font-semibold text-green-900">Evaluation Complete</h3>
              </div>
<<<<<<< HEAD

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
=======
              <div className="text-sm text-green-800">
                {summary.per_config.length > 0
                  ? `Currently comparing ${summary.per_config.length} config${summary.per_config.length > 1 ? 's' : ''}: ${summary.per_config.map((item) => item.config_name).join(', ')}`
                  : 'No configs selected. Select at least one config to view metrics.'}
>>>>>>> ronshakutai/presidio-evaluation-repo
              </div>

              <ResponsiveContainer width="100%" height={360}>
                <BarChart data={metricChartData} margin={{ top: 8, right: 8, left: 0, bottom: 24 }}>
                  <CartesianGrid strokeDasharray="3 3" />
                  <XAxis dataKey="metric" />
                  <YAxis />
                  <Tooltip />
                  <Legend />
                  {summary.per_config.map((config, index) => (
                    <Bar
                      key={config.config_name}
                      dataKey={config.config_name}
                      fill={metricColors[index % metricColors.length]}
                      radius={[4, 4, 0, 0]}
                    />
                  ))}
                </BarChart>
              </ResponsiveContainer>
            </div>
          </Card>

<<<<<<< HEAD
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
=======
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center justify-between gap-4">
                <h3 className="font-semibold text-slate-900">Error Explorer</h3>
                <div className="w-full max-w-xs">
                  <Select value={activeErrorConfig} onValueChange={setActiveErrorConfig}>
                    <SelectTrigger>
                      <SelectValue placeholder="Choose config" />
                    </SelectTrigger>
                    <SelectContent>
                      {summary.per_config.map((config) => (
                        <SelectItem key={config.config_name} value={config.config_name}>
                          {config.config_name}
                        </SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
>>>>>>> ronshakutai/presidio-evaluation-repo

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
                <Card className="p-4">
<<<<<<< HEAD
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
=======
                  <div className="text-2xl font-semibold text-slate-900">{activeConfigResult?.summary.total_misses ?? 0}</div>
                  <div className="text-sm text-slate-600">Total Misses</div>
                </Card>
                <Card className="p-4 border-amber-200 bg-amber-50">
                  <div className="text-2xl font-semibold text-amber-900">{activeConfigResult?.summary.false_positives ?? 0}</div>
                  <div className="text-sm text-amber-700">False Positives</div>
                </Card>
                <Card className="p-4 border-red-200 bg-red-50">
                  <div className="text-2xl font-semibold text-red-900">{activeConfigResult?.summary.false_negatives ?? 0}</div>
                  <div className="text-sm text-red-700">False Negatives</div>
                </Card>
                <Card className="p-4 border-red-300 bg-red-100">
                  <div className="text-2xl font-semibold text-red-900">{activeConfigResult?.summary.high_risk ?? 0}</div>
                  <div className="text-sm text-red-700">High Risk</div>
                </Card>
                <Card className="p-4 border-amber-300 bg-amber-100">
                  <div className="text-2xl font-semibold text-amber-900">{activeConfigResult?.summary.medium_risk ?? 0}</div>
                  <div className="text-sm text-amber-700">Medium Risk</div>
                </Card>
>>>>>>> ronshakutai/presidio-evaluation-repo
              </div>

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
                    <Select value={filterType} onValueChange={(val) => setFilterType(val as MissType)}>
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
                        {entityTypes.map((type) => (
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

              <div className="text-sm text-slate-600">
                Showing {filteredMisses.length} of {activeConfigResult?.misses.length ?? 0} errors for {activeConfigResult?.config_name ?? 'the selected config'}
              </div>

              <div className="space-y-3">
<<<<<<< HEAD
                <div className="text-sm text-slate-600">
                  Showing {filteredMisses.length} of {misses.length} errors
                </div>
=======
>>>>>>> ronshakutai/presidio-evaluation-repo
                {filteredMisses.map((miss, index) => (
                  <Card
                    key={`${miss.record_id}-${miss.miss_type}-${miss.missed_entity.start}-${index}`}
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
<<<<<<< HEAD
                          <Badge
                            className={
                              miss.risk_level === 'high' ? 'bg-red-600 text-white' :
                              miss.risk_level === 'medium' ? 'bg-amber-600 text-white' :
                              'bg-slate-600 text-white'
                            }
                          >
=======
                          <Badge className={
                            miss.risk_level === 'high' ? 'bg-red-600 text-white' :
                            miss.risk_level === 'medium' ? 'bg-amber-600 text-white' :
                            'bg-slate-600 text-white'
                          }>
>>>>>>> ronshakutai/presidio-evaluation-repo
                            {miss.risk_level} risk
                          </Badge>
                        </div>
                      </div>
                      <div className="p-3 bg-white rounded border border-slate-200">
                        <div className="text-sm font-mono text-slate-700">{miss.record_text}</div>
                      </div>
                      <div className="flex flex-wrap items-center gap-4 text-sm">
                        <div>
<<<<<<< HEAD
                          <span className="text-slate-600">Missed Entity: </span>
=======
                          <span className="text-slate-600">Entity: </span>
>>>>>>> ronshakutai/presidio-evaluation-repo
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

                {filteredMisses.length === 0 && (
                  <Card className="p-6 text-sm text-slate-600">
                    No errors match the current config selection and filters.
                  </Card>
                )}
              </div>
<<<<<<< HEAD
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
=======
            </div>
          </Card>
>>>>>>> ronshakutai/presidio-evaluation-repo
        </>
      )}

      <div className="flex justify-between gap-3 pt-4">
        <Button variant="outline" size="lg" onClick={() => navigate('/anonymization')}>
          <ChevronLeft className="size-4 mr-1" />
          Back
        </Button>
        <Button size="lg" onClick={handleContinue} disabled={!summary}>
          View Insights
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
