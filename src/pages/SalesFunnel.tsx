import React, { useState } from 'react';
import { 
  ArrowRight, 
  CheckCircle, 
  Clock, 
  Zap, 
  Shield, 
  TrendingUp, 
  BarChart3,
  FileText,
  Target,
  Users,
  Building2,
  ChevronDown,
  ChevronUp,
  Play,
  Star,
  Quote,
  Sparkles,
  Brain,
  LineChart,
  Upload
} from 'lucide-react';

interface SalesFunnelProps {
  onGetStarted: () => void;
}

const SalesFunnel: React.FC<SalesFunnelProps> = ({ onGetStarted }) => {
  const [openFaq, setOpenFaq] = useState<number | null>(null);
  const [selectedPlan, setSelectedPlan] = useState<'monthly' | 'annual'>('annual');

  return (
    <div className="min-h-screen bg-white">
      {/* Navigation */}
      <nav className="fixed top-0 left-0 right-0 z-50 bg-white/90 backdrop-blur-md border-b border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <div className="h-9 w-9 bg-[#005253] rounded-lg flex items-center justify-center mr-3 shadow-sm">
                <span className="text-white font-serif font-bold text-xl">D</span>
              </div>
              <span className="font-serif font-bold text-2xl text-[#28323E] tracking-tight">DreamVision</span>
            </div>
            <div className="hidden md:flex items-center space-x-8">
              <a href="#features" className="text-sm font-medium text-gray-600 hover:text-[#005253] transition-colors">Features</a>
              <a href="#how-it-works" className="text-sm font-medium text-gray-600 hover:text-[#005253] transition-colors">How It Works</a>
              <a href="#pricing" className="text-sm font-medium text-gray-600 hover:text-[#005253] transition-colors">Pricing</a>
              <a href="#testimonials" className="text-sm font-medium text-gray-600 hover:text-[#005253] transition-colors">Testimonials</a>
            </div>
            <div className="flex items-center space-x-4">
              <button className="text-sm font-medium text-[#005253] hover:text-[#003f3f] transition-colors">
                Sign In
              </button>
              <button 
                onClick={onGetStarted}
                className="bg-[#005253] hover:bg-[#003f3f] text-white px-5 py-2.5 rounded-lg text-sm font-semibold transition-all shadow-sm hover:shadow-md"
              >
                Start Free Trial
              </button>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <section className="pt-32 pb-20 bg-gradient-to-b from-[#f8f9fa] to-white overflow-hidden">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid lg:grid-cols-2 gap-12 items-center">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 bg-[#58ABA8]/10 text-[#005253] px-4 py-2 rounded-full text-sm font-medium">
                <Sparkles className="w-4 h-4" />
                AI-Powered Deal Analysis
              </div>
              
              <h1 className="text-5xl lg:text-6xl font-serif font-bold text-[#28323E] leading-tight">
                Close More Deals in
                <span className="text-[#005253]"> Less Time</span>
              </h1>
              
              <p className="text-xl text-gray-600 leading-relaxed max-w-lg">
                Transform your real estate acquisitions workflow. Analyze deals in minutes instead of hours with AI-powered underwriting that institutional investors trust.
              </p>
              
              <div className="flex flex-col sm:flex-row gap-4">
                <button 
                  onClick={onGetStarted}
                  className="inline-flex items-center justify-center bg-[#005253] hover:bg-[#003f3f] text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all shadow-lg hover:shadow-xl group"
                >
                  Start Free Trial
                  <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
                </button>
                <button className="inline-flex items-center justify-center border-2 border-gray-200 hover:border-[#005253] text-[#28323E] px-8 py-4 rounded-xl text-lg font-semibold transition-all group">
                  <Play className="mr-2 w-5 h-5 text-[#005253]" />
                  Watch Demo
                </button>
              </div>
              
              <div className="flex items-center gap-6 pt-4">
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-[#58ABA8]" />
                  <span className="text-sm text-gray-600">14-day free trial</span>
                </div>
                <div className="flex items-center gap-2">
                  <CheckCircle className="w-5 h-5 text-[#58ABA8]" />
                  <span className="text-sm text-gray-600">No credit card required</span>
                </div>
              </div>
            </div>
            
            <div className="relative lg:ml-8">
              {/* Main Dashboard Preview */}
              <div className="bg-white rounded-2xl shadow-2xl border border-gray-100 overflow-hidden">
                <div className="bg-[#005253] px-4 py-3 flex items-center gap-2">
                  <div className="flex gap-1.5">
                    <div className="w-3 h-3 rounded-full bg-red-400"></div>
                    <div className="w-3 h-3 rounded-full bg-yellow-400"></div>
                    <div className="w-3 h-3 rounded-full bg-green-400"></div>
                  </div>
                  <span className="text-white/80 text-sm ml-2">DreamVision Analysis</span>
                </div>
                <div className="p-6 space-y-4">
                  {/* Score Card */}
                  <div className="flex items-center justify-between p-4 bg-gradient-to-r from-[#58ABA8]/10 to-transparent rounded-xl">
                    <div>
                      <p className="text-xs text-gray-500 uppercase tracking-wide font-medium">Investment Score</p>
                      <p className="text-3xl font-bold text-[#28323E] font-serif mt-1">87<span className="text-lg text-gray-400">/100</span></p>
                    </div>
                    <div className="bg-[#58ABA8]/20 text-[#005253] px-3 py-1.5 rounded-full text-sm font-bold">
                      STRONG BUY
                    </div>
                  </div>
                  
                  {/* Metrics Grid */}
                  <div className="grid grid-cols-3 gap-3">
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500">IRR</p>
                      <p className="text-lg font-bold text-[#28323E]">18.5%</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500">Equity Multiple</p>
                      <p className="text-lg font-bold text-[#28323E]">2.1x</p>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-3">
                      <p className="text-xs text-gray-500">Cap Rate</p>
                      <p className="text-lg font-bold text-[#28323E]">5.8%</p>
                    </div>
                  </div>
                  
                  {/* Analysis Bar */}
                  <div className="flex items-center gap-3 text-sm">
                    <div className="flex-1 bg-gray-100 rounded-full h-2">
                      <div className="bg-[#58ABA8] h-2 rounded-full" style={{width: '87%'}}></div>
                    </div>
                    <span className="text-gray-600 font-medium">Analysis complete</span>
                  </div>
                </div>
              </div>
              
              {/* Floating Card - Time Saved */}
              <div className="absolute -left-8 top-1/2 transform -translate-y-1/2 bg-white rounded-xl shadow-lg border border-gray-100 p-4 hidden lg:block">
                <div className="flex items-center gap-3">
                  <div className="bg-[#F3B8A7]/20 p-2 rounded-lg">
                    <Clock className="w-5 h-5 text-[#C94A3E]" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-[#28323E]">4.5 hrs</p>
                    <p className="text-xs text-gray-500">Saved per deal</p>
                  </div>
                </div>
              </div>
              
              {/* Floating Card - Deals Analyzed */}
              <div className="absolute -right-4 bottom-8 bg-white rounded-xl shadow-lg border border-gray-100 p-4 hidden lg:block">
                <div className="flex items-center gap-3">
                  <div className="bg-[#95C9E6]/20 p-2 rounded-lg">
                    <TrendingUp className="w-5 h-5 text-[#005253]" />
                  </div>
                  <div>
                    <p className="text-2xl font-bold text-[#28323E]">12,400+</p>
                    <p className="text-xs text-gray-500">Deals analyzed</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Social Proof - Logos */}
      <section className="py-12 bg-gray-50 border-y border-gray-100">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <p className="text-center text-sm text-gray-500 uppercase tracking-wider font-medium mb-8">
            Trusted by leading real estate investment firms
          </p>
          <div className="flex flex-wrap justify-center items-center gap-x-12 gap-y-6 opacity-60">
            {['Blackstone', 'Starwood', 'Greystar', 'Brookfield', 'CBRE Investment'].map((name) => (
              <div key={name} className="text-xl font-serif font-bold text-gray-400">
                {name}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Problem Statement */}
      <section className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-4xl font-serif font-bold text-[#28323E] mb-6">
              Stop Losing Deals to Slow Analysis
            </h2>
            <p className="text-xl text-gray-600">
              In today's competitive market, speed wins. Traditional underwriting methods are costing you time, money, and opportunities.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                icon: Clock,
                title: '4-8 Hours Per Deal',
                description: 'Manual analysis takes entire days, limiting how many opportunities you can evaluate.',
                color: 'text-[#C94A3E]',
                bgColor: 'bg-[#C94A3E]/10'
              },
              {
                icon: FileText,
                title: 'Inconsistent Methodology',
                description: 'Different analysts, different approaches. Quality varies and errors slip through.',
                color: 'text-[#F3B8A7]',
                bgColor: 'bg-[#F3B8A7]/20'
              },
              {
                icon: Target,
                title: 'Missed Opportunities',
                description: 'While you\'re analyzing one deal, three more pass you by to faster competitors.',
                color: 'text-[#D6C9BA]',
                bgColor: 'bg-[#D6C9BA]/30'
              }
            ].map((item, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-md transition-shadow">
                <div className={`${item.bgColor} w-14 h-14 rounded-xl flex items-center justify-center mb-6`}>
                  <item.icon className={`w-7 h-7 ${item.color}`} />
                </div>
                <h3 className="text-xl font-serif font-bold text-[#28323E] mb-3">{item.title}</h3>
                <p className="text-gray-600">{item.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Solution - Features */}
      <section id="features" className="py-20 bg-gradient-to-b from-[#28323E] to-[#1a2129]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <div className="inline-flex items-center gap-2 bg-white/10 text-[#58ABA8] px-4 py-2 rounded-full text-sm font-medium mb-6">
              <Brain className="w-4 h-4" />
              AI-Powered Solution
            </div>
            <h2 className="text-4xl font-serif font-bold text-white mb-6">
              Everything You Need to Win More Deals
            </h2>
            <p className="text-xl text-gray-400">
              DreamVision combines cutting-edge AI with institutional-grade methodology to supercharge your acquisitions workflow.
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              {
                icon: Zap,
                title: '15-Minute Analysis',
                description: 'Upload any offering memorandum and get a complete BOE analysis in minutes, not hours.'
              },
              {
                icon: BarChart3,
                title: 'Instant Market Intel',
                description: 'AI-powered research delivers demographics, rent trends, and submarket analysis automatically.'
              },
              {
                icon: Shield,
                title: 'Investment Scoring',
                description: 'Configurable scoring framework ensures consistent, defensible investment decisions.'
              },
              {
                icon: LineChart,
                title: 'Pro Forma Modeling',
                description: 'Generate 10-year projections with sensitivity analysis and multiple scenarios.'
              },
              {
                icon: Building2,
                title: 'Pipeline CRM',
                description: 'Track every deal from sourcing to close with our purpose-built pipeline management.'
              },
              {
                icon: Users,
                title: 'Team Collaboration',
                description: 'Share analyses, assign tasks, and keep your entire team aligned on every opportunity.'
              }
            ].map((feature, index) => (
              <div key={index} className="bg-white/5 backdrop-blur-sm rounded-2xl p-6 border border-white/10 hover:bg-white/10 transition-colors group">
                <div className="bg-[#58ABA8]/20 w-12 h-12 rounded-xl flex items-center justify-center mb-4 group-hover:scale-110 transition-transform">
                  <feature.icon className="w-6 h-6 text-[#58ABA8]" />
                </div>
                <h3 className="text-lg font-serif font-bold text-white mb-2">{feature.title}</h3>
                <p className="text-gray-400 text-sm">{feature.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* How It Works */}
      <section id="how-it-works" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-4xl font-serif font-bold text-[#28323E] mb-6">
              From Upload to Decision in 3 Simple Steps
            </h2>
            <p className="text-xl text-gray-600">
              Our streamlined workflow gets you from deal to decision faster than ever before.
            </p>
          </div>
          
          <div className="grid lg:grid-cols-3 gap-8">
            {[
              {
                step: '01',
                title: 'Upload Your Deal',
                description: 'Drag and drop your OM, rent roll, or financials. Our AI extracts all the key data automatically.',
                icon: Upload
              },
              {
                step: '02',
                title: 'AI Analyzes Everything',
                description: 'In minutes, DreamVision evaluates financials, researches the market, and scores the opportunity.',
                icon: Brain
              },
              {
                step: '03',
                title: 'Make Informed Decisions',
                description: 'Get a clear recommendation backed by data. Export professional reports for your IC.',
                icon: Target
              }
            ].map((item, index) => (
              <div key={index} className="relative">
                <div className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm hover:shadow-lg transition-shadow h-full">
                  <div className="text-6xl font-serif font-bold text-[#58ABA8]/20 absolute top-4 right-6">
                    {item.step}
                  </div>
                  <div className="bg-[#005253] w-14 h-14 rounded-xl flex items-center justify-center mb-6">
                    <item.icon className="w-7 h-7 text-white" />
                  </div>
                  <h3 className="text-xl font-serif font-bold text-[#28323E] mb-3">{item.title}</h3>
                  <p className="text-gray-600">{item.description}</p>
                </div>
                {index < 2 && (
                  <div className="hidden lg:block absolute top-1/2 -right-4 transform -translate-y-1/2 z-10">
                    <ArrowRight className="w-8 h-8 text-[#58ABA8]" />
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-[#005253]">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8">
            {[
              { value: '96%', label: 'Faster Analysis' },
              { value: '$2.4B+', label: 'Deal Volume Analyzed' },
              { value: '12,400+', label: 'Deals Processed' },
              { value: '340+', label: 'Active Teams' }
            ].map((stat, index) => (
              <div key={index} className="text-center">
                <p className="text-4xl lg:text-5xl font-serif font-bold text-white mb-2">{stat.value}</p>
                <p className="text-[#58ABA8] font-medium">{stat.label}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section id="testimonials" className="py-20 bg-gray-50">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-16">
            <h2 className="text-4xl font-serif font-bold text-[#28323E] mb-6">
              Loved by Acquisitions Teams
            </h2>
            <p className="text-xl text-gray-600">
              See why industry leaders choose DreamVision for their deal analysis.
            </p>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                quote: "DreamVision cut our underwriting time by 80%. We're now able to evaluate 3x more deals with the same team.",
                name: "Sarah Chen",
                title: "VP of Acquisitions",
                company: "Apex Capital Partners",
                rating: 5
              },
              {
                quote: "The AI-powered market research alone is worth the subscription. It would take our analysts hours to compile what DreamVision delivers in minutes.",
                name: "Marcus Rodriguez",
                title: "Managing Director",
                company: "Coastal Investment Group",
                rating: 5
              },
              {
                quote: "Finally, a tool built by people who understand real estate. The scoring framework matches exactly how we think about deals.",
                name: "Jennifer Walsh",
                title: "Chief Investment Officer",
                company: "Evergreen Properties",
                rating: 5
              }
            ].map((testimonial, index) => (
              <div key={index} className="bg-white rounded-2xl p-8 border border-gray-100 shadow-sm">
                <div className="flex gap-1 mb-4">
                  {[...Array(testimonial.rating)].map((_, i) => (
                    <Star key={i} className="w-5 h-5 text-yellow-400 fill-current" />
                  ))}
                </div>
                <Quote className="w-8 h-8 text-[#58ABA8]/30 mb-4" />
                <p className="text-gray-700 mb-6 leading-relaxed">"{testimonial.quote}"</p>
                <div className="border-t border-gray-100 pt-4">
                  <p className="font-bold text-[#28323E]">{testimonial.name}</p>
                  <p className="text-sm text-gray-500">{testimonial.title}</p>
                  <p className="text-sm text-[#005253] font-medium">{testimonial.company}</p>
                </div>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Pricing */}
      <section id="pricing" className="py-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center max-w-3xl mx-auto mb-12">
            <h2 className="text-4xl font-serif font-bold text-[#28323E] mb-6">
              Simple, Transparent Pricing
            </h2>
            <p className="text-xl text-gray-600 mb-8">
              Choose the plan that fits your deal flow. All plans include a 14-day free trial.
            </p>
            
            {/* Billing Toggle */}
            <div className="inline-flex items-center gap-4 bg-gray-100 p-1 rounded-full">
              <button 
                onClick={() => setSelectedPlan('monthly')}
                className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${selectedPlan === 'monthly' ? 'bg-white shadow text-[#28323E]' : 'text-gray-500'}`}
              >
                Monthly
              </button>
              <button 
                onClick={() => setSelectedPlan('annual')}
                className={`px-6 py-2 rounded-full text-sm font-medium transition-all ${selectedPlan === 'annual' ? 'bg-white shadow text-[#28323E]' : 'text-gray-500'}`}
              >
                Annual <span className="text-[#58ABA8]">(Save 20%)</span>
              </button>
            </div>
          </div>
          
          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: 'Starter',
                price: selectedPlan === 'annual' ? 199 : 249,
                period: '/month',
                description: 'Perfect for emerging sponsors and small teams',
                features: [
                  'Up to 25 deal analyses/month',
                  '2 team members',
                  'BOE memo generation',
                  'Basic market research',
                  'Email support'
                ],
                cta: 'Start Free Trial',
                popular: false
              },
              {
                name: 'Professional',
                price: selectedPlan === 'annual' ? 499 : 625,
                period: '/month',
                description: 'For growing investment firms with active pipelines',
                features: [
                  'Up to 100 deal analyses/month',
                  '10 team members',
                  'Full underwriting package',
                  'Advanced market intelligence',
                  'Custom scoring criteria',
                  'Slack & Drive integrations',
                  'Priority support'
                ],
                cta: 'Start Free Trial',
                popular: true
              },
              {
                name: 'Enterprise',
                price: null,
                period: '',
                description: 'For institutional investors with high-volume needs',
                features: [
                  'Unlimited deal analyses',
                  'Unlimited team members',
                  'Custom AI model training',
                  'API access',
                  'SSO & advanced security',
                  'Dedicated success manager',
                  'Custom integrations'
                ],
                cta: 'Contact Sales',
                popular: false
              }
            ].map((plan, index) => (
              <div 
                key={index} 
                className={`relative bg-white rounded-2xl p-8 border ${plan.popular ? 'border-[#005253] shadow-xl ring-1 ring-[#005253]' : 'border-gray-100 shadow-sm'}`}
              >
                {plan.popular && (
                  <div className="absolute -top-4 left-1/2 transform -translate-x-1/2 bg-[#005253] text-white px-4 py-1 rounded-full text-sm font-medium">
                    Most Popular
                  </div>
                )}
                <div className="text-center mb-6">
                  <h3 className="text-xl font-serif font-bold text-[#28323E] mb-2">{plan.name}</h3>
                  <p className="text-gray-500 text-sm mb-4">{plan.description}</p>
                  <div className="flex items-baseline justify-center">
                    {plan.price ? (
                      <>
                        <span className="text-4xl font-bold text-[#28323E]">${plan.price}</span>
                        <span className="text-gray-500 ml-1">{plan.period}</span>
                      </>
                    ) : (
                      <span className="text-3xl font-bold text-[#28323E]">Custom</span>
                    )}
                  </div>
                </div>
                
                <ul className="space-y-3 mb-8">
                  {plan.features.map((feature, i) => (
                    <li key={i} className="flex items-start gap-3">
                      <CheckCircle className="w-5 h-5 text-[#58ABA8] flex-shrink-0 mt-0.5" />
                      <span className="text-gray-600 text-sm">{feature}</span>
                    </li>
                  ))}
                </ul>
                
                <button 
                  onClick={onGetStarted}
                  className={`w-full py-3 rounded-xl font-semibold transition-all ${
                    plan.popular 
                      ? 'bg-[#005253] text-white hover:bg-[#003f3f]' 
                      : 'bg-gray-100 text-[#28323E] hover:bg-gray-200'
                  }`}
                >
                  {plan.cta}
                </button>
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* FAQ */}
      <section className="py-20 bg-gray-50">
        <div className="max-w-3xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="text-center mb-12">
            <h2 className="text-4xl font-serif font-bold text-[#28323E] mb-6">
              Frequently Asked Questions
            </h2>
          </div>
          
          <div className="space-y-4">
            {[
              {
                question: 'How accurate is the AI analysis?',
                answer: 'DreamVision achieves over 90% accuracy on data extraction and financial calculations. All extracted data is flagged with confidence scores, and users can easily review and override any values. Our AI is trained on thousands of real estate documents and continuously improves.'
              },
              {
                question: 'What document formats do you support?',
                answer: 'We support PDF offering memorandums, Excel financial models and rent rolls, and can import from Google Sheets. Our AI can handle both clean digital PDFs and scanned documents with OCR.'
              },
              {
                question: 'Can I customize the scoring criteria?',
                answer: 'Absolutely. DreamVision lets you configure your own investment criteria with hard stops, soft preferences, and target ranges. You can weight categories according to your investment thesis and save multiple criteria profiles.'
              },
              {
                question: 'What asset classes do you support?',
                answer: 'We currently support conventional multifamily, with student housing, affordable/LIHTC, mobile home parks, and senior housing coming soon. Each asset class has specialized underwriting metrics and scoring frameworks.'
              },
              {
                question: 'How does the free trial work?',
                answer: 'Start with a 14-day free trial with full access to all features. No credit card required upfront. Analyze up to 10 deals during your trial. If you love it, pick a plan that fits your needs.'
              },
              {
                question: 'Is my data secure?',
                answer: 'Yes. We use bank-level encryption for all data in transit and at rest. Your deals and documents are never shared or used to train models for other customers. We offer SSO and advanced security controls for enterprise customers.'
              }
            ].map((faq, index) => (
              <div 
                key={index} 
                className="bg-white rounded-xl border border-gray-100 overflow-hidden"
              >
                <button 
                  onClick={() => setOpenFaq(openFaq === index ? null : index)}
                  className="w-full px-6 py-4 text-left flex items-center justify-between hover:bg-gray-50 transition-colors"
                >
                  <span className="font-medium text-[#28323E]">{faq.question}</span>
                  {openFaq === index ? (
                    <ChevronUp className="w-5 h-5 text-gray-400" />
                  ) : (
                    <ChevronDown className="w-5 h-5 text-gray-400" />
                  )}
                </button>
                {openFaq === index && (
                  <div className="px-6 pb-4">
                    <p className="text-gray-600">{faq.answer}</p>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      </section>

      {/* Final CTA */}
      <section className="py-20 bg-gradient-to-br from-[#005253] to-[#003f3f]">
        <div className="max-w-4xl mx-auto px-4 sm:px-6 lg:px-8 text-center">
          <h2 className="text-4xl lg:text-5xl font-serif font-bold text-white mb-6">
            Ready to Transform Your Acquisitions?
          </h2>
          <p className="text-xl text-[#58ABA8] mb-8 max-w-2xl mx-auto">
            Join hundreds of investment teams already using DreamVision to close more deals, faster.
          </p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <button 
              onClick={onGetStarted}
              className="inline-flex items-center justify-center bg-white text-[#005253] px-8 py-4 rounded-xl text-lg font-semibold transition-all hover:bg-gray-100 group shadow-lg"
            >
              Start Your Free Trial
              <ArrowRight className="ml-2 w-5 h-5 group-hover:translate-x-1 transition-transform" />
            </button>
            <button className="inline-flex items-center justify-center border-2 border-white/30 text-white px-8 py-4 rounded-xl text-lg font-semibold transition-all hover:bg-white/10">
              Schedule a Demo
            </button>
          </div>
          <p className="text-white/60 text-sm mt-6">
            14-day free trial • No credit card required • Cancel anytime
          </p>
        </div>
      </section>

      {/* Footer */}
      <footer className="bg-[#28323E] py-16">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="grid md:grid-cols-4 gap-12">
            <div>
              <div className="flex items-center mb-4">
                <div className="h-8 w-8 bg-white rounded-lg flex items-center justify-center mr-2">
                  <span className="text-[#005253] font-serif font-bold text-lg">D</span>
                </div>
                <span className="font-serif font-bold text-xl text-white">DreamVision</span>
              </div>
              <p className="text-gray-400 text-sm">
                AI-powered acquisitions intelligence for modern real estate investors.
              </p>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Product</h4>
              <ul className="space-y-2">
                <li><a href="#features" className="text-gray-400 hover:text-white text-sm transition-colors">Features</a></li>
                <li><a href="#pricing" className="text-gray-400 hover:text-white text-sm transition-colors">Pricing</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Integrations</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">API</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Resources</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Documentation</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Blog</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Case Studies</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Support</a></li>
              </ul>
            </div>
            
            <div>
              <h4 className="text-white font-semibold mb-4">Company</h4>
              <ul className="space-y-2">
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">About</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Careers</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Privacy</a></li>
                <li><a href="#" className="text-gray-400 hover:text-white text-sm transition-colors">Terms</a></li>
              </ul>
            </div>
          </div>
          
          <div className="border-t border-gray-700 mt-12 pt-8 text-center">
            <p className="text-gray-500 text-sm">
              © 2025 DreamVision, a DREAM.AI company. All rights reserved.
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
};

export default SalesFunnel;
