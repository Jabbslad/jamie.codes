+++
title = "I Built Multi-Agent Teams for My AI Coding Assistant"
date = "2026-04-04"
description = "How Anthropic's Claude Code inspired me to build a multi-agent coordination plugin for pi, and why one AI agent is no longer enough."
tags = ["ai", "engineering", "developer-tools", "open-source"]

[extra]
comment = true
hero_image = "/images/heroes/default-hero.svg"
hero_image_alt = "A team of agents collaborating around a digital task board"
+++

One AI agent is clever. Two agents working together is a system. I wanted a system.

That's the short version of why I built [pi-team-agents](https://github.com/Jabbslad/pi-team-agents), a multi-agent coordination plugin for [pi](https://github.com/mariozechner/pi-coding-agent), the terminal-based AI coding agent. The longer version involves a lot of time spent watching a single agent think, getting frustrated, and realising the bottleneck wasn't the model. It was me, trying to be a project manager for something that could manage itself.

<!-- more -->

## The problem with one brain

If you've used any AI coding tool, you know the pattern. You describe a task. The agent reads files. Thinks. Reads more files. Thinks some more. Eventually it starts writing code. Then it runs the tests. Then it reads the error output. Then it thinks about the error output. Then it fixes the code. Then it runs the tests again.

For a single, well-scoped task, this works fine. But what about when you want to research three different parts of a codebase *at the same time*? Or have one agent implement a feature while another reviews what it just wrote? Or fan out a security audit across a dozen modules in parallel?

You wait. That's what you do. You wait while your single agent works through things sequentially that could clearly be done in parallel.

## The inspiration: Claude Code's team features

Anthropic's Claude Code team has been remarkably open about how they work. Boris Cherny, who leads the project, runs 5 parallel Claude Code instances simultaneously, each in its own git checkout. He's spoken about it on [Lenny's Podcast](https://www.lennysnewsletter.com/p/head-of-claude-code-what-happens), the [YC Lightcone](https://www.ycombinator.com/library/NJ-inside-claude-code-with-its-creator-boris-cherny), and various interviews. The man ships 259 PRs a month by essentially acting as a dispatcher for multiple AI agents.

He's also public about the tools his team uses: `/code-review` spawns adversarial subagents. `/simplify` runs parallel quality checks. The writer/reviewer pattern, where one instance writes code and a fresh instance reviews it, is a core part of their workflow.

I wrote about this in a [previous post](/posts/steal-boris-chnernys-claude-code-workflow/). But reading about it and living it are different things. The gap between "run five terminal tabs" and "have agents that actually coordinate" is where pi-team-agents was born.

## What it does

The plugin adds multi-agent team coordination to pi. You create a team, spawn specialised agents into it, and they collaborate through a shared task board and mailbox system. Each agent runs as an in-process session with its own context window, its own tools, and its own understanding of what it's supposed to be doing.

There are two main workflows:

**`team_dispatch`** is the simple one. You describe what you want, it spawns the right number of agents, waits for all of them to finish, and hands you the results in a single response. No coordination overhead. No polling. Just "go do these things and come back when you're done."

```
team_dispatch({
    agents: [
        { name: "r1", agent: "researcher", prompt: "Audit src/auth/ for security issues..." },
        { name: "r2", agent: "researcher", prompt: "Check all API endpoints in src/api/ for..." },
    ]
})
```

**`team_create` + `team_spawn`** is for when you need a sequential pipeline. Research first, then plan, then implement, then review. Each stage feeds into the next, and you stay in control throughout.

The built-in agents cover the common roles: researchers (read-only, fast, safe), planners (architecture and design), coders (full read/write), reviewers (code audit), and a general-purpose agent that can search the web.

## The design decisions that mattered

Building this taught me a few things about what makes multi-agent systems actually work versus just being cool demos.

### Mailboxes, not shouting

Agents communicate through mailboxes. When one agent sends a message, it writes to a JSON file in the recipient's inbox directory. The recipient polls their inbox between turns. This sounds low-tech compared to some message queue or RPC system, but it has one enormous advantage: it's debuggable. When something goes wrong, you can literally `cat` the mailbox files and see exactly what messages were sent, when, and to whom.

The protocol routing was important too. Not every message should reach the LLM's context. Idle notifications, shutdown requests, and task assignments are structured messages that get routed to handlers, not dumped into the prompt. Only actual human-meaningful messages get delivered to the agent's context window. This saves tokens and reduces confusion.

### Separation of core from SDK

The core logic (`team-core.ts`) has zero imports from the pi SDK. Everything is pure functions operating on the filesystem. This means the entire logic layer is unit-testable without API keys, without LLM sessions, without anything except Node.js and a temp directory.

The extension layer (`team-agents.ts`) handles the SDK wiring: tool registration, agent spawning, event subscriptions. It's the adapter between the pure logic and the pi runtime.

This separation saved me repeatedly. When I needed to debug the mailbox system, I wrote tests against the core. When I needed to change how agents were spawned, I only touched the extension. The two layers evolved independently, which kept the complexity manageable.

### File-based state with locking

All state is stored as JSON files with directory-based locking. The lock is simply a `mkdir` call, which is atomic on most filesystems. This handles concurrent writes correctly: two agents writing to the same mailbox at the same time will serialise rather than corrupt each other's data.

Is it as fast as Redis? No. Is it fast enough for agents that take seconds per turn? Absolutely. And it has the benefit of zero infrastructure dependencies.

### Blocking dispatch

The `team_dispatch` tool is deliberately blocking. Once called, the LLM can't do anything else until all agents finish. This was a hard-won lesson: when the leader LLM is free to act during a dispatch, it inevitably does unhelpful things. It polls `agent_output` when there's nothing new. It reads shared memory that hasn't been updated. It deletes the team prematurely. Blocking removes the temptation entirely.

Progress is streamed to the terminal via `onUpdate`, so you're not staring at a blank screen. You see "2/3 agents completed" ticking up in real time.

### Graceful shutdown

Shutting down agents is a structured protocol, not a kill signal. The leader sends a shutdown request. The agent's model decides whether to approve it. If the agent thinks it has critical work unfinished, it can reject the shutdown with a reason. After a timeout, the leader force-kills.

This matters because agents sometimes have genuinely important state in progress. A coder that's half-way through writing a complex refactoring shouldn't be yanked mid-function. The model gets to have an opinion about its own lifecycle, which is both technically sound and slightly unnerving.

## What I learned

The biggest surprise was how well the skill system works. The `team-work` skill in the plugin analyses a task, decides what agents are needed, and chooses the right workflow automatically. In practice, you just describe what you want and pi figures out the team composition. "Research the codebase and plan a migration to TypeScript" becomes: spawn two researchers in parallel, wait for their findings, then spawn a planner with the synthesised context.

The anti-patterns were instructive too. Spawning a coder without a plan is a recipe for chaos; the agent explores randomly instead of implementing. More than five agents and coordination overhead exceeds the benefit. Vague prompts like "implement the feature" fail consistently; specific prompts like "edit src/foo.ts to add function bar() that does X, following the pattern in src/baz.ts" work reliably.

## Standing on shoulders

None of this is truly novel. The concepts are all borrowed from Anthropic's work on Claude Code: the parallel agent pattern, the writer/reviewer workflow, the task board, the structured communication. What pi-team-agents does is package these ideas into an installable plugin that works with an open-source coding agent.

If you're using pi, give it a try:

```bash
pi install git:github.com/Jabbslad/pi-team-agents
```

And if you're not using pi but are curious about multi-agent coordination patterns, the [architecture docs](https://github.com/Jabbslad/pi-team-agents) and [design notes](https://github.com/Jabbslad/pi-team-agents/blob/master/DESIGN-team-dispatch.md) are worth a read. The patterns are transferable regardless of which AI tool you use.

The future of AI-assisted development isn't one omniscient model that does everything. It's teams of specialised agents that divide, conquer, and collaborate. We're just starting to figure out what that looks like in practice.

---

*Thanks to the Anthropic team, particularly Boris Cherny, for being so transparent about how they build with AI. And thanks to Mario Zechner for building pi with an extension system that made this plugin possible.*
