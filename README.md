# ASO App Store Screenshots

A Claude Code skill that generates high-converting App Store screenshots for your iOS app. It analyzes your codebase, identifies core benefits, and creates professional screenshot images using AI.

## What It Does

1. **Benefit Discovery** — Analyzes your app's codebase to identify the 3-5 core benefits that drive downloads
2. **Localization** — Optionally translates the screenshot headlines into multiple languages, with back-translation verification so you can confirm the meaning is preserved before generating
3. **Screenshot Pairing** — Reviews your simulator screenshots, rates them, and pairs each with the best benefit
4. **Generation** — Creates polished App Store screenshots using a two-stage process: deterministic scaffolding (compose.py) + AI enhancement (Nano Banana Pro via Gemini MCP)
5. **Showcase** — Generates a preview image with all screenshots side-by-side

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

The skill defaults to **SF Pro Display Black** for headline text. On macOS, install it from [Apple's developer fonts](https://developer.apple.com/fonts/). The expected path is:

```
/Library/Fonts/SF-Pro-Display-Black.otf
```

You can also use any custom font installed in `/Library/Fonts/`. The skill will ask which font you'd like during the generation phase. To use a custom font, just provide the filename (e.g., `Inter-Black.otf`, `Montserrat-Black.ttf`).

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

### Localization

After benefit discovery, the skill can localize your screenshot headlines into multiple languages:

1. **Pick languages** — Default is English only. You can request any combination (e.g. `english, french, german, ukrainian`).
2. **Validation** — Only languages written in **Latin or Cyrillic script** are supported (the font pipeline can't reliably render other scripts). Unsupported languages such as Japanese, Chinese, Korean, Arabic, Hebrew, Thai, or Greek are rejected with a clear reason. Each accepted language is mapped to its ISO 639-1 code.
3. **Translation + back-translation** — Each benefit's action verb and descriptor are translated, then back-translated into English so you can confirm the meaning is preserved before any images are generated. You can edit or request alternatives for any line.
4. **Per-language sets** — Generation runs one language at a time, producing a cohesive, App Store-ready set per locale. Each language keeps its own style template so source-language text never leaks into translated screenshots.

### Output

Screenshots are saved to a `screenshots/` directory in your project, organised by language then benefit:

```
screenshots/
  en/                       ← working versions for English
    01-benefit-slug/
      scaffold.png          ← deterministic compose.py output
      v1.jpg, v2.jpg, v3.jpg          ← AI-enhanced versions
      v1-resized.jpg, ...             ← cropped to App Store dimensions
  fr/                       ← working versions for French (translated headlines)
    01-benefit-slug/
      ...
  final/                    ← approved screenshots, ready to upload
    en/
      01-benefit-slug.jpg
      02-benefit-slug.jpg
    fr/
      01-benefit-slug.jpg
      02-benefit-slug.jpg
  showcase-en.png           ← preview image per language
  showcase-fr.png
```

Each `final/<lang>/` folder contains App Store-ready screenshots at exact Apple dimensions (default: 1290×2796px for iPhone 6.7") and maps directly to one App Store Connect locale slot. If you only generate English, you'll simply have a single `en/` folder.

## Files

| File | Purpose |
|------|---------|
| `SKILL.md` | The skill prompt — defines the multi-phase workflow |
| `compose.py` | Deterministic scaffold generator (Pillow-based) |
| `generate_frame.py` | Generates the device frame template |
| `showcase.py` | Generates the side-by-side showcase image |
| `assets/device_frame.png` | Pre-rendered iPhone device frame template |

## License

MIT
