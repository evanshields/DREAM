import type { Deal } from './types';

export const MOCK_ANALYSIS_DEAL: Deal = {
  id: '1',
  name: 'Sunset Ridge Apartments',
  address: '4521 Palm Harbor Drive, Tampa, FL 33615',
  units: 248,
  vintage: 1998,
  price: 35340000,
  score: 87,
  recommendation: 'STRONG BUY',
  stage: 'Screening',
  daysInStage: 2,
  assignedTo: ['JD'],
  location: 'Tampa, FL',
  summary: 'Strong value-add opportunity in high-growth Tampa submarket with above-target returns',
  metrics: {
    irr: '18.5%',
    em: '2.1x',
    coc: '8.2%',
    dscr: '1.42x',
    capRate: '5.8%',
    pricePerUnit: '$142,500'
  }
};

export const PIPELINE_DEALS: Deal[] = [
  MOCK_ANALYSIS_DEAL,
  {
    id: '2',
    name: 'Highland Park Lofts',
    address: '1200 Highland Ave, Atlanta, GA',
    units: 156,
    vintage: 2015,
    price: 42000000,
    score: 74,
    recommendation: 'HOLD',
    stage: 'New',
    daysInStage: 1,
    assignedTo: ['SAR'],
    location: 'Atlanta, GA',
    summary: 'Class A asset with minimal upside, priced aggressively.',
    metrics: {
        irr: '13.2%',
        em: '1.6x',
        coc: '5.5%',
        dscr: '1.25x',
        capRate: '4.9%',
        pricePerUnit: '$269,000'
    }
  },
  {
    id: '3',
    name: 'The Oaks at Riverview',
    address: '88 Riverview Dr, Austin, TX',
    units: 312,
    vintage: 1985,
    price: 28500000,
    score: 62,
    recommendation: 'PASS',
    stage: 'Screening',
    daysInStage: 5,
    assignedTo: ['JD', 'MK'],
    location: 'Austin, TX',
    summary: 'Significant deferred maintenance identified in initial scan.',
    metrics: {
        irr: '11.0%',
        em: '1.4x',
        coc: '4.2%',
        dscr: '1.15x',
        capRate: '5.2%',
        pricePerUnit: '$91,300'
    }
  },
  {
    id: '4',
    name: 'Beacon Hill Flats',
    address: 'Seattle, WA',
    units: 85,
    vintage: 1960,
    price: 18000000,
    score: 81,
    recommendation: 'BUY',
    stage: 'LOI',
    daysInStage: 12,
    assignedTo: ['MK'],
    location: 'Seattle, WA',
    summary: 'Prime location value-add, heavy lift but high reward.',
    metrics: {
        irr: '16.8%',
        em: '2.0x',
        coc: '6.5%',
        dscr: '1.30x',
        capRate: '5.1%',
        pricePerUnit: '$211,700'
    }
  },
  {
    id: '5',
    name: 'Desert Springs',
    address: 'Phoenix, AZ',
    units: 200,
    vintage: 2002,
    price: 38000000,
    score: 89,
    recommendation: 'STRONG BUY',
    stage: 'Due Diligence',
    daysInStage: 24,
    assignedTo: ['SAR', 'JD'],
    location: 'Phoenix, AZ',
    summary: 'Off-market deal with motivated seller.',
    metrics: {
        irr: '19.2%',
        em: '2.3x',
        coc: '9.1%',
        dscr: '1.55x',
        capRate: '6.2%',
        pricePerUnit: '$190,000'
    }
  },
   {
    id: '6',
    name: 'Maplewood Courts',
    address: 'Charlotte, NC',
    units: 120,
    vintage: 1990,
    price: 15000000,
    score: 55,
    recommendation: 'PASS',
    stage: 'Passed',
    daysInStage: 0,
    assignedTo: ['MK'],
    location: 'Charlotte, NC',
    summary: 'Flood zone risk too high.',
    metrics: {
        irr: '10.0%',
        em: '1.2x',
        coc: '4.0%',
        dscr: '1.10x',
        capRate: '5.0%',
        pricePerUnit: '$125,000'
    }
  }
];

export const PIPELINE_STAGES = [
  'New',
  'Screening',
  'LOI',
  'Due Diligence',
  'Under Contract',
  'Closed',
  'Passed'
];
