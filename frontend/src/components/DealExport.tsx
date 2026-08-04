import { useRef, useState } from 'react';
import {
  FileSpreadsheet,
  Upload,
  AlertTriangle,
  CheckCircle2,
  XCircle,
  ShieldAlert,
} from 'lucide-react';
import { exportDealToExcel, ApiError, type ExportWriteReport } from '../lib/api';
import { downloadBlob } from '../lib/download';
import { Card, Button, Badge, Spinner } from './ui';

// ---------------------------------------------------------------------------
// DealExport — the "Export" tab on /deal/:id (Wave D: App -> Excel push).
// The Mini Model template is a USER-SUPPLIED .xlsx upload (they live in the
// user's Drive, not the repo), so this is an upload-then-export flow:
//   1. pick the Mini Model .xlsx
//   2. POST /api/deals/{id}/export (multipart: template + download flag)
//   3. clean populate + download flag -> the draft .xlsx streams back
//      (marked PENDING EXCEL RECALC); otherwise the WriteReport JSON returns
//      and every BL-gate refusal is rendered legibly (BL-06: non-collapsible).
// ---------------------------------------------------------------------------

type Outcome =
  | { kind: 'file'; filename: string }
  | { kind: 'report'; report: ExportWriteReport };

function RefusalGroup({
  title,
  note,
  items,
}: {
  title: string;
  note?: string;
  items: string[];
}) {
  if (items.length === 0) return null;
  return (
    <div className="pt-3">
      <p className="text-sm font-medium text-slate flex items-center gap-2">
        <XCircle className="w-4 h-4 text-warn shrink-0" /> {title}
        <span className="text-xs text-slate/40 font-normal">({items.length})</span>
      </p>
      {note && <p className="text-xs text-slate/50 mt-0.5 ml-6">{note}</p>}
      <div className="ml-6 mt-1.5 flex flex-wrap gap-1.5">
        {items.map((it, i) => (
          <span key={i} className="font-mono text-xs bg-slate/5 border border-slate/15 rounded px-1.5 py-0.5">
            {it}
          </span>
        ))}
      </div>
    </div>
  );
}

function WriteReportView({ report }: { report: ExportWriteReport }) {
  const { refusals } = report;
  return (
    <Card className="p-5 space-y-1 divide-y divide-slate/10">
      <div className="flex items-center gap-3 pb-3">
        {report.ok ? (
          <Badge tone="ok">
            <CheckCircle2 className="w-3 h-3" /> Clean populate
          </Badge>
        ) : (
          <Badge tone="warn">
            <AlertTriangle className="w-3 h-3" /> Populate completed with refusals
          </Badge>
        )}
        <span className="text-sm text-slate/70 tnum">
          {report.written_count} input cell{report.written_count === 1 ? '' : 's'} written
        </span>
      </div>

      {/* BL-02: identity mismatch — populate refused entirely */}
      {report.identity_blocked && (
        <div className="pt-3">
          <div className="flex items-start gap-2 text-sm">
            <ShieldAlert className="w-4 h-4 text-danger mt-0.5 shrink-0" />
            <div>
              <p className="font-medium text-danger">
                Populate refused: deal identity mismatch (BL-02).
              </p>
              <p className="text-slate/70 mt-0.5">
                The uploaded template appears to belong to a different deal than this spec —
                nothing was written. Upload the Mini Model for this deal, or clear the template
                identity, then retry.
              </p>
            </div>
          </div>
        </div>
      )}

      {/* structural diff guard */}
      {!report.structural_diff_ok && (
        <div className="pt-3">
          <div className="flex items-start gap-2 text-sm">
            <ShieldAlert className="w-4 h-4 text-danger mt-0.5 shrink-0" />
            <div className="min-w-0">
              <p className="font-medium text-danger">
                Structural diff failed — the populated draft&rsquo;s structure changed.
              </p>
              <p className="text-slate/70 mt-0.5">
                The draft is not shippable: populating should only change INPUT cell values,
                never workbook structure.
              </p>
              {Object.keys(report.structural_diff_detail ?? {}).length > 0 && (
                <details className="mt-1">
                  <summary className="text-xs text-slate/45 cursor-pointer hover:text-teal select-none">
                    diff detail
                  </summary>
                  <pre className="mt-1 font-mono text-xs bg-slate/5 border border-slate/10 rounded-lg p-3 overflow-x-auto whitespace-pre-wrap">
                    {JSON.stringify(report.structural_diff_detail, null, 2)}
                  </pre>
                </details>
              )}
            </div>
          </div>
        </div>
      )}

      {/* refusal groups — every BL gate rendered, none hidden (BL-06) */}
      {refusals.formula.length > 0 && (
        <div className="pt-3">
          <p className="text-sm font-medium text-slate flex items-center gap-2">
            <CheckCircle2 className="w-4 h-4 text-slate/40 shrink-0" /> Formula cells left intact
            <span className="text-xs text-slate/40 font-normal">({refusals.formula.length})</span>
          </p>
          <p className="text-xs text-slate/50 mt-0.5 ml-6">
            Expected — the populator never overwrites a formula cell.
          </p>
          <details className="ml-6 mt-1">
            <summary className="text-xs text-slate/45 cursor-pointer hover:text-teal select-none">
              show cells
            </summary>
            <ul className="mt-1 space-y-0.5">
              {refusals.formula.map((f, i) => (
                <li key={i} className="font-mono text-xs text-slate/60">
                  {f.cell} <span className="text-slate/35">= {f.existing}</span>
                </li>
              ))}
            </ul>
          </details>
        </div>
      )}
      {refusals.fee_bounds.length > 0 && (
        <div className="pt-3">
          <p className="text-sm font-medium text-slate flex items-center gap-2">
            <XCircle className="w-4 h-4 text-warn shrink-0" /> Fee out of bounds — refused (BL-03)
            <span className="text-xs text-slate/40 font-normal">({refusals.fee_bounds.length})</span>
          </p>
          <ul className="ml-6 mt-1.5 space-y-1">
            {refusals.fee_bounds.map((f, i) => (
              <li key={i} className="text-xs text-slate/70">
                <span className="font-mono bg-slate/5 border border-slate/15 rounded px-1.5 py-0.5 mr-1.5">
                  {f.cell}
                </span>
                {f.reason}
              </li>
            ))}
          </ul>
        </div>
      )}
      <RefusalGroup
        title="Unit-count cells refused (BL-01)"
        note="S-cells were refused because the unit count is blocked."
        items={refusals.unit_count}
      />
      <RefusalGroup
        title="LTV cells refused (BL-15)"
        note="Refused because the LTV gate failed."
        items={refusals.ltv}
      />
      <RefusalGroup
        title="RUBS cells refused (BL-16)"
        note="Refused because the RUBS sign check failed."
        items={refusals.rubs}
      />
      <RefusalGroup
        title="Exit-cap cell refused (BL-10)"
        note="Refused because the exit-cap gate failed."
        items={refusals.exit_cap}
      />

      {report.missing_cells.length > 0 && (
        <RefusalGroup
          title="Cells missing from the template"
          note="Spec cells the template doesn't have — check the Mini Model version."
          items={report.missing_cells}
        />
      )}

      {report.patch_log.length > 0 && (
        <div className="pt-3">
          <details>
            <summary className="text-xs text-slate/45 cursor-pointer hover:text-teal select-none">
              formula-audit log ({report.patch_log.length} entries
              {report.patches_applied.length > 0
                ? `, ${report.patches_applied.length} patch(es) applied`
                : ''}
              )
            </summary>
            <pre className="mt-1 font-mono text-xs bg-slate/5 border border-slate/10 rounded-lg p-3 overflow-x-auto whitespace-pre-wrap">
              {report.patch_log.join('\n')}
            </pre>
          </details>
        </div>
      )}
    </Card>
  );
}

export function DealExport({ dealId }: { dealId: string }) {
  const fileInput = useRef<HTMLInputElement>(null);
  const [file, setFile] = useState<File | null>(null);
  const [wantDownload, setWantDownload] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [outcome, setOutcome] = useState<Outcome | null>(null);

  async function run() {
    if (!file) return;
    setBusy(true);
    setError(null);
    setOutcome(null);
    try {
      const res = await exportDealToExcel(dealId, file, wantDownload);
      if (res.kind === 'file') {
        downloadBlob(res.blob, res.filename);
        setOutcome({ kind: 'file', filename: res.filename });
      } else {
        setOutcome({ kind: 'report', report: res.report });
      }
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) return; // global handler bounced
      setError(e instanceof Error ? e.message : String(e));
    } finally {
      setBusy(false);
    }
  }

  return (
    <div className="space-y-4">
      <h2 className="eyebrow text-slate/60 flex items-center">
        <FileSpreadsheet className="w-4 h-4 mr-2" /> Export to Excel
        <span className="ml-2 normal-case font-normal text-xs text-slate/50">
          — push this deal&rsquo;s inputs into your Mini Model
        </span>
      </h2>

      <Card className="p-5 space-y-4">
        <p className="text-sm text-slate/70">
          Upload your Mini Model <span className="font-mono text-xs">.xlsx</span> template and
          DREAM populates a <em>copy</em> with this deal&rsquo;s input cells — formula cells are
          never touched. A clean populate downloads the draft workbook (marked{' '}
          <span className="font-mono text-xs">PENDING EXCEL RECALC</span>); open it in Excel, let
          it recalc, and save.
        </p>

        <div className="flex flex-wrap items-center gap-3">
          <input
            ref={fileInput}
            type="file"
            accept=".xlsx,application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
            className="hidden"
            onChange={(e) => {
              setFile(e.target.files?.[0] ?? null);
              setOutcome(null);
              setError(null);
            }}
          />
          <Button
            variant="secondary"
            icon={Upload}
            onClick={() => fileInput.current?.click()}
            disabled={busy}
          >
            {file ? 'Change template' : 'Choose Mini Model template'}
          </Button>
          {file && (
            <span className="text-sm text-slate/70 font-mono truncate max-w-[280px]" title={file.name}>
              {file.name}
            </span>
          )}
        </div>

        <label className="flex items-center gap-2 text-sm text-slate/70 select-none">
          <input
            type="checkbox"
            checked={wantDownload}
            onChange={(e) => setWantDownload(e.target.checked)}
            disabled={busy}
            className="accent-[#005253]"
          />
          Download the populated draft (unchecked: return the write report only)
        </label>

        <div className="flex items-center gap-3">
          <Button icon={FileSpreadsheet} onClick={run} disabled={!file || busy}>
            {busy ? 'Populating…' : 'Export to Excel'}
          </Button>
          {busy && <Spinner className="text-lg" />}
        </div>
      </Card>

      {error && (
        <Card className="p-4 border-danger/30 bg-danger/5">
          <div className="flex items-start gap-2 text-sm">
            <AlertTriangle className="w-4 h-4 text-danger mt-0.5 shrink-0" />
            <div>
              <p className="font-medium text-danger">Export failed.</p>
              <p className="text-slate/70 mt-1">{error}</p>
            </div>
          </div>
        </Card>
      )}

      {outcome?.kind === 'file' && (
        <Card className="p-4 border-ok/30 bg-ok/5">
          <div className="flex items-start gap-2 text-sm">
            <CheckCircle2 className="w-4 h-4 text-ok mt-0.5 shrink-0" />
            <div>
              <p className="font-medium text-ok">
                Draft downloaded — <span className="font-mono text-xs">{outcome.filename}</span>
              </p>
              <p className="text-slate/70 mt-1">
                It&rsquo;s marked PENDING EXCEL RECALC. Open it in Excel, let it recalculate, and
                save — then it&rsquo;s ready for CP-2 reconciliation.
              </p>
            </div>
          </div>
        </Card>
      )}

      {outcome?.kind === 'report' && <WriteReportView report={outcome.report} />}
    </div>
  );
}
