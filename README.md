# Zotero Library Organizer Skill

Portable Zotero library-maintenance skill for audit-first organization, duplicate analysis, and safe direct SQLite workflows.

## What Ships

- installable skill: [`zotero-library-organizer`](./zotero-library-organizer)
- bundled public references: [`zotero-library-organizer/references/`](./zotero-library-organizer/references)
- bundled helper scripts: [`zotero-library-organizer/scripts/`](./zotero-library-organizer/scripts)

## Install / Use

- `Codex App`: install the skill from this repo path `zotero-library-organizer`
- GitHub install target:
  - repo: `<owner>/zotero-library-organizer-skill`
  - path: `zotero-library-organizer`
- Restart `Codex App` after installation so the new skill is discovered.

## Coverage

- audit-first workflow before direct database writes
- duplicate and unfiled-item analysis from a copied SQLite snapshot
- backup-before-write guidance for deterministic library maintenance

## Trigger Examples

- `Audit this Zotero library before cleanup.`
- `Find duplicates and unfiled items safely.`
- `Plan a deterministic Zotero collection reorganization.`

## Non-Trigger Examples

- `Only locate one local PDF attachment.`
- `Debug a Zotero MCP startup issue.`
- `Do a literature review without library edits.`

## Privacy Boundary

This public repository keeps the workflow generic and reusable.

- User-specific taxonomy wording is rewritten into generic policy wording where needed.
- Database defaults use host-relative paths or environment overrides instead of private absolute paths.

## Repository Layout

- `zotero-library-organizer/`: installable `Codex App` skill
- `zotero-library-organizer/references/`: bundled public references
- `zotero-library-organizer/scripts/`: bundled public scripts
- `CHANGELOG.md`: release history
- `LICENSE`: `MIT`

Chinese:

- [README.zh-CN.md](./README.zh-CN.md)
