export type ValueKind = 'text' | 'number' | 'boolean' | 'null';

// Which "Value type" the edit box starts on. Server validation still decides what is accepted.
// A missing (null) value starts on a typeable kind so Edit is usable at once. Null stays available
// in the selector for an explicit clear, but it is never the starting state for a missing field.
export function initialEditKind(value: unknown, unit: string | undefined): ValueKind {
  if (value === null || value === undefined) return unit === 'text' ? 'text' : 'number';
  if (typeof value === 'number') return 'number';
  if (typeof value === 'boolean') return 'boolean';
  return 'text';
}
