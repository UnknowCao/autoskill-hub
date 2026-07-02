#!/usr/bin/env python3
"""
Extract non-deleted requirements from a DOORS raw JSON file and write to a Markdown file.

Usage:
  python extract_nondeleted_reqs.py <input_raw.json> <output.md>

Heuristics:
- Recursively search JSON for objects that contain an identifier (`id`, `ID`, `req_id`, `Identifier`)
  and a text-like field (`text`, `description`, `content`, `req`, `requirement`, `body`).
- Skip objects where a deletion flag or status indicates deletion: keys like `deleted`, `isDeleted`,
  `status` with value `deleted`/`Removed`, or `lifecycle` indicating removal.
"""
import json
import sys
from collections import OrderedDict


def looks_like_id(k):
    return k.lower() in ("id", "identifier", "req_id", "reqid", "docid")


def looks_like_text(k):
    return k.lower() in ("text", "description", "content", "req", "requirement", "body", "shortname", "name")


def is_deleted_obj(obj):
    # check common deletion indicators
    for k, v in obj.items():
        lk = k.lower()
        if lk in ("deleted", "isdeleted", "removed", "is_removed"):
            if isinstance(v, bool):
                return v
            if isinstance(v, str) and v.strip().lower() in ("true", "yes", "deleted", "removed", "1"):
                return True
        if lk in ("status", "state", "lifecycle"):
            if isinstance(v, str) and v.strip().lower() in ("deleted", "removed", "obsolete"):
                return True
    return False


def find_reqs(node, results):
    # node can be dict, list, or primitive
    if isinstance(node, dict):
        # quick deletion check
        if is_deleted_obj(node):
            return

        # try to find id + text in this dict
        id_val = None
        text_val = None
        for k, v in node.items():
            if id_val is None and looks_like_id(k) and (isinstance(v, (str, int))):
                id_val = str(v)
            if text_val is None and looks_like_text(k) and isinstance(v, str):
                text_val = v.strip()

        if id_val and text_val:
            # record if not deleted and not seen before
            if id_val not in results:
                results[id_val] = text_val
        # recurse into children
        for v in node.values():
            find_reqs(v, results)
    elif isinstance(node, list):
        for item in node:
            find_reqs(item, results)


def main():
    if len(sys.argv) < 3:
        print("Usage: python extract_nondeleted_reqs.py <input_raw.json> <output.md>")
        sys.exit(2)

    inp = sys.argv[1]
    out = sys.argv[2]

    with open(inp, 'r', encoding='utf-8') as f:
        data = json.load(f)

    results = OrderedDict()

    # Special-case: DOORS raw export is often a list of objects with 'id' and 'attrs'
    if isinstance(data, list) and data and isinstance(data[0], dict) and 'attrs' in data[0]:
        for item in data:
            iid = item.get('id') or item.get('ID') or item.get('abs_ref')
            attrs = item.get('attrs', {}) or {}
            status = attrs.get('Object_Status') or attrs.get('Object Status') or attrs.get('Object_Status', '')
            if isinstance(status, str) and status.strip().lower() == 'deleted':
                continue
            otype = attrs.get('Object_Type') or attrs.get('Object Type') or ''
            # treat as requirement when Object_Type contains 'req' (Req-Quality, Req-Product etc.)
            if isinstance(otype, str) and 'req' in otype.lower():
                text = attrs.get('Object Text') or attrs.get('Object_Text') or attrs.get('Object Heading') or attrs.get('Object_Heading') or ''
                if text and iid:
                    results[str(iid)] = {'text': text.strip(), 'type': otype}
        # if we found some entries, skip the generic heuristics
        if not results:
            # also try to include objects where Object_Type is missing but Object Text present and status not deleted
            for item in data:
                iid = item.get('id') or item.get('ID') or item.get('abs_ref')
                attrs = item.get('attrs', {}) or {}
                status = attrs.get('Object_Status') or attrs.get('Object Status') or ''
                if isinstance(status, str) and status.strip().lower() == 'deleted':
                    continue
                text = attrs.get('Object Text') or attrs.get('Object_Text')
                if text and iid:
                    # try to record type if present
                    otype2 = attrs.get('Object_Type') or attrs.get('Object Type') or ''
                    results[str(iid)] = {'text': text.strip(), 'type': otype2}
    else:
        find_reqs(data, results)

    # fallback: if no results found, try looser heuristic: any dict with 'id' and any string child
    if not results:
        def loose_search(node, results):
            if isinstance(node, dict):
                if is_deleted_obj(node):
                    return
                id_val = None
                text_val = None
                for k, v in node.items():
                    if id_val is None and any(tok in k.lower() for tok in ('id', 'ident', 'req')) and isinstance(v, (str, int)):
                        id_val = str(v)
                    if text_val is None and isinstance(v, str) and len(v.strip())>10:
                        text_val = v.strip()
                if id_val and text_val and id_val not in results:
                    results[id_val] = text_val
                for v in node.values():
                    loose_search(v, results)
            elif isinstance(node, list):
                for it in node:
                    loose_search(it, results)

        loose_search(data, results)

    # write markdown
    with open(out, 'w', encoding='utf-8') as f:
        f.write('# Extracted requirements (non-deleted)\n\n')
        if not results:
            f.write('_No requirements found by heuristics._\n')
        else:
            for rid, info in results.items():
                # info can be a dict {'text':..., 'type':...} or a plain string from older runs
                if isinstance(info, dict):
                    text = info.get('text', '')
                    otype = info.get('type', '')
                else:
                    text = str(info)
                    otype = ''
                f.write('### ID: {}\n\n'.format(rid))
                if otype:
                    f.write('Type: {}\n\n'.format(otype))
                # ensure text is single-spaced and trimmed
                lines = [ln.rstrip() for ln in text.splitlines()]
                f.write('\n'.join(lines))
                f.write('\n\n')


if __name__ == '__main__':
    main()
