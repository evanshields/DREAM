import { MapPin, Calendar, User } from 'lucide-react';
import ScoreBadge from './ScoreBadge';
import RecommendationBadge from './RecommendationBadge';

type Recommendation = 'STRONG_BUY' | 'BUY' | 'HOLD' | 'PASS';

interface Deal {
  id: string;
  name: string;
  address: string;
  city: string;
  state: string;
  units: number;
  askingPrice: number;
  score: number;
  recommendation: Recommendation;
  daysInStage: number;
  assignee?: string;
}

interface DealCardProps {
  deal: Deal;
  onClick?: () => void;
}

export default function DealCard({ deal, onClick }: DealCardProps) {
  const formatPrice = (price: number) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(price);
  };

  return (
    <div
      onClick={onClick}
      className="bg-white rounded-lg border border-border p-4 hover:shadow-lg hover:border-primary-seafoam/30 transition-all cursor-pointer group"
    >
      {/* Header with name and badges */}
      <div className="flex items-start justify-between gap-3 mb-3">
        <div className="flex-1 min-w-0">
          <h3 className="text-lg font-heading font-semibold text-primary truncate group-hover:text-primary-seafoam transition-colors">
            {deal.name}
          </h3>
          <div className="flex items-center gap-1 text-sm text-muted mt-1">
            <MapPin size={14} />
            <span className="truncate">
              {deal.city}, {deal.state}
            </span>
          </div>
        </div>
        <ScoreBadge score={deal.score} size="sm" />
      </div>

      {/* Address */}
      <p className="text-sm text-muted mb-3">{deal.address}</p>

      {/* Key metrics */}
      <div className="grid grid-cols-2 gap-3 mb-3">
        <div>
          <p className="text-xs text-muted">Units</p>
          <p className="text-sm font-semibold">{deal.units}</p>
        </div>
        <div>
          <p className="text-xs text-muted">Asking Price</p>
          <p className="text-sm font-semibold">{formatPrice(deal.askingPrice)}</p>
        </div>
      </div>

      {/* Footer with recommendation and metadata */}
      <div className="flex items-center justify-between pt-3 border-t border-border">
        <RecommendationBadge recommendation={deal.recommendation} size="sm" />

        <div className="flex items-center gap-3 text-xs text-muted">
          {deal.assignee && (
            <div className="flex items-center gap-1">
              <User size={12} />
              <span>{deal.assignee}</span>
            </div>
          )}
          <div className="flex items-center gap-1">
            <Calendar size={12} />
            <span>{deal.daysInStage}d</span>
          </div>
        </div>
      </div>
    </div>
  );
}
