# AGENTS.md

This file provides repository-specific guidance when working in this skill repository.

## What This Is

The repository root is the `aso-appstore-screenshots` skill, which guides users through creating high-converting App Store screenshots. It supports both Codex and Claude Code.

## Architecture

The main pieces are:

- **SKILL.md** — The skill prompt. Defines the multi-phase workflow: Benefit Discovery → Screenshot Pairing → Generation → Showcase. Resume state is stored in a project-local JSON ledger, defaulting to `.agents/aso-appstore-screenshots/state.json` while still reusing legacy `.codex/...` or `.claude/...` state if present.
- **agents/openai.yaml** — Codex UI metadata for display name, short description, and default prompt.
- **CLAUDE.md** — Claude Code guidance for the root screenshot skill.
- **compose.py** — A standalone Python compositing script (Pillow-based) that deterministically renders App Store screenshots. Takes a background hex colour, action verb, benefit descriptor, and simulator screenshot path, then produces a pixel-perfect 1290×2796 PNG with headline text, device frame template, and the screenshot composited inside. The verb text auto-sizes to fit the canvas width.
- **generate_frame.py** — Generates the device frame template PNG (`assets/device_frame.png`). Run once to create or update the template. The template is a 1290×2796 RGBA PNG with a black iPhone body, transparent screen cutout, Dynamic Island, and side buttons.
- **showcase.py** — Generates a showcase image showing up to 3 final screenshots side-by-side with an optional GitHub link at the bottom. Used as the final step after all screenshots are approved.
- **assets/device_frame.png** — Pre-rendered iPhone device frame template used by `compose.py`. Using a template instead of drawing the frame at compose time ensures pixel-perfect consistency across all generated screenshots.

## Skill Runtime Assumptions

- Keep the repository name unchanged.
- The root screenshot skill supports both Codex and Claude Code.
- The user's app project receives generated assets under `screenshots/` plus the resume ledger under `.agents/aso-appstore-screenshots/state.json` by default.
- Existing `.codex/aso-appstore-screenshots/state.json` and `.claude/aso-appstore-screenshots/state.json` ledgers should continue to work.
- Gemini MCP remains the image-enhancement backend.
- Codex local skill discovery is expected from `.agents/skills/` in a repo or `$HOME/.agents/skills/` for a user install.
- Claude Code local skill discovery is expected from `.claude/skills/` in a repo or `$HOME/.claude/skills/` for a user install.

## Running compose.py

```bash
# Requires: python3 -m pip install Pillow
# Requires: SF Pro Display Black at /Library/Fonts/SF-Pro-Display-Black.otf

python3 compose.py \
  --bg "#E31837" \
  --verb "TRACK" \
  --desc "TRADING CARD PRICES" \
  --screenshot path/to/simulator.png \
  --output output.png
```

## Key Design Decisions

- **Two-stage generation**: `compose.py` creates a deterministic scaffold first (text + frame + screenshot), then Nano Banana Pro enhances it. This avoids the inconsistencies of generating from scratch.
- **compose.py outputs exact App Store Connect dimensions** (1290×2796 for iPhone 6.7") for the scaffold stage.
- **Device frame is a template image** (`assets/device_frame.png`) — not drawn at compose time. Regenerate with `python3 generate_frame.py` if the frame design needs updating.
- **Verb text auto-sizes** — shrinks from 172px down to 100px to fit multi-word verbs (e.g. "TURN YOURSELF") within the canvas width.
- **SKILL.md always generates 3 versions in parallel** for each benefit so the user can pick the best one.
- **The crop/resize step in SKILL.md is mandatory** after every `generate_image` or `edit_image` call — raw Gemini output is never the correct dimensions for App Store Connect.
- **Project-local state is central to the workflow** — benefits, screenshot assessments, pairings, brand colour, and generation state are all persisted so users can resume across Codex or Claude Code conversations.

## Verification

Run these checks after prompt or packaging changes:

```bash
python3 -m py_compile compose.py generate_frame.py showcase.py
git diff --check
```

Also confirm `SKILL.md`, `README.md`, `AGENTS.md`, and `CLAUDE.md` stay aligned on which parts are Codex-specific, Claude-specific, or shared.
