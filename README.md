# ASO App Store Creative Skills

This repository contains two App Store creative skills:

1. **`aso-appstore-screenshots`** — plans, critiques, and generates screenshot sets for iOS apps
2. **`aso-appstore-icon`** — audits the current icon, drafts distinct directions, and generates App Store-ready icon concepts

The screenshot skill supports both Codex and Claude Code. The app-icon skill is currently documented for Codex packaging.

## Included Skills

### `aso-appstore-screenshots`

The screenshot skill:

1. Analyzes the app to identify the strongest user benefits
2. Reviews simulator screenshots and pairs each one to the right benefit
3. Builds deterministic screenshot scaffolds with `compose.py`
4. Enhances those scaffolds into App Store-ready creatives with Gemini MCP
5. Generates a final side-by-side showcase image

### `aso-appstore-icon`

The app-icon skill:

1. Analyzes the app, existing icon assets, and brand cues
2. Audits the current icon and competitor or inspiration references
3. Drafts 3 distinct icon directions
4. Generates icon concepts with Gemini MCP
5. Normalizes raw outputs to exact App Store requirements with `prepare_icon.py`
6. Builds review boards with `preview_icons.py` for fast comparison and iteration

## Installation

The screenshot skill lives at the repository root. The app-icon skill lives in the [`aso-appstore-icon/`](aso-appstore-icon) subdirectory and must be installed as its own skill folder.

### 1. Install the screenshot skill for Codex

Codex discovers user skills from `~/.agents/skills/` and project skills from `.agents/skills/`.

Global install:

```bash
mkdir -p "$HOME/.agents/skills"
git clone https://github.com/confianick/claude-skill-aso-appstore-screenshots "$HOME/.agents/skills/aso-appstore-screenshots"
```

In-place development symlink:

```bash
mkdir -p "$HOME/.agents/skills"
rm -f "$HOME/.agents/skills/aso-appstore-screenshots"
ln -s "$(pwd)" "$HOME/.agents/skills/aso-appstore-screenshots"
```

### 2. Install the screenshot skill for Claude Code

Claude Code discovers user skills from `~/.claude/skills/` and project skills from `.claude/skills/`.

Global in-place development symlink:

```bash
mkdir -p "$HOME/.claude/skills"
rm -f "$HOME/.claude/skills/aso-appstore-screenshots"
ln -s "$(pwd)" "$HOME/.claude/skills/aso-appstore-screenshots"
```

If you prefer a project-local install inside a consuming app repository, use `.claude/skills/aso-appstore-screenshots`.

### 3. Install the app-icon skill for Codex

Symlink the subfolder as its own skill:

```bash
mkdir -p "$HOME/.agents/skills"
rm -f "$HOME/.agents/skills/aso-appstore-icon"
ln -s "$(pwd)/aso-appstore-icon" "$HOME/.agents/skills/aso-appstore-icon"
```

If you are installing into a consuming app repository instead of your global user skills directory, use:

- `.agents/skills/aso-appstore-screenshots` for the screenshot skill
- `.claude/skills/aso-appstore-screenshots` for the screenshot skill in Claude Code
- `.agents/skills/aso-appstore-icon` for the icon skill

Restart Codex or Claude Code after installing or updating a skill.

### 4. Install Python dependencies

Both skills use Pillow-based local helpers:

```bash
python3 -m pip install Pillow
```

### 5. Install the screenshot font dependency

The screenshot scaffold renderer uses **SF Pro Display Black** for headline text. On macOS, install it from [Apple's developer fonts](https://developer.apple.com/fonts/). The expected path is:

```text
/Library/Fonts/SF-Pro-Display-Black.otf
```

The icon helpers do not require this exact font. They fall back gracefully if SF Pro display fonts are unavailable.

### 6. Configure Gemini MCP

Both skills use Gemini as the generation and editing backend.

For Codex:

```bash
codex mcp add gemini --env GEMINI_API_KEY=your-api-key-here -- npx -y @houtini/gemini-mcp
codex mcp get gemini
```

Codex stores MCP server registrations in `~/.codex/config.toml`.

For Claude Code, register the same server command in your Claude MCP config:

```text
env GEMINI_API_KEY=your-api-key-here VERBOSE=true -- npx -y @houtini/gemini-mcp
```

Use `~/.claude/settings.json` for a user-level server or a project `.mcp.json` for a repo-local server.

If Gemini image generation or editing returns `429 RESOURCE_EXHAUSTED` with zero image quota, generation cannot continue. Enable billing or image-model quota for the Gemini project backing `GEMINI_API_KEY`, then resume later.

## Usage

### Screenshot skill in Codex

From inside an app project, invoke the screenshot skill explicitly in your prompt:

```text
$aso-appstore-screenshots
```

You can also use the Codex skills picker or slash-command list once the skill is installed.

### Screenshot skill in Claude Code

Claude Code can discover the screenshot skill automatically from `.claude/skills/` or `~/.claude/skills/` when the request matches the skill description.

For explicit use, ask Claude Code to use `aso-appstore-screenshots` for the current app-store creative task. If your Claude Code build exposes user-invocable skills as slash commands, `/aso-appstore-screenshots` also works.

### App-icon skill in Codex

```text
$aso-appstore-icon
```

You can also use the Codex skills picker or slash-command list once the icon skill is installed.

## State And Output

### Screenshot skill

Resume state is stored at:

```text
.agents/aso-appstore-screenshots/state.json
```

Legacy state at `.codex/aso-appstore-screenshots/state.json` or `.claude/aso-appstore-screenshots/state.json` is still recognized and reused.

Generated assets are stored under:

```text
screenshots/
  01-benefit-slug/
    scaffold.png
    v1.jpg
    v1-resized.jpg
    v2.jpg
    v2-resized.jpg
    v3.jpg
    v3-resized.jpg
  final/
    01-benefit-slug.jpg
  showcase.png
```

### App-icon skill

Resume state is stored at:

```text
.codex/aso-appstore-icon/state.json
```

Generated assets are stored under:

```text
app-icon/
  01-direction-slug/
    v1.png
    v1-prepared.png
    v2.png
    v2-prepared.png
    v3.png
    v3-prepared.png
    review.png
  final/
    01-direction-slug.png
  preview.png
```

## Repository Layout

| Path | Purpose |
|------|---------|
| `SKILL.md` | Screenshot skill prompt and workflow |
| `agents/openai.yaml` | Screenshot skill UI metadata |
| `CLAUDE.md` | Claude Code guidance for the screenshot skill |
| `compose.py` | Deterministic screenshot scaffold generator |
| `generate_frame.py` | Regenerates the screenshot device frame template |
| `showcase.py` | Builds the final screenshot showcase image |
| `assets/device_frame.png` | Pre-rendered iPhone frame template |
| `aso-appstore-icon/SKILL.md` | App-icon skill prompt and workflow |
| `aso-appstore-icon/agents/openai.yaml` | App-icon skill UI metadata |
| `aso-appstore-icon/prepare_icon.py` | Normalizes generated icons to exact App Store source requirements |
| `aso-appstore-icon/preview_icons.py` | Builds icon comparison and preview boards |
| `AGENTS.md` | Repository-specific engineering guidance |

## Verification

Run these checks after updating the skill prompts or helper scripts:

```bash
python3 -m py_compile compose.py generate_frame.py showcase.py
python3 -m py_compile aso-appstore-icon/prepare_icon.py aso-appstore-icon/preview_icons.py
python3 -m unittest discover -s tests
git diff --check
```

## License

MIT
