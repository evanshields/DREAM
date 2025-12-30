import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import * as z from 'zod';
import { Input } from '@/components/ui/input';
import { Textarea } from '@/components/ui/textarea';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import type { USState, PropertyType, PropertyClass, SourceType, HowReceived, MarketStatus, Priority } from '@/types/deal';
import { Loader2, CheckCircle2, AlertCircle } from 'lucide-react';

// US States and Territories
const US_STATES: { value: USState; label: string }[] = [
  { value: 'AL', label: 'Alabama' }, { value: 'AK', label: 'Alaska' }, { value: 'AZ', label: 'Arizona' },
  { value: 'AR', label: 'Arkansas' }, { value: 'CA', label: 'California' }, { value: 'CO', label: 'Colorado' },
  { value: 'CT', label: 'Connecticut' }, { value: 'DE', label: 'Delaware' }, { value: 'FL', label: 'Florida' },
  { value: 'GA', label: 'Georgia' }, { value: 'HI', label: 'Hawaii' }, { value: 'ID', label: 'Idaho' },
  { value: 'IL', label: 'Illinois' }, { value: 'IN', label: 'Indiana' }, { value: 'IA', label: 'Iowa' },
  { value: 'KS', label: 'Kansas' }, { value: 'KY', label: 'Kentucky' }, { value: 'LA', label: 'Louisiana' },
  { value: 'ME', label: 'Maine' }, { value: 'MD', label: 'Maryland' }, { value: 'MA', label: 'Massachusetts' },
  { value: 'MI', label: 'Michigan' }, { value: 'MN', label: 'Minnesota' }, { value: 'MS', label: 'Mississippi' },
  { value: 'MO', label: 'Missouri' }, { value: 'MT', label: 'Montana' }, { value: 'NE', label: 'Nebraska' },
  { value: 'NV', label: 'Nevada' }, { value: 'NH', label: 'New Hampshire' }, { value: 'NJ', label: 'New Jersey' },
  { value: 'NM', label: 'New Mexico' }, { value: 'NY', label: 'New York' }, { value: 'NC', label: 'North Carolina' },
  { value: 'ND', label: 'North Dakota' }, { value: 'OH', label: 'Ohio' }, { value: 'OK', label: 'Oklahoma' },
  { value: 'OR', label: 'Oregon' }, { value: 'PA', label: 'Pennsylvania' }, { value: 'RI', label: 'Rhode Island' },
  { value: 'SC', label: 'South Carolina' }, { value: 'SD', label: 'South Dakota' }, { value: 'TN', label: 'Tennessee' },
  { value: 'TX', label: 'Texas' }, { value: 'UT', label: 'Utah' }, { value: 'VT', label: 'Vermont' },
  { value: 'VA', label: 'Virginia' }, { value: 'WA', label: 'Washington' }, { value: 'WV', label: 'West Virginia' },
  { value: 'WI', label: 'Wisconsin' }, { value: 'WY', label: 'Wyoming' },
  { value: 'DC', label: 'District of Columbia' }, { value: 'AS', label: 'American Samoa' },
  { value: 'GU', label: 'Guam' }, { value: 'MP', label: 'Northern Mariana Islands' },
  { value: 'PR', label: 'Puerto Rico' }, { value: 'VI', label: 'U.S. Virgin Islands' },
];

// Validation schema based on PRD Section 7.1
const formSchema = z.object({
  // Section 1: Property Identification
  propertyName: z.string().min(3, 'Property name must be at least 3 characters').max(100, 'Property name must be less than 100 characters'),
  streetAddress: z.string().min(5, 'Street address must be at least 5 characters'),
  city: z.string().min(2, 'City must be at least 2 characters'),
  state: z.enum([
    'AL', 'AK', 'AZ', 'AR', 'CA', 'CO', 'CT', 'DE', 'FL', 'GA',
    'HI', 'ID', 'IL', 'IN', 'IA', 'KS', 'KY', 'LA', 'ME', 'MD',
    'MA', 'MI', 'MN', 'MS', 'MO', 'MT', 'NE', 'NV', 'NH', 'NJ',
    'NM', 'NY', 'NC', 'ND', 'OH', 'OK', 'OR', 'PA', 'RI', 'SC',
    'SD', 'TN', 'TX', 'UT', 'VT', 'VA', 'WA', 'WV', 'WI', 'WY',
    'DC', 'AS', 'GU', 'MP', 'PR', 'VI'
  ] as const),
  zipCode: z.string().regex(/^\d{5}(-\d{4})?$/, 'ZIP code must be 5 or 9 digits'),
  propertyType: z.enum([
    'Multifamily',
    'Single Family',
    'Student Housing',
    'Senior Housing',
    'Mobile Home Park',
    'Mixed Use',
    'Affordable Housing (Tax Credits)',
    'Other'
  ] as const),
  propertyClass: z.enum([
    'A+', 'A', 'A-', 'B+', 'B', 'B-', 'C+', 'C', 'C-', 'D+', 'D'
  ] as const).optional(),
  yearBuilt: z.number().min(1800).max(new Date().getFullYear()).optional().or(z.literal('')),
  numberOfUnits: z.number().min(1, 'Number of units must be greater than 0').max(9999, 'Number of units must be less than 9999'),

  // Section 2: Financial Overview
  askingPrice: z.number().min(0).max(999999999).optional().or(z.literal('')),
  pricePerUnit: z.number().optional(),
  currentOccupancy: z.number().min(0).max(100, 'Occupancy must be between 0-100%').optional().or(z.literal('')),
  inPlaceNOI: z.number().min(0).max(99999999).optional().or(z.literal('')),
  proFormaNOI: z.number().min(0).max(99999999).optional().or(z.literal('')),
  inPlaceCapRate: z.number().optional(),

  // Section 3: Deal Source
  sourceType: z.enum([
    'Broker',
    'Direct from Owner',
    'Auction',
    'Wholesaler',
    'Network/Referral',
    'LoopNet/CoStar',
    'Other'
  ] as const).optional(),
  sourceName: z.string().max(100).optional(),
  sourceCompany: z.string().max(100).optional(),
  sourceEmail: z.string().email('Invalid email address').optional().or(z.literal('')),
  sourcePhone: z.string().optional(),
  howReceived: z.enum([
    'Email',
    'Phone Call',
    'In Person',
    'Website/Portal',
    'Referral',
    'Other'
  ] as const).optional(),
  marketStatus: z.enum([
    'Listed',
    'Off-Market',
    'Pre-Market',
    'Pocket Listing',
    'REO/Foreclosure'
  ] as const).optional(),

  // Section 4: Notes & Tags
  initialNotes: z.string().max(2000).optional(),
  tags: z.array(z.string()).optional(),
  priority: z.enum(['Low', 'Medium', 'High'] as const).optional(),
});

type FormData = z.infer<typeof formSchema>;

interface ManualEntryFormProps {
  onSuccess?: (dealId: string) => void;
  onCancel?: () => void;
}

export const ManualEntryForm: React.FC<ManualEntryFormProps> = ({ onSuccess, onCancel }) => {
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [submitError, setSubmitError] = useState<string | null>(null);
  const [submitSuccess, setSubmitSuccess] = useState(false);

  const {
    register,
    handleSubmit,
    watch,
    setValue,
    formState: { errors },
  } = useForm<FormData>({
    resolver: zodResolver(formSchema),
    defaultValues: {
      propertyType: 'Multifamily',
      sourceType: 'Broker',
      howReceived: 'Email',
      marketStatus: 'Listed',
      priority: 'Medium',
    },
  });

  // Watch for auto-calculations
  const askingPrice = watch('askingPrice');
  const numberOfUnits = watch('numberOfUnits');
  const inPlaceNOI = watch('inPlaceNOI');

  // Auto-calculate Price Per Unit
  useEffect(() => {
    if (askingPrice && numberOfUnits && numberOfUnits > 0) {
      const pricePerUnit = askingPrice / numberOfUnits;
      setValue('pricePerUnit', Math.round(pricePerUnit));
    }
  }, [askingPrice, numberOfUnits, setValue]);

  // Auto-calculate In-Place Cap Rate
  useEffect(() => {
    if (inPlaceNOI && askingPrice && askingPrice > 0) {
      const capRate = (inPlaceNOI / askingPrice) * 100;
      setValue('inPlaceCapRate', Number(capRate.toFixed(2)));
    }
  }, [inPlaceNOI, askingPrice, setValue]);

  // Helper function to convert frontend enum values to backend format
  const convertPropertyType = (type: string): string => {
    const mapping: Record<string, string> = {
      'Multifamily': 'MULTIFAMILY',
      'Single Family': 'SINGLE_FAMILY',
      'Student Housing': 'STUDENT_HOUSING',
      'Senior Housing': 'SENIOR_HOUSING',
      'Mobile Home Park': 'MOBILE_HOME_PARK',
      'Mixed Use': 'MIXED_USE',
      'Affordable Housing (Tax Credits)': 'AFFORDABLE_HOUSING',
      'Other': 'OTHER',
    };
    return mapping[type] || type.toUpperCase();
  };

  const convertPriority = (priority: string): string => {
    return priority.toUpperCase();
  };

  const convertHowReceived = (how: string): string => {
    const mapping: Record<string, string> = {
      'Email': 'EMAIL',
      'Phone Call': 'PHONE',
      'In Person': 'IN_PERSON',
      'Website/Portal': 'WEBSITE',
      'Referral': 'REFERRAL',
      'Other': 'OTHER',
    };
    return mapping[how] || how.toUpperCase();
  };

  const convertMarketStatus = (status: string): string => {
    const mapping: Record<string, string> = {
      'Listed': 'LISTED',
      'Off-Market': 'OFF_MARKET',
      'Pre-Market': 'PRE_MARKET',
      'Pocket Listing': 'POCKET_LISTING',
      'REO/Foreclosure': 'REO',
    };
    return mapping[status] || status.toUpperCase();
  };

  const convertSourceType = (type: string): string => {
    const mapping: Record<string, string> = {
      'Broker': 'BROKER',
      'Direct from Owner': 'DIRECT_OWNER',
      'Auction': 'AUCTION',
      'Wholesaler': 'WHOLESALER',
      'Network/Referral': 'NETWORK',
      'LoopNet/CoStar': 'LOOPNET_COSTAR',
      'Other': 'OTHER',
    };
    return mapping[type] || type.toUpperCase();
  };

  const onSubmit = async (data: FormData) => {
    setIsSubmitting(true);
    setSubmitError(null);
    setSubmitSuccess(false);

    try {
      // Transform form data to match backend API format (PRD Section 9.1)
      const apiPayload = {
        property_name: data.propertyName,
        address: {
          street: data.streetAddress || undefined,
          city: data.city || undefined,
          state: data.state || undefined,
          zip: data.zipCode || undefined,
        },
        property_type: convertPropertyType(data.propertyType),
        property_class: data.propertyClass || undefined,
        year_built: data.yearBuilt || undefined,
        units: data.numberOfUnits,
        asking_price: data.askingPrice || undefined,
        occupancy: data.currentOccupancy ? data.currentOccupancy / 100 : undefined, // Convert 0-100% to 0-1
        noi_in_place: data.inPlaceNOI || undefined,
        noi_pro_forma: data.proFormaNOI || undefined,
        source: {
          type: data.sourceType ? convertSourceType(data.sourceType) : undefined,
          name: data.sourceName || undefined,
          company: data.sourceCompany || undefined,
          email: data.sourceEmail || undefined,
          phone: data.sourcePhone || undefined,
        },
        notes: data.initialNotes || undefined,
        tags: data.tags || undefined,
        priority: data.priority ? convertPriority(data.priority) : undefined,
        how_received: data.howReceived ? convertHowReceived(data.howReceived) : undefined,
        market_status: data.marketStatus ? convertMarketStatus(data.marketStatus) : undefined,
      };

      // API call - use environment variable or default to localhost
      const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/api/v1/deals`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(apiPayload),
      });

      if (!response.ok) {
        const errorData = await response.json().catch(() => ({ 
          detail: { message: 'Failed to create deal' } 
        }));
        
        // Handle validation errors (422)
        if (response.status === 422 && errorData.detail) {
          if (typeof errorData.detail === 'string') {
            throw new Error(errorData.detail);
          } else if (errorData.detail.errors) {
            const errorMessages = Array.isArray(errorData.detail.errors) 
              ? errorData.detail.errors.join(', ')
              : errorData.detail.message || 'Validation failed';
            throw new Error(errorMessages);
          } else {
            throw new Error(errorData.detail.message || 'Validation failed');
          }
        }
        
        throw new Error(errorData.detail?.message || errorData.message || 'Failed to create deal');
      }

      const result = await response.json();
      setSubmitSuccess(true);
      
      if (onSuccess) {
        onSuccess(result.id);
      }
    } catch (error) {
      setSubmitError(error instanceof Error ? error.message : 'An unexpected error occurred');
    } finally {
      setIsSubmitting(false);
    }
  };


  if (submitSuccess) {
    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="bg-success-bg border border-success rounded-lg p-6 text-center">
          <CheckCircle2 className="w-12 h-12 text-success mx-auto mb-4" />
          <h2 className="text-2xl font-heading font-bold text-primary mb-2">Deal Created Successfully!</h2>
          <p className="text-secondary mb-6">Your deal has been added to the pipeline.</p>
          <Button onClick={() => window.location.reload()}>Create Another Deal</Button>
        </div>
      </div>
    );
  }

  return (
    <form onSubmit={handleSubmit(onSubmit)} className="max-w-4xl mx-auto p-6 space-y-8">
      {/* Success/Error Messages */}
      {submitError && (
        <div className="bg-danger-bg border border-danger rounded-lg p-4 flex items-start gap-3">
          <AlertCircle className="w-5 h-5 text-danger flex-shrink-0 mt-0.5" />
          <div>
            <h3 className="font-semibold text-danger mb-1">Error</h3>
            <p className="text-sm text-secondary">{submitError}</p>
          </div>
        </div>
      )}

      {/* Section 1: Property Identification */}
      <section className="bg-background-primary rounded-lg border border-border p-6">
        <h2 className="text-xl font-heading font-bold text-primary mb-6">Property Identification</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div className="md:col-span-2">
            <label htmlFor="propertyName" className="block text-sm font-medium text-secondary mb-2">
              Property Name <span className="text-danger">*</span>
            </label>
            <Input
              id="propertyName"
              {...register('propertyName')}
              aria-invalid={errors.propertyName ? 'true' : 'false'}
              className={errors.propertyName ? 'border-danger' : ''}
            />
            {errors.propertyName && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.propertyName.message}</p>
            )}
          </div>

          <div className="md:col-span-2">
            <label htmlFor="streetAddress" className="block text-sm font-medium text-secondary mb-2">
              Street Address <span className="text-danger">*</span>
            </label>
            <Input
              id="streetAddress"
              {...register('streetAddress')}
              aria-invalid={errors.streetAddress ? 'true' : 'false'}
              className={errors.streetAddress ? 'border-danger' : ''}
            />
            {errors.streetAddress && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.streetAddress.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="city" className="block text-sm font-medium text-secondary mb-2">
              City <span className="text-danger">*</span>
            </label>
            <Input
              id="city"
              {...register('city')}
              aria-invalid={errors.city ? 'true' : 'false'}
              className={errors.city ? 'border-danger' : ''}
            />
            {errors.city && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.city.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="state" className="block text-sm font-medium text-secondary mb-2">
              State <span className="text-danger">*</span>
            </label>
            <Select
              value={watch('state')}
              onValueChange={(value) => setValue('state', value as USState)}
            >
              <SelectTrigger id="state" aria-invalid={errors.state ? 'true' : 'false'}>
                <SelectValue placeholder="Select state" />
              </SelectTrigger>
              <SelectContent>
                {US_STATES.map((state) => (
                  <SelectItem key={state.value} value={state.value}>
                    {state.label}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
            {errors.state && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.state.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="zipCode" className="block text-sm font-medium text-secondary mb-2">
              ZIP Code <span className="text-danger">*</span>
            </label>
            <Input
              id="zipCode"
              {...register('zipCode')}
              placeholder="12345 or 12345-6789"
              aria-invalid={errors.zipCode ? 'true' : 'false'}
              className={errors.zipCode ? 'border-danger' : ''}
            />
            {errors.zipCode && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.zipCode.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="propertyType" className="block text-sm font-medium text-secondary mb-2">
              Property Type <span className="text-danger">*</span>
            </label>
            <Select
              value={watch('propertyType')}
              onValueChange={(value) => setValue('propertyType', value as PropertyType)}
            >
              <SelectTrigger id="propertyType">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Multifamily">Multifamily</SelectItem>
                <SelectItem value="Single Family">Single Family</SelectItem>
                <SelectItem value="Student Housing">Student Housing</SelectItem>
                <SelectItem value="Senior Housing">Senior Housing</SelectItem>
                <SelectItem value="Mobile Home Park">Mobile Home Park</SelectItem>
                <SelectItem value="Mixed Use">Mixed Use</SelectItem>
                <SelectItem value="Affordable Housing (Tax Credits)">Affordable Housing (Tax Credits)</SelectItem>
                <SelectItem value="Other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label htmlFor="propertyClass" className="block text-sm font-medium text-secondary mb-2">
              Property Class
            </label>
            <Select
              value={watch('propertyClass') || ''}
              onValueChange={(value) => setValue('propertyClass', value as PropertyClass)}
            >
              <SelectTrigger id="propertyClass">
                <SelectValue placeholder="Select class" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="A+">A+</SelectItem>
                <SelectItem value="A">A</SelectItem>
                <SelectItem value="A-">A-</SelectItem>
                <SelectItem value="B+">B+</SelectItem>
                <SelectItem value="B">B</SelectItem>
                <SelectItem value="B-">B-</SelectItem>
                <SelectItem value="C+">C+</SelectItem>
                <SelectItem value="C">C</SelectItem>
                <SelectItem value="C-">C-</SelectItem>
                <SelectItem value="D+">D+</SelectItem>
                <SelectItem value="D">D</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label htmlFor="yearBuilt" className="block text-sm font-medium text-secondary mb-2">
              Year Built
            </label>
            <Input
              id="yearBuilt"
              type="number"
              min="1800"
              max={new Date().getFullYear()}
              placeholder={`1800-${new Date().getFullYear()}`}
              {...register('yearBuilt', { valueAsNumber: true })}
              aria-invalid={errors.yearBuilt ? 'true' : 'false'}
              className={errors.yearBuilt ? 'border-danger' : ''}
            />
            {errors.yearBuilt && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.yearBuilt.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="numberOfUnits" className="block text-sm font-medium text-secondary mb-2">
              Number of Units <span className="text-danger">*</span>
            </label>
            <Input
              id="numberOfUnits"
              type="number"
              min="1"
              max="9999"
              className={`tabular-nums ${errors.numberOfUnits ? 'border-danger' : ''}`}
              {...register('numberOfUnits', { valueAsNumber: true })}
              aria-invalid={errors.numberOfUnits ? 'true' : 'false'}
            />
            {errors.numberOfUnits && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.numberOfUnits.message}</p>
            )}
          </div>
        </div>
      </section>

      {/* Section 2: Financial Overview */}
      <section className="bg-background-primary rounded-lg border border-border p-6">
        <h2 className="text-xl font-heading font-bold text-primary mb-6">Financial Overview</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="askingPrice" className="block text-sm font-medium text-secondary mb-2">
              Asking Price
            </label>
            <Input
              id="askingPrice"
              type="number"
              min="0"
              step="1000"
              placeholder="$0"
              className={`tabular-nums ${errors.askingPrice ? 'border-danger' : ''}`}
              {...register('askingPrice', { valueAsNumber: true })}
              aria-invalid={errors.askingPrice ? 'true' : 'false'}
            />
            {errors.askingPrice && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.askingPrice.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="pricePerUnit" className="block text-sm font-medium text-secondary mb-2">
              Price Per Unit
            </label>
            <Input
              id="pricePerUnit"
              type="number"
              readOnly
              value={watch('pricePerUnit') || ''}
              className="tabular-nums bg-background-secondary"
              tabIndex={-1}
            />
            <p className="mt-1 text-xs text-secondary-muted">Auto-calculated</p>
          </div>

          <div>
            <label htmlFor="currentOccupancy" className="block text-sm font-medium text-secondary mb-2">
              Current Occupancy (%)
            </label>
            <Input
              id="currentOccupancy"
              type="number"
              min="0"
              max="100"
              step="0.1"
              placeholder="0-100"
              className={`tabular-nums ${errors.currentOccupancy ? 'border-danger' : ''}`}
              {...register('currentOccupancy', { valueAsNumber: true })}
              aria-invalid={errors.currentOccupancy ? 'true' : 'false'}
            />
            {errors.currentOccupancy && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.currentOccupancy.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="inPlaceNOI" className="block text-sm font-medium text-secondary mb-2">
              In-Place NOI
            </label>
            <Input
              id="inPlaceNOI"
              type="number"
              min="0"
              step="1000"
              placeholder="$0"
              className={`tabular-nums ${errors.inPlaceNOI ? 'border-danger' : ''}`}
              {...register('inPlaceNOI', { valueAsNumber: true })}
              aria-invalid={errors.inPlaceNOI ? 'true' : 'false'}
            />
            {errors.inPlaceNOI && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.inPlaceNOI.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="proFormaNOI" className="block text-sm font-medium text-secondary mb-2">
              Pro Forma NOI
            </label>
            <Input
              id="proFormaNOI"
              type="number"
              min="0"
              step="1000"
              placeholder="$0"
              className={`tabular-nums ${errors.proFormaNOI ? 'border-danger' : ''}`}
              {...register('proFormaNOI', { valueAsNumber: true })}
              aria-invalid={errors.proFormaNOI ? 'true' : 'false'}
            />
            {errors.proFormaNOI && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.proFormaNOI.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="inPlaceCapRate" className="block text-sm font-medium text-secondary mb-2">
              In-Place Cap Rate (%)
            </label>
            <Input
              id="inPlaceCapRate"
              type="number"
              readOnly
              value={watch('inPlaceCapRate') || ''}
              className="tabular-nums bg-background-secondary"
              tabIndex={-1}
            />
            <p className="mt-1 text-xs text-secondary-muted">Auto-calculated</p>
          </div>
        </div>
      </section>

      {/* Section 3: Deal Source */}
      <section className="bg-background-primary rounded-lg border border-border p-6">
        <h2 className="text-xl font-heading font-bold text-primary mb-6">Deal Source</h2>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <div>
            <label htmlFor="sourceType" className="block text-sm font-medium text-secondary mb-2">
              Source Type
            </label>
            <Select
              value={watch('sourceType') || ''}
              onValueChange={(value) => setValue('sourceType', value as SourceType)}
            >
              <SelectTrigger id="sourceType">
                <SelectValue placeholder="Select source type" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Broker">Broker</SelectItem>
                <SelectItem value="Direct from Owner">Direct from Owner</SelectItem>
                <SelectItem value="Auction">Auction</SelectItem>
                <SelectItem value="Wholesaler">Wholesaler</SelectItem>
                <SelectItem value="Network/Referral">Network/Referral</SelectItem>
                <SelectItem value="LoopNet/CoStar">LoopNet/CoStar</SelectItem>
                <SelectItem value="Other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label htmlFor="howReceived" className="block text-sm font-medium text-secondary mb-2">
              How Received
            </label>
            <Select
              value={watch('howReceived') || ''}
              onValueChange={(value) => setValue('howReceived', value as HowReceived)}
            >
              <SelectTrigger id="howReceived">
                <SelectValue placeholder="Select how received" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Email">Email</SelectItem>
                <SelectItem value="Phone Call">Phone Call</SelectItem>
                <SelectItem value="In Person">In Person</SelectItem>
                <SelectItem value="Website/Portal">Website/Portal</SelectItem>
                <SelectItem value="Referral">Referral</SelectItem>
                <SelectItem value="Other">Other</SelectItem>
              </SelectContent>
            </Select>
          </div>

          <div>
            <label htmlFor="sourceName" className="block text-sm font-medium text-secondary mb-2">
              Source Name
            </label>
            <Input
              id="sourceName"
              {...register('sourceName')}
              placeholder="Broker/contact name"
            />
          </div>

          <div>
            <label htmlFor="sourceCompany" className="block text-sm font-medium text-secondary mb-2">
              Source Company
            </label>
            <Input
              id="sourceCompany"
              {...register('sourceCompany')}
              placeholder="Brokerage firm"
            />
          </div>

          <div>
            <label htmlFor="sourceEmail" className="block text-sm font-medium text-secondary mb-2">
              Source Email
            </label>
            <Input
              id="sourceEmail"
              type="email"
              {...register('sourceEmail')}
              placeholder="email@example.com"
              aria-invalid={errors.sourceEmail ? 'true' : 'false'}
              className={errors.sourceEmail ? 'border-danger' : ''}
            />
            {errors.sourceEmail && (
              <p className="mt-1 text-sm text-danger" role="alert">{errors.sourceEmail.message}</p>
            )}
          </div>

          <div>
            <label htmlFor="sourcePhone" className="block text-sm font-medium text-secondary mb-2">
              Source Phone
            </label>
            <Input
              id="sourcePhone"
              type="tel"
              {...register('sourcePhone')}
              placeholder="(555) 123-4567"
            />
          </div>

          <div>
            <label htmlFor="marketStatus" className="block text-sm font-medium text-secondary mb-2">
              Market Status
            </label>
            <Select
              value={watch('marketStatus') || ''}
              onValueChange={(value) => setValue('marketStatus', value as MarketStatus)}
            >
              <SelectTrigger id="marketStatus">
                <SelectValue placeholder="Select market status" />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Listed">Listed</SelectItem>
                <SelectItem value="Off-Market">Off-Market</SelectItem>
                <SelectItem value="Pre-Market">Pre-Market</SelectItem>
                <SelectItem value="Pocket Listing">Pocket Listing</SelectItem>
                <SelectItem value="REO/Foreclosure">REO/Foreclosure</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </section>

      {/* Section 4: Notes & Tags */}
      <section className="bg-background-primary rounded-lg border border-border p-6">
        <h2 className="text-xl font-heading font-bold text-primary mb-6">Notes & Tags</h2>
        
        <div className="space-y-6">
          <div>
            <label htmlFor="initialNotes" className="block text-sm font-medium text-secondary mb-2">
              Initial Notes
            </label>
            <Textarea
              id="initialNotes"
              rows={6}
              maxLength={2000}
              {...register('initialNotes')}
              placeholder="Add any additional notes about this deal..."
              className={errors.initialNotes ? 'border-danger' : ''}
            />
            <p className="mt-1 text-xs text-secondary-muted">
              {watch('initialNotes')?.length || 0} / 2000 characters
            </p>
          </div>

          <div>
            <label htmlFor="priority" className="block text-sm font-medium text-secondary mb-2">
              Priority
            </label>
            <Select
              value={watch('priority') || 'Medium'}
              onValueChange={(value) => setValue('priority', value as Priority)}
            >
              <SelectTrigger id="priority">
                <SelectValue />
              </SelectTrigger>
              <SelectContent>
                <SelectItem value="Low">Low</SelectItem>
                <SelectItem value="Medium">Medium</SelectItem>
                <SelectItem value="High">High</SelectItem>
              </SelectContent>
            </Select>
          </div>
        </div>
      </section>

      {/* Form Actions */}
      <div className="flex flex-col sm:flex-row gap-4 justify-end">
        {onCancel && (
          <Button type="button" variant="outline" onClick={onCancel} disabled={isSubmitting}>
            Cancel
          </Button>
        )}
        <Button type="submit" disabled={isSubmitting} className="min-w-[120px]">
          {isSubmitting ? (
            <>
              <Loader2 className="w-4 h-4 mr-2 animate-spin" />
              Creating...
            </>
          ) : (
            'Create Deal'
          )}
        </Button>
      </div>
    </form>
  );
};

export default ManualEntryForm;

