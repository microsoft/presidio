import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { Database, ArrowRight, FileText, CheckCircle, Loader2, X, Plus, Pencil, Trash2, Shield, Sparkles, AlertTriangle } from 'lucide-react';
import { api } from '../lib/api';
import { FileDropzone } from '../components/FileDropzone';
import type { ComplianceFramework, UploadedDataset } from '../types';

export function Setup() {
  const navigate = useNavigate();
  const [datasets, setDatasets] = useState<UploadedDataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [datasetFile, setDatasetFile] = useState<File | null>(null);
  const [datasetPath, setDatasetPath] = useState('');
  const [datasetInputMode, setDatasetInputMode] = useState<'file' | 'path'>('file');
  const [datasetName, setDatasetName] = useState('');
  const [datasetDescription, setDatasetDescription] = useState('');
  const [textColumn, setTextColumn] = useState('text');
  const [entitiesColumn, setEntitiesColumn] = useState('');
  const [csvColumns, setCsvColumns] = useState<string[]>([]);
  const [columnsLoading, setColumnsLoading] = useState(false);
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [previewRecords, setPreviewRecords] = useState<any[]>([]);
  const [complianceFrameworks, setComplianceFrameworks] = useState<ComplianceFramework[]>(['general']);
  const [cloudRestriction, setCloudRestriction] = useState<'allowed' | 'restricted'>('allowed');
  const [runPresidio, setRunPresidio] = useState(true);
  const [runLlm, setRunLlm] = useState(true);
  const [editingName, setEditingName] = useState(false);
  const [editNameValue, setEditNameValue] = useState('');

  // Presidio config
  const [savedConfigs, setSavedConfigs] = useState<{ name: string; path: string | null }[]>([]);
  const [selectedConfig, setSelectedConfig] = useState('default_spacy');
  const [showAddConfig, setShowAddConfig] = useState(false);
  const [newConfigName, setNewConfigName] = useState('');
  const [newConfigFile, setNewConfigFile] = useState<File | null>(null);
  const [newConfigPath, setNewConfigPath] = useState('');
  const [newConfigInputMode, setNewConfigInputMode] = useState<'file' | 'path'>('file');
  const [presidioConfigError, setPresidioConfigError] = useState<string | null>(null);

  // LLM config
  const [models, setModels] = useState<{ id: string; label: string; provider: string }[]>([]);
  const [selectedModel, setSelectedModel] = useState('gpt-5.4');
  const [llmEnvReady, setLlmEnvReady] = useState<boolean | null>(null);

  // Fetch saved datasets on mount and restore previous selection
  useEffect(() => {
    api.datasets.saved().then(saved => {
      if (saved.length > 0) {
        setDatasets(saved);
        // Restore previously selected dataset from sessionStorage
        const stored = sessionStorage.getItem('setupConfig');
        if (stored) {
          try {
            const parsed = JSON.parse(stored);
            if (parsed.datasetId && saved.some((d: UploadedDataset) => d.id === parsed.datasetId)) {
              setSelectedDatasetId(parsed.datasetId);
              api.datasets.preview(parsed.datasetId).then(setPreviewRecords).catch(() => {});
            }
          } catch { /* ignore */ }
        }
      }
    }).catch(() => {});
  }, []);

  // Fetch Presidio configs and LLM models on mount
  useEffect(() => {
    api.presidio.configs().then(configs => setSavedConfigs(configs)).catch(() => {});
    Promise.all([api.llm.models(), api.llm.settings()]).then(([modelList, settings]) => {
      setModels(modelList);
      setSelectedModel(settings.deployment_name || 'gpt-4o');
      setLlmEnvReady(settings.env_ready);
    }).catch(() => setLlmEnvReady(false));
  }, []);

  const selectedDataset = datasets.find(d => d.id === selectedDatasetId) ?? null;
  const canProceed = selectedDataset !== null;

  const handleSelectDataset = async (value: string) => {
    setSelectedDatasetId(value);
    setShowAddForm(false);
    setPreviewRecords([]);
    setEditingName(false);

    try {
      const preview = await api.datasets.preview(value);
      setPreviewRecords(preview);
    } catch { /* ignore */ }
  };

  const handleLoadDataset = async () => {
    if (datasetInputMode === 'file' && !datasetFile) {
      setLoadError('Please select a CSV file.');
      return;
    }
    if (datasetInputMode === 'path' && !datasetPath.trim()) {
      setLoadError('Please enter a file path.');
      return;
    }

    const proposedName = datasetName.trim() || (datasetInputMode === 'file' ? datasetFile!.name.replace(/\.csv$/i, '') : datasetPath.trim().split('/').pop()?.replace(/\.csv$/i, '') || 'dataset');
    const nameExists = datasets.some(ds => ds.name.toLowerCase() === proposedName.toLowerCase());
    if (nameExists) {
      setLoadError(`A dataset named "${proposedName}" already exists. Please choose a different name.`);
      return;
    }

    setLoading(true);
    setLoadError(null);
    try {
      let dataset: UploadedDataset;
      if (datasetInputMode === 'path') {
        dataset = await api.datasets.load({
          path: datasetPath.trim(),
          format: 'csv',
          text_column: textColumn.trim() || 'text',
          entities_column: entitiesColumn.trim() || undefined,
          name: datasetName.trim() || undefined,
          description: datasetDescription.trim() || undefined,
        });
      } else {
        dataset = await api.datasets.upload(datasetFile!, {
          text_column: textColumn.trim() || 'text',
          entities_column: entitiesColumn.trim() || undefined,
          name: datasetName.trim() || undefined,
          description: datasetDescription.trim() || undefined,
        });
      }

      setDatasets(prev => [...prev, dataset]);
      setSelectedDatasetId(dataset.id);
      setShowAddForm(false);

      const preview = await api.datasets.preview(dataset.id);
      setPreviewRecords(preview);

      // Reset form fields
      setDatasetFile(null);
      setDatasetPath('');
      setDatasetName('');
      setDatasetDescription('');
      setTextColumn('text');
      setEntitiesColumn('');
      setCsvColumns([]);
    } catch (err: any) {
      setLoadError(err.message || 'Failed to load dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveConfig = async () => {
    const name = newConfigName.trim();
    if (!name) return;
    if (newConfigInputMode === 'file' && !newConfigFile) return;
    if (newConfigInputMode === 'path' && !newConfigPath.trim()) return;
    try {
      let res;
      if (newConfigInputMode === 'path') {
        res = await api.presidio.saveConfig(name, newConfigPath.trim());
      } else {
        res = await api.presidio.uploadConfig(newConfigFile!, name);
      }
      setSavedConfigs(res.configs);
      setSelectedConfig(name);
      setNewConfigName('');
      setNewConfigFile(null);
      setNewConfigPath('');
      setShowAddConfig(false);
    } catch (err: any) {
      setPresidioConfigError(err.message ?? 'Failed to save config');
    }
  };

  const handleDeleteConfig = async (name: string) => {
    try {
      const res = await api.presidio.deleteConfig(name);
      setSavedConfigs(res.configs);
      if (selectedConfig === name) setSelectedConfig('default_spacy');
    } catch (err: any) {
      setPresidioConfigError(err.message ?? 'Failed to delete config');
    }
  };

  const handleContinue = () => {
    if (canProceed && selectedDataset) {
      const presidioConfig = savedConfigs.find(c => c.name === selectedConfig);
      const config = {
        datasetId: selectedDataset.id,
        complianceFrameworks,
        cloudRestriction,
        runPresidio,
        runLlm,
        hasDatasetEntities: selectedDataset.has_entities,
        hasFinalEntities: selectedDataset.has_final_entities ?? false,
        presidioConfigName: selectedConfig,
        presidioConfigPath: presidioConfig?.path ?? null,
        llmModel: selectedModel,
      };
      sessionStorage.setItem('setupConfig', JSON.stringify(config));
      sessionStorage.setItem('datasetRecordCount', String(selectedDataset.record_count));
      navigate('/anonymization');
    }
  };

  return (
    <div className="max-w-4xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">Input & Setup</h2>
        <p className="text-slate-600">
          Select an existing dataset or load a new input file to start the evaluation workflow.
        </p>
      </div>

      {/* Dataset Selection */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Database className="size-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900">Dataset</h3>
          </div>

          {/* Dataset Dropdown */}
          <div>
            <Label htmlFor="dataset-select">Select a dataset</Label>
            <div className="flex gap-2 mt-1">
              <Select value={selectedDatasetId} onValueChange={handleSelectDataset} disabled={showAddForm}>
                <SelectTrigger className="flex-1" id="dataset-select">
                  <SelectValue placeholder="Choose a dataset…" />
                </SelectTrigger>
                <SelectContent>
                  {datasets.map(ds => (
                    <SelectItem key={ds.id} value={ds.id}>
                      {ds.name} — {ds.record_count.toLocaleString()} records
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button size="icon" variant="outline" onClick={() => setShowAddForm(!showAddForm)} title="Add new dataset">
                <Plus className="size-4" />
              </Button>
            </div>
          </div>

          {/* Large dataset warning */}
          {selectedDataset && selectedDataset.record_count > 200 && !showAddForm && (
            <Alert className="border-amber-200 bg-amber-50">
              <AlertTriangle className="size-4 text-amber-600" />
              <AlertDescription className="text-sm text-amber-800">
                This dataset has <strong>{selectedDataset.record_count.toLocaleString()}</strong> records. Processing a large number of records may take a while.
              </AlertDescription>
            </Alert>
          )}

          {/* Add Dataset Form */}
          {showAddForm && (
            <div className="space-y-4 p-4 bg-slate-50 border border-slate-200 rounded-lg">
              <div className="flex items-center justify-between">
                <Label className="font-medium text-slate-900">Load Dataset from File</Label>
                <Button size="sm" variant="ghost" onClick={() => { setShowAddForm(false); setLoadError(null); }}>
                  <X className="size-4" />
                </Button>
              </div>

              <div className="space-y-3">
                <div>
                  <Label htmlFor="dataset-name">Dataset Name <span className="text-slate-400">(optional)</span></Label>
                  <Input
                    id="dataset-name"
                    placeholder="e.g. Patient-Records-Q4"
                    value={datasetName}
                    onChange={(e) => {
                      const v = e.target.value;
                      if (v === '' || /^[A-Za-z0-9][A-Za-z0-9 _.\-]*$/.test(v)) setDatasetName(v);
                    }}
                    className="mt-1 text-sm"
                  />
                  <p className="text-xs text-slate-400 mt-1">Letters, numbers, hyphens, underscores, and dots only.</p>
                </div>

                <div>
                  <Label htmlFor="dataset-description">Description <span className="text-slate-400">(optional)</span></Label>
                  <Input
                    id="dataset-description"
                    placeholder="Brief description of the dataset contents"
                    value={datasetDescription}
                    onChange={(e) => setDatasetDescription(e.target.value)}
                    className="mt-1 text-sm"
                  />
                </div>

                <div>
                  <div className="flex items-center justify-between mb-1">
                    <Label>CSV File</Label>
                    <button
                      type="button"
                      className="text-xs text-blue-600 hover:underline"
                      onClick={() => { setDatasetInputMode(datasetInputMode === 'file' ? 'path' : 'file'); setDatasetFile(null); setDatasetPath(''); }}
                    >
                      {datasetInputMode === 'file' ? 'Enter file path instead' : 'Upload file instead'}
                    </button>
                  </div>
                  {datasetInputMode === 'file' ? (
                    <FileDropzone
                      accept=".csv"
                      label="Drop CSV dataset file here or click to browse"
                      onFile={async (f) => {
                        setDatasetFile(f);
                        setCsvColumns([]);
                        setTextColumn('');
                        if (f) {
                          setColumnsLoading(true);
                          try {
                            const { columns } = await api.datasets.columns(f);
                            setCsvColumns(columns);
                            setTextColumn(columns.includes('text') ? 'text' : columns[0] || '');
                          } catch { /* ignore */ }
                          setColumnsLoading(false);
                        }
                      }}
                    />
                  ) : (
                    <Input
                      placeholder="/path/to/dataset.csv"
                      value={datasetPath}
                      onChange={(e) => setDatasetPath(e.target.value)}
                      onBlur={async () => {
                        const p = datasetPath.trim();
                        if (p && p.toLowerCase().endsWith('.csv')) {
                          setCsvColumns([]);
                          setTextColumn('');
                          setColumnsLoading(true);
                          try {
                            const { columns } = await api.datasets.columnsFromPath(p);
                            setCsvColumns(columns);
                            setTextColumn(columns.includes('text') ? 'text' : columns[0] || '');
                          } catch { /* ignore */ }
                          setColumnsLoading(false);
                        }
                      }}
                      className="text-sm"
                    />
                  )}
                </div>

                {csvColumns.length > 0 && (
                  <div className="grid grid-cols-2 gap-3">
                    <div>
                      <Label htmlFor="text-col">Text Column</Label>
                      <Select value={textColumn} onValueChange={setTextColumn}>
                        <SelectTrigger className="mt-1 text-sm">
                          <SelectValue placeholder="Select text column…" />
                        </SelectTrigger>
                        <SelectContent>
                          {csvColumns.map(col => (
                            <SelectItem key={col} value={col}>{col}</SelectItem>
                          ))}
                        </SelectContent>
                      </Select>
                    </div>
                  </div>
                )}
                {columnsLoading && (
                  <div className="flex items-center gap-2 text-sm text-slate-500">
                    <Loader2 className="size-4 animate-spin" />
                    Reading columns…
                  </div>
                )}

                {loadError && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertDescription className="text-red-800 text-sm">{loadError}</AlertDescription>
                  </Alert>
                )}

                <Button onClick={handleLoadDataset} disabled={loading || columnsLoading || !textColumn || (datasetInputMode === 'file' ? !datasetFile : !datasetPath.trim())}>
                  {loading ? (
                    <>
                      <Loader2 className="size-4 mr-2 animate-spin" />
                      Loading...
                    </>
                  ) : (
                    'Load Dataset'
                  )}
                </Button>
              </div>
            </div>
          )}

          {/* Selected dataset summary */}
          {selectedDataset && !showAddForm && (
            <div className="space-y-4">
              <div className="p-4 bg-green-50 border border-green-200 rounded-lg">
                <div className="flex items-start gap-3">
                  <CheckCircle className="size-5 text-green-600 mt-0.5" />
                  <div className="flex-1">
                    <div className="flex items-center gap-2">
                      {editingName ? (
                        <form
                          className="flex items-center gap-2"
                          onSubmit={async (e) => {
                            e.preventDefault();
                            if (!editNameValue.trim()) return;
                            try {
                              const updated = await api.datasets.rename(selectedDataset.id, editNameValue.trim());
                              setDatasets(prev => prev.map(d => d.id === updated.id ? updated : d));
                              setEditingName(false);
                            } catch { /* ignore */ }
                          }}
                        >
                          <Input
                            value={editNameValue}
                            onChange={(e) => setEditNameValue(e.target.value)}
                            className="h-7 text-sm w-56"
                            autoFocus
                          />
                          <Button type="submit" size="sm" variant="ghost" className="h-7 px-2">
                            <CheckCircle className="size-3.5" />
                          </Button>
                          <Button type="button" size="sm" variant="ghost" className="h-7 px-2" onClick={() => setEditingName(false)}>
                            <X className="size-3.5" />
                          </Button>
                        </form>
                      ) : (
                        <>
                          <span className="font-medium text-green-900">{selectedDataset.name}</span>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-6 px-1.5 text-green-700 hover:text-green-900"
                            onClick={() => { setEditingName(true); setEditNameValue(selectedDataset.name); }}
                          >
                            <Pencil className="size-3" />
                          </Button>
                          <Button
                            size="sm"
                            variant="ghost"
                            className="h-6 px-1.5 text-red-500 hover:text-red-700"
                            onClick={async () => {
                              try {
                                await api.datasets.remove(selectedDataset.id);
                                setDatasets(prev => prev.filter(d => d.id !== selectedDataset.id));
                                setSelectedDatasetId('');
                                setPreviewRecords([]);
                              } catch { /* ignore */ }
                            }}
                          >
                            <Trash2 className="size-3" />
                          </Button>
                        </>
                      )}
                    </div>
                    <div className="text-sm text-green-800 mt-1 space-y-0.5">
                      {selectedDataset.description && (
                        <div className="text-green-700 italic">{selectedDataset.description}</div>
                      )}
                      <div>{selectedDataset.record_count.toLocaleString()} records • {selectedDataset.format.toUpperCase()} format</div>
                      <div className="text-xs text-green-700 font-mono truncate">{selectedDataset.path}</div>
                      <div>
                        {selectedDataset.has_final_entities ? (
                          <span className="text-amber-700 font-medium">✓ Contains golden dataset entities (from previous review)</span>
                        ) : (
                          <span className="text-slate-600">Text only — no pre-identified entities</span>
                        )}
                      </div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Preview Records */}
              {previewRecords.length > 0 && (
                <div>
                  <Label className="mb-2 block">Preview (first {previewRecords.length} records)</Label>
                  <div className="space-y-2 max-h-60 overflow-y-auto">
                    {previewRecords.map((record: any, i: number) => (
                      <div key={i} className="p-3 bg-slate-50 border border-slate-200 rounded text-sm">
                        <div className="flex items-start gap-2">
                          <FileText className="size-4 text-slate-400 mt-0.5 flex-shrink-0" />
                          <div className="flex-1 min-w-0">
                            <p className="text-slate-800 line-clamp-2">{record.text}</p>
                            {(() => {
                              const entities = record.dataset_entities?.length > 0
                                ? record.dataset_entities
                                : record.final_entities?.length > 0
                                  ? record.final_entities
                                  : null;
                              return entities && (
                                <div className="flex flex-wrap gap-1 mt-1">
                                  {entities.map((e: any, j: number) => (
                                    <span key={j} className="inline-block px-1.5 py-0.5 bg-amber-100 text-amber-800 text-xs rounded">
                                      {e.entity_type}: {e.text}
                                    </span>
                                  ))}
                                </div>
                              );
                            })()}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

            </div>
          )}
        </div>
      </Card>

      {/* Presidio Configuration */}
      <Card className={`p-6 ${!runPresidio ? 'opacity-60' : ''}`}>
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Shield className="size-5 text-blue-600" />
              <h3 className="font-semibold text-slate-900">Presidio Configuration</h3>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="run-presidio"
                checked={runPresidio}
                onCheckedChange={(checked) => setRunPresidio(checked === true)}
              />
              <Label htmlFor="run-presidio" className="text-sm font-medium cursor-pointer">Enable</Label>
            </div>
          </div>

          {runPresidio && (<>
          <div className="space-y-1.5">
            <Label className="text-xs font-medium">Configuration</Label>
            <div className="flex gap-2">
              <Select value={selectedConfig} onValueChange={setSelectedConfig}>
                <SelectTrigger className="flex-1">
                  <SelectValue />
                </SelectTrigger>
                <SelectContent>
                  {savedConfigs.map((c) => (
                    <SelectItem key={c.name} value={c.name}>
                      {c.name}
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
              <Button size="icon" variant="outline" onClick={() => setShowAddConfig(!showAddConfig)} title="Add new config">
                <Plus className="size-4" />
              </Button>
              {selectedConfig !== 'default_spacy' && (
                <Button size="icon" variant="outline" onClick={() => handleDeleteConfig(selectedConfig)} title="Delete config">
                  <Trash2 className="size-4" />
                </Button>
              )}
            </div>
          </div>

          {showAddConfig && (
            <div className="space-y-2 border rounded-md p-3 bg-slate-50">
              <Label className="text-xs font-medium">New Configuration</Label>
              <Input
                placeholder="Config name (e.g. transformer-stanford)"
                value={newConfigName}
                onChange={(e) => {
                  const v = e.target.value;
                  if (v === '' || /^[A-Za-z0-9][A-Za-z0-9 _.\-]*$/.test(v)) setNewConfigName(v);
                }}
                className="text-sm"
              />
              <p className="text-xs text-slate-400">Letters, numbers, hyphens, underscores, and dots only.</p>
              <div className="flex items-center justify-between mb-1">
                <Label className="text-xs font-medium">YAML File</Label>
                <button
                  type="button"
                  className="text-xs text-blue-600 hover:underline"
                  onClick={() => { setNewConfigInputMode(newConfigInputMode === 'file' ? 'path' : 'file'); setNewConfigFile(null); setNewConfigPath(''); }}
                >
                  {newConfigInputMode === 'file' ? 'Enter file path instead' : 'Upload file instead'}
                </button>
              </div>
              {newConfigInputMode === 'file' ? (
                <FileDropzone
                  accept=".yml,.yaml"
                  label="Drop YAML config file here or click to browse"
                  onFile={setNewConfigFile}
                />
              ) : (
                <Input
                  placeholder="/path/to/config.yml"
                  value={newConfigPath}
                  onChange={(e) => setNewConfigPath(e.target.value)}
                  className="text-sm"
                />
              )}
              <div className="flex gap-2">
                <Button size="sm" variant="outline" onClick={() => { setShowAddConfig(false); setNewConfigName(''); setNewConfigFile(null); setNewConfigPath(''); }} className="flex-1">
                  Cancel
                </Button>
                <Button size="sm" onClick={handleSaveConfig} disabled={!newConfigName.trim() || (newConfigInputMode === 'file' ? !newConfigFile : !newConfigPath.trim())} className="flex-1">
                  Save Config
                </Button>
              </div>
            </div>
          )}

          {presidioConfigError && (
            <Alert className="border-red-200 bg-red-50">
              <AlertTriangle className="size-4 text-red-600" />
              <AlertDescription className="text-sm text-red-800">{presidioConfigError}</AlertDescription>
            </Alert>
          )}
          </>)}
        </div>
      </Card>

      {/* LLM Configuration */}
      <Card className={`p-6 ${!runLlm ? 'opacity-60' : ''}`}>
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Sparkles className="size-5 text-purple-600" />
              <h3 className="font-semibold text-slate-900">LLM Configuration</h3>
            </div>
            <div className="flex items-center gap-2">
              <Checkbox
                id="run-llm"
                checked={runLlm}
                onCheckedChange={(checked) => setRunLlm(checked === true)}
              />
              <Label htmlFor="run-llm" className="text-sm font-medium cursor-pointer">Enable</Label>
            </div>
          </div>

          {runLlm && (<>
          {llmEnvReady === false ? (
            <Alert className="border-amber-200 bg-amber-50">
              <AlertTriangle className="size-4 text-amber-600" />
              <AlertDescription>
                <p className="text-sm text-amber-900">
                  <strong>Azure OpenAI endpoint is required.</strong>{' '}
                  Add it to the <code className="bg-amber-100 px-1 rounded text-xs">backend/.env</code> file:
                </p>
                <pre className="mt-2 text-xs bg-amber-100/60 rounded p-2 text-amber-900 font-mono">
{`PRESIDIO_EVAL_AZURE_ENDPOINT=https://your-resource.openai.azure.com

# Option A — API key auth:
PRESIDIO_EVAL_AZURE_API_KEY=your-api-key-here

# Option B — leave API key empty to use
# DefaultAzureCredential (managed identity / az login)`}
                </pre>
                <p className="text-xs text-amber-700 mt-2">
                  Then restart the backend server. See <code className="bg-amber-100 px-1 rounded">.env.example</code> for reference.
                </p>
              </AlertDescription>
            </Alert>
          ) : llmEnvReady === null ? (
            <div className="flex items-center gap-2 text-sm text-slate-500">
              <Loader2 className="size-4 animate-spin" /> Loading configuration…
            </div>
          ) : (
            <div className="space-y-1.5">
              <Label htmlFor="model-select" className="text-xs font-medium">Model Deployment</Label>
              <Select value={selectedModel} onValueChange={setSelectedModel}>
                <SelectTrigger id="model-select">
                  <SelectValue placeholder="Select a model" />
                </SelectTrigger>
                <SelectContent>
                  {models.map((m) => (
                    <SelectItem key={m.id} value={m.id}>
                      {m.label} <span className="text-slate-400 ml-1">— {m.provider}</span>
                    </SelectItem>
                  ))}
                </SelectContent>
              </Select>
            </div>
          )}
          </>)}
        </div>
      </Card>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4">
        <Button
          size="lg"
          onClick={handleContinue}
          disabled={!canProceed || (!runPresidio && !runLlm)}
        >
          Continue
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
