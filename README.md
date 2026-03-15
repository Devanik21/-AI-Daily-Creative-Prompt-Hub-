# AI Daily Creative Prompt Hub

![Language](https://img.shields.io/badge/Language-Python-3776AB?style=flat-square) ![Stars](https://img.shields.io/github/stars/Devanik21/-AI-Daily-Creative-Prompt-Hub-?style=flat-square&color=yellow) ![Forks](https://img.shields.io/github/forks/Devanik21/-AI-Daily-Creative-Prompt-Hub-?style=flat-square&color=blue) ![Author](https://img.shields.io/badge/Author-Devanik21-black?style=flat-square&logo=github) ![Status](https://img.shields.io/badge/Status-Active-brightgreen?style=flat-square)

> A daily fountain of creative inspiration — AI-curated, freshly generated prompts for writers, artists, musicians, and game designers, every single day.

---

**Topics:** `content-creation` · `creative-ai` · `creative-writing-prompts` · `daily-prompts` · `deep-learning` · `generative-ai` · `large-language-models` · `nlp` · `text-generation` · `inspiration-generation`

## Overview

AI Daily Creative Prompt Hub is a living creative resource that generates fresh, unique, and genuinely
inspiring prompts across multiple creative disciplines every day. Unlike static prompt databases that
repeat and feel exhausted after a few weeks of use, this platform uses generative AI to synthesise
novel prompts dynamically — drawing on an ever-expanding context of genre conventions, stylistic
constraints, thematic combinations, and creative tensions that keep prompts surprising and valuable.

The platform serves four creative communities with distinct prompt styles. Writers receive story
prompts with character seeds, setting constraints, and thematic tensions (genre × subgenre × constraint).
Visual artists receive compositional, thematic, and stylistic directives (mood × technique × subject).
Musicians receive generative constraints: a scale, a rhythmic pattern, a mood, and an unusual
instrumentation or production technique. Game designers receive mechanical constraints: a core
mechanic, a win condition, a twist, and a thematic wrapper.

A key quality feature is the Constraint Generator — inspired by the Oulipo literary movement's
productive constraints, it generates prompts with specific formal limitations (write a story where
each paragraph begins with consecutive letters of the alphabet; create a painting using only three
values; compose a melody using only the notes in a pentatonic scale). Constraints eliminate the
paralysis of infinite choice and have historically produced some of the most original creative work.

---

## Motivation

Creative blocks are universal and costly — hours, days, or weeks of productive time lost staring
at a blank page or canvas. The right prompt at the right moment can cut through that paralysis
and unlock a creative flow state. This project was built on the belief that a well-crafted, surprising
prompt is a genuine creative service — and that AI can generate those prompts at sufficient quality
and variety to serve as a daily creative companion.

---

## Architecture

```
Date + Creative Domain + Difficulty + Style Tags
        │
  Prompt Generation Engine (LLM)
  ├── Writer prompts: character + setting + tension + constraint
  ├── Visual prompts: mood + technique + subject + limitation
  ├── Music prompts: scale + rhythm + mood + instrumentation
  └── Game prompts: mechanic + win_condition + twist + theme
        │
  Quality filter (diversity check vs. recent prompts)
        │
  Daily prompt cache (one prompt per domain per day)
        │
  Streamlit display + email digest + RSS feed
```

---

## Features

### Multi-Domain Prompt Generation
Separate, domain-specific prompt generators for fiction writing, visual art, music composition, and game design — each with its own constraint vocabulary and creative tension framework.

### Constraint-Based Creativity
Oulipo-inspired formal constraints built into every prompt: specific limitations that channel creative energy rather than leaving it unfocused — producing more original work than unconstrained prompts.

### Daily Freshness Engine
Prompts generated fresh each day with a diversity constraint that prevents thematic repetition against the past 30 days' prompt history — ensuring the calendar never feels stale.

### Difficulty Scaling
Three difficulty levels per domain: Accessible (familiar techniques and subjects), Intermediate (genre-bending and technical challenge), and Advanced (formally complex or philosophically demanding constraints).

### Community Gallery
Users can submit and share their responses to prompts — creating a daily gallery of creative work inspired by the same prompt, with voting and discussion.

### Prompt Personalisation
Configure genre preferences, stylistic inclinations, and favourite artists/authors/composers — the generator incorporates these as soft constraints for personalised prompt flavour.

### Email Digest Subscription
Daily email delivery of the morning's prompts across all selected domains — arriving before breakfast to seed the creative day.

### Prompt Archive and Search
Searchable archive of all previously generated prompts with tag-based filtering — revisit past prompts, find prompts by theme, or use the archive for workshop facilitation.

---

## Tech Stack

| Library / Tool | Role | Why This Choice |
|---|---|---|
| **OpenAI GPT-4o / Gemini** | Prompt generation | Diverse, high-quality creative prompt synthesis |
| **Streamlit** | Web interface | Daily prompt display, gallery, personalisation |
| **SQLite** | Prompt archive | Daily prompt storage with deduplication |
| **pandas** | Diversity tracking | Recent prompt history for diversity constraint |
| **feedgenerator** | RSS feed | Machine-readable prompt subscription feed |
| **APScheduler** | Daily automation | Scheduled prompt generation at midnight UTC |

---

## Getting Started

### Prerequisites

- Python 3.9+ (or Node.js 18+ for TypeScript/JavaScript projects)
- A virtual environment manager (`venv`, `conda`, or equivalent)
- API keys as listed in the Configuration section

### Installation

```bash
git clone https://github.com/Devanik21/-AI-Daily-Creative-Prompt-Hub-.git
cd -AI-Daily-Creative-Prompt-Hub-
python -m venv venv && source venv/bin/activate
pip install streamlit openai google-generativeai pandas sqlite3 apscheduler python-dotenv
echo 'OPENAI_API_KEY=sk-...' > .env
# Generate today's prompts
python generate_daily_prompts.py
# Launch the hub
streamlit run app.py
```

---

## Usage

```bash
# Launch prompt hub
streamlit run app.py

# Generate prompts for a specific date
python generate_daily_prompts.py --date 2026-03-15

# Generate a custom prompt
python generate_prompt.py --domain writing --difficulty advanced --genre 'cli-fi'

# Subscribe to daily digest
python subscribe_digest.py --email your@email.com --domains writing,music

# Export prompt archive
python export_archive.py --format csv --output prompts_archive.csv
```

---

## Configuration

| Variable | Default | Description |
|---|---|---|
| `OPENAI_API_KEY` | `(required)` | LLM API key for prompt generation |
| `DEFAULT_DOMAINS` | `writing,visual,music,game` | Active creative domains |
| `DIFFICULTY_DEFAULT` | `intermediate` | Default difficulty: accessible, intermediate, advanced |
| `DIVERSITY_WINDOW_DAYS` | `30` | Days of history to check for prompt diversity |
| `GENERATE_TIME_UTC` | `00:00` | Daily prompt generation time in UTC |

> Copy `.env.example` to `.env` and populate required values before running.

---

## Project Structure

```
AI-Daily-Creative-Prompt-Hub/
├── README.md
├── requirements.txt
├── app.py
└── ...
```

---

## Roadmap

- [ ] Mobile app with morning notification delivery and swipe-to-save favourite prompts
- [ ] Workshop mode: generate a themed set of 10–20 related prompts for a creative writing class
- [ ] Prompt response AI feedback: submit your creative work and receive constructive AI feedback
- [ ] Collaborative prompts: multi-part prompts where each participant receives one constraint to contribute
- [ ] Integration with Notion, Obsidian, and Roam Research for automatic prompt insertion into personal knowledge bases

---

## Contributing

Contributions, issues, and suggestions are welcome.

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-idea`
3. Commit your changes: `git commit -m 'feat: add your idea'`
4. Push to your branch: `git push origin feature/your-idea`
5. Open a Pull Request with a clear description

Please follow conventional commit messages and add documentation for new features.

---

## Notes

Prompt quality varies with model choice — GPT-4o produces more nuanced and surprising prompts than smaller models. For maximum daily freshness, the generation time is set to midnight UTC so users in all timezones see fresh prompts at the start of their creative day. Community gallery submissions are moderated for content appropriateness before display.

---

## Author

**Devanik Debnath**  
B.Tech, Electronics & Communication Engineering  
National Institute of Technology Agartala

[![GitHub](https://img.shields.io/badge/GitHub-Devanik21-black?style=flat-square&logo=github)](https://github.com/Devanik21)
[![LinkedIn](https://img.shields.io/badge/LinkedIn-devanik-blue?style=flat-square&logo=linkedin)](https://www.linkedin.com/in/devanik/)

---

## License

This project is open source and available under the [MIT License](LICENSE).

---

*Built with curiosity, depth, and care — because good projects deserve good documentation.*
