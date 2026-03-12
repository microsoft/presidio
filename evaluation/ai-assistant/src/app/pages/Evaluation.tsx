import { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { Button } from '../components/ui/button';
import { Card } from '../components/ui/card';
import { Checkbox } from '../components/ui/checkbox';
import { Input } from '../components/ui/input';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
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
    by_entity_type: Array<{
      type: string;
      precision: number;
      recall: number;
      f1: number;
    }>;
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

const metricColors = ['#2563eb', '#059669', '#7c3aed', '#ea580c', '#dc2626', '#0f172a'] as const;

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
  const [filterRiskLevel, setFilterRiskLevel] = useState<string>('all');
  const [searchQuery, setSearchQuery] = useState('');
  const [activeErrorConfig, setActiveErrorConfig] = useState<string>('');

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

  const allEntityTypes = useMemo(() => {
    const types = new Set<string>();
    summary?.per_config.forEach((config) => {
      config.by_entity_type?.forEach((e) => types.add(e.type));
    });
    return Array.from(types).sort();
  }, [summary]);

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
          <Button variant="outline" size="lg" onClick={() => navigate('/anonymization')}>
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
          <Card className="p-6 border-green-200 bg-green-50">
            <div className="space-y-4">
              <div className="flex items-center gap-2">
                <CheckCircle className="size-5 text-green-700" />
                <h3 className="font-semibold text-green-900">Evaluation Complete</h3>
              </div>
              <div className="text-sm text-green-800">
                {summary.per_config.length > 0
                  ? `Currently comparing ${summary.per_config.length} config${summary.per_config.length > 1 ? 's' : ''}: ${summary.per_config.map((item) => item.config_name).join(', ')}`
                  : 'No configs selected. Select at least one config to view metrics.'}
              </div>
            </div>
          </Card>

          {/* Overall Metrics Per Config */}
          {summary.per_config.map((config, index) => (
            <Card key={config.config_name} className="p-6">
              <div className="space-y-4">
                <div className="flex items-center gap-2">
                  <div className="size-3 rounded-full" style={{ background: metricColors[index % metricColors.length] }} />
                  <h3 className="font-semibold text-slate-900">{config.config_name}</h3>
                </div>
                <div className="grid grid-cols-3 md:grid-cols-6 gap-4">
                  <div className="text-center p-3 rounded-lg bg-blue-50">
                    <div className="text-2xl font-semibold text-blue-700">{config.overall.precision}%</div>
                    <div className="text-xs text-blue-600 mt-1">Precision</div>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-emerald-50">
                    <div className="text-2xl font-semibold text-emerald-700">{config.overall.recall}%</div>
                    <div className="text-xs text-emerald-600 mt-1">Recall</div>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-violet-50">
                    <div className="text-2xl font-semibold text-violet-700">{config.overall.f1_score}%</div>
                    <div className="text-xs text-violet-600 mt-1">F Score</div>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-slate-50">
                    <div className="text-2xl font-semibold text-slate-700">{config.overall.true_positives}</div>
                    <div className="text-xs text-slate-600 mt-1">True Positives</div>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-amber-50">
                    <div className="text-2xl font-semibold text-amber-700">{config.overall.false_positives}</div>
                    <div className="text-xs text-amber-600 mt-1">False Positives</div>
                  </div>
                  <div className="text-center p-3 rounded-lg bg-red-50">
                    <div className="text-2xl font-semibold text-red-700">{config.overall.false_negatives}</div>
                    <div className="text-xs text-red-600 mt-1">False Negatives</div>
                  </div>
                </div>
              </div>
            </Card>
          ))}

          {/* Per-Entity Metrics Table */}
          {allEntityTypes.length > 0 && (
            <Card className="p-6">
              <div className="space-y-4">
                <h3 className="font-semibold text-slate-900">Metrics Per Entity Type</h3>
                <div className="overflow-x-auto">
                  <table className="w-full text-sm">
                    <thead>
                      <tr className="border-b border-slate-200">
                        <th className="text-left py-2 pr-4 font-medium text-slate-600">Entity Type</th>
                        {summary.per_config.map((config, index) => (
                          <th key={config.config_name} colSpan={3} className="text-center py-2 px-2 font-medium" style={{ color: metricColors[index % metricColors.length] }}>
                            {config.config_name}
                          </th>
                        ))}
                      </tr>
                      <tr className="border-b border-slate-100">
                        <th />
                        {summary.per_config.map((config) => (
                          <>
                            <th key={`${config.config_name}-p`} className="text-center py-1 px-2 text-xs font-medium text-slate-500">Prec</th>
                            <th key={`${config.config_name}-r`} className="text-center py-1 px-2 text-xs font-medium text-slate-500">Rec</th>
                            <th key={`${config.config_name}-f`} className="text-center py-1 px-2 text-xs font-medium text-slate-500">F</th>
                          </>
                        ))}
                      </tr>
                    </thead>
                    <tbody>
                      {allEntityTypes.map((entityType) => (
                        <tr key={entityType} className="border-b border-slate-100 hover:bg-slate-50">
                          <td className="py-2 pr-4 font-medium text-slate-800">{entityType}</td>
                          {summary.per_config.map((config) => {
                            const entity = config.by_entity_type?.find((e) => e.type === entityType);
                            return (
                              <>
                                <td key={`${config.config_name}-${entityType}-p`} className="text-center py-2 px-2 tabular-nums">
                                  {entity ? `${entity.precision}%` : <span className="text-slate-300">—</span>}
                                </td>
                                <td key={`${config.config_name}-${entityType}-r`} className="text-center py-2 px-2 tabular-nums">
                                  {entity ? `${entity.recall}%` : <span className="text-slate-300">—</span>}
                                </td>
                                <td key={`${config.config_name}-${entityType}-f`} className="text-center py-2 px-2 tabular-nums font-medium">
                                  {entity ? `${entity.f1}%` : <span className="text-slate-300">—</span>}
                                </td>
                              </>
                            );
                          })}
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
              </div>
            </Card>
          )}

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

              <div className="grid grid-cols-2 md:grid-cols-5 gap-4">
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
                <Card className="p-4 border-red-300 bg-red-100">
                  <div className="text-2xl font-semibold text-red-900">{activeConfigResult?.summary.high_risk ?? 0}</div>
                  <div className="text-sm text-red-700">High Risk</div>
                </Card>
                <Card className="p-4 border-amber-300 bg-amber-100">
                  <div className="text-2xl font-semibold text-amber-900">{activeConfigResult?.summary.medium_risk ?? 0}</div>
                  <div className="text-sm text-amber-700">Medium Risk</div>
                </Card>
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
                          <Badge className={
                            miss.risk_level === 'high' ? 'bg-red-600 text-white' :
                            miss.risk_level === 'medium' ? 'bg-amber-600 text-white' :
                            'bg-slate-600 text-white'
                          }>
                            {miss.risk_level} risk
                          </Badge>
                        </div>
                      </div>
                      <div className="p-3 bg-white rounded border border-slate-200">
                        <div className="text-sm font-mono text-slate-700">{miss.record_text}</div>
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

                {filteredMisses.length === 0 && (
                  <Card className="p-6 text-sm text-slate-600">
                    No errors match the current config selection and filters.
                  </Card>
                )}
              </div>
            </div>
          </Card>
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
