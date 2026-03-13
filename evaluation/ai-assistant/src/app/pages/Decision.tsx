import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Badge } from '../components/ui/badge';
import { Checkbox } from '../components/ui/checkbox';
import { ChevronLeft, Download, FileText, ExternalLink, Lightbulb, RotateCcw } from 'lucide-react';
import { useNavigate } from 'react-router';
import { toast } from 'sonner';

import { useEffect, useMemo, useState } from 'react';
import { api } from '../lib/api';

const bestPractices = [
  {
    title: 'Deny List Recognizer',
    description: 'Add domain-specific terms (product names, internal codes) that Presidio should always detect using a simple deny list.',
    url: 'https://github.com/microsoft/presidio/blob/main/docs/samples/python/customizing_presidio_analyzer.ipynb',
  },
  {
    title: 'Custom Regex Recognizers',
    description: 'Create pattern-based recognizers for entity formats specific to your data (e.g., internal IDs, policy numbers).',
    url: 'https://github.com/microsoft/presidio/blob/main/docs/analyzer/adding_recognizers.md',
  },
  {
    title: 'Transformers-based NLP Models',
    description: 'Use transformer models (e.g., from HuggingFace) for higher accuracy NER instead of the default spaCy models.',
    url: 'https://github.com/microsoft/presidio/blob/main/docs/analyzer/customizing_nlp_models.md',
  },
  {
    title: 'Custom Recognizer Development',
    description: 'Build fully custom recognizers with validation logic, context enhancement, and confidence scoring.',
    url: 'https://github.com/microsoft/presidio/blob/main/docs/analyzer/developing_recognizers.md',
  },
  {
    title: 'Adjusting Confidence Thresholds',
    description: 'Fine-tune score thresholds per entity type to balance precision and recall for your use case.',
    url: 'https://github.com/microsoft/presidio/blob/main/docs/analyzer/decision_process.md',
  },
  {
    title: 'Multi-language Support',
    description: 'Configure Presidio to detect PII across multiple languages using language-specific NLP models.',
    url: 'https://github.com/microsoft/presidio/blob/main/docs/analyzer/languages.md',
  },
  {
    title: 'GLiNER for Zero-shot NER',
    description: 'Use the GLiNER model for zero-shot PII detection — recognizes entity types not seen during training, including a dedicated PII model.',
    url: 'https://github.com/microsoft/presidio/blob/main/docs/samples/python/gliner.md',
  },
  {
    title: 'LLM / SLM-based Detection',
    description: 'Leverage large or small language models (e.g., via LangExtract + Ollama) for flexible, context-aware PII/PHI recognition.',
    url: 'https://github.com/microsoft/presidio/blob/main/docs/samples/python/langextract/index.md',
  },
];

export function Decision() {
  const navigate = useNavigate();

  const setupConfig = useMemo(() => {
    try {
      const raw = sessionStorage.getItem('setupConfig');
      return raw ? JSON.parse(raw) : null;
    } catch { return null; }
  }, []);

  const [ranConfigs, setRanConfigs] = useState<string[]>([]);
  const [exportDataset, setExportDataset] = useState(true);
  const [exportConfigs, setExportConfigs] = useState(true);

  useEffect(() => {
    // Get ran configs from dataset metadata
    const datasetId = setupConfig?.datasetId;
    if (!datasetId) return;
    api.datasets.saved().then((datasets: any[]) => {
      const ds = datasets.find((d: any) => d.id === datasetId);
      if (!ds?.ran_configs) return;
      setRanConfigs(ds.ran_configs as string[]);
    }).catch(() => {});
  }, [setupConfig?.datasetId]);

  const handleExportArtifacts = async () => {
    let downloaded = 0;

    // 1. Download each ran config YAML first
    if (exportConfigs && ranConfigs.length > 0) {
      for (const name of ranConfigs) {
        try {
          const resp = await fetch(`/api/presidio/configs/${encodeURIComponent(name)}/download`);
          if (!resp.ok) continue;
          const blob = await resp.blob();
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = `${name}.yml`;
          link.click();
          URL.revokeObjectURL(url);
          downloaded++;
        } catch {
          // skip silently
        }
      }
    }

    // 2. Download the dataset CSV
    if (exportDataset) {
      const datasetId = setupConfig?.datasetId;
      if (datasetId) {
        try {
          const resp = await fetch(`/api/datasets/${encodeURIComponent(datasetId)}/download`);
          if (!resp.ok) throw new Error('Download failed');
          const blob = await resp.blob();
          const disposition = resp.headers.get('content-disposition');
          let filename = 'evaluation_dataset.csv';
          if (disposition) {
            const match = disposition.match(/filename="?([^"]+)"?/);
            if (match) filename = match[1];
          }
          const url = URL.createObjectURL(blob);
          const link = document.createElement('a');
          link.href = url;
          link.download = filename;
          link.click();
          URL.revokeObjectURL(url);
          downloaded++;
        } catch {
          toast.error('Failed to download dataset CSV');
        }
      }
    }

    if (downloaded > 0) {
      toast.success(`Exported ${downloaded} artifact${downloaded > 1 ? 's' : ''}`);
    }
  };

  const canExport = exportDataset || (exportConfigs && ranConfigs.length > 0);

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <Button variant="ghost" size="sm" onClick={() => navigate('/human-review')} className="mb-2 -ml-2 text-slate-600 hover:text-slate-900">
          <ChevronLeft className="size-4 mr-1" /> Back to Human Review
        </Button>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">Insights</h2>
        <p className="text-slate-600">
          Review improvement suggestions and export the artifacts from this run.
        </p>
      </div>

      {/* Best Practices */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <Lightbulb className="size-5 text-amber-500" />
            <h3 className="font-semibold text-slate-900">Best Practices to Improve Results</h3>
          </div>
          <p className="text-sm text-slate-600">
            Based on your evaluation, consider these approaches to improve PII detection coverage and accuracy.
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {bestPractices.map((practice) => (
              <a
                key={practice.title}
                href={practice.url}
                target="_blank"
                rel="noopener noreferrer"
                className="p-4 bg-slate-50 rounded-lg border border-slate-200 hover:border-blue-300 hover:bg-blue-50 transition-colors group"
              >
                <div className="flex items-start justify-between gap-2">
                  <div>
                    <div className="font-medium text-slate-900 group-hover:text-blue-700 text-sm">{practice.title}</div>
                    <div className="text-xs text-slate-600 mt-1">{practice.description}</div>
                  </div>
                  <ExternalLink className="size-4 text-slate-400 group-hover:text-blue-500 shrink-0 mt-0.5" />
                </div>
              </a>
            ))}
          </div>
        </div>
      </Card>

      {/* Outputs & Artifacts */}
      <Card className="p-6 bg-blue-50 border-blue-200">
        <div className="space-y-4">
          <div className="flex items-center gap-2">
            <FileText className="size-5 text-blue-600" />
            <h3 className="font-semibold text-blue-900">Output & Reusable Artifacts</h3>
          </div>
          <p className="text-sm text-blue-800">Select the artifacts to include in the export:</p>

          <div className="space-y-3">
            {/* Evaluation Dataset */}
            <label className="flex items-start gap-3 cursor-pointer">
              <Checkbox
                checked={exportDataset}
                onCheckedChange={(v) => setExportDataset(!!v)}
                className="mt-0.5"
              />
              <div>
                <span className="font-medium text-blue-900">Evaluation Dataset (CSV)</span>
                <p className="text-xs text-blue-700 mt-0.5">Full dataset with detection results of all configs tried and human review labels</p>
              </div>
            </label>

            {/* Presidio Analyzer Configs */}
            <label className="flex items-start gap-3 cursor-pointer">
              <Checkbox
                checked={exportConfigs}
                onCheckedChange={(v) => setExportConfigs(!!v)}
                disabled={ranConfigs.length === 0}
                className="mt-0.5"
              />
              <div>
                <span className={`font-medium ${ranConfigs.length > 0 ? 'text-blue-900' : 'text-blue-400'}`}>
                  Presidio Analyzer Configs (YAML)
                </span>
                {ranConfigs.length > 0 ? (
                  <p className="text-xs text-blue-700 mt-0.5">
                    {ranConfigs.length} config{ranConfigs.length > 1 ? 's' : ''} used: {ranConfigs.join(', ')}
                  </p>
                ) : (
                  <p className="text-xs text-blue-400 mt-0.5">No configs were run in this session</p>
                )}
              </div>
            </label>

            {/* Evaluation Report — coming soon */}
            <label className="flex items-start gap-3 cursor-not-allowed opacity-60">
              <Checkbox disabled className="mt-0.5" />
              <div>
                <span className="font-medium text-blue-900">
                  Evaluation Report
                  <Badge className="ml-2 bg-blue-100 text-blue-700 border-blue-300 text-[10px] py-0">Coming soon</Badge>
                </span>
                <p className="text-xs text-blue-700 mt-0.5">Metrics summary, key findings, and notes</p>
              </div>
            </label>
          </div>
        </div>
      </Card>

      {/* Actions */}
      <div className="flex justify-between pt-4">
        <Button variant="outline" onClick={() => navigate('/evaluation')}>
          <ChevronLeft className="size-4 mr-1" />
          Back
        </Button>
        <div className="flex gap-3">
          <Button size="lg" onClick={handleExportArtifacts} disabled={!canExport}>
            <Download className="size-4 mr-2" />
            Export Artifacts
          </Button>
          <Button size="lg" variant="outline" onClick={() => navigate('/')}>
            <RotateCcw className="size-4 mr-2" />
            Start New Iteration
          </Button>
        </div>
      </div>
    </div>
  );
}
