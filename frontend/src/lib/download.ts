// Client-side file downloads via object URLs (memo .md, exported .xlsx drafts).

export function downloadBlob(blob: Blob, filename: string): void {
  const url = URL.createObjectURL(blob);
  const a = document.createElement('a');
  a.href = url;
  a.download = filename;
  document.body.appendChild(a);
  a.click();
  a.remove();
  // revoke off the current tick so the click's navigation has consumed the URL
  setTimeout(() => URL.revokeObjectURL(url), 1_000);
}

export function downloadText(text: string, filename: string, mime = 'text/markdown'): void {
  downloadBlob(new Blob([text], { type: `${mime};charset=utf-8` }), filename);
}
