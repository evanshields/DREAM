import React from 'react';
import { PIPELINE_DEALS, PIPELINE_STAGES } from '../constants';
import { Deal } from '../types';
import { Badge, Button } from '../components/UIComponents';
import { Plus, Filter, Search, MoreHorizontal, Clock } from 'lucide-react';

const PipelineBoard: React.FC = () => {
  const getDealsByStage = (stage: string) => PIPELINE_DEALS.filter(d => d.stage === stage);

  const getStageColor = (stage: string) => {
    switch(stage) {
      case 'New': return 'border-t-gray-400';
      case 'Screening': return 'border-t-brand-info';
      case 'LOI': return 'border-t-brand-warning';
      case 'Due Diligence': return 'border-t-brand-warning';
      case 'Under Contract': return 'border-t-brand-success';
      case 'Closed': return 'border-t-brand-success';
      case 'Passed': return 'border-t-brand-danger opacity-70';
      default: return 'border-t-gray-300';
    }
  };

  const DealCard: React.FC<{ deal: Deal }> = ({ deal }) => (
    <div className="bg-background-primary p-4 rounded-md shadow-sm border border-border hover:shadow-md transition-shadow cursor-pointer mb-3 group">
      <div className="flex justify-between items-start mb-2">
        <h4 className="font-semibold text-secondary text-sm leading-tight group-hover:text-primary transition-colors">{deal.name}</h4>
        <button className="text-secondary-muted hover:text-secondary opacity-0 group-hover:opacity-100">
          <MoreHorizontal className="w-4 h-4" />
        </button>
      </div>
      <p className="text-xs text-secondary-muted mb-3">{deal.location}</p>
      
      <div className="flex items-center gap-2 mb-3">
        <Badge variant={deal.recommendation === 'STRONG BUY' ? 'success' : deal.recommendation === 'PASS' ? 'danger' : 'default'}>
          {deal.score}/100
        </Badge>
        <span className="text-xs font-medium text-secondary">{(deal.price / 1000000).toFixed(1)}M</span>
      </div>

      <div className="flex items-center justify-between mt-2 pt-2 border-t border-border">
        <div className="flex -space-x-2">
           {deal.assignedTo.map((user, i) => (
             <div key={i} className="h-6 w-6 rounded-full bg-primary-light border-2 border-white dark:border-slate-800 flex items-center justify-center text-[9px] text-white font-bold">
               {user}
             </div>
           ))}
        </div>
        <div className="flex items-center text-xs text-secondary-muted">
          <Clock className="w-3 h-3 mr-1" />
          {deal.daysInStage}d
        </div>
      </div>
    </div>
  );

  return (
    <div className="h-[calc(100vh-8rem)] flex flex-col">
      {/* Controls */}
      <div className="flex justify-between items-center mb-6">
        <div className="flex items-center space-x-2">
          <div className="relative">
             <Search className="w-4 h-4 absolute left-3 top-1/2 transform -translate-y-1/2 text-secondary-muted" />
             <input type="text" placeholder="Search pipeline..." className="pl-9 pr-4 py-1.5 text-sm border border-border bg-background-primary text-secondary rounded-md focus:outline-none focus:ring-1 focus:ring-primary placeholder-secondary-muted" />
          </div>
          <Button variant="outline" size="sm" icon={Filter}>Filters</Button>
        </div>
        <Button variant="primary" icon={Plus}>New Deal</Button>
      </div>

      {/* Kanban Board */}
      <div className="flex-1 overflow-x-auto overflow-y-hidden pb-4">
        <div className="flex h-full space-x-4 min-w-max">
          {PIPELINE_STAGES.map((stage) => (
             <div key={stage} className={`w-72 flex flex-col h-full bg-background-tertiary/50 rounded-lg border-t-4 ${getStageColor(stage)}`}>
               {/* Column Header */}
               <div className="p-3 flex justify-between items-center border-b border-border bg-background-tertiary rounded-t-lg">
                 <div className="flex items-center gap-2">
                   <h3 className="font-semibold text-sm text-secondary">{stage}</h3>
                   <span className="bg-border text-secondary-muted py-0.5 px-2 rounded-full text-xs font-medium">
                     {getDealsByStage(stage).length}
                   </span>
                 </div>
                 <button className="text-secondary-muted hover:text-secondary"><Plus className="w-4 h-4" /></button>
               </div>
               
               {/* Column Body */}
               <div className="p-2 flex-1 overflow-y-auto custom-scrollbar">
                  {getDealsByStage(stage).map(deal => (
                    <DealCard key={deal.id} deal={deal} />
                  ))}
               </div>
             </div>
          ))}
        </div>
      </div>
    </div>
  );
};

export default PipelineBoard;