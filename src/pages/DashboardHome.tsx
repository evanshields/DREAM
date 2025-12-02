import { Link } from 'react-router-dom';
import { ArrowRight, Upload, TrendingUp, CheckCircle2 } from 'lucide-react';
import ScoreBadge from '../components/ScoreBadge';
import RecommendationBadge from '../components/RecommendationBadge';

export default function DashboardHome() {
  // Get greeting based on time
  const getGreeting = () => {
    const hour = new Date().getHours();
    if (hour < 12) return 'Good morning';
    if (hour < 18) return 'Good afternoon';
    return 'Good evening';
  };

  const getTodayDate = () => {
    return new Date().toLocaleDateString('en-US', {
      weekday: 'long',
      month: 'long',
      day: 'numeric',
      year: 'numeric'
    });
  };

  // Sample data for recent analyses
  const recentAnalyses = [
    { id: '1', name: 'Sunset Ridge Apartments', score: 87, recommendation: 'STRONG_BUY' as const, time: '2 hours ago' },
    { id: '2', name: 'Oakwood Gardens', score: 74, recommendation: 'BUY' as const, time: '5 hours ago' },
    { id: '3', name: 'Palm Vista', score: 82, recommendation: 'BUY' as const, time: '1 day ago' },
    { id: '4', name: 'Riverside Commons', score: 68, recommendation: 'HOLD' as const, time: '2 days ago' },
  ];

  // Sample tasks
  const tasks = [
    { id: '1', description: 'Complete site visit', dealName: 'Sunset Ridge', dueDate: 'Dec 5', completed: false },
    { id: '2', description: 'Submit LOI', dealName: 'Oakwood Gardens', dueDate: 'Dec 3', completed: false },
    { id: '3', description: 'Review inspection report', dealName: 'Palm Vista', dueDate: 'Dec 8', completed: false },
    { id: '4', description: 'Schedule lender call', dealName: 'Willowbrook Place', dueDate: 'Dec 4', completed: false },
  ];

  // Pipeline stages data
  const pipelineData = [
    { stage: 'New', count: 2, color: 'bg-secondary-gray' },
    { stage: 'Screening', count: 2, color: 'bg-secondary-yinmn' },
    { stage: 'LOI', count: 1, color: 'bg-primary-alt' },
    { stage: 'Due Diligence', count: 1, color: 'bg-warning' },
    { stage: 'Under Contract', count: 1, color: 'bg-primary-seafoam' },
    { stage: 'Closed', count: 0, color: 'bg-primary-teal' },
    { stage: 'Passed', count: 1, color: 'bg-secondary-tan' },
  ];

  const totalDeals = pipelineData.reduce((sum, stage) => sum + stage.count, 0);

  return (
    <div className="min-h-screen bg-background-secondary p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Welcome Header */}
        <div className="bg-white rounded-xl border border-border p-8 shadow-sm">
          <h1 className="text-4xl font-heading font-bold text-primary mb-2">
            {getGreeting()}, Evan
          </h1>
          <p className="text-muted mb-6">{getTodayDate()}</p>

          {/* Quick Stats Row */}
          <div className="flex flex-wrap gap-6 text-sm">
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-primary-seafoam" />
              <span className="font-semibold">{totalDeals} deals in pipeline</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-warning" />
              <span className="font-semibold">2 need review</span>
            </div>
            <div className="flex items-center gap-2">
              <div className="w-2 h-2 rounded-full bg-success" />
              <span className="font-semibold">1 closing this month</span>
            </div>
          </div>
        </div>

        {/* Grid of Cards */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Pipeline Summary Card */}
          <div className="bg-white rounded-xl border border-border p-6 shadow-sm">
            <div className="flex items-center justify-between mb-6">
              <h2 className="text-xl font-heading font-semibold text-primary">
                Pipeline Summary
              </h2>
              <Link
                to="/pipeline"
                className="flex items-center gap-1 text-sm text-primary-seafoam hover:text-primary-teal font-medium"
              >
                View Pipeline
                <ArrowRight size={16} />
              </Link>
            </div>

            <div className="space-y-3">
              {pipelineData.map((stage) => (
                <div key={stage.stage} className="flex items-center gap-3">
                  <div className={`${stage.color} w-20 h-6 rounded flex items-center justify-center text-white text-xs font-medium`}>
                    {stage.count}
                  </div>
                  <span className="text-sm text-muted">{stage.stage}</span>
                </div>
              ))}
            </div>
          </div>

          {/* Recent Analyses Card */}
          <div className="bg-white rounded-xl border border-border p-6 shadow-sm">
            <h2 className="text-xl font-heading font-semibold text-primary mb-6">
              Recent Analyses
            </h2>

            <div className="space-y-4">
              {recentAnalyses.map((analysis) => (
                <Link
                  key={analysis.id}
                  to={`/analysis/${analysis.id}`}
                  className="flex items-center justify-between p-3 rounded-lg hover:bg-background-secondary transition-colors"
                >
                  <div className="flex-1 min-w-0">
                    <p className="font-medium text-primary truncate">{analysis.name}</p>
                    <p className="text-xs text-muted mt-0.5">{analysis.time}</p>
                  </div>
                  <div className="flex items-center gap-3 ml-4">
                    <ScoreBadge score={analysis.score} size="sm" />
                    <RecommendationBadge recommendation={analysis.recommendation} size="sm" />
                  </div>
                </Link>
              ))}
            </div>
          </div>

          {/* Tasks Due Card */}
          <div className="bg-white rounded-xl border border-border p-6 shadow-sm">
            <h2 className="text-xl font-heading font-semibold text-primary mb-6">
              Tasks Due
            </h2>

            <div className="space-y-4">
              {tasks.map((task) => (
                <div key={task.id} className="flex items-start gap-4 p-4 rounded-lg hover:bg-background-secondary transition-colors">
                  <input
                    type="checkbox"
                    checked={task.completed}
                    className="mt-1 w-4 h-4 rounded border-border text-primary-seafoam focus:ring-primary-seafoam cursor-pointer"
                  />
                  <div className="flex-1 min-w-0">
                    <p className="text-sm font-medium text-primary">
                      {task.description} - <span className="text-muted">{task.dealName}</span>
                    </p>
                    <p className="text-xs text-muted mt-0.5">Due {task.dueDate}</p>
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* Quick Actions Card */}
          <div className="bg-white rounded-xl border border-border p-6 shadow-sm">
            <h2 className="text-xl font-heading font-semibold text-primary mb-6">
              Quick Actions
            </h2>

            <div className="space-y-3">
              <Link
                to="/deals/new"
                className="flex items-center gap-4 p-4 border-2 border-dashed border-border rounded-lg hover:border-primary-seafoam hover:bg-background-secondary transition-all group"
              >
                <div className="w-12 h-12 rounded-lg bg-primary-seafoam/10 flex items-center justify-center group-hover:bg-primary-seafoam/20 transition-colors">
                  <Upload size={24} className="text-primary-seafoam" />
                </div>
                <div>
                  <p className="font-semibold text-primary">Upload New Deal</p>
                  <p className="text-sm text-muted">Start AI analysis on a property</p>
                </div>
              </Link>

              <button className="w-full flex items-center gap-4 p-4 border-2 border-dashed border-border rounded-lg hover:border-secondary-yinmn hover:bg-background-secondary transition-all group">
                <div className="w-12 h-12 rounded-lg bg-secondary-yinmn/10 flex items-center justify-center group-hover:bg-secondary-yinmn/20 transition-colors">
                  <TrendingUp size={24} className="text-secondary-yinmn" />
                </div>
                <div>
                  <p className="font-semibold text-primary">Run Market Research</p>
                  <p className="text-sm text-muted">Analyze market trends and comps</p>
                </div>
              </button>
            </div>
          </div>
        </div>

        {/* Market Watchlist Card (Optional) */}
        <div className="bg-white rounded-xl border border-border p-6 shadow-sm">
          <h2 className="text-xl font-heading font-semibold text-primary mb-6">
            Market Watchlist
          </h2>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p className="font-semibold text-primary">Tampa-St. Pete, FL</p>
                <CheckCircle2 size={16} className="text-success" />
              </div>
              <div className="flex items-center gap-3">
                <ScoreBadge score={82} size="sm" />
                <span className="text-xs text-success">↑ +3 pts</span>
              </div>
            </div>

            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p className="font-semibold text-primary">Austin, TX</p>
                <CheckCircle2 size={16} className="text-success" />
              </div>
              <div className="flex items-center gap-3">
                <ScoreBadge score={78} size="sm" />
                <span className="text-xs text-warning">↓ -2 pts</span>
              </div>
            </div>

            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p className="font-semibold text-primary">Charlotte, NC</p>
                <CheckCircle2 size={16} className="text-success" />
              </div>
              <div className="flex items-center gap-3">
                <ScoreBadge score={75} size="sm" />
                <span className="text-xs text-muted">→ No change</span>
              </div>
            </div>

            <div className="p-4 bg-background-secondary rounded-lg">
              <div className="flex items-center justify-between mb-2">
                <p className="font-semibold text-primary">Nashville, TN</p>
                <CheckCircle2 size={16} className="text-success" />
              </div>
              <div className="flex items-center gap-3">
                <ScoreBadge score={73} size="sm" />
                <span className="text-xs text-success">↑ +5 pts</span>
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
