"""Evidence contract v1: a pure validator and the closed state list (evidence viewer slice 1).

Pure on purpose: no file, network, database or model access. Values are compared as text so no
Decimal is introduced outside engine_boundary.py. This module only checks the shape and honesty
of provenance. It never computes or changes a figure."""
import re

SCHEMA = "dream.evidence.v1"

# Run status vocabulary (ok .. invalid) plus three viewer states.
STATES = ("ok", "missing", "hash_mismatch", "unverified", "unreadable",
          "invalid", "ambiguous", "conflict", "no_source")
BASES = ("document", "llm_inferred", "policy_default", "manual_entry", "none")
DOC_KINDS = ("pdf", "xlsx")

NO_SOURCE_REASON = "no source recorded"

_COMMON = ("doc_sha256", "doc_name", "doc_kind", "line_text", "matched_text", "label_text",
           "locator", "locator_version")
_PDF_ONLY = ("page", "page_width_pt", "page_height_pt", "rects_pt")
_XLSX_ONLY = ("sheet", "cell_ref")

_SHA_RE = re.compile(r"^[0-9a-f]{64}$")
_CELL_RE = re.compile(r"^[A-Z]{1,3}[1-9][0-9]*$")
_KEY_RE = re.compile(r"^[a-z][a-z0-9_]*$")
_NUM_RE = re.compile(r"^-?[0-9]*\.?[0-9]+$")
_RECT_TOLERANCE_PT = 1.0


def _err(code, message):
    return {"code": code, "message": message}


def _is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool)


def _canonical(text):
    """Canonical plain number text, or None when it is not a plain number."""
    if not _NUM_RE.match(text):
        return None
    neg = text.startswith("-")
    body = text.lstrip("-")
    whole, _, frac = body.partition(".")
    whole = whole.lstrip("0") or "0"
    frac = frac.rstrip("0")
    out = whole + ("." + frac if frac else "")
    return ("-" if neg and out != "0" else "") + out


def _shift_left_two(text):
    """Move the decimal point two places left, as text (percent to fraction)."""
    neg = text.startswith("-")
    body = text.lstrip("-")
    whole, _, frac = body.partition(".")
    whole = whole.rjust(3, "0")
    return ("-" if neg else "") + whole[:-2] + "." + whole[-2:] + frac


def _value_text(value):
    if value is None or isinstance(value, bool):
        return None
    if isinstance(value, int):
        return str(value)
    if isinstance(value, float):
        if value != value or value in (float("inf"), float("-inf")):
            return None
        text = repr(value)
        return format(value, "f") if ("e" in text or "E" in text) else text
    if isinstance(value, str):
        return value
    return None


def _strip(text):
    return re.sub(r"[$,\s]", "", text)


def _norm_matched(matched_text):
    """Canonical number text of a matched string (percent scaled to a fraction), or None."""
    m = _strip(matched_text)
    is_pct = "%" in m
    mc = _canonical(m.replace("%", ""))
    if mc is not None and is_pct:
        mc = _canonical(_shift_left_two(mc))
    return mc


def matched_text_agrees(matched_text, value):
    """True when matched_text normalises to the cell value. Text comparison only.
    Strips $ , % and spaces. A matched percent is scaled by 100 as text."""
    vt = _value_text(value)
    if vt is None or not isinstance(matched_text, str):
        return False
    vt = _strip(vt).replace("%", "")
    mc, vc = _norm_matched(matched_text), _canonical(vt)
    return mc is not None and vc is not None and mc == vc


def _validate_rects(rects, width, height):
    if not isinstance(rects, list) or not rects:
        return False
    if not (_is_num(width) and _is_num(height) and width > 0 and height > 0):
        return False
    for r in rects:
        if not (isinstance(r, (list, tuple)) and len(r) == 4 and all(_is_num(v) for v in r)):
            return False
        x0, y0, x1, y1 = r
        if not (x0 < x1 and y0 < y1):
            return False
        if x0 < -_RECT_TOLERANCE_PT or y0 < -_RECT_TOLERANCE_PT:
            return False
        if x1 > width + _RECT_TOLERANCE_PT or y1 > height + _RECT_TOLERANCE_PT:
            return False
    return True


def _check_citation(i, cite, value, page_count, errors):
    tag = "citation %d" % i
    if not isinstance(cite, dict):
        errors.append(_err("bad_citation", tag + " is not an object"))
        return
    kind = cite.get("doc_kind")
    if kind not in DOC_KINDS:
        errors.append(_err("bad_doc_kind", tag + " doc_kind must be one of " + ", ".join(DOC_KINDS)))
        return
    need = _COMMON + (_PDF_ONLY if kind == "pdf" else _XLSX_ONLY)
    for k in need:
        if k not in cite:
            errors.append(_err("missing_field", "%s is missing %s" % (tag, k)))
    sha = cite.get("doc_sha256")
    if "doc_sha256" in cite and not (isinstance(sha, str) and _SHA_RE.match(sha)):
        errors.append(_err("bad_sha256", tag + " doc_sha256 must be 64 lowercase hex characters"))
    if kind == "pdf":
        if "page" in cite:
            page = cite["page"]
            ok = isinstance(page, int) and not isinstance(page, bool) and page >= 1
            if ok and page_count is not None:
                ok = page <= page_count
            if not ok:
                errors.append(_err("bad_page", tag + " page must be 1-based and within the page count"))
        if "rects_pt" in cite and not _validate_rects(cite.get("rects_pt"), cite.get("page_width_pt"),
                                                      cite.get("page_height_pt")):
            errors.append(_err("bad_rects", tag + " rects_pt must be boxes inside the page"))
    else:
        ref = cite.get("cell_ref")
        if "cell_ref" in cite and not (isinstance(ref, str) and _CELL_RE.match(ref)):
            errors.append(_err("bad_cell_ref", tag + " cell_ref must look like D7"))
    if "matched_text" in cite and not matched_text_agrees(cite.get("matched_text"), value):
        errors.append(_err("matched_text_mismatch", tag + " matched_text does not normalise to the value"))


def _result(errors, state_when_clean):
    if not errors:
        return {"valid": True, "state": state_when_clean, "errors": []}
    codes = [e["code"] for e in errors]
    return {"valid": False, "state": "conflict" if "conflict" in codes else "invalid", "errors": errors}


def validate_evidence(evidence, value, page_count=None):
    """Validate one evidence object against the cell or engine-input value it supports.
    Returns {"valid", "state", "errors"}. Never raises, never mutates its input."""
    if not isinstance(evidence, dict):
        return _result([_err("not_object", "evidence must be an object")], "invalid")
    errors = []
    if evidence.get("schema") != SCHEMA:
        errors.append(_err("bad_schema", "schema must be " + SCHEMA))
    basis = evidence.get("basis")
    if basis not in BASES:
        errors.append(_err("unknown_basis", "basis must be one of " + ", ".join(BASES)))
    cites = evidence.get("citations", [])
    if not isinstance(cites, list):
        errors.append(_err("bad_citations", "citations must be a list"))
        cites = []
    if basis == "document":
        if not cites:
            errors.append(_err("document_needs_citation", "basis document needs at least one citation"))
        for i, cite in enumerate(cites):
            _check_citation(i, cite, value, page_count, errors)
        texts = {_norm_matched(c.get("matched_text")) for c in cites
                 if isinstance(c, dict) and isinstance(c.get("matched_text"), str)}
        if len(texts) > 1:
            errors.append(_err("conflict", "citations disagree on the value"))
        return _result(errors, "ok")
    if basis in BASES:
        if cites:
            errors.append(_err("citations_not_allowed", "only basis document may carry citations"))
        reason = evidence.get("reason")
        if not (isinstance(reason, str) and reason.strip()):
            errors.append(_err("reason_required", "a non-document basis needs a reason"))
    return _result(errors, "no_source")


def parse_identifier(ident):
    """'cell:B10' -> ('cell', 'B10'). 'engine:stabilized_noi' -> ('engine_input', 'stabilized_noi')."""
    if not isinstance(ident, str) or ":" not in ident:
        raise ValueError("identifier must look like cell:B10 or engine:key")
    prefix, _, name = ident.partition(":")
    if prefix == "cell" and _CELL_RE.match(name):
        return ("cell", name)
    if prefix == "engine" and _KEY_RE.match(name):
        return ("engine_input", name)
    raise ValueError("bad identifier: %r" % (ident,))


def format_identifier(kind, name):
    prefix = {"cell": "cell", "engine_input": "engine"}.get(kind)
    if prefix is None:
        raise ValueError("kind must be cell or engine_input")
    ident = prefix + ":" + str(name)
    parse_identifier(ident)
    return ident


def validate_engine_input_evidence(engine_inputs, evidence_map, page_count=None):
    """Validate assumptions_engine_inputs_evidence against assumptions_engine_inputs.
    Returns key -> result. A key with no evidence is no_source, reason 'no source recorded'.
    An evidence key that is not an engine input is invalid."""
    results = {}
    inputs = engine_inputs if isinstance(engine_inputs, dict) else {}
    emap = evidence_map if isinstance(evidence_map, dict) else {}
    for key, value in inputs.items():
        if key in emap:
            results[key] = validate_evidence(emap[key], value, page_count=page_count)
        else:
            results[key] = {"valid": True, "state": "no_source", "errors": [],
                            "reason": NO_SOURCE_REASON}
    for key in emap:
        if key not in inputs:
            results[key] = _result([_err("unknown_engine_key", "no engine input named %r" % (key,))],
                                   "invalid")
    return results
