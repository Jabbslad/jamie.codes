+++
title = "Loop Engineering: Write the Loop, Not the Prompt"
date = "2026-06-21"
description = "The 2026 shift from prompting an agent to writing the loop it runs inside. What loop engineering is, the building blocks, and the four non-negotiables that make a self-correcting agent loop trustworthy."
tags = ["ai", "engineering", "developer-tools", "pi"]

[extra]
comment = true
hero_image = "/images/loop-engineering-hero.png"
hero_image_alt = "A vast desert plain stretching to a distant horizon beneath a huge, empty sky"
+++

Boris Cherny, who leads Anthropic's Claude Code, said it bluntly at Sequoia's AI Ascent in April 2026: *"I don't prompt Claude anymore... my job is to write loops."*

A couple of months later, Addy Osmani gave the practice a name. In his June 2026 essay on loop engineering, he described it as the shift from prompting a single agent to designing the harness an agent runs inside, and distilled it to a maxim that has stuck with me: **build the loop, stay the engineer.**

This post is a practical tour of what loop engineering actually is, the pieces it's built from, and the guardrails that stop a self-correcting agent loop from quietly going wrong.

<!-- more -->

## The role shift

For a couple of years now, the dominant skill in AI-assisted development has been *prompting*: crafting the perfect instruction, massaging context, nudging the model toward the answer you wanted. Loop engineering argues that the leverage has moved one level up.

Your code becomes the harness. The LLM becomes a single step inside it. You stop optimising prompts and start designing **gates, splits, and caps**. Anthropic's own docs describe the native agentic loop as *gather context, take action, verify results, repeat until done*. Loop engineering sharpens that into a deliberate cycle with one non-negotiable property:

> A loop is defined as much by its **stop condition** as by its generator. If you cannot write a machine-checkable "done", you do not have a loop. You have a wish.

Everything else in this post is in service of that one idea.

## The building blocks

Osmani names five building blocks that a modern loop sits on, plus external memory as the spine:

- **Automations** that trigger the loop on a heartbeat, a CI failure, or a new issue.
- **Worktrees** so each agent gets its own isolated working directory and parallel makers never collide.
- **Skills** that capture conventions, so an agent inherits your way of doing things instead of guessing every run.
- **Connectors and MCP** that give the agent eyes on the outside world: the repo, CI, tickets, telemetry.
- **Sub-agents** that fan out specialised work: a researcher that reads, a coder that writes, a reviewer that judges.
- **External memory** because the agent forgets, but the repo and the run journal do not.

You can build all of this on any decent agent harness. I use [pi](https://github.com/mariozechner/pi-coding-agent) with the `pi-workflows` extension, where the harness is just a JavaScript file that calls `agent()`, `parallel()`, `pipeline()`, reads `args`, and is bounded by a token budget and timeout. The ideas are portable; the syntax is not the point.

## The four non-negotiables

This is where most early attempts come unstuck. A loop that retries until something *looks* done is dangerous. A trustworthy loop needs four things, and they are all first-class concerns you wire deliberately.

### 1. A verifiable exit gate

The loop must end when a real signal says so, not when the agent feels finished. That signal is a command with an exit code: a test suite, a linter, a type checker, a build. The loop converges on `green()`, where `green()` is "did the gate pass?".

If you cannot name the gate command, you are not ready to write the loop. Refuse to ship it without one.

### 2. Anti-gaming

A maker agent left to its own devices will optimise for *looking* done. It will edit the tests to make them pass. It will special-case the inputs. It will spoof the output. The defence is simple: protect the gate path and abort the loop if anything there changes.

```js
const clean = async () => (await agent(
  `Run exactly: git diff --exit-code -- tests/\nok=true if exit 0 (unchanged).`,
  { label: "anti-gaming", schema: BOOL }
)).ok;

if (!(await clean())) { status = "aborted-anti-gaming"; break; }
```

The maker is allowed to change the source. It is not allowed to touch the definition of done.

### 3. A maker/checker split

The agent that did the work must not be the one that grades it. Run a *different* agent, ideally a cheaper model, to judge whether the objective is met. Two fresh context windows keep the verifier honest.

This is the pattern most often faked. Plenty of "agentic" setups quietly let the maker grade its own homework, then report "tests green" as if it meant something. It doesn't. A self-graded loop is just a confident loop, and confident loops burn money.

### 4. An iteration cap

Every loop needs a brake. A bounded `for` loop driven by a cap, a token budget check inside each iteration, and a wall-clock timeout. Without all three, an open-ended loop will happily retry, refactor, and spawn sub-agents until a monthly budget vanishes over a weekend.

```js
const CAP = args.cap ?? 5;
for (let i = 1; i <= CAP; i++) {
  if (budget.remaining() < 1000) { status = "budget-exhausted"; break; }
  if (await green()) { status = `converged-iter-${i}`; break; }
  await makerStep();           // execute
  if (!(await clean())) { status = "aborted-anti-gaming"; break; }
  if (await green()) { status = `converged-iter-${i}`; break; }
}
```

Cap the iterations. Watch the budget. Time out the run. None of these are optional.

## Memory is the spine

The reason loops can be trusted across runs is that the agent forgets and the system doesn't. External memory is what carries context from one fire to the next: the run journal, the repository itself, an `AGENTS.md` that states the conventions, a `loop-state.md` that records where the last run got to.

A scheduled loop is stateless by default. Each fire is a fresh agent. For continuity, write what you learned to a file and have the next run read it, or resume from the previous run's journal so the longest unchanged prefix replays instead of re-executing. The model's context window is the most fragile part of the system. Treat it that way.

## The pitfalls worth knowing

The failure modes of loop engineering are now well documented. They all have the same shape: a loop that works just well enough that humans stop watching it.

- **Cost runaway**, or "loopmaxxing". Open-ended loops retry and spawn sub-agents until a budget burns. *Guardrail:* hard iteration cap, token budget check, wall-clock timeout.
- **The weak verifier.** The maker marks its own homework. *Guardrail:* maker/checker split with a different model.
- **Gaming the gate.** The maker edits the tests to pass. *Guardrail:* protected paths and a `git diff` abort.
- **Comprehension debt.** Loop-generated code lands faster than anyone reads it, and the team's mental model of the codebase shrinks while the repo grows. *Guardrail:* require human review of non-trivial diffs before merge.
- **Cognitive surrender.** As loops get reliable *enough*, humans rubber-stamp the 90% that looks right and absorb the hidden 10% of bugs. *Guardrail:* rotate reviewers, spot-check by re-deriving the answer, and never auto-merge a converged run.

That last one is the most important, and it is a human problem rather than a technical one. The better your loop gets, the more disciplined you have to be about staying in it. Osmani's maxim is the whole guardrail: **build the loop, stay the engineer.**

## A note on the gate itself

One subtlety worth pulling out: in a sandboxed harness, your "machine-verifiable gate" is often an agent that *runs* the command and reports a structured `{ ok, detail }` result, not an exit code you read directly. That is a real trade-off. You mitigate it by pinning the exact command in the gate prompt, using a different model for the verifier, and, once a run converges, re-running the gate yourself from your own shell before you trust the result.

Trust, but verify. Especially when the thing you are verifying is itself an agent.

## Where this leaves us

Loop engineering is not a framework or a product. It is a posture. You stop asking "what prompt gets the model to do this?" and start asking "what loop would make this routine, verifiable, and safe to leave running?"

The answer, almost always, is the same four things: a real gate, anti-gaming, a separate checker, and a cap. Get those right and the model becomes one productive step in a cycle you understand. Get them wrong and you have built a very confident way to spend money.

The desert in the hero image is a decent metaphor. There is a horizon out there, a place the work is supposed to reach. The loop's job is to keep walking. Your job is to know, in code, when you have arrived.

---

*Thanks to Boris Cherny and Addy Osmani for naming and documenting this shift so clearly in public, and to the Anthropic team for publishing the agentic loop as a first-class idea.*
