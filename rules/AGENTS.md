# Obsidian Vault Documentation Standards & Guidelines — agentic-project-documenting-plugin

This rule set applies whenever the `agentic-project-documenting-plugin` is active in an Antigravity session.

---

## 1. Documentation Principles & Obsidian Vault Architecture
- **Centralized Knowledge Repository**: All long-term workspace intelligence, architecture decisions, feature specifications, git statuses, and session records must be maintained in the shared Obsidian vault (`agentic-obsidian/`).
- **Comprehensive Coverage**:
  - **Project & Feature Specs**: Document system purpose, capabilities, user journeys, and configuration in `agentic-obsidian/projects/` and `agentic-obsidian/features/`.
  - **Architecture & ADRs**: Formalize architectural decisions, system boundaries, component diagrams (Mermaid), and interface contracts in `agentic-obsidian/architecture/`.
  - **Session & Artifact Archival**: Every significant session trajectory, prompt, tool execution trace, and generated artifact must be preserved under `agentic-obsidian/sessions/` and `agentic-obsidian/sessions/attachments/<session-id>/`.
  - **Code Changes & Git Tracking**: Document active git branches, worktrees, staged/unstaged changes, and commit statuses across repositories in `agentic-obsidian/git-status.md` and feature notes.
- **Wikilinks & Clickable References**: Combine Obsidian internal wikilinks (`[[Note Name]]`) with Antigravity clickable markdown links using the `file://` scheme for all workspace file paths, symbols, and artifacts.

---

## 2. Autonomous Documentation Specialist (`@coding-document`)
- **Authority & Permissions**: The `@coding-document` subagent is granted permissions to:
  - Read code, configs, transcripts, and git states (`read_file`, `list_dir`).
  - Author and update Obsidian vault notes inside `<vault_root>/.worktrees/<slug>/` (or `<vault_root>/` under Non-Git Fallback) and session artifacts (`write_file` only; `edit_file` is prohibited).
  - Execute read-only git inspection commands (`git status`, `git branch -a`, `git log`, `git diff`) across workspace code repositories, `scripts/sync_sessions.py`, and git worktree/staging/commit/push/`gh` PR/base-sync/cleanup commands scoped strictly to `*-obsidian/` (`run_command`).
  - Communicate with caller subagents and users (`send_message`, `ask_question`).
- **Safety Boundary**: `@coding-document`'s `write_file` usage is restricted strictly to isolated Obsidian vault worktrees (`<vault_root>/.worktrees/<slug>/`, or `<vault_root>/` only under Non-Git Fallback when `*-obsidian/` is not a Git repository) and session artifacts under `<appDataDir>/brain/<conversation-id>/*.md`. It must NEVER use `edit_file` or `write_file` to modify application source code, production configs, test suites, or repository-local documentation (`README.md`, `CONTRIBUTING.md`)—all code repository file changes belong exclusively to `@coding-develop`. `run_command` must remain strictly non-mutating with respect to code repositories.
- **Self-Managed Worktree & PR Lifecycle (`*-obsidian/`)**:
  - `@coding-document` keeps `<vault_root>` on `<base>` (`main` or `master`) at all times, isolates edits in `<vault_root>/.worktrees/<slug>` on `docs/<slug>`, ensures `.worktrees/` is ignored, and executes Remote Release Strategy (`git push`, `gh pr create` / compare URL fallback, Hybrid PR Waiting Gate, Post-Merge Base Sync & Cleanup), Local-Only Release Strategy, or Non-Git Fallback when `defer_pr=false`. `@coding-merge` manages code repositories exclusively.
- **Dual-Mode Question Relay Protocol**:
  - **Subagent Mode (`caller_id` present)**: Never call `ask_question` directly. Relay interactive prompts (Hybrid PR Waiting Gate, `gh` fallback, dirty-state/conflict decisions) to `caller_id` via `send_message` using `[QUESTION_RELAY_REQUEST]` and await `[QUESTION_RELAY_RESPONSE]`.
  - **Standalone Mode (no `caller_id`)**: Call `ask_question` directly at the session root.

---

## 3. Cross-Plugin Integration & Handoff Protocols
When `agentic-project-documenting-plugin` is active, other plugins coordinate with `@coding-document`:
- **`agentic-coding-plugin` (`@coding`)**:
  - `@coding` passes a consistent `slug=<slug>` and `defer_pr` directive to `@coding-document` across three lifecycle hooks:
    - **Post-Plan Hook (`defer_pr=true`)**: Document implementation plans, architecture diagrams, approved `specification.md`, and formalize ADRs in `<vault_root>/.worktrees/<slug>` on `docs/<slug>`, commit incrementally, and return without pushing, opening a PR, or removing the worktree.
    - **Pre-Merge Hook (`defer_pr=true`)**: Reuse `<vault_root>/.worktrees/<slug>` on `docs/<slug>`, perform pre-merge Obsidian vault documentation tidy-up across architecture records and feature specs in `*-obsidian/` (repo-local `README.md` updates are delegated to `@coding-develop`), and commit incrementally.
    - **Post-Merge Hook (`defer_pr=false`)**: Reuse `<vault_root>/.worktrees/<slug>` on `docs/<slug>`, update repository git statuses (`agentic-obsidian/git-status.md`), branch topologies, and release changelogs, commit, and execute the Release & Cleanup Strategy (single accumulated PR or local merge + worktree/branch cleanup).
- **`agentic-issue-investigation-plugin` (`@coding-investigate`)**:
  - Once the issue investigation is done, `@coding-investigate` invokes `@coding-document` (`defer_pr=false`) to store the root cause analysis, evidence, and remediation assessment into `agentic-obsidian/investigations/`.
- **`agentic-topic-researching-plugin` (`@coding-research`)**:
  - Upon research report approval, `@coding-research` invokes `@coding-document` (`defer_pr=false`) to record the research into `agentic-obsidian/research/`, creating a new topic/subject or updating an existing one.
- **`agentic-task-monitoring-plugin` (`@coding-monitor`)**:
  - At the end of monitoring, `@coding-monitor` invokes `@coding-document` (`defer_pr=false`) to record telemetry logs, error anomalies, and remediation actions in `agentic-obsidian/monitoring/`.
- **`agentic-design-plugin` (`@coding-design`)**:
  - Upon design specification approval, `@coding-design` invokes `@coding-document` (`defer_pr=false`) to archive the approved `design-spec.md`, PenPot project/file/frame links, and design tokens into `agentic-obsidian/designs/<design-slug>.md` and update `agentic-obsidian/designs/index.md`.
- **`agentic-prompt-triage-plugin`**:
  - If `agentic-project-documenting-plugin` is installed, dynamic triage classifies documentation requests and routes them directly to `@coding-document`.

---

## 4. Communication & Presentation
- Keep documentation well-structured, readable, and visually clear using GitHub Flavored Markdown alerts (`> [!NOTE]`, `> [!IMPORTANT]`, `> [!TIP]`, `> [!WARNING]`).
- Include Mermaid diagrams (`mermaid` blocks) for architecture flows, sequence interactions, and state transitions.
