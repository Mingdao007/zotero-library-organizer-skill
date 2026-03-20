# Zotero Library Policy

This file captures the current the user Zotero organization policy established on 2026-03-07.

## Protected Areas

Do not restructure by default:

- `Courses`
- `Robot Scenarios`

You may add new items into them when classification requires it.

## Current Research Top Level

- `Impedance control`
- `Friction model`
- `Learning-based control`
- `Geometry and planning`
- `Resources and tools`

## Current Subcollections

### Impedance control

- `Foundations and surveys`
- `Force-impedance formulations`
- `Variable impedance and compliance`

### Friction model

- `Friction modeling`
- `Force estimation and compensation`

### Learning-based control

- `Policy learning`
- `Adaptation and meta-learning`
- `Physics-guided learning`
- `World models and foundation models`

### Geometry and planning

- `Lie groups and rotation`
- `Constraint and null-space`
- `Motion planning`

### Resources and tools

- `Textbooks and notes`
- `Repos and code`
- `Software and reference docs`

## Robot Scenarios

This branch is allowed to cross-file with research collections.

Keep these scenario subcollections:

- `Aerial Robots and Quadrotors`
- `Assembly and Insertion`
- `Contact-Rich Manipulation`
- `Generic Manipulator Control`
- `Grasping and Dexterous Manipulation`
- `Grinding and Surface Processing`
- `Household and Service Tasks`
- `Locomotion and Legged Robots`
- `Teleoperation and Haptics`

Only robot-related items should enter this branch.

## Naming Rule

Collection naming rule:

- first word capitalized

Examples:

- `Impedance control`
- `Learning-based control`
- `Session 9`

## Routing Heuristics

### Impedance control

Use for:

- force control
- force-impedance formulations
- impedance/compliance
- variable impedance
- force tracking
- interaction control

### Friction model

Use for:

- friction modeling
- disturbance/friction estimation
- force estimation related to friction compensation

### Learning-based control

Use for:

- policy learning
- meta-learning
- adaptation
- diffusion policy
- VLA/foundation/world-model topics
- physics-guided learning for control

### Geometry and planning

Use for:

- Lie groups
- rotation representation
- null-space methods
- control barrier functions
- motion planning
- constraint manifold planning

### Resources and tools

Use for:

- textbooks
- notes
- repos
- software docs
- non-robot methods references
- miscellaneous references not part of the main research taxonomy

## Unfiled Items Interpretation

In this library, `Unfiled Items` may come from:

- top-level parent items with no collection
- standalone attachments with no collection

Not all `Unfiled Items` are papers.

## Duplicates Policy

### Auto-resolve candidates

Usually safe when:

- same DOI
- same title
- same attachment hash
- no important notes/annotations
- or only download watermark differences

### Manual review candidates

Always review with the user when:

- preprint vs final
- proof vs final
- same DOI but different role
- one copy has annotations
- attachment sets differ

### Duplicate Panel Cleanup Policy

The Zotero `Duplicate Items` panel is heuristic, not authoritative.
In this library, false positives came from two recurrent patterns:

- version pairs such as `preprint` vs `conferencePaper` or `proof` vs final journal item
- course materials polluted by imported `book` metadata

If the user wants the panel itself to become empty, use these rules:

- proof vs final:
  keep the final published parent item by default
- preprint vs conference/journal:
  keep the formal publication parent item by default
- then reparent useful child objects from the discarded parent under the kept parent:
  - PDF
  - HTML snapshot
  - note
  - existing annotations on the moved child attachment
- finally move the redundant parent item to Trash

For course materials falsely detected as duplicate books:

- convert the course material to `document` unless the user explicitly wants another type
- keep only semantically correct fields such as the course-note title
- remove inherited book metadata such as:
  - `ISBN`
  - `DOI`
  - `URL`
  - publisher metadata
  - series metadata
  - imported book creators

## Reporting Format For Manual Review

Always report:

- title
- attachment filename
- absolute local path
- Zotero collection path
- item key

Do not report key alone.

## Process Exit Caveat

On this user's machines, closing the Zotero window does not guarantee the process exited.
Plugin-related quit hangs can leave `zotero.sqlite` locked even after the UI disappears.

Before any direct write:

- check the actual process, not just the window state
- require `pgrep` to return nothing before writing

Useful check:

```bash
pgrep -fl '/Applications/Zotero.app/Contents/MacOS/zotero' || true
```

## Integrity Pitfall Found In This Session

During collection consolidation, old collections were deleted but some orphan rows remained in `collectionItems`.
This caused Zotero UI errors like:

- `Collection 16 not found for item 1/EKWD7NQG`

Required post-delete check:

```sql
SELECT COUNT(*)
FROM collectionItems ci
LEFT JOIN collections c ON c.collectionID = ci.collectionID
WHERE c.collectionID IS NULL;
```

If the count is nonzero, back up first, then repair:

```sql
DELETE FROM collectionItems
WHERE collectionID NOT IN (SELECT collectionID FROM collections);
```

## Sync And Cloud Verification Rule

Direct SQLite edits are local and can fail to propagate through normal Zotero sync bookkeeping.

After local edits:

1. verify locally first
2. run ordinary sync once
3. verify:
   - local Zotero app
   - Zotero Web Library
   - at least one other device when cross-device correctness matters
4. remember that `WebDAV` only reflects attachments, not collection structure
5. if ordinary sync does not propagate the direct DB edits, use:
   - `Sync -> Reset -> Replace Online Library`

This reset is a fallback, not the default first action.
