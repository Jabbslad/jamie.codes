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

259 PRs in 30 days. 497 commits. 325 million tokens. Zero lines written by hand.

That's not a team. That's [Boris Cherny](https://x.com/bcherny), one person, building Claude Code with Claude Code. I've been studying how he works, and the gap between his output and mine was bothering me. So I pulled apart everything he's shared publicly and tried to figure out what's actually transferable.

Turns out, most of it is.

<!-- more -->

## Stop coding. Start planning.

This is the one that changed how I work.

Boris starts 80% of his tasks in **Plan Mode** (Shift+Tab twice). He doesn't touch code until the plan is right. Then he flips to auto-accept and lets Claude execute the whole thing in one shot.

> "Once there is a good plan, it will one-shot the implementation almost every time." [Lenny's Podcast](https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens)

I used to do the opposite: jump in, start coding, course-correct as I went. That works when you're writing the code yourself. With an AI agent, it's backwards. Every minute you spend refining the plan saves ten minutes of "no, not like that" later.

Try it on your next task. Open Plan Mode, describe what you want, and don't leave until the plan actually makes sense. The implementation will feel like cheating.

## You're not running enough agents

Boris runs **5 parallel Claude Code instances** in iTerm2 tabs, each in its own full git checkout. On top of those, 5-10 web sessions on claude.ai/code. Sometimes he starts things from his phone.

When I first [read this](https://x.com/bcherny/status/2007179832300581177), I thought it was showing off. Then I tried running three sessions in parallel and realised how much time I'd been wasting watching a single agent think. While one agent is implementing a feature, another is writing tests, and a third is fixing that bug you've been ignoring.

The key detail: **use separate git checkouts, not branches.** Branches in the same worktree cause conflicts when multiple agents edit files simultaneously. Separate checkouts are clean.

Set up terminal notifications so you know when a session finishes or needs input. Boris uses iTerm2's built-in notifications and the `--teleport` flag to bounce sessions between terminal and web.

*"It's not so much about deep work anymore. It's about how good I am at context switching."* ([YC Lightcone](https://www.ycombinator.com/library/NJ-inside-claude-code-with-its-creator-boris-cherny))

That quote felt wrong to me at first. But he's right. The bottleneck isn't thinking deeply about one problem. It's keeping five plates spinning and knowing when each one needs attention.

## Kill bad sessions early

Boris abandons **10-20% of sessions** that go sideways. No sunk cost fallacy, no trying to steer a confused agent back on track. Just kill it and start fresh.

He also runs **Opus 4.5 with extended thinking**. His [reasoning](https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens): you steer it less, so it's actually faster than a cheaper model, even though each token costs more. I was sceptical, but after switching, the difference is real. Fewer corrections means fewer wasted rounds.

If a session is spiralling after 2-3 corrections, stop. Open a new one with a cleaner prompt. Your time is worth more than the tokens.

## Automate everything you do twice

The Claude Code team has built [slash commands for their entire workflow](https://every.to/podcast/how-to-use-claude-code-like-the-people-who-built-it):

- **`/commit-push-pr`**: Boris runs this dozens of times a day. Formats, commits, pushes, opens a PR.
- **`/feature-dev`**: asks clarifying questions, writes a spec, plans, builds a todo, then executes step by step
- **`/code-review`**: this one's wild. It spawns subagents for a first-pass review, then **five adversarial subagents** that attack the original findings to kill false positives
- **`/simplify`**: parallel agents checking quality, efficiency, and CLAUDE.md compliance

I started with just one: a `/ship` command that formats, commits, and opens a PR. It's embarrassingly simple and I use it constantly. Start there. Add more as patterns emerge.

**Hooks** are the other half. The team runs `bun run format || true` as a PostToolUse hook after every edit. Stop hooks run tests and send Claude back to fix its own failures. You set it up once and never think about it again.

## Your CLAUDE.md is compounding interest

This might be the highest-leverage thing Boris's team does, and it's the simplest.

Their shared CLAUDE.md is about 2,500 tokens. Build commands, coding conventions, architecture notes, known pitfalls. The whole team updates it multiple times a week.

The rule: **when Claude does something wrong, add it to CLAUDE.md so it doesn't happen again.** Even better, after correcting Claude, tell it: *"Update your CLAUDE.md so you don't make that mistake again."* Boris [says](https://newsletter.pragmaticengineer.com/p/how-claude-code-is-built) Claude is "eerily good at writing rules for itself."

I started doing this three weeks ago and the difference is already noticeable. Claude stops making the same mistakes. It remembers your preferences. Each correction makes every future session slightly better. That's compounding interest on your attention.

Keep it under 200 lines. Review it weekly. Cut anything that's no longer relevant.

## Wire Claude into your actual stack

The team connects Claude Code to **Slack, BigQuery, and Sentry** via MCP servers, configured in a shared `.mcp.json` in the repo.

This is where it stops feeling like a code assistant and starts feeling like a colleague. "Look at the latest Sentry errors and fix the top one." "Query the analytics table and tell me what changed." "Check Slack for what the team decided about the API format."

If you're only using Claude Code to write and edit files, you're leaving most of its value on the table.

## The bigger picture

Three principles from Boris that I keep coming back to:

**Build for the model six months from now.** Don't write elaborate workarounds for today's limitations. They'll be irrelevant by the next model release. Keep your scaffolding general.

**Prototype, don't spec.** Boris's team doesn't write PRDs. They build 10-20+ working prototypes before shipping a feature. The subagents feature shipped in three days. If you're still writing documents about what you're going to build, you could have built it twice by now.

**Give Claude a way to check its own work.** Write tests first. Use the [writer/reviewer pattern](https://www.anthropic.com/engineering/claude-code-best-practices): one Claude instance writes code, a fresh instance reviews it without the authorship bias. This alone 2-3x's output quality.

---

*I'm not shipping 259 PRs a month yet. But I've gone from watching one agent work to running three in parallel, from hand-editing code to planning and accepting, from repeating the same corrections to compounding them in CLAUDE.md. The gap between where I am and where Boris is isn't talent. It's just layers of automation I haven't built yet. Each one is simple. They stack.*
