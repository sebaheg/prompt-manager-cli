# prompt-manager-cli

A CLI tool to create and organize prompt files for code agents (Claude Code, Codex, Gemini CLI, etc.).

## Installation

```bash
pip install prompt-manager-cli
```

Or install in editable mode for development:

```bash
pip install -e ".[dev]"
```

## Usage

### Create a new prompt file

```bash
pm new
```

This creates a new Markdown file in `.prompt-manager/prompts/` with a timestamped filename:

```
prompt-2026-01-05-14-37-a1b2c3d.md
```

The file contains a template with metadata:

```markdown
---
created_at: "2026-01-05T14:37:00+01:00"
git_hash: "a1b2c3d"
cwd: "/path/to/your/project"
---

# Goal

# Context

# Constraints

# Acceptance criteria
```

### Options

```bash
# Specify a custom output directory
pm new --dir ./my-prompts

# Open the file in your editor after creation
pm new --edit
```

The `--edit` flag uses `$VISUAL` or `$EDITOR` environment variables to determine which editor to use.

## Local Development

Run directly without installing:

```bash
python -m prompt_manager_cli new
```

Run tests:

```bash
pytest
```

## License

MIT
