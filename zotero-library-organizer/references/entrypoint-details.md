# Zotero Library Organizer Entrypoint Details

Extracted from the former over-200-line `SKILL.md` so the entrypoint stays concise. Load this file only when the current task needs the detailed workflow, examples, command recipes, or edge-case policy.

## Contents

- Overview
- Trigger Conditions
- Canonical Workflow
  - 1. Audit First
  - 2. Backup Before Writes
  - 3. Write Safely
  - 4. Verify After Writes
  - 5. Sync And Cross-Device Verification After Direct DB Writes
  - 6. Run Integrity Checks After Collection Deletions
- Current Library Policy
- Current Collection Rules
  - Protected By Default
  - Current Top-Level Research Collections
  - Current Subcollections
  - Naming Convention
- Classification Rules For New Items
  - Main Decision
  - Cross-Filing Rule
  - Non-Robot Papers
- Duplicate Handling Protocol
  - Safe Automatic Merge
  - Manual Review Required
  - Duplicate Items Panel Cleanup Rule
- Unfiled Items Rule
- Tools
  - Direct SQLite
  - Python
  - PDF Extraction
- Reporting Back To The User

# Zotero Library Organizer

## Overview

Use this skill for direct Zotero library maintenance on the local machine.
It is optimized for the user's current library structure and the workflow established in this session:

- edit `~/Zotero/zotero.sqlite` directly with SQLite
- always backup before write operations
- verify after changes, then remove the temporary backup
- preserve `Courses` and `Robot Scenarios` unless the user explicitly asks otherwise
- allow cross-filing, but keep it limited and intentional
- verify cloud sync after direct DB edits when cross-device consistency matters

## Trigger Conditions

Use this skill when the user asks to:

- organize new Zotero papers or attachments into collections
- clean duplicate Zotero items
- inspect or clear `Unfiled Items`
- normalize collection names
- merge or simplify Zotero folders
- place new robot papers into the current force-control taxonomy
- audit the current library before making changes

Route these requests to other workflows:

- Zotero MCP transport/debugging only
  Use `zotero-mcp-repair` instead.
- generic literature review or paper explanation with no library edits

## Canonical Workflow

### 1. Audit First

Before any write:

1. Check whether the Zotero process is still running.
2. Treat a closed window as insufficient evidence that the app is fully closed.
3. On this user's setup, window-close is not enough and plugin-related quit hangs can leave `zotero.sqlite` locked.
4. If Zotero is running, switch to a read-only or copied snapshot for diagnosis.
5. Audit the relevant part of the library first:
   - collection tree
   - duplicate candidates
   - unfiled items
   - attachment paths

Practical check:

```bash
pgrep -fl '/Applications/Zotero.app/Contents/MacOS/zotero' || true
```

Preferred helper:

```bash
python3 $CODEX_HOME/skills/zotero-library-organizer/scripts/zotero_audit.py summary
python3 $CODEX_HOME/skills/zotero-library-organizer/scripts/zotero_audit.py unfiled
python3 $CODEX_HOME/skills/zotero-library-organizer/scripts/zotero_audit.py duplicates
python3 $CODEX_HOME/skills/zotero-library-organizer/scripts/zotero_audit.py integrity
```

### 2. Backup Before Writes

Before any change to `~/Zotero/zotero.sqlite`, create a timestamped backup in the same directory.

After the write:

1. verify the intended result
2. remove only the backup created for the current operation
3. preserve older `.bak` files unless the user explicitly asks to remove them

### 3. Write Safely

Use direct SQLite updates for deterministic collection edits.

Typical write operations:

- rename collections
- create collections/subcollections
- add items to collections
- move duplicate items to `deletedItems`
- create or remove collection memberships

Constraints:

- keep files in `~/Zotero/storage` in place and manage organization through Zotero metadata
- treat collection membership as placement metadata, not as a file copy
- require manual review for ambiguous version pairs
- preserve both proof/final items when both carry value
- modify `Courses` or `Robot Scenarios` only when the user explicitly requests it

### 4. Verify After Writes

Always verify:

- target collections exist
- item memberships changed as intended
- duplicate/trash state is correct
- no orphan `collectionItems` remain
- temporary backup for this operation is removed

### 5. Sync And Cross-Device Verification After Direct DB Writes

Direct edits to `zotero.sqlite` are local database edits, not supported object-level Zotero writes.
Normal sync may or may not pick them up reliably.

After local verification:

1. Reopen Zotero.
2. Run one ordinary sync first.
3. Verify in three places when the user cares about cloud consistency:
   - local Zotero app
   - Zotero Web Library
   - another Zotero device
4. Distinguish metadata sync from file sync:
   - collection tree, item placement, notes, tags: Zotero data sync
   - PDFs and snapshots: file sync / WebDAV
5. Judge collection structure from the Zotero data model rather than WebDAV folders.
   WebDAV only tells you whether attachments exist.
6. If ordinary sync does not propagate the DB-level edits, use:
   - `Sync -> Reset -> Replace Online Library`

This is a fallback, not the default first action.

### 6. Run Integrity Checks After Collection Deletions

Deleting old collections can leave orphan membership rows in `collectionItems`.
These orphans can trigger Zotero UI errors such as:

- `Collection <id> not found for item ...`

After any structural cleanup, run:

```bash
python3 $CODEX_HOME/skills/zotero-library-organizer/scripts/zotero_audit.py integrity
```

If orphan memberships exist, fix them only after a fresh backup.
The practical repair is:

```sql
DELETE FROM collectionItems
WHERE collectionID NOT IN (SELECT collectionID FROM collections);
```

Then verify again before reopening Zotero.

## Current Library Policy

Read:

- `references/library-policy.md`

This file contains:

- protected folders
- current top-level taxonomy
- current subcollection taxonomy
- naming conventions
- routing rules for new items
- duplicate-handling policy
- how to interpret `Unfiled Items`

## Current Collection Rules

### Protected By Default

Restructure these only when the user explicitly asks:

- `Courses`
- `Robot Scenarios`

### Current Top-Level Research Collections

Outside `Courses` and `Robot Scenarios`, the canonical top level is:

- `Impedance control`
- `Friction model`
- `Learning-based control`
- `Geometry and planning`
- `Resources and tools`

`Unread short` has been removed and should not be recreated.

### Current Subcollections

Use only these subcollections unless the user explicitly wants a taxonomy change:

- `Impedance control / Foundations and surveys`
- `Impedance control / Force-impedance formulations`
- `Impedance control / Variable impedance and compliance`
- `Friction model / Friction modeling`
- `Friction model / Force estimation and compensation`
- `Learning-based control / Policy learning`
- `Learning-based control / Adaptation and meta-learning`
- `Learning-based control / Physics-guided learning`
- `Learning-based control / World models and foundation models`
- `Geometry and planning / Lie groups and rotation`
- `Geometry and planning / Constraint and null-space`
- `Geometry and planning / Motion planning`
- `Resources and tools / Textbooks and notes`
- `Resources and tools / Repos and code`
- `Resources and tools / Software and reference docs`

### Naming Convention

Collection names follow this normalization rule:

- capitalize the first word only

Examples:

- `Impedance control`
- `Learning-based control`
- `Session 9`

Keep this capitalization rule by default and switch to Title Case only when the user asks for a different rule.

## Classification Rules For New Items

### Main Decision

For a new item, classify in this order:

1. Is it a course material?
   Put it in the matching `Courses` branch.
2. Is it a robot application/scenario paper?
   Optionally add it to one `Robot Scenarios` subcollection.
3. Assign one main research collection and one subcollection.

### Cross-Filing Rule

Cross-filing is allowed, but keep it bounded:

- prefer `1` main collection
- optionally `1` subcollection under that main collection
- optionally `1` `Robot Scenarios` placement

Keep each paper's cross-filing bounded to the placements above instead of spreading it across many narrowly overlapping collections.

### Non-Robot Papers

If the item is not about robotics or not part of the active research taxonomy:

- place it in `Resources and tools / Textbooks and notes`
- or leave it in a course collection if it is course-specific

## Duplicate Handling Protocol

### Safe Automatic Merge

You may auto-resolve when all important evidence agrees, for example:

- same DOI
- same title
- same attachment hash
- no conflicting notes/annotations
- or only trivial differences such as download watermark timestamps

### Manual Review Required

Require user confirmation when any of these are true:

- preprint vs conference/journal version
- proof vs final published version
- same title but different extracted text
- same DOI but clearly different document role
- one copy has annotations and the other does not
- attachment set differs meaningfully

When presenting manual-review candidates, identify each candidate with the full fields below.
Always include:

- title
- attachment filename
- absolute local path
- Zotero collection path
- item key

If the user asks where to click inside Zotero, default to the Zotero collection path.
Add the filesystem path only when the user needs the local file itself.

### Duplicate Items Panel Cleanup Rule

The Zotero `Duplicate Items` panel is heuristic.
It can keep showing candidates that are not true byte-for-byte duplicates.

Common patterns in this library:

- proof vs final journal item
- preprint vs conference/journal item
- course note accidentally imported as a `book` with inherited book metadata

If the user explicitly wants the `Duplicate Items` panel empty:

1. Keep one canonical parent item.
2. Reparent useful child objects from the other candidate under the kept parent:
   - PDF
   - HTML snapshot
   - note
   - annotations attached to the moved child attachment
3. Move the redundant parent item to `deletedItems`.
4. Re-check duplicates and integrity.

Special case:

- for a course handout falsely matching a real book, convert it to a non-book item type such as `document`
- strip inherited book metadata such as `ISBN`, `DOI`, `URL`, publisher metadata, and book creators if they are no longer semantically correct
- then re-check the panel

## Unfiled Items Rule

Treat `Unfiled Items` as potentially including both of these cases:

- top-level parent items with no collection membership
- standalone attachments with no collection membership

So audit both:

1. top-level items without any `collectionItems` row
2. standalone attachments where `parentItemID IS NULL` and no collection membership

If a standalone attachment is an exact duplicate of a filed attachment and has no notes/annotations, it can usually be moved to Trash.
If it is a real course artifact, file it into the relevant `Courses` branch instead.

Typical real examples from this library:

- duplicate standalone course PDFs that already exist inside a course branch: move the standalone copy to Trash
- genuine standalone course artifacts such as a PPTX or mini-project brief: add them to the relevant `Courses` branch

## Tools

### Direct SQLite

Primary mechanism for deterministic edits:

- `sqlite3 ~/Zotero/zotero.sqlite`

Use for:

- collection creation/deletion
- collection membership edits
- duplicate trashing
- quick audits
- child attachment reparenting
- metadata cleanup for duplicate-panel false positives

### Python

Use Python when the logic is easier to express safely than raw SQL:

- copying a locked DB snapshot
- hashing attachments
- reading PDF metadata/text
- generating multi-step audit reports

### PDF Extraction

Use `pypdf` when content comparison matters.

This is especially useful for:

- deciding whether two PDFs are truly duplicates
- distinguishing preprint vs final
- spotting proof copies

## Reporting Back To The User

Keep the report short and concrete.
When applicable, include:

- what was changed
- what was intentionally not changed
- what still needs manual confirmation
- whether cloud verification is still pending
- whether the temporary backup was removed

Keep the close direct and concrete, and skip filler closers or repeated offer-style transitions.
