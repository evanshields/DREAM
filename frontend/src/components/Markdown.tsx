import { type ReactNode } from 'react';

// ---------------------------------------------------------------------------
// Markdown — a tiny hand-rolled renderer for the LLM-generated deal memo.
// NO new deps, NO dangerouslySetInnerHTML: source is parsed line-by-line into
// React elements, so markup in the memo can never inject HTML.
//
// Supported (all a memo realistically uses): #–###### headings, **bold**,
// *italic*, `code`, [links](https://…), - / * / 1. lists, > blockquotes,
// ``` fenced code, --- rules, and simple pipe tables. Anything else renders
// as a plain paragraph — a legible preformatted-ish fallback, never an error.
// ---------------------------------------------------------------------------

const INLINE_RE = /(\*\*[^*]+\*\*|\*[^*\s][^*]*\*|`[^`]+`|\[[^\]]+\]\([^)\s]+\))/g;

function renderInline(text: string): ReactNode[] {
  const nodes: ReactNode[] = [];
  let last = 0;
  let k = 0;
  INLINE_RE.lastIndex = 0;
  let m: RegExpExecArray | null;
  while ((m = INLINE_RE.exec(text)) !== null) {
    if (m.index > last) nodes.push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith('**')) {
      nodes.push(
        <strong key={k++} className="font-semibold text-slate-near">
          {tok.slice(2, -2)}
        </strong>,
      );
    } else if (tok.startsWith('`')) {
      nodes.push(
        <code key={k++} className="font-mono text-[0.85em] bg-slate/5 rounded px-1 py-0.5">
          {tok.slice(1, -1)}
        </code>,
      );
    } else if (tok.startsWith('[')) {
      const link = /^\[([^\]]+)\]\(([^)\s]+)\)$/.exec(tok);
      if (link && /^https?:\/\//.test(link[2])) {
        nodes.push(
          <a
            key={k++}
            href={link[2]}
            target="_blank"
            rel="noreferrer"
            className="text-teal underline"
          >
            {link[1]}
          </a>,
        );
      } else {
        nodes.push(link ? link[1] : tok); // non-http target — render the text, drop the link
      }
    } else {
      nodes.push(<em key={k++}>{tok.slice(1, -1)}</em>);
    }
    last = m.index + tok.length;
  }
  if (last < text.length) nodes.push(text.slice(last));
  return nodes;
}

const HEADING_CLASS: Record<number, string> = {
  1: 'font-head font-bold text-2xl text-slate-near mt-6 mb-2',
  2: 'font-head font-bold text-xl text-slate-near mt-5 mb-2',
  3: 'font-head font-semibold text-lg text-slate-near mt-4 mb-1.5',
  4: 'font-label font-semibold text-sm uppercase tracking-wide text-slate/70 mt-4 mb-1',
  5: 'font-label font-semibold text-xs uppercase tracking-wide text-slate/60 mt-3 mb-1',
  6: 'font-label font-semibold text-xs uppercase tracking-wide text-slate/50 mt-3 mb-1',
};

const isHr = (l: string) => /^\s*(-{3,}|\*{3,}|_{3,})\s*$/.test(l);
const isUl = (l: string) => /^\s*[-*+]\s+/.test(l);
const isOl = (l: string) => /^\s*\d+[.)]\s+/.test(l);
const isQuote = (l: string) => /^\s*>/.test(l);
const isTableRow = (l: string) => l.trim().startsWith('|') && l.trim().length > 1;
const isTableSep = (l: string) => /^\s*\|?[\s|:-]+\|?\s*$/.test(l) && l.includes('-');
const isHeading = (l: string) => /^#{1,6}\s+/.test(l);
const isFence = (l: string) => l.trim().startsWith('```');
const isBlockStart = (l: string) =>
  isHeading(l) || isHr(l) || isUl(l) || isOl(l) || isQuote(l) || isTableRow(l) || isFence(l);

function splitRow(row: string): string[] {
  return row.trim().replace(/^\|/, '').replace(/\|$/, '').split('|').map((c) => c.trim());
}

function renderBlocks(source: string): ReactNode[] {
  const lines = source.replace(/\r\n/g, '\n').split('\n');
  const out: ReactNode[] = [];
  let i = 0;
  let key = 0;

  while (i < lines.length) {
    const line = lines[i];

    if (!line.trim()) {
      i++;
      continue;
    }

    // fenced code
    if (isFence(line)) {
      const buf: string[] = [];
      i++;
      while (i < lines.length && !isFence(lines[i])) {
        buf.push(lines[i]);
        i++;
      }
      i++; // closing fence
      out.push(
        <pre
          key={key++}
          className="font-mono text-xs bg-slate/5 border border-slate/10 rounded-lg p-3 overflow-x-auto my-3"
        >
          {buf.join('\n')}
        </pre>,
      );
      continue;
    }

    // heading
    const h = /^(#{1,6})\s+(.*)$/.exec(line);
    if (h) {
      const lvl = h[1].length;
      const cls = HEADING_CLASS[lvl];
      out.push(
        lvl === 1 ? (
          <h3 key={key++} className={cls}>{renderInline(h[2])}</h3>
        ) : lvl === 2 ? (
          <h4 key={key++} className={cls}>{renderInline(h[2])}</h4>
        ) : (
          <h5 key={key++} className={cls}>{renderInline(h[2])}</h5>
        ),
      );
      i++;
      continue;
    }

    // horizontal rule
    if (isHr(line)) {
      out.push(<hr key={key++} className="border-slate/15 my-4" />);
      i++;
      continue;
    }

    // blockquote — strip one '>' level, recurse
    if (isQuote(line)) {
      const buf: string[] = [];
      while (i < lines.length && isQuote(lines[i])) {
        buf.push(lines[i].replace(/^\s*>\s?/, ''));
        i++;
      }
      out.push(
        <blockquote
          key={key++}
          className="border-l-4 border-taupe bg-taupe/10 rounded-r-lg pl-4 pr-3 py-2 my-3 text-sm text-slate/80"
        >
          {renderBlocks(buf.join('\n'))}
        </blockquote>,
      );
      continue;
    }

    // simple pipe table
    if (isTableRow(line)) {
      const rows: string[] = [];
      while (i < lines.length && isTableRow(lines[i])) {
        rows.push(lines[i]);
        i++;
      }
      const hasHeader = rows.length > 1 && isTableSep(rows[1]);
      const header = hasHeader ? splitRow(rows[0]) : null;
      const body = (hasHeader ? rows.slice(2) : rows).map(splitRow);
      out.push(
        <div key={key++} className="overflow-x-auto my-3">
          <table className="text-sm border-collapse min-w-[50%]">
            {header && (
              <thead>
                <tr>
                  {header.map((c, ci) => (
                    <th
                      key={ci}
                      className="text-left font-label font-semibold text-xs uppercase tracking-wide text-slate/60 border-b border-slate/20 px-3 py-1.5"
                    >
                      {renderInline(c)}
                    </th>
                  ))}
                </tr>
              </thead>
            )}
            <tbody>
              {body.map((r, ri) => (
                <tr key={ri} className="border-b border-slate/10 last:border-0">
                  {r.map((c, ci) => (
                    <td key={ci} className="px-3 py-1.5 text-slate/80 tnum">
                      {renderInline(c)}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>,
      );
      continue;
    }

    // unordered list
    if (isUl(line)) {
      const items: string[] = [];
      while (i < lines.length && isUl(lines[i])) {
        items.push(lines[i].replace(/^\s*[-*+]\s+/, ''));
        i++;
      }
      out.push(
        <ul key={key++} className="list-disc pl-5 my-2 space-y-1 text-sm text-slate/80">
          {items.map((it, ii) => (
            <li key={ii}>{renderInline(it)}</li>
          ))}
        </ul>,
      );
      continue;
    }

    // ordered list
    if (isOl(line)) {
      const items: string[] = [];
      while (i < lines.length && isOl(lines[i])) {
        items.push(lines[i].replace(/^\s*\d+[.)]\s+/, ''));
        i++;
      }
      out.push(
        <ol key={key++} className="list-decimal pl-5 my-2 space-y-1 text-sm text-slate/80">
          {items.map((it, ii) => (
            <li key={ii}>{renderInline(it)}</li>
          ))}
        </ol>,
      );
      continue;
    }

    // paragraph — consecutive plain lines merge
    const buf: string[] = [line];
    i++;
    while (i < lines.length && lines[i].trim() && !isBlockStart(lines[i])) {
      buf.push(lines[i]);
      i++;
    }
    out.push(
      <p key={key++} className="text-sm text-slate/80 leading-relaxed my-2">
        {renderInline(buf.join(' '))}
      </p>,
    );
  }

  return out;
}

export function Markdown({ source, className }: { source: string; className?: string }) {
  return <div className={className}>{renderBlocks(source)}</div>;
}
