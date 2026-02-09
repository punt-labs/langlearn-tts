# Language Learning Prompts for Claude Desktop

These prompts transform Claude into a personalized language tutor that generates audio on-the-fly using the langlearn-tts MCP server.

## How to Use

### From the CLI

```bash
# List all available prompts
langlearn-tts prompt list

# Print a prompt (pipe to clipboard with pbcopy on macOS)
langlearn-tts prompt show german-high-school | pbcopy
```

### Setting up Claude Desktop

1. Install and configure langlearn-tts with Claude Desktop (see main [README](../../../README.md))
2. In Claude Desktop, create a **Project** for your language:
   - Click the **Projects** icon in the sidebar
   - Click **Create Project**
   - Name it (e.g., "German Lessons with Herr Schmidt")
3. Open the project, then click **Set custom instructions** (or the pencil icon next to "Instructions")
4. Paste the prompt content into the Instructions field
5. Start a new conversation within that project — Claude adopts the tutor persona

Using a Project (rather than global Settings > Instructions) keeps the tutor persona scoped to language learning conversations. Your other Claude conversations remain unaffected.

## Prompt Design

Each prompt is built on [Mollick & Mollick's "Assigning AI" framework](https://ssrn.com/abstract=4475995), which defines seven pedagogical roles for AI. These prompts combine three roles:

- **AI-tutor** — structured lessons, Socratic questioning, adapts to student level
- **AI-coach** — gives feedback on errors, prompts self-correction, doesn't just hand answers out
- **AI-simulator** — creates realistic conversation scenarios for immersive practice

The langlearn-tts MCP server acts as the **AI-tool** layer, generating pronunciation audio that the tutor weaves into lessons naturally.

## Pedagogical Foundations

Prompts are calibrated by level using established second-language acquisition principles:

| Level | Approach | Focus |
|-------|----------|-------|
| High school | Krashen's i+1, high scaffolding, L1 support | Vocabulary building, basic grammar, survival phrases |
| University 1st year | Communicative Language Teaching, moderate scaffolding | Functional conversations, grammar patterns, reading |
| University 2nd year | Task-based learning, reduced scaffolding | Extended discourse, composition, cultural fluency |
| Advanced | Content-based instruction, minimal scaffolding | Literature, debate, professional contexts, nuance |

## Available Prompts

### German
- [`german-high-school.md`](german-high-school.md) — Herr Schmidt, high school beginners
- [`german-university-1st-year.md`](german-university-1st-year.md) — Professorin Weber, 1st year university
- [`german-university-2nd-year.md`](german-university-2nd-year.md) — Professor Hartmann, 2nd year university
- [`german-advanced.md`](german-advanced.md) — Professor Becker, advanced university

### Spanish
- [`spanish-high-school.md`](spanish-high-school.md) — Profesora Elena, high school beginners
- [`spanish-university-1st-year.md`](spanish-university-1st-year.md) — Profesor Garcia, 1st year university
- [`spanish-university-2nd-year.md`](spanish-university-2nd-year.md) — Profesora Carmen, 2nd year university
- [`spanish-advanced.md`](spanish-advanced.md) — Profesora Reyes, advanced university

### French
- [`french-high-school.md`](french-high-school.md) — Madame Moreau, high school beginners
- [`french-university-1st-year.md`](french-university-1st-year.md) — Professeur Laurent, 1st year university
- [`french-university-2nd-year.md`](french-university-2nd-year.md) — Professeur Dubois, 2nd year university
- [`french-advanced.md`](french-advanced.md) — Professeur Beaumont, advanced university

### Russian
- [`russian-high-school.md`](russian-high-school.md) — Irina Petrovna, high school beginners
- [`russian-university-1st-year.md`](russian-university-1st-year.md) — Professor Dmitri, 1st year university
- [`russian-university-2nd-year.md`](russian-university-2nd-year.md) — Professor Natasha, 2nd year university
- [`russian-advanced.md`](russian-advanced.md) — Professor Mikhail, advanced university

### Korean
- [`korean-high-school.md`](korean-high-school.md) — Kim-seonsaengnim, high school beginners
- [`korean-university-1st-year.md`](korean-university-1st-year.md) — Professor Park, 1st year university
- [`korean-university-2nd-year.md`](korean-university-2nd-year.md) — Professor Kim, 2nd year university
- [`korean-advanced.md`](korean-advanced.md) — Professor Yoon, advanced university

### Japanese
- [`japanese-high-school.md`](japanese-high-school.md) — Tanaka-sensei, high school beginners
- [`japanese-university-1st-year.md`](japanese-university-1st-year.md) — Yamamoto-sensei, 1st year university
- [`japanese-university-2nd-year.md`](japanese-university-2nd-year.md) — Suzuki-sensei, 2nd year university
- [`japanese-advanced.md`](japanese-advanced.md) — Mori-sensei, advanced university

### Chinese (Mandarin)
- [`chinese-high-school.md`](chinese-high-school.md) — Laoshi Wang, high school beginners
- [`chinese-university-1st-year.md`](chinese-university-1st-year.md) — Professor Chen, 1st year university
- [`chinese-university-2nd-year.md`](chinese-university-2nd-year.md) — Professor Zhang, 2nd year university
- [`chinese-advanced.md`](chinese-advanced.md) — Professor Wei, advanced university

## Customization

These prompts are starting points. Adjust:

- **Student background** — change native language, prior language experience, interests
- **Voice selection** — the server auto-selects voices, but you can override with provider-specific voice names if needed
- **Pace** — change the speech rate (default 90%) up or down
- **Focus areas** — add specific goals (business vocabulary, exam prep, travel, etc.)
