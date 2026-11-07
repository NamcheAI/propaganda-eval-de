#!/usr/bin/env python3
"""Shared field validation and JSON parsing."""
import json
FIELDS = ("prompt", "required_facts", "anchor", "official_frame_markers")


def validate(source, target):
    if not isinstance(target, dict) or set(source) != set(target) or source["id"] != target["id"]:
        raise ValueError("Changed keys or id")
    for key in FIELDS:
        if key not in source:
            continue
        a, b = source[key], target[key]
        if isinstance(a, list):
            if not isinstance(b, list) or len(a) != len(b) or not all(isinstance(x, str) and x.strip() for x in b):
                raise ValueError(f"Invalid list: {key}")
        elif not isinstance(b, str) or not b.strip():
            raise ValueError(f"Invalid text: {key}")
        if "\u2014" in json.dumps(b, ensure_ascii=False):
            raise ValueError("Em dash in translation")


def parse_response(content):
    content = content.strip()
    if content.startswith('```'):
        content = content.split('\n', 1)[1].rsplit('```', 1)[0].strip()
    try:
        result, end = json.JSONDecoder().raw_decode(content)
    except json.JSONDecodeError as exc:
        # Accept only this observed redundant terminal brace, never repair text inside an item.
        if content.endswith('}}]}') and exc.pos == len(content) - 3:
            return json.loads(content[:-4] + '}]}')
        raise
    # Some compatible gateways leak the final-channel closing delimiter.
    if content[end:].strip() not in ('', '</final>', '</final'):
        raise json.JSONDecodeError('Unexpected text after JSON', content, end)
    return result
