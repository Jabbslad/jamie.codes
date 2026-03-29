+++
title = "How Boris Cherny's Team Uses Claude Code to Build Claude Code"
date = "2026-03-29"
description = "Around 90% of Claude Code is written by Claude Code itself. How Boris Cherny's team at Anthropic built a billion-dollar product using the tool it ships."
tags = ["ai", "engineering", "developer-tools", "anthropic"]

[extra]
comment = false
hero_image = "/images/claude-code-builds-claude-code-hero.png"
hero_image_alt = "A surreal panoramic landscape with enormous floating orbs above ancient architecture, evoking recursive creation"
+++

Around 90% of Claude Code is written by Claude Code itself, making it one of the most striking examples of recursive software development in the industry. Boris Cherny, who created Claude Code as a side project in his first month at Anthropic in September 2024, now leads a team where prototypes have replaced PRDs, every team member codes (including designers, PMs, and the finance lead), and the creator himself hasn't written a single line of code by hand since November 2025. What began as a bash script hitting the Claude API has grown into a product responsible for **4% of all public GitHub commits** and over $1 billion in annual recurring revenue — built almost entirely by the AI tool it ships.

<!-- more -->

## From a bash script to a billion-dollar product

Boris Cherny joined Anthropic in September 2024 after five years at Meta, where he rose to Principal Engineer (IC8) at Instagram. His first PR at Anthropic was rejected — not for code quality, but because he wrote it by hand. His ramp-up buddy Adam Wolf told him: "You wrote this by hand. What are you doing?" That cultural shock set the stage for what came next.

Within his first month, Boris prototyped a terminal tool using the Claude 3.6 model. The first version could use AppleScript to tell him what music he was listening to. After a conversation with **Cat Wu** (now the product's founding PM), he gave the terminal filesystem access and bash tools. "Suddenly, this agent was really interesting. I ran it in our codebase, and Claude started exploring the filesystem — reading one file, looking at the imports, then reading the files defined in those imports," Boris recalled on The Pragmatic Engineer podcast. He recognized what he calls **"product overhang"** — the model could already do far more than existing products allowed.

**Sid Bidasaria** joined as engineer #2 in November 2024 and became the creator of Claude Code's subagents feature (built in just three days). A dogfooding-ready version shipped internally that same month. On day one, 20% of Anthropic's engineering used it. By day five, 50%. The team grew to roughly 10 engineers by July 2025 and is now a full product organization with engineering, PM, design, and data science. Critically, everyone at Anthropic carries the same title — "Member of Technical Staff" — by design, to flatten hierarchy. Boris co-leads the product alongside Cat Wu and a management lead.

The team debated whether to release Claude Code publicly or keep it as an internal competitive advantage. They chose to ship it because Anthropic is fundamentally a safety company, and they learn about model safety through the tools people use. Claude Code launched as a research preview in February 2025 alongside Sonnet 3.7, went generally available in May 2025, and passed **$1 billion in ARR by December 2025**.

## The recursive loop: how Claude Code builds itself

The self-referential development process is central to how the team operates. Boris stated across multiple interviews that **roughly 90% of Claude Code's codebase was written using Claude Code**. Mike Krieger, Anthropic's head of product (and Instagram co-founder), confirmed at the Cisco AI Summit in February 2026: "Claude is now writing Claude... for most products at Anthropic it's effectively 100% just Claude writing, and then what we've done is created all the right scaffolds around it to let us trust it."

The tech stack was chosen explicitly to enable this recursive loop. The team uses **TypeScript, React with Ink, Yoga (Meta's layout engine), and Bun** — all technologies that are "on distribution," meaning Claude already knows them well. Boris explained: "We wanted a tech stack which we didn't need to teach: one where Claude Code could build itself." The architectural philosophy is radical simplicity: a lightweight shell on top of the Claude model with as little business logic as possible. With each new model release, the team deletes code. When the 4.0 models shipped, they deleted approximately half the system prompt. Boris noted he "deleted like 2,000 tokens from the system prompt" when Sonnet 4.5 launched because the model simply didn't need the guidance anymore.

Anthropic calls this internal dogfooding practice **"antfooding"** (employees are affectionately known as "ants"). Cat Wu reported that 70-80% of technical Anthropic employees use Claude Code daily, and their internal feedback channel receives a message every five minutes. New features are pushed to internal users first for rapid validation. The culture is bottom-up: engineers build what they need for themselves, then ship it to the world.

## Boris Cherny's daily workflow and parallel agent orchestra

Boris's personal development workflow, shared in a viral X/Twitter thread (8M+ views, 103K bookmarks), is built around **massive parallelism and minimal manual intervention**. He runs 5 parallel Claude Code instances in numbered iTerm2 terminal tabs, each in a separate git checkout (not branches or worktrees, to avoid conflicts). On top of those, he runs 5-10 additional sessions on claude.ai/code, plus mobile sessions started from his iPhone. He uses iTerm2 system notifications to ping him when a session finishes or needs input, and the `--teleport` flag to move sessions between local and web contexts.

His core loop follows a consistent pattern. He starts **80% of tasks in Plan Mode** (activated with Shift+Tab twice), iterating on the plan until it's solid. Then he switches to auto-accept mode and lets Claude one-shot the implementation. "Once there is a good plan, it will one-shot the implementation almost every time," he explained on Lenny's Podcast. He ships **10-30 PRs daily** — 259 PRs in one 30-day stretch, comprising 497 commits and roughly 40,000 lines of code added and 38,000 removed, consuming approximately 325 million tokens across 1,600 sessions.

Boris's preferred model is **Opus 4.5 with extended thinking** enabled. His reasoning: "It's the best coding model I've ever used... since you have to steer it less and it's better at tool use, it is almost always faster than using a smaller model in the end." He abandons 10-20% of sessions that go sideways, preferring to start fresh rather than fight a bad trajectory. The mindset shift is telling: "It's not so much about deep work anymore. It's about how good I am at context switching and jumping across multiple different contexts very quickly."

## The team's slash commands, subagents, and automation stack

The Claude Code team has built a rich ecosystem of custom tooling that lives in the repository and is shared across the entire team. Their most-used **slash commands** include:

- **`/commit-push-pr`** — used dozens of times daily by Boris for automated git operations
- **`/feature-dev`** — a structured workflow that walks through asking questions, writing a spec, creating a plan, building a todo list, and executing step-by-step
- **`/code-review`** — spawns multiple subagents for first-pass review (style checker, project history reviewer, bug finder), then **five more adversarial subagents** that poke holes in the original findings to eliminate false positives
- **`/simplify`** — runs parallel agents for code quality, efficiency, and CLAUDE.md compliance
- **`/batch`** — interactive migration planning executed by dozens of parallel agents in worktrees

Custom subagents stored in `.claude/agents/` include a **code-simplifier** (simplifies code after Claude writes it), a **verify-app** agent (detailed end-to-end testing), a **code-architect**, an **oncall-guide**, and a **build-validator**. The code review automation is particularly sophisticated — Boris built its predecessor at Meta, where he logged every repeated review comment in a spreadsheet and turned patterns with 3-4 occurrences into automated lint rules.

**Hooks** provide deterministic automation. The team uses a PostToolUse hook that runs `bun run format || true` after every code edit, catching the last 10% of formatting issues that would otherwise fail CI. Stop hooks run test suites and send Claude back to fix failures automatically, creating self-sufficient loops. Boris never uses `--dangerously-skip-permissions` except in sandboxed long-running tasks, instead using `/permissions` to pre-allow safe commands, with the allowlist shared via `.claude/settings.json` in the repository.

**MCP (Model Context Protocol) integrations** are configured in a shared `.mcp.json` file. The team connects Claude Code to Slack, BigQuery (via the bq CLI), and Sentry error logs. Cat Wu recommends Puppeteer, Playwright, Sentry, and Asana MCPs for other teams. The Data Infrastructure team uses MCP servers instead of direct BigQuery CLI access for security control over sensitive data.

## The CLAUDE.md file as living documentation

The team's shared **CLAUDE.md** lives in the git repository, runs approximately **2,500 tokens**, and is updated multiple times weekly by the entire team. Boris's personal CLAUDE.md is "basically two lines pointing to the team's shared one." The file includes build commands (`bun run typecheck`, `bun run test`, `bun run lint`), coding conventions (never use TypeScript enums — prefer string literal unions; use `bun` not `npm`), architecture notes, and common pitfalls.

The team's rule is simple: **when Claude does something wrong, add it to the CLAUDE.md so it doesn't happen again**. They use a `@.claude` tag on coworkers' pull requests via GitHub Actions to automatically suggest CLAUDE.md additions — what Boris calls their version of "Compounding Engineering." One of the team's most effective practices is telling Claude at the end of a correction: "Update your CLAUDE.md so you don't make that mistake again." Boris notes that "Claude is eerily good at writing rules for itself."

Anthropic's official best practices recommend keeping CLAUDE.md files under 200 lines for maximum adherence, using markdown headers and bullets, and supporting a hierarchical structure with root project files plus subdirectory-specific overrides. The auto-memory feature (added in v2.1.59) allows Claude to accumulate knowledge across sessions — build commands, debugging insights, architecture preferences — creating a persistent learning loop.

## Productivity gains that rewrote the math

The numbers Boris and Anthropic report are striking, though they come in several formulations across different interviews. Anthropic's own research paper ("How AI is transforming work at Anthropic," December 2025) surveyed 132 engineers and analyzed 200,000 internal Claude Code transcripts. It found a **67% increase in pull requests merged per engineer per day**, even as the engineering team doubled in size. Engineers self-reported using Claude in **59% of their work** (up from 28% a year prior) and estimated a **50% productivity boost** (up from 20%).

Boris himself cites higher figures in later interviews. On Lenny's Podcast (February 2026), he stated engineering productivity at Anthropic increased **200% per engineer**, a number he contextualized by noting: "Back at Meta, with hundreds of engineers working on productivity, we'd see gains of a few percentage points in a year." On the Peterman Pod, he cited a **70% productivity increase per engineer**. The discrepancy likely reflects different timeframes, measurement methods, and the rapid acceleration through late 2025 and into 2026 as models improved.

Specific team-level metrics from Anthropic's internal study paint a granular picture:

- The **Inference team** reported an 80% reduction in research time (from 1 hour to 10-20 minutes)
- The **Security Engineering team** cut debugging time from 10-15 minutes to roughly 5 minutes
- The **Growth Marketing team** (a single non-technical employee) reduced ad copy creation from 2 hours to 15 minutes
- **Data scientists** achieved 2-4x time savings on routine tasks
- The **Product Design team** saw 2-3x faster execution on visual and state management changes, with complex copy changes going from a week of coordination to two 30-minute calls

Perhaps the most telling metric is qualitative: **27% of Claude-assisted work** at Anthropic consists of tasks that wouldn't have been done otherwise — previously deprioritized quality improvements, experiments, and "papercut fixes" that now become economically viable.

## A philosophy of building for the model six months from now

Boris's development philosophy rests on several interconnected principles that have become widely cited in the AI engineering community.

**"Build for the model six months from now."** This was his manager Ben Mann's early push, and it became the team's north star. Boris: "At Anthropic, we don't build for the model of today, we build for the model of six months from now. And that's still my advice to founders building on LLMs." This means investing in general-purpose scaffolding rather than elaborate workarounds for current model limitations. Teams building rigid orchestration workflows, Boris warns, "get wiped out with the next model release" — an echo of Rich Sutton's Bitter Lesson.

**Underfund teams on purpose.** Give one great engineer a big problem and unlimited tokens, rather than staffing five people on it. "With unlimited tokens and intrinsic motivation, one person ships faster because they are forced to let AI do the work." Some Anthropic engineers spend hundreds of thousands of dollars per month on tokens. Boris's advice: "Don't try to cost-cut at the beginning. Start by giving engineers as many tokens as possible."

**Prototype, don't spec.** PRDs are dead on the Claude Code team. Boris: "The culture is we don't really write stuff, we just... show." The team builds 10-20+ working prototypes before shipping a major feature. The Cowork desktop product (an Electron + TypeScript app for non-coding tasks) was built by four engineers in 10 days, with most code written by Claude Code. The subagents feature shipped in three days.

**"Coding is largely solved."** Boris stated this flatly on Lenny's Podcast in February 2026. His personal trajectory illustrates the claim: Claude Code wrote 20% of his code at launch in February 2025, 30% by May, and **100% by November** — with zero manual edits since. He predicts the title "software engineer" will begin disappearing, replaced by "builder." He compares the moment to the printing press: "Before Gutenberg, sub-1% of Europe was literate. Scribes did all the reading and writing. In 50 years after the press, more material was printed than in the thousand years before."

**Test-driven development as the foundation.** TDD is described as the "Anthropic-favorite workflow" in the official best practices blog, authored by Boris. The pattern: have Claude write tests based on expected inputs/outputs, confirm they fail, then have Claude write the implementation. The writer/reviewer pattern adds another layer — one Claude instance writes code, a fresh instance reviews it without the bias of having authored it.

## Every major talk, podcast, and interview

Boris Cherny has given an unusually dense series of public appearances since late 2025. The most substantive include **Lenny's Podcast** (February 19, 2026; ~88 minutes covering the "coding is solved" thesis, productivity metrics, and why he briefly left for Cursor before returning), the **Y Combinator Lightcone Podcast** (February 17, 2026; ~50 minutes with detailed CLAUDE.md discussion and the "build for 6 months from now" principle), and the **Every.to AI & I Podcast** with Cat Wu (October 29, 2025; the most technical episode, covering subagent patterns, slash commands, and adversarial code review in depth).

The **Pragmatic Engineer** published both a deep-dive article ("How Claude Code is Built," September 2025) and a follow-up podcast (March 2026) — together these are the most technically detailed sources, covering architecture decisions, the glob-and-grep-beats-RAG insight, and the internal adoption timeline. The **Peterman Pod** (December 2025) offers the fullest career narrative, from Boris's first startup at 18 through his Meta years to Anthropic. **The Vergecast** (February 24, 2026) covered the product's first anniversary. Boris spoke at the **AI Engineer World's Fair** (October 2025) on the evolution of coding UX since the 1950s, at **STATION F in Paris** (March 2026) where he stated "I have not written a single line of code since November," and at **Anthropic's Code with Claude** conferences in 2025 and 2026. He has also led webinars on Claude Code for Financial Services and Service Delivery.

On X/Twitter (@bcherny, 261.5K followers), Boris published a multi-part series of workflow tips totaling **57+ individual tips across 8 threads** from January to March 2026. The first thread alone (January 2, 2026) garnered 8 million views, 54,000 likes, and 103,000 bookmarks. A fan site, howborisusesclaudecode.com, compiles all tips into an interactive guide.

---

*The Claude Code team's approach represents a genuinely novel development paradigm — not just using AI as an assistant, but structuring an entire engineering organization around the assumption that AI writes virtually all the code. The key insights are not about prompting tricks but about organizational design: flat hierarchies where everyone codes, prototyping cultures that make PRDs obsolete, aggressive parallelism across 10-15 simultaneous agent sessions, and the discipline to invest heavily in CLAUDE.md files as living institutional memory. The recursive nature of the work — Claude Code building Claude Code — creates an unusually tight feedback loop where every improvement to the product immediately improves the team's own development velocity. Boris's most actionable advice may also be his simplest: give Claude a way to verify its own work, and it will 2-3x the quality of the final result.*
