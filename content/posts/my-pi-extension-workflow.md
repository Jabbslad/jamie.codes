+++
title = "Three Extensions, One Workflow: How I Supercharged Pi"
date = "2026-04-04"
description = "I built three pi extensions that work together to create the most productive AI coding workflow I've ever used. Here's how plan mode, worktrees, and multi-agent teams combine into something greater than the sum of their parts."
tags = ["ai", "engineering", "developer-tools", "open-source", "pi"]

[extra]
comment = true
hero_image = "/images/multi-agent-teams-hero.png"
hero_image_alt = "A team of agents collaborating around a digital task board"
+++

I've been using [pi](https://github.com/mariozechner/pi-coding-agent) as my daily coding agent for a while now. It's fast, it's minimal, and it stays out of the way. But what makes it genuinely special is its extension system. You can shape it into exactly the workflow you want.

Over the past few months, I built three extensions that, individually, each solve a real problem. Together, they've completely transformed how I work. I'm shipping faster, making fewer mistakes, and honestly having more fun doing it.

Let me show you what I mean.

<!-- more -->

## The three pieces

### 1. Plan Mode: think before you type

[pi-plan-mode](https://github.com/Jabbslad/pi-plan-mode) forces the agent to explore and understand your codebase before it writes a single line of code.

You type `/plan add OAuth2 support` and the agent drops into read-only mode. It can read files, grep, search, run non-destructive bash commands. It cannot edit anything. It explores your codebase, understands the architecture, and writes a plan to a markdown file. Then it presents the plan for your approval.

You review it. You can approve it, edit it in your editor, or send it back with feedback. Only after you give the green light does the agent gain write access.

This sounds like a small thing. It is not a small thing. Without plan mode, agents jump straight into implementation and regularly misunderstand the codebase. They rename things that shouldn't be renamed. They add dependencies you don't want. They restructure code without understanding why it was structured that way in the first place.

Plan mode eliminates an entire category of "undo everything the agent just did" moments.

### 2. Worktrees: isolation without the mess

[pi-worktree](https://github.com/Jabbslad/pi-worktree) wraps git worktrees into a seamless experience. Type `/worktree create` and you get a fresh checkout in `.pi/worktrees/` with its own branch, its own working directory, and its own pi session. Your `.pi/` config, extensions, and settings are automatically synced across.

When you're done, `/worktree remove` cleans everything up. It checks for uncommitted changes and unpushed commits before removing anything. If you close your session and forget about the worktree, it prompts you on shutdown.

Why does this matter? Because when an agent is doing experimental work, refactoring, or trying something risky, you want isolation. You want to be able to throw everything away if it goes wrong. Worktrees give you that without the overhead of managing branches and checkouts manually.

The extension also auto-detects when you're inside a worktree and shows the status in your terminal footer. You always know where you are.

### 3. Team Agents: parallelism that actually works

[pi-team-agents](https://github.com/Jabbslad/pi-team-agents) adds multi-agent coordination. Instead of one agent doing everything sequentially, you can spawn teams of specialised agents that work in parallel.

Researchers explore your codebase (read-only, fast, safe). Planners design architecture. Coders implement. Reviewers audit. Each agent runs in its own context window with its own tool access, communicating through a shared task board and mailbox system.

The simplest way to use it is `team_dispatch`: fire off three researchers to audit different parts of your codebase simultaneously, then collect all the results at once. For more complex workflows, you create a team and spawn agents in stages, feeding one agent's output into the next.

I wrote about this in more detail in my [previous post](/posts/multi-agent-teams-for-pi/), but the short version is: it turns your single-threaded agent into a properly parallel system.

## The workflow: all three together

Here's where it gets exciting. These three extensions weren't designed to work together, but because pi's extension system is composable, they slot together beautifully.

Here's my typical workflow for a non-trivial feature:

### Step 1: Plan it

```
/plan add structured logging with correlation IDs
```

The agent enters read-only mode. It greps through the codebase, reads the existing logging setup, checks the dependencies, looks at how errors are currently handled. Five minutes later, it presents a plan:

- Replace `console.log` calls with a structured logger
- Add correlation ID middleware to the HTTP layer  
- Propagate IDs through the async context
- Update 14 files across 3 modules

I review the plan, tweak one section where it missed a module boundary, and approve.

### Step 2: Isolate it

The agent creates a worktree. Fresh branch, fresh working directory, complete isolation from my main checkout. If this whole thing goes sideways, I lose nothing.

```
Worktree created:
  Name: calm-hawk-x9f2
  Path: /home/jabbslad/dev/myproject/.pi/worktrees/calm-hawk-x9f2
  Branch: worktree/calm-hawk-x9f2
```

I `cd` into the worktree and start a new pi session. My extensions, settings, and project config are all there waiting.

### Step 3: Execute it with a team

Now the plan is approved and I'm in an isolated worktree. Time to bring in the team.

```
Dispatch a researcher to gather the current logging patterns across the codebase,
a coder to implement the structured logger module, and another coder to add the
correlation ID middleware. The researcher should finish first so the coders have context.
```

Three agents spin up. The researcher finishes in about 30 seconds and its findings feed into shared memory. The two coders pick up the context and implement in parallel, one working on the logger, the other on the middleware. A live footer in the terminal shows me which agents are busy.

When the coders finish, I spawn a reviewer to audit everything they wrote. It catches a missing error handler and a type inconsistency. I have a coder fix both.

Total time: about 8 minutes for what would have been at least an hour of sequential work.

### Step 4: Merge and clean up

Back in my main checkout, I review the diff, merge the branch, and remove the worktree. Three commands and it's done.

## Why this works so well

The key insight is that each extension handles a different phase of the development loop:

| Phase | Extension | What it does |
|-------|-----------|-------------|
| **Think** | pi-plan-mode | Explore, understand, design |
| **Isolate** | pi-worktree | Safe sandbox for experimental work |
| **Execute** | pi-team-agents | Parallel implementation and review |

They don't need to know about each other. Plan mode doesn't care whether you're in a worktree. Worktrees don't care whether you're using agents. Team agents don't care how you arrived at your plan. They compose through pi's extension system without any coupling.

This is what makes pi's architecture genuinely brilliant. Mario Zechner designed it so that extensions register tools, commands, and event handlers independently. There's no central orchestrator you need to plug into. You just install packages and they work.

```bash
pi install git:github.com/Jabbslad/pi-plan-mode
pi install git:github.com/Jabbslad/pi-worktree
pi install git:github.com/Jabbslad/pi-team-agents
```

Three lines. That's the entire setup.

## The productivity gains are real

I'm not going to throw around made-up percentages. What I will say is this:

**Before these extensions**, my workflow was: describe task to agent, watch it fumble around the codebase for a while, correct it when it went off-track, wait while it implemented sequentially, manually review everything, hope it didn't break something I didn't notice.

**After**: I get a plan I can review before anything changes. I work in isolation so mistakes are free. I fan out work across multiple agents so the wall-clock time drops dramatically. And the reviewer agent catches things I'd miss at 11pm on a Thursday.

The biggest win isn't speed, though. It's confidence. When I merge a worktree branch, I know the work was planned, isolated, implemented by specialists, and reviewed by a fresh pair of (artificial) eyes. That's a workflow I trust.

## Build your own

The whole point of pi is that you don't have to use my workflow. Maybe you don't need worktrees because you work on small projects. Maybe you want plan mode but prefer to implement manually. Maybe you want to write your own agents with custom roles.

Pi's extension API gives you the building blocks. I built all three of these extensions in TypeScript using pi's SDK, and each one is open source:

- [pi-plan-mode](https://github.com/Jabbslad/pi-plan-mode): Think first, code second
- [pi-worktree](https://github.com/Jabbslad/pi-worktree): Git worktree lifecycle management
- [pi-team-agents](https://github.com/Jabbslad/pi-team-agents): Multi-agent team coordination

If you're using pi, give them a try. If you're not using pi yet, this is the kind of flexibility that made me switch. You don't adapt to the tool. You make the tool adapt to you.

---

*Pi is open source and built by [Mario Zechner](https://github.com/mariozechner/pi-coding-agent). If you're tired of AI coding tools that are opinionated about how you should work, it's worth a look.*
