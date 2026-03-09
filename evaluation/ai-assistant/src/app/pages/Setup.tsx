import { useEffect, useState } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { Input } from '../components/ui/input';
import { Checkbox } from '../components/ui/checkbox';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Database, Shield, ArrowRight, Cloud, FileText, CheckCircle, Loader2, X, Plus, Pencil, Trash2 } from 'lucide-react';
import { api } from '../lib/api';
import type { ComplianceFramework, UploadedDataset } from '../types';

export function Setup() {
  const navigate = useNavigate();
  const [datasets, setDatasets] = useState<UploadedDataset[]>([]);
  const [selectedDatasetId, setSelectedDatasetId] = useState('');
  const [showAddForm, setShowAddForm] = useState(false);
  const [filePath, setFilePath] = useState('');
  const [fileFormat, setFileFormat] = useState<'csv' | 'json'>('csv');
  const [datasetName, setDatasetName] = useState('');
  const [datasetDescription, setDatasetDescription] = useState('');
  const [textColumn, setTextColumn] = useState('text');
  const [entitiesColumn, setEntitiesColumn] = useState('');
  const [loading, setLoading] = useState(false);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [previewRecords, setPreviewRecords] = useState<any[]>([]);
  const [complianceFrameworks, setComplianceFrameworks] = useState<ComplianceFramework[]>(['general']);
  const [cloudRestriction, setCloudRestriction] = useState<'allowed' | 'restricted'>('allowed');
  const [runPresidio, setRunPresidio] = useState(true);
  const [runLlm, setRunLlm] = useState(true);
  const [editingName, setEditingName] = useState(false);
  const [editNameValue, setEditNameValue] = useState('');

  // Fetch saved datasets on mount
  useEffect(() => {
    api.datasets.saved().then(saved => {
      if (saved.length > 0) setDatasets(saved);
    }).catch(() => {});
  }, []);

  const selectedDataset = datasets.find(d => d.id === selectedDatasetId) ?? null;
  const canProceed = selectedDataset !== null;

  const handleSelectDataset = async (value: string) => {
    if (value === '__add_new__') {
      setShowAddForm(true);
      return;
    }
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
    if (!filePath.trim()) {
      setLoadError('Please provide an absolute file path.');
      return;
    }

    setLoading(true);
    setLoadError(null);
    try {
      const dataset: UploadedDataset = await api.datasets.load({
        path: filePath.trim(),
        format: fileFormat,
        text_column: textColumn.trim() || 'text',
        entities_column: entitiesColumn.trim() || undefined,
        name: datasetName.trim() || undefined,
        description: datasetDescription.trim() || undefined,
      });

      setDatasets(prev => [...prev, dataset]);
      setSelectedDatasetId(dataset.id);
      setShowAddForm(false);

      const preview = await api.datasets.preview(dataset.id);
      setPreviewRecords(preview);

      // Reset form fields
      setFilePath('');
      setDatasetName('');
      setDatasetDescription('');
      setTextColumn('text');
      setEntitiesColumn('');
    } catch (err: any) {
      setLoadError(err.message || 'Failed to load dataset');
    } finally {
      setLoading(false);
    }
  };

  const handleContinue = () => {
    if (canProceed && selectedDataset) {
      const config = {
        datasetId: selectedDataset.id,
        complianceFrameworks,
        cloudRestriction,
        runPresidio,
        runLlm,
        hasDatasetEntities: selectedDataset.has_entities,
        hasFinalEntities: selectedDataset.has_final_entities ?? false,
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
          Select your dataset and configure data access constraints for the evaluation process.
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
            <Select value={showAddForm ? '__add_new__' : selectedDatasetId} onValueChange={handleSelectDataset}>
              <SelectTrigger className="mt-1" id="dataset-select">
                <SelectValue placeholder="Choose a dataset…" />
              </SelectTrigger>
              <SelectContent>
                {datasets.map(ds => (
                  <SelectItem key={ds.id} value={ds.id}>
                    {ds.name} — {ds.record_count.toLocaleString()} records
                  </SelectItem>
                ))}
                <SelectItem value="__add_new__">
                  <span className="flex items-center gap-1">
                    <Plus className="size-3" />
                    Add new dataset…
                  </span>
                </SelectItem>
              </SelectContent>
            </Select>
          </div>

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
                    placeholder="e.g. Patient Records Q4"
                    value={datasetName}
                    onChange={(e) => setDatasetName(e.target.value)}
                    className="mt-1 text-sm"
                  />
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
                  <Label htmlFor="file-path">Absolute File Path</Label>
                  <Input
                    id="file-path"
                    placeholder="/path/to/dataset.csv"
                    value={filePath}
                    onChange={(e) => setFilePath(e.target.value)}
                    className="mt-1 font-mono text-sm"
                  />
                </div>

                <div>
                  <Label htmlFor="file-format">Format</Label>
                  <Select value={fileFormat} onValueChange={(val) => setFileFormat(val as 'csv' | 'json')}>
                    <SelectTrigger className="mt-1">
                      <SelectValue />
                    </SelectTrigger>
                    <SelectContent>
                      <SelectItem value="csv">CSV</SelectItem>
                      <SelectItem value="json">JSON</SelectItem>
                    </SelectContent>
                  </Select>
                </div>

                <div className="grid grid-cols-2 gap-3">
                  <div>
                    <Label htmlFor="text-col">Text Column Name</Label>
                    <Input
                      id="text-col"
                      placeholder="text"
                      value={textColumn}
                      onChange={(e) => setTextColumn(e.target.value)}
                      className="mt-1 text-sm"
                    />
                  </div>
                </div>

                {loadError && (
                  <Alert className="border-red-200 bg-red-50">
                    <AlertDescription className="text-red-800 text-sm">{loadError}</AlertDescription>
                  </Alert>
                )}

                <Button onClick={handleLoadDataset} disabled={loading || !filePath.trim()}>
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
                      <div>Columns: {selectedDataset.columns.join(', ')}</div>
                      <div>
                        {selectedDataset.has_entities ? (
                          <span className="text-green-700 font-medium">✓ Contains pre-identified entities</span>
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
                            {record.dataset_entities?.length > 0 && (
                              <div className="flex flex-wrap gap-1 mt-1">
                                {record.dataset_entities.map((e: any, j: number) => (
                                  <span key={j} className="inline-block px-1.5 py-0.5 bg-blue-100 text-blue-800 text-xs rounded">
                                    {e.entity_type}: {e.text}
                                  </span>
                                ))}
                              </div>
                            )}
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Detection Options — not implemented yet */}
              {selectedDataset.has_entities && (
                <div className="p-4 bg-slate-50 border border-slate-200 rounded-lg space-y-3 opacity-50 pointer-events-none">
                  <div className="flex items-center justify-between">
                    <Label className="text-slate-400 font-medium">Detection Options</Label>
                    <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">Coming soon</span>
                  </div>
                  <p className="text-sm text-slate-400">
                    Your dataset includes pre-identified entities. Additional detection engines will be available soon:
                  </p>
                  <div className="space-y-2">
                    <div className="flex items-center space-x-3">
                      <Checkbox
                        id="run-presidio"
                        checked={false}
                        disabled
                      />
                      <Label htmlFor="run-presidio" className="cursor-default">
                        <span className="font-medium text-slate-400">Run Presidio detection</span>
                        <span className="text-sm text-slate-400 ml-2">— compare against baseline PII detection</span>
                      </Label>
                    </div>
                    <div className="flex items-center space-x-3">
                      <Checkbox
                        id="run-llm"
                        checked={false}
                        disabled
                      />
                      <Label htmlFor="run-llm" className="cursor-default">
                        <span className="font-medium text-slate-400">Run LLM detection</span>
                        <span className="text-sm text-slate-400 ml-2">— AI-assisted entity detection</span>
                      </Label>
                    </div>
                  </div>
                </div>
              )}
            </div>
          )}
        </div>
      </Card>

      {/* Compliance Framework (disabled) */}
      <Card className="p-6 opacity-50 pointer-events-none">
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Shield className="size-5 text-slate-400" />
              <h3 className="font-semibold text-slate-400">Compliance Context</h3>
            </div>
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">Coming soon</span>
          </div>
          <p className="text-sm text-slate-400">Support for compliance frameworks (HIPAA, GDPR, CCPA) will be added soon.</p>
        </div>
      </Card>

      {/* Cloud Access (disabled) */}
      <Card className="p-6 opacity-50 pointer-events-none">
        <div className="space-y-4">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-2">
              <Cloud className="size-5 text-slate-400" />
              <h3 className="font-semibold text-slate-400">Data Access Constraints</h3>
            </div>
            <span className="text-xs text-slate-400 bg-slate-100 px-2 py-1 rounded">Coming soon</span>
          </div>
          <p className="text-sm text-slate-400">Currently only cloud-based LLM processing is supported. On-premises / local deployment options will be added soon.</p>
        </div>
      </Card>

      {/* Presidio Configuration Notice */}
      <Alert>
        <Shield className="size-4" />
        <AlertDescription>
          <div className="space-y-1">
            <div className="font-medium">Presidio Configuration</div>
            <div className="text-sm">
              Using current baseline configuration (v1.2). This evaluation will help determine if tuning is needed for your specific dataset.
            </div>
          </div>
        </AlertDescription>
      </Alert>

      {/* Actions */}
      <div className="flex justify-end gap-3 pt-4">
        <Button
          size="lg"
          onClick={handleContinue}
          disabled={!canProceed}
        >
          Continue to Sampling
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
