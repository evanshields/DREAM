import { Badge, Card } from '../ui';
import type { MonoIdentity, MonoJob, MonoResult } from '../../lib/monoApi';
import { asRecord, Details, Evidence, monoText, monoValue, ProblemList } from './MonoEvidence';

const outputLabels: Record<string, string> = {
  out_noi_y1: 'Year 1 net operating income', out_irr_gross: 'Gross annualized return (IRR)',
  out_em_gross: 'Gross equity multiple', out_cap_going_in: 'Going-in cap rate',
  out_yield_on_cost: 'Yield on cost', out_coc_avg: 'Average cash-on-cash return',
  out_loan_close: 'Loan at closing', out_debt_service_y1: 'Year 1 debt service',
  out_dscr_y1: 'Year 1 debt coverage', out_dscr_min: 'Minimum debt coverage', out_exit_value: 'Exit value',
  out_irr_lp: 'Limited partner annualized return', out_irr_gp: 'Sponsor annualized return',
  out_em_lp: 'Limited partner equity multiple', out_em_gp: 'Sponsor equity multiple',
  out_equity_lp: 'Limited partner equity', out_equity_gp: 'Sponsor equity', out_promote_gp: 'Sponsor promote',
  out_sources_total: 'Total sources', out_uses_total: 'Total uses',
};

function Output({ id, value, metadata }: { id: string; value: unknown; metadata: Record<string, unknown> }) {
  const applicability = asRecord(metadata.applicability);
  const availability = asRecord(metadata.availability);
  const notApplicable = applicability.status === 'not_applicable';
  const totalLoss = !notApplicable && availability.status === 'total_loss';
  return <div data-output-id={id} className="p-4 rounded-lg border border-slate/10 bg-white min-w-0">
    <p className="text-xs font-label uppercase tracking-wide text-slate/60 break-words">{typeof metadata.label === 'string' ? metadata.label : outputLabels[id] ?? id}</p>
    <p className="text-xl tnum text-teal font-semibold mt-2 whitespace-pre-wrap break-words">{notApplicable ? 'Not applicable' : totalLoss ? monoText(availability.display_text) : monoValue(value, metadata.unit)}</p>
    <p className="text-xs mt-1 text-slate/60">Unit: {monoText(metadata.unit)}</p>
    {notApplicable && <div className="mt-2 text-xs text-slate/70 space-y-1"><p>{monoText(applicability.reason)}</p><p>Rule: {monoText(applicability.rule_id)}</p></div>}
    {totalLoss && <p className="text-xs mt-2 text-warn">{monoText(availability.reason)}</p>}
    {value === null && !notApplicable && !totalLoss && <p className="text-xs mt-2 text-warn">No numeric value returned.</p>}
    <details className="mt-3"><summary className="text-xs cursor-pointer text-teal">Output evidence</summary><div className="mt-2"><Evidence value={{...metadata, displayed_value: value}} label={`Metadata for ${id}`} /></div></details>
  </div>;
}

export function MonoIdentityDetails({ identity }: { identity: MonoIdentity }) {
  return <Details title="Revision identity and source hashes"><Evidence value={identity} label="Revision identity" /></Details>;
}

export function MonoResultView({ result, historical = false }: { result: MonoResult; historical?: boolean }) {
  const checks = asRecord(result.checks);
  return <div className="space-y-4">
    <div className="flex flex-wrap gap-2 items-center"><Badge tone={historical ? 'taupe' : 'teal'}>{historical ? 'Historical result' : 'Validated current result'}</Badge><p className="text-xs text-slate/60 break-all">Result {result.result_id}</p></div>
    <div className="grid grid-cols-1 sm:grid-cols-2 xl:grid-cols-3 gap-3">{Object.entries(result.outputs).filter(([id]) => !id.startsWith('out_checks_')).map(([id, value]) => <Output key={id} id={id} value={value} metadata={result.output_metadata[id] ?? {}} />)}</div>
    {!Object.keys(result.outputs).length && <p className="text-sm text-warn">This result contains no outputs.</p>}
    <Details title="Release checks and caution rows" open={checks.release_passed !== true}>
      <p className="text-sm">{checks.release_passed === true ? 'The server verified release checks for this result.' : 'Release checks have not been verified as passing.'}</p>
      <Evidence value={result.checks} label="All native release checks" />
      <Evidence value={Object.fromEntries(Object.entries(result.outputs).filter(([id]) => id.startsWith('out_checks_')))} label="Workbook check outputs" />
    </Details>
    <Details title="Result receipt"><p className="text-xs break-all">Artifact SHA-256: {result.artifact_sha256}</p><Evidence value={result.identity} label="Result identity" /></Details>
  </div>;
}

export function MonoRunHistory({ jobs }: { jobs: MonoJob[] }) {
  return <section className="space-y-3" aria-label="Calculation history"><h2 className="text-2xl">Calculation history</h2><p className="text-sm text-slate/60">Earlier completions remain available here. Only the validated current result supplies the current output panel.</p>
    {jobs.length === 0 && <Card className="p-5 text-sm text-slate/60">No calculation has been recorded.</Card>}
    {jobs.map((job) => <Details key={job.job_id} title={`Revision ${job.revision} · ${job.state} · ${job.job_id}`}>
      <div className="flex flex-wrap gap-2 items-center"><Badge tone={job.is_current ? 'teal' : 'taupe'}>{job.is_current ? 'Matches current revision' : 'Historical revision'}</Badge><span className="text-xs text-slate/60">Created {job.created_at} · Server elapsed {job.elapsed_seconds} seconds</span></div>
      <ProblemList values={job.warnings} /><ProblemList values={job.diagnostics} />
      {job.result ? <MonoResultView result={job.result} historical /> : <p className="text-sm">No completed result.</p>}
      <MonoIdentityDetails identity={job.identity} />
    </Details>)}
  </section>;
}
