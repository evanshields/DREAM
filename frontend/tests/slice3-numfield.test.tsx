// Slice 3 (plan docs/research/2026-11-04-frontend-test-plan.md). Synthetic data only, fetch stubbed, no live service.
// Vitest + jsdom + React Testing Library. NOT run: no runner is installed on this branch (see PR body).
// it.fails = the app really has this gap today, so the test is expected to fail until the product is fixed.
import { describe, it, expect, vi, afterEach } from 'vitest';
import { render, screen, fireEvent, cleanup } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import { NumField, displayValue, fromEditString } from '../src/components/livecalc';

afterEach(cleanup);

describe('F17 input parsing', () => {
  it('F17 pure helpers: null is a dash, junk is ignored, pct divides by 100', () => {
    expect(displayValue('pct', null)).toBe('—');
    expect(fromEditString('pct', 'abc')).toBeUndefined();
    expect(fromEditString('pct', '  ')).toBeNull();
    expect(fromEditString('pct', '7')).toBeCloseTo(0.07);
  });

  it('F17 NumField keeps the last good value for junk and cleared input, commits 0.07 for 7', async () => {
    const onCommit = vi.fn();
    const user = userEvent.setup();
    render(<NumField label="Exit Cap" kind="pct" optional={false} value={0.065} onCommit={onCommit} />);
    const input = screen.getByLabelText('Exit Cap') as HTMLInputElement;
    expect(input.value).toBe('6.5');

    await user.clear(input);
    await user.type(input, 'abc'); // number input drops non-numeric text
    fireEvent.blur(input);
    expect(onCommit).not.toHaveBeenCalled();
    expect(input.value).toBe('6.5');

    await user.clear(input);
    fireEvent.blur(input);
    expect(onCommit).not.toHaveBeenCalled();
    expect(input.value).toBe('6.5');

    await user.clear(input);
    await user.type(input, '7');
    fireEvent.blur(input);
    expect(onCommit).toHaveBeenCalledTimes(1);
    expect(onCommit.mock.calls[0][0]).toBeCloseTo(0.07);
  });
});
