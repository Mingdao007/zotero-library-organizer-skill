# Zotero Library Organizer Skill

用于 Zotero 库维护的可移植 skill，强调先审计、再分析重复项，并安全执行 SQLite 直改工作流。

## 提供内容

- 可安装 skill: [`zotero-library-organizer`](./zotero-library-organizer)
- 公开 references: [`zotero-library-organizer/references/`](./zotero-library-organizer/references)
- 辅助脚本: [`zotero-library-organizer/scripts/`](./zotero-library-organizer/scripts)

## 安装 / 使用

- `Codex App`：从本仓库路径 `zotero-library-organizer` 安装
- GitHub 安装目标：
  - repo：`<owner>/zotero-library-organizer-skill`
  - path：`zotero-library-organizer`
- 安装后重启 `Codex App`，让新 skill 被发现。

## 覆盖范围

- 强调 direct DB write 之前先做 audit
- 支持基于复制快照的 duplicate 与 unfiled analysis
- 提供 backup-before-write 的确定性维护流程

## 触发示例

- `Audit this Zotero library before cleanup.`
- `Find duplicates and unfiled items safely.`
- `Plan a deterministic Zotero collection reorganization.`

## 不触发示例

- `Only locate one local PDF attachment.`
- `Debug a Zotero MCP startup issue.`
- `Do a literature review without library edits.`

## 隐私边界

这个公开仓库只保留可复用、可公开的工作流部分。

- User-specific taxonomy wording is rewritten into generic policy wording where needed.
- Database defaults use host-relative paths or environment overrides instead of private absolute paths.

## 仓库结构

- `zotero-library-organizer/`: installable `Codex App` skill
- `zotero-library-organizer/references/`: bundled public references
- `zotero-library-organizer/scripts/`: bundled public scripts
- `CHANGELOG.md`: release history
- `LICENSE`: `MIT`

English:

- [README.md](./README.md)
