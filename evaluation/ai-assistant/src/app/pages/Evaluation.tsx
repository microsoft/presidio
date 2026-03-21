import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Checkbox } from '../components/ui/checkbox';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { AlertTriangle, ArrowRight, BarChart3, CheckCircle2, ChevronLeft, ChevronRight, Filter, Grid3X3, List, Loader2, Search, XCircle } from 'lucide-react';
import { api } from '../lib/api';

type MissType = 'all' | 'true-positive' | 'false-positive' | 'false-negative';

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
      miss_type: 'true-positive' | 'false-positive' | 'false-negative';
      entity_type: string;
      risk_level: 'high' | 'medium' | 'low';
    }>;
    by_entity_type: Array<{
      type: string;
      precision: number;
      recall: number;
      f1: number;
      true_positives: number;
      false_positives: number;
      false_negatives: number;
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
  const [filterEntityType, setFilterEntityType] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeErrorConfig, setActiveErrorConfig] = useState<string>('');
  const [currentPage, setCurrentPage] = useState(1);
  const pageSize = 10;
  const [showTruePositives, setShowTruePositives] = useState(false);

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
      if (!showTruePositives && miss.miss_type === 'true-positive') return false;
      if (filterType !== 'all' && miss.miss_type !== filterType) return false;
      if (filterEntityType !== 'all' && miss.entity_type !== filterEntityType) return false;
      if (searchQuery && !miss.record_text.toLowerCase().includes(searchQuery.toLowerCase())) return false;
      return true;
    });
  }, [activeConfigResult, filterEntityType, filterType, searchQuery, showTruePositives]);

  // Reset page when filters change
  useEffect(() => {
    setCurrentPage(1);
  }, [filterType, filterEntityType, searchQuery, activeErrorConfig, showTruePositives]);

  // Reset filterType if TP is selected but toggle is turned off
  useEffect(() => {
    if (!showTruePositives && filterType === 'true-positive') {
      setFilterType('all');
    }
  }, [showTruePositives]);

  const totalPages = Math.max(1, Math.ceil(filteredMisses.length / pageSize));
  const pagedMisses = filteredMisses.slice((currentPage - 1) * pageSize, currentPage * pageSize);

  const entityTypes = useMemo(() => {
    const types = new Set((activeConfigResult?.misses || []).map((miss) => miss.entity_type));
    return ['all', ...Array.from(types).sort()];
  }, [activeConfigResult]);

  const toggleConfig = (configName: string, checked: boolean) => {
    setSelectedConfigs((current) => {
      if (checked) return Array.from(new Set([...current, configName]));
      return current.filter((name) => name !== configName);
    });
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
          <Button variant="outline" size="lg" onClick={() => navigate('/human-review')}>
            <ChevronLeft className="size-4 mr-1" />
            Back
          </Button>
        </div>
      </div>
    );
  }

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

      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <BarChart3 className="size-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900">Configs Included in This Evaluation</h3>
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

      {summary && (
        <>
          <Card className="p-6">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <List className="size-5 text-blue-600" />
                <h3 className="font-semibold text-slate-900">Metrics Comparison</h3>
              </div>
              <div className="text-sm text-slate-600">
                {summary.per_config.length > 0
                  ? `Comparing ${summary.per_config.length} config${summary.per_config.length > 1 ? 's' : ''}`
                  : 'No configs selected. Select at least one config to view metrics.'}
              </div>

              {summary.per_config.length > 0 && (
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-200">
                        <th className="text-left py-3 pr-4 font-medium text-slate-600">Config</th>
                        <th className="text-right py-3 px-4 font-medium text-slate-600">Precision</th>
                        <th className="text-right py-3 px-4 font-medium text-slate-600">Recall</th>
                        <th className="text-right py-3 px-4 font-medium text-slate-600">F1 Score</th>
                        <th className="text-right py-3 px-4 font-medium text-slate-600">TP</th>
                        <th className="text-right py-3 px-4 font-medium text-slate-600">FP</th>
                        <th className="text-right py-3 pl-4 font-medium text-slate-600">FN</th>
                      </tr>
                    </thead>
                    <tbody>
                      {summary.per_config.map((config) => (
                        <tr key={config.config_name} className="border-b border-slate-100 last:border-0">
                          <td className="py-3 pr-4 font-medium text-slate-900">{config.config_name}</td>
                          <td className="text-right py-3 px-4 text-slate-700">{config.overall.precision.toFixed(1)}%</td>
                          <td className="text-right py-3 px-4 text-slate-700">{config.overall.recall.toFixed(1)}%</td>
                          <td className="text-right py-3 px-4">
                            <span className={`font-semibold ${
                              config.overall.f1_score >= 80 ? 'text-green-700' :
                              config.overall.f1_score >= 50 ? 'text-amber-700' : 'text-red-700'
                            }`}>
                              {config.overall.f1_score.toFixed(1)}%
                            </span>
                          </td>
                          <td className="text-right py-3 px-4 text-slate-700">{config.overall.true_positives}</td>
                          <td className="text-right py-3 px-4 text-amber-700">{config.overall.false_positives}</td>
                          <td className="text-right py-3 pl-4 text-red-700">{config.overall.false_negatives}</td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              )}
            </div>
          </Card>

          {/* Entity Performance Matrix */}
          {summary.per_config.length > 0 && (() => {
            const allEntityTypes = Array.from(
              new Set(summary.per_config.flatMap(c => c.by_entity_type?.map(e => e.type) ?? []))
            ).sort();
            if (allEntityTypes.length === 0) return null;
            const metricKey = 'f1' as const;
            return (
              <Card className="p-6">
                <div className="space-y-4">
                  <div className="flex items-center gap-2">
                    <Grid3X3 className="size-5 text-purple-600" />
                    <h3 className="font-semibold text-slate-900">Entity Performance Matrix</h3>
                  </div>
                  <div className="text-sm text-slate-600">
                    F1 score per entity type across configs. Hover for details.
                  </div>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-slate-200">
                          <th className="text-left py-3 pr-4 font-medium text-slate-600">Entity Type</th>
                          {summary.per_config.map(c => (
                            <th key={c.config_name} className="text-center py-3 px-3 font-medium text-slate-600">
                              {c.config_name}
                            </th>
                          ))}
                        </tr>
                      </thead>
                      <tbody>
                        {allEntityTypes.map(entityType => (
                          <tr key={entityType} className="border-b border-slate-100 last:border-0">
                            <td className="py-3 pr-4 font-medium text-slate-900 whitespace-nowrap">{entityType}</td>
                            {summary.per_config.map(config => {
                              const entry = config.by_entity_type?.find(e => e.type === entityType);
                              if (!entry) {
                                return (
                                  <td key={config.config_name} className="text-center py-3 px-3">
                                    <span className="text-slate-300">—</span>
                                  </td>
                                );
                              }
                              const f1 = entry[metricKey];
                              const bg = f1 >= 80 ? 'bg-green-100 text-green-800'
                                : f1 >= 50 ? 'bg-amber-100 text-amber-800'
                                : 'bg-red-100 text-red-800';
                              return (
                                <td key={config.config_name} className="text-center py-3 px-3">
                                  <span
                                    className={`inline-block rounded-md px-2.5 py-1.5 text-xs font-semibold cursor-default ${bg}`}
                                    title={`Precision: ${entry.precision.toFixed(1)}%\nRecall: ${entry.recall.toFixed(1)}%\nF1: ${f1.toFixed(1)}%\nTP: ${entry.true_positives}  FP: ${entry.false_positives}  FN: ${entry.false_negatives}`}
                                  >
                                    {f1.toFixed(1)}%
                                  </span>
                                </td>
                              );
                            })}
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>
              </Card>
            );
          })()}

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

              <div className="grid grid-cols-3 gap-4">
                <Card className="p-4">
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
              </div>

              <Card className="p-4">
                <div className="flex items-center gap-3">
                  <Filter className="size-4 text-slate-600" />
                  <div className="flex-1 grid grid-cols-1 md:grid-cols-3 gap-3">
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
                        {showTruePositives && <SelectItem value="true-positive">True Positives</SelectItem>}
                        <SelectItem value="false-positive">False Positives</SelectItem>
                        <SelectItem value="false-negative">False Negatives</SelectItem>
                      </SelectContent>
                    </Select>
                    <label className="flex items-center gap-2 cursor-pointer whitespace-nowrap">
                      <Checkbox checked={showTruePositives} onCheckedChange={(v) => setShowTruePositives(!!v)} />
                      <span className="text-sm text-slate-600">Show True Positives</span>
                    </label>
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
                  </div>
                </div>
              </Card>

              <div className="text-sm text-slate-600">
                Showing {(currentPage - 1) * pageSize + 1}–{Math.min(currentPage * pageSize, filteredMisses.length)} of {filteredMisses.length} results for {activeConfigResult?.config_name ?? 'the selected config'}
              </div>

              <div className="space-y-3">
                {pagedMisses.map((miss, index) => (
                  <Card
                    key={`${miss.record_id}-${miss.miss_type}-${miss.missed_entity.start}-${index}`}
                    className="p-4 border-slate-200"
                  >
                    <div className="space-y-3">
                      <div className="flex items-start justify-between gap-4">
                        <div className="flex items-center gap-2">
                          {miss.miss_type === 'false-negative' ? (
                            <XCircle className="size-5 text-red-600 flex-shrink-0" />
                          ) : miss.miss_type === 'true-positive' ? (
                            <CheckCircle2 className="size-5 text-green-600 flex-shrink-0" />
                          ) : (
                            <AlertTriangle className="size-5 text-amber-600 flex-shrink-0" />
                          )}
                          <div>
                            <div className="font-medium text-slate-900">
                              {miss.miss_type === 'false-negative' ? 'Missed Entity' : miss.miss_type === 'true-positive' ? 'Correct Detection' : 'Incorrect Detection'}
                            </div>
                            <div className="text-sm text-slate-600">Record ID: {miss.record_id}</div>
                          </div>
                        </div>
                        <Badge variant="outline">{miss.entity_type}</Badge>
                      </div>
                      <div className="p-3 bg-white rounded border border-slate-200">
                        <div className="text-sm font-mono text-slate-700">
                          {miss.record_text.substring(0, miss.missed_entity.start)}
                          <mark className={`px-0.5 rounded ${
                            miss.miss_type === 'false-negative'
                              ? 'bg-red-200 text-red-900'
                              : miss.miss_type === 'true-positive'
                              ? 'bg-green-200 text-green-900'
                              : 'bg-amber-200 text-amber-900'
                          }`}>{miss.record_text.substring(miss.missed_entity.start, miss.missed_entity.end)}</mark>
                          {miss.record_text.substring(miss.missed_entity.end)}
                        </div>
                      </div>
                      <div className="flex flex-wrap items-center gap-4 text-sm">
                        <div>
                          <span className="text-slate-600">Entity: </span>
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

                {totalPages > 1 && (
                  <div className="flex items-center justify-center gap-2 pt-2">
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={currentPage <= 1}
                      onClick={() => setCurrentPage((p) => p - 1)}
                    >
                      <ChevronLeft className="size-4" />
                    </Button>
                    <span className="text-sm text-slate-600">
                      Page {currentPage} of {totalPages}
                    </span>
                    <Button
                      variant="outline"
                      size="sm"
                      disabled={currentPage >= totalPages}
                      onClick={() => setCurrentPage((p) => p + 1)}
                    >
                      <ChevronRight className="size-4" />
                    </Button>
                  </div>
                )}

                {filteredMisses.length === 0 && (
                  <Card className="p-6 text-sm text-slate-600">
                    No results match the current config selection and filters.
                  </Card>
                )}
              </div>
            </div>
          </Card>
        </>
      )}

      <div className="flex justify-between gap-3 pt-4">
        <Button variant="outline" size="lg" onClick={() => navigate('/human-review')}>
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
