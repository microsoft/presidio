import { useState, useMemo } from 'react';
import { useNavigate } from 'react-router';
import { Button } from '../components/ui/button';
import { Progress } from '../components/ui/progress';
import { Alert, AlertDescription } from '../components/ui/alert';
import { ArrowRight, Users, CheckCircle, ChevronLeft, ChevronRight, FastForward } from 'lucide-react';
import { EntityComparison } from '../components/EntityComparison';
import { mockRecords } from '../lib/mockData';
import type { Entity, SetupConfig } from '../types';

export function HumanReview() {
  const navigate = useNavigate();
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

  const hasDatasetEntities = setupConfig?.hasDatasetEntities ?? false;

  const currentRecord = mockRecords[currentRecordIndex];
  const totalRecords = mockRecords.length;
  const reviewProgress = (reviewedRecords.size / totalRecords) * 100;

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
        e.text !== entity.text || e.start !== entity.start || e.end !== entity.end
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

  const handleContinue = () => {
    navigate('/evaluation');
  };

  const handleSkipTagging = () => {
    // Auto-accept all entities from all sources for all records
    const allReviewed = new Set<string>();
    const autoGolden: Record<string, Entity[]> = {};

    mockRecords.forEach(record => {
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
      if ('datasetEntities' in record) {
        (record as any).datasetEntities?.forEach(addUnique);
      }

      autoGolden[record.id] = entities;
    });

    setReviewedRecords(allReviewed);
    setGoldenSet(autoGolden);
  };

  const isReviewed = reviewedRecords.has(currentRecord.id);
  const canContinue = reviewedRecords.size === totalRecords;

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
              <span className="text-sm text-blue-800">{reviewedRecords.size} of {totalRecords} records reviewed ({reviewProgress.toFixed(0)}%)</span>
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
        datasetEntities={'datasetEntities' in currentRecord ? (currentRecord as any).datasetEntities : []}
        onConfirm={handleConfirm}
        onReject={handleReject}
        onAddManual={handleAddManual}
      />

      {/* Legend */}
      <div className="p-4 bg-slate-50 rounded-lg border border-slate-200">
        <div className="text-sm font-medium text-slate-900 mb-3">Entity Status Legend</div>
        <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-sm">
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-blue-500" />
            <span>✓ Match - Both systems agree</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-amber-500" />
            <span>⚠ Conflict - Type mismatch</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-purple-500" />
            <span>Presidio only detection</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-cyan-500" />
            <span>LLM only detection</span>
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
              onClick={handleSkipTagging}
            >
              <FastForward className="size-4 mr-1" />
              Skip Tagging
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
