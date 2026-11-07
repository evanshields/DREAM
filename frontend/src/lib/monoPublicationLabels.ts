export function validComparisonMonth(value: unknown): value is string {
  return typeof value === 'string' && /^(?!0000)[0-9]{4}-(?:0[1-9]|1[0-2])$/.test(value);
}

export function historicalDownloadName(filename: string, month: unknown): string | null {
  return validComparisonMonth(month) ? `historical-source-comparison-${month}-${filename}` : null;
}
