"""Phase 5 acceptance tests — SQLiteCRMStore: opaque-doc round trip, derived index, optimistic
concurrency, idempotent links, and the delete cascades. Mirrors test_deal_store.py's style."""
import os
import sys

import pytest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from store import (  # noqa: E402
    SQLiteCRMStore, ContactNotFound, ItemNotFound, VersionConflict, CONTACT_ROLES,
)

NOW = "2026-07-13T12:00:00Z"
LATER = "2026-07-13T13:00:00Z"


def store():
    return SQLiteCRMStore(":memory:")


def _person(full_name="Jane Broker", role="broker", **extra):
    return {"kind": "person", "full_name": full_name, "role": role,
            "emails": ["jane@example.com"], **extra}


def _company(name="Acme Capital", **extra):
    return {"kind": "company", "name": name, "company_type": "lender",
            "domain": "acme.example", **extra}


def _task(title="Call the lender", **extra):
    return {"kind": "task", "title": title, "due_at": "2026-07-20", **extra}


def _note(body="Seller is motivated.", **extra):
    return {"kind": "note", "body": body, "author": "evan", **extra}


# ---------------------------------------------------------------------------
# Contacts — round trip + derived index
# ---------------------------------------------------------------------------

def test_create_person_round_trips_and_derives_index():
    s = store()
    rec = s.create_contact(_person(), owner="evan@shieldstone.co", now_iso=NOW)
    got = s.get_contact(rec.contact_id)
    assert got.doc == {**_person(), "kind": "person"}  # opaque doc survives byte-for-byte
    assert got.version == 1
    assert got.kind == "person" and got.name == "Jane Broker" and got.role == "broker"
    assert got.primary_email == "jane@example.com"
    assert got.owner == "evan@shieldstone.co"
    assert got.created_at == NOW and got.updated_at == NOW


def test_create_company_indexes_name_and_domain():
    s = store()
    rec = s.create_contact(_company(), owner="evan", now_iso=NOW)
    got = s.get_contact(rec.contact_id)
    assert got.kind == "company" and got.name == "Acme Capital"
    assert got.role == "" and got.company_id == ""
    assert got.primary_email == "acme.example"  # company domain lands in the email index slot


def test_all_six_plus_roles_index_cleanly():
    s = store()
    for role in CONTACT_ROLES:
        rec = s.create_contact(_person(full_name=f"P {role}", role=role), owner="evan", now_iso=NOW)
        assert s.get_contact(rec.contact_id).role == role
    assert set(CONTACT_ROLES) == {
        "broker", "seller", "lender", "bond_counsel", "issuer", "nonprofit_sponsor", "other"}


def test_put_contact_increments_version_and_updates_index():
    s = store()
    rec = s.create_contact(_person(), owner="evan", now_iso=NOW)
    updated = s.put_contact(rec.contact_id, _person(full_name="Jane Seller", role="seller"),
                            expected_version=1, now_iso=LATER)
    assert updated.version == 2
    assert updated.name == "Jane Seller" and updated.role == "seller"
    assert updated.updated_at == LATER and updated.created_at == NOW


def test_contact_version_conflict_blocks_lost_update():
    s = store()
    rec = s.create_contact(_person(), owner="evan", now_iso=NOW)
    s.put_contact(rec.contact_id, _person(full_name="A"), expected_version=1, now_iso=LATER)
    with pytest.raises(VersionConflict) as ei:
        s.put_contact(rec.contact_id, _person(full_name="B"), expected_version=1, now_iso=LATER)
    assert ei.value.expected == 1 and ei.value.actual == 2
    assert s.get_contact(rec.contact_id).name == "A"


def test_contact_missing_raises():
    s = store()
    with pytest.raises(ContactNotFound):
        s.get_contact("nope")
    with pytest.raises(ContactNotFound):
        s.put_contact("nope", _person(), expected_version=1, now_iso=NOW)


def test_list_contacts_filters():
    s = store()
    s.create_contact(_person(full_name="Broker A", role="broker"), owner="evan", now_iso=NOW)
    s.create_contact(_person(full_name="Lender B", role="lender"), owner="evan", now_iso=NOW)
    s.create_contact(_company(name="Co C"), owner="chuck", now_iso=NOW)
    assert {c.name for c in s.list_contacts(kind="person")} == {"Broker A", "Lender B"}
    assert {c.name for c in s.list_contacts(role="broker")} == {"Broker A"}
    assert {c.name for c in s.list_contacts(kind="company")} == {"Co C"}
    assert {c.name for c in s.list_contacts(owner="chuck")} == {"Co C"}


# ---------------------------------------------------------------------------
# Items — tasks + notes
# ---------------------------------------------------------------------------

def test_create_task_defaults_open_and_indexes():
    s = store()
    rec = s.create_item(_task(), owner="evan", now_iso=NOW)
    got = s.get_item(rec.item_id)
    assert got.kind == "task" and got.status == "open"  # status defaulted
    assert got.title == "Call the lender" and got.due_at == "2026-07-20"


def test_create_note_has_no_status():
    s = store()
    rec = s.create_item(_note(), owner="evan", now_iso=NOW)
    got = s.get_item(rec.item_id)
    assert got.kind == "note" and got.status == ""
    assert got.author == "evan"
    assert got.doc["body"] == "Seller is motivated."


def test_task_toggle_via_put_flips_status():
    s = store()
    rec = s.create_item(_task(), owner="evan", now_iso=NOW)
    done = s.put_item(rec.item_id, {**_task(), "status": "done"},
                      expected_version=1, now_iso=LATER)
    assert done.status == "done" and done.version == 2


def test_item_version_conflict():
    s = store()
    rec = s.create_item(_task(), owner="evan", now_iso=NOW)
    s.put_item(rec.item_id, {**_task(), "status": "done"}, expected_version=1, now_iso=LATER)
    with pytest.raises(VersionConflict):
        s.put_item(rec.item_id, _task(), expected_version=1, now_iso=LATER)


def test_item_missing_raises():
    s = store()
    with pytest.raises(ItemNotFound):
        s.get_item("nope")


def test_list_items_filters_by_kind_and_status():
    s = store()
    s.create_item(_task(title="open task"), owner="evan", now_iso=NOW)
    done = s.create_item(_task(title="done task"), owner="evan", now_iso=NOW)
    s.put_item(done.item_id, {**_task(title="done task"), "status": "done"},
               expected_version=1, now_iso=LATER)
    s.create_item(_note(), owner="evan", now_iso=NOW)
    assert {i.title for i in s.list_items(kind="task")} == {"open task", "done task"}
    assert {i.title for i in s.list_items(kind="task", status="open")} == {"open task"}
    assert {i.title for i in s.list_items(kind="task", status="done")} == {"done task"}
    assert len(s.list_items(kind="note")) == 1


# ---------------------------------------------------------------------------
# Links — attach / detach / idempotency / filters
# ---------------------------------------------------------------------------

def test_link_attach_and_list_by_target():
    s = store()
    c = s.create_contact(_person(), owner="evan", now_iso=NOW)
    n = s.create_item(_note(), owner="evan", now_iso=NOW)
    s.create_link("contact", c.contact_id, "deal", "deal-1", now_iso=NOW)
    s.create_link("note", n.item_id, "deal", "deal-1", now_iso=NOW)
    links = s.list_links(target_kind="deal", target_id="deal-1")
    assert len(links) == 2
    assert {l.source_kind for l in links} == {"contact", "note"}


def test_link_is_idempotent():
    s = store()
    c = s.create_contact(_person(), owner="evan", now_iso=NOW)
    a = s.create_link("contact", c.contact_id, "deal", "deal-1", now_iso=NOW)
    b = s.create_link("contact", c.contact_id, "deal", "deal-1", now_iso=LATER)
    assert a.link_id == b.link_id  # no duplicate row
    assert len(s.list_links(target_kind="deal", target_id="deal-1")) == 1


def test_delete_link_returns_bool():
    s = store()
    c = s.create_contact(_person(), owner="evan", now_iso=NOW)
    link = s.create_link("contact", c.contact_id, "deal", "deal-1", now_iso=NOW)
    assert s.delete_link(link.link_id) is True
    assert s.delete_link(link.link_id) is False  # idempotent detach
    assert s.list_links(target_kind="deal", target_id="deal-1") == []


def test_list_links_source_and_target_filters():
    s = store()
    c = s.create_contact(_person(), owner="evan", now_iso=NOW)
    s.create_link("contact", c.contact_id, "deal", "d1", now_iso=NOW)
    s.create_link("contact", c.contact_id, "deal", "d2", now_iso=NOW)
    assert len(s.list_links(source_kind="contact", source_id=c.contact_id)) == 2
    assert len(s.list_links(target_kind="deal", target_id="d1")) == 1


# ---------------------------------------------------------------------------
# Cascades
# ---------------------------------------------------------------------------

def test_delete_contact_cascades_links():
    s = store()
    c = s.create_contact(_person(), owner="evan", now_iso=NOW)
    s.create_link("contact", c.contact_id, "deal", "deal-1", now_iso=NOW)
    s.delete_contact(c.contact_id)
    with pytest.raises(ContactNotFound):
        s.get_contact(c.contact_id)
    assert s.list_links(target_kind="deal", target_id="deal-1") == []
    with pytest.raises(ContactNotFound):
        s.delete_contact(c.contact_id)  # second delete raises


def test_delete_item_cascades_links():
    s = store()
    n = s.create_item(_note(), owner="evan", now_iso=NOW)
    s.create_link("note", n.item_id, "deal", "deal-1", now_iso=NOW)
    s.delete_item(n.item_id)
    with pytest.raises(ItemNotFound):
        s.get_item(n.item_id)
    assert s.list_links(target_kind="deal", target_id="deal-1") == []


def test_delete_links_for_target_is_the_deal_delete_hook():
    """The deal-delete cascade: unpin every link pointing at a deal, leaving the records alive."""
    s = store()
    c = s.create_contact(_person(), owner="evan", now_iso=NOW)
    n = s.create_item(_note(), owner="evan", now_iso=NOW)
    s.create_link("contact", c.contact_id, "deal", "deal-1", now_iso=NOW)
    s.create_link("note", n.item_id, "deal", "deal-1", now_iso=NOW)
    removed = s.delete_links_for_target("deal", "deal-1")
    assert removed == 2
    assert s.list_links(target_kind="deal", target_id="deal-1") == []
    # the records themselves survive the deal delete (a contact belongs to many deals)
    assert s.get_contact(c.contact_id) is not None
    assert s.get_item(n.item_id) is not None
    # unpinning a deal with no links is a harmless 0
    assert s.delete_links_for_target("deal", "deal-none") == 0


def test_delete_links_for_either_endpoint():
    s = store()
    c = s.create_contact(_person(), owner="evan", now_iso=NOW)
    s.create_link("contact", c.contact_id, "deal", "deal-1", now_iso=NOW)  # contact as source
    s.create_link("note", "note-x", "contact", c.contact_id, now_iso=NOW)  # contact as target
    removed = s.delete_links_for("contact", c.contact_id)
    assert removed == 2


def test_duplicate_explicit_id_guard():
    s = store()
    s.create_contact(_person(), owner="evan", now_iso=NOW, contact_id="fixed")
    with pytest.raises(ValueError):
        s.create_contact(_person(), owner="evan", now_iso=NOW, contact_id="fixed")
