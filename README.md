# ASO App Store Screenshots

A Claude Code skill that generates high-converting App Store screenshots for your iOS app. It analyzes your codebase, identifies core benefits, and creates professional screenshot images using AI.

## What It Does

1. **Benefit Discovery** — Analyzes your app's codebase to identify the 3-5 core benefits that drive downloads
2. **Screenshot Pairing** — Reviews your simulator screenshots, rates them, and pairs each with the best benefit
3. **Generation** — Creates polished App Store screenshots using a two-stage process: deterministic scaffolding (compose.py) + AI enhancement (Nano Banana Pro via Gemini MCP)
4. **Showcase** — Generates a preview image with all screenshots side-by-side

## Installation

### 1. Add the skill to Claude Code

```bash
claude install-skill github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots
```

### 2. Install Python dependencies

```bash
pip install Pillow
```

### 3. Font requirement

The skill uses **SF Pro Display Black** for headline text. On macOS, install it from [Apple's developer fonts](https://developer.apple.com/fonts/). The expected path is:

```
/Library/Fonts/SF-Pro-Display-Black.otf
```

On Linux/CI (or to use a different face), point the compositors at any bold
display font instead:

```bash
export ASO_FONT=/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf
```

### 4. Set up Gemini MCP (for AI enhancement)

The generation phase requires [@houtini/gemini-mcp](https://www.npmjs.com/package/@houtini/gemini-mcp) to be configured as an MCP server in Claude Code:

```bash
npm install -g @houtini/gemini-mcp
```

Then add it to your Claude Code MCP config (`~/.claude/settings.json` or project `.mcp.json`).

## Usage

From within your app's project directory, run:

```
/aso-appstore-screenshots
```

The skill will guide you through each phase interactively. Progress is saved to Claude Code's memory system, so you can resume across conversations.

## How It Works

### Scaffold → Enhance Pipeline

Rather than generating screenshots from scratch (which produces inconsistent results), the skill uses a two-stage approach:

1. **compose.py** creates a deterministic scaffold with exact text positioning, device frame, and your simulator screenshot composited inside
2. **Nano Banana Pro** (via Gemini MCP) enhances the scaffold — adding a photorealistic device frame, breakout elements, and visual polish

This ensures consistent layout across all screenshots while letting AI handle the creative enhancement.

### Offline alternative: `frame_compose.py`

`frame_compose.py` is a second, fully-deterministic compositor that needs **no
AI step**. It composites the screenshot into a device frame, floats it on a
dark radial-glow background, and sets a sentence-case headline above it —
producing an upload-ready 1290×2796 image on its own.

```bash
python3 frame_compose.py \
  --screenshot path/to/simulator.png \
  --line1 "Game night" --line2 "in your pocket" \
  --output out.png
```

It is configured entirely through environment variables:

| Variable | Default | Purpose |
|----------|---------|---------|
| `ASO_FRAME` | bundled placeholder | Path to a device frame PNG (transparent screen cutout + opaque Dynamic Island). |
| `ASO_FONT` | per-platform system font | Bold display `.ttf`/`.otf` for the headline. |
| `ASO_GLOW` | `150,92,255` | `R,G,B` of the background glow. |

> **The bundled frame is a placeholder.** `assets/frame-placeholder.png` is a
> plain, flat outline (regenerate it with `generate_frame_placeholder.py`) — it
> exists only so the script runs out of the box. For production-quality output,
> set `ASO_FRAME` to your own **photographic device render**. The screen
> rectangle is detected from the frame's alpha channel, so any frame with a
> transparent screen and an opaque island works as a drop-in replacement.

### Output

Screenshots are saved to a `screenshots/` directory in your project:

```
screenshots/
  01-benefit-slug/          ← working versions
    scaffold.png            ← deterministic compose.py output
    v1.png, v2.png, v3.png  ← AI-enhanced versions
    v1-resized.png, ...     ← cropped to App Store dimensions
  final/                    ← approved screenshots, ready to upload
    01-benefit-slug.png
    02-benefit-slug.png
  showcase.png              ← preview image with all screenshots
```

The `final/` folder contains App Store-ready screenshots at exact Apple dimensions (default: 1290×2796px for iPhone 6.7").

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill prompt — defines the multi-phase workflow |
| `compose.py` | Deterministic scaffold generator (Pillow-based) |
| `frame_compose.py` | Offline "floating device" compositor (no AI step) |
| `generate_frame.py` | Generates the device frame template |
| `generate_frame_placeholder.py` | Generates the placeholder frame for `frame_compose.py` |
| `showcase.py` | Generates the side-by-side showcase image |
| `assets/device_frame.png` | Pre-rendered iPhone device frame template |
| `assets/frame-placeholder.png` | Placeholder frame for `frame_compose.py` (replace via `ASO_FRAME`) |

## License

MIT
