import { useEffect, useState, useMemo } from 'react';
import { useNavigate } from 'react-router';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowRight, CheckCircle, ChevronLeft, ChevronRight, CheckCheck, Loader2, BookOpen, List } from 'lucide-react';
import { EntityComparison } from '../components/EntityComparison';
import { ReadingView } from '../components/ReadingView';
import { api } from '../lib/api';
import type { Entity, Record as RecordType, SetupConfig } from '../types';

/** Map backend snake_case record to frontend camelCase Record. */
function toFrontendRecord(raw: any): RecordType {
  const datasetEntities = raw.dataset_entities ?? raw.datasetEntities ?? [];
  const finalEntities = raw.final_entities ?? raw.finalEntities ?? [];
  return {
    id: raw.id,
    text: raw.text,
    presidioEntities: raw.presidio_entities ?? raw.presidioEntities ?? [],
    llmEntities: raw.llm_entities ?? raw.llmEntities ?? [],
    datasetEntities: datasetEntities.length > 0 ? datasetEntities : finalEntities,
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
  const [bulkConfirmedRecords, setBulkConfirmedRecords] = useState<Set<string>>(new Set());
  const [goldenSet, setGoldenSet] = useState<Record<string, Entity[]>>({});
  const [viewMode, setViewMode] = useState<'entity' | 'reading'>('entity');

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
        const [rawRecords, llmStatus, presidioStatus] = await Promise.all([
          api.datasets.records(datasetId),
          api.llm.status(),
          api.presidio.status(),
        ]);

        // Only fetch LLM results if analysis actually ran
        const llmResults = (llmStatus.progress > 0 && llmStatus.total > 0)
          ? await api.llm.results()
          : {};

        // Only fetch Presidio results if analysis actually ran
        const presidioResults = (presidioStatus.progress > 0 && presidioStatus.total > 0)
          ? await api.presidio.results()
          : {};

        const merged = rawRecords.map((raw: any) => {
          const rec = toFrontendRecord(raw);
          // Merge in LLM entities only if LLM was run
          const llmEntities = llmResults[rec.id];
          if (llmEntities) {
            rec.llmEntities = llmEntities;
          }
          // Merge in Presidio entities only if Presidio was run
          const presidioEntities = presidioResults[rec.id];
          if (presidioEntities) {
            rec.presidioEntities = presidioEntities;
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

  const hasFinalEntities = setupConfig?.hasFinalEntities ?? false;

  // Auto-confirm golden (final_entities) on second-config runs
  // Only golden/dataset entities are auto-confirmed; new entities from the
  // current config run are left unconfirmed for the user to review.
  useEffect(() => {
    if (!records.length || !hasFinalEntities) return;
    const autoGolden: Record<string, Entity[]> = {};
    const autoReviewed = new Set<string>();

    for (const rec of records) {
      if (rec.datasetEntities && rec.datasetEntities.length > 0) {
        autoGolden[rec.id] = [...rec.datasetEntities];
        autoReviewed.add(rec.id);
      }
    }

    if (Object.keys(autoGolden).length > 0) {
      setGoldenSet(autoGolden);
      setReviewedRecords(autoReviewed);
    }
  }, [records, hasFinalEntities]);

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
        !(e.start === entity.start && e.end === entity.end && e.entity_type === entity.entity_type)
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

  const handleUndo = (recordId: string, entity: Entity) => {
    setGoldenSet(prev => ({
      ...prev,
      [recordId]: (prev[recordId] || []).filter(e =>
        !(e.start === entity.start && e.end === entity.end && e.entity_type === entity.entity_type)
      ),
    }));
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
    if (!currentRecord) return;
    const record = currentRecord;
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
    if (record.datasetEntities) {
      record.datasetEntities.forEach(addUnique);
    }

    setGoldenSet(prev => ({ ...prev, [record.id]: entities }));
    setReviewedRecords(new Set([...reviewedRecords, record.id]));
    setBulkConfirmedRecords(new Set([...bulkConfirmedRecords, record.id]));
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
        <h2 className="text-2xl font-semibold text-slate-900 mb-1">Human Review</h2>
        <p className="text-sm text-slate-500">
          Confirm, reject, or adjust entity detections to build the golden reference set.
        </p>
      </div>

      {/* Entity Status Legend */}
      <div className="p-3 bg-slate-50 rounded-lg border border-slate-200">
        <div className="flex items-center gap-6 text-sm">
          <span className="text-xs font-medium text-slate-500 mr-1">Sources:</span>
          {currentRecord.datasetEntities && currentRecord.datasetEntities.length > 0 && (
            <div className="flex items-center gap-1.5">
              <div className="size-2.5 rounded-full bg-amber-500" />
              <span className="text-slate-600">Golden Dataset</span>
            </div>
          )}
          {currentRecord.presidioEntities.length > 0 && (
            <div className="flex items-center gap-1.5">
              <div className="size-2.5 rounded-full bg-purple-500" />
              <span className="text-slate-600">Presidio Analyzer</span>
            </div>
          )}
          {currentRecord.llmEntities.length > 0 && (
            <div className="flex items-center gap-1.5">
              <div className="size-2.5 rounded-full bg-cyan-500" />
              <span className="text-slate-600">Presidio LLM Recognizer</span>
            </div>
          )}
        </div>
      </div>

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

      {/* View Mode Toggle */}
      <div className="flex items-center gap-1 p-1 bg-slate-100 rounded-lg w-fit">
        <button
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            viewMode === 'entity'
              ? 'bg-white text-slate-900 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
          onClick={() => setViewMode('entity')}
        >
          <List className="size-4" />
          Entity View
        </button>
        <button
          className={`flex items-center gap-1.5 px-3 py-1.5 rounded-md text-sm font-medium transition-colors ${
            viewMode === 'reading'
              ? 'bg-white text-slate-900 shadow-sm'
              : 'text-slate-600 hover:text-slate-900'
          }`}
          onClick={() => setViewMode('reading')}
        >
          <BookOpen className="size-4" />
          Reading View
        </button>
      </div>

      {/* Entity Comparison / Reading View */}
      {viewMode === 'entity' ? (
        <EntityComparison
          recordId={currentRecord.id}
          recordText={currentRecord.text}
          presidioEntities={currentRecord.presidioEntities}
          llmEntities={currentRecord.llmEntities}
          datasetEntities={currentRecord.datasetEntities}
          allConfirmed={bulkConfirmedRecords.has(currentRecord.id)}
          autoConfirmDataset={hasFinalEntities}
          onConfirm={handleConfirm}
          onReject={handleReject}
          onAddManual={handleAddManual}
          onUndo={handleUndo}
        />
      ) : (
        <ReadingView
          recordId={currentRecord.id}
          recordText={currentRecord.text}
          presidioEntities={currentRecord.presidioEntities}
          llmEntities={currentRecord.llmEntities}
          datasetEntities={currentRecord.datasetEntities}
          allConfirmed={bulkConfirmedRecords.has(currentRecord.id)}
          autoConfirmDataset={hasFinalEntities}
          onConfirm={handleConfirm}
          onReject={handleReject}
          onAddManual={handleAddManual}
          onUndo={handleUndo}
        />
      )}

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

      {/* Review Progress */}
      <div className="p-4 bg-blue-50 rounded-lg border border-blue-200 space-y-2">
        <div className="flex items-center justify-between">
          <span className="text-sm font-medium text-blue-900">
            {reviewedRecords.size} of {totalRecords} records reviewed
          </span>
          <Button
            size="sm"
            variant="outline"
            className="border-blue-300 text-blue-700 hover:bg-blue-100"
            onClick={handleAutoConfirmAll}
          >
            <CheckCheck className="size-4 mr-1" />
            Confirm All Entities
          </Button>
        </div>
        <Progress value={reviewProgress} className="h-2" />
      </div>

      {/* Actions */}
      <div className="flex items-center justify-between pt-2">
        <div className="text-sm text-slate-600">
          {canContinue ? (
            <span className="text-green-700 font-medium">
              All records reviewed — ready to proceed
            </span>
          ) : (
            <span>
              {reviewedRecords.size}/{totalRecords} completed
            </span>
          )}
        </div>
        <div className="flex items-center gap-2">
          <Button
            size="lg"
            variant="outline"
            onClick={() => navigate('/setup')}
          >
            <ChevronLeft className="size-4 mr-1" />
            Back
          </Button>
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
    </div>
  );
}
