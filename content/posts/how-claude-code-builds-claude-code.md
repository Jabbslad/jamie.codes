+++
title = "Steal Boris Cherny's Claude Code Workflow"
date = "2026-03-29"
description = "Boris Cherny ships 10-30 PRs a day using Claude Code. Here's exactly how he does it, and how you can too."
tags = ["ai", "engineering", "developer-tools", "anthropic"]

[extra]
comment = false
hero_image = "/images/claude-code-builds-claude-code-hero.png"
hero_image_alt = "A surreal panoramic landscape with enormous floating orbs above ancient architecture, evoking recursive creation"
+++

Boris Cherny created Claude Code and hasn't written a line of code by hand since November 2025. He ships 10-30 PRs a day. In one 30-day stretch: 259 PRs, 497 commits, 325 million tokens across 1,600 sessions.

Here's the workflow behind those numbers, and how to apply it yourself.

<!-- more -->

## The core loop: plan first, then let it rip

Boris starts **80% of tasks in Plan Mode** (Shift+Tab twice). He iterates on the plan until it's solid, then switches to auto-accept and lets Claude one-shot the implementation.

> "Once there is a good plan, it will one-shot the implementation almost every time." [Lenny's Podcast](https://www.lennysnewsletter.com/)

That's the entire inner loop. Plan, accept, ship. No hand-editing.

**How to apply this:** Resist the urge to jump straight into coding. Spend the time upfront getting the plan right. A good plan in Plan Mode is worth more than an hour of back-and-forth corrections.

## Run agents in parallel

Boris runs **5 Claude Code instances** in numbered iTerm2 tabs, each in a separate git checkout (not branches or worktrees; full checkouts avoid conflicts). On top of those, 5-10 sessions on claude.ai/code, plus mobile sessions from his iPhone.

He uses iTerm2 notifications to know when a session finishes or needs input, and `--teleport` to move sessions between local and web.

The mindset shift: *"It's not so much about deep work anymore. It's about how good I am at context switching and jumping across multiple different contexts very quickly."*

**How to apply this:** Start with 2-3 parallel sessions on separate tasks. Use separate git checkouts, not branches. Set up terminal notifications so you're not watching paint dry.

## Use the right model and know when to quit

Boris runs **Opus 4.5 with extended thinking**. His logic: you steer it less, so it's faster end-to-end than a cheaper model, even if each token costs more.

He abandons **10-20% of sessions** that go sideways. Starting fresh beats fighting a bad trajectory.

**How to apply this:** Use the best model you can afford. If a session is spiralling after 2-3 corrections, kill it and start over with a cleaner prompt. Don't throw good tokens after bad.

## Build slash commands for everything you repeat

The Claude Code team's most-used commands:

- **`/commit-push-pr`**: Boris runs this dozens of times a day
- **`/feature-dev`**: asks questions, writes a spec, creates a plan, builds a todo list, executes step-by-step
- **`/code-review`**: spawns subagents for first-pass review, then **five adversarial subagents** that poke holes in the findings to kill false positives
- **`/simplify`**: parallel agents checking code quality, efficiency, and CLAUDE.md compliance

**How to apply this:** Look at what you do repeatedly and turn it into a slash command. Start with your git workflow. A `/ship` command that formats, commits, and opens a PR will pay for itself on day one.

## Let hooks close the loop

The team uses a **PostToolUse hook** that runs `bun run format || true` after every code edit. Stop hooks run tests and send Claude back to fix failures automatically.

**How to apply this:** Add a format-on-edit hook. Then add a test hook. Now Claude formats its own code and fixes its own test failures without you touching anything.

## Treat CLAUDE.md as your team's memory

The team's shared CLAUDE.md is ~2,500 tokens, updated multiple times a week. It has build commands, coding conventions, architecture notes, and common pitfalls.

The rule: **when Claude does something wrong, add it to CLAUDE.md so it doesn't happen again.** After correcting Claude, tell it: *"Update your CLAUDE.md so you don't make that mistake again."* Boris says Claude is "eerily good at writing rules for itself."

**How to apply this:** Start a CLAUDE.md today. After every correction, add a rule. Keep it under 200 lines. Review it weekly. This compounds; within a month, Claude will make dramatically fewer mistakes in your codebase.

## Connect Claude to your tools

The team wires Claude Code into **Slack, BigQuery, and Sentry** via MCP servers, all in a shared `.mcp.json` committed to the repo.

**How to apply this:** Connect your error tracker and your database. Being able to say "look at the latest Sentry errors and fix the top one" or "query the analytics table and tell me what's wrong" turns Claude from a code writer into an actual collaborator.

## The philosophy underneath

Three principles that tie this together:

**Build for the model six months from now.** Don't build elaborate workarounds for current limitations. Invest in general scaffolding. Teams that build rigid orchestration workflows "get wiped out with the next model release."

**Prototype, don't spec.** PRDs are dead on this team. They build 10-20+ working prototypes before shipping a feature. The subagents feature shipped in three days.

**Give Claude a way to verify its own work.** Write tests first. Use the writer/reviewer pattern: one Claude instance writes, a fresh one reviews. This alone 2-3x's the quality of the output.

---

*Boris's workflow isn't magic. It's a system: plan before you build, run things in parallel, automate what you repeat, and compound your corrections into CLAUDE.md. The gap between his 259 PRs in a month and your current output isn't talent, it's tooling. Start with one slash command, one hook, and a CLAUDE.md file. The rest follows.*
