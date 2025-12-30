import React, { useState, useEffect, useMemo } from 'react';
import { useNavigate } from 'react-router-dom';
import { Search, Filter, ArrowUpDown, Plus, Loader2 } from 'lucide-react';
import { Input } from '@/components/ui/input';
import { Button } from '@/components/ui/button';
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from '@/components/ui/select';
import DealCard from '@/components/DealCard';
import StatusBadge from '@/components/StatusBadge';
import type { DealListItem, DealStatus, Priority, PropertyType } from '@/types/deal';
import { Card } from '@/components/UIComponents';

// Mock data - Replace with API call when backend is ready
const mockDeals: DealListItem[] = [
  {
    id: '1',
    name: 'Oak Creek Apartments',
    address: '1234 Oak Creek Dr',
    city: 'Austin',
    state: 'TX',
    zipCode: '78701',
    propertyType: 'Multifamily',
    propertyClass: 'B+',
    units: 96,
    askingPrice: 12500000,
    currentOccupancy: 92,
    status: 'Screening',
    priority: 'High',
    createdAt: new Date('2024-01-15'),
    score: 78,
    recommendation: 'BUY',
    daysInStage: 5,
    tags: ['Value-Add', 'Austin'],
  },
  {
    id: '2',
    name: 'Riverside Commons',
    address: '5678 Riverside Blvd',
    city: 'Dallas',
    state: 'TX',
    zipCode: '75201',
    propertyType: 'Multifamily',
    propertyClass: 'A-',
    units: 120,
    askingPrice: 18500000,
    currentOccupancy: 95,
    status: 'LOI',
    priority: 'High',
    createdAt: new Date('2024-01-10'),
    score: 85,
    recommendation: 'STRONG BUY',
    daysInStage: 12,
    tags: ['Stabilized', 'Dallas'],
  },
  {
    id: '3',
    name: 'Sunset Terrace',
    address: '9012 Sunset Ave',
    city: 'Houston',
    state: 'TX',
    zipCode: '77002',
    propertyType: 'Multifamily',
    propertyClass: 'C+',
    units: 64,
    askingPrice: 6800000,
    currentOccupancy: 88,
    status: 'New',
    priority: 'Medium',
    createdAt: new Date('2024-01-20'),
    score: 65,
    recommendation: 'HOLD',
    daysInStage: 2,
    tags: ['Distressed', 'Houston'],
  },
  {
    id: '4',
    name: 'University Heights',
    address: '3456 University Dr',
    city: 'College Station',
    state: 'TX',
    zipCode: '77840',
    propertyType: 'Student Housing',
    propertyClass: 'B',
    units: 200,
    askingPrice: 22000000,
    currentOccupancy: 98,
    status: 'Due Diligence',
    priority: 'High',
    createdAt: new Date('2024-01-05'),
    score: 82,
    recommendation: 'BUY',
    daysInStage: 20,
    tags: ['Student Housing', 'College Station'],
  },
  {
    id: '5',
    name: 'Maple Grove Senior Living',
    address: '7890 Maple Grove Ln',
    city: 'San Antonio',
    state: 'TX',
    zipCode: '78201',
    propertyType: 'Senior Housing',
    propertyClass: 'A',
    units: 80,
    askingPrice: 14500000,
    currentOccupancy: 94,
    status: 'Under Contract',
    priority: 'High',
    createdAt: new Date('2023-12-20'),
    score: 88,
    recommendation: 'STRONG BUY',
    daysInStage: 35,
    tags: ['Senior Housing', 'San Antonio'],
  },
  {
    id: '6',
    name: 'Parkview Apartments',
    address: '2345 Parkview St',
    city: 'Fort Worth',
    state: 'TX',
    zipCode: '76102',
    propertyType: 'Multifamily',
    propertyClass: 'C',
    units: 48,
    askingPrice: 4200000,
    currentOccupancy: 85,
    status: 'New',
    priority: 'Low',
    createdAt: new Date('2024-01-22'),
    score: 58,
    recommendation: 'PASS',
    daysInStage: 1,
    tags: ['Value-Add', 'Fort Worth'],
  },
];

type SortField = 'createdAt' | 'askingPrice' | 'name';
type SortDirection = 'asc' | 'desc';

export default function DealsList() {
  const navigate = useNavigate();
  const [deals, setDeals] = useState<DealListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [searchQuery, setSearchQuery] = useState('');
  const [statusFilter, setStatusFilter] = useState<DealStatus | 'all'>('all');
  const [priorityFilter, setPriorityFilter] = useState<Priority | 'all'>('all');
  const [propertyTypeFilter, setPropertyTypeFilter] = useState<PropertyType | 'all'>('all');
  const [sortField, setSortField] = useState<SortField>('createdAt');
  const [sortDirection, setSortDirection] = useState<SortDirection>('desc');

  // Fetch deals from API
  useEffect(() => {
    const fetchDeals = async () => {
      setLoading(true);
      try {
        // Build query parameters
        const params = new URLSearchParams();
        if (statusFilter !== 'all') params.append('status', statusFilter);
        if (priorityFilter !== 'all') params.append('priority', priorityFilter);
        if (propertyTypeFilter !== 'all') params.append('property_type', propertyTypeFilter);
        params.append('sort_by', sortField === 'createdAt' ? 'created_at' : sortField === 'askingPrice' ? 'asking_price' : 'property_name');
        params.append('sort_order', sortDirection);
        params.append('page', '1');
        params.append('page_size', '100'); // Get all for client-side filtering
        
        const apiUrl = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        const response = await fetch(`${apiUrl}/api/v1/deals?${params.toString()}`);
        
        if (!response.ok) {
          throw new Error(`Failed to fetch deals: ${response.statusText}`);
        }
        
        const data = await response.json();
        
        // Transform API response to DealListItem format
        const transformedDeals: DealListItem[] = data.deals.map((deal: any) => ({
          id: deal.id,
          name: deal.property_name,
          address: deal.address_street || '',
          city: deal.address_city || '',
          state: deal.address_state || '',
          zipCode: deal.address_zip,
          propertyType: deal.property_type || 'Multifamily',
          propertyClass: deal.property_class as PropertyClass | undefined,
          units: deal.units || 0,
          askingPrice: deal.asking_price ? parseFloat(deal.asking_price.toString()) : undefined,
          currentOccupancy: deal.occupancy ? parseFloat(deal.occupancy.toString()) * 100 : undefined, // Convert 0-1 to 0-100
          status: deal.stage as DealStatus,
          priority: deal.priority as Priority | undefined,
          createdAt: new Date(deal.created_at),
          tags: [],
        }));
        
        setDeals(transformedDeals);
      } catch (error) {
        console.error('Failed to fetch deals:', error);
        // Fallback to mock data if API fails
        setDeals(mockDeals);
      } finally {
        setLoading(false);
      }
    };

    fetchDeals();
  }, [statusFilter, priorityFilter, propertyTypeFilter, sortField, sortDirection]);

  // Filter and sort deals
  const filteredAndSortedDeals = useMemo(() => {
    let filtered = [...deals];

    // Search filter
    if (searchQuery) {
      const query = searchQuery.toLowerCase();
      filtered = filtered.filter(
        deal =>
          deal.name.toLowerCase().includes(query) ||
          deal.address.toLowerCase().includes(query) ||
          deal.city.toLowerCase().includes(query) ||
          deal.state.toLowerCase().includes(query) ||
          deal.tags?.some(tag => tag.toLowerCase().includes(query))
      );
    }

    // Status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter(deal => deal.status === statusFilter);
    }

    // Priority filter
    if (priorityFilter !== 'all') {
      filtered = filtered.filter(deal => deal.priority === priorityFilter);
    }

    // Property type filter
    if (propertyTypeFilter !== 'all') {
      filtered = filtered.filter(deal => deal.propertyType === propertyTypeFilter);
    }

    // Sort
    filtered.sort((a, b) => {
      let aValue: string | number | Date;
      let bValue: string | number | Date;

      switch (sortField) {
        case 'name':
          aValue = a.name.toLowerCase();
          bValue = b.name.toLowerCase();
          break;
        case 'askingPrice':
          aValue = a.askingPrice || 0;
          bValue = b.askingPrice || 0;
          break;
        case 'createdAt':
          aValue = new Date(a.createdAt).getTime();
          bValue = new Date(b.createdAt).getTime();
          break;
        default:
          return 0;
      }

      if (aValue < bValue) return sortDirection === 'asc' ? -1 : 1;
      if (aValue > bValue) return sortDirection === 'asc' ? 1 : -1;
      return 0;
    });

    return filtered;
  }, [deals, searchQuery, statusFilter, priorityFilter, propertyTypeFilter, sortField, sortDirection]);

  const handleSort = (field: SortField) => {
    if (sortField === field) {
      setSortDirection(sortDirection === 'asc' ? 'desc' : 'asc');
    } else {
      setSortField(field);
      setSortDirection('desc');
    }
  };

  const getStatusVariant = (status: DealStatus): 'default' | 'success' | 'warning' | 'danger' | 'info' => {
    switch (status) {
      case 'Closed':
        return 'success';
      case 'Under Contract':
      case 'Due Diligence':
        return 'info';
      case 'LOI':
      case 'Screening':
        return 'warning';
      case 'Passed':
        return 'danger';
      default:
        return 'default';
    }
  };

  const getPriorityVariant = (priority?: Priority): 'default' | 'success' | 'warning' | 'danger' | 'info' => {
    switch (priority) {
      case 'High':
        return 'danger';
      case 'Medium':
        return 'warning';
      case 'Low':
        return 'default';
      default:
        return 'default';
    }
  };

  const formatDate = (date: string | Date) => {
    const d = new Date(date);
    return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });
  };

  if (loading) {
    return (
      <div className="flex items-center justify-center min-h-screen">
        <div className="flex flex-col items-center gap-4">
          <Loader2 className="w-8 h-8 animate-spin text-accent-primary" />
          <p className="text-secondary-muted">Loading deals...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="max-w-7xl mx-auto p-6 space-y-6">
      {/* Header */}
      <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-4">
        <div>
          <h1 className="text-3xl font-heading font-bold text-primary mb-2">Deals</h1>
          <p className="text-secondary-muted">
            {filteredAndSortedDeals.length} {filteredAndSortedDeals.length === 1 ? 'deal' : 'deals'}
            {searchQuery || statusFilter !== 'all' || priorityFilter !== 'all' || propertyTypeFilter !== 'all'
              ? ' (filtered)'
              : ''}
          </p>
        </div>
        <Button onClick={() => navigate('/deals/new')} className="min-w-[140px]">
          <Plus className="w-4 h-4 mr-2" />
          New Deal
        </Button>
      </div>

      {/* Filters and Search */}
      <Card className="p-4">
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-4">
          {/* Search */}
          <div className="lg:col-span-2 relative">
            <Search className="absolute left-3 top-1/2 transform -translate-y-1/2 w-4 h-4 text-secondary-muted" />
            <Input
              type="text"
              placeholder="Search deals..."
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              className="pl-9"
            />
          </div>

          {/* Status Filter */}
          <Select value={statusFilter} onValueChange={(value) => setStatusFilter(value as DealStatus | 'all')}>
            <SelectTrigger>
              <SelectValue placeholder="All Statuses" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Statuses</SelectItem>
              <SelectItem value="New">New</SelectItem>
              <SelectItem value="Screening">Screening</SelectItem>
              <SelectItem value="LOI">LOI</SelectItem>
              <SelectItem value="Due Diligence">Due Diligence</SelectItem>
              <SelectItem value="Under Contract">Under Contract</SelectItem>
              <SelectItem value="Closed">Closed</SelectItem>
              <SelectItem value="Passed">Passed</SelectItem>
            </SelectContent>
          </Select>

          {/* Priority Filter */}
          <Select value={priorityFilter} onValueChange={(value) => setPriorityFilter(value as Priority | 'all')}>
            <SelectTrigger>
              <SelectValue placeholder="All Priorities" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Priorities</SelectItem>
              <SelectItem value="High">High</SelectItem>
              <SelectItem value="Medium">Medium</SelectItem>
              <SelectItem value="Low">Low</SelectItem>
            </SelectContent>
          </Select>

          {/* Property Type Filter */}
          <Select
            value={propertyTypeFilter}
            onValueChange={(value) => setPropertyTypeFilter(value as PropertyType | 'all')}
          >
            <SelectTrigger>
              <SelectValue placeholder="All Types" />
            </SelectTrigger>
            <SelectContent>
              <SelectItem value="all">All Types</SelectItem>
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

        {/* Sort Options */}
        <div className="flex items-center gap-2 mt-4 pt-4 border-t border-border">
          <span className="text-sm text-secondary-muted">Sort by:</span>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleSort('createdAt')}
            className="h-8"
          >
            Date
            {sortField === 'createdAt' && (
              <ArrowUpDown className={`w-3 h-3 ml-1 ${sortDirection === 'asc' ? 'rotate-180' : ''}`} />
            )}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleSort('askingPrice')}
            className="h-8"
          >
            Price
            {sortField === 'askingPrice' && (
              <ArrowUpDown className={`w-3 h-3 ml-1 ${sortDirection === 'asc' ? 'rotate-180' : ''}`} />
            )}
          </Button>
          <Button
            variant="ghost"
            size="sm"
            onClick={() => handleSort('name')}
            className="h-8"
          >
            Name
            {sortField === 'name' && (
              <ArrowUpDown className={`w-3 h-3 ml-1 ${sortDirection === 'asc' ? 'rotate-180' : ''}`} />
            )}
          </Button>
        </div>
      </Card>

      {/* Deal List */}
      {filteredAndSortedDeals.length === 0 ? (
        <Card className="p-12 text-center">
          <div className="max-w-md mx-auto">
            <Filter className="w-12 h-12 text-secondary-muted mx-auto mb-4" />
            <h3 className="text-xl font-heading font-semibold text-primary mb-2">No deals found</h3>
            <p className="text-secondary-muted mb-6">
              {searchQuery || statusFilter !== 'all' || priorityFilter !== 'all' || propertyTypeFilter !== 'all'
                ? 'Try adjusting your filters or search query.'
                : 'Get started by creating your first deal.'}
            </p>
            {(!searchQuery && statusFilter === 'all' && priorityFilter === 'all' && propertyTypeFilter === 'all') && (
              <Button onClick={() => navigate('/deals/new')}>
                <Plus className="w-4 h-4 mr-2" />
                Create New Deal
              </Button>
            )}
          </div>
        </Card>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {filteredAndSortedDeals.map((deal) => (
            <div key={deal.id} className="relative">
              <DealCard
                deal={{
                  id: deal.id,
                  name: deal.name,
                  address: deal.address,
                  city: deal.city,
                  state: deal.state,
                  units: deal.units,
                  askingPrice: deal.askingPrice || 0,
                  score: deal.score || 0,
                  recommendation: (deal.recommendation?.replace(' ', '_') || 'HOLD') as 'STRONG_BUY' | 'BUY' | 'HOLD' | 'PASS',
                  daysInStage: deal.daysInStage || 0,
                }}
                onClick={() => navigate(`/deals/${deal.id}`)}
              />
              {/* Status and Priority Badges */}
              <div className="absolute top-4 right-4 flex flex-col gap-2">
                <StatusBadge status={deal.status} variant={getStatusVariant(deal.status)} />
                {deal.priority && (
                  <StatusBadge status={deal.priority} variant={getPriorityVariant(deal.priority)} />
                )}
              </div>
              {/* Created Date */}
              <div className="absolute bottom-4 left-4 text-xs text-secondary-muted">
                Created {formatDate(deal.createdAt)}
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

