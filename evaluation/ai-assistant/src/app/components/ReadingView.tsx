import { useState, useEffect, useRef, useCallback, useMemo } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Check, X, CheckCheck, Plus } from 'lucide-react';
import type { Entity } from '../types';

type EntitySource = 'presidio' | 'llm' | 'dataset' | 'manual';

interface AnnotatedEntity extends Entity {
  sources: EntitySource[];
}

interface ReadingViewProps {
  recordId: string;
  recordText: string;
  presidioEntities: Entity[];
  llmEntities: Entity[];
  datasetEntities?: Entity[];
  allConfirmed?: boolean;
  autoConfirmDataset?: boolean;
  onConfirm: (recordId: string, entity: Entity, source: EntitySource) => void;
  onReject: (recordId: string, entity: Entity, source: EntitySource) => void;
  onAddManual: (recordId: string, entity: Entity) => void;
  onUndo?: (recordId: string, entity: Entity) => void;
}

// Color palette by entity type
const ENTITY_TYPE_COLORS: Record<string, { bg: string; text: string; border: string }> = {
  PERSON: { bg: 'bg-green-200', text: 'text-green-900', border: 'border-green-400' },
  DATE: { bg: 'bg-purple-200', text: 'text-purple-900', border: 'border-purple-400' },
  DATE_TIME: { bg: 'bg-purple-200', text: 'text-purple-900', border: 'border-purple-400' },
  DATE_OF_BIRTH: { bg: 'bg-purple-200', text: 'text-purple-900', border: 'border-purple-400' },
  LOCATION: { bg: 'bg-blue-200', text: 'text-blue-900', border: 'border-blue-400' },
  ADDRESS: { bg: 'bg-blue-200', text: 'text-blue-900', border: 'border-blue-400' },
  PHONE_NUMBER: { bg: 'bg-pink-200', text: 'text-pink-900', border: 'border-pink-400' },
  EMAIL: { bg: 'bg-orange-200', text: 'text-orange-900', border: 'border-orange-400' },
  EMAIL_ADDRESS: { bg: 'bg-orange-200', text: 'text-orange-900', border: 'border-orange-400' },
  CREDIT_CARD: { bg: 'bg-red-200', text: 'text-red-900', border: 'border-red-400' },
  SSN: { bg: 'bg-rose-200', text: 'text-rose-900', border: 'border-rose-400' },
  PERSON_ID: { bg: 'bg-fuchsia-200', text: 'text-fuchsia-900', border: 'border-fuchsia-400' },
  IP_ADDRESS: { bg: 'bg-teal-200', text: 'text-teal-900', border: 'border-teal-400' },
  MEDICAL_RECORD: { bg: 'bg-amber-200', text: 'text-amber-900', border: 'border-amber-400' },
  MEDICAL_CONDITION: { bg: 'bg-yellow-200', text: 'text-yellow-900', border: 'border-yellow-400' },
};

const FALLBACK_COLOR = { bg: 'bg-slate-200', text: 'text-slate-900', border: 'border-slate-400' };

function getEntityColor(type: string) {
  return ENTITY_TYPE_COLORS[type] || FALLBACK_COLOR;
}

const DEFAULT_ENTITY_TYPES = [
  'PERSON', 'EMAIL', 'PHONE_NUMBER', 'SSN', 'CREDIT_CARD', 'DATE_OF_BIRTH',
  'MEDICAL_RECORD', 'IP_ADDRESS', 'ADDRESS', 'MEDICAL_CONDITION',
];

export function ReadingView({
  recordId,
  recordText,
  presidioEntities = [],
  llmEntities = [],
  datasetEntities = [],
  allConfirmed = false,
  autoConfirmDataset = false,
  onConfirm,
  onReject,
  onAddManual,
  onUndo,
}: ReadingViewProps) {
  const [manualEntities, setManualEntities] = useState<Entity[]>([]);
  const [confirmedEntities, setConfirmedEntities] = useState<Set<string>>(new Set());
  const [rejectedEntities, setRejectedEntities] = useState<Set<string>>(new Set());

  // Context menu state
  const [contextMenu, setContextMenu] = useState<{
    x: number;
    y: number;
    type: 'entity' | 'text';
    entities?: AnnotatedEntity[];
    textSelection?: { start: number; end: number; text: string };
  } | null>(null);

  // Add entity form (for adding via context menu)
  const [addEntityForm, setAddEntityForm] = useState<{
    text: string;
    start: number;
    end: number;
    entity_type: string;
  } | null>(null);

  // Adjust entity form
  const [adjustEntity, setAdjustEntity] = useState<{
    entity: AnnotatedEntity;
    start: number;
    end: number;
  } | null>(null);

  const [customTypes, setCustomTypes] = useState<string[]>([]);
  const [newTypeName, setNewTypeName] = useState('');
  const [showNewTypeInput, setShowNewTypeInput] = useState(false);
  const [selectedEntityType, setSelectedEntityType] = useState<string | null>(null);

  const menuRef = useRef<HTMLDivElement>(null);
  const textContainerRef = useRef<HTMLDivElement>(null);
  const manualDragRef = useRef<{ active: boolean; anchorIdx: number } | null>(null);
  const dragRef = useRef<{ side: 'start' | 'end' } | null>(null);

  // Reset state per record
  useEffect(() => {
    setManualEntities([]);
    setConfirmedEntities(new Set());
    setRejectedEntities(new Set());
    setContextMenu(null);
    setAddEntityForm(null);
    setAdjustEntity(null);
  }, [recordId]);

  // Clear drag on global mouseup
  useEffect(() => {
    const handleGlobalMouseUp = () => {
      manualDragRef.current = null;
      dragRef.current = null;
    };
    window.addEventListener('mouseup', handleGlobalMouseUp);
    return () => window.removeEventListener('mouseup', handleGlobalMouseUp);
  }, []);

  // Handle drag-move for boundary adjustment handles
  const handleDragMove = useCallback((e: React.MouseEvent) => {
    if (!dragRef.current || !adjustEntity) return;
    e.preventDefault();
    const target = document.elementFromPoint(e.clientX, e.clientY);
    if (!target) return;
    const charIdx = target.getAttribute('data-adj-char-idx');
    if (charIdx === null) return;
    const idx = Number(charIdx);
    const { side } = dragRef.current;
    setAdjustEntity(prev => {
      if (!prev) return null;
      if (side === 'start') {
        const newStart = Math.max(0, Math.min(idx, prev.end));
        return { ...prev, start: newStart };
      } else {
        const newEnd = Math.max(prev.start, Math.min(idx + 1, recordText.length));
        return { ...prev, end: newEnd };
      }
    });
  }, [adjustEntity, recordText.length]);

  // Entity key helper
  const getEntityKey = (entity: AnnotatedEntity) =>
    `${entity.entity_type}-${entity.text}-${entity.start}-${entity.end}-${entity.sources.join(',')}`;

  // Merge entities from all sources
  const annotatedEntities = useMemo(() => {
    const result: AnnotatedEntity[] = [];
    const addEntity = (entity: Entity, source: EntitySource) => {
      // Check if we already have an entity at this exact position with same type
      const existing = result.find(
        e => e.start === entity.start && e.end === entity.end && e.entity_type === entity.entity_type
      );
      if (existing) {
        if (!existing.sources.includes(source)) {
          existing.sources.push(source);
        }
      } else {
        result.push({ ...entity, sources: [source] });
      }
    };

    presidioEntities.forEach(e => addEntity(e, 'presidio'));
    llmEntities.forEach(e => addEntity(e, 'llm'));
    (datasetEntities || []).forEach(e => addEntity(e, 'dataset'));
    manualEntities.forEach(e => addEntity(e, 'manual'));

    return result.sort((a, b) => a.start - b.start);
  }, [presidioEntities, llmEntities, datasetEntities, manualEntities]);

  // Entities at exact same position but different types
  const exactMatchGroups = useMemo(() => {
    const groups = new Map<string, AnnotatedEntity[]>();
    for (const entity of annotatedEntities) {
      const posKey = `${entity.start}-${entity.end}`;
      if (!groups.has(posKey)) groups.set(posKey, []);
      groups.get(posKey)!.push(entity);
    }
    // Only keep groups with more than one entity type
    const multiGroups = new Map<string, AnnotatedEntity[]>();
    groups.forEach((entities, key) => {
      if (entities.length > 1) multiGroups.set(key, entities);
    });
    return multiGroups;
  }, [annotatedEntities]);

  // Active entities (not rejected)
  const activeEntities = useMemo(
    () => annotatedEntities.filter(e => !rejectedEntities.has(getEntityKey(e))),
    [annotatedEntities, rejectedEntities]
  );

  // All entity types present
  const ENTITY_TYPES = useMemo(() => {
    const types = annotatedEntities.map(e => e.entity_type).filter(Boolean);
    return Array.from(new Set([...DEFAULT_ENTITY_TYPES, ...types, ...customTypes])).sort();
  }, [annotatedEntities, customTypes]);

  // Bulk confirm
  useEffect(() => {
    if (allConfirmed && annotatedEntities.length > 0) {
      setConfirmedEntities(new Set(annotatedEntities.map(e => getEntityKey(e))));
      setRejectedEntities(new Set());
    }
  }, [allConfirmed, recordId]);

  // Auto-confirm only golden-dataset entities on second-config runs
  useEffect(() => {
    if (!autoConfirmDataset || annotatedEntities.length === 0) return;
    const datasetKeys = annotatedEntities
      .filter(e => e.sources.includes('dataset'))
      .map(e => getEntityKey(e));
    if (datasetKeys.length > 0) {
      setConfirmedEntities(prev => new Set([...prev, ...datasetKeys]));
    }
  }, [autoConfirmDataset, recordId]);

  // Close context menu on outside click
  useEffect(() => {
    const handleClick = (e: MouseEvent) => {
      if (menuRef.current && !menuRef.current.contains(e.target as Node)) {
        setContextMenu(null);
      }
    };
    document.addEventListener('mousedown', handleClick);
    return () => document.removeEventListener('mousedown', handleClick);
  }, []);

  // Build text segments: non-entity text interspersed with entity highlights
  const segments = useMemo(() => {
    const segs: Array<{
      text: string;
      start: number;
      end: number;
      entities?: AnnotatedEntity[];
    }> = [];

    let pos = 0;
    for (const entity of activeEntities) {
      if (entity.start > pos) {
        segs.push({ text: recordText.substring(pos, entity.start), start: pos, end: entity.start });
      }
      // Group entities at same position
      const entitiesAtPos = activeEntities.filter(
        e => e.start === entity.start && e.end === entity.end
      );
      // Only add once per position
      if (entity.start >= pos) {
        segs.push({
          text: recordText.substring(entity.start, entity.end),
          start: entity.start,
          end: entity.end,
          entities: entitiesAtPos,
        });
        pos = entity.end;
      }
    }
    if (pos < recordText.length) {
      segs.push({ text: recordText.substring(pos), start: pos, end: recordText.length });
    }
    return segs;
  }, [activeEntities, recordText]);

  const handleContextMenu = useCallback((e: React.MouseEvent, entities?: AnnotatedEntity[], textRange?: { start: number; end: number }) => {
    e.preventDefault();
    e.stopPropagation();

    if (entities && entities.length > 0) {
      setContextMenu({
        x: e.clientX,
        y: e.clientY,
        type: 'entity',
        entities,
      });
    } else if (textRange) {
      const selectedText = recordText.substring(textRange.start, textRange.end);
      setContextMenu({
        x: e.clientX,
        y: e.clientY,
        type: 'text',
        textSelection: { start: textRange.start, end: textRange.end, text: selectedText },
      });
    }
  }, [recordText]);

  const handleTextContextMenu = useCallback((e: React.MouseEvent) => {
    e.preventDefault();
    e.stopPropagation();

    const selection = window.getSelection();
    if (selection && selection.toString().trim()) {
      // User has selected text
      const range = selection.getRangeAt(0);
      const container = textContainerRef.current;
      if (!container) return;

      // Find character indices from data attributes
      const startEl = range.startContainer.parentElement;
      const endEl = range.endContainer.parentElement;
      const startIdx = startEl?.closest('[data-char-start]')?.getAttribute('data-char-start');
      const endIdx = endEl?.closest('[data-char-end]')?.getAttribute('data-char-end');

      if (startIdx !== null && startIdx !== undefined && endIdx !== null && endIdx !== undefined) {
        setContextMenu({
          x: e.clientX,
          y: e.clientY,
          type: 'text',
          textSelection: {
            start: Number(startIdx),
            end: Number(endIdx),
            text: selection.toString(),
          },
        });
      }
    } else {
      // No selection — show generic add option at click position
      const target = (e.target as HTMLElement).closest('[data-char-start]');
      if (target) {
        const charStart = Number(target.getAttribute('data-char-start'));
        const charEnd = Number(target.getAttribute('data-char-end'));
        setContextMenu({
          x: e.clientX,
          y: e.clientY,
          type: 'text',
          textSelection: {
            start: charStart,
            end: charEnd,
            text: recordText.substring(charStart, charEnd),
          },
        });
      }
    }
  }, [recordText]);

  const handleRejectEntity = (entity: AnnotatedEntity) => {
    const key = getEntityKey(entity);
    setRejectedEntities(prev => new Set([...prev, key]));
    setConfirmedEntities(prev => {
      const s = new Set(prev);
      s.delete(key);
      return s;
    });
    onReject(recordId, entity, entity.sources[0]);
    setContextMenu(null);
  };

  const handleConfirmEntity = (entity: AnnotatedEntity) => {
    const key = getEntityKey(entity);
    setConfirmedEntities(prev => new Set([...prev, key]));
    setRejectedEntities(prev => {
      const s = new Set(prev);
      s.delete(key);
      return s;
    });
    onConfirm(recordId, entity, entity.sources[0]);
    setContextMenu(null);
  };

  const handleStartAdjust = (entity: AnnotatedEntity) => {
    setAdjustEntity({ entity, start: entity.start, end: entity.end });
    setContextMenu(null);
  };

  const handleSaveAdjust = () => {
    if (!adjustEntity) return;
    const { entity, start, end } = adjustEntity;

    // Reject the original
    const key = getEntityKey(entity);
    setRejectedEntities(prev => new Set([...prev, key]));
    onReject(recordId, entity, entity.sources[0]);

    // Add as a new manual entity with adjusted bounds
    const adjusted: Entity = {
      text: recordText.substring(start, end),
      entity_type: entity.entity_type,
      start,
      end,
      score: 1.0,
      original_start: entity.start,
      original_end: entity.end,
      original_text: entity.text,
    };
    setManualEntities(prev => [...prev, adjusted]);
    const manualKey = `${adjusted.text}-${adjusted.start}-${adjusted.end}-manual`;
    setConfirmedEntities(prev => new Set([...prev, manualKey]));
    onAddManual(recordId, adjusted);
    setAdjustEntity(null);
  };

  const handleStartAdd = () => {
    if (!contextMenu?.textSelection) return;
    setAddEntityForm({
      text: contextMenu.textSelection.text,
      start: contextMenu.textSelection.start,
      end: contextMenu.textSelection.end,
      entity_type: '',
    });
    setContextMenu(null);
  };

  const handleSaveAdd = () => {
    if (!addEntityForm || !addEntityForm.entity_type) return;
    const entity: Entity = { ...addEntityForm, score: 1.0 };
    setManualEntities(prev => [...prev, entity]);
    const manualKey = `${entity.text}-${entity.start}-${entity.end}-manual`;
    setConfirmedEntities(prev => new Set([...prev, manualKey]));
    onAddManual(recordId, entity);
    setAddEntityForm(null);
  };

  const handleUndoEntity = (entity: AnnotatedEntity) => {
    const key = getEntityKey(entity);
    setConfirmedEntities(prev => {
      const s = new Set(prev);
      s.delete(key);
      return s;
    });
    setRejectedEntities(prev => {
      const s = new Set(prev);
      s.delete(key);
      return s;
    });
    onUndo?.(recordId, entity);
    setContextMenu(null);
  };

  const addCustomType = () => {
    const name = newTypeName.trim().toUpperCase().replace(/\s+/g, '_');
    if (name && !ENTITY_TYPES.includes(name)) {
      setCustomTypes(prev => [...prev, name]);
    }
    if (name && addEntityForm) {
      setAddEntityForm(prev => prev ? { ...prev, entity_type: name } : null);
    }
    setNewTypeName('');
    setShowNewTypeInput(false);
  };

  // Entity type legend from active entities
  const entityTypeLegend = useMemo(() => {
    const types = new Set(activeEntities.map(e => e.entity_type));
    return Array.from(types).sort();
  }, [activeEntities]);

  return (
    <Card className="p-6">
      <div className="space-y-4">
        {/* Entity Type Legend */}
        {entityTypeLegend.length > 0 && (
          <div className="flex flex-wrap items-center gap-3 text-xs">
            <span className="text-slate-500 font-medium">Entity types:</span>
            {entityTypeLegend.map(type => {
              const color = getEntityColor(type);
              const isSelected = selectedEntityType === type;
              return (
                <span
                  key={type}
                  className={`inline-flex items-center gap-1 px-2 py-0.5 rounded cursor-pointer transition-all ${
                    isSelected
                      ? `${color.bg} ${color.text} ring-2 ring-offset-1 ring-slate-400`
                      : 'bg-slate-100 text-slate-500 hover:bg-slate-200'
                  }`}
                  onClick={() => setSelectedEntityType(prev => prev === type ? null : type)}
                >
                  {type}
                </span>
              );
            })}
          </div>
        )}

        {/* Record Text with Inline Highlights */}
        <div
          ref={textContainerRef}
          className="p-4 rounded-lg border border-slate-200 bg-white text-sm leading-relaxed font-mono whitespace-pre-wrap"
          onContextMenu={(e) => {
            // Only fire if not on an entity span
            const target = e.target as HTMLElement;
            if (!target.closest('[data-entity]')) {
              handleTextContextMenu(e);
            }
          }}
        >
          {segments.map((seg, i) => {
            if (seg.entities && seg.entities.length > 0) {
              const primaryEntity = seg.entities[0];
              const isHighlighted = selectedEntityType === null ? false : seg.entities.some(e => e.entity_type === selectedEntityType);
              const color = isHighlighted ? { bg: 'bg-yellow-200', text: 'text-yellow-900', border: 'border-yellow-400' } : { bg: 'bg-slate-200', text: 'text-slate-600', border: 'border-slate-300' };
              const isConfirmed = seg.entities.some(e => confirmedEntities.has(getEntityKey(e)));
              const isRejected = seg.entities.every(e => rejectedEntities.has(getEntityKey(e)));
              const hasExactMatch = seg.entities.length > 1;

              return (
                <span
                  key={i}
                  data-entity="true"
                  data-char-start={seg.start}
                  data-char-end={seg.end}
                  className={`relative inline cursor-pointer rounded px-0.5 border-b-2 ${color.bg} ${color.text} ${color.border} ${
                    isConfirmed ? 'ring-2 ring-green-400' : ''
                  }`}
                  title={`${primaryEntity.entity_type}${hasExactMatch ? ` (+${seg.entities.length - 1} more)` : ''} — right-click for options`}
                  onContextMenu={(e) => handleContextMenu(e, seg.entities)}
                >
                  {seg.text}
                  <sup className={`ml-0.5 text-[10px] font-bold ${color.text} opacity-70`}>
                    {primaryEntity.entity_type}
                    {hasExactMatch && ` +${seg.entities.length - 1}`}
                  </sup>
                </span>
              );
            }
            return (
              <span
                key={i}
                data-char-start={seg.start}
                data-char-end={seg.end}
                className="text-slate-700"
              >
                {seg.text}
              </span>
            );
          })}
        </div>

        {/* Rejected entities (shown faded below) */}
        {annotatedEntities.some(e => rejectedEntities.has(getEntityKey(e))) && (
          <div className="text-xs text-slate-500">
            <span className="font-medium">Rejected:</span>{' '}
            {annotatedEntities
              .filter(e => rejectedEntities.has(getEntityKey(e)))
              .map((e, i) => (
                <span key={i} className="inline-flex items-center gap-1 mr-2">
                  <span className="line-through text-red-400">{e.text}</span>
                  <span className="text-slate-400">({e.entity_type})</span>
                  <button
                    className="text-blue-500 hover:text-blue-700 underline"
                    onClick={() => handleUndoEntity(e)}
                  >
                    undo
                  </button>
                </span>
              ))}
          </div>
        )}

        {/* Context Menu */}
        {contextMenu && (
          <div
            ref={menuRef}
            className="fixed z-50 bg-white rounded-lg shadow-lg border border-slate-200 py-1 min-w-[200px]"
            style={{ left: contextMenu.x, top: contextMenu.y }}
          >
            {contextMenu.type === 'entity' && contextMenu.entities && (
              <>
                {/* Show entity info */}
                <div className="px-3 py-1.5 text-xs text-slate-500 border-b border-slate-100">
                  {contextMenu.entities.length === 1
                    ? `${contextMenu.entities[0].entity_type}: "${contextMenu.entities[0].text}"`
                    : `${contextMenu.entities.length} entities at this position`}
                </div>

                {/* Per-entity actions for each entity at this position */}
                {contextMenu.entities.map((entity, i) => {
                  const color = getEntityColor(entity.entity_type);
                  const key = getEntityKey(entity);
                  const isConfirmed = confirmedEntities.has(key);
                  const isRejected = rejectedEntities.has(key);
                  return (
                    <div key={i}>
                      {i > 0 && <div className="border-t border-slate-100" />}
                      <div className="px-3 py-1.5 text-xs font-medium text-slate-700 flex items-center gap-2 border-b border-slate-50">
                        <span className={`inline-block w-2 h-2 rounded-full ${color.bg}`} />
                        {entity.entity_type}
                        <span className="text-slate-400 text-xs ml-auto">{entity.sources.join(', ')}</span>
                      </div>
                      {!isConfirmed && (
                        <button
                          className="w-full text-left px-3 py-1.5 text-sm hover:bg-green-50 text-green-700 flex items-center gap-2"
                          onClick={() => handleConfirmEntity(entity)}
                        >
                          <Check className="size-3.5" />
                          Confirm
                        </button>
                      )}
                      {!isRejected && (
                        <button
                          className="w-full text-left px-3 py-1.5 text-sm hover:bg-red-50 text-red-700 flex items-center gap-2"
                          onClick={() => handleRejectEntity(entity)}
                        >
                          <X className="size-3.5" />
                          Reject
                        </button>
                      )}
                      <button
                        className="w-full text-left px-3 py-1.5 text-sm hover:bg-amber-50 text-amber-700 flex items-center gap-2"
                        onClick={() => handleStartAdjust(entity)}
                      >
                        Adjust boundaries
                      </button>
                      {(isConfirmed || isRejected) && (
                        <button
                          className="w-full text-left px-3 py-1.5 text-sm hover:bg-slate-50 text-slate-600 flex items-center gap-2"
                          onClick={() => handleUndoEntity(entity)}
                        >
                          Undo
                        </button>
                      )}
                    </div>
                  );
                })}
              </>
            )}

            {contextMenu.type === 'text' && (
              <>
                <div className="px-3 py-1.5 text-xs text-slate-500 border-b border-slate-100">
                  "{contextMenu.textSelection?.text}"
                </div>
                <button
                  className="w-full text-left px-3 py-1.5 text-sm hover:bg-emerald-50 text-emerald-700 flex items-center gap-2"
                  onClick={handleStartAdd}
                >
                  <Plus className="size-3.5" />
                  Add as entity
                </button>
              </>
            )}
          </div>
        )}

        {/* Add Entity Form (appears after "Add as entity" from context menu) */}
        {addEntityForm && (
          <div className="p-4 bg-emerald-50 border border-emerald-200 rounded-lg space-y-3">
            <div className="text-xs font-medium text-emerald-800">Add New Entity</div>

            {/* Interactive text marker */}
            <div>
              <Label className="text-xs text-emerald-700">Click and drag to mark the entity in the text</Label>
              <div
                className="mt-1 p-2 bg-white rounded border border-emerald-200 text-sm font-mono leading-relaxed select-none max-h-40 overflow-y-auto"
                onMouseMove={(e) => {
                  if (!manualDragRef.current?.active) return;
                  e.preventDefault();
                  const target = document.elementFromPoint(e.clientX, e.clientY);
                  if (!target) return;
                  const charIdx = target.getAttribute('data-add-char-idx');
                  if (charIdx === null) return;
                  const idx = Number(charIdx);
                  const anchor = manualDragRef.current.anchorIdx;
                  const newStart = Math.min(anchor, idx);
                  const newEnd = Math.max(anchor, idx) + 1;
                  setAddEntityForm(prev => prev ? {
                    ...prev,
                    text: recordText.substring(newStart, newEnd),
                    start: newStart,
                    end: newEnd,
                  } : null);
                }}
                onMouseUp={() => { manualDragRef.current = null; }}
              >
                {recordText.split('').map((ch, i) => {
                  const isHighlighted = addEntityForm.text && i >= addEntityForm.start && i < addEntityForm.end;
                  return (
                    <span
                      key={i}
                      data-add-char-idx={i}
                      className={isHighlighted
                        ? 'bg-emerald-200 text-emerald-900 font-semibold'
                        : 'text-slate-700 hover:bg-emerald-100'}
                      style={{ cursor: 'text' }}
                      onMouseDown={(e) => {
                        e.preventDefault();
                        manualDragRef.current = { active: true, anchorIdx: i };
                        setAddEntityForm(prev => prev ? {
                          ...prev,
                          text: recordText[i],
                          start: i,
                          end: i + 1,
                        } : null);
                      }}
                    >
                      {ch}
                    </span>
                  );
                })}
              </div>
            </div>

            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs">Entity Text</Label>
                <Input
                  value={addEntityForm.text}
                  onChange={(e) => {
                    const newText = e.target.value;
                    const idx = recordText.indexOf(newText);
                    setAddEntityForm(prev => prev ? {
                      ...prev,
                      text: newText,
                      start: idx >= 0 ? idx : prev.start,
                      end: idx >= 0 ? idx + newText.length : prev.end,
                    } : null);
                  }}
                  placeholder="Select text above or type here..."
                  className="text-sm"
                />
              </div>
              <div>
                <Label className="text-xs">Entity Type</Label>
                {showNewTypeInput ? (
                  <div className="flex gap-1">
                    <Input
                      autoFocus
                      placeholder="NEW_TYPE_NAME"
                      value={newTypeName}
                      onChange={(e) => setNewTypeName(e.target.value)}
                      onKeyDown={(e) => {
                        if (e.key === 'Enter') addCustomType();
                        if (e.key === 'Escape') { setNewTypeName(''); setShowNewTypeInput(false); }
                      }}
                      className="text-sm h-8 uppercase"
                    />
                    <Button size="sm" variant="ghost" className="h-8 px-2" onClick={addCustomType}>
                      <Check className="size-3" />
                    </Button>
                    <Button size="sm" variant="ghost" className="h-8 px-2" onClick={() => { setNewTypeName(''); setShowNewTypeInput(false); }}>
                      <X className="size-3" />
                    </Button>
                  </div>
                ) : (
                  <Select
                    value={addEntityForm.entity_type}
                    onValueChange={(val) => {
                      if (val === '__add_new__') { setShowNewTypeInput(true); return; }
                      setAddEntityForm(prev => prev ? { ...prev, entity_type: val } : null);
                    }}
                  >
                    <SelectTrigger className="text-sm">
                      <SelectValue placeholder="Select type..." />
                    </SelectTrigger>
                    <SelectContent>
                      {ENTITY_TYPES.map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                      <SelectItem value="__add_new__" className="text-blue-600 font-medium">
                        <span className="flex items-center gap-1"><Plus className="size-3" /> Add new type...</span>
                      </SelectItem>
                    </SelectContent>
                  </Select>
                )}
              </div>
            </div>
            <div className="text-xs text-slate-600">
              Position: <span className="font-mono">{addEntityForm.start}-{addEntityForm.end}</span>
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={handleSaveAdd} disabled={!addEntityForm.entity_type}>
                <Check className="size-3 mr-1" />
                Add Entity
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setAddEntityForm(null)}>Cancel</Button>
            </div>
          </div>
        )}

        {/* Adjust Entity Form */}
        {adjustEntity && (
          <div className="p-4 bg-amber-50 border border-amber-200 rounded-lg space-y-3">
            <div className="text-xs font-medium text-amber-800">Adjust Entity Boundaries</div>
            <div className="grid grid-cols-2 gap-3">
              <div>
                <Label className="text-xs">Start Position</Label>
                <Input
                  type="number"
                  min={0}
                  max={recordText.length}
                  value={adjustEntity.start}
                  onChange={(e) => setAdjustEntity(prev => prev ? { ...prev, start: Math.max(0, Number(e.target.value)) } : null)}
                  className="h-8 text-sm font-mono"
                />
              </div>
              <div>
                <Label className="text-xs">End Position</Label>
                <Input
                  type="number"
                  min={0}
                  max={recordText.length}
                  value={adjustEntity.end}
                  onChange={(e) => setAdjustEntity(prev => prev ? { ...prev, end: Math.min(recordText.length, Number(e.target.value)) } : null)}
                  className="h-8 text-sm font-mono"
                />
              </div>
            </div>
            {/* Live preview with draggable boundaries */}
            <div>
              <Label className="text-xs text-amber-700">Live Preview <span className="text-amber-500 font-normal">(drag the handles to adjust)</span></Label>
              <div
                className="mt-1 p-2 bg-white rounded border border-amber-200 text-sm font-mono leading-relaxed select-none"
                onMouseMove={handleDragMove}
                onMouseUp={() => { dragRef.current = null; }}
                style={{ cursor: dragRef.current ? 'col-resize' : undefined }}
              >
                {(() => {
                  const PREVIEW_CTX = 80;
                  const clampedStart = Math.max(0, Math.min(adjustEntity.start, recordText.length));
                  const clampedEnd = Math.max(clampedStart, Math.min(adjustEntity.end, recordText.length));
                  const previewStartIdx = Math.max(0, clampedStart - PREVIEW_CTX);
                  const previewEndIdx = Math.min(recordText.length, clampedEnd + PREVIEW_CTX);
                  const hasChanged = adjustEntity.start !== adjustEntity.entity.start || adjustEntity.end !== adjustEntity.entity.end;
                  const chars: React.ReactNode[] = [];
                  if (previewStartIdx > 0) {
                    chars.push(<span key="ellipsis-before" className="text-slate-400">…</span>);
                  }
                  for (let i = previewStartIdx; i < previewEndIdx; i++) {
                    const ch = recordText[i];
                    const isHighlighted = i >= clampedStart && i < clampedEnd;
                    const isLeftEdge = i === clampedStart;
                    const isRightEdge = i === clampedEnd - 1;
                    chars.push(
                      <span
                        key={i}
                        data-adj-char-idx={i}
                        className={isHighlighted
                          ? `px-0 ${hasChanged ? 'bg-amber-200 text-amber-900' : 'bg-yellow-200 text-slate-900'} font-semibold`
                          : 'text-slate-400'}
                        style={{ position: 'relative' }}
                      >
                        {isLeftEdge && (
                          <span
                            className="absolute left-0 top-0 bottom-0 w-[3px] bg-amber-500 rounded-full cursor-col-resize hover:bg-amber-600 hover:w-[5px] z-10"
                            style={{ transform: 'translateX(-1px)' }}
                            onMouseDown={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              dragRef.current = { side: 'start' };
                            }}
                            title="Drag to adjust start"
                          />
                        )}
                        {ch}
                        {isRightEdge && (
                          <span
                            className="absolute right-0 top-0 bottom-0 w-[3px] bg-amber-500 rounded-full cursor-col-resize hover:bg-amber-600 hover:w-[5px] z-10"
                            style={{ transform: 'translateX(1px)' }}
                            onMouseDown={(e) => {
                              e.preventDefault();
                              e.stopPropagation();
                              dragRef.current = { side: 'end' };
                            }}
                            title="Drag to adjust end"
                          />
                        )}
                      </span>
                    );
                  }
                  if (previewEndIdx < recordText.length) {
                    chars.push(<span key="ellipsis-after" className="text-slate-400">…</span>);
                  }
                  return chars;
                })()}
              </div>
            </div>
            <div className="text-xs text-amber-700">
              Original: "{adjustEntity.entity.text}" → New: "{recordText.substring(adjustEntity.start, adjustEntity.end)}"
            </div>
            <div className="flex gap-2">
              <Button size="sm" onClick={handleSaveAdjust}>
                <Check className="size-3 mr-1" />
                Save Adjustment
              </Button>
              <Button size="sm" variant="ghost" onClick={() => setAdjustEntity(null)}>Cancel</Button>
            </div>
          </div>
        )}

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
