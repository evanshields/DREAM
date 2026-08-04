import { useState } from 'react';
import { Plus, Trash2, Check, CalendarClock } from 'lucide-react';
import { InlineEdit } from './ui';
import { type ItemView } from '../lib/api';

// ---------------------------------------------------------------------------
// TaskList — the next-step affordance on the deal rail (Phase 5). Re-implements
// Twenty's TaskRow mechanics (studied, not copied):
//   - a rounded checkbox toggles status; the title gets line-through when done
//   - the due date is red ONLY when it is past AND the task is still open
//     (a past date on a DONE task is not red)
//   - open tasks group above done tasks; an inline composer adds to the open group
// Presentational: the DealRail owns the data + optimistic writes and passes handlers.
// ---------------------------------------------------------------------------

function isOverdue(due: string, status: string): boolean {
  if (!due || status !== 'open') return false;
  const d = new Date(due);
  return !Number.isNaN(d.getTime()) && d.getTime() < Date.now();
}

function fmtDue(due: string): string {
  const d = new Date(due);
  if (Number.isNaN(d.getTime())) return due;
  return d.toLocaleDateString('en-US', { month: 'short', day: 'numeric' });
}

function TaskRow({
  task,
  onToggle,
  onDelete,
  onRename,
}: {
  task: ItemView;
  onToggle: (t: ItemView) => void;
  onDelete: (t: ItemView) => void;
  onRename: (t: ItemView, title: string) => void;
}) {
  const done = task.status === 'done';
  const overdue = isOverdue(task.due_at, task.status);
  return (
    <li className="group flex items-start gap-2.5 py-2">
      <button
        type="button"
        onClick={() => onToggle(task)}
        aria-label={done ? 'Mark task open' : 'Mark task done'}
        aria-pressed={done}
        className={`mt-0.5 w-4 h-4 rounded-[5px] border flex items-center justify-center shrink-0 transition-colors ${
          done
            ? 'bg-teal border-teal text-offwhite'
            : 'border-slate/30 hover:border-teal text-transparent'
        }`}
      >
        <Check className="w-3 h-3" strokeWidth={3} />
      </button>

      <div className="min-w-0 flex-1">
        <InlineEdit
          value={task.title}
          onSave={(title) => onRename(task, title)}
          placeholder="Task title"
          ariaLabel="Task title"
          className={`block w-full text-sm leading-snug ${
            done ? 'text-slate/45 line-through' : 'text-slate'
          }`}
        />
        {task.due_at && (
          <span
            className={`inline-flex items-center gap-1 text-[11px] mt-0.5 ${
              overdue ? 'text-danger font-medium' : 'text-slate/45'
            }`}
          >
            <CalendarClock className="w-3 h-3" /> {fmtDue(task.due_at)}
            {overdue && ' · overdue'}
          </span>
        )}
      </div>

      <button
        type="button"
        onClick={() => onDelete(task)}
        aria-label="Delete task"
        className="opacity-0 group-hover:opacity-100 text-slate/30 hover:text-danger transition-opacity shrink-0 mt-0.5"
      >
        <Trash2 className="w-3.5 h-3.5" />
      </button>
    </li>
  );
}

export function TaskList({
  tasks,
  onToggle,
  onDelete,
  onAdd,
  onRename,
}: {
  tasks: ItemView[];
  onToggle: (t: ItemView) => void;
  onDelete: (t: ItemView) => void;
  onAdd: (title: string, dueAt: string) => void;
  onRename: (t: ItemView, title: string) => void;
}) {
  const open = tasks.filter((t) => t.status !== 'done');
  const done = tasks.filter((t) => t.status === 'done');

  const [title, setTitle] = useState('');
  const [dueAt, setDueAt] = useState('');
  const [adding, setAdding] = useState(false);

  const submit = () => {
    const t = title.trim();
    if (!t) return;
    onAdd(t, dueAt);
    setTitle('');
    setDueAt('');
    setAdding(false);
  };

  return (
    <div>
      {open.length === 0 && done.length === 0 ? (
        <p className="text-xs text-slate/45 py-1">All tasks addressed. Add the next step below.</p>
      ) : (
        <ul className="divide-y divide-slate/8">
          {open.map((t) => (
            <TaskRow
              key={t.item_id}
              task={t}
              onToggle={onToggle}
              onDelete={onDelete}
              onRename={onRename}
            />
          ))}
        </ul>
      )}

      {/* inline composer */}
      {adding ? (
        <div className="mt-2 space-y-2">
          <input
            autoFocus
            value={title}
            onChange={(e) => setTitle(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter') submit();
              if (e.key === 'Escape') {
                setAdding(false);
                setTitle('');
                setDueAt('');
              }
            }}
            placeholder="Task title"
            className="input py-1.5 text-sm"
          />
          <div className="flex items-center gap-2">
            <input
              type="date"
              value={dueAt}
              onChange={(e) => setDueAt(e.target.value)}
              className="input py-1.5 text-sm w-auto"
              aria-label="Due date"
            />
            <button
              type="button"
              onClick={submit}
              disabled={!title.trim()}
              className="btn-primary px-3 py-1.5 text-xs"
            >
              Add
            </button>
            <button
              type="button"
              onClick={() => {
                setAdding(false);
                setTitle('');
                setDueAt('');
              }}
              className="btn-ghost px-2 py-1.5 text-xs"
            >
              Cancel
            </button>
          </div>
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setAdding(true)}
          className="mt-1 inline-flex items-center gap-1.5 text-xs font-label font-semibold text-teal hover:text-teal/80"
        >
          <Plus className="w-3.5 h-3.5" /> Add task
        </button>
      )}

      {/* done group */}
      {done.length > 0 && (
        <div className="mt-3 pt-3 border-t border-slate/10">
          <p className="eyebrow text-slate/40 mb-1">Done · {done.length}</p>
          <ul className="divide-y divide-slate/8">
            {done.map((t) => (
              <TaskRow
              key={t.item_id}
              task={t}
              onToggle={onToggle}
              onDelete={onDelete}
              onRename={onRename}
            />
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
