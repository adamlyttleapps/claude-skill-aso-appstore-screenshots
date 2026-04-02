# CLAUDE.md

This file provides guidance to Claude Code when working with the root `aso-appstore-screenshots` skill in this repository.

## What This Is

The repository root is the `aso-appstore-screenshots` skill. It supports both Claude Code and Codex, but this file is the Claude Code-facing guidance.

## Runtime Assumptions

- Claude Code discovers the skill from `.claude/skills/aso-appstore-screenshots` in a project or `$HOME/.claude/skills/aso-appstore-screenshots` for a user install.
- The skill uses a project-local JSON ledger for resumability. Prefer `.agents/aso-appstore-screenshots/state.json`, but keep using `.codex/aso-appstore-screenshots/state.json` or `.claude/aso-appstore-screenshots/state.json` if one already exists for the app.
- Gemini MCP remains the image-enhancement backend.
- `user-invocable: true` is intentionally kept in `SKILL.md` for Claude Code compatibility.

## Architecture

The main pieces are:

- **SKILL.md** — The shared skill prompt. Defines the multi-phase workflow: Benefit Discovery → Screenshot Pairing → Generation → Showcase.
- **compose.py** — A Pillow-based compositor that renders deterministic 1290×2796 screenshot scaffolds with the headline text, device frame template, and simulator screenshot.
- **generate_frame.py** — Regenerates `assets/device_frame.png`.
- **showcase.py** — Generates the final side-by-side preview of approved screenshots.
- **assets/device_frame.png** — Pre-rendered iPhone frame template used by `compose.py`.

## Working Conventions

- Keep Claude Code and Codex support aligned instead of treating one as legacy.
- When editing runtime instructions, document Claude-specific and Codex-specific behavior separately if they differ.
- Prefer shared project-local state and shared helper scripts over runtime-specific logic in Python code.
- Do not reintroduce the old Claude memory-file workflow unless explicitly requested. The shared JSON ledger replaced it.

## Verification

Run these checks after changing the screenshot skill packaging or prompt:

```bash
python3 -m py_compile compose.py generate_frame.py showcase.py
git diff --check
```

Also confirm:

- `README.md`, `SKILL.md`, `AGENTS.md`, and `CLAUDE.md` agree on dual-runtime support
- the screenshot skill still resolves from `.agents/skills` and `.claude/skills`
- legacy `.codex` and `.claude` state ledgers remain accepted if they already exist in a consuming app
