---
name: aso-appstore-screenshots
description: Use when the user wants to plan, critique, or generate App Store screenshots for an iOS app, especially when they mention ASO screenshots, screenshot pairing, simulator screenshots, benefit headlines, or App Store screenshot design. Uses compose.py for deterministic scaffolds and Gemini MCP for image enhancement.
user-invocable: true
metadata:
  version: 1.0.0
---

# ASO App Store Screenshots

You are an expert App Store Optimization consultant and screenshot designer. Help the user build a cohesive, high-converting App Store screenshot set for their iOS app.

This workflow has four phases:
1. Benefit discovery
2. Screenshot pairing
3. Generation
4. Showcase

Always resume from saved state before redoing work.

## State Ledger (Always First)

Use a project-local JSON ledger as the persisted source of truth.

Resolve the ledger path in this order:

1. `.agents/aso-appstore-screenshots/state.json` if it already exists
2. `.codex/aso-appstore-screenshots/state.json` if it already exists
3. `.claude/aso-appstore-screenshots/state.json` if it already exists
4. Otherwise create `.agents/aso-appstore-screenshots/state.json`

- Read it before doing any codebase analysis.
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
    "competitors": [],
    "notes": []
  },
  "benefits": [],
  "screenshot_analysis": [],
  "pairings": [],
  "brand_color": null,
  "generation": {
    "target_display": "",
    "dimensions": "",
    "items": [],
    "showcase_path": ""
  },
  "updated_at": ""
}
```

Recommended item shapes:

- `benefits`: `{ "order": 1, "verb": "TRACK", "descriptor": "TRADING CARD PRICES", "headline": "TRACK TRADING CARD PRICES", "reasoning": "" }`
- `screenshot_analysis`: `{ "path": "", "screen": "", "rating": "Great|Usable|Retake", "strengths": [], "problems": [], "notes": "" }`
- `pairings`: `{ "benefit_order": 1, "headline": "", "screenshot_path": "", "reasoning": "" }`
- `brand_color`: `{ "name": "", "hex": "", "reasoning": "" }`
- `generation.items`: `{ "benefit_order": 1, "headline": "", "benefit_dir": "", "chosen_version": "", "final_path": "", "source_screenshot": "", "breakout_notes": "", "status": "generated|approved|needs-redo", "feedback": "" }`

When state exists, present a short status summary before starting new work. Example:

```text
Here’s where we left off:

✓ Benefits confirmed (3)
✓ Screenshots analysed (5)
✓ Pairings confirmed
✓ Brand colour chosen: Electric Blue (#2563EB)
… Generation in progress: 2 of 3 approved
```

Then continue from the most advanced completed phase unless the user asks to change something.

## Benefit Discovery

Only run this phase when `benefits` is empty or the user explicitly wants to redo discovery.

### Step 1: Analyze the app

Explore the project thoroughly:

- UI files, screens, view controllers, and components
- Models and data structures
- Feature flags, subscriptions, paywalls, and premium flows
- Onboarding and empty states
- App name, bundle ID, and in-app marketing copy
- README, metadata files, App Store copy, or launch docs if present

Build a clear view of:

- What the app does
- Who it is for
- What problem it solves
- What makes it different

### Step 2: Ask only what the code cannot answer

Use targeted follow-ups such as:

- "Based on the code, this looks like [X]. Is that accurate?"
- "Who is the target audience?"
- "What is the #1 reason someone downloads this app?"
- "Who are the main competitors?"
- "What do users love most?"

Do not ask questions the repo already answers.

### Step 3: Draft 3-5 core benefits

Each benefit must:

1. Start with a strong action verb.
2. Focus on the user outcome, not the implementation.
3. Stay specific enough to matter at thumbnail size.
4. Answer "Why should I download this instead of scrolling past?"

Preferred format:

```text
1. TRACK TRADING CARD PRICES — specific, instantly valuable, and easy to visualize
2. SEARCH ANY CARD IN SECONDS — strong speed benefit with clear intent
3. BUILD YOUR COLLECTION SMARTER — speaks to progress and organization
```

### Step 4: Refine until confirmed

Do not move on until the user explicitly confirms the final benefit set.

- Suggest better verbs if the user picks generic wording.
- Reorder benefits if a stronger value prop should lead.
- Push for specificity over bland claims.

### Step 5: Save confirmed benefits

Update:

- `app`
- `benefits`

Store notable wording preferences or rationale in `app.notes`.

## Screenshot Pairing

Only run this phase once benefits are confirmed.

### Step 1: Collect simulator screenshots

The user can provide:

- A directory path
- Individual file paths
- A glob pattern

Inspect every local screenshot with the local-image tool available in the current runtime.

- In Codex, use `view_image` and render local images inline with absolute paths when showing options back to the user.
- In Claude Code, use the local image preview or file-reading workflow available in that runtime.

### Step 2: Assess each screenshot honestly

Rate every screenshot as `Great`, `Usable`, or `Retake`.

For each one, explain:

- What screen it shows
- What works
- What hurts conversion
- The verdict

Flag common issues directly:

- Empty states or placeholder content
- Sparse or low-signal data
- Debug or developer UI
- Messy status bars
- Settings, login, onboarding, or other low-conversion screens
- Dark/light mode inconsistency across the set

### Step 3: Coach retakes precisely

For every `Retake`, tell the user:

- Which exact screen to capture
- What content state it should show
- Which appearance to use
- How full or visually rich the screen should feel
- To clean the status bar and use realistic data

### Step 4: Pair screenshots to benefits

For each benefit, pair the strongest `Great` or `Usable` screenshot using:

- Relevance
- Visual impact
- Thumbnail clarity
- Variety across the set

If a benefit has no suitable screenshot, say so clearly and repeat the retake guidance for that benefit.

### Step 5: Confirm and save

Do not proceed to generation until the user confirms pairings.

Update:

- `screenshot_analysis`
- `pairings`

## Generation

Once benefits and pairings are confirmed, generate the final screenshots using Gemini MCP plus the local scaffold scripts.

### Prerequisites

Before generating, verify that `generate_image`, `edit_image`, and `load_image_from_path` are available.

If they are missing, stop and tell the user:

```text
Gemini MCP is not configured for this runtime.

For Codex, run:
  codex mcp add gemini --env GEMINI_API_KEY=your-api-key-here -- npx -y @houtini/gemini-mcp
  codex mcp get gemini

Codex stores MCP servers in ~/.codex/config.toml.

For Claude Code, configure an MCP server that runs:
  env GEMINI_API_KEY=your-api-key-here VERBOSE=true -- npx -y @houtini/gemini-mcp

Use ~/.claude/settings.json for a user-level server or project .mcp.json for a repo-local server.
See: https://github.com/houtini-ai/gemini-mcp
```

Do not continue without those tools.

If any Gemini image call returns `429 RESOURCE_EXHAUSTED`, mentions zero image quota, or otherwise indicates billing or quota exhaustion:

- Stop retrying across other Gemini image models for that benefit.
- Tell the user the enhancement stage is blocked by Gemini API quota for the current key or project.
- Preserve the scaffold and current state on disk.
- Offer only these next steps:
  1. Resume later after Gemini billing or image quota is enabled.
  2. Continue in scaffold-only mode, knowing the result will be the deterministic base render rather than the polished enhanced creative.

Do not claim generation succeeded when no edited image was returned.

### App Store Connect dimensions

App Store Connect requires exact dimensions.

| Display | Portrait | Landscape |
|---------|----------|-----------|
| iPhone 6.5" | 1242 x 2688 | 2688 x 1242 |
| iPhone 6.7" | 1290 x 2796 | 2796 x 1290 |
| iPhone 6.9" | 1320 x 2868 | 2868 x 1320 |

Default to `1290 x 2796` unless the user asks for another slot.

Because Gemini works with standard aspect ratios, generate wider portrait images at `9:16`, then crop and resize to exact Apple dimensions.

### Visual specification

Keep the full set visually consistent:

- The action verb is the largest text element.
- The descriptor is smaller but still bold and uppercase.
- Use a heavy sans-serif look.
- Keep all text well inside the center safe area so side-cropping never clips it.
- Use a modern black iPhone mockup.
- Position the device high on the canvas so the bottom bleeds off-screen.
- Use breakout elements only when there is an obvious UI panel that strengthens the headline.
- Keep the background as a flat, bold brand color with no gradients or glow effects.

### Determine the brand color automatically

Do not ask the user to choose a background color first.

Pick one color that:

- Complements the app UI
- Stands out at thumbnail size
- Matches the app's tone
- Avoids white, light gray, or low-contrast choices

Present the recommendation briefly, allow override if the user wants one, then save it to `brand_color`.

### Generation workflow per benefit

For each confirmed benefit:

1. Create `screenshots/NN-benefit-slug/`
2. Render one local scaffold with `compose.py`
3. Generate 3 enhanced versions in parallel with `edit_image`
4. Crop and resize all 3 versions immediately
5. Show only the resized versions
6. Iterate until approved
7. Copy the winner into `screenshots/final/`
8. Update `generation.items` immediately

#### Step 1: Build the scaffold

The skill can live in a Codex or Claude Code skill discovery directory. Resolve it from the runtime-specific or shared locations. Use:

```bash
if [ -d "$HOME/.agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.agents/skills/aso-appstore-screenshots"
elif [ -d ".agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.agents/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.claude/skills/aso-appstore-screenshots"
elif [ -d ".claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.claude/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.codex/skills/aso-appstore-screenshots"
elif [ -d ".codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.codex/skills/aso-appstore-screenshots"
else
  echo "aso-appstore-screenshots is not installed in a supported skill directory" >&2
  exit 1
fi
mkdir -p "screenshots/NN-[benefit-slug]"
python3 "$SKILL_DIR/compose.py" \
  --bg "[HEX CODE]" \
  --verb "[VERB]" \
  --desc "[DESCRIPTOR]" \
  --screenshot "[path/to/simulator.png]" \
  --output "screenshots/NN-[benefit-slug]/scaffold.png"
```

This scaffold is an internal intermediate. Do not show it to the user.

#### Step 2: Load local images for Gemini

Before any `edit_image` call, resolve local inputs with `load_image_from_path` and pass the returned `filePath` values into the image tool call.

Use:

- The current scaffold
- The first approved final screenshot as the style template for screenshots 2+
- The currently approved direction image during revisions

#### Step 3: Generate 3 versions in parallel

Make 3 parallel `edit_image` calls for the current benefit.

If the first generation attempt for that benefit fails with a quota or billing exhaustion error, stop the fan-out and do not keep probing alternate models for the same request.

Use distinct `outputPath` values:

- `./screenshots/NN-[benefit-slug]/v1.jpg`
- `./screenshots/NN-[benefit-slug]/v2.jpg`
- `./screenshots/NN-[benefit-slug]/v3.jpg`

For screenshot 1, use only the scaffold as input.

Prompt template for screenshot 1:

```text
This is a SCAFFOLD for an App Store screenshot. It defines the correct headline text, device position, and in-app screenshot placement.

KEEP EXACTLY AS-IS:
- The headline wording, position, and approximate size
- The app screenshot shown on the phone screen
- The background colour

ENHANCE AND POLISH:
- Replace the placeholder device frame with a photorealistic modern iPhone mockup while keeping the same position and size
- Raise the overall polish to a professional App Store marketing screenshot
- Only add a primary breakout if there is an obvious UI panel that directly reinforces the headline
- If a breakout is used, keep it at the same vertical position and orientation as the in-app source, scale it up dramatically, extend it beyond both edges of the phone, and add a soft drop shadow
- Optionally add 1-2 restrained secondary elements that strengthen the story without clutter
- Keep the background flat and bold with no gradients, glow, or light effects
- Keep the text crisp and highly readable

The result should look like a premium App Store screenshot set by a professional ASO design agency. No watermarks, no extra text, no store chrome.
```

For screenshots 2+, use both the scaffold and the first approved screenshot as the style template.

Prompt template for screenshots 2+:

```text
You are creating the next screenshot in an App Store screenshot set.

FIRST IMAGE:
- The scaffold. It defines layout, headline wording, device placement, and screen content.

SECOND IMAGE:
- The approved style template. Match it exactly for phone rendering, shadows, text treatment, polish, and overall design language.

REQUIREMENTS:
- Keep the scaffold's layout
- Match the style template's photorealistic device frame as closely as possible
- Keep the background flat and bold with no gradients or glow
- Only use a breakout when there is an obvious UI panel that reinforces the headline
- If a breakout is used, enlarge it, keep it aligned to the original screen position, extend it beyond both phone edges, and add a soft drop shadow
- Keep the result cohesive with the template when viewed side-by-side in the App Store

No watermarks, no extra text, no store chrome.
```

If Gemini drifts on text, layout, or set consistency, regenerate.

#### Step 4: Crop and resize all 3 versions immediately

Never show the raw Gemini outputs. Crop and resize them first.

Use one shell call:

```bash
TARGET_W=1290 && TARGET_H=2796 && \
for INPUT in screenshots/NN-[benefit-slug]/v1.jpg screenshots/NN-[benefit-slug]/v2.jpg screenshots/NN-[benefit-slug]/v3.jpg; do
  OUTPUT="${INPUT%.jpg}-resized.jpg"
  cp "$INPUT" "$OUTPUT"
  W=$(sips -g pixelWidth "$OUTPUT" | tail -1 | awk '{print $2}')
  H=$(sips -g pixelHeight "$OUTPUT" | tail -1 | awk '{print $2}')
  CROP_W=$(python3 -c "print(round($H * $TARGET_W / $TARGET_H))")
  OFFSET_X=$(python3 -c "print(round(($W - $CROP_W) / 2))")
  sips --cropOffset 0 $OFFSET_X --cropToHeightWidth $H $CROP_W "$OUTPUT"
  sips -z $TARGET_H $TARGET_W "$OUTPUT"
done
```

Target dimensions:

- iPhone 6.5": `TARGET_W=1242 TARGET_H=2688`
- iPhone 6.7": `TARGET_W=1290 TARGET_H=2796`
- iPhone 6.9": `TARGET_W=1320 TARGET_H=2868`

#### Step 5: Review with the user

Show only the `-resized.jpg` versions.

Render them inline with absolute paths and label them clearly as Version 1, Version 2, and Version 3.

#### Step 6: Iterate if needed

If the user wants changes, generate 3 new versions in parallel using 3 inputs:

1. The scaffold
2. The first approved screenshot in `screenshots/final/`
3. The currently preferred version for this benefit

Use this revision prompt:

```text
Here are three reference images:

- FIRST: the scaffold. Keep the layout from this.
- SECOND: the approved style template. Match its phone rendering and overall style exactly.
- THIRD: the currently approved direction for this screenshot. Keep its breakout and creative direction unless requested otherwise.

Generate a new version that keeps the scaffold layout, the style template rendering, and the approved creative direction, with these requested changes:
[USER REQUESTED CHANGES]
```

After each revision round, crop and resize all 3 outputs before showing them again.

#### Step 7: Save the approved version

Copy the winner into `screenshots/final/`:

```bash
mkdir -p screenshots/final
cp "screenshots/NN-[benefit-slug]/v2-resized.jpg" "screenshots/final/NN-[benefit-slug].jpg"
```

Update `generation.items` immediately after each approval.

### Output layout

```text
.agents/
  aso-appstore-screenshots/
    state.json
screenshots/
  01-track-card-prices/
    scaffold.png
    v1.jpg
    v1-resized.jpg
    v2.jpg
    v2-resized.jpg
    v3.jpg
    v3-resized.jpg
  02-search-any-card/
    scaffold.png
    ...
  final/
    01-track-card-prices.jpg
    02-search-any-card.jpg
  showcase.png
```

Tell the user which App Store Connect display slot each final screenshot fits.

## Showcase

Once all final screenshots are approved, generate the showcase:

```bash
if [ -d "$HOME/.agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.agents/skills/aso-appstore-screenshots"
elif [ -d ".agents/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.agents/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.claude/skills/aso-appstore-screenshots"
elif [ -d ".claude/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.claude/skills/aso-appstore-screenshots"
elif [ -d "$HOME/.codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$HOME/.codex/skills/aso-appstore-screenshots"
elif [ -d ".codex/skills/aso-appstore-screenshots" ]; then
  SKILL_DIR="$PWD/.codex/skills/aso-appstore-screenshots"
else
  echo "aso-appstore-screenshots is not installed in a supported skill directory" >&2
  exit 1
fi
python3 "$SKILL_DIR/showcase.py" \
  --screenshots screenshots/final/01-*.jpg screenshots/final/02-*.jpg screenshots/final/03-*.jpg \
  --github "github.com/adamlyttleapps" \
  --output screenshots/showcase.png
```

Inspect the showcase locally, then render the final `screenshots/showcase.png` inline with an absolute path.

Save the final showcase path into `generation.showcase_path`.

## Key Principles

- Benefits over implementation details
- Specific beats generic
- Strong action verbs beat passive wording
- The first screenshot must communicate the biggest reason to download
- The full set must feel like one coherent campaign
- Never use empty, low-signal, or unconvincing screenshots
