import React, { useState } from 'react';
import { MOCK_ANALYSIS_DEAL } from '../constants';
import { Button, Badge, Card } from '../components/UIComponents';
import { 
  Download, Share2, PlusCircle, ChevronDown, ChevronUp, MapPin, 
  Building2, Calendar, TrendingUp, AlertTriangle, CheckCircle2, 
  ShieldAlert, ArrowRight
} from 'lucide-react';
// recharts import removed - not currently used

const AnalysisView: React.FC = () => {
  const deal = MOCK_ANALYSIS_DEAL;
  const [expandedSection, setExpandedSection] = useState<string | null>('financial');

  const toggleSection = (id: string) => {
    setExpandedSection(expandedSection === id ? null : id);
  };

  const MetricCard = ({ label, value, subtext, subtextColor = 'text-brand-success' }: { label: string, value: string, subtext: string, subtextColor?: string }) => (
    // Updated border-t to use fixed Deep Teal instead of semantic primary-dark which fades in dark mode
    <Card className="p-5 flex flex-col justify-between h-full border-t-4 border-t-[#005253] hover:border-t-accent transition-all">
      <span className="text-xs font-medium text-secondary-muted uppercase tracking-wider">{label}</span>
      <div className="mt-2">
        <span className="text-3xl font-bold text-secondary font-heading">{value}</span>
      </div>
      <div className={`mt-2 text-xs font-medium flex items-center ${subtextColor}`}>
        {subtext.includes('above') || subtext.includes('below') ? <TrendingUp className="w-3 h-3 mr-1" /> : null}
        {subtext}
      </div>
    </Card>
  );

  const AccordionItem: React.FC<{ id: string, title: string, icon: any, children: React.ReactNode }> = ({ id, title, icon: Icon, children }) => {
    const isOpen = expandedSection === id;
    return (
      <div className="border border-border rounded-lg bg-background-primary mb-4 overflow-hidden shadow-sm">
        <button 
          className={`w-full px-6 py-4 flex items-center justify-between bg-background-primary hover:bg-background-tertiary transition-colors ${isOpen ? 'border-b border-border' : ''}`}
          onClick={() => toggleSection(id)}
        >
          <div className="flex items-center space-x-3">
            <div className={`p-2 rounded-md ${isOpen ? 'bg-[#005253] text-white' : 'bg-background-tertiary text-secondary'}`}>
              <Icon className="w-5 h-5" />
            </div>
            <h3 className="text-lg font-heading font-semibold text-secondary">{title}</h3>
          </div>
          {isOpen ? <ChevronUp className="w-5 h-5 text-secondary-muted" /> : <ChevronDown className="w-5 h-5 text-secondary-muted" />}
        </button>
        {isOpen && (
          <div className="p-6 bg-background-primary animate-in fade-in slide-in-from-top-2 duration-200">
            {children}
          </div>
        )}
      </div>
    );
  };

  return (
    <div className="space-y-8 animate-in fade-in duration-500">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <div className="flex items-center gap-3 mb-2">
            <h1 className="text-3xl font-heading font-bold text-primary">{deal.name}</h1>
            <Badge variant="success">Analysis Complete</Badge>
          </div>
          <div className="flex items-center text-secondary-muted text-sm space-x-4">
            <span className="flex items-center"><MapPin className="w-4 h-4 mr-1" /> {deal.address}</span>
            <span className="flex items-center"><Calendar className="w-4 h-4 mr-1" /> Generated Oct 24, 2023</span>
          </div>
        </div>
        <div className="flex space-x-3">
          <Button variant="secondary" icon={Share2} size="sm">Share</Button>
          <Button variant="secondary" icon={Download} size="sm">Export PDF</Button>
          <Button variant="primary" icon={PlusCircle} size="sm">Add to Pipeline</Button>
        </div>
      </div>

      {/* Executive Summary */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        <Card className="lg:col-span-3 p-0 overflow-hidden flex flex-col md:flex-row">
          {/* Enhanced gradient with more prominence on fixed Deep Teal */}
          <div className="p-8 md:w-1/3 bg-gradient-to-br from-[#005253] to-primary flex flex-col items-center justify-center text-white text-center">
            <span className="text-sm font-medium opacity-80 uppercase tracking-widest mb-4">Recommendation</span>
            <div className="bg-white/10 px-6 py-2 rounded-full backdrop-blur-sm border border-white/20 mb-6 shadow-sm">
              <span className="text-2xl font-bold font-heading text-brand-success tracking-wide">STRONG BUY</span>
            </div>
            <div className="flex items-center gap-6">
               <div className="text-center">
                 <div className="text-4xl font-bold font-heading">87</div>
                 <div className="text-xs opacity-70 mt-1">Score</div>
               </div>
               <div className="h-10 w-px bg-white/20"></div>
               <div className="text-center">
                 <div className="text-4xl font-bold font-heading">High</div>
                 <div className="text-xs opacity-70 mt-1">Confidence</div>
               </div>
            </div>
          </div>
          <div className="p-8 md:w-2/3 flex flex-col justify-center">
             <h3 className="text-lg font-heading font-bold text-secondary mb-3">AI Executive Summary</h3>
             <p className="text-secondary leading-relaxed mb-6">
               {deal.summary}. This asset presents a compelling opportunity to acquire a well-maintained vintage property in a Tier 2 submarket. 
               The asking price is <b>8% below replacement cost</b>. Initial underwriting suggests <b>conservative rent bumps of $150/unit</b> are achievable with a light renovation scope.
             </p>
             <div className="flex gap-4">
               <div className="flex items-center text-sm font-medium text-brand-success">
                 <CheckCircle2 className="w-4 h-4 mr-1" /> Strong Rent Growth
               </div>
               <div className="flex items-center text-sm font-medium text-brand-success">
                 <CheckCircle2 className="w-4 h-4 mr-1" /> Operational Upside
               </div>
               <div className="flex items-center text-sm font-medium text-brand-warning">
                 <AlertTriangle className="w-4 h-4 mr-1" /> Insurance Volatility
               </div>
             </div>
          </div>
        </Card>
      </div>

      {/* Key Metrics Grid */}
      <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-6 gap-4">
        <MetricCard label="IRR" value={deal.metrics.irr} subtext="↑ Target 15%" />
        <MetricCard label="Equity Multiple" value={deal.metrics.em} subtext="↑ Target 1.8x" />
        <MetricCard label="Cash on Cash" value={deal.metrics.coc} subtext="↑ Target 7%" />
        <MetricCard label="DSCR" value={deal.metrics.dscr} subtext="Safe > 1.25x" />
        <MetricCard label="Cap Rate" value={deal.metrics.capRate} subtext="Market 5.5%" subtextColor="text-secondary-muted" />
        <MetricCard label="Price / Unit" value={deal.metrics.pricePerUnit} subtext="Below Market" />
      </div>

      {/* Main Content Layout */}
      <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
        
        {/* Left Column: Accordions */}
        <div className="lg:col-span-3 space-y-4">
          
          <AccordionItem id="overview" title="Property Overview" icon={Building2}>
             <div className="grid grid-cols-2 gap-x-8 gap-y-4 mb-6">
                <div>
                  <h4 className="text-xs font-semibold text-secondary-muted uppercase mb-1">Unit Mix</h4>
                  <table className="w-full text-sm text-left">
                    <thead>
                      <tr className="border-b border-border text-xs text-secondary-muted">
                        <th className="py-2 font-medium">Type</th>
                        <th className="py-2 font-medium">Count</th>
                        <th className="py-2 font-medium">Sq Ft</th>
                        <th className="py-2 font-medium">Rent</th>
                      </tr>
                    </thead>
                    <tbody>
                      <tr className="border-b border-border">
                        <td className="py-2 text-secondary">1 Bed / 1 Bath</td>
                        <td className="py-2 text-secondary">96</td>
                        <td className="py-2 text-secondary">750</td>
                        <td className="py-2 text-secondary">$1,250</td>
                      </tr>
                      <tr className="border-b border-border">
                        <td className="py-2 text-secondary">2 Bed / 2 Bath</td>
                        <td className="py-2 text-secondary">112</td>
                        <td className="py-2 text-secondary">1,050</td>
                        <td className="py-2 text-secondary">$1,550</td>
                      </tr>
                      <tr>
                        <td className="py-2 text-secondary">3 Bed / 2 Bath</td>
                        <td className="py-2 text-secondary">40</td>
                        <td className="py-2 text-secondary">1,300</td>
                        <td className="py-2 text-secondary">$1,850</td>
                      </tr>
                    </tbody>
                  </table>
                </div>
                <div>
                   <h4 className="text-xs font-semibold text-secondary-muted uppercase mb-2">Key Characteristics</h4>
                   <ul className="space-y-2 text-sm text-secondary">
                     <li className="flex justify-between border-b border-border pb-1">
                       <span>Year Built</span> <span className="font-medium">1998</span>
                     </li>
                     <li className="flex justify-between border-b border-border pb-1">
                       <span>Construction</span> <span className="font-medium">Garden Style, Wood Frame</span>
                     </li>
                     <li className="flex justify-between border-b border-border pb-1">
                       <span>Roof Age</span> <span className="font-medium">5 Years (2018)</span>
                     </li>
                     <li className="flex justify-between border-b border-border pb-1">
                       <span>Heating/Cooling</span> <span className="font-medium">Individual HVAC</span>
                     </li>
                     <li className="flex justify-between pt-1">
                       <span>Parking</span> <span className="font-medium">1.8 Ratio (Surface)</span>
                     </li>
                   </ul>
                </div>
             </div>
          </AccordionItem>

          <AccordionItem id="financial" title="Financial Analysis" icon={TrendingUp}>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
              <div>
                <h4 className="text-sm font-semibold text-secondary mb-3">Sources & Uses</h4>
                <div className="space-y-1">
                  <div className="flex justify-between text-sm py-1 border-b border-border">
                    <span className="text-secondary-muted">Purchase Price</span>
                    <span className="font-medium text-secondary">$35,340,000</span>
                  </div>
                  <div className="flex justify-between text-sm py-1 border-b border-border">
                    <span className="text-secondary-muted">CapEx / Reno</span>
                    <span className="font-medium text-secondary">$2,150,000</span>
                  </div>
                  <div className="flex justify-between text-sm py-1 border-b border-border">
                    <span className="text-secondary-muted">Closing Costs</span>
                    <span className="font-medium text-secondary">$850,000</span>
                  </div>
                  <div className="flex justify-between text-sm py-1 bg-background-tertiary px-2 rounded font-semibold mt-2">
                    <span className="text-secondary">Total Project Cost</span>
                    <span className="text-secondary">$38,340,000</span>
                  </div>
                </div>

                <div className="mt-6">
                  <h4 className="text-sm font-semibold text-secondary mb-3">Debt Assumptions</h4>
                   <div className="flex gap-2">
                     <Badge variant="outline">LTV: 65%</Badge>
                     <Badge variant="outline">Rate: 5.75%</Badge>
                     <Badge variant="outline">Amort: 30yr</Badge>
                     <Badge variant="outline">I/O: 24mo</Badge>
                   </div>
                </div>
              </div>

              <div>
                <h4 className="text-sm font-semibold text-secondary mb-3">Price Sensitivity (IRR)</h4>
                <table className="w-full text-sm text-center">
                  <thead>
                     <tr className="text-xs text-secondary-muted bg-background-tertiary">
                       <th className="py-2 rounded-l">Purchase Price</th>
                       <th className="py-2">$/Unit</th>
                       <th className="py-2">IRR</th>
                       <th className="py-2 rounded-r">Rec</th>
                     </tr>
                  </thead>
                  <tbody className="divide-y divide-border">
                    <tr className="hover:bg-background-tertiary transition-colors">
                      <td className="py-2 text-secondary">$37.0M (+5%)</td>
                      <td className="py-2 text-secondary-muted">$149k</td>
                      <td className="py-2 text-secondary font-medium">16.1%</td>
                      <td className="py-2"><span className="text-brand-success font-medium text-xs">BUY</span></td>
                    </tr>
                    {/* Highlighted Row - Use semantic primary-dark text as it contrasts well in both modes (dark teal on light, light gray on dark) */}
                    <tr className="bg-primary-dark/5 dark:bg-primary-dark/20 font-semibold">
                      <td className="py-2 text-primary-dark border-l-2 border-primary-dark">$35.3M (Ask)</td>
                      <td className="py-2 text-primary-dark">$142k</td>
                      <td className="py-2 text-primary-dark">18.5%</td>
                      <td className="py-2"><span className="text-brand-success font-bold text-xs">STRONG</span></td>
                    </tr>
                    <tr className="hover:bg-background-tertiary transition-colors">
                      <td className="py-2 text-secondary">$33.5M (-5%)</td>
                      <td className="py-2 text-secondary-muted">$135k</td>
                      <td className="py-2 text-secondary font-medium">21.2%</td>
                      <td className="py-2"><span className="text-brand-success font-bold text-xs">UNICORN</span></td>
                    </tr>
                  </tbody>
                </table>
              </div>
            </div>
          </AccordionItem>

          <AccordionItem id="risk" title="Risk Assessment" icon={ShieldAlert}>
            <div className="flex gap-6 mb-4">
              <div className="w-1/4 bg-brand-bg-danger p-4 rounded-lg border border-brand-danger/20">
                <div className="text-xs font-semibold text-brand-danger uppercase mb-1">Overall Risk Score</div>
                <div className="text-2xl font-bold text-brand-danger font-heading">Low-Med</div>
                <p className="text-xs text-brand-danger/80 mt-2">Standard execution risk with some market volatility exposure.</p>
              </div>
              <div className="w-3/4 space-y-3">
                <div className="flex items-start">
                   <Badge variant="danger" className="mt-0.5 mr-3 shrink-0">HIGH</Badge>
                   <div>
                     <p className="text-sm font-semibold text-secondary">Insurance Premiums</p>
                     <p className="text-sm text-secondary-muted">Florida market seeing 25-40% annual increases. Underwriting assumes 35% growth in Y1.</p>
                   </div>
                </div>
                <div className="flex items-start">
                   <Badge variant="warning" className="mt-0.5 mr-3 shrink-0">MED</Badge>
                   <div>
                     <p className="text-sm font-semibold text-secondary">Real Estate Tax Reassessment</p>
                     <p className="text-sm text-secondary-muted">Sale will trigger reassessment. Modeled at 85% of purchase price @ 18 mills.</p>
                   </div>
                </div>
                 <div className="flex items-start">
                   <Badge variant="info" className="mt-0.5 mr-3 shrink-0">LOW</Badge>
                   <div>
                     <p className="text-sm font-semibold text-secondary">Delinquency</p>
                     <p className="text-sm text-secondary-muted">Current delinquency is 1.5%, well below market average of 3%.</p>
                   </div>
                </div>
              </div>
            </div>
          </AccordionItem>

        </div>

        {/* Right Sidebar: Sticky */}
        <div className="lg:col-span-1">
          <div className="sticky top-24 space-y-6">
            
            {/* Nav */}
            <div className="bg-background-primary rounded-lg border border-border shadow-sm p-4">
              <h4 className="text-xs font-bold text-secondary-muted uppercase tracking-wider mb-3">Quick Navigation</h4>
              <nav className="space-y-1">
                <button onClick={() => setExpandedSection('overview')} className="w-full text-left px-2 py-1.5 text-sm text-secondary hover:bg-background-tertiary rounded transition-colors">Property Overview</button>
                {/* Updated Active State to use fixed Deep Teal text and subtle background */}
                <button onClick={() => setExpandedSection('financial')} className="w-full text-left px-2 py-1.5 text-sm text-[#005253] dark:text-accent font-medium bg-[#005253]/10 rounded transition-colors border-l-2 border-[#005253] dark:border-accent pl-1.5">Financial Analysis</button>
                <button onClick={() => setExpandedSection('market')} className="w-full text-left px-2 py-1.5 text-sm text-secondary hover:bg-background-tertiary rounded transition-colors">Market Research</button>
                <button onClick={() => setExpandedSection('risk')} className="w-full text-left px-2 py-1.5 text-sm text-secondary hover:bg-background-tertiary rounded transition-colors">Risk Assessment</button>
              </nav>
            </div>

            {/* Metadata */}
            <div className="bg-background-tertiary rounded-lg p-4 border border-border">
              <h4 className="text-xs font-bold text-secondary-muted uppercase tracking-wider mb-3">Deal Info</h4>
              <ul className="space-y-3">
                 <li className="text-sm">
                   <span className="block text-secondary-muted text-xs">Source</span>
                   <span className="text-secondary font-medium">Broker OM (Marcus & Millichap)</span>
                 </li>
                 <li className="text-sm">
                   <span className="block text-secondary-muted text-xs">Analyzed By</span>
                   <div className="flex items-center mt-1">
                     <div className="h-5 w-5 rounded-full bg-[#005253] text-white text-[10px] flex items-center justify-center mr-2">JD</div>
                     <span className="text-secondary font-medium">John Doe</span>
                   </div>
                 </li>
                 <li className="text-sm">
                   <span className="block text-secondary-muted text-xs">Last Updated</span>
                   <span className="text-secondary font-medium">2 hours ago</span>
                 </li>
              </ul>
            </div>

            <Button variant="outline" className="w-full" icon={ArrowRight}>View Full Model</Button>
          </div>
        </div>

      </div>
    </div>
  );
};

export default AnalysisView;