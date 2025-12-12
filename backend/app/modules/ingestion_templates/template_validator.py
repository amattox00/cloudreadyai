from __future__ import annotations

import csv
import json
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List, Optional

# Templates live in: app/modules/ingestion_templates/templates/*.template.json
TEMPLATE_DIR = Path(__file__).resolve().parent / "templates"


@dataclass
class TemplateValidationResult:
    slice: str
    valid: bool
    missing_required: List[str]
    missing_optional: List[str]
    unknown_columns: List[str]
    used_aliases: Dict[str, str]          # alias_used -> canonical
    header_renames: Dict[str, str]        # current_header -> canonical_header
    warnings: List[str]
    blockers: List[str]


def _norm(h: Optional[str]) -> str:
    return (h or "").strip()


def load_template(slice_name: str) -> Dict[str, Any]:
    path = TEMPLATE_DIR / f"{slice_name}.template.json"
    if not path.exists():
        raise FileNotFoundError(f"Template not found: {path}")
    return json.loads(path.read_text(encoding="utf-8"))


def validate_headers(*, slice_name: str, headers: List[str]) -> TemplateValidationResult:
    tpl = load_template(slice_name)
    required = [str(x) for x in tpl.get("required_headers", [])]
    optional = [str(x) for x in tpl.get("optional_headers", [])]
    aliases: Dict[str, str] = {str(k): str(v) for k, v in (tpl.get("header_aliases", {}) or {}).items()}

    policy = tpl.get("policy", {}) or {}
    unknown_policy = str(policy.get("unknown_columns", "warn")).lower()
    missing_optional_policy = str(policy.get("missing_optional", "warn")).lower()
    missing_required_policy = str(policy.get("missing_required", "block")).lower()

    raw_headers = [_norm(h) for h in headers if _norm(h)]
    header_set = set(raw_headers)

    # Track alias usage and plan renames (only when canonical not already present)
    used_aliases: Dict[str, str] = {}
    header_renames: Dict[str, str] = {}

    for h in list(raw_headers):
        if h in aliases:
            canonical = aliases[h]
            if canonical not in header_set:
                used_aliases[h] = canonical
                header_renames[h] = canonical

    # Determine which canonical headers are present (either directly or via alias)
    def is_present(canonical: str) -> bool:
        if canonical in header_set:
            return True
        for a, c in aliases.items():
            if c == canonical and a in header_set:
                return True
        return False

    missing_required = [h for h in required if not is_present(h)]
    missing_optional = [h for h in optional if not is_present(h)]

    allowed = set(required + optional)
    # Unknown columns: anything not in allowed, and not an alias we understand
    unknown_columns = [h for h in raw_headers if (h not in allowed and h not in aliases)]

    warnings: List[str] = []
    blockers: List[str] = []

    if used_aliases:
        warnings.append(
            "CSV uses non-standard header names (aliases). We can normalize them, but the template should be used for best results."
        )
        for a, c in used_aliases.items():
            warnings.append(f"Header alias detected: '{a}' → '{c}'")

    if unknown_columns:
        msg = f"Unknown columns detected: {', '.join(unknown_columns)}"
        if unknown_policy == "block":
            blockers.append(msg)
        else:
            warnings.append(msg)

    if missing_optional:
        msg = f"Missing optional columns: {', '.join(missing_optional)}"
        if missing_optional_policy == "block":
            blockers.append(msg)
        else:
            warnings.append(msg)

    if missing_required:
        msg = f"Missing required columns: {', '.join(missing_required)}"
        if missing_required_policy == "warn":
            warnings.append(msg)
        else:
            blockers.append(msg)

    valid = len(blockers) == 0

    return TemplateValidationResult(
        slice=slice_name,
        valid=valid,
        missing_required=missing_required,
        missing_optional=missing_optional,
        unknown_columns=unknown_columns,
        used_aliases=used_aliases,
        header_renames=header_renames,
        warnings=warnings,
        blockers=blockers,
    )


def normalize_csv_headers(
    *,
    csv_path: str,
    header_renames: Dict[str, str],
    output_path: Optional[str] = None,
) -> str:
    """
    Rewrite the CSV to use canonical headers when we detect known aliases.
    Returns path to normalized CSV (may be same as input if no renames).
    """
    if not header_renames:
        return csv_path

    in_path = Path(csv_path)
    out_path = Path(output_path) if output_path else Path(f"{csv_path}.normalized")

    with in_path.open("r", newline="", encoding="utf-8", errors="ignore") as fin:
        reader = csv.DictReader(fin)
        if not reader.fieldnames:
            raise ValueError("CSV appears to have no header row.")

        original_headers = [h.strip() for h in reader.fieldnames if h and h.strip()]
        new_headers: List[str] = []
        seen = set()

        # Rename any alias header to canonical; keep order
        for h in original_headers:
            nh = header_renames.get(h, h)
            if nh in seen:
                continue
            new_headers.append(nh)
            seen.add(nh)

        with out_path.open("w", newline="", encoding="utf-8") as fout:
            writer = csv.DictWriter(fout, fieldnames=new_headers)
            writer.writeheader()

            for row in reader:
                if not row:
                    continue
                out_row: Dict[str, Any] = {}
                for k, v in row.items():
                    if k is None:
                        continue
                    key = k.strip()
                    if not key:
                        continue
                    nk = header_renames.get(key, key)
                    if nk not in seen:
                        continue
                    if nk in out_row:
                        continue
                    out_row[nk] = v
                writer.writerow(out_row)

    return str(out_path)
