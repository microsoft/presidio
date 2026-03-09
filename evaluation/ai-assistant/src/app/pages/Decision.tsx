import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Badge } from '../components/ui/badge';
import { AlertTriangle, Download, FileText, ExternalLink, Lightbulb } from 'lucide-react';
import { toast } from 'sonner';

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

  const handleExportArtifacts = () => {
    // Generate CSV from dataset
    const csvHeader = 'text,entity_type,start,end,score,source\n';
    const csvContent = csvHeader + 'Sample data - export will include full dataset results';
    const csvBlob = new Blob([csvContent], { type: 'text/csv' });
    const csvUrl = URL.createObjectURL(csvBlob);
    const csvLink = document.createElement('a');
    csvLink.href = csvUrl;
    csvLink.download = 'evaluation_dataset.csv';
    csvLink.click();
    URL.revokeObjectURL(csvUrl);

    // Generate evaluation report
    const report = [
      '# Presidio Evaluation Report',
      '',
      `Generated: ${new Date().toISOString()}`,
      '',
      '## Metrics Summary',
      '- Precision: 94%',
      '- Recall: 88%',
      '- F1 Score: 91%',
      '',
      '## Key Findings',
      '- 18 critical false negatives identified (12 credit cards, 6 SSNs)',
      '',
    ].join('\n');
    const reportBlob = new Blob([report], { type: 'text/markdown' });
    const reportUrl = URL.createObjectURL(reportBlob);
    const reportLink = document.createElement('a');
    reportLink.href = reportUrl;
    reportLink.download = 'evaluation_report.md';
    reportLink.click();
    URL.revokeObjectURL(reportUrl);

    toast.success('Exported dataset CSV and evaluation report');
  };

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">Insights</h2>
        <p className="text-slate-600">
          Review the evaluation summary and export your results.
        </p>
      </div>

      {/* Evaluation Summary */}
      <Card className="p-6 bg-slate-50 border-slate-300">
        <div className="space-y-4">
          <h3 className="font-semibold text-slate-900">Evaluation Summary</h3>

          <div className="grid grid-cols-3 gap-4">
            <div className="p-4 bg-white rounded-lg border border-slate-200">
              <div className="text-sm text-slate-600 mb-1">Precision</div>
              <div className="text-2xl font-semibold text-slate-900">94%</div>
              <Badge className="mt-2 bg-green-100 text-green-800 border-green-300">Good</Badge>
            </div>
            <div className="p-4 bg-white rounded-lg border border-slate-200">
              <div className="text-sm text-slate-600 mb-1">Recall</div>
              <div className="text-2xl font-semibold text-slate-900">88%</div>
              <Badge className="mt-2 bg-amber-100 text-amber-800 border-amber-300">Room for improvement</Badge>
            </div>
            <div className="p-4 bg-white rounded-lg border border-slate-200">
              <div className="text-sm text-slate-600 mb-1">F1 Score</div>
              <div className="text-2xl font-semibold text-slate-900">91%</div>
              <Badge className="mt-2 bg-green-100 text-green-800 border-green-300">Good</Badge>
            </div>
          </div>

          <Alert className="border-red-200 bg-red-50">
            <AlertTriangle className="size-4 text-red-600" />
            <AlertDescription>
              <div className="space-y-1">
                <div className="font-medium text-red-900">High-Risk Misses Detected</div>
                <div className="text-sm text-red-800">
                  18 critical false negatives identified (12 credit cards, 6 SSNs). Consider iteration to improve recall.
                </div>
              </div>
            </AlertDescription>
          </Alert>
        </div>
      </Card>

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
        <div className="space-y-3">
          <div className="flex items-center gap-2">
            <FileText className="size-5 text-blue-600" />
            <h3 className="font-semibold text-blue-900">Output & Reusable Artifacts</h3>
          </div>
          <div className="text-sm text-blue-800 space-y-2">
            <p>The following artifacts will be exported:</p>
            <ul className="list-disc list-inside space-y-1 ml-2">
              <li><span className="font-medium">Evaluation Dataset (CSV)</span> - Full dataset with detection results and human review labels</li>
              <li><span className="font-medium">Evaluation Report</span> - Metrics summary, key findings, and notes</li>
              <li className="text-blue-600"><span className="font-medium">Presidio Analyzer Config (YAML)</span> - The Presidio Analyzer configuration used in this evaluation <Badge className="ml-1 bg-blue-100 text-blue-700 border-blue-300 text-[10px] py-0">Coming soon</Badge></li>
            </ul>
          </div>
        </div>
      </Card>

      {/* Export Action */}
      <div className="flex justify-end pt-4">
        <Button size="lg" onClick={handleExportArtifacts}>
          <Download className="size-4 mr-2" />
          Export Artifacts
        </Button>
      </div>
    </div>
  );
}
