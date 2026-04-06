# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code skill (`aso-appstore-screenshots`) that guides users through creating high-converting App Store screenshots. It is invoked via the `/aso-appstore-screenshots` slash command from within a user's app project.

## Architecture

Five files + one asset make up the skill:

- **SKILL.md** — The skill prompt. Defines a multi-phase workflow: Benefit Discovery → Screenshot Pairing → Generation. Uses Claude Code's memory system to persist state across conversations so users can resume mid-workflow. Generation first creates a deterministic scaffold via compose.py, then sends it to Nano Banana Pro for AI enhancement.
- **compose.py** — A standalone Python compositing script (Pillow-based) that deterministically renders App Store screenshots. Takes a background hex colour, action verb, benefit descriptor, and simulator screenshot path, then produces a pixel-perfect 1290×2796 PNG with headline text, device frame template, and the screenshot composited inside. The verb text auto-sizes to fit the canvas width.
- **resize.py** — Cross-platform crop and resize script (Pillow-based). Takes one or more images and crops them to the target aspect ratio (center-crop, top edge preserved) then resizes to exact pixel dimensions. Provides a cross-platform alternative to the macOS-only `sips` commands. Works on macOS, Linux, and Windows.
- **generate_frame.py** — Generates the device frame template PNG (`assets/device_frame.png`). Run once to create or update the template. The template is a 1290×2796 RGBA PNG with a black iPhone body, transparent screen cutout, Dynamic Island, and side buttons.
- **showcase.py** — Generates a showcase image showing up to 3 final screenshots side-by-side with an optional GitHub link at the bottom. Used as the final step after all screenshots are approved.
- **assets/device_frame.png** — Pre-rendered iPhone device frame template used by compose.py. Using a template instead of drawing the frame at compose time ensures pixel-perfect consistency across all generated screenshots.

## Running compose.py

```bash
# Requires: pip install Pillow
# Requires: SF Pro Display Black font at /Library/Fonts/SF-Pro-Display-Black.otf

python3 compose.py \
  --bg "#E31837" \
  --verb "TRACK" \
  --desc "TRADING CARD PRICES" \
  --screenshot path/to/simulator.png \
  --output output.png \
  --accent  # optional: adds dark arc behind device
```

## Running resize.py

```bash
# Requires: pip install Pillow

# Default: iPhone 6.7" (1290×2796)
python3 resize.py screenshots/01-benefit/v1.jpg screenshots/01-benefit/v2.jpg screenshots/01-benefit/v3.jpg

# Custom dimensions (e.g. iPhone 6.5")
python3 resize.py --width 1242 --height 2688 screenshots/01-benefit/v*.jpg
```

Each input file gets a `-resized` sibling (e.g. `v1.jpg` → `v1-resized.jpg`). Crops to the target aspect ratio (center-crop, top edge preserved) then resizes to exact dimensions.

## Key Design Decisions

- **Two-stage generation**: compose.py creates a deterministic scaffold first (text + frame + screenshot), then Nano Banana Pro enhances it. This avoids the inconsistencies of generating from scratch.
- **compose.py outputs exact App Store Connect dimensions** (1290×2796 for iPhone 6.7") — no post-processing crop needed.
- **Device frame is a template image** (`assets/device_frame.png`) — not drawn at compose time. Regenerate with `python3 generate_frame.py` if the frame design needs updating.
- **Verb text auto-sizes** — shrinks from 172px down to 100px to fit multi-word verbs (e.g. "TURN YOURSELF") within the canvas width.
- **SKILL.md always generates 3 versions in parallel** for each benefit so the user can pick the best one.
- **The crop/resize step in SKILL.md is mandatory** after every `generate_image` or `edit_image` call — raw Nano Banana output is never the correct dimensions for App Store Connect.
- **Memory is central to the workflow** — benefits, screenshot assessments, pairings, brand colour, and generation state are all persisted so users can resume across conversations.
