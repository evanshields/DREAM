'use client';

import React, { useState, useEffect } from 'react';
import { useParams, useNavigate } from 'react-router-dom';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import { Loader2, CheckCircle2, AlertCircle, ChevronLeft, ChevronRight, Download } from 'lucide-react';

// Types
interface ExtractedField {
  value: any;
  confidence: number;
  source?: string;
}

interface ExtractedData {
  [key: string]: ExtractedField | ExtractedField[] | any;
}

interface DocumentStatus {
  id: string;
  document_type: string | null;
  classification_confidence: number | null;
  extraction_status: string;
}

interface ExtractionJobStatus {
  job_id: string;
  status: 'PENDING' | 'PROCESSING' | 'COMPLETED' | 'FAILED';
  started_at: string | null;
  completed_at: string | null;
  documents: DocumentStatus[];
  extracted_data: ExtractedData | null;
  fields_requiring_review: string[];
  overall_confidence: number | null;
  cost_cents: number | null;
  error_message: string | null;
}

interface ExtractionReviewProps {
  jobId: string;
  dealId: string;
}

export const ExtractionReview: React.FC<ExtractionReviewProps> = ({ jobId, dealId }) => {
  const navigate = useNavigate();
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [jobStatus, setJobStatus] = useState<ExtractionJobStatus | null>(null);
  const [extractedData, setExtractedData] = useState<ExtractedData>({});
  const [corrections, setCorrections] = useState<Record<string, any>>({});
  const [currentPage, setCurrentPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [saving, setSaving] = useState(false);
  const [confirming, setConfirming] = useState(false);

  // Fetch extraction job status
  useEffect(() => {
    const fetchJobStatus = async () => {
      try {
        setLoading(true);
        const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/extraction-jobs/${jobId}`);

        if (!response.ok) {
          throw new Error(`Failed to fetch extraction status: ${response.statusText}`);
        }

        const data: ExtractionJobStatus = await response.json();
        setJobStatus(data);

        // Extract and flatten extracted data
        if (data.extracted_data) {
          setExtractedData(data.extracted_data);
        }

        // Estimate total pages (would come from document metadata)
        setTotalPages(24); // Placeholder

        setLoading(false);
      } catch (err) {
        setError(err instanceof Error ? err.message : 'Failed to load extraction data');
        setLoading(false);
      }
    };

    fetchJobStatus();
  }, [jobId]);

  // Handle field value change
  const handleFieldChange = (fieldPath: string, value: any) => {
    setCorrections((prev) => ({
      ...prev,
      [fieldPath]: value,
    }));
  };

  // Get field value (from corrections or extracted data)
  const getFieldValue = (fieldPath: string): any => {
    if (corrections[fieldPath] !== undefined) {
      return corrections[fieldPath];
    }

    // Navigate nested object path (e.g., "property_name.value")
    const parts = fieldPath.split('.');
    let current: any = extractedData;
    for (const part of parts) {
      if (current && typeof current === 'object' && part in current) {
        current = current[part];
      } else {
        return null;
      }
    }
    return current;
  };

  // Get field confidence
  const getFieldConfidence = (fieldPath: string): number => {
    const parts = fieldPath.split('.');
    const basePath = parts.slice(0, -1).join('.');
    const field = basePath ? getNestedValue(extractedData, basePath) : extractedData[parts[0]];

    if (field && typeof field === 'object' && 'confidence' in field) {
      return field.confidence;
    }
    return 0;
  };

  // Get nested value helper
  const getNestedValue = (obj: any, path: string): any => {
    const parts = path.split('.');
    let current = obj;
    for (const part of parts) {
      if (current && typeof current === 'object' && part in current) {
        current = current[part];
      } else {
        return null;
      }
    }
    return current;
  };

  // Get confidence badge styling
  const getConfidenceBadge = (confidence: number) => {
    if (confidence >= 90) {
      return {
        className: 'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[#58ABA8]/10 text-[#58ABA8]',
        icon: <CheckCircle2 className="w-3 h-3" />,
        label: 'High',
      };
    } else if (confidence >= 70) {
      return {
        className: 'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[#F3B8A7]/20 text-[#EAB308] border border-[#F3B8A7]/50',
        icon: <AlertCircle className="w-3 h-3" />,
        label: 'Medium',
      };
    } else if (confidence >= 50) {
      return {
        className: 'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[#F97316]/20 text-[#F97316] border border-[#F97316]/50',
        icon: <AlertCircle className="w-3 h-3" />,
        label: 'Low',
      };
    } else {
      return {
        className: 'inline-flex items-center gap-1 px-2 py-0.5 rounded-full text-xs font-medium bg-[#C94A3E]/20 text-[#C94A3E] border border-[#C94A3E]/50',
        icon: <AlertCircle className="w-3 h-3" />,
        label: 'Very Low',
      };
    }
  };

  // Save changes
  const handleSaveChanges = async () => {
    // In a real implementation, this would save corrections to the backend
    // For now, just show a success message
    setSaving(true);
    await new Promise((resolve) => setTimeout(resolve, 500));
    setSaving(false);
    // TODO: Implement save endpoint
  };

  // Confirm extraction
  const handleConfirmExtraction = async () => {
    try {
      setConfirming(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/deals/${dealId}/confirm-extraction`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          corrections,
          confirmed: true,
        }),
      });

      if (!response.ok) {
        throw new Error('Failed to confirm extraction');
      }

      const result = await response.json();
      
      // Navigate to deal detail page
      navigate(`/deals/${dealId}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to confirm extraction');
      setConfirming(false);
    }
  };

  // Format currency
  const formatCurrency = (value: number | string | null): string => {
    if (value === null || value === undefined) return '';
    const num = typeof value === 'string' ? parseFloat(value.replace(/[^0-9.-]/g, '')) : value;
    return new Intl.NumberFormat('en-US', { style: 'currency', currency: 'USD', maximumFractionDigits: 0 }).format(num);
  };

  // Format number
  const formatNumber = (value: number | string | null): string => {
    if (value === null || value === undefined) return '';
    const num = typeof value === 'string' ? parseFloat(value) : value;
    return new Intl.NumberFormat('en-US').format(num);
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <Loader2 className="w-8 h-8 text-yinmn-blue animate-spin" />
        <p className="ml-3 text-secondary">Loading extraction data...</p>
      </div>
    );
  }

  if (error || !jobStatus) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-brand-danger/10 border border-brand-danger rounded-lg p-6">
          <AlertCircle className="w-6 h-6 text-brand-danger mb-2" />
          <h2 className="text-xl font-heading font-semibold text-brand-danger mb-2">Error</h2>
          <p className="text-secondary mb-4">{error || 'Failed to load extraction data'}</p>
          <Button onClick={() => window.location.reload()}>Retry</Button>
        </div>
      </div>
    );
  }

  const fieldsRequiringReview = jobStatus.fields_requiring_review || [];
  const totalFields = Object.keys(extractedData).length;
  const reviewCount = fieldsRequiringReview.length;

  return (
    <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8 lg:py-12">
      {/* Page Header */}
      <header className="mb-8">
        <nav aria-label="Breadcrumb" className="mb-6">
          <ol className="flex items-center gap-2 text-sm text-secondary">
            <li>
              <button onClick={() => navigate('/dashboard')} className="hover:text-primary hover:underline">
                Dashboard
              </button>
            </li>
            <li className="text-secondary-muted">/</li>
            <li>
              <button onClick={() => navigate(`/deals/${dealId}`)} className="hover:text-primary hover:underline">
                Deal Details
              </button>
            </li>
            <li className="text-secondary-muted">/</li>
            <li aria-current="page" className="text-primary font-medium">
              Review Extraction
            </li>
          </ol>
        </nav>

        <h1 className="text-4xl font-heading font-bold text-primary mb-2">Review Extracted Data</h1>
        <p className="text-lg text-secondary max-w-2xl">
          Review and correct extracted information from your documents. Fields highlighted in yellow or orange require
          your attention.
        </p>
      </header>

      {/* Extraction Summary */}
      <section aria-label="Extraction summary" className="mb-8">
        <div className="bg-background-primary border border-border rounded-lg p-6">
          <h2 className="text-xl font-heading font-semibold text-primary mb-4">Extraction Summary</h2>
          <div className="grid grid-cols-1 sm:grid-cols-3 gap-4">
            <div>
              <p className="text-sm text-secondary-muted mb-1">Fields Extracted</p>
              <p className="text-2xl font-semibold text-primary tabular-nums">{totalFields}</p>
            </div>
            <div>
              <p className="text-sm text-secondary-muted mb-1">Need Review</p>
              <p className="text-2xl font-semibold text-brand-warning tabular-nums">{reviewCount}</p>
            </div>
            <div>
              <p className="text-sm text-secondary-muted mb-1">Overall Confidence</p>
              <p className="text-2xl font-semibold text-primary tabular-nums">
                {jobStatus.overall_confidence || 0}%
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Split-View Layout */}
      <section aria-label="Extraction review" className="mb-8">
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Left: Document Viewer */}
          <aside aria-label="Document viewer" className="lg:sticky lg:top-24 lg:h-[calc(100vh-8rem)]">
            <div className="bg-background-primary border border-border rounded-lg overflow-hidden flex flex-col h-full">
              <header className="px-4 py-3 border-b border-border flex items-center justify-between">
                <h2 className="text-base font-medium text-primary truncate">
                  {jobStatus.documents[0]?.document_type || 'Document'}
                </h2>
                <Button variant="ghost" size="sm" aria-label="Download document">
                  <Download className="w-4 h-4" />
                </Button>
              </header>

              {/* PDF Viewer */}
              <div role="region" aria-label="PDF viewer" className="flex-1 overflow-hidden bg-background-tertiary">
                <iframe
                  src={`/api/v1/documents/${jobStatus.documents[0]?.id}/preview?page=${currentPage}`}
                  title="Document preview"
                  aria-label="Document preview"
                  className="w-full h-full"
                />
              </div>

              {/* Page Navigation */}
              <nav aria-label="Page navigation" className="px-4 py-3 border-t border-border flex items-center justify-between gap-4">
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setCurrentPage((p) => Math.max(1, p - 1))}
                  disabled={currentPage === 1}
                  aria-label="Previous page"
                >
                  <ChevronLeft className="w-4 h-4" />
                  Previous
                </Button>
                <span className="text-sm text-secondary">
                  Page
                  <Input
                    type="number"
                    value={currentPage}
                    min={1}
                    max={totalPages}
                    onChange={(e) => {
                      const page = parseInt(e.target.value);
                      if (page >= 1 && page <= totalPages) {
                        setCurrentPage(page);
                      }
                    }}
                    className="w-16 px-2 py-1 mx-2 text-center tabular-nums"
                    aria-label="Page number"
                  />
                  of {totalPages}
                </span>
                <Button
                  variant="ghost"
                  size="sm"
                  onClick={() => setCurrentPage((p) => Math.min(totalPages, p + 1))}
                  disabled={currentPage === totalPages}
                  aria-label="Next page"
                >
                  Next
                  <ChevronRight className="w-4 h-4" />
                </Button>
              </nav>
            </div>
          </aside>

          {/* Right: Extracted Data Form */}
          <section aria-label="Extracted data" className="space-y-6">
            <form className="space-y-6">
              {/* Property Information Section */}
              <fieldset className="bg-background-primary border border-border rounded-lg p-6 space-y-4">
                <legend className="text-lg font-heading font-semibold text-primary px-2 mb-4">
                  Property Information
                </legend>

                {/* Property Name */}
                {renderField(
                  'property_name',
                  'Property Name',
                  'text',
                  getFieldValue('property_name.value') || '',
                  getFieldConfidence('property_name'),
                  getNestedValue(extractedData, 'property_name.source') || 'Page 1',
                  (value) => handleFieldChange('property_name.value', value)
                )}

                {/* Street Address */}
                {renderField(
                  'street_address',
                  'Street Address',
                  'text',
                  getFieldValue('street_address.value') || '',
                  getFieldConfidence('street_address'),
                  getNestedValue(extractedData, 'street_address.source') || 'Page 2',
                  (value) => handleFieldChange('street_address.value', value)
                )}

                {/* City */}
                {renderField(
                  'city',
                  'City',
                  'text',
                  getFieldValue('city.value') || '',
                  getFieldConfidence('city'),
                  getNestedValue(extractedData, 'city.source') || 'Page 2',
                  (value) => handleFieldChange('city.value', value)
                )}

                {/* State */}
                {renderSelectField(
                  'state',
                  'State',
                  getFieldValue('state.value') || '',
                  getFieldConfidence('state'),
                  getNestedValue(extractedData, 'state.source') || 'Page 2',
                  (value) => handleFieldChange('state.value', value)
                )}

                {/* ZIP Code */}
                {renderField(
                  'zip_code',
                  'ZIP Code',
                  'text',
                  getFieldValue('zip_code.value') || '',
                  getFieldConfidence('zip_code'),
                  getNestedValue(extractedData, 'zip_code.source') || 'Page 2',
                  (value) => handleFieldChange('zip_code.value', value)
                )}

                {/* Year Built */}
                {renderField(
                  'year_built',
                  'Year Built',
                  'number',
                  getFieldValue('year_built.value') || '',
                  getFieldConfidence('year_built'),
                  getNestedValue(extractedData, 'year_built.source') || 'Page 3',
                  (value) => handleFieldChange('year_built.value', value),
                  fieldsRequiringReview.includes('year_built')
                )}

                {/* Number of Units */}
                {renderField(
                  'number_of_units',
                  'Number of Units',
                  'number',
                  getFieldValue('number_of_units.value') || '',
                  getFieldConfidence('number_of_units'),
                  getNestedValue(extractedData, 'number_of_units.source') || 'Page 3',
                  (value) => handleFieldChange('number_of_units.value', value)
                )}

                {/* Total SF */}
                {renderField(
                  'total_sf',
                  'Total Square Footage',
                  'number',
                  getFieldValue('total_sf.value') || '',
                  getFieldConfidence('total_sf'),
                  getNestedValue(extractedData, 'total_sf.source') || 'Page 3',
                  (value) => handleFieldChange('total_sf.value', value)
                )}

                {/* Property Class */}
                {renderSelectField(
                  'property_class',
                  'Property Class',
                  getFieldValue('property_class.value') || '',
                  getFieldConfidence('property_class'),
                  getNestedValue(extractedData, 'property_class.source') || 'Page 4',
                  (value) => handleFieldChange('property_class.value', value),
                  fieldsRequiringReview.includes('property_class'),
                  [
                    { value: '', label: 'Select...' },
                    { value: 'A', label: 'Class A' },
                    { value: 'B', label: 'Class B' },
                    { value: 'C', label: 'Class C' },
                    { value: 'D', label: 'Class D' },
                  ]
                )}
              </fieldset>

              {/* Financial Data Section */}
              <fieldset className="bg-background-primary border border-border rounded-lg p-6 space-y-4">
                <legend className="text-lg font-heading font-semibold text-primary px-2 mb-4">Financial Data</legend>

                {/* Asking Price */}
                {renderField(
                  'asking_price',
                  'Asking Price',
                  'text',
                  formatCurrency(getFieldValue('asking_price.value')),
                  getFieldConfidence('asking_price'),
                  getNestedValue(extractedData, 'asking_price.source') || 'Page 1',
                  (value) => handleFieldChange('asking_price.value', value)
                )}

                {/* Price Per Unit */}
                {renderField(
                  'price_per_unit',
                  'Price Per Unit',
                  'text',
                  formatCurrency(getFieldValue('price_per_unit.value')),
                  getFieldConfidence('price_per_unit'),
                  'Calculated',
                  () => {},
                  false,
                  true
                )}

                {/* In-Place NOI */}
                {renderField(
                  'in_place_noi',
                  'In-Place NOI',
                  'text',
                  formatCurrency(getFieldValue('in_place_noi.value')),
                  getFieldConfidence('in_place_noi'),
                  getNestedValue(extractedData, 'in_place_noi.source') || 'Page 6',
                  (value) => handleFieldChange('in_place_noi.value', value)
                )}

                {/* Pro Forma NOI */}
                {renderField(
                  'pro_forma_noi',
                  'Pro Forma NOI',
                  'text',
                  formatCurrency(getFieldValue('pro_forma_noi.value')),
                  getFieldConfidence('pro_forma_noi'),
                  getNestedValue(extractedData, 'pro_forma_noi.source') || 'Page 6',
                  (value) => handleFieldChange('pro_forma_noi.value', value)
                )}
              </fieldset>
            </form>
          </section>
        </div>
      </section>

      {/* Action Buttons */}
      <section aria-label="Form actions" className="mt-8">
        <div className="flex flex-col sm:flex-row gap-4 justify-end">
          <Button
            variant="outline"
            onClick={handleSaveChanges}
            disabled={saving || Object.keys(corrections).length === 0}
          >
            {saving ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Saving...
              </>
            ) : (
              'Save Changes'
            )}
          </Button>
          <Button onClick={handleConfirmExtraction} disabled={confirming}>
            {confirming ? (
              <>
                <Loader2 className="w-4 h-4 mr-2 animate-spin" />
                Confirming...
              </>
            ) : (
              'Looks Good ✓'
            )}
          </Button>
        </div>
      </section>
    </div>
  );

  // Render field helper
  function renderField(
    fieldId: string,
    label: string,
    type: string,
    value: any,
    confidence: number,
    source: string,
    onChange: (value: any) => void,
    needsReview: boolean = false,
    readonly: boolean = false
  ) {
    const badge = getConfidenceBadge(confidence);
    const needsReviewClass = needsReview
      ? 'bg-brand-warning/5 border border-brand-warning/30 rounded-md p-4'
      : '';

    return (
      <div className={needsReviewClass}>
        <label htmlFor={fieldId} className="block text-sm font-medium text-secondary mb-1 flex items-center gap-2">
          {label}
          <span aria-label={`${badge.label} confidence: ${confidence}%`} className={badge.className}>
            {badge.icon} {confidence}%
          </span>
        </label>
        <Input
          type={type}
          id={fieldId}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          readOnly={readonly}
          className={`w-full ${readonly ? 'bg-background-tertiary' : ''} tabular-nums`}
        />
        <p className="text-xs text-secondary-muted mt-1">Source: {source}</p>
        {needsReview && (
          <p className="text-xs text-brand-warning mt-1 font-medium">Please verify this value</p>
        )}
      </div>
    );
  }

  // Render select field helper
  function renderSelectField(
    fieldId: string,
    label: string,
    value: string,
    confidence: number,
    source: string,
    onChange: (value: string) => void,
    needsReview: boolean = false,
    options: { value: string; label: string }[] = []
  ) {
    const badge = getConfidenceBadge(confidence);
    const needsReviewClass = needsReview
      ? 'bg-brand-warning/5 border border-brand-warning/30 rounded-md p-4'
      : '';

    return (
      <div className={needsReviewClass}>
        <label htmlFor={fieldId} className="block text-sm font-medium text-secondary mb-1 flex items-center gap-2">
          {label}
          <span aria-label={`${badge.label} confidence: ${confidence}%`} className={badge.className}>
            {badge.icon} {confidence}%
          </span>
        </label>
        <Select value={value} onValueChange={onChange}>
          <SelectTrigger id={fieldId} className="w-full">
            <SelectValue placeholder="Select..." />
          </SelectTrigger>
          <SelectContent>
            {options.map((option) => (
              <SelectItem key={option.value} value={option.value}>
                {option.label}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <p className="text-xs text-secondary-muted mt-1">Source: {source}</p>
        {needsReview && (
          <p className="text-xs text-brand-warning mt-1 font-medium">Please verify this value</p>
        )}
      </div>
    );
  }
};

export default ExtractionReview;

