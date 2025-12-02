export function SkeletonCard() {
  return (
    <div className="bg-white rounded-xl border border-border p-8 shadow-sm animate-pulse">
      <div className="h-6 bg-background-secondary rounded w-1/3 mb-4"></div>
      <div className="space-y-4">
        <div className="h-4 bg-background-secondary rounded"></div>
        <div className="h-4 bg-background-secondary rounded w-5/6"></div>
        <div className="h-4 bg-background-secondary rounded w-4/6"></div>
      </div>
    </div>
  );
}

export function SkeletonMetric() {
  return (
    <div className="bg-white rounded-lg border border-border p-4 animate-pulse">
      <div className="h-4 bg-background-secondary rounded w-2/3 mb-4"></div>
      <div className="h-8 bg-background-secondary rounded w-1/2"></div>
    </div>
  );
}

export function SkeletonTable() {
  return (
    <div className="bg-white rounded-xl border border-border p-8 animate-pulse">
      <div className="h-6 bg-background-secondary rounded w-1/4 mb-8"></div>
      <div className="space-y-4">
        {[1, 2, 3, 4].map((i) => (
          <div key={i} className="flex gap-4">
            <div className="h-4 bg-background-secondary rounded flex-1"></div>
            <div className="h-4 bg-background-secondary rounded w-24"></div>
            <div className="h-4 bg-background-secondary rounded w-24"></div>
          </div>
        ))}
      </div>
    </div>
  );
}

export function SkeletonAnalysis() {
  return (
    <div className="min-h-screen bg-background-secondary p-8">
      <div className="max-w-7xl mx-auto space-y-8">
        {/* Header skeleton */}
        <div className="space-y-4">
          <div className="h-10 bg-white rounded w-1/3 animate-pulse"></div>
          <div className="h-4 bg-white rounded w-1/4 animate-pulse"></div>
        </div>

        {/* Metrics skeleton */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          {[1, 2, 3, 4, 5, 6].map((i) => (
            <SkeletonMetric key={i} />
          ))}
        </div>

        {/* Content skeleton */}
        <SkeletonTable />
      </div>
    </div>
  );
}

export function FileUploadSpinner() {
  return (
    <div className="inline-flex items-center gap-2">
      <div className="w-4 h-4 border-2 border-primary-seafoam border-t-transparent rounded-full animate-spin"></div>
      <span className="text-sm text-muted">Uploading...</span>
    </div>
  );
}

export function AnalyzingSpinner() {
  return (
    <div className="flex flex-col items-center justify-center p-12">
      <div className="w-16 h-16 border-4 border-primary-seafoam border-t-transparent rounded-full animate-spin mb-4"></div>
      <p className="text-lg font-heading font-semibold text-primary mb-2">Analyzing Deal</p>
      <p className="text-sm text-muted">This usually takes 2-3 minutes...</p>
    </div>
  );
}
