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

Boris Cherny hasn't written a line of code by hand since November 2025. Not because he can't — he was a Principal Engineer at Instagram — but because the tool his team builds writes it for him. That tool is Claude Code, and about 90% of it was written by itself.

What started as a side project in his first month at Anthropic has become a product responsible for 4% of all public GitHub commits and over a billion dollars in annual recurring revenue. This is the story of how it's built.

<!-- more -->

## A rejected PR and a bash script

Boris arrived at Anthropic in September 2024 fresh from five years at Meta. He submitted his first pull request. It was rejected — not for any technical reason, but because he'd written it by hand. His ramp-up buddy Adam Wolf looked at it and said: *"You wrote this by hand. What are you doing?"*

Point taken.

Within weeks, Boris had a prototype: a terminal tool wired up to Claude 3.6. The first version was whimsical — it could use AppleScript to tell him what song was playing. But after a conversation with Cat Wu (who'd go on to become the product's founding PM), he gave it filesystem access and a bash shell. That's when things got interesting.

"I ran it in our codebase, and Claude started exploring the filesystem — reading one file, looking at the imports, then reading the files defined in those imports," Boris [recalled on The Pragmatic Engineer podcast](https://www.pragmaticengineer.com/). He saw what he calls **"product overhang"** — the model was already far more capable than any product was letting it be.

Sid Bidasaria joined as engineer #2 in November and built the subagents feature in three days. They shipped an internal dogfooding version that same month. Day one: 20% of Anthropic's engineers were using it. Day five: 50%.

The team debated whether to keep Claude Code as an internal advantage or ship it publicly. They shipped it — because Anthropic is a safety company, and you learn about safety by watching how people actually use your tools. It launched as a research preview in February 2025, went GA in May, and crossed **$1 billion in ARR by December**.

## The tool that builds itself

Here's the thing that makes Claude Code genuinely strange: it's recursive. The product writes itself.

Boris has said this in [every interview he's given](https://www.lennysnewsletter.com/): roughly 90% of the codebase was written using Claude Code. Mike Krieger, Anthropic's head of product, put it even more bluntly at the Cisco AI Summit: *"For most products at Anthropic it's effectively 100% just Claude writing, and then what we've done is created all the right scaffolds around it to let us trust it."*

The tech stack was chosen to make this loop work. **TypeScript, React with Ink, Yoga, and Bun** — all technologies Claude already knows well. "We wanted a tech stack which we didn't need to teach," Boris explained. "One where Claude Code could build itself."

The architectural philosophy is radical simplicity: a thin shell on top of the model with as little business logic as possible. And with every new model release, the team *deletes code*. When Sonnet 4.5 shipped, Boris cut 2,000 tokens from the system prompt. The model just didn't need the hand-holding anymore.

Anthropic calls their internal dogfooding practice **"antfooding"** (employees go by "ants"). Around 70-80% of technical staff use Claude Code daily, and the internal feedback channel gets a message every five minutes. Engineers build what they need for themselves, then ship it to the world.

## Running 15 agents at once

Boris's workflow — which he shared in [a viral X thread](https://x.com/bcherny) that hit 8 million views and 103,000 bookmarks — is built around massive parallelism.

He runs 5 Claude Code instances in iTerm2 tabs, each in a separate git checkout. On top of that, 5-10 more sessions on claude.ai/code. Plus the odd mobile session kicked off from his iPhone. iTerm2 notifications ping him when a session finishes or needs input, and the `--teleport` flag lets him move sessions between local and web.

The core loop is surprisingly consistent. He starts **80% of tasks in Plan Mode**, iterating until the plan is solid. Then he flips to auto-accept and lets Claude one-shot the implementation. *"Once there is a good plan, it will one-shot the implementation almost every time,"* he said on [Lenny's Podcast](https://www.lennysnewsletter.com/).

The numbers are wild: **10-30 PRs a day**. In one 30-day stretch, he shipped 259 PRs — 497 commits, ~40,000 lines added, ~38,000 removed, burning through 325 million tokens across 1,600 sessions.

His model of choice? **Opus 4.5 with extended thinking.** His logic: "Since you have to steer it less and it's better at tool use, it is almost always faster than using a smaller model in the end." He abandons 10-20% of sessions that go sideways — starting fresh beats fighting a bad trajectory.

The mindset shift is the quiet part: *"It's not so much about deep work anymore. It's about how good I am at context switching and jumping across multiple different contexts very quickly."*

## The automation stack

The team's custom tooling lives in the repo and is shared across everyone. Some of the slash commands they've built:

- **`/commit-push-pr`** — Boris uses this dozens of times a day
- **`/feature-dev`** — walks through questions, spec, plan, todo list, then executes
- **`/code-review`** — the clever one. It spawns subagents for first-pass review (style, history, bugs), then **five more adversarial subagents** that poke holes in the original findings to kill false positives
- **`/simplify`** — parallel agents checking quality, efficiency, and CLAUDE.md compliance
- **`/batch`** — migration planning executed by dozens of parallel agents in worktrees

Boris built the ancestor of the code review system at Meta, where he logged every repeated review comment in a spreadsheet and turned patterns with 3-4 occurrences into lint rules. Same instinct, wildly different execution.

**Hooks** handle the deterministic stuff. A PostToolUse hook runs `bun run format || true` after every edit, catching formatting issues before CI does. Stop hooks run tests and send Claude back to fix failures automatically — closed-loop, self-healing development.

They connect Claude Code to **Slack, BigQuery, and Sentry** via MCP, all configured in a shared `.mcp.json`. The Data Infrastructure team uses MCP servers for BigQuery instead of direct CLI access — security control over sensitive data without losing the AI workflow.

## CLAUDE.md as institutional memory

The team's shared CLAUDE.md is about 2,500 tokens, updated multiple times a week by the whole team. Boris's personal one? "Basically two lines pointing to the team's shared one."

It contains build commands, coding conventions (no TypeScript enums — string literal unions only; `bun` not `npm`), architecture notes, and common pitfalls. The rule is dead simple: **when Claude does something wrong, add it to the CLAUDE.md so it doesn't happen again.**

They've automated this too. A `@.claude` tag on pull requests via GitHub Actions suggests CLAUDE.md additions — what Boris calls "Compounding Engineering." One of the team's best tricks: after correcting Claude, tell it to *"Update your CLAUDE.md so you don't make that mistake again."* Boris notes that "Claude is eerily good at writing rules for itself."

## What the numbers actually say

The productivity gains are real, if hard to pin to a single figure.

Anthropic's internal study (December 2025) surveyed 132 engineers and analyzed 200,000 Claude Code transcripts. It found a **67% increase in PRs merged per engineer per day** — even as the team doubled in size. Engineers reported using Claude in 59% of their work and estimated a 50% productivity boost.

Boris cites higher numbers in later interviews — **200% per engineer** on Lenny's Podcast, 70% on the Peterman Pod. The gap probably reflects different timeframes and the rapid acceleration through late 2025 as models improved.

The team-level numbers tell the sharper story:

- **Inference team**: research time dropped 80% (1 hour to 10-20 minutes)
- **Security engineering**: debugging cut from 10-15 minutes to ~5
- **Growth marketing** (one non-technical person): ad copy from 2 hours to 15 minutes
- **Product design**: 2-3x faster on visual changes; complex copy changes went from a week of coordination to two 30-minute calls

But the most interesting number? **27% of Claude-assisted work** consists of things that would never have been done otherwise — papercut fixes, experiments, quality improvements that were always deprioritized. AI didn't just make existing work faster. It made new work economically viable.

## Build for the model that doesn't exist yet

A few principles from Boris that have stuck with me.

**"Build for the model six months from now."** This came from his manager Ben Mann, and it became the team's north star. Don't build elaborate workarounds for current model limitations — invest in general-purpose scaffolding. Teams that build rigid orchestration workflows, Boris warns, "get wiped out with the next model release." Rich Sutton's [Bitter Lesson](http://www.incompleteideas.net/IncIdeas/BitterLesson.html), applied to product development.

**Underfund teams on purpose.** Give one great engineer a big problem and unlimited tokens. "With unlimited tokens and intrinsic motivation, one person ships faster because they are forced to let AI do the work." Some Anthropic engineers spend hundreds of thousands of dollars per month on tokens.

**Prototype, don't spec.** PRDs are dead on this team. "The culture is we don't really write stuff, we just... show." They build 10-20+ working prototypes before shipping a major feature. The desktop Cowork app was built by four engineers in 10 days.

**"Coding is largely solved."** Boris said this on Lenny's Podcast in February 2026, and his own trajectory backs it up: Claude Code wrote 20% of his code at launch, 30% by May, and 100% by November. Zero manual edits since. He compares it to the printing press: *"Before Gutenberg, sub-1% of Europe was literate. In 50 years after the press, more material was printed than in the thousand years before."*

And the most practical principle of all: **give Claude a way to verify its own work**, and it will 2-3x the quality of the result. Write the tests first. Use the writer/reviewer pattern — one Claude instance writes, a fresh one reviews without authorship bias. Build the feedback loops. The rest follows.
