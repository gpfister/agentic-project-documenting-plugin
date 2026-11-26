---
name: coding-obsidian-catalog
description: Architecture overview and catalog for the agentic-project-documenting-plugin subagents.
enable_write_tools: false
enable_subagent_tools: false
enable_mcp_tools: false
tools:
  - read_file
  - list_dir
---

# Coding - Obsidian Vault Documentation Subagents & Architecture (agents/agent.md)

This document defines the subagent architecture and catalog for the **`agentic-project-documenting-plugin`**.

---

## 1. Architectural Overview

The `agentic-project-documenting-plugin` establishes the centralized knowledge base and documentation engine across the workspace using **Obsidian vaults** (`agentic-obsidian/`). It provides an autonomous specialist agent, **`@coding-document`**, capable of being invoked independently by users or programmatically by other pipeline subagents (`@coding`, `@coding-investigate`, `@coding-research`, `@coding-monitor`).

### Directory Structure
```text
agents/
├── agent.md                    # Master subagent catalog (this file)
└── coding-document/            # Autonomous Documentation Specialist (@coding-document)
    └── agent.md
```

---

## 2. Subagent Catalog

| Agent Handle | Directory | `enable_write_tools` | `enable_subagent_tools` | `enable_mcp_tools` | Allowed Tools | Description |
| :--- | :--- | :---: | :---: | :---: | :--- | :--- |
| **`@coding-document`** | [`agents/coding-document/`](file:///Users/gpfister/Development/Projects/gpfister/agentic/agentic-project-documenting-plugin/agents/coding-document/) | `True` | `True` | `True` | `read_file`, `write_file`, `list_dir`, `run_command`, `ask_question`, `send_message` | Autonomous documentation specialist documenting projects, features, architecture, sessions, artifacts, code changes, and git status in Obsidian vaults. |

---

## 3. Subagent Capabilities & Scope

### 3.1 Core Responsibilities
1. **Project & Feature Documentation**: Authoring and updating overview notes, capability catalogs, configuration guides, and user journeys under `agentic-obsidian/projects/` and `agentic-obsidian/features/`.
2. **Architecture & ADRs**: Maintaining system architecture notes, Mermaid diagrams, interface contracts, and Architecture Decision Records under `agentic-obsidian/architecture/`.
3. **Session & Artifact Archival**: Syncing Antigravity session transcripts and copying session artifacts from `<appDataDir>/brain/<conversation-id>/` into `agentic-obsidian/sessions/` and `agentic-obsidian/sessions/attachments/<session-id>/`.
4. **Code Changes & Git Status Tracking**: Auditing git branches, unstaged diffs, commit histories, and worktrees across all workspace repositories, recording snapshots into `agentic-obsidian/git-status.md`.
5. **Self-Managed Obsidian Worktree & PR Lifecycle**: Isolating all `*-obsidian/` documentation writes inside `<vault_root>/.worktrees/<slug>` on `docs/<slug>` while keeping `<vault_root>` on `<base>` (`main` or `master`), supporting multi-phase `defer_pr` accumulation (`@coding`) and single-shot release/cleanup (`gh pr create`, Hybrid PR Waiting Gate, Post-Merge Base Sync & Cleanup, Local-Only merge, or Non-Git Fallback), and relaying interactive prompts via Dual-Mode Question Relay (`[QUESTION_RELAY_REQUEST]` / `[QUESTION_RELAY_RESPONSE]`).

### 3.2 Inter-Plugin Collaboration Pipeline
```text
@coding (Post-Plan / Pre-Merge: defer_pr=true; Post-Merge: defer_pr=false) ──> @coding-document
                                                                                     │
@coding-design (concluded, defer_pr=false)       ──> @coding-document (archive design-spec & tokens)
                                                                                     │
@coding-investigate (concluded, defer_pr=false)  ──> @coding-document (archive investigation & root cause)
                                                                                     │
@coding-research (concluded, defer_pr=false)     ──> @coding-document (record research report)
                                                                                     │
@coding-monitor (concluded, defer_pr=false)      ──> @coding-document (record monitoring telemetry & alerts)
```
