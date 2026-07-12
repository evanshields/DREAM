import { useState } from 'react';
import { FileText, RefreshCw, Download, AlertTriangle, Sparkles } from 'lucide-react';
import { generateMemo, ApiError, type DealMemoBlock } from '../lib/api';
import { downloadText } from '../lib/download';
import { Card, Button, Badge, Spinner } from './ui';
import { Markdown } from './Markdown';
import { fmtDateTime } from '../lib/format';

// ---------------------------------------------------------------------------
// DealMemo — the "Memo" tab on /deal/:id.
// The memo is LLM-written PROSE over the deal's deterministic engine outputs;
// it persists at spec.narrative.memo, so `memo` (from GET /api/deals/{id})
// seeds the view on load. POST /memo (re)generates — 10-30s live LLM call.
// 409 = the deal hasn't been computed yet (memo needs CP-1 engine outputs).
// ---------------------------------------------------------------------------

interface DealMemoProps {
  dealId: string;
  dealName: string;
  memo: DealMemoBlock | null; // spec.narrative.memo off the loaded deal (or CP-1 job spec)
}

export function DealMemo({ dealId, dealName, memo: specMemo }: DealMemoProps) {
  // Freshly generated memo wins over the one loaded off the spec.
  const [generated, setGenerated] = useState<DealMemoBlock | null>(null);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<{ headline: string; detail: string } | null>(null);

  const memo = generated ?? specMemo;

  async function run() {
    setBusy(true);
    setError(null);
    try {
      const res = await generateMemo(dealId);
      setGenerated({ markdown: res.memo_markdown, generated_at: res.generated_at });
    } catch (e) {
      if (e instanceof ApiError) {
        if (e.status === 401) return; // global handler already bounced to /login
        if (e.status === 409) {
          setError({
            headline: 'This deal has to reach CP-1 first.',
            detail:
              'The memo is written over the deal’s computed engine outputs (headline metrics + QA gates), ' +
              'so it can’t be generated for a draft. Run the underwrite to CP-1, then come back. ' +
              `Server said: ${e.message}`,
          });
        } else {
          setError({ headline: 'Memo generation failed.', detail: e.message });
        }
      } else {
        setError({
          headline: 'Memo generation failed.',
          detail: e instanceof Error ? e.message : String(e),
        });
      }
    } finally {
      setBusy(false);
    }
  }

  function downloadMd() {
    if (!memo) return;
    const slug = dealName.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-|-$/g, '') || dealId;
    downloadText(memo.markdown, `${slug}-memo.md`);
  }

  return (
    <div className="space-y-4">
      <div className="flex flex-wrap items-center justify-between gap-3">
        <h2 className="eyebrow text-slate/60 flex items-center">
          <FileText className="w-4 h-4 mr-2" /> Deal Memo
          {memo && (
            <span className="ml-2 normal-case font-normal text-xs text-slate/50">
              — generated {fmtDateTime(memo.generated_at)}
            </span>
          )}
        </h2>
        {memo && (
          <div className="flex items-center gap-2">
            <Button variant="secondary" icon={Download} onClick={downloadMd} disabled={busy}>
              Download .md
            </Button>
            <Button variant="secondary" icon={RefreshCw} onClick={run} disabled={busy}>
              {busy ? 'Regenerating…' : 'Regenerate'}
            </Button>
          </div>
        )}
      </div>

      {busy && (
        <Card className="p-5 bg-teal-panel/40 border-teal/15">
          <div className="flex items-center gap-3 text-sm text-slate/70">
            <Spinner className="text-lg shrink-0" />
            <span>
              Writing the memo — the LLM drafts prose over the deal&rsquo;s computed engine
              outputs. This usually takes 10&ndash;30 seconds.
            </span>
          </div>
        </Card>
      )}

      {error && (
        <Card className="p-4 border-danger/30 bg-danger/5">
          <div className="flex items-start gap-2 text-sm">
            <AlertTriangle className="w-4 h-4 text-danger mt-0.5 shrink-0" />
            <div>
              <p className="font-medium text-danger">{error.headline}</p>
              <p className="text-slate/70 mt-1">{error.detail}</p>
            </div>
          </div>
        </Card>
      )}

      {memo ? (
        <Card className="p-6">
          <div className="flex items-center gap-2 mb-3">
            <Badge tone="warn">Generated draft</Badge>
            <span className="text-xs text-slate/40">
              AI-written from deterministic engine outputs — review before distribution.
            </span>
          </div>
          <Markdown source={memo.markdown} />
        </Card>
      ) : (
        !busy && (
          <Card className="p-8 text-center">
            <Sparkles className="w-6 h-6 text-teal mx-auto mb-3" />
            <p className="text-sm text-slate/70 max-w-md mx-auto">
              No memo on file for this deal yet. Generate the one-page institutional memo —
              LLM-written prose over the deal&rsquo;s computed headline metrics and QA gates
              (the deal must have reached CP-1).
            </p>
            <Button className="mt-4" icon={FileText} onClick={run} disabled={busy}>
              Generate Memo
            </Button>
          </Card>
        )
      )}
    </div>
  );
}
