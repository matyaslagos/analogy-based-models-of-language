#!/usr/bin/env python3
"""Extract label inventory from Kainoki treebank files and compare to overview tags."""

from __future__ import annotations

import argparse
import re
from collections import Counter
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable


TABLE_HEADER_TO_SECTION = {
    "Table 1.1:": "Word class tags",
    "Table 1.2:": "Phrase layer tags",
    "Table 1.3:": "Clause layer tags",
    "Table 1.4:": "Function tags",
    "Table 1.5:": "Other tags",
}

TOKEN_RE = re.compile(r"\(|\)|[^\s()]+")


@dataclass(frozen=True)
class LabelInfo:
    label: str
    count: int
    leaf_count: int
    meaning: str
    notes: str


def extract_labels(treebank_dir: Path) -> tuple[Counter[str], Counter[str]]:
    label_counts: Counter[str] = Counter()
    leaf_counts: Counter[str] = Counter()

    for path in sorted(treebank_dir.iterdir()):
        if not path.is_file():
            continue

        tokens = TOKEN_RE.findall(path.read_text(encoding="utf-8"))
        for i in range(len(tokens) - 1):
            if tokens[i] == "(" and tokens[i + 1] not in {"(", ")"}:
                label = tokens[i + 1]
                label_counts[label] += 1
                if i + 2 < len(tokens) and tokens[i + 2] != "(":
                    leaf_counts[label] += 1

    return label_counts, leaf_counts


def parse_overview_tables(overview_path: Path) -> tuple[dict[str, str], dict[str, str], dict[str, str]]:
    """Return mappings: tag->meaning, tag->section, function_without_dash->meaning."""

    lines = overview_path.read_text(encoding="utf-8").splitlines()
    tag_meanings: dict[str, str] = {}
    tag_sections: dict[str, str] = {}
    function_meanings: dict[str, str] = {}

    current_section = ""
    collecting = False

    for raw_line in lines:
        line = raw_line.strip()

        matched_header = next((h for h in TABLE_HEADER_TO_SECTION if line.startswith(h)), None)
        if matched_header:
            current_section = TABLE_HEADER_TO_SECTION[matched_header]
            collecting = True
            continue

        if collecting and line.startswith("Table 1."):
            matched_header = next((h for h in TABLE_HEADER_TO_SECTION if line.startswith(h)), None)
            if matched_header:
                current_section = TABLE_HEADER_TO_SECTION[matched_header]
            continue

        if collecting and re.match(r"^\d+\.\d+", line):
            break

        if not collecting or not line:
            continue

        parts = line.split(None, 1)
        if not parts:
            continue

        tag = parts[0]
        meaning = parts[1].strip() if len(parts) > 1 else ""

        # Skip non-table prose if any appears inside parsed region.
        if tag in {"adoption", "not", "the", "and", "or"}:
            continue

        tag_meanings[tag] = meaning
        tag_sections[tag] = current_section

        if current_section == "Function tags" and tag.startswith("-"):
            function_meanings[tag[1:]] = meaning

    return tag_meanings, tag_sections, function_meanings


def compose_meaning(
    label: str,
    tag_meanings: dict[str, str],
    function_meanings: dict[str, str],
    non_function_tags: set[str],
) -> tuple[str, str, bool, bool]:
    """Return meaning, notes, is_compositional, is_documented_exact."""

    sort_suffix = ""
    core_label = label
    if ";" in label:
        core_label, sort_suffix = label.split(";", 1)

    if label in tag_meanings:
        meaning = tag_meanings[label]
        notes = ""
        if sort_suffix:
            notes = f"Sort/reference annotation `;{sort_suffix}`"
        return meaning, notes, False, True

    base_candidates = [
        t for t in non_function_tags if core_label == t or core_label.startswith(t + "-")
    ]
    base_tag = max(base_candidates, key=len) if base_candidates else ""

    suffix_parts: list[str] = []
    unknown_parts: list[str] = []

    if base_tag:
        remainder = core_label[len(base_tag) :]
        if remainder.startswith("-"):
            suffix_parts = [p for p in remainder[1:].split("-") if p]

    if base_tag and base_tag in tag_meanings:
        meaning_parts = [tag_meanings[base_tag]]
        notes_list: list[str] = []

        for part in suffix_parts:
            if part in function_meanings:
                meaning_parts.append(function_meanings[part])
            elif part.isdigit():
                notes_list.append(f"Coindexation suffix `-{part}`")
            else:
                unknown_parts.append(part)

        if sort_suffix:
            notes_list.append(f"Sort/reference annotation `;{sort_suffix}`")

        if unknown_parts:
            notes_list.append(
                "Undocumented extension part(s): "
                + ", ".join(f"`-{p}`" for p in unknown_parts)
            )

        is_compositional = bool(suffix_parts or sort_suffix)
        notes = "; ".join(notes_list)
        return " + ".join(meaning_parts), notes, is_compositional, False

    notes = []
    if sort_suffix:
        notes.append(f"Sort/reference annotation `;{sort_suffix}`")
    notes.append("No direct mapping in overview tables")
    return "(not documented in overview)", "; ".join(notes), False, False


def classify_missing_labels(
    labels: Iterable[str],
    tag_meanings: dict[str, str],
    function_meanings: dict[str, str],
    non_function_tags: set[str],
) -> tuple[list[str], list[str], list[str]]:
    compositional: list[str] = []
    sort_annotated: list[str] = []
    undocumented: list[str] = []

    for label in sorted(labels):
        core = label.split(";", 1)[0]

        base_candidates = [
            t for t in non_function_tags if core == t or core.startswith(t + "-")
        ]
        base_tag = max(base_candidates, key=len) if base_candidates else ""

        if ";" in label:
            sort_annotated.append(label)
            continue

        if base_tag:
            remainder = core[len(base_tag) :]
            suffixes = [p for p in remainder[1:].split("-") if p] if remainder.startswith("-") else []
            if suffixes and all(s in function_meanings or s.isdigit() for s in suffixes):
                compositional.append(label)
                continue

        undocumented.append(label)

    return compositional, sort_annotated, undocumented


def write_markdown_report(
    output_path: Path,
    label_counts: Counter[str],
    leaf_counts: Counter[str],
    tag_meanings: dict[str, str],
    tag_sections: dict[str, str],
    function_meanings: dict[str, str],
) -> None:
    non_function_tags = {tag for tag in tag_meanings if not tag.startswith("-")}

    overview_tags = set(tag_meanings)
    extracted_tags = set(label_counts)
    missing_from_overview = extracted_tags - overview_tags
    missing_from_treebank = overview_tags - extracted_tags

    compositional_missing, sort_annotated_missing, undocumented_missing = classify_missing_labels(
        missing_from_overview, tag_meanings, function_meanings, non_function_tags
    )

    lines: list[str] = []
    lines.append("# Kainoki Treebank Labels (Extracted from `treebank_files`)")
    lines.append("")
    lines.append(
        f"Extracted **{len(extracted_tags)}** unique labels from the five treebank files."
    )
    lines.append(
        f"Overview tables list **{len(overview_tags)}** unique tags (word/phrase/clause/function/other)."
    )
    lines.append("")

    lines.append("## Differences from `kainoki_treebank_annotation_overview.md`")
    lines.append("")
    lines.append(
        f"- Labels present in treebank but not listed as exact tags in the overview: **{len(missing_from_overview)}**"
    )
    lines.append(
        f"- Overview tags not attested in these five files: **{len(missing_from_treebank)}**"
    )
    lines.append(
        f"- Compositional combinations of documented tags/functions: **{len(compositional_missing)}**"
    )
    lines.append(f"- Sort/reference-annotated labels (`;...`): **{len(sort_annotated_missing)}**")
    lines.append(f"- Undocumented/non-compositional labels: **{len(undocumented_missing)}**")
    lines.append("")

    if compositional_missing:
        lines.append("### Compositional combinations (not listed as standalone rows)")
        lines.append("")
        lines.append(", ".join(f"`{x}`" for x in compositional_missing))
        lines.append("")

    if sort_annotated_missing:
        lines.append("### Sort/reference-annotated labels")
        lines.append("")
        lines.append(", ".join(f"`{x}`" for x in sort_annotated_missing))
        lines.append("")

    if undocumented_missing:
        lines.append("### Undocumented/non-compositional labels")
        lines.append("")
        lines.append(", ".join(f"`{x}`" for x in undocumented_missing))
        lines.append("")

    if missing_from_treebank:
        lines.append("### Overview tags not attested in this sample")
        lines.append("")
        lines.append(", ".join(f"`{x}`" for x in sorted(missing_from_treebank)))
        lines.append("")

    leaf_labels = sorted(label for label, c in leaf_counts.items() if c > 0)
    lines.append("## Leaf-Level Labels")
    lines.append("")
    lines.append(
        "Labels that directly dominate token leaves at least once in the extracted files:"
    )
    lines.append("")
    lines.append(", ".join(f"`{x}`" for x in leaf_labels))
    lines.append("")

    lines.append("## Extracted Labels and Meanings")
    lines.append("")
    lines.append("| Label | Count | Leaf label count | Meaning | Notes |")
    lines.append("|---|---:|---:|---|---|")

    for label in sorted(extracted_tags):
        meaning, notes, _, is_exact = compose_meaning(
            label, tag_meanings, function_meanings, non_function_tags
        )

        if is_exact and label in tag_sections:
            notes = f"Documented in overview ({tag_sections[label]})"

        lines.append(
            "| "
            + " | ".join(
                [
                    f"`{label}`",
                    str(label_counts[label]),
                    str(leaf_counts.get(label, 0)),
                    meaning.replace("|", "\\|"),
                    notes.replace("|", "\\|") if notes else "",
                ]
            )
            + " |"
        )

    output_path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Extract labels from Kainoki treebank files and produce a markdown report."
    )
    parser.add_argument(
        "--treebank-dir",
        default="treebank_files",
        type=Path,
        help="Directory containing treebank files (default: treebank_files)",
    )
    parser.add_argument(
        "--overview",
        default="kainoki_treebank_annotation_overview.md",
        type=Path,
        help="Path to annotation overview markdown file",
    )
    parser.add_argument(
        "--output",
        default="kainoki_treebank_labels.md",
        type=Path,
        help="Output markdown report path",
    )
    return parser.parse_args()


def main() -> None:
    args = parse_args()

    label_counts, leaf_counts = extract_labels(args.treebank_dir)
    tag_meanings, tag_sections, function_meanings = parse_overview_tables(args.overview)

    write_markdown_report(
        output_path=args.output,
        label_counts=label_counts,
        leaf_counts=leaf_counts,
        tag_meanings=tag_meanings,
        tag_sections=tag_sections,
        function_meanings=function_meanings,
    )


if __name__ == "__main__":
    main()
