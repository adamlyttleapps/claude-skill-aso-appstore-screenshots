# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What This Is

A Claude Code skill (`aso-appstore-screenshots`) that guides users through creating high-converting App Store and Google Play Store screenshots. Supports iOS (iPhone) and Android device frames. It is invoked via the `/aso-appstore-screenshots` slash command from within a user's app project.

## Architecture

Four files + two assets make up the skill:

- **SKILL.md** — The skill prompt. Defines a multi-phase workflow: Benefit Discovery → Screenshot Pairing → Generation. Uses Claude Code's memory system to persist state across conversations so users can resume mid-workflow. Generation first creates a deterministic scaffold via compose.py, then sends it to Nano Banana Pro for AI enhancement.
- **compose.py** — A standalone Python compositing script (Pillow-based) that deterministically renders store screenshots. Accepts a `--device` flag to select the target device profile (`iphone-6.7`, `iphone-6.5`, `iphone-6.9`, or `android`). Takes a background hex colour, action verb, benefit descriptor, and screenshot path, then produces a pixel-perfect PNG at the correct store dimensions with headline text, device frame template, and the screenshot composited inside. Typography sizes scale proportionally to canvas width.
- **generate_frame.py** — Generates device frame template PNGs. Accepts `--device` flag: `iphone` (default), `android`, or `all`. iPhone template has Dynamic Island and side buttons; Android template has a punch-hole camera and thin bezels.
- **showcase.py** — Generates a showcase image showing up to 3 final screenshots side-by-side with an optional GitHub link at the bottom. Used as the final step after all screenshots are approved.
- **assets/device_frame.png** — Pre-rendered iPhone device frame template used by compose.py.
- **assets/device_frame_android.png** — Pre-rendered Android device frame template used by compose.py.

## Running compose.py

```bash
# Requires: pip install Pillow
# Requires: SF Pro Display Black font at /Library/Fonts/SF-Pro-Display-Black.otf

# iPhone (default)
python3 compose.py \
  --bg "#E31837" \
  --verb "TRACK" \
  --desc "TRADING CARD PRICES" \
  --screenshot path/to/simulator.png \
  --output output.png

# Android
python3 compose.py \
  --bg "#E31837" \
  --verb "TRACK" \
  --desc "TRADING CARD PRICES" \
  --screenshot path/to/emulator.png \
  --output output.png \
  --device android
```

## Key Design Decisions

- **Two-stage generation**: compose.py creates a deterministic scaffold first (text + frame + screenshot), then Nano Banana Pro enhances it. This avoids the inconsistencies of generating from scratch.
- **compose.py outputs exact store dimensions** — 1290×2796 for iPhone 6.7", 1080×1920 for Android, etc. Each device profile has its own canvas size, device proportions, and typography scaling.
- **Device frames are template images** — `assets/device_frame.png` (iPhone) and `assets/device_frame_android.png` (Android). Regenerate with `python3 generate_frame.py --device all` if the frame designs need updating.
- **Verb text auto-sizes** — scales proportionally to canvas width to fit multi-word verbs within the canvas.
- **SKILL.md always generates 3 versions in parallel** for each benefit so the user can pick the best one.
- **The crop/resize step in SKILL.md is mandatory** after every `generate_image` or `edit_image` call — raw Nano Banana output is never the correct dimensions for store upload.
- **Memory is central to the workflow** — platform, benefits, screenshot assessments, pairings, brand colour, and generation state are all persisted so users can resume across conversations.
