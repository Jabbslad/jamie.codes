+++
title = "Dynamic Factories: the factory that rebuilt itself while building Kiln"
date = 2026-10-21
updated = 2026-10-22
draft = false
description = "Agentic software factories already write, test, merge and deploy code, but people still design their shape. A Dynamic Factory reshapes itself from what it measures. Notes for engineering leaders, with the factory that builds Kiln as an early working example."
tags = ["ai", "engineering", "developer-tools", "kiln"]
aliases = ["/posts/grok-bot-agents-prs/"]
+++

Agents can already run most of a software factory. They write the code, open the PRs, run CI, merge and deploy. What they don't do yet, in most setups I've seen, is decide what the factory looks like. A person still chooses which agents exist, what each one does, and where the gates and handoffs sit.

Over the past few days I watched a factory start making those choices for itself. It added a specialist when it was missing a skill, retired one that had stopped earning its place, and rewrote its own pipeline from what it measured. I've started calling this a Dynamic Factory. I think it's where agentic factories are heading, and this post describes an early working example.

The product it built is [Kiln](https://github.com/Jabbslad/kiln), a self-hosted tool for booting and deploying Firecracker microVMs on your own bare-metal server. In three days the factory merged 137 PRs and published 61 releases of it. Kiln is what came off the line. This post is about the line.

## Agentic software factories, and where they stop

The agentic software factory is already a real thing. Coding agents take a task, work in their own VM, open a PR, and fix it when CI goes red. With a merge rule and a deploy job, code can go from request to production without a person touching it.

That kind of factory is automated, but its shape is fixed. A person designed it. They decided there would be a reviewer agent, a deploy step and an approval gate before release, and they wired the handoffs between them. When the work changes, the shape doesn't change with it until someone redesigns it.

I ran into that limit on the second day. The agents were opening PRs faster than the line could move them, and I asked my assistant:

> Why so few? Stuff has been happening all day but I'm struggling to understand why it's taken so long for anything to get deployed.

The answer was that every stage waited for another bot to notice it was its turn. That evening, a release that was already built and packaged took about two and a half hours to go from published to working. The agents weren't slow. The shape I had designed was.

## The Dynamic Factory

A Dynamic Factory designs and reshapes itself. In the setup I run, that shows up in five ways.

**It staffs itself.** When the factory is missing a capability, it adds a specialist bot. When a bot stops earning its place, the factory retires it. Perfy arrived to own lead time. Proof, the reviewer, left once CI could do its job.

**It rewrites its own pipeline from what it measures.** A check that a bot did by hand becomes a CI job. A check that tested the wrong path moves onto the real one. When risky changes held up routine ones, the factory started building a slow lane.

**It scales with the work and routes by risk.** Each job gets its own cloud agent, so more work means more agents working in parallel, though merges still go one at a time. Changes that touch deploys, sign-in or SSH take a slower path than the rest.

**It holds itself to targets it agreed.** Perfy agrees lead-time targets with Chief and checks them against quality limits every weekday.

**The human runs the factory, not the line.** I set the goals and the hard limits, and I approve the few things that touch identity, keys or money. I don't design the stages, and I don't write the product.

## The factory behind Kiln

The factory is a team of bots and the rules around them. Here is who does what today:

- **Grok Bot** is my single point of contact. I talk to it from a desktop app.
- **Chief** is my chief of staff. It relays work to the engineering side and keeps the chatter out of my chat.
- **Forge** is an engineering lead that never writes code. It turns requests into jobs for Cursor cloud agents, each in its own VM, and follows each PR through to release.
- **Kiln Ops** looks after deploys. It's the only bot that holds the deploy key, and it makes the rare change that has to happen on the server by hand.
- **Perfy** owns lead time and the targets that go with it.
- **CI** is the reviewer. A PR merges when every check is green.

It didn't start like that. On the second day the factory looked like this, with a reviewer bot in the middle and every handoff waiting for another bot's turn:

![The factory on day two: every handoff waits for another bot's turn](/images/grok-bot-agents-prs/diagram-before.png)

Over the next two days it reshaped itself. Proof's checks moved into CI, and Proof retired. The release tag that someone had to push went away, so a green merge now releases and deploys in the same run. Chief took over as the layer between me and Forge. Perfy joined when lead time needed an owner. This is the factory now:

![The factory now: Chief and Perfy set the targets, CI reviews, and a green merge releases and deploys](/images/grok-bot-agents-prs/diagram-after.png)

## The operating rules

These are the 15 rules the factory runs on. It learnt each one from something that went wrong or took too long while building Kiln, and encoded it into its own checks, roles or targets. I've grouped them by what they govern.

### How it's staffed

#### 1. Give agents short, strict rules

Agents copy whatever is easiest, so the factory's rules make the easy thing the right thing. A few short rules for every job work better than long instructions per task.

Every brief Forge writes tells the agent to use [pstack](https://github.com/cursor/plugins/tree/main/pstack), the skill pack from Lauren Tan, who posts as [poteto](https://x.com/poteto). Its rules are short: make the smallest diff, fix the root cause, and prove it works. On the first afternoon the agents moved Kiln's installer from Python to bash, added a deploy from GitHub Actions, put the CLI behind sign-in and started serving the dashboard API.

#### 2. The slow part is the waiting, so automate every handoff

When a stage waits for someone to notice it's their turn, it waits a long time. Every handoff in the factory starts on its own.

Early on, a review took about 15 minutes and every fail meant another round trip. One PR sat idle after rework because nobody asked for a new review. So the factory removed the turns. The review verdict became a commit status, which gave the merge a gate that a machine can read. Then a release tag started the deploy. Then the tag went too. A green push to main now picks the next version, builds, attests, publishes and deploys in the same run, and nobody has pushed a tag by hand since.

### How quality is built in

#### 3. CI is the reviewer

A PR merges when every check is green at its current head commit, one PR at a time. No human or bot review step sits in the way.

poteto's team runs an agentic code review that rates every PR for risk, and low and medium risk PRs merge without a human:

{% tweet(id="2108283057581195413", user="poteto", name="lauren", date="October 8, 2026") %}
we have agentic code review, so every PR gets assessed for risk. low-medium risk ones don't require a review so you just merge it. also bugbot of course

there's many more interesting ideas we have for the agentic forge that we've been discussing cc @jacobgold
{% end %}

The next day she put it more bluntly:

{% tweet(id="2108394806548566459", user="poteto", name="lauren", date="October 9, 2026") %}
anything requiring a human review step is ngmi
{% end %}

A week later she posted what she calls an inverse pyramid of trust. Most of the effort goes into the codebase, then static analysis and tests, then prose such as rules and skills, and the least into human review:

{% tweet(id="2111133080526495985", user="poteto", name="lauren", date="October 16, 2026") %}
how do you trust your agents' work more? copy this post/link and give it to your @bot or agent!

1. codebase improvements: this is just good software engineering - better architecture, stronger types and invariants, clear boundaries. agents love to copy what exists and take the shortest path, so make the easy thing the right thing. categorically eliminate problems through code and you won't need to think about it again.
2. static analysis: lint rules, tests, CI, verification (eg TLA+). very token efficient ways to catch issues ahead of time.
3. prose: comments, rules, AGENTS.md, skills - anything that can't be enforced and requires agent judgment. use it minimally, but do use /create-verification-skill.
4. human review: the hardest to scale. at the rate agents land code, it's pretty much impossible to thoroughly review every PR, so spend that effort on the highest leverage point, designing an environment where agents do the right thing by default.

this forms an inverse pyramid: you want most of your effort at the top, least at the bottom.
{% end %}

Proof was a review step on every PR, the layer she spends least on, so the factory retired it. CI flags any PR that touches workflows, deploys, sign-in or secrets as risky. Releases carry GitHub build attestations, and CI checks every signature before it publishes a release.

#### 4. If a bot checks it by hand, it should be a CI job

A check that lives in a bot's head runs when the bot gets round to it. A check in CI runs on every push. Every incident also leaves a guard behind, so the same mistake fails the build next time.

Proof knew how to drive a change like a user. Kiln Ops knew to run the doctor command and boot a smoke box. Forge knew to ask for a new review after a push. All of that is code now. CI guards attestations, secrets and tool downloads, and refuses a release whose tag doesn't match the version in the code. poteto [reviews the videos and screenshots her agents record](https://x.com/poteto/status/2107529532144234937) rather than reading every diff, so any PR that changes the dashboard or the CLI now carries before and after screenshots from a script anyone can rerun.

The guards came from mistakes. Once, the deploy ran with an empty SSH key, because GitHub doesn't pass secrets into a reusable workflow unless the caller asks. The fix came with a CI check that fails any caller that forgets. In the 165 PR builds after the afternoon of 21 October, 49 went red before merge.

#### 5. A check that only runs after merge doesn't protect main

If a test only runs on main, the PR that breaks it will look green.

When the CI checks moved from Python to Rust, the Windows client job on main failed straight away. A test read a bash script, Git on Windows checked the script out with Windows line endings, and the parser panicked. The PR had passed because that test only ran on pushes to main. Main stayed red for about four hours, until a fix landed and the same tests started running on pull requests. A release tag later failed while stamping the version, so the whole release path now gets a dry run on every pull request too.

#### 6. Green has to mean live

A deploy checks what's running on the server, not only that its own steps finished.

One release shipped a new dashboard, but the deploy never installed it. The server kept serving the old one and the job still went green. Now every deploy installs the dashboard and fails if the live site serves anything other than the bundle in the release. After restarting the sign-in service, the deploy also checks that the login page still answers before it carries on.

#### 7. Checks must test the real path

A check is only as good as the path it takes. The factory tests from the outside, in typed code, and on an upgrade as well as a fresh install.

It learnt this three ways in one day.

*From the outside.* When SSH went through Kiln's public front door, the deploy check passed because it called the door service directly on the server. From a laptop, the request goes through a web proxy first. The proxy spoke HTTP/2 to the door, and HTTP/2 can't carry the SSH upgrade request, so every real user got an error. The fix pinned the proxy to HTTP/1.1 and moved the check onto the public address that laptops use. The new check then failed the next deploy, correctly, because the deploy never updated the live proxy config. Fixing that took a decision from me and a one-off manual change by Kiln Ops.

*In typed code.* Three deploys in a row failed at a new dashboard metrics check. The first two times, the host CPU value came back empty. The third time, the check script needed `jq`, which the server doesn't have. The check is now a typed Rust self-check inside the server binary, and CI fails if a deploy script calls `jq`.

*On an upgrade.* A change moved the server's operation journal to a new schema version. The installer only accepted the old version, so the next upgrade failed halfway through. A fresh install would have worked. CI now rehearses an upgrade from an old journal and checks that the server and installer agree on the version. Separately, the sign-in service had reported the same old version for many releases, because the deploy skipped replacing it whenever the bytes matched.

#### 8. Every fix brings a new bug, so make undoing cheap

At this speed, fixes cause their own problems. The factory keeps each step narrow, rolls back without waiting for a person, and hides unfinished features behind a one-line switch.

A deploy opened so many SSH connections that it hit the server's limit and failed. The fix shared one connection for the whole job. That fix had its own bug. Cleanup ran after the shared connection had closed. The follow-up landed 47 minutes later, with a test that refuses SSH calls once the connection has gone.

Kiln's dashboard now has one typed list of features, each marked available or not yet, and tests fail if an unfinished feature looks broken. The first time the dashboard showed SSH commands, they didn't work from a laptop. The revert took the same 10 minutes from merge to live as the mistake had. The second time, hiding them again was a one-line change that merged 37 minutes after the feature it hid. When the upgrade failed on the journal schema, the installer put the previous version back.

The factory doesn't fully meet this rule yet. If a deploy fails at a check after the install, the new version stays in place even though the deploy shows red. That happened during the metrics failures above.

#### 9. Retry only the failure you understand

Blanket retries hide real problems. The factory retries the one flaky thing it has diagnosed, and fails loudly on everything else.

One release never got published, because the signature checker failed to start on GitHub's side. The tag existed, but the release didn't. The fix retries that exact error three times with a short backoff. Any other verification failure still fails on the first attempt and prints what went wrong.

### How it measures and tunes itself

#### 10. Measure lead time by stage, and give it an owner

A single total hides the cause. The factory breaks the time from open to live into stages, and one bot is responsible for the number.

Perfy measured the 46 PRs merged after a green main started releasing itself. Merge to live takes about 12 minutes at the median, which is fine. The surprise was before the merge. Green PRs waiting to be merged made up about 78% of all the time those PRs spent open. The total would never have shown that.

That measuring job is why Perfy exists. It keeps the stage breakdown current and agrees speed targets with Chief, so someone looks after the number every day rather than when I happen to check.

#### 11. Every speed target comes paired with a quality limit

A faster pipeline only counts if it isn't breaking more. A speed target holds only while the flake rate, deploy failure rate and change failure rate stay the same or improve.

Flaky failures are rare, about 0.1% of job runs. Deploy failures are not. About 14% of deploys since releases became automatic failed, mostly at the new checks that run after the install. Roughly one merged PR in six was a fix or revert of something merged the day before. That last figure is rough, because a follow-up isn't always a fix for a failure.

Perfy checks these limits every weekday alongside the speed numbers. The rules that keep quality up don't bend to meet a target. CI is still the reviewer, and anything a bot checks by hand still becomes a coded check.

#### 12. Check the critical path before you count a win

A stage is only worth speeding up if it's on the critical path. The factory looks at what else has to finish first.

Skipping the duplicate test run on main after a merge looked like an easy win, since the tests had already passed on the PR. Measured, it saves about 1.4 minutes at the median. The tests run alongside packaging and signing, which finish only slightly earlier, so the release still waits.

#### 13. Treat a slowing build as a warning sign

Build time creeps up one reasonable change at a time. The factory tracks it, because nobody notices a slow drift.

The median PR CI run went from about 2 minutes on the first day to about 10 by the fourth. Each new check was worth adding, and nobody noticed the total until Perfy measured it. A typical PR now goes round CI three or four times before it merges, so the extra minutes add up.

### Where the human sits

#### 14. Talk to one bot and keep the chatter out of your chat

The factory puts a layer between me and the engineering bots, so I see decisions rather than build logs.

At first I asked Grok Bot to start coding jobs directly, and my chat filled with build logs and PR links. Forge took that noise away. Later I copied poteto's setup one step further. She mostly talks to her chief of staff, who talks to her engineering lead, so the factory got Chief. The bots now argue among themselves in a group chat, and I hear about it when something needs me.

#### 15. Once the machine is fast, the queue and the human are the bottleneck

When merge to live takes about 12 minutes, the slow part moves to the merge queue and to anything waiting for a person. The list of things that need a yes stays short.

The bots have a standing yes for routine PRs, merges, releases and deploys. A short list still needs me: force-pushes, tags and branches, repo settings, secrets and keys, server access keys, and anything touching identity or login.

That list is where the time goes now. The PR that changed how Kiln's dashboard gets its login token touched login, so it waited for me, and it took about 24 hours from open to merge, the longest of the lot. The proxy fix above waited for my decision in the morning. The rest of the slow tail is the queue. PRs merge one at a time, and a long PR keeps having to merge main back in while others go first. Three PRs took between 12 and 15 hours.

Risky PRs wait longest. The slowest tenth of them sat green and unmerged for more than nine hours, and several went green in the afternoon but didn't merge until the early hours. Meanwhile, 15 PRs merged overnight with nobody awake. The automated stages keep up. The waits are in the queue and with me.

## What came off the line

Kiln boots Firecracker microVMs, called boxes, on a bare-metal server. You ask for a box and get SSH, a dashboard and a sign-in, and Kiln's installer handles upgrades and rollbacks on the server. Its output over three days, starting from the first PR at 12:58 on 19 October, is the best evidence I have that the factory works:

- 137 PRs merged, out of 149 opened.
- 61 releases went out.
- Merge to live takes about 12 minutes at the median, since a green merge started releasing and deploying itself.
- 15 PRs merged between midnight and 8am on 22 October, with nobody watching.
- Open-to-merge time fell to a median of 13 minutes once CI became the reviewer, then rose to 50 minutes as the queue and my yeses became the bottleneck.

![PRs opened and merged per hour on Kiln, with release times marked](/images/grok-bot-agents-prs/prs-per-hour.png)

![Where the time goes from PR opened to live, by stage](/images/grok-bot-agents-prs/time-by-stage.png)

![Median and P90 open-to-merge time by phase](/images/grok-bot-agents-prs/open-to-merge-by-phase.png)

## What it means for engineering leaders

The main point is that the factory is portable. Nothing in the bots or the rules above is specific to Kiln. Point the same setup at a different product and it reshapes itself again. It adds the specialists that product needs, retires the ones it doesn't, and turns that product's manual checks into CI jobs. An agentic pipeline built around one codebase can't do that. Its shape is tied to that codebase.

That changes what you build. Instead of a pipeline per product, you build a factory with rules, targets and the ability to restaff itself, and you give it products.

It also changes your job. You run the factory. You set its goals, its quality limits and the short list of things only you approve. You don't design the stages, and you don't build the product. Keep the approval list short, because every item on it waits for you.

A few things carry over from the rules. Review capacity won't keep up with agent output, so put review into code. Measure the factory by stage, and pair every speed target with a quality limit, or a faster pipeline can become a less reliable one without anyone noticing.

## What's next for the factory

- A slow lane for risky PRs, so routine work doesn't queue behind them. It's open now. CI already skips jobs a change can't affect.
- A daily SLO check on lead time and the quality limits, so a slip in either shows up within a day.
- Roll back on any failed check, not only a failed install.
- Run the deploy's final checks on a throwaway stand-in server in CI, so a bad check fails there and not on the real one.
- Point the factory at a second product, and see how much of its shape it rebuilds on its own.
- Keep moving checks into code. Every time I catch myself asking a bot "did you test X?", that's a missing CI job.

Thanks to poteto for writing so openly about how she works with agents. Much of this factory started as one of her posts.
