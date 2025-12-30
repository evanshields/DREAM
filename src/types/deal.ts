/**
 * TypeScript types for Deal data structures
 * Based on PRD Section 5.1: Manual Entry Form
 */

export type PropertyType = 
  | 'Multifamily'
  | 'Single Family'
  | 'Student Housing'
  | 'Senior Housing'
  | 'Mobile Home Park'
  | 'Mixed Use'
  | 'Affordable Housing (Tax Credits)'
  | 'Other';

export type PropertyClass = 
  | 'A+'
  | 'A'
  | 'A-'
  | 'B+'
  | 'B'
  | 'B-'
  | 'C+'
  | 'C'
  | 'C-'
  | 'D+'
  | 'D';

export type SourceType = 
  | 'Broker'
  | 'Direct from Owner'
  | 'Auction'
  | 'Wholesaler'
  | 'Network/Referral'
  | 'LoopNet/CoStar'
  | 'Other';

export type HowReceived = 
  | 'Email'
  | 'Phone Call'
  | 'In Person'
  | 'Website/Portal'
  | 'Referral'
  | 'Other';

export type MarketStatus = 
  | 'Listed'
  | 'Off-Market'
  | 'Pre-Market'
  | 'Pocket Listing'
  | 'REO/Foreclosure';

export type Priority = 'Low' | 'Medium' | 'High';

export type DealStatus = 
  | 'New'
  | 'Screening'
  | 'LOI'
  | 'Due Diligence'
  | 'Under Contract'
  | 'Closed'
  | 'Passed';

export type USState = 
  | 'AL' | 'AK' | 'AZ' | 'AR' | 'CA' | 'CO' | 'CT' | 'DE' | 'FL' | 'GA'
  | 'HI' | 'ID' | 'IL' | 'IN' | 'IA' | 'KS' | 'KY' | 'LA' | 'ME' | 'MD'
  | 'MA' | 'MI' | 'MN' | 'MS' | 'MO' | 'MT' | 'NE' | 'NV' | 'NH' | 'NJ'
  | 'NM' | 'NY' | 'NC' | 'ND' | 'OH' | 'OK' | 'OR' | 'PA' | 'RI' | 'SC'
  | 'SD' | 'TN' | 'TX' | 'UT' | 'VT' | 'VA' | 'WA' | 'WV' | 'WI' | 'WY'
  | 'DC' | 'AS' | 'GU' | 'MP' | 'PR' | 'VI';

/**
 * Manual Entry Form Data Structure
 */
export interface ManualEntryFormData {
  // Section 1: Property Identification
  propertyName: string;
  streetAddress: string;
  city: string;
  state: USState;
  zipCode: string;
  propertyType: PropertyType;
  propertyClass?: PropertyClass;
  yearBuilt?: number;
  numberOfUnits: number;

  // Section 2: Financial Overview
  askingPrice?: number;
  pricePerUnit?: number; // Auto-calculated
  currentOccupancy?: number; // Percentage 0-100
  inPlaceNOI?: number;
  proFormaNOI?: number;
  inPlaceCapRate?: number; // Auto-calculated

  // Section 3: Deal Source
  sourceType?: SourceType;
  sourceName?: string;
  sourceCompany?: string;
  sourceEmail?: string;
  sourcePhone?: string;
  howReceived?: HowReceived;
  marketStatus?: MarketStatus;

  // Section 4: Notes & Tags
  initialNotes?: string;
  tags?: string[];
  priority?: Priority;
}

/**
 * Deal creation payload for API
 */
export interface CreateDealPayload {
  name: string;
  address: string;
  city: string;
  state: string;
  zipCode: string;
  propertyType: PropertyType;
  propertyClass?: PropertyClass;
  yearBuilt?: number;
  units: number;
  askingPrice?: number;
  currentOccupancy?: number;
  inPlaceNOI?: number;
  proFormaNOI?: number;
  sourceType?: SourceType;
  sourceName?: string;
  sourceCompany?: string;
  sourceEmail?: string;
  sourcePhone?: string;
  howReceived?: HowReceived;
  marketStatus?: MarketStatus;
  notes?: string;
  tags?: string[];
  priority?: Priority;
}

/**
 * Deal list item (for list views)
 */
export interface DealListItem {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  zipCode?: string;
  propertyType: PropertyType;
  propertyClass?: PropertyClass;
  units: number;
  askingPrice?: number;
  currentOccupancy?: number;
  status: DealStatus;
  priority?: Priority;
  createdAt: string | Date;
  updatedAt?: string | Date;
  score?: number;
  recommendation?: 'STRONG BUY' | 'BUY' | 'HOLD' | 'PASS';
  daysInStage?: number;
  assignedTo?: string[];
  tags?: string[];
}

/**
 * Form validation errors
 */
export interface FormErrors {
  [key: string]: string | undefined;
}
