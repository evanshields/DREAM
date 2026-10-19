import React from 'react';
import { Card, Button } from '../components/UIComponents';
import { Upload, FileText, Activity, Calendar, ArrowUpRight, ArrowRight } from 'lucide-react';
import { PIPELINE_DEALS } from '../constants';

const Dashboard: React.FC<{ onNavigate: (view: any) => void }> = ({ onNavigate }) => {
  const recentDeals = PIPELINE_DEALS.slice(0, 4);

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Welcome Section */}
      <div className="flex justify-between items-end">
        <div>
           <h1 className="text-3xl font-heading font-bold text-primary mb-2">Good morning, John</h1>
           <p className="text-secondary-muted">Here's what's happening in your pipeline today.</p>
        </div>
        <div className="flex gap-3">
          <Button variant="secondary" icon={Activity}>Market Watch</Button>
          <Button variant="primary" icon={Upload} onClick={() => onNavigate('intake')}>Upload New Deal</Button>
        </div>
      </div>

      {/* Stats Row */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <Card className="p-4 border-l-4 border-l-primary">
          <p className="text-xs text-secondary-muted font-medium uppercase">Total Pipeline</p>
          <p className="text-2xl font-bold font-heading text-secondary mt-1">12 Deals</p>
        </Card>
        <Card className="p-4 border-l-4 border-l-accent">
          <p className="text-xs text-secondary-muted font-medium uppercase">Active Analysis</p>
          <p className="text-2xl font-bold font-heading text-secondary mt-1">3 Deals</p>
        </Card>
        <Card className="p-4 border-l-4 border-l-brand-success">
          <p className="text-xs text-secondary-muted font-medium uppercase">Closing This Month</p>
          <p className="text-2xl font-bold font-heading text-secondary mt-1">2 Deals</p>
        </Card>
        <Card className="p-4 border-l-4 border-l-brand-warning">
          <p className="text-xs text-secondary-muted font-medium uppercase">Tasks Due</p>
          <p className="text-2xl font-bold font-heading text-secondary mt-1">5 Items</p>
        </Card>
      </div>

      {/* Main Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
        
        {/* Recent Analysis */}
        <div className="lg:col-span-2 space-y-4">
          <div className="flex justify-between items-center">
            <h2 className="text-xl font-heading font-semibold text-secondary">Recent Analyses</h2>
            <Button variant="ghost" size="sm" className="text-accent" onClick={() => onNavigate('pipeline')}>View All</Button>
          </div>
          <div className="bg-background-primary rounded-lg border border-border shadow-sm overflow-hidden">
             <table className="min-w-full divide-y divide-border">
               <thead className="bg-background-tertiary">
                 <tr>
                   <th className="px-6 py-3 text-left text-xs font-medium text-secondary-muted uppercase tracking-wider">Property</th>
                   <th className="px-6 py-3 text-left text-xs font-medium text-secondary-muted uppercase tracking-wider">Score</th>
                   <th className="px-6 py-3 text-left text-xs font-medium text-secondary-muted uppercase tracking-wider">Rec</th>
                   <th className="px-6 py-3 text-left text-xs font-medium text-secondary-muted uppercase tracking-wider">Date</th>
                   <th className="relative px-6 py-3"><span className="sr-only">View</span></th>
                 </tr>
               </thead>
               <tbody className="bg-background-primary divide-y divide-border">
                 {recentDeals.map((deal) => (
                   <tr key={deal.id} className="hover:bg-background-tertiary transition-colors group cursor-pointer" onClick={() => onNavigate('analysis')}>
                     <td className="px-6 py-4 whitespace-nowrap">
                       <div className="flex items-center">
                         <div className="ml-0">
                           <div className="text-sm font-medium text-secondary group-hover:text-primary">{deal.name}</div>
                           <div className="text-xs text-secondary-muted">{deal.location}</div>
                         </div>
                       </div>
                     </td>
                     <td className="px-6 py-4 whitespace-nowrap">
                       <div className="text-sm text-secondary font-bold">{deal.score}/100</div>
                     </td>
                     <td className="px-6 py-4 whitespace-nowrap">
                       <span className={`px-2 inline-flex text-xs leading-5 font-semibold rounded-full 
                         ${deal.recommendation === 'STRONG BUY' ? 'bg-brand-bg-success text-brand-success' : 
                           deal.recommendation === 'BUY' ? 'bg-brand-bg-success/50 text-brand-success' :
                           deal.recommendation === 'HOLD' ? 'bg-brand-bg-warning text-brand-warning' : 
                           'bg-brand-bg-danger text-brand-danger'}`}>
                         {deal.recommendation}
                       </span>
                     </td>
                     <td className="px-6 py-4 whitespace-nowrap text-sm text-secondary-muted">
                       Oct {24 - parseInt(deal.id)}, 2023
                     </td>
                     <td className="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                       <ArrowRight className="w-4 h-4 text-secondary-muted group-hover:text-accent" />
                     </td>
                   </tr>
                 ))}
               </tbody>
             </table>
          </div>
        </div>

        {/* Side Widgets */}
        <div className="space-y-8">
           {/* Tasks Widget */}
           <div>
              <h2 className="text-xl font-heading font-semibold text-secondary mb-4">Priority Tasks</h2>
              <Card className="p-0 divide-y divide-border">
                {[
                  { text: 'Review LOI for Beacon Hill', due: 'Today', urgent: true },
                  { text: 'Update market rent assumptions', due: 'Tomorrow', urgent: false },
                  { text: 'Schedule tour for Desert Springs', due: 'Fri', urgent: false },
                ].map((task, i) => (
                  <div key={i} className="p-4 flex items-start space-x-3 hover:bg-background-tertiary cursor-pointer transition-colors">
                     <div className="mt-0.5 h-4 w-4 rounded border border-secondary-muted"></div>
                     <div className="flex-1">
                       <p className="text-sm font-medium text-secondary">{task.text}</p>
                       <p className={`text-xs mt-1 ${task.urgent ? 'text-brand-danger font-medium' : 'text-secondary-muted'}`}>Due: {task.due}</p>
                     </div>
                  </div>
                ))}
                <div className="p-3 text-center">
                  <button className="text-xs font-medium text-accent hover:text-accent-light">View All Tasks</button>
                </div>
              </Card>
           </div>
           
           {/* Market Watch */}
           <div>
             <h2 className="text-xl font-heading font-semibold text-secondary mb-4">Market Watch</h2>
             <Card className="p-4">
                <div className="flex items-center justify-between mb-4 pb-4 border-b border-border">
                   <div>
                     <p className="font-medium text-secondary">Tampa, FL</p>
                     <p className="text-xs text-secondary-muted">Multifamily Class B</p>
                   </div>
                   <div className="text-right">
                     <div className="flex items-center text-brand-success text-sm font-bold">
                       <ArrowUpRight className="w-4 h-4 mr-1" /> +2.4%
                     </div>
                     <p className="text-xs text-secondary-muted">Rent Growth (YoY)</p>
                   </div>
                </div>
                <div className="flex items-center justify-between">
                   <div>
                     <p className="font-medium text-secondary">Austin, TX</p>
                     <p className="text-xs text-secondary-muted">Multifamily Class A</p>
                   </div>
                   <div className="text-right">
                     <div className="flex items-center text-brand-danger text-sm font-bold">
                       <ArrowUpRight className="w-4 h-4 mr-1 transform rotate-90" /> -1.1%
                     </div>
                     <p className="text-xs text-secondary-muted">Rent Growth (YoY)</p>
                   </div>
                </div>
             </Card>
           </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;