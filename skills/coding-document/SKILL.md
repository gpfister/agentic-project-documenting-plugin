---
name: coding-document
description: >-
  Autonomous Obsidian vault documentation skill for projects, architecture, features, code changes,
  git branch statuses, sessions, and artifacts.
---

# Obsidian Vault Documentation & Knowledge Curation (`@coding-document`)

The `coding-document` skill orchestrates documentation generation, synchronization, and archival into the workspace Obsidian vault (`*-obsidian/`, e.g., `agentic-obsidian/`) using self-managed Git worktree isolation (`<vault_root>/.worktrees/<slug>` on `docs/<slug>`). It is executed by the autonomous specialist agent **`@coding-document`**, using `write_file` restricted strictly to `<vault_root>/.worktrees/<slug>/**` (or `<vault_root>/**` only under Non-Git Fallback) and session artifacts under `<appDataDir>/brain/<conversation-id>/*.md` (`edit_file` is strictly prohibited, and repository-local file edits—including `README.md`, source code, configs, and tests—are delegated exclusively to `@coding-develop`).

---

## 1. Capabilities & Scope

1. **Project & Feature Documentation**:
   - Synthesizes workspace layout, project roles, and cross-repo dependencies into `agentic-obsidian/projects/`.
   - Documents features, endpoints, and specifications in `agentic-obsidian/features/`.
2. **Architecture & Decision Records (ADRs)**:
   - Formulates system designs, boundary diagrams (using Mermaid), and formal ADRs in `agentic-obsidian/architecture/`.
3. **Session & Artifact Archival**:
   - Captures conversation transcripts, user requests, tool reasoning traces, and tokens into `agentic-obsidian/sessions/`.
   - Saves session artifacts to `agentic-obsidian/sessions/attachments/<session-id>/`.
4. **Code Changes & Git Status Tracking**:
   - Documents branch states, commit history, dirty/clean status, and worktree allocations in `agentic-obsidian/git-status.md`.
5. **Self-Managed Obsidian Git Worktree & PR Lifecycle**:
   - Isolates all `*-obsidian/` edits in `<vault_root>/.worktrees/<slug>` on `docs/<slug>` while keeping `<vault_root>` checked out on `<base>` (`main` or `master`).
   - Supports multi-phase `defer_pr` accumulation (`@coding`) and single-shot release/cleanup (`@coding-design`, `@coding-investigate`, `@coding-research`, `@coding-monitor`, direct invocations).
6. **Cross-Plugin Lifecycle Coordination**:
   - Serves as the designated documentation worker for `@coding` (Post-Plan, Pre-Merge, Post-Merge hooks), `@coding-design` (approved UI/UX design specifications, PenPot links, and design tokens), `@coding-investigate` (concluded issue assessments), `@coding-research` (creating/updating topics and subjects), and `@coding-monitor` (telemetry and session alerts).

---

## 2. Worktree Isolation, `defer_pr`, & Release Lifecycle

### Worktree Setup & Primary Repository Invariant
- **Primary Repository Invariant**: `<vault_root>` (`*-obsidian/`) MUST remain on `<base>` (`main` or `master`) at all times.
- **Worktree & Branch**: `<vault_root>/.worktrees/<slug>` on `docs/<slug>`.
- **Ignore Rule**: Ensure `.worktrees/` is ignored in `<vault_root>/.gitignore` or `<vault_root>/.git/info/exclude`.
- **Setup / Reuse**: Inspect via `git -C <vault_root> worktree list`, prune stale entries with `git -C <vault_root> worktree prune`, reuse `<vault_root>/.worktrees/<slug>` if on `docs/<slug>`, otherwise create with `git -C <vault_root> worktree add -b docs/<slug> <vault_root>/.worktrees/<slug> <base>` (or `worktree add <vault_root>/.worktrees/<slug> docs/<slug>` if the branch already exists).

### `defer_pr` Parameter Contract
- **`defer_pr=true`** (`@coding` Post-Plan and Pre-Merge hooks): Author into `<vault_root>/.worktrees/<slug>`, stage & commit if `git status --porcelain` is non-empty (skip empty commits), and return without pushing, opening a PR, or removing the worktree.
- **`defer_pr=false`** (default for single-shot callers, direct user invocations, and `@coding` Post-Merge hook): Author into `<vault_root>/.worktrees/<slug>`, commit if non-empty, and execute the Release & Cleanup Strategy (if `docs/<slug>` has no commits ahead of `<base>`, skip push/PR and clean up the unused worktree/branch).

### Release & Cleanup Strategies
1. **Remote Release Strategy (`origin` configured)**:
   - Push `docs/<slug>`: `git -C <vault_root>/.worktrees/<slug> push -u origin docs/<slug>`.
   - Check `gh auth status` and run `gh pr create --base <base> --head docs/<slug>` (or present `https://github.com/<owner>/<repo>/compare/<base>...docs/<slug>?expand=1` fallback via Question Relay).
   - **Hybrid PR Waiting Gate**: Inspect `gh pr view <pr_number> --json state,reviewDecision,mergedAt,url`. If `state == "OPEN"`, **never** sleep or poll; prompt via Dual-Mode Question Relay (`(Recommended) Re-check PR status`, `Enable GitHub auto-merge (gh pr merge --auto --merge) and re-check`, or `Proceed without waiting` leaving the worktree/branch intact).
   - **Post-Merge Base Sync & Cleanup** (`state == "MERGED"`): Verify `<vault_root>` is clean, `checkout <base>`, `pull --ff-only origin <base>`, `worktree remove` (with `--force` fallback) + `worktree prune`, idempotent remote branch delete (`ls-remote` + `push origin --delete docs/<slug>`), `branch -d docs/<slug>`, `fetch --prune origin`, and verify `branch --show-current` is `<base>`.
2. **Local-Only Release Strategy (no remote)**: Verify `<vault_root>` is clean, `checkout <base>`, `merge docs/<slug>`, verify `branch --show-current` is `<base>`, `worktree remove` + `worktree prune`, and `branch -d docs/<slug>`.
3. **Non-Git Fallback**: If `git -C <vault_root> rev-parse --is-inside-work-tree` fails, emit a warning and write directly to `<vault_root>/...`.

### Dual-Mode Question Relay Protocol
- **Subagent Mode (`caller_id` present)**: Never call `ask_question`; send `[QUESTION_RELAY_REQUEST]` via `send_message` to `caller_id` and await `[QUESTION_RELAY_RESPONSE]`.
- **Standalone Mode (no `caller_id`)**: Call `ask_question` directly.

---

## 3. Standard Workflows

### Workflow A: Multi-Phase Coding Workflow Maintenance (`@coding`)
1. **Post-Plan Hook (`slug=<slug>`, `defer_pr=true`)**: Documents implementation plans, repository breakdowns, approved `specification.md`, and formalizes ADRs under `<vault_root>/.worktrees/<slug>/architecture/` and `features/`, committing incrementally.
2. **Pre-Merge Hook (`slug=<slug>`, `defer_pr=true`)**: Reuses `<vault_root>/.worktrees/<slug>` on `docs/<slug>`, performs pre-merge Obsidian vault tidy-up across architecture records and feature notes in `*-obsidian/` (repo-local `README.md` updates are delegated to `@coding-develop`), and commits incrementally.
3. **Post-Merge Hook (`slug=<slug>`, `defer_pr=false`)**: Reuses `<vault_root>/.worktrees/<slug>` on `docs/<slug>`, updates repository git statuses (`agentic-obsidian/git-status.md`), branch topologies, and release changelogs, commits, and executes the Release & Cleanup Strategy.

### Workflow B: Archiving Multi-Agent Deliverables (Single-Shot, `defer_pr=false`)
- **From `@coding-design`**: Archives approved `design-spec.md`, PenPot project/file/frame links, component hierarchies, and extracted design tokens into `agentic-obsidian/designs/<design-slug>.md`, and updates `agentic-obsidian/designs/index.md`.
- **From `@coding-investigate`**: Formats and stores root-cause analysis and approved `issue-assessment.md` into `agentic-obsidian/investigations/<issue-slug>.md`.
- **From `@coding-research`**: Records approved research reports into `agentic-obsidian/research/`, creating a new topic/subject or updating an existing one, and updates `agentic-obsidian/research/index.md`.
- **From `@coding-monitor`**: Documents telemetry metrics, observed streams, error alerts, and container surveillance logs into `agentic-obsidian/monitoring/<service-slug>.md`.

### Workflow C: Session Syncing
- Invokes `python3 scripts/sync_sessions.py <session-id>` to sync transcripts and copy artifacts from `<appDataDir>/brain/<conversation-id>/` into `<vault_root>/.worktrees/<slug>/sessions/` (or `agentic-obsidian/sessions/` under Non-Git Fallback).

---

## 4. Triggering the Subagent

- **Direct User Invocation**:
  - `@coding-document Document the new authentication module and add an ADR for token storage`
  - `@coding-document Update git status and branch documentation across all repositories`
  - `@coding-document Sync and archive the latest session into Obsidian`
- **Programmatic Delegation**:
  - Subagents invoke `@coding-document` using `invoke_subagent(TypeName="coding-document", Role="Documentation Specialist", Prompt=...)` (passing `slug=<slug>` and `defer_pr=true|false` for multi-phase `@coding` hooks).
