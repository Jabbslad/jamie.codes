+++
title = "The Great Monorepo Unbundling: Why Big Tech is Fragmenting for the AI Agent Era"
date = "2026-01-31"
authors = ["Stephen Bennett"]

[taxonomies]
tags = ["ai", "software-architecture", "monorepo", "engineering"]

[extra]
comment = true
+++

There's a quiet revolution happening in the engineering departments of the world's largest technology companies. According to recent industry chatter, FAANG-style organisations are actively refactoring their legendary monorepos — those massive, unified codebases that have been the backbone of their engineering culture for over a decade.

The reason? They're preparing for what insiders are calling "infinite agent code."

<!-- more -->

## The Monorepo Era: A Brief History

For the uninitiated, a monorepo is a single repository containing all of an organisation's code. Google famously operates one of the largest, housing billions of lines of code in a single repository. Facebook, Microsoft, and others followed suit, building sophisticated tooling to make this approach work at scale.

The benefits were compelling:
- **Atomic changes** across multiple services
- **Unified versioning** eliminating dependency hell
- **Code reuse** through shared libraries
- **Consistent tooling** and developer experience

Companies invested millions in custom build systems (Bazel, Buck), code review tools, and infrastructure to make monorepos viable at scale.

## The Agent Inflection Point

So why the sudden reversal? The answer lies in understanding how AI coding agents actually work.

Modern AI agents don't just autocomplete your code — they reason about entire codebases, understand architectural patterns, and make sweeping changes across multiple files. They're getting better at this every month. But they face a fundamental limitation: **context windows**.

Even with context windows expanding to millions of tokens, a multi-billion line monorepo presents unique challenges:

### 1. Context Pollution

When an AI agent needs to modify a payment service, it shouldn't need to wade through unrelated code from the video encoding team. In a monorepo, establishing relevant context becomes exponentially harder. The agent either:
- Includes too much irrelevant code, wasting tokens and introducing noise
- Misses crucial dependencies because it couldn't fit them in context

### 2. Blast Radius Amplification

AI agents can now make changes across hundreds of files in seconds. In a monorepo, a subtle misunderstanding of one team's conventions could cascade into breaking changes across dozens of services. The same interconnectedness that made atomic human changes easy makes autonomous agent changes terrifying.

### 3. Ownership and Accountability Blur

With human engineers, code ownership in monorepos was already complex. With agents generating code at scale, the question "who owns this change?" becomes nearly impossible to answer. Fragmenting repositories creates natural boundaries for agent operations.

### 4. Testing and Validation Bottlenecks

Monorepo CI/CD systems weren't designed for the volume of changes that agent-assisted development produces. When every engineer has an AI pair programmer generating PRs at 10x the previous rate, centralised build systems become immediate bottlenecks.

## The New Architecture: Federated Repositories

What's emerging isn't a return to the bad old days of completely isolated repositories. Instead, companies are moving toward a **federated model**:

- **Domain-bounded repositories** aligned with team ownership
- **Explicit API contracts** between repos, enforced by tooling
- **Agent-optimised documentation** that serves as context for AI systems
- **Standardised scaffolding** so agents can reason about unfamiliar codebases quickly

This architecture gives AI agents clear boundaries while maintaining the coordination benefits of shared infrastructure.

## The Tooling Gap

The transition isn't without challenges. A decade of monorepo tooling doesn't translate directly:

- **Cross-repo refactoring** needs new tools
- **Dependency management** becomes critical again
- **Version compatibility** matrices return with a vengeance

Companies are betting that AI agents themselves will help bridge this gap — using agents to manage the complexity that distributed repositories reintroduce.

## What This Means for Engineering Culture

The implications extend beyond architecture:

**Team autonomy increases.** With clearer repository boundaries, teams gain more control over their technical choices.

**Agent specialisation becomes viable.** You can fine-tune or configure agents for specific domains rather than teaching them your entire organisation's conventions.

**Hiring patterns may shift.** Engineers who excel at defining clear interfaces and documentation become more valuable than those who navigate complexity through tribal knowledge.

## The Irony

There's a certain irony here. Monorepos emerged partly because distributed systems were too hard for humans to coordinate. Now, as AI agents become capable of managing that coordination complexity, the pendulum swings back.

We're not simplifying for human comprehension — we're restructuring for machine comprehension. The agents work better with clearer boundaries, so we're giving them clearer boundaries.

## Looking Forward

The "infinite agent code" future isn't about agents writing unlimited amounts of code. It's about agents becoming genuine collaborators in software development at every scale. For that to work, our systems need to be legible to them.

The FAANG companies fragmenting their monorepos aren't abandoning the benefits of unified codebases. They're evolving toward an architecture that serves both human and artificial intelligence.

The question isn't whether this transition will happen elsewhere. It's whether your organisation will lead it or be forced to catch up.

---

*Stephen Bennett is a software architect and engineering consultant specialising in developer experience and tooling evolution. He writes about the intersection of AI and software engineering practices.*

*Originally sparked by [this observation](https://x.com/samswoora/status/2017625209096835552) from @samswoora on X.*
