export interface Metric {
  label: string;
  value: string;
  target?: string;
  status: 'positive' | 'neutral' | 'negative';
}

export interface Deal {
  id: string;
  name: string;
  address: string;
  units: number;
  price: number;
  vintage: number;
  score: number;
  recommendation: 'STRONG BUY' | 'BUY' | 'HOLD' | 'PASS';
  stage: 'New' | 'Screening' | 'LOI' | 'Due Diligence' | 'Under Contract' | 'Closed' | 'Passed';
  daysInStage: number;
  assignedTo: string[];
  metrics: {
    irr: string;
    em: string;
    coc: string;
    dscr: string;
    capRate: string;
    pricePerUnit: string;
  };
  summary: string;
  location: string;
  image?: string;
}

export type ViewState = 'dashboard' | 'pipeline' | 'analysis' | 'intake' | 'landing';
