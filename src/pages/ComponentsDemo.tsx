import { Plus } from 'lucide-react';
import MetricCard from '../components/MetricCard';
import RecommendationBadge from '../components/RecommendationBadge';
import ScoreBadge from '../components/ScoreBadge';
import StatusBadge from '../components/StatusBadge';
import SectionHeader from '../components/SectionHeader';
import DealCard from '../components/DealCard';

export default function ComponentsDemo() {
  const sampleDeals = [
    {
      id: '1',
      name: 'Sunset Gardens Apartments',
      address: '1234 Maple Street',
      city: 'Austin',
      state: 'TX',
      units: 48,
      askingPrice: 8500000,
      score: 87,
      recommendation: 'STRONG_BUY' as const,
      daysInStage: 12,
      assignee: 'John D.',
    },
    {
      id: '2',
      name: 'Downtown Plaza',
      address: '567 Oak Avenue',
      city: 'Denver',
      state: 'CO',
      units: 120,
      askingPrice: 22000000,
      score: 65,
      recommendation: 'HOLD' as const,
      daysInStage: 28,
      assignee: 'Sarah M.',
    },
    {
      id: '3',
      name: 'River View Complex',
      address: '890 Pine Road',
      city: 'Portland',
      state: 'OR',
      units: 75,
      askingPrice: 12500000,
      score: 42,
      recommendation: 'PASS' as const,
      daysInStage: 5,
    },
  ];

  return (
    <div className="p-8 bg-background-secondary min-h-screen">
      <div className="max-w-7xl mx-auto space-y-12">
        {/* Page Header */}
        <div>
          <h1 className="text-4xl font-heading font-bold text-primary mb-2">
            Component Library Demo
          </h1>
          <p className="text-muted">
            Showcasing all reusable components with sample data
          </p>
        </div>

        {/* MetricCard Section */}
        <section>
          <SectionHeader
            title="MetricCard"
            subtitle="Display key metrics with optional trends and status colors"
          />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <MetricCard
              label="Total Portfolio Value"
              value="$142.5M"
              trend="up"
              status="success"
            />
            <MetricCard
              label="Active Deals"
              value="23"
              subtext="+3 this week"
              trend="up"
            />
            <MetricCard
              label="Avg. Deal Score"
              value="72"
              trend="down"
              status="warning"
            />
            <MetricCard
              label="Close Rate"
              value="34%"
              subtext="Last 30 days"
              status="neutral"
            />
          </div>
        </section>

        {/* RecommendationBadge Section */}
        <section>
          <SectionHeader
            title="RecommendationBadge"
            subtitle="Investment recommendation indicators"
          />
          <div className="bg-white p-8 rounded-lg border border-border">
            <div className="space-y-6">
              <div>
                <p className="text-sm text-muted mb-3">Small Size</p>
                <div className="flex flex-wrap gap-3">
                  <RecommendationBadge recommendation="STRONG_BUY" size="sm" />
                  <RecommendationBadge recommendation="BUY" size="sm" />
                  <RecommendationBadge recommendation="HOLD" size="sm" />
                  <RecommendationBadge recommendation="PASS" size="sm" />
                </div>
              </div>
              <div>
                <p className="text-sm text-muted mb-3">Medium Size (Default)</p>
                <div className="flex flex-wrap gap-3">
                  <RecommendationBadge recommendation="STRONG_BUY" />
                  <RecommendationBadge recommendation="BUY" />
                  <RecommendationBadge recommendation="HOLD" />
                  <RecommendationBadge recommendation="PASS" />
                </div>
              </div>
              <div>
                <p className="text-sm text-muted mb-3">Large Size (Analysis Header)</p>
                <div className="flex flex-wrap gap-3">
                  <RecommendationBadge recommendation="STRONG_BUY" size="lg" />
                  <RecommendationBadge recommendation="BUY" size="lg" />
                  <RecommendationBadge recommendation="HOLD" size="lg" />
                  <RecommendationBadge recommendation="PASS" size="lg" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* ScoreBadge Section */}
        <section>
          <SectionHeader
            title="ScoreBadge"
            subtitle="Circular score indicators with progress rings"
          />
          <div className="bg-white p-8 rounded-lg border border-border">
            <div className="space-y-6">
              <div>
                <p className="text-sm text-muted mb-4">Small Size</p>
                <div className="flex flex-wrap gap-6">
                  <ScoreBadge score={87} size="sm" />
                  <ScoreBadge score={65} size="sm" />
                  <ScoreBadge score={42} size="sm" />
                </div>
              </div>
              <div>
                <p className="text-sm text-muted mb-4">Medium Size</p>
                <div className="flex flex-wrap gap-6">
                  <ScoreBadge score={87} size="md" />
                  <ScoreBadge score={65} size="md" />
                  <ScoreBadge score={42} size="md" />
                </div>
              </div>
              <div>
                <p className="text-sm text-muted mb-4">Large Size</p>
                <div className="flex flex-wrap gap-6">
                  <ScoreBadge score={87} size="lg" />
                  <ScoreBadge score={65} size="lg" />
                  <ScoreBadge score={42} size="lg" />
                </div>
              </div>
            </div>
          </div>
        </section>

        {/* StatusBadge Section */}
        <section>
          <SectionHeader
            title="StatusBadge"
            subtitle="Generic status indicators for various states"
          />
          <div className="bg-white p-8 rounded-lg border border-border">
            <div className="flex flex-wrap gap-3">
              <StatusBadge status="Active" variant="success" />
              <StatusBadge status="Pending" variant="warning" />
              <StatusBadge status="Rejected" variant="danger" />
              <StatusBadge status="Under Review" variant="info" />
              <StatusBadge status="Draft" variant="default" />
              <StatusBadge status="In Diligence" variant="info" />
              <StatusBadge status="Closed Won" variant="success" />
              <StatusBadge status="Archived" variant="default" />
            </div>
          </div>
        </section>

        {/* SectionHeader Section */}
        <section>
          <SectionHeader
            title="SectionHeader"
            subtitle="Consistent headers for content sections"
          />
          <div className="space-y-4">
            <div className="bg-white p-6 rounded-lg border border-border">
              <SectionHeader title="Simple Header" />
              <p className="text-sm text-muted">Content goes here...</p>
            </div>
            <div className="bg-white p-6 rounded-lg border border-border">
              <SectionHeader
                title="Header with Subtitle"
                subtitle="This is a descriptive subtitle"
              />
              <p className="text-sm text-muted">Content goes here...</p>
            </div>
            <div className="bg-white p-6 rounded-lg border border-border">
              <SectionHeader
                title="Header with Action"
                subtitle="Includes an action button"
                action={
                  <button className="flex items-center gap-2 px-4 py-2 bg-primary-seafoam text-white rounded-lg hover:bg-primary-teal transition-colors">
                    <Plus size={16} />
                    Add New
                  </button>
                }
              />
              <p className="text-sm text-muted">Content goes here...</p>
            </div>
          </div>
        </section>

        {/* DealCard Section */}
        <section>
          <SectionHeader
            title="DealCard"
            subtitle="Compact cards for pipeline and list views"
          />
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            {sampleDeals.map((deal) => (
              <DealCard
                key={deal.id}
                deal={deal}
                onClick={() => alert(`Clicked deal: ${deal.name}`)}
              />
            ))}
          </div>
        </section>
      </div>
    </div>
  );
}
