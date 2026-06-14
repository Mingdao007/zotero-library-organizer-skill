---
name: zotero-library-organizer
description: Organize, deduplicate, classify, and normalize a local Zotero library by editing `zotero.sqlite` safely. Use when the user asks to sort new Zotero items into collections, clean duplicate entries, inspect `Unfiled Items`, normalize collection names, consolidate collection trees, or apply the the user force-control library taxonomy without touching protected folders unless explicitly requested.
---

# Zotero Library Organizer

## Purpose

Use this skill to safely inspect and organize a local Zotero library, including
collections, duplicate candidates, unfiled items, and force-control taxonomy
maintenance. Treat direct `zotero.sqlite` edits as mutation-gated work.

Keep this `SKILL.md` as a concise routing and execution entrypoint. Do not load
long examples, command catalogs, detailed checklists, or edge-case policy until
the current task needs them.

## Workflow

1. Confirm the user request matches this skill's frontmatter description.
2. Bind the concrete target: source file, artifact, repo, device, document,
   dataset, or user-facing deliverable.
3. Use the smallest relevant workflow from this entrypoint first.
4. Before database mutation, taxonomy application, duplicate cleanup, or
   protected-folder handling, read `references/entrypoint-details.md`.
5. Preserve local owner boundaries: route to a narrower skill or repo-specific
   workflow when the detailed reference indicates a more specific owner.

## Detailed Reference

Read `references/entrypoint-details.md` for:

- Overview
- Trigger Conditions
- Canonical Workflow
- Current Library Policy
- Current Collection Rules
- Classification Rules For New Items
- Duplicate Handling Protocol
- Unfiled Items Rule
- Tools
- Reporting Back To The User

## Validation

- Use the skill-specific validation or acceptance checks from the detailed
  reference before declaring completion.
- When editing this skill, run `quick_validate.py` on the skill directory and
  verify all referenced files still exist.
