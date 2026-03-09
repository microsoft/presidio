import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowRight, Users, CheckCircle, ChevronLeft, ChevronRight, CheckCheck, Loader2 } from 'lucide-react';
import { EntityComparison } from '../components/EntityComparison';
import { api } from '../lib/api';
import type { Entity, Record as RecordType, SetupConfig } from '../types';

/** Map backend snake_case record to frontend camelCase Record. */
function toFrontendRecord(raw: any): RecordType {
  return {
    id: raw.id,
    text: raw.text,
    presidioEntities: raw.presidio_entities ?? raw.presidioEntities ?? [],
    llmEntities: raw.llm_entities ?? raw.llmEntities ?? [],
    datasetEntities: raw.dataset_entities ?? raw.datasetEntities ?? [],
    goldenEntities: raw.golden_entities ?? raw.goldenEntities ?? undefined,
  };
}

export function HumanReview() {
  const navigate = useNavigate();
  const [records, setRecords] = useState<RecordType[]>([]);
  const [loading, setLoading] = useState(true);
  const [loadError, setLoadError] = useState<string | null>(null);
  const [currentRecordIndex, setCurrentRecordIndex] = useState(0);
  const [reviewedRecords, setReviewedRecords] = useState<Set<string>>(new Set());
  const [goldenSet, setGoldenSet] = useState<Record<string, Entity[]>>({});

  const setupConfig = useMemo<SetupConfig | null>(() => {
    try {
      const raw = sessionStorage.getItem('setupConfig');
      return raw ? JSON.parse(raw) : null;
    } catch {
      return null;
    }
  }, []);

  // Fetch sampled records + LLM results on mount
  useEffect(() => {
    async function loadRecords() {
      try {
        setLoading(true);
        const datasetId = setupConfig?.datasetId;
        if (!datasetId) {
          setLoadError('No dataset selected. Go back to Setup.');
          return;
        }
        const [rawRecords, llmResults] = await Promise.all([
          api.datasets.records(datasetId),
          api.llm.results(),
        ]);

        const merged = rawRecords.map((raw: any) => {
          const rec = toFrontendRecord(raw);
          // Merge in LLM entities from analysis results
          const llmEntities = llmResults[rec.id];
          if (llmEntities) {
            rec.llmEntities = llmEntities;
          }
          return rec;
        });

        setRecords(merged);
      } catch (err: any) {
        setLoadError(err.message || 'Failed to load records');
      } finally {
        setLoading(false);
      }
    }
    loadRecords();
  }, []);

  const currentRecord = records[currentRecordIndex] ?? null;
  const totalRecords = records.length;
  const reviewProgress = totalRecords > 0 ? (reviewedRecords.size / totalRecords) * 100 : 0;

  const handleConfirm = (recordId: string, entity: Entity, _source: string) => {
    setGoldenSet(prev => ({
      ...prev,
      [recordId]: [...(prev[recordId] || []), entity],
    }));
    setReviewedRecords(new Set([...reviewedRecords, recordId]));
  };

  const handleReject = (recordId: string, entity: Entity, _source: string) => {
    setGoldenSet(prev => ({
      ...prev,
      [recordId]: (prev[recordId] || []).filter(e => 
        !(e.start < entity.end && entity.start < e.end)
      ),
    }));
    setReviewedRecords(new Set([...reviewedRecords, recordId]));
  };

  const handleAddManual = (recordId: string, entity: Entity) => {
    setGoldenSet(prev => ({
      ...prev,
      [recordId]: [...(prev[recordId] || []), { ...entity, score: 1.0 }],
    }));
    setReviewedRecords(new Set([...reviewedRecords, recordId]));
  };

  const handleNext = () => {
    if (currentRecordIndex < totalRecords - 1) {
      setCurrentRecordIndex(currentRecordIndex + 1);
    }
  };

  const handlePrevious = () => {
    if (currentRecordIndex > 0) {
      setCurrentRecordIndex(currentRecordIndex - 1);
    }
  };

  const handleContinue = async () => {
    // Save the golden set as final_entities in the stored dataset
    const datasetId = setupConfig?.datasetId;
    if (datasetId && Object.keys(goldenSet).length > 0) {
      try {
        await api.review.saveFinalEntities(datasetId, goldenSet);
      } catch {
        // Non-blocking — continue even if save fails
      }
    }
    navigate('/evaluation');
  };

  const handleAutoConfirmAll = () => {
    const allReviewed = new Set<string>();
    const autoGolden: Record<string, Entity[]> = {};

    records.forEach(record => {
      allReviewed.add(record.id);
      const entities: Entity[] = [];
      const seen = new Set<string>();

      const addUnique = (e: Entity) => {
        const key = `${e.text}-${e.start}-${e.end}-${e.entity_type}`;
        if (!seen.has(key)) {
          seen.add(key);
          entities.push(e);
        }
      };

      record.presidioEntities.forEach(addUnique);
      record.llmEntities.forEach(addUnique);

      autoGolden[record.id] = entities;
    });

    setReviewedRecords(allReviewed);
    setGoldenSet(autoGolden);
  };

  const isReviewed = currentRecord ? reviewedRecords.has(currentRecord.id) : false;
  const canContinue = totalRecords > 0 && reviewedRecords.size === totalRecords;

  if (loading) {
    return (
      <div className="max-w-5xl mx-auto flex items-center justify-center py-20">
        <Loader2 className="size-6 animate-spin text-slate-400 mr-3" />
        <span className="text-slate-600">Loading records…</span>
      </div>
    );
  }

  if (loadError) {
    return (
      <div className="max-w-5xl mx-auto py-10">
        <Alert className="border-red-200 bg-red-50">
          <AlertDescription className="text-red-800">{loadError}</AlertDescription>
        </Alert>
      </div>
    );
  }

  if (!currentRecord) {
    return (
      <div className="max-w-5xl mx-auto py-10">
        <Alert>
          <AlertDescription>
            No sampled records found. Go back to <strong>Sampling</strong> to select a sample first.
          </AlertDescription>
        </Alert>
      </div>
    );
  }

  return (
    <div className="max-w-5xl mx-auto space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-900 mb-2">Human Review & Golden Set Creation</h2>
        <p className="text-slate-600">
          Review entity detections from Presidio and LLM to create a validated golden set for evaluation.
        </p>
      </div>

      {/* Progress Overview */}
      <Alert className="border-blue-200 bg-blue-50">
        <Users className="size-4 text-blue-600" />
        <AlertDescription>
          <div className="space-y-2">
            <div className="flex items-center justify-between">
              <span className="font-medium text-blue-900">Review Progress</span>
              <div className="flex items-center gap-3">
                <span className="text-sm text-blue-800">{reviewedRecords.size} of {totalRecords} records reviewed ({reviewProgress.toFixed(0)}%)</span>
                {!canContinue && (
                  <Button
                    size="sm"
                    variant="outline"
                    className="border-blue-300 text-blue-700 hover:bg-blue-100"
                    onClick={handleAutoConfirmAll}
                  >
                    <CheckCheck className="size-4 mr-1" />
                    Auto Confirm All
                  </Button>
                )}
              </div>
            </div>
            <Progress value={reviewProgress} className="h-2" />
          </div>
        </AlertDescription>
      </Alert>

      {/* Record Navigation */}
      <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-slate-200">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-slate-900">
            Record {currentRecordIndex + 1} of {totalRecords}
          </span>
          {isReviewed && (
            <div className="flex items-center gap-1 text-green-700">
              <CheckCircle className="size-4" />
              <span className="text-sm">Reviewed</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={handlePrevious}
            disabled={currentRecordIndex === 0}
          >
            <ChevronLeft className="size-4 mr-1" />
            Previous
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleNext}
            disabled={currentRecordIndex === totalRecords - 1}
          >
            Next
            <ChevronRight className="size-4 ml-1" />
          </Button>
        </div>
      </div>

      {/* Entity Comparison */}
      <EntityComparison
        recordId={currentRecord.id}
        recordText={currentRecord.text}
        presidioEntities={currentRecord.presidioEntities}
        llmEntities={currentRecord.llmEntities}
        onConfirm={handleConfirm}
        onReject={handleReject}
        onAddManual={handleAddManual}
      />

      {/* Legend */}
      <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
        <div className="text-sm font-medium text-slate-900 mb-3">Entity Status Legend</div>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-blue-500" />
            <span>✓ Match (all sources agree)</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-purple-500" />
            <span>Presidio</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-cyan-500" />
            <span>LLM Judge</span>
          </div>
        </div>
      </div>

      {/* Bottom Record Navigation */}
      <div className="flex items-center justify-between p-4 bg-white rounded-lg border border-slate-200">
        <div className="flex items-center gap-4">
          <span className="text-sm font-medium text-slate-900">
            Record {currentRecordIndex + 1} of {totalRecords}
          </span>
          {isReviewed && (
            <div className="flex items-center gap-1 text-green-700">
              <CheckCircle className="size-4" />
              <span className="text-sm">Reviewed</span>
            </div>
          )}
        </div>

        <div className="flex items-center gap-2">
          <Button
            size="sm"
            variant="outline"
            onClick={handlePrevious}
            disabled={currentRecordIndex === 0}
          >
            <ChevronLeft className="size-4 mr-1" />
            Previous
          </Button>
          <Button
            size="sm"
            variant="outline"
            onClick={handleNext}
            disabled={currentRecordIndex === totalRecords - 1}
          >
            Next
            <ChevronRight className="size-4 ml-1" />
          </Button>
        </div>
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-4">
        <div className="flex items-center gap-4">
          <div className="text-sm text-slate-600">
            {canContinue ? (
              <span className="text-green-700 font-medium">
                ✓ All records reviewed - ready to proceed
              </span>
            ) : (
              <span>
                Review all records to continue ({reviewedRecords.size}/{totalRecords} completed)
              </span>
            )}
          </div>
          {!canContinue && (
            <Button
              size="sm"
              variant="outline"
              onClick={handleAutoConfirmAll}
            >
              <CheckCheck className="size-4 mr-1" />
              Auto Confirm All
            </Button>
          )}
        </div>
        <Button
          size="lg"
          onClick={handleContinue}
          disabled={!canContinue}
        >
          Continue to Evaluation
          <ArrowRight className="size-4 ml-2" />
        </Button>
      </div>
    </div>
  );
}
