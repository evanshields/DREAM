import { useCallback, useEffect, useRef, useState } from 'react';
import {
  Users,
  ListTodo,
  StickyNote,
  Plus,
  X,
  Trash2,
  Mail,
  UserPlus,
  Loader2,
} from 'lucide-react';
import {
  listDealContacts,
  listDealItems,
  listContacts,
  createContact,
  createItem,
  createLink,
  deleteLink,
  deleteItem,
  toggleItem,
  ApiError,
  CONTACT_ROLES,
  ROLE_LABELS,
  type ContactView,
  type ItemView,
  type ContactRole,
} from '../lib/api';
import { Card } from './ui';
import { TaskList } from './TaskList';
import { useToast } from '../contexts/ToastContext';
import { fmtDate } from '../lib/format';

// ---------------------------------------------------------------------------
// DealRail — the right rail on a deal's Overview tab (Phase 5). Three stacked
// sections: who is on the deal (contacts, one slot per role), what is next
// (tasks), and what was noted (notes). Owns the deal-scoped CRM data + every
// optimistic write; calls onChanged so the parent can refresh the timeline
// (notes + tasks show there too). Deletes are deferred (undo toast, zero backend
// during the countdown). Attach-or-create contacts inline, no page nav.
// ---------------------------------------------------------------------------

export function DealRail({ dealId, onChanged }: { dealId: string; onChanged?: () => void }) {
  const { showToast } = useToast();
  const [contacts, setContacts] = useState<ContactView[]>([]);
  const [tasks, setTasks] = useState<ItemView[]>([]);
  const [notes, setNotes] = useState<ItemView[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  const load = useCallback(() => {
    let cancelled = false;
    setError(null);
    Promise.all([
      listDealContacts(dealId),
      listDealItems(dealId, 'task'),
      listDealItems(dealId, 'note'),
    ])
      .then(([c, t, n]) => {
        if (cancelled) return;
        setContacts(c);
        setTasks(t);
        setNotes(n);
        setLoading(false);
      })
      .catch((e) => {
        if (cancelled) return;
        if (e instanceof ApiError && e.status === 401) return;
        setError(e instanceof Error ? e.message : String(e));
        setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, [dealId]);

  useEffect(() => load(), [load]);

  const notify = () => onChanged?.();

  // ---- contacts ----
  const attachContact = async (contact: ContactView) => {
    try {
      await createLink({
        source_kind: 'contact',
        source_id: contact.contact_id,
        target_kind: 'deal',
        target_id: dealId,
      });
      load();
      notify();
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) return;
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const createAndAttach = async (role: ContactRole, fullName: string, email: string) => {
    try {
      const doc: Record<string, unknown> = { kind: 'person', full_name: fullName, role };
      if (email.trim()) doc.emails = [email.trim()];
      const c = await createContact(doc);
      await createLink({
        source_kind: 'contact',
        source_id: c.contact_id,
        target_kind: 'deal',
        target_id: dealId,
      });
      load();
      notify();
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) return;
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const detachContact = (contact: ContactView) => {
    if (!contact.link_id) return;
    const linkId = contact.link_id;
    setContacts((prev) => prev.filter((c) => c.contact_id !== contact.contact_id));
    showToast({
      message: `Removed ${contact.name} from this deal`,
      tone: 'info',
      action: { label: 'Undo', onClick: () => load() },
      onExpire: () => {
        deleteLink(linkId).then(notify).catch(() => load());
      },
      dedupeKey: `detach-${linkId}`,
    });
  };

  // ---- tasks ----
  const addTask = async (title: string, dueAt: string) => {
    try {
      const doc: Record<string, unknown> = { kind: 'task', title, status: 'open' };
      if (dueAt) doc.due_at = dueAt;
      const t = await createItem(doc);
      await createLink({
        source_kind: 'task',
        source_id: t.item_id,
        target_kind: 'deal',
        target_id: dealId,
      });
      load();
      notify();
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) return;
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const toggleTask = async (task: ItemView) => {
    const nextStatus = task.status === 'done' ? 'open' : 'done';
    setTasks((prev) =>
      prev.map((t) => (t.item_id === task.item_id ? { ...t, status: nextStatus } : t)),
    );
    try {
      const updated = await toggleItem(task.item_id, task.version);
      setTasks((prev) => prev.map((t) => (t.item_id === task.item_id ? updated : t)));
      notify();
    } catch (e) {
      setTasks((prev) => prev.map((t) => (t.item_id === task.item_id ? task : t))); // revert
      if (e instanceof ApiError && e.status === 401) return;
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const deleteTask = (task: ItemView) => {
    setTasks((prev) => prev.filter((t) => t.item_id !== task.item_id));
    showToast({
      message: `Deleted task “${task.title}”`,
      tone: 'danger',
      action: { label: 'Undo', onClick: () => load() },
      onExpire: () => {
        deleteItem(task.item_id).then(notify).catch(() => load());
      },
      dedupeKey: `del-task-${task.item_id}`,
    });
  };

  // ---- notes ----
  const addNote = async (body: string) => {
    try {
      const n = await createItem({ kind: 'note', body });
      await createLink({
        source_kind: 'note',
        source_id: n.item_id,
        target_kind: 'deal',
        target_id: dealId,
      });
      load();
      notify();
    } catch (e) {
      if (e instanceof ApiError && e.status === 401) return;
      setError(e instanceof Error ? e.message : String(e));
    }
  };

  const deleteNote = (note: ItemView) => {
    setNotes((prev) => prev.filter((n) => n.item_id !== note.item_id));
    showToast({
      message: 'Deleted note',
      tone: 'danger',
      action: { label: 'Undo', onClick: () => load() },
      onExpire: () => {
        deleteItem(note.item_id).then(notify).catch(() => load());
      },
      dedupeKey: `del-note-${note.item_id}`,
    });
  };

  if (loading) {
    return (
      <Card className="p-5">
        <div className="flex items-center justify-center py-8 text-slate/40 text-sm">
          <Loader2 className="w-4 h-4 animate-spin mr-2" /> Loading deal team…
        </div>
      </Card>
    );
  }

  return (
    <div className="space-y-4">
      {error && (
        <Card className="p-3 border-danger/30 bg-danger/5">
          <p className="text-xs text-danger">{error}</p>
        </Card>
      )}

      {/* Contacts by role */}
      <Card className="p-5">
        <h3 className="eyebrow text-slate/55 flex items-center mb-3">
          <Users className="w-3.5 h-3.5 mr-2" /> Deal Team
        </h3>
        <div className="space-y-3">
          {CONTACT_ROLES.map((role) => (
            <RoleSlot
              key={role}
              role={role}
              contacts={contacts.filter((c) => c.role === role)}
              onAttach={attachContact}
              onCreate={createAndAttach}
              onDetach={detachContact}
            />
          ))}
        </div>
      </Card>

      {/* Tasks */}
      <Card className="p-5">
        <h3 className="eyebrow text-slate/55 flex items-center mb-3">
          <ListTodo className="w-3.5 h-3.5 mr-2" /> Tasks
        </h3>
        <TaskList tasks={tasks} onToggle={toggleTask} onDelete={deleteTask} onAdd={addTask} />
      </Card>

      {/* Notes */}
      <Card className="p-5">
        <h3 className="eyebrow text-slate/55 flex items-center mb-3">
          <StickyNote className="w-3.5 h-3.5 mr-2" /> Notes
        </h3>
        <NoteComposer onAdd={addNote} />
        {notes.length > 0 && (
          <ul className="mt-3 space-y-2">
            {notes.map((n) => (
              <NoteRow key={n.item_id} note={n} onDelete={deleteNote} />
            ))}
          </ul>
        )}
      </Card>
    </div>
  );
}

// ---------------------------------------------------------------------------
// Role slot — a labelled row that lists the pinned contacts of one role and
// exposes an inline attach-or-create popover.
// ---------------------------------------------------------------------------

function RoleSlot({
  role,
  contacts,
  onAttach,
  onCreate,
  onDetach,
}: {
  role: ContactRole;
  contacts: ContactView[];
  onAttach: (c: ContactView) => void;
  onCreate: (role: ContactRole, fullName: string, email: string) => void;
  onDetach: (c: ContactView) => void;
}) {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement | null>(null);

  useEffect(() => {
    if (!open) return;
    const onDown = (e: PointerEvent) => {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    };
    document.addEventListener('pointerdown', onDown);
    return () => document.removeEventListener('pointerdown', onDown);
  }, [open]);

  return (
    <div ref={ref} className="relative">
      <div className="flex items-center justify-between gap-2">
        <span className="text-[11px] font-label font-semibold uppercase tracking-wide text-slate/40">
          {ROLE_LABELS[role]}
        </span>
        <button
          type="button"
          onClick={() => setOpen((v) => !v)}
          aria-label={`Add ${ROLE_LABELS[role]}`}
          className="text-slate/30 hover:text-teal transition-colors"
        >
          <Plus className="w-3.5 h-3.5" />
        </button>
      </div>

      {contacts.length > 0 ? (
        <div className="mt-1 flex flex-wrap gap-1.5">
          {contacts.map((c) => (
            <ContactChip key={c.contact_id} contact={c} onDetach={onDetach} />
          ))}
        </div>
      ) : (
        <button
          type="button"
          onClick={() => setOpen(true)}
          className="mt-0.5 text-xs text-slate/35 hover:text-teal transition-colors"
        >
          + add {ROLE_LABELS[role].toLowerCase()}
        </button>
      )}

      {open && (
        <AttachPopover
          role={role}
          alreadyLinked={contacts.map((c) => c.contact_id)}
          onAttach={(c) => {
            onAttach(c);
            setOpen(false);
          }}
          onCreate={(name, email) => {
            onCreate(role, name, email);
            setOpen(false);
          }}
          onClose={() => setOpen(false)}
        />
      )}
    </div>
  );
}

function ContactChip({
  contact,
  onDetach,
}: {
  contact: ContactView;
  onDetach: (c: ContactView) => void;
}) {
  const email =
    contact.primary_email ||
    (Array.isArray(contact.doc.emails) ? String((contact.doc.emails as unknown[])[0] ?? '') : '');
  return (
    <span
      className="group inline-flex items-center gap-1.5 rounded-full bg-teal-panel border border-teal/15 pl-2.5 pr-1.5 py-1 text-xs text-slate"
      title={email || undefined}
    >
      <span className="font-medium">{contact.name}</span>
      <button
        type="button"
        onClick={() => onDetach(contact)}
        aria-label={`Remove ${contact.name}`}
        className="text-teal/40 hover:text-danger transition-colors"
      >
        <X className="w-3 h-3" />
      </button>
    </span>
  );
}

function AttachPopover({
  role,
  alreadyLinked,
  onAttach,
  onCreate,
  onClose,
}: {
  role: ContactRole;
  alreadyLinked: string[];
  onAttach: (c: ContactView) => void;
  onCreate: (name: string, email: string) => void;
  onClose: () => void;
}) {
  const [existing, setExisting] = useState<ContactView[]>([]);
  const [q, setQ] = useState('');
  const [email, setEmail] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    let cancelled = false;
    listContacts({ kind: 'person', role })
      .then((cs) => {
        if (cancelled) return;
        setExisting(cs.filter((c) => !alreadyLinked.includes(c.contact_id)));
        setLoading(false);
      })
      .catch(() => setLoading(false));
    return () => {
      cancelled = true;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [role]);

  const matches = existing.filter((c) => c.name.toLowerCase().includes(q.trim().toLowerCase()));
  const canCreate = q.trim().length > 0;

  return (
    <div className="absolute z-20 top-full right-0 mt-1 w-64 rounded-xl border border-slate/15 bg-white shadow-cardHover p-3">
      <div className="flex items-center justify-between mb-2">
        <span className="eyebrow text-slate/45">Add {ROLE_LABELS[role]}</span>
        <button type="button" onClick={onClose} aria-label="Close" className="text-slate/30 hover:text-slate">
          <X className="w-3.5 h-3.5" />
        </button>
      </div>

      <input
        autoFocus
        value={q}
        onChange={(e) => setQ(e.target.value)}
        placeholder="Search or type a name"
        className="input py-1.5 text-sm"
      />

      {loading ? (
        <p className="text-xs text-slate/40 mt-2">Loading…</p>
      ) : (
        <>
          {matches.length > 0 && (
            <ul className="mt-2 max-h-40 overflow-y-auto -mx-1">
              {matches.map((c) => (
                <li key={c.contact_id}>
                  <button
                    type="button"
                    onClick={() => onAttach(c)}
                    className="w-full flex items-center gap-2 px-2 py-1.5 rounded-lg text-left text-sm text-slate hover:bg-teal-panel/60"
                  >
                    <UserPlus className="w-3.5 h-3.5 text-teal shrink-0" />
                    <span className="min-w-0 flex-1 truncate">{c.name}</span>
                    {c.primary_email && (
                      <Mail className="w-3 h-3 text-slate/30 shrink-0" />
                    )}
                  </button>
                </li>
              ))}
            </ul>
          )}

          {canCreate && (
            <div className="mt-2 pt-2 border-t border-slate/10 space-y-2">
              <input
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="Email (optional)"
                type="email"
                className="input py-1.5 text-sm"
              />
              <button
                type="button"
                onClick={() => onCreate(q.trim(), email)}
                className="btn-primary w-full px-3 py-1.5 text-xs"
              >
                <Plus className="w-3.5 h-3.5" /> Create “{q.trim()}”
              </button>
            </div>
          )}

          {!canCreate && matches.length === 0 && (
            <p className="text-xs text-slate/40 mt-2">
              Type a name to create a new {ROLE_LABELS[role].toLowerCase()}.
            </p>
          )}
        </>
      )}
    </div>
  );
}

// ---------------------------------------------------------------------------
// Notes — a plain markdown textarea composer (no rich-text editor, per the
// refuse-to-copy list) + the pinned note list.
// ---------------------------------------------------------------------------

function NoteComposer({ onAdd }: { onAdd: (body: string) => void }) {
  const [body, setBody] = useState('');
  const submit = () => {
    const b = body.trim();
    if (!b) return;
    onAdd(b);
    setBody('');
  };
  return (
    <div>
      <textarea
        value={body}
        onChange={(e) => setBody(e.target.value)}
        onKeyDown={(e) => {
          // Cmd/Ctrl+Enter submits (a plain Enter keeps a newline — it's a note body)
          if ((e.metaKey || e.ctrlKey) && e.key === 'Enter') submit();
        }}
        placeholder="Add a note…"
        rows={2}
        className="input text-sm resize-y min-h-[2.5rem]"
      />
      {body.trim() && (
        <div className="flex items-center gap-2 mt-2">
          <button type="button" onClick={submit} className="btn-primary px-3 py-1.5 text-xs">
            Add note
          </button>
          <span className="text-[10px] text-slate/35">⌘↵ to save</span>
        </div>
      )}
    </div>
  );
}

function NoteRow({ note, onDelete }: { note: ItemView; onDelete: (n: ItemView) => void }) {
  const body = typeof note.doc.body === 'string' ? note.doc.body : '';
  return (
    <li className="group rounded-lg border border-slate/10 bg-slate/[0.02] px-3 py-2">
      <div className="flex items-start justify-between gap-2">
        <p className="text-sm text-slate/80 whitespace-pre-wrap min-w-0 flex-1">{body}</p>
        <button
          type="button"
          onClick={() => onDelete(note)}
          aria-label="Delete note"
          className="opacity-0 group-hover:opacity-100 text-slate/30 hover:text-danger transition-opacity shrink-0"
        >
          <Trash2 className="w-3.5 h-3.5" />
        </button>
      </div>
      <p className="text-[10px] text-slate/35 mt-1">
        {note.author && <span>{note.author} · </span>}
        {fmtDate(note.created_at)}
      </p>
    </li>
  );
}
