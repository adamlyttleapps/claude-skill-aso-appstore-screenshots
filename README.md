# ASO App Store Screenshots

A Claude Code skill that generates high-converting App Store screenshots for your iOS app. It analyzes your codebase, identifies the core benefits that drive downloads, and creates professional screenshot images using AI.

## What It Does

1. **Benefit Discovery** — Analyzes your app's codebase to identify the 3–5 core benefits that drive downloads, then collaborates with you to refine and confirm them
2. **Screenshot Pairing** — Reviews your simulator screenshots, rates them (Great / Usable / Retake), and pairs each with the most relevant benefit
3. **Generation** — Creates polished App Store screenshots using a two-stage pipeline: deterministic scaffolding (`compose.py`) + AI enhancement (Nano Banana Pro via Gemini MCP)
4. **Showcase** — Generates a side-by-side preview image of all final screenshots

Progress is saved to Claude Code's memory system after each phase, so you can resume across conversations without starting over.

---

## Installation

### 1. Install the skill

There is no `claude install-skill` command — skills are installed by copying a folder into `~/.claude/skills/`. Run the following one-liner in your terminal:

```bash
git clone https://github.com/adamlyttleapps/claude-skill-aso-appstore-screenshots.git /tmp/aso-skill \
  && mkdir -p ~/.claude/skills \
  && cp -r /tmp/aso-skill ~/.claude/skills/aso-appstore-screenshots \
  && rm -rf /tmp/aso-skill \
  && echo "✅ Skill installed"
```

### 2. Install Python dependencies

```bash
pip install Pillow
```

### 3. Font requirement

The skill uses **SF Pro Display Black** for headline text. On macOS, download and install it from [Apple's developer fonts page](https://developer.apple.com/fonts/). The skill expects it at:

```
/Library/Fonts/SF-Pro-Display-Black.otf
```

### 4. Set up Gemini MCP (required for AI enhancement)

The generation phase requires the [`@houtini/gemini-mcp`](https://www.npmjs.com/package/@houtini/gemini-mcp) MCP server. You need to configure it in both **Claude Desktop** and **Claude Code CLI** separately — they use different configuration systems.

You will need a **Gemini API key**, which you can obtain from [Google AI Studio](https://aistudio.google.com/app/apikey).

---

#### Claude Desktop

Edit the Claude Desktop configuration file for your OS:

- **macOS:** `~/Library/Application Support/Claude/claude_desktop_config.json`
- **Windows:** `C:\Users\{username}\AppData\Roaming\Claude\claude_desktop_config.json`

Add the following entry inside `mcpServers` (create the file if it doesn't exist):

```json
{
  "mcpServers": {
    "gemini": {
      "command": "npx",
      "args": ["@houtini/gemini-mcp"],
      "env": {
        "GEMINI_API_KEY": "your-api-key-here"
      }
    }
  }
}
```

> `npx` fetches the package automatically on first run — no separate `npm install` needed. Restart Claude Desktop after saving the file.

**Tip (macOS shortcut):** Open Claude Desktop → menu bar → **Claude** → **Settings** → **Developer** → **Edit Config**. This opens the file in your default editor and creates it if it doesn't exist.

---

#### Claude Code CLI

Claude Code CLI uses a separate configuration file at `~/.claude.json`. The easiest way to add the server is with the built-in `claude mcp add` command:

```bash
claude mcp add --scope user \
  --transport stdio \
  --env GEMINI_API_KEY=your-api-key-here \
  gemini -- npx @houtini/gemini-mcp
```

This registers the server globally (available in all your projects). To verify it was added correctly:

```bash
claude mcp list
```

You should see `gemini` listed. No restart required — the server is picked up automatically on the next Claude Code session.

> **Alternative (manual edit):** If you prefer to edit the config file directly, open `~/.claude.json` and add the `gemini` entry inside the top-level `mcpServers` object:
>
> ```json
> {
>   "mcpServers": {
>     "gemini": {
>       "command": "npx",
>       "args": ["@houtini/gemini-mcp"],
>       "env": {
>         "GEMINI_API_KEY": "your-api-key-here"
>       }
>     }
>   }
> }
> ```

---

## Usage

Open a Claude Code session inside your app's project directory and run:

```
/aso-appstore-screenshots
```

The skill will guide you through each phase interactively. If you've run it before, it will check memory first and offer to resume from where you left off.

---

## How It Works

### Scaffold → Enhance Pipeline

Rather than generating screenshots from scratch (which produces inconsistent results), the skill uses a two-stage approach:

1. **`compose.py`** creates a deterministic scaffold with exact text positioning, device frame placement, and your simulator screenshot composited inside — ensuring consistent layout across all screenshots
2. **Nano Banana Pro** (via Gemini MCP) enhances the scaffold — adding a photorealistic device frame, breakout elements, and visual polish

This separation means layout is always predictable and repeatable, while the AI handles the creative enhancement.

### Output

Screenshots are saved to a `screenshots/` directory in your project root:

```
screenshots/
  01-benefit-slug/          ← working files for benefit 1
    scaffold.png            ← deterministic compose.py output
    v1.jpg, v2.jpg, v3.jpg  ← AI-enhanced versions
    v1-resized.jpg, ...     ← cropped to App Store dimensions
  02-benefit-slug/
    ...
  final/                    ← approved screenshots, ready to upload
    01-benefit-slug.jpg
    02-benefit-slug.jpg
  showcase.png              ← side-by-side preview of the full set
```

The `final/` folder is the only one you need to care about — it contains one approved, App Store-ready screenshot per benefit, at exact Apple dimensions (default: 1290×2796px for iPhone 6.7").

---

## Files

| File | Purpose |
|---|---|
| `SKILL.md` | The skill prompt — defines the multi-phase workflow |
| `compose.py` | Deterministic scaffold generator (Pillow-based) |
| `generate_frame.py` | Generates the device frame template |
| `showcase.py` | Generates the side-by-side showcase image |
| `assets/device_frame.png` | Pre-rendered iPhone device frame template |

---

## License

MIT
