"""Tests for agentic-project-documenting-plugin structure and specifications."""

import json
from pathlib import Path
import re

PLUGIN_ROOT = Path(__file__).resolve().parent.parent


def parse_frontmatter(md_path: Path) -> dict:
    content = md_path.read_text(encoding="utf-8")
    fm_match = re.match(r"^---\s*\n(.*?)\n---", content, re.DOTALL)
    metadata = {}
    if fm_match:
        current_list_key = None
        for line in fm_match.group(1).splitlines():
            line_str = line.strip()
            if not line_str or line_str.startswith("#"):
                continue
            if line_str.startswith("- ") and current_list_key:
                val = line_str[2:].strip().strip('"').strip("'")
                metadata[current_list_key].append(val)
            elif ":" in line:
                key, val = line.split(":", 1)
                key = key.strip()
                val = val.strip().strip('"').strip("'")
                if not val:
                    metadata[key] = []
                    current_list_key = key
                else:
                    current_list_key = None
                    if val.lower() == "true":
                        metadata[key] = True
                    elif val.lower() == "false":
                        metadata[key] = False
                    else:
                        metadata[key] = val
    return metadata


def test_plugin_manifest_valid():
    manifest_file = PLUGIN_ROOT / "plugin.json"
    assert manifest_file.exists(), "plugin.json must exist"
    data = json.loads(manifest_file.read_text(encoding="utf-8"))
    assert data.get("name") == "agentic-project-documenting-plugin"
    assert data.get("version") == "0.1.0"
    assert data.get("license") == "MIT"
    assert "description" in data and len(data["description"]) > 0


def test_pyproject_valid():
    pyproject_file = PLUGIN_ROOT / "pyproject.toml"
    assert pyproject_file.exists(), "pyproject.toml must exist"
    content = pyproject_file.read_text(encoding="utf-8")
    assert 'name = "agentic-project-documenting-plugin"' in content
    assert 'version = "0.1.0"' in content
    assert 'requires-python = ">=3.11"' in content
    assert "pytest>=8.0.0" in content


def test_license_exists():
    license_file = PLUGIN_ROOT / "LICENSE"
    assert license_file.exists(), "LICENSE must exist"
    content = license_file.read_text(encoding="utf-8")
    assert "MIT License" in content
    assert "Greg PFISTER" in content


def test_contributing_exists():
    contrib_file = PLUGIN_ROOT / "CONTRIBUTING.md"
    assert contrib_file.exists(), "CONTRIBUTING.md must exist"
    content = contrib_file.read_text(encoding="utf-8")
    assert "agentic-project-documenting-plugin" in content
    assert "pytest" in content


def test_readme_exists():
    readme_file = PLUGIN_ROOT / "README.md"
    assert readme_file.exists(), "README.md must exist"
    content = readme_file.read_text(encoding="utf-8")
    assert "agentic-project-documenting-plugin" in content
    assert "@coding-document" in content
    assert "agentic-obsidian/" in content


def test_rules_exist():
    rules_file = PLUGIN_ROOT / "rules" / "AGENTS.md"
    assert rules_file.exists(), "rules/AGENTS.md must exist"
    content = rules_file.read_text(encoding="utf-8")
    assert "Obsidian Vault Documentation Standards" in content
    assert "@coding-document" in content
    assert "agentic-obsidian/" in content


def test_agent_catalog_exists():
    catalog_file = PLUGIN_ROOT / "agents" / "agent.md"
    assert catalog_file.exists(), "agents/agent.md catalog must exist"
    meta = parse_frontmatter(catalog_file)
    assert meta.get("name") in ("obsidian-catalog", "coding-obsidian-catalog")
    content = catalog_file.read_text(encoding="utf-8")
    assert "# Coding - Obsidian Vault Documentation Subagents & Architecture (agents/agent.md)" in content
    assert "@coding-document" in content


def test_coding_document_agent_valid():
    agent_file = PLUGIN_ROOT / "agents" / "coding-document" / "agent.md"
    assert agent_file.exists(), "coding-document agent.md must exist"
    meta = parse_frontmatter(agent_file)
    assert meta.get("name") == "coding-document"
    assert meta.get("enable_write_tools") is True
    assert meta.get("enable_subagent_tools") is True
    assert meta.get("enable_mcp_tools") is True

    tools = meta.get("tools", [])
    expected_tools = ["read_file", "write_file", "list_dir", "run_command", "ask_question", "send_message"]
    for t in expected_tools:
        assert t in tools, f"Tool {t} must be declared in agent tools"
    assert "edit_file" not in tools, "edit_file must not be declared on coding-document"

    aliases = meta.get("aliases", [])
    assert "coding-document" in aliases
    assert "document" not in aliases
    for alias in aliases:
        assert re.match(r"^coding(-.*)?$", alias), f"Alias '{alias}' does not match ^coding(-.*)?$"

    content = agent_file.read_text(encoding="utf-8")
    assert "# Coding - Autonomous Documentation Specialist (@coding-document)" in content
    assert "Obsidian vault" in content
    assert "projects" in content
    assert "features" in content
    assert "architecture" in content
    assert "sessions" in content
    assert "git" in content


def test_coding_document_skill_valid():
    legacy_dir = PLUGIN_ROOT / "skills" / "document"
    assert not legacy_dir.exists(), "Legacy skills/document directory must not exist"

    skill_file = PLUGIN_ROOT / "skills" / "coding-document" / "SKILL.md"
    assert skill_file.exists(), "skills/coding-document/SKILL.md must exist"
    meta = parse_frontmatter(skill_file)
    assert meta.get("name") == "coding-document"
    assert "description" in meta
    content = skill_file.read_text(encoding="utf-8")
    assert "@coding-document" in content


def test_no_stale_companion_plugin_references():
    stale_names = [
        f"agentic-{part}-plugin"
        for part in ["investigate", "monitor", "research", "triage"]
    ]
    md_files = list(PLUGIN_ROOT.glob("*.md")) + list(PLUGIN_ROOT.glob("*/**/*.md"))
    for md_file in md_files:
        content = md_file.read_text(encoding="utf-8")
        for stale in stale_names:
            assert stale not in content, f"Found stale plugin reference '{stale}' in {md_file.relative_to(PLUGIN_ROOT)}"

    readme = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
    assert "agentic-issue-investigation-plugin" in readme
    assert "agentic-topic-researching-plugin" in readme
    assert "agentic-task-monitoring-plugin" in readme
    assert "agentic-prompt-triage-plugin" in readme


def test_coding_design_archival_documented():
    skill_content = (PLUGIN_ROOT / "skills" / "coding-document" / "SKILL.md").read_text(encoding="utf-8")
    assert "@coding-design" in skill_content
    assert "design-spec.md" in skill_content
    assert "agentic-obsidian/designs/" in skill_content
    assert "agentic-obsidian/designs/index.md" in skill_content

    rules_content = (PLUGIN_ROOT / "rules" / "AGENTS.md").read_text(encoding="utf-8")
    assert "agentic-design-plugin" in rules_content
    assert "@coding-design" in rules_content
    assert "agentic-obsidian/designs/" in rules_content
    assert "agentic-obsidian/designs/index.md" in rules_content


def test_obsidian_worktree_isolation_documented():
    paths = [
        PLUGIN_ROOT / "agents" / "coding-document" / "agent.md",
        PLUGIN_ROOT / "skills" / "coding-document" / "SKILL.md",
        PLUGIN_ROOT / "rules" / "AGENTS.md",
    ]
    for path in paths:
        content = path.read_text(encoding="utf-8")
        assert ".worktrees/<slug>" in content, f"Missing .worktrees/<slug> in {path}"
        assert "docs/<slug>" in content, f"Missing docs/<slug> in {path}"
        assert "<base>" in content, f"Missing primary repo base branch invariant in {path}"
        assert ".worktrees/" in content, f"Missing .worktrees/ ignore rule in {path}"


def test_defer_pr_and_multi_phase_accumulation_documented():
    for rel_path in [
        Path("agents/coding-document/agent.md"),
        Path("skills/coding-document/SKILL.md"),
        Path("rules/AGENTS.md"),
        Path("agents/agent.md"),
        Path("README.md"),
    ]:
        content = (PLUGIN_ROOT / rel_path).read_text(encoding="utf-8")
        assert "defer_pr=true" in content, f"Missing defer_pr=true in {rel_path}"
        assert "defer_pr=false" in content, f"Missing defer_pr=false in {rel_path}"

    agent_content = (PLUGIN_ROOT / "agents" / "coding-document" / "agent.md").read_text(encoding="utf-8")
    assert "Post-Plan" in agent_content
    assert "Pre-Merge" in agent_content
    assert "Post-Merge" in agent_content
    assert "@coding-merge" in agent_content


def test_release_strategies_and_hybrid_pr_gate_documented():
    for rel_path in [
        Path("agents/coding-document/agent.md"),
        Path("skills/coding-document/SKILL.md"),
        Path("rules/AGENTS.md"),
    ]:
        content = (PLUGIN_ROOT / rel_path).read_text(encoding="utf-8")
        assert "gh pr create" in content, f"Missing gh pr create in {rel_path}"
        assert "Hybrid PR Waiting Gate" in content, f"Missing Hybrid PR Waiting Gate in {rel_path}"
        assert "Local-Only Release Strategy" in content, f"Missing Local-Only Release Strategy in {rel_path}"
        assert "Non-Git Fallback" in content, f"Missing Non-Git Fallback in {rel_path}"

    agent_content = (PLUGIN_ROOT / "agents" / "coding-document" / "agent.md").read_text(encoding="utf-8")
    assert "gh pr view" in agent_content
    assert "gh pr merge --auto --merge" in agent_content
    assert "pull --ff-only" in agent_content
    assert "worktree remove" in agent_content
    assert "worktree prune" in agent_content
    assert "rev-parse --is-inside-work-tree" in agent_content


def test_question_relay_and_edit_file_prohibition_documented():
    for rel_path in [
        Path("agents/coding-document/agent.md"),
        Path("skills/coding-document/SKILL.md"),
        Path("rules/AGENTS.md"),
        Path("agents/agent.md"),
        Path("README.md"),
    ]:
        content = (PLUGIN_ROOT / rel_path).read_text(encoding="utf-8")
        assert "[QUESTION_RELAY_REQUEST]" in content, f"Missing [QUESTION_RELAY_REQUEST] in {rel_path}"
        assert "[QUESTION_RELAY_RESPONSE]" in content, f"Missing [QUESTION_RELAY_RESPONSE] in {rel_path}"

    agent_content = (PLUGIN_ROOT / "agents" / "coding-document" / "agent.md").read_text(encoding="utf-8")
    assert "edit_file" in agent_content and "prohibited" in agent_content.lower()
    readme_content = (PLUGIN_ROOT / "README.md").read_text(encoding="utf-8")
    assert "edit_file` is strictly prohibited" in readme_content


