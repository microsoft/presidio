import { useState } from 'react';
import { Card } from './ui/card';
import { Button } from './ui/button';
import { Badge } from './ui/badge';
import { Input } from './ui/input';
import { Label } from './ui/label';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from './ui/select';
import { Collapsible, CollapsibleContent, CollapsibleTrigger } from './ui/collapsible';
import { CheckCircle, XCircle, Edit, AlertTriangle, Check, X, ChevronDown, FileText } from 'lucide-react';
import type { Entity } from '../types';

interface EntityComparisonProps {
  recordId: string;
  recordText: string;
  presidioEntities: Entity[];
  llmEntities: Entity[];
  onConfirm: (recordId: string, entity: Entity, source: 'presidio' | 'llm' | 'manual') => void;
  onReject: (recordId: string, entity: Entity, source: 'presidio' | 'llm') => void;
  onAddManual: (recordId: string, entity: Entity) => void;
}

type EntityStatus = 'match' | 'conflict' | 'presidio-only' | 'llm-only' | 'pending';

interface AnnotatedEntity extends Entity {
  status: EntityStatus;
  source: 'presidio' | 'llm' | 'both';
  confirmed?: boolean;
}

export function EntityComparison({
  recordId,
  recordText,
  presidioEntities,
  llmEntities,
  onConfirm,
  onReject,
  onAddManual,
}: EntityComparisonProps) {
  const [showAddManual, setShowAddManual] = useState(false);
  const [manualEntity, setManualEntity] = useState({ text: '', type: '', start: 0, end: 0 });
  const [confirmedEntities, setConfirmedEntities] = useState<Set<string>>(new Set());
  const [rejectedEntities, setRejectedEntities] = useState<Set<string>>(new Set());
  const [expandedContexts, setExpandedContexts] = useState<Set<string>>(new Set());

  // Combine and classify entities
  const annotatedEntities: AnnotatedEntity[] = [];

  presidioEntities.forEach(pe => {
    const matchingLlm = llmEntities.find(
      le => le.text === pe.text && le.start === pe.start && le.end === pe.end
    );
    
    if (matchingLlm) {
      if (matchingLlm.type === pe.type) {
        annotatedEntities.push({ ...pe, status: 'match', source: 'both' });
      } else {
        annotatedEntities.push({ ...pe, status: 'conflict', source: 'both' });
      }
    } else {
      annotatedEntities.push({ ...pe, status: 'presidio-only', source: 'presidio' });
    }
  });

  llmEntities.forEach(le => {
    const alreadyAdded = annotatedEntities.some(
      ae => ae.text === le.text && ae.start === le.start && ae.end === le.end
    );
    if (!alreadyAdded) {
      annotatedEntities.push({ ...le, status: 'llm-only', source: 'llm' });
    }
  });

  const getEntityKey = (entity: Entity) => `${entity.text}-${entity.start}-${entity.end}`;

  const getContextForEntity = (entity: Entity) => {
    const CONTEXT_CHARS = 150;
    const start = Math.max(0, entity.start - CONTEXT_CHARS);
    const end = Math.min(recordText.length, entity.end + CONTEXT_CHARS);
    
    const before = recordText.substring(start, entity.start);
    const entityText = recordText.substring(entity.start, entity.end);
    const after = recordText.substring(entity.end, end);
    
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
    setConfirmedEntities(new Set([...confirmedEntities, key]));
    setRejectedEntities(prev => {
      const newSet = new Set(prev);
      newSet.delete(key);
      return newSet;
    });
    onConfirm(recordId, entity, entity.source === 'both' ? 'presidio' : entity.source);
  };

  const handleRejectEntity = (entity: AnnotatedEntity) => {
    const key = getEntityKey(entity);
    setRejectedEntities(new Set([...rejectedEntities, key]));
    setConfirmedEntities(prev => {
      const newSet = new Set(prev);
      newSet.delete(key);
      return newSet;
    });
    if (entity.source !== 'both') {
      onReject(recordId, entity, entity.source);
    }
  };

  const handleAddManualEntity = () => {
    if (manualEntity.text && manualEntity.type) {
      onAddManual(recordId, manualEntity);
      setManualEntity({ text: '', type: '', start: 0, end: 0 });
      setShowAddManual(false);
    }
  };

  const getStatusBadge = (status: EntityStatus, confirmed?: boolean, rejected?: boolean) => {
    if (confirmed) {
      return <Badge className="bg-green-100 text-green-800 border-green-300"><Check className="size-3 mr-1" />Confirmed</Badge>;
    }
    if (rejected) {
      return <Badge className="bg-red-100 text-red-800 border-red-300"><X className="size-3 mr-1" />Rejected</Badge>;
    }

    switch (status) {
      case 'match':
        return <Badge className="bg-blue-100 text-blue-800 border-blue-300">✓ Match</Badge>;
      case 'conflict':
        return <Badge className="bg-amber-100 text-amber-800 border-amber-300">⚠ Conflict</Badge>;
      case 'presidio-only':
        return <Badge className="bg-purple-100 text-purple-800 border-purple-300">Presidio Only</Badge>;
      case 'llm-only':
        return <Badge className="bg-cyan-100 text-cyan-800 border-cyan-300">LLM Only</Badge>;
      default:
        return <Badge variant="secondary">Pending</Badge>;
    }
  };

  return (
    <Card className="p-6">
      <div className="space-y-6">
        {/* Record Text */}
        <div className="space-y-2">
          <Label>Record Text</Label>
          <div className="p-4 bg-slate-50 rounded-lg border border-slate-200 text-sm font-mono">
            {recordText}
          </div>
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
            <div className="p-4 bg-blue-50 border border-blue-200 rounded-lg space-y-3">
              <div className="grid grid-cols-2 gap-3">
                <div>
                  <Label>Entity Text</Label>
                  <Input
                    value={manualEntity.text}
                    onChange={(e) => setManualEntity({ ...manualEntity, text: e.target.value })}
                    placeholder="Enter entity text..."
                  />
                </div>
                <div>
                  <Label>Entity Type</Label>
                  <Select value={manualEntity.type} onValueChange={(val) => setManualEntity({ ...manualEntity, type: val })}>
                    <SelectTrigger>
                      <SelectValue placeholder="Select type..." />
                    </SelectTrigger>
                    <SelectContent>
                      {['PERSON', 'EMAIL', 'PHONE_NUMBER', 'SSN', 'CREDIT_CARD', 'DATE_OF_BIRTH', 
                        'MEDICAL_RECORD', 'IP_ADDRESS', 'ADDRESS', 'MEDICAL_CONDITION'].map(type => (
                        <SelectItem key={type} value={type}>{type}</SelectItem>
                      ))}
                    </SelectContent>
                  </Select>
                </div>
              </div>
              <div className="flex gap-2">
                <Button size="sm" onClick={handleAddManualEntity}>Add Entity</Button>
                <Button size="sm" variant="ghost" onClick={() => setShowAddManual(false)}>Cancel</Button>
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
                    isConfirmed ? 'bg-green-50 border-green-300' :
                    isRejected ? 'bg-red-50 border-red-300' :
                    entity.status === 'conflict' ? 'bg-amber-50 border-amber-300' :
                    'bg-white border-slate-200'
                  }`}
                >
                  <div className="flex items-start justify-between gap-4">
                    <div className="flex-1 space-y-2">
                      <div className="flex items-center gap-2">
                        <span className="font-medium text-slate-900">{entity.text}</span>
                        <Badge variant="outline">{entity.type}</Badge>
                        {getStatusBadge(entity.status, isConfirmed, isRejected)}
                      </div>
                      
                      <div className="flex items-center gap-4 text-sm text-slate-600">
                        <span>Position: {entity.start}-{entity.end}</span>
                        {entity.score && <span>Confidence: {(entity.score * 100).toFixed(0)}%</span>}
                        {entity.status === 'conflict' && (
                          <div className="flex items-center gap-1 text-amber-700">
                            <AlertTriangle className="size-3" />
                            <span className="text-xs">Type mismatch between Presidio and LLM</span>
                          </div>
                        )}
                      </div>
                    </div>

                    {!isConfirmed && !isRejected && (
                      <div className="flex gap-2">
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
                    )}
                  </div>

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
                          <span className="text-slate-600">{getContextForEntity(entity).before}</span>
                          <span className="bg-yellow-200 px-1 rounded font-semibold text-slate-900">{getContextForEntity(entity).entity}</span>
                          <span className="text-slate-600">{getContextForEntity(entity).after}</span>
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
