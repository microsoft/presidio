import { useState, useEffect, useRef, useCallback } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { CheckCircle, XCircle, Edit, Check, X, ChevronDown, FileText, Move, MousePointerClick, Undo2 } from 'lucide-react';
import type { Entity } from '../types';

interface EntityComparisonProps {
  recordId: string;
  recordText: string;
  presidioEntities: Entity[];
  llmEntities: Entity[];
  datasetEntities?: Entity[];
  allConfirmed?: boolean;
  onConfirm: (recordId: string, entity: Entity, source: 'presidio' | 'llm' | 'dataset' | 'manual') => void;
  onReject: (recordId: string, entity: Entity, source: 'presidio' | 'llm' | 'dataset' | 'manual') => void;
  onAddManual: (recordId: string, entity: Entity) => void;
  onUndo?: (recordId: string, entity: Entity) => void;
}

type EntitySource = 'presidio' | 'llm' | 'dataset' | 'manual';
type EntityStatus = 'match' | 'presidio-only' | 'llm-only' | 'dataset-only' | 'manual' | 'pending';

interface AnnotatedEntity extends Entity {
  status: EntityStatus;
  sources: EntitySource[];
  confirmed?: boolean;
}

export function EntityComparison({
  recordId,
  recordText,
  presidioEntities = [],
  llmEntities = [],
  datasetEntities = [],
  allConfirmed = false,
  onConfirm,
  onReject,
  onAddManual,
  onUndo,
}: EntityComparisonProps) {
  const [showAddManual, setShowAddManual] = useState(false);
  const [manualEntity, setManualEntity] = useState({ text: '', entity_type: '', start: 0, end: 0 });
  const [confirmedEntities, setConfirmedEntities] = useState<Set<string>>(new Set());
  const [rejectedEntities, setRejectedEntities] = useState<Set<string>>(new Set());
  const [expandedContexts, setExpandedContexts] = useState<Set<string>>(new Set());
  const [editedTypes, setEditedTypes] = useState<Record<string, string>>({});
  // Boundary adjustment state: key -> { start, end }
  const [adjustingKeys, setAdjustingKeys] = useState<Set<string>>(new Set());
  const [adjustedBounds, setAdjustedBounds] = useState<Record<string, { start: number; end: number }>>({});
  // Manually added entities (tracked locally for rendering)
  const [manualEntities, setManualEntities] = useState<Entity[]>([]);
  // Text selection mode
  const [selectionMode, setSelectionMode] = useState(false);
  const recordTextRef = useRef<HTMLDivElement>(null);

  // Handle text selection from the record text element
  const handleTextSelection = useCallback(() => {
    if (!selectionMode || !recordTextRef.current) return;
    const sel = window.getSelection();
    if (!sel || sel.isCollapsed || !sel.rangeCount) return;

    const range = sel.getRangeAt(0);
    // Ensure selection is within the record text element
    if (!recordTextRef.current.contains(range.startContainer) || !recordTextRef.current.contains(range.endContainer)) return;

    const selectedText = sel.toString().trim();
    if (!selectedText) return;

    // Find the start position in the full record text
    const fullText = recordText;
    // Use the text node offset approach: walk through the container to compute absolute offset
    const textContent = recordTextRef.current.textContent || '';
    const preRange = document.createRange();
    preRange.selectNodeContents(recordTextRef.current);
    preRange.setEnd(range.startContainer, range.startOffset);
    const preText = preRange.toString();

    // Map DOM offset to recordText offset — the DOM textContent should match recordText
    const startIdx = fullText.indexOf(selectedText, preText.length > 0 ? fullText.indexOf(preText.slice(-20)) : 0);
    const fallbackStart = fullText.indexOf(selectedText);
    const actualStart = startIdx >= 0 ? startIdx : (fallbackStart >= 0 ? fallbackStart : 0);
    const actualEnd = actualStart + selectedText.length;

    setManualEntity({
      text: selectedText,
      entity_type: '',
      start: actualStart,
      end: actualEnd,
    });
    setShowAddManual(true);
    sel.removeAllRanges();
  }, [selectionMode, recordText]);

  // Combine and classify entities from all three sources
  const annotatedEntities: AnnotatedEntity[] = [];

  // Two spans overlap if one starts before the other ends
  const spansOverlap = (a: Entity, b: Entity) =>
    a.start < b.end && b.start < a.end;

  // Build a unified list: for each unique span, track which sources detected it
  interface SpanEntry { entity: Entity; sources: Set<EntitySource>; types: Map<string, string> }
  const spans: SpanEntry[] = [];

  const addToSpans = (entity: Entity, source: EntitySource) => {
    const existing = spans.find(s => spansOverlap(s.entity, entity));
    if (existing) {
      existing.sources.add(source);
      existing.types.set(source, entity.entity_type);
      // Prefer the entity with more text or higher score
      if (entity.text.length > existing.entity.text.length) {
        existing.entity = { ...entity };
      }
    } else {
      const types = new Map<string, string>();
      types.set(source, entity.entity_type);
      spans.push({ entity: { ...entity }, sources: new Set([source]), types });
    }
  };

  presidioEntities.forEach(e => addToSpans(e, 'presidio'));
  llmEntities.forEach(e => addToSpans(e, 'llm'));
  datasetEntities.forEach(e => addToSpans(e, 'dataset'));
  manualEntities.forEach(e => addToSpans(e, 'manual'));

  const statusForSource = (src: EntitySource): EntityStatus => {
    if (src === 'presidio') return 'presidio-only';
    if (src === 'llm') return 'llm-only';
    if (src === 'manual') return 'manual';
    return 'dataset-only';
  };

  spans.forEach(({ entity, sources, types }) => {
    const sourceList = Array.from(sources) as EntitySource[];
    const uniqueTypes = new Set(types.values());
    const allAgree = uniqueTypes.size === 1;

    if (sourceList.length >= 2 && allAgree) {
      // All active sources agree on type → single "Match" card
      annotatedEntities.push({ ...entity, status: 'match', sources: sourceList });
    } else if (sourceList.length >= 2 && !allAgree) {
      // Sources disagree on type → separate card per source so user can confirm/reject each
      for (const src of sourceList) {
        const srcType = types.get(src) || entity.entity_type;
        annotatedEntities.push({ ...entity, entity_type: srcType, status: statusForSource(src), sources: [src] });
      }
    } else if (sourceList.length === 1) {
      const s = sourceList[0];
      annotatedEntities.push({ ...entity, status: statusForSource(s), sources: sourceList });
    } else {
      annotatedEntities.push({ ...entity, status: 'pending', sources: sourceList });
    }
  });

  const getEntityKey = (entity: AnnotatedEntity) => `${entity.text}-${entity.start}-${entity.end}-${entity.sources.join(',')}`;

  // When parent signals all entities are confirmed, mark them all
  useEffect(() => {
    if (allConfirmed && annotatedEntities.length > 0) {
      setConfirmedEntities(new Set(annotatedEntities.map(e => getEntityKey(e))));
      setRejectedEntities(new Set());
    }
  }, [allConfirmed]);

  const getContextForEntity = (entity: Entity, adjustedKey?: string) => {
    const CONTEXT_CHARS = 150;
    // Use adjusted bounds if available
    const adj = adjustedKey ? adjustedBounds[adjustedKey] : undefined;
    const useStart = adj ? adj.start : entity.start;
    const useEnd = adj ? adj.end : entity.end;

    // Use indexOf for robust highlighting regardless of position accuracy
    const idx = adj ? -1 : recordText.indexOf(entity.text);
    const entityStart = idx >= 0 ? idx : useStart;
    const entityEnd = idx >= 0 ? idx + entity.text.length : useEnd;

    const start = Math.max(0, entityStart - CONTEXT_CHARS);
    const end = Math.min(recordText.length, entityEnd + CONTEXT_CHARS);

    const before = recordText.substring(start, entityStart);
    const entityText = recordText.substring(entityStart, entityEnd);
    const after = recordText.substring(entityEnd, end);

    return {
      before: (start > 0 ? '...' : '') + before,
      entity: entityText,
      after: after + (end < recordText.length ? '...' : ''),
    };
  };

  const toggleContext = (key: string) => {
    setExpandedContexts(prev => {
      const newSet = new Set(prev);
      if (newSet.has(key)) {
        newSet.delete(key);
      } else {
        newSet.add(key);
      }
      return newSet;
    });
  };

  const handleConfirmEntity = (entity: AnnotatedEntity) => {
    const key = getEntityKey(entity);
    // Build final entity with optional type edit + boundary adjustment
    let finalEntity: Entity = { ...entity };
    if (editedTypes[key]) {
      finalEntity.entity_type = editedTypes[key];
    }
    const adj = adjustedBounds[key];
    if (adj) {
      // Record original span for audit
      finalEntity.original_start = entity.start;
      finalEntity.original_end = entity.end;
      finalEntity.original_text = entity.text;
      // Apply adjusted boundaries
      finalEntity.start = adj.start;
      finalEntity.end = adj.end;
      finalEntity.text = recordText.substring(adj.start, adj.end);
    }
    setConfirmedEntities(new Set([...confirmedEntities, key]));
    setRejectedEntities(prev => {
      const newSet = new Set(prev);
      newSet.delete(key);
      return newSet;
    });
    // Close adjustment panel
    setAdjustingKeys(prev => {
      const newSet = new Set(prev);
      newSet.delete(key);
      return newSet;
    });
    onConfirm(recordId, finalEntity, entity.sources[0]);
  };

  const handleRejectEntity = (entity: AnnotatedEntity) => {
    const key = getEntityKey(entity);
    setRejectedEntities(new Set([...rejectedEntities, key]));
    setConfirmedEntities(prev => {
      const newSet = new Set(prev);
      newSet.delete(key);
      return newSet;
    });
    onReject(recordId, entity, entity.sources[0]);
  };

  const handleUndoEntity = (entity: AnnotatedEntity) => {
    const key = getEntityKey(entity);
    setConfirmedEntities(prev => {
      const newSet = new Set(prev);
      newSet.delete(key);
      return newSet;
    });
    setRejectedEntities(prev => {
      const newSet = new Set(prev);
      newSet.delete(key);
      return newSet;
    });
    onUndo?.(recordId, entity);
  };

  const handleAddManualEntity = () => {
    if (manualEntity.text && manualEntity.entity_type) {
      const entity: Entity = { ...manualEntity, score: 1.0 };
      setManualEntities(prev => [...prev, entity]);
      // Auto-confirm manual entities
      const manualKey = `${entity.text}-${entity.start}-${entity.end}-manual`;
      setConfirmedEntities(prev => new Set([...prev, manualKey]));
      onAddManual(recordId, entity);
      setManualEntity({ text: '', entity_type: '', start: 0, end: 0 });
      setShowAddManual(false);
      setSelectionMode(false);
    }
  };

  const DEFAULT_ENTITY_TYPES = ['PERSON', 'EMAIL', 'PHONE_NUMBER', 'SSN', 'CREDIT_CARD', 'DATE_OF_BIRTH',
    'MEDICAL_RECORD', 'IP_ADDRESS', 'ADDRESS', 'MEDICAL_CONDITION'];

  // Include any entity types found in the data that aren't in the default list
  const dataTypes = annotatedEntities.map(e => e.entity_type).filter(Boolean);
  const ENTITY_TYPES = Array.from(new Set([...DEFAULT_ENTITY_TYPES, ...dataTypes])).sort();

  const getStatusBadge = (entity: AnnotatedEntity, confirmed?: boolean, rejected?: boolean) => {
    if (confirmed) {
      return <Badge className="bg-green-100 text-green-800 border-green-300"><Check className="size-3 mr-1" />Confirmed</Badge>;
    }
    if (rejected) {
      return <Badge className="bg-red-100 text-red-800 border-red-300"><X className="size-3 mr-1" />Rejected</Badge>;
    }

    const badges: React.ReactNode[] = [];
    if (entity.sources.includes('manual')) {
      badges.push(<Badge key="manual" className="bg-emerald-100 text-emerald-800 border-emerald-300"><Edit className="size-3 mr-1" />Manual</Badge>);
    }
    if (entity.sources.includes('dataset')) {
      badges.push(<Badge key="dataset" className="bg-amber-100 text-amber-800 border-amber-300">Golden Dataset</Badge>);
    }
    if (entity.sources.includes('presidio')) {
      badges.push(<Badge key="presidio" className="bg-purple-100 text-purple-800 border-purple-300">Presidio</Badge>);
    }
    if (entity.sources.includes('llm')) {
      badges.push(<Badge key="llm" className="bg-cyan-100 text-cyan-800 border-cyan-300">LLM as a Judge</Badge>);
    }
    if (badges.length === 0) {
      badges.push(<Badge key="pending" variant="secondary">Pending</Badge>);
    }
    return <>{badges}</>;
  };

  return (
    <Card className="p-6">
      <div className="space-y-6">
        {/* Record Text — selectable for manual annotation */}
        <div className="space-y-2">
          <div className="flex items-center justify-between">
            <Label>Record Text</Label>
            <Button
              size="sm"
              variant={selectionMode ? 'default' : 'outline'}
              onClick={() => setSelectionMode(!selectionMode)}
              className={selectionMode ? 'bg-emerald-600 hover:bg-emerald-700' : ''}
            >
              <MousePointerClick className="size-3 mr-1" />
              {selectionMode ? 'Selection Mode On' : 'Select Text to Annotate'}
            </Button>
          </div>
          <div
            ref={recordTextRef}
            onMouseUp={handleTextSelection}
            className={`p-4 rounded-lg border text-sm font-mono transition-colors ${
              selectionMode
                ? 'bg-emerald-50 border-emerald-300 cursor-text select-text'
                : 'bg-slate-50 border-slate-200'
            }`}
          >
            {recordText}
          </div>
          {selectionMode && (
            <p className="text-xs text-emerald-700">Highlight text above to create a manual entity annotation.</p>
          )}
        </div>

        {/* Entities List */}
        <div className="space-y-3">
          <div className="flex items-center justify-between">
            <Label>Detected Entities ({annotatedEntities.length})</Label>
            <Button
              size="sm"
              variant="outline"
              onClick={() => setShowAddManual(!showAddManual)}
            >
              <Edit className="size-3 mr-1" />
              Add Manual Entity
            </Button>
          </div>

          {/* Manual Add Form */}
          {showAddManual && (
            <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg space-y-3">
              <div className="flex items-center gap-2 text-xs font-medium text-emerald-800 mb-1">
                <Edit className="size-3" />
                Manual Entity Annotation
              </div>
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label className="text-xs">Entity Text</Label>
                  <Input
                    value={manualEntity.text}
                    onChange={(e) => {
                      const newText = e.target.value;
                      const idx = recordText.indexOf(newText);
                      setManualEntity({
                        text: newText,
                        entity_type: manualEntity.entity_type,
                        start: idx >= 0 ? idx : manualEntity.start,
                        end: idx >= 0 ? idx + newText.length : manualEntity.end,
                      });
                    }}
                    placeholder="Select text above or type here..."
                    className="text-sm"
                  />
                </div>
                <div>
                  <Label className="text-xs">Entity Type</Label>
                  <Select value={manualEntity.entity_type} onValueChange={(val) => setManualEntity({ ...manualEntity, entity_type: val })}>
                    <SelectTrigger className="text-sm">
                      <SelectValue placeholder="Select type..." />
                    </SelectTrigger>
                    <SelectContent>
                      {ENTITY_TYPES.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              {manualEntity.text && (
                <div className="text-xs text-slate-600">
                  Position: <span className="font-mono">{manualEntity.start}-{manualEntity.end}</span>
                  {manualEntity.text && (
                    <span className="ml-3">Preview: &ldquo;<span className="font-mono font-medium">{manualEntity.text}</span>&rdquo;</span>
                  )}
                </div>
              )}
              <div className="flex gap-2">
                <Button size="sm" onClick={handleAddManualEntity} disabled={!manualEntity.text || !manualEntity.entity_type}>
                  <Check className="size-3 mr-1" />
                  Add Entity
                </Button>
                <Button size="sm" variant="ghost" onClick={() => { setShowAddManual(false); setManualEntity({ text: '', entity_type: '', start: 0, end: 0 }); }}>Cancel</Button>
              </div>
            </div>
          )}

          {/* Entity Cards */}
          <div className="space-y-2">
            {annotatedEntities.map((entity, index) => {
              const key = getEntityKey(entity);
              const isConfirmed = confirmedEntities.has(key);
              const isRejected = rejectedEntities.has(key);

              return (
                <div
                  key={index}
                  className={`p-4 rounded-lg border ${
                    isConfirmed && entity.sources.includes('manual' as EntitySource) ? 'bg-emerald-50 border-emerald-300' :
                    isConfirmed ? 'bg-green-50 border-green-300' :
                    isRejected ? 'bg-red-50 border-red-300' :
                    entity.sources.includes('manual' as EntitySource) ? 'bg-emerald-50/50 border-emerald-200' :
                    'bg-white border-slate-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-slate-900">{entity.text}</span>
                        {!isConfirmed && !isRejected ? (
                          <Select
                            value={editedTypes[key] || entity.entity_type}
                            onValueChange={(val) => setEditedTypes(prev => ({ ...prev, [key]: val }))}
                          >
                            <SelectTrigger className="h-7 w-auto min-w-[140px] text-xs">
                              <SelectValue />
                            </SelectTrigger>
                            <SelectContent>
                              {ENTITY_TYPES.map(type => (
                                <SelectItem key={type} value={type}>{type}</SelectItem>
                              ))}
                            </SelectContent>
                          </Select>
                        ) : (
                          <Badge variant="outline">{editedTypes[key] || entity.entity_type}</Badge>
                        )}
                        {getStatusBadge(entity, isConfirmed, isRejected)}
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-slate-600">
                        <span>Position: {adjustedBounds[key] ? `${adjustedBounds[key].start}-${adjustedBounds[key].end}` : `${entity.start}-${entity.end}`}</span>
                        {entity.score && <span>Confidence: {(entity.score * 100).toFixed(0)}%</span>}
                        {adjustedBounds[key] && (
                          <span className="text-amber-600 text-xs">(original: {entity.start}-{entity.end})</span>
                        )}
                      </div>
                    </div>

                    {!isConfirmed && !isRejected ? (
                      <div className="flex gap-2">
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-slate-600 hover:text-slate-800 hover:bg-slate-100"
                          onClick={() => {
                            setAdjustingKeys(prev => {
                              const newSet = new Set(prev);
                              if (newSet.has(key)) {
                                newSet.delete(key);
                              } else {
                                newSet.add(key);
                                // Initialize with current bounds
                                if (!adjustedBounds[key]) {
                                  setAdjustedBounds(prev => ({ ...prev, [key]: { start: entity.start, end: entity.end } }));
                                }
                              }
                              return newSet;
                            });
                          }}
                          title="Adjust entity boundaries"
                        >
                          <Move className="size-4 mr-1" />
                          Adjust
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-green-700 hover:text-green-800 hover:bg-green-100"
                          onClick={() => handleConfirmEntity(entity)}
                        >
                          <CheckCircle className="size-4 mr-1" />
                          Confirm
                        </Button>
                        <Button
                          size="sm"
                          variant="ghost"
                          className="text-red-700 hover:text-red-800 hover:bg-red-100"
                          onClick={() => handleRejectEntity(entity)}
                        >
                          <XCircle className="size-4 mr-1" />
                          Reject
                        </Button>
                      </div>
                    ) : (
                      <Button
                        size="sm"
                        variant="ghost"
                        className="text-slate-600 hover:text-slate-800 hover:bg-slate-100"
                        onClick={() => handleUndoEntity(entity)}
                      >
                        <Undo2 className="size-4 mr-1" />
                        Undo
                      </Button>
                    )}
                  </div>

                  {/* Boundary Adjustment Panel */}
                  {adjustingKeys.has(key) && !isConfirmed && !isRejected && (() => {
                    const bounds = adjustedBounds[key] || { start: entity.start, end: entity.end };
                    const clampedStart = Math.max(0, Math.min(bounds.start, recordText.length));
                    const clampedEnd = Math.max(clampedStart, Math.min(bounds.end, recordText.length));
                    const previewText = recordText.substring(clampedStart, clampedEnd);
                    const PREVIEW_CTX = 80;
                    const ctxBefore = recordText.substring(Math.max(0, clampedStart - PREVIEW_CTX), clampedStart);
                    const ctxAfter = recordText.substring(clampedEnd, Math.min(recordText.length, clampedEnd + PREVIEW_CTX));
                    const hasChanged = bounds.start !== entity.start || bounds.end !== entity.end;
                    return (
                      <div className="mt-3 p-3 bg-amber-50 border border-amber-200 rounded-lg space-y-3">
                        <div className="flex items-center gap-2 text-xs font-medium text-amber-800">
                          <Move className="size-3" />
                          Adjust Entity Boundaries
                        </div>
                        <div className="grid grid-cols-2 gap-3">
                          <div>
                            <Label className="text-xs">Start Position</Label>
                            <Input
                              type="number"
                              min={0}
                              max={recordText.length}
                              value={bounds.start}
                              onChange={(e) => {
                                const newStart = Math.max(0, Math.min(Number(e.target.value), recordText.length));
                                setAdjustedBounds(prev => ({
                                  ...prev,
                                  [key]: { ...prev[key], start: newStart, end: Math.max(newStart, prev[key]?.end ?? entity.end) },
                                }));
                              }}
                              className="h-8 text-sm font-mono mt-1"
                            />
                          </div>
                          <div>
                            <Label className="text-xs">End Position</Label>
                            <Input
                              type="number"
                              min={0}
                              max={recordText.length}
                              value={bounds.end}
                              onChange={(e) => {
                                const newEnd = Math.max(0, Math.min(Number(e.target.value), recordText.length));
                                setAdjustedBounds(prev => ({
                                  ...prev,
                                  [key]: { ...prev[key], start: Math.min(prev[key]?.start ?? entity.start, newEnd), end: newEnd },
                                }));
                              }}
                              className="h-8 text-sm font-mono mt-1"
                            />
                          </div>
                        </div>
                        {/* Live preview */}
                        <div>
                          <Label className="text-xs text-amber-700">Live Preview</Label>
                          <div className="mt-1 p-2 bg-white rounded border border-amber-200 text-sm font-mono leading-relaxed">
                            <span className="text-slate-400">{clampedStart > PREVIEW_CTX ? '...' : ''}{ctxBefore}</span>
                            <span className={`px-0.5 rounded font-semibold ${hasChanged ? 'bg-amber-200 text-amber-900' : 'bg-yellow-200 text-slate-900'}`}>
                              {previewText || <span className="text-slate-400 italic">empty</span>}
                            </span>
                            <span className="text-slate-400">{ctxAfter}{clampedEnd + PREVIEW_CTX < recordText.length ? '...' : ''}</span>
                          </div>
                        </div>
                        {/* Adjusted entity text */}
                        {hasChanged && (
                          <div className="text-xs text-amber-700">
                            New text: <span className="font-mono font-medium">&ldquo;{previewText}&rdquo;</span>
                            <span className="ml-2 text-slate-500">(was: &ldquo;{entity.text}&rdquo;)</span>
                          </div>
                        )}
                        <div className="flex gap-2">
                          <Button
                            size="sm"
                            variant="outline"
                            className="text-xs h-7"
                            onClick={() => {
                              setAdjustedBounds(prev => {
                                const next = { ...prev };
                                delete next[key];
                                return next;
                              });
                              setAdjustingKeys(prev => { const s = new Set(prev); s.delete(key); return s; });
                            }}
                          >
                            Reset & Close
                          </Button>
                        </div>
                      </div>
                    );
                  })()}

                  {/* Context Collapsible */}
                  <Collapsible open={expandedContexts.has(key)} onOpenChange={() => toggleContext(key)}>
                    <CollapsibleTrigger asChild>
                      <Button
                        variant="ghost"
                        size="sm"
                        className="mt-2 h-auto py-1 px-2 text-xs text-slate-600 hover:text-slate-900"
                      >
                        <ChevronDown className={`size-3 mr-1 transition-transform ${expandedContexts.has(key) ? 'rotate-180' : ''}`} />
                        {expandedContexts.has(key) ? 'Hide Context' : 'View Context'}
                      </Button>
                    </CollapsibleTrigger>
                    <CollapsibleContent className="mt-2">
                      <div className="p-3 bg-slate-50 rounded border border-slate-200">
                        <div className="flex items-center gap-2 mb-2 text-xs text-slate-500">
                          <FileText className="size-3" />
                          <span>Surrounding Context:</span>
                        </div>
                        <div className="text-sm font-mono leading-relaxed">
                          <span className="text-slate-600">{getContextForEntity(entity, key).before}</span>
                          <span className="bg-yellow-200 px-1 rounded font-semibold text-slate-900">{getContextForEntity(entity, key).entity}</span>
                          <span className="text-slate-600">{getContextForEntity(entity, key).after}</span>
                        </div>
                      </div>
                    </CollapsibleContent>
                  </Collapsible>
                </div>
              );
            })}
          </div>
        </div>

        {/* Summary */}
        <div className="flex items-center gap-4 text-sm">
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-green-500" />
            <span>{confirmedEntities.size} Confirmed</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-red-500" />
            <span>{rejectedEntities.size} Rejected</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="size-3 rounded-full bg-slate-400" />
            <span>{annotatedEntities.length - confirmedEntities.size - rejectedEntities.size} Pending</span>
          </div>
        </div>
      </div>
    </Card>
  );
}
