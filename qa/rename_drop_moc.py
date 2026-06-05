#!/usr/bin/env python3
"""rename_drop_moc.py — One-time migration: drop the " MOC" suffix from hub files.

The hub/index pages were historically named "{Subject} MOC", "{Institution} MOC",
"{Institution} Analys MOC" and "Ej Aktiv {Subject} MOC". Staff found the "MOC"
jargon confusing, so we rename them to plain names ("Svenska", "IIT",
"IIT Analys", "Ej Aktiv Svenska") and rewrite every reference.

This only touches *display* — the `MOC` frontmatter tag is kept untouched as
internal plumbing for the graph colouring and QA pipeline.

What it does:
  1. Discovers every "* MOC.md" file → builds an old→new name map (strip trailing
     " MOC").
  2. Rewrites all references across the vault:
       [[Old]]        -> [[New]]
       [[Old|disp]]   -> [[New|disp]]
       "Old"          -> "New"        (non-bracketed up: values)
  3. In each hub file, rewrites its own "# Old" H1 to "# New" and drops a now-
     redundant self-alias.
  4. Renames the files last.

Run --dry-run first to preview. --apply to write.
"""
from __future__ import annotations

import argparse
from pathlib import Path

VAULT = Path(__file__).resolve().parent.parent / "vault-dalarna-university"
SUFFIX = " MOC"


def build_map(vault: Path) -> dict[str, str]:
    """old stem -> new stem for every '* MOC.md' hub file."""
    mapping: dict[str, str] = {}
    for md in vault.rglob("*MOC*.md"):
        stem = md.stem
        if stem.endswith(SUFFIX):
            mapping[stem] = stem[: -len(SUFFIX)]
    return mapping


def rewrite_refs(text: str, mapping: dict[str, str]) -> tuple[str, int]:
    """Replace link/up references. Returns (new_text, num_replacements)."""
    n = 0
    # Longest old names first so no shorter name is a prefix-substring of another.
    for old in sorted(mapping, key=len, reverse=True):
        new = mapping[old]
        for a, b in (
            (f"[[{old}]]", f"[[{new}]]"),
            (f"[[{old}|", f"[[{new}|"),
            (f"[[{old}#", f"[[{new}#"),
            (f'"{old}"', f'"{new}"'),
        ):
            if a in text:
                n += text.count(a)
                text = text.replace(a, b)
    return text, n


def fix_hub_self(text: str, old: str, new: str) -> str:
    """Inside a hub file, rewrite its own H1 and drop a redundant self-alias."""
    text = text.replace(f"# {old}\n", f"# {new}\n", 1)
    # aliases: [New]  becomes redundant once the file *is* New — drop that exact alias.
    text = text.replace(f"aliases: [{new}]\n", "aliases: []\n")
    return text


def main() -> None:
    ap = argparse.ArgumentParser()
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--dry-run", action="store_true")
    g.add_argument("--apply", action="store_true")
    args = ap.parse_args()

    mapping = build_map(VAULT)
    print(f"Hub files to rename: {len(mapping)}")

    files_changed = 0
    total_refs = 0
    renames: list[tuple[Path, Path]] = []

    for md in VAULT.rglob("*.md"):
        text = original = md.read_text(encoding="utf-8")
        text, n = rewrite_refs(text, mapping)
        if md.stem in mapping:
            text = fix_hub_self(text, md.stem, mapping[md.stem])
            renames.append((md, md.with_name(mapping[md.stem] + ".md")))
        if text != original:
            files_changed += 1
            total_refs += n
            if args.apply:
                md.write_text(text, encoding="utf-8")

    # Rename hub files last (after their content is rewritten).
    collisions = [dst for _, dst in renames if dst.exists() and dst not in {s for s, _ in renames}]
    if collisions:
        print("\n⚠️  Name collisions — aborting before rename:")
        for c in collisions:
            print(f"   {c}")
        return

    for src, dst in renames:
        if args.apply:
            src.rename(dst)

    print(f"Files with rewritten references: {files_changed}")
    print(f"Total references rewritten:      {total_refs}")
    print(f"Hub files renamed:               {len(renames)}")
    if args.dry_run:
        print("\n(dry-run — nothing written. Re-run with --apply to commit changes.)")
        print("\nSample renames:")
        for src, dst in renames[:8]:
            print(f"   {src.name}  ->  {dst.name}")


if __name__ == "__main__":
    main()
