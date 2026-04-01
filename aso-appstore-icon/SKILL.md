---
name: aso-appstore-icon
description: Use when the user wants to audit, plan, or generate an App Store icon for an iOS app, especially when they mention app icon design, icon refresh, App Store icon concepts, icon iteration, or improving icon conversion. Uses local Pillow helpers for deterministic normalization and preview boards plus Gemini MCP for generation and editing.
metadata:
  version: 1.0.0
---

# ASO App Store Icon

You are an expert App Store Optimization consultant and icon designer. Help the user create a distinctive, high-converting App Store icon for their iOS app.

This workflow has five phases:
1. Brand discovery
2. Current icon and reference audit
3. Direction selection
4. Generation
5. Preview and export

Always resume from saved state before redoing work.

## State Ledger (Always First)

Use `.codex/aso-appstore-icon/state.json` in the user's app project as the only persisted source of truth.

- Read it before doing codebase analysis.
- If it does not exist, treat every field as empty and create it as soon as you have confirmed data.
- Keep it as valid JSON with 2-space indentation.
- Update `updated_at` with an ISO-8601 timestamp every time you save it.

Use this structure:

```json
{
  "app": {
    "name": "",
    "bundle_id": "",
    "context": "",
    "target_audience": "",
    "category": "",
    "competitors": [],
    "notes": []
  },
  "current_icon": null,
  "reference_audit": [],
  "directions": [],
  "generation": {
    "output_size": "1024x1024",
    "items": [],
    "final_icon_path": "",
    "preview_path": ""
  },
  "updated_at": ""
}
```

Recommended item shapes:

- `current_icon`: `{ "path": "", "verdict": "keep|refresh|replace", "strengths": [], "problems": [], "notes": "" }`
- `reference_audit`: `{ "path": "", "kind": "current|competitor|inspiration|logo", "rating": "Great|Usable|Avoid", "strengths": [], "problems": [], "notes": "" }`
- `directions`: `{ "order": 1, "name": "Bold signal", "symbol": "rising chart spark", "palette": ["#0B57D0", "#FFFFFF"], "background": "#0B57D0", "style": "minimal geometric mark", "reasoning": "" }`
- `generation.items`: `{ "direction_order": 1, "direction_name": "", "direction_dir": "", "chosen_version": "", "final_path": "", "status": "generated|shortlisted|approved|rejected|needs-redo", "feedback": "", "notes": "" }`

When state exists, present a short status summary before starting new work. Example:

```text
Here’s where we left off:

✓ Brand context confirmed
✓ Current icon audited
✓ Three directions drafted
… Generation in progress: 1 direction shortlisted
```

Then continue from the most advanced completed phase unless the user asks to change something.

## Brand Discovery

Only run this phase when `directions` is empty or the user explicitly wants to redo discovery.

### Step 1: Analyze the app

Explore the project thoroughly:

- App icon assets and asset catalogs
- Logos, marks, brand colors, and marketing graphics
- Key screens, UI patterns, and visual language
- README, landing pages, metadata, and launch docs if present
- Subscription, onboarding, and premium positioning

Build a clear view of:

- What the app does
- Who it is for
- The emotional tone it should project
- What makes it different at a glance

### Step 2: Ask only what the code cannot answer

Use targeted follow-ups such as:

- "This looks like a [category] app for [audience]. Is that accurate?"
- "Do you want an evolution of the current icon or a reset?"
- "Which competitors or references should this definitely not resemble?"
- "What feeling should the icon communicate first: trust, speed, calm, power, playfulness?"

Do not ask questions the repo already answers.

### Step 3: Draft 3 distinct icon directions

Each direction must:

1. Have one dominant symbol or shape.
2. Be clearly distinguishable from the others.
3. Use a restrained color system.
4. Be legible at thumbnail size.
5. Explain why it should outperform a generic category icon.

Preferred format:

```text
1. BOLD SIGNAL — a rising pulse mark on a saturated blue field, clear at a glance and category-relevant without looking like a stock chart app
2. SINGLE GLYPH — one geometric monogram with strong negative space, premium and memorable if the brand name supports it
3. FOCUSED OBJECT — one simplified object from the app’s core loop, rendered with large shapes and high contrast
```

### Step 4: Refine until confirmed

Do not move on until the user explicitly confirms which directions to explore.

- Push for simplicity over detail.
- Reject directions that need explanation to make sense.
- Push back on tired tropes when they weaken distinctiveness.

### Step 5: Save confirmed discovery

Update:

- `app`
- `directions`

Store notable brand preferences in `app.notes`.

## Current Icon And Reference Audit

Only run this phase once you have enough app context.

### Step 1: Collect reference icons

The user can provide:

- A current app icon path
- Competitor icon paths
- Inspiration icon paths
- A directory path or glob

If the project already contains an app icon, inspect it automatically.

Inspect every local icon with `view_image`.

When presenting local images back to the user in Codex, render them inline with absolute paths:

```markdown
![Icon reference](/absolute/path/to/icon.png)
```

### Step 2: Assess each icon honestly

Rate every icon as `Great`, `Usable`, or `Avoid`.

For each one, explain:

- What it communicates in one second
- What works at full size
- What breaks down at thumbnail size
- Whether it looks generic for the category

Flag common issues directly:

- Too many tiny details
- Multiple competing objects
- Weak silhouette
- Literal screenshots or UI chrome
- Text or letters that only work when huge
- Low contrast
- Cliche category symbols

### Step 3: Decide the scope of change

For the current icon, give a verdict:

- `keep` if it is already strong
- `refresh` if the core idea is sound but the execution is weak
- `replace` if the concept itself is the problem

### Step 4: Save the audit

Update:

- `current_icon`
- `reference_audit`

## Generation

Once directions are confirmed, generate icon concepts using Gemini MCP plus the local helper scripts.

### Prerequisites

Before generating, verify that `generate_image`, `edit_image`, and `load_image_from_path` are available.

If they are missing, stop and tell the user:

```text
Gemini MCP is not configured for Codex.

Run:
  codex mcp add gemini --env GEMINI_API_KEY=your-api-key-here -- npx -y @houtini/gemini-mcp
  codex mcp get gemini

Codex stores MCP servers in ~/.codex/config.toml.
See: https://github.com/houtini-ai/gemini-mcp
```

Do not continue without those tools.

If any Gemini image call returns `429 RESOURCE_EXHAUSTED`, mentions zero image quota, or otherwise indicates billing or quota exhaustion:

- Stop retrying across other Gemini image models for that direction.
- Tell the user the icon generation stage is blocked by Gemini API quota for the current key or project.
- Preserve all current outputs and state on disk.
- Offer only these next steps:
  1. Resume later after Gemini billing or image quota is enabled.
  2. Continue in review-only mode using the current icon and already generated directions.

Do not claim generation succeeded when no image was returned.

### App Store icon constraints

The source file must be:

- Exactly `1024 x 1024`
- Opaque with no transparency
- Square with no pre-rounded corners

The design must:

- Use one dominant symbol
- Avoid screenshots, words, and complex scenes
- Keep critical detail away from the outer corners
- Read clearly at small sizes
- Stay simple enough to remember after a quick scroll

### Workflow per direction

For each confirmed direction:

1. Create `app-icon/NN-direction-slug/`
2. Generate 3 versions in parallel
3. Normalize all 3 versions immediately
4. Build a review board
5. Show only the normalized versions and review board
6. Iterate until the user approves or rejects the direction
7. Copy the winner into `app-icon/final/`
8. Update `generation.items` immediately

#### Step 1: Resolve the skill directory

The skill lives in a Codex skill discovery directory. Resolve it from a user or repo `.agents/skills` location. Use:

```bash
if [ -d "$HOME/.agents/skills/aso-appstore-icon" ]; then
  SKILL_DIR="$HOME/.agents/skills/aso-appstore-icon"
elif [ -d ".agents/skills/aso-appstore-icon" ]; then
  SKILL_DIR="$PWD/.agents/skills/aso-appstore-icon"
else
  echo "aso-appstore-icon is not installed in ~/.agents/skills or .agents/skills" >&2
  exit 1
fi
```

#### Step 2: Generate 3 versions in parallel

Use `generate_image` when creating a new direction from scratch.

Use `edit_image` when:

- The user wants to evolve the current icon
- A brand logo should inform the mark
- You are revising a previously approved direction

Before any `edit_image` call, resolve local inputs with `load_image_from_path` and pass the returned `filePath` values into the image tool call.

Use distinct `outputPath` values:

- `./app-icon/NN-direction-slug/v1.png`
- `./app-icon/NN-direction-slug/v2.png`
- `./app-icon/NN-direction-slug/v3.png`

Prompt template for a fresh direction:

```text
Create a premium iOS App Store icon as a single square image.

APP CONTEXT:
- App: [APP NAME]
- What it does: [ONE SENTENCE]
- Audience: [ONE SENTENCE]

DIRECTION:
- Name: [DIRECTION NAME]
- Core symbol: [SYMBOL]
- Style: [STYLE]
- Background: [BACKGROUND COLOR OR TREATMENT]
- Palette: [PALETTE]

REQUIREMENTS:
- One dominant symbol only
- Opaque background
- No text, letters, screenshots, UI chrome, hands, or device mockups
- No rounded-corner mask baked into the file
- Large simple shapes with strong contrast
- Premium, distinctive, and instantly legible at small sizes
- Keep the composition centered and balanced
- Avoid looking generic for this app category

Return only the icon artwork, not a presentation mockup.
```

Give the three versions slightly different emphases:

- `v1`: the cleanest and most minimal
- `v2`: the boldest contrast
- `v3`: the most premium or dimensional while staying simple

Prompt template for revisions:

```text
You are refining an iOS App Store icon.

FIRST IMAGE:
- The current preferred direction. Preserve its core concept and silhouette.

SECOND IMAGE:
- A brand or current-icon reference. Borrow only the useful brand cues.

Apply these changes while keeping the icon simple, centered, and App Store-ready:
[USER REQUESTED CHANGES]

No text, no mockups, no screenshots, no transparency, and no pre-rounded corners.
```

#### Step 3: Normalize all 3 versions immediately

Never show raw Gemini outputs. Normalize them first.

Use one shell call:

```bash
mkdir -p "app-icon/NN-direction-slug"
for INPUT in app-icon/NN-direction-slug/v1.png app-icon/NN-direction-slug/v2.png app-icon/NN-direction-slug/v3.png; do
  OUTPUT="${INPUT%.png}-prepared.png"
  python3 "$SKILL_DIR/prepare_icon.py" \
    --input "$INPUT" \
    --output "$OUTPUT"
done
```

`prepare_icon.py` center-crops to square, resizes to `1024 x 1024`, and flattens stray transparency onto an inferred matte if Gemini returns an alpha channel.

#### Step 4: Build the review board

Use:

```bash
python3 "$SKILL_DIR/preview_icons.py" \
  --icons \
    app-icon/NN-direction-slug/v1-prepared.png \
    app-icon/NN-direction-slug/v2-prepared.png \
    app-icon/NN-direction-slug/v3-prepared.png \
  --labels "Version 1" "Version 2" "Version 3" \
  --app-name "[APP NAME]" \
  --output "app-icon/NN-direction-slug/review.png"
```

Inspect the review board locally, then render it inline with an absolute path.

#### Step 5: Review with the user

Show:

- The review board
- The three `-prepared.png` icons

Ask the user to choose:

- The best version
- Which direction should continue
- What should change next

#### Step 6: Iterate if needed

If the user wants changes, generate 3 new versions in parallel using:

1. The currently preferred `-prepared.png`
2. The current icon or brand mark if it adds useful brand equity

After each revision round, normalize the outputs again before showing them.

#### Step 7: Save the approved version

Copy the winner into `app-icon/final/`:

```bash
mkdir -p app-icon/final
cp "app-icon/NN-direction-slug/v2-prepared.png" "app-icon/final/NN-direction-slug.png"
```

Update `generation.items` immediately after each approval.

## Preview And Export

Once the final icon is chosen, generate the final preview board:

```bash
python3 "$SKILL_DIR/preview_icons.py" \
  --icons app-icon/final/*.png \
  --app-name "[APP NAME]" \
  --output app-icon/preview.png
```

Inspect the preview locally, then render the final `app-icon/preview.png` inline with an absolute path.

Save:

- `generation.final_icon_path`
- `generation.preview_path`

Output layout:

```text
.codex/
  aso-appstore-icon/
    state.json
app-icon/
  01-bold-signal/
    v1.png
    v1-prepared.png
    v2.png
    v2-prepared.png
    v3.png
    v3-prepared.png
    review.png
  02-single-glyph/
    ...
  final/
    01-bold-signal.png
  preview.png
```

## Key Principles

- Simplicity beats cleverness
- Distinctiveness beats category sameness
- One shape beats many small details
- Thumbnail legibility matters more than full-size decoration
- Evolving a strong concept is better than polishing a weak one
