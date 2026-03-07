import { useState } from 'react';
import { useNavigate } from 'react-router';
import { Card } from '../components/ui/card';
import { Button } from '../components/ui/button';
import { Label } from '../components/ui/label';
import { RadioGroup, RadioGroupItem } from '../components/ui/radio-group';
import { Select, SelectContent, SelectItem, SelectTrigger, SelectValue } from '../components/ui/select';
import { Checkbox } from '../components/ui/checkbox';
import { Alert, AlertDescription } from '../components/ui/alert';
import { Database, Shield, ArrowRight, Cloud, CloudOff } from 'lucide-react';
import { mockDatasets } from '../lib/mockData';
import type { ComplianceFramework } from '../types';

const complianceInfo = {
  hipaa: {
    label: 'HIPAA',
    description: 'Health Insurance Portability and Accountability Act - for protected health information (PHI)',
    requirements: 'Requires strict handling of medical records, patient data, and health-related PII',
  },
  gdpr: {
    label: 'GDPR',
    description: 'General Data Protection Regulation - European data privacy law',
    requirements: 'Emphasizes data subject rights, consent, and cross-border data transfers',
  },
  ccpa: {
    label: 'CCPA',
    description: 'California Consumer Privacy Act - California state privacy law',
    requirements: 'Focuses on consumer rights to know, delete, and opt-out of data sales',
  },
  general: {
    label: 'General',
    description: 'Standard data protection practices',
    requirements: 'Basic PII protection without specific regulatory requirements',
  },
};

export function Setup() {
  const navigate = useNavigate();
  const [selectedDataset, setSelectedDataset] = useState('');
  const [complianceFrameworks, setComplianceFrameworks] = useState<ComplianceFramework[]>(['general']);
  const [cloudRestriction, setCloudRestriction] = useState<'allowed' | 'restricted'>('allowed');

  const canProceed = selectedDataset !== '';
  const selectedDatasetObj = mockDatasets.find(d => d.id === selectedDataset);

  const handleComplianceToggle = (framework: ComplianceFramework) => {
    setComplianceFrameworks(prev => {
      if (prev.includes(framework)) {
        if (prev.length === 1) return prev;
        return prev.filter(f => f !== framework);
      } else {
        return [...prev, framework];
      }
    });
  };

  const handleContinue = () => {
    if (canProceed) {
      navigate('/sampling');
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
            <h3 className="font-semibold text-slate-900">Dataset Selection</h3>
          </div>

          <div className="space-y-3">
            <Label>Select Dataset</Label>
            <Select value={selectedDataset} onValueChange={setSelectedDataset}>
              <SelectTrigger>
                <SelectValue placeholder="Choose a dataset to evaluate..." />
              </SelectTrigger>
              <SelectContent>
                {mockDatasets.map(dataset => (
                  <SelectItem key={dataset.id} value={dataset.id}>
                    <div className="flex items-center gap-2">
                      <span>{dataset.name}</span>
                      <span className="text-xs text-slate-500">
                        ({dataset.recordCount.toLocaleString()} records)
                      </span>
                    </div>
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>

            {selectedDatasetObj && (
              <Alert>
                <AlertDescription>
                  <div className="space-y-1">
                    <div className="flex items-center gap-2">
                      <span className="font-medium">Type:</span>
                      <span className="capitalize">{selectedDatasetObj.type}</span>
                    </div>
                    <div className="text-sm text-slate-600">{selectedDatasetObj.description}</div>
                  </div>
                </AlertDescription>
              </Alert>
            )}
          </div>
        </div>
      </Card>

      {/* Compliance Framework */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Shield className="size-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900">Compliance Context</h3>
          </div>

          <div className="space-y-3">
            <Label>Regulatory Frameworks (select one or more)</Label>
            <div className="space-y-2">
              {Object.entries(complianceInfo).map(([key, info]) => (
                <div key={key} className="flex items-start space-x-3 p-3 rounded-lg border border-slate-200 hover:bg-slate-50">
                  <Checkbox
                    id={key}
                    checked={complianceFrameworks.includes(key as ComplianceFramework)}
                    onCheckedChange={() => handleComplianceToggle(key as ComplianceFramework)}
                    className="mt-1"
                  />
                  <div className="flex-1">
                    <Label htmlFor={key} className="cursor-pointer">
                      <div className="font-medium">{info.label}</div>
                      <div className="text-sm text-slate-600 mt-1">{info.description}</div>
                      {complianceFrameworks.includes(key as ComplianceFramework) && (
                        <div className="text-xs text-slate-500 mt-2 pl-3 border-l-2 border-blue-600">
                          {info.requirements}
                        </div>
                      )}
                    </Label>
                  </div>
                </div>
              ))}
            </div>
          </div>
        </div>
      </Card>

      {/* Cloud Access */}
      <Card className="p-6">
        <div className="space-y-4">
          <div className="flex items-center gap-2 mb-4">
            <Cloud className="size-5 text-blue-600" />
            <h3 className="font-semibold text-slate-900">Data Access Constraints</h3>
          </div>

          <div className="space-y-3">
            <Label>Cloud Processing</Label>
            <RadioGroup value={cloudRestriction} onValueChange={(val) => setCloudRestriction(val as 'allowed' | 'restricted')}>
              <div className="flex items-start space-x-3 p-3 rounded-lg border border-slate-200 hover:bg-slate-50">
                <RadioGroupItem value="allowed" id="cloud-allowed" className="mt-1" />
                <div className="flex-1">
                  <Label htmlFor="cloud-allowed" className="cursor-pointer flex items-center gap-2">
                    <Cloud className="size-4" />
                    <span className="font-medium">Cloud Processing Allowed</span>
                  </Label>
                  <div className="text-sm text-slate-600 mt-1">
                    Data can be processed using cloud-based LLM services (Azure AI Foundry)
                  </div>
                </div>
              </div>

              <div className="flex items-start space-x-3 p-3 rounded-lg border border-slate-200 hover:bg-slate-50">
                <RadioGroupItem value="restricted" id="cloud-restricted" className="mt-1" />
                <div className="flex-1">
                  <Label htmlFor="cloud-restricted" className="cursor-pointer flex items-center gap-2">
                    <CloudOff className="size-4" />
                    <span className="font-medium">Cloud Processing Restricted</span>
                  </Label>
                  <div className="text-sm text-slate-600 mt-1">
                    Data must remain on-premises; LLM judging will use local deployment
                  </div>
                </div>
              </div>
            </RadioGroup>
          </div>
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
