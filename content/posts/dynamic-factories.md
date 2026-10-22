+++
title = "Dynamic Factories: when the software factory rebuilds itself"
date = 2026-10-21
updated = 2026-10-22
draft = false
description = "A classic software factory is a fixed line that people design once and staff at the slow steps. With agents doing the building, the line has to rebuild itself. Notes for engineering leaders, with kiln as the case study."
tags = ["ai", "engineering", "developer-tools", "kiln"]
aliases = ["/posts/grok-bot-agents-prs/"]
+++

Most mature engineering organisations run some kind of software factory. Code went in at one end, and tested, packaged, deployed software came out of the other. Over the past few days I've watched agents outgrow that idea. The factory still works, but it's now the slowest part of delivery.

This post is about what replaces it. I've started calling it a Dynamic Factory. It's a delivery system that adds and retires its own workers, turns its own manual checks into code, opens new lanes as risk demands, and measures and tunes its own lead time. The human stops working on the line and owns its rules instead.

My evidence is kiln, a small project where cloud agents opened 149 pull requests in three days and 137 merged. I didn't write any of that code. Kiln is the case study, though, not the subject. The subject is what happens to the factory once building gets cheap.

## The old factory

The software factory was a real step forward. CI ran the tests on every change. CD took the manual release weekend away. Platform teams built golden paths, so a new service got a pipeline, monitoring and a deploy on day one instead of after a month of tickets. If you lived through the move from hand-built releases to pipelines, you know how much it changed.

It was also a fixed line. People designed it once, around the work they expected, and then staffed it at the slow steps. Code review was a person. Release approval was a person. When the line was too slow, the fix was a better pipeline or more reviewers, and either one took a quarter to arrive. That was fine, because the work arriving at the line changed about as slowly as the line did.

## What changes with agents

Agents changed the input side. On kiln, the first afternoon of agent work moved the installer from Python to bash, added a deploy from GitHub Actions, put the CLI behind sign-in and started serving the dashboard API. Over the first two days, the median PR went from opened to merged in about 20 minutes.

The line didn't keep up. On my busiest day I asked my assistant:

> Why so few? Stuff has been happening all day but I'm struggling to understand why it's taken so long for anything to get deployed.

The answer was that every step on the line waited for someone to notice it was their turn. That evening, a release that was already built and packaged took about two and a half hours to go from published to working.

The other change is subtler. The work now changes daily. One day it's an installer, the next a dashboard, the next SSH through a proxy. Each kind of work needs different checks and carries different risk, and a line designed once can't follow it.

## The Dynamic Factory

A Dynamic Factory scales and rewires itself instead of waiting for someone to redesign it. In kiln, that happened in four ways.

**Workers come and go with the work.** The factory is a team of bots, and the team changes. Forge is an engineering lead that never writes code. It turns requests into jobs for Cursor cloud agents, each in its own VM. Kiln Ops deploys, and it's the only bot that holds the deploy key. Chief is my chief of staff. Proof reviewed every PR for a day and a half and then retired, because its work had moved into CI. Perfy arrived later to own lead time. None of these were planned on day one.

**Manual checks harden into code.** Each time a bot checked something by hand, that check became a CI job. Proof's review became a set of coded checks. Kiln Ops's habit of booting a smoke box after a deploy became a step in the deploy.

**Lanes open by risk.** Routine changes and risky ones don't need the same path. Changes that touch deploys, sign-in or SSH now count as slow lane, and a slow lane that merges them only after main has deployed green is being built now.

**The factory measures itself.** Perfy tracks lead time by stage, agrees targets with Chief, and checks them against quality limits. When a number slips, Perfy reports it.

Here's the line as it was on the second day, with every handoff waiting for another bot:

![The bot team on 20 October: every handoff waits for another bot's turn](/images/grok-bot-agents-prs/diagram-before.png)

And here it is now:

![The pipeline now: CI checks gate the merge, and a green push to main releases and deploys](/images/grok-bot-agents-prs/diagram-after.png)

## The operating rules

These are the 15 rules kiln's factory runs on. Each one came from something that went wrong or took too long. I've grouped them by what they govern.

### How it's staffed

#### 1. Give agents small, strict rules

Agents copy whatever is easiest, so the rules have to make the easy thing the right thing. A few short rules for every job work better than long instructions per task.

Every brief Forge writes tells the agent to use [pstack](https://github.com/cursor/plugins/tree/main/pstack), the skill pack from Lauren Tan, who posts as [poteto](https://x.com/poteto). Its rules are short: make the smallest diff, fix the root cause, and prove it works. 27 PRs merged before 2:30 the next morning under those rules.

#### 2. The slow part is the waiting, so automate every handoff

When a step waits for someone to notice it's their turn, it waits a long time. Every handoff should start on its own.

Early on, a review took about 15 minutes and every fail meant another round trip. One PR sat idle after rework because nobody asked for a new review. So I took the turns away. The review verdict became a commit status, which gave the merge a gate that a machine can read. Then a release tag started the deploy. Then the tag went too. A green push to main now picks the next version, builds, attests, publishes and deploys in the same run, and nobody has pushed a tag by hand since.

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

Proof was a review step on every PR, the layer she spends least on, so I retired it. CI flags any PR that touches workflows, deploys, sign-in or secrets as risky. Releases carry GitHub build attestations, and CI checks every signature before it publishes a release.

#### 4. If a bot checks it by hand, it should be a CI job

A check that lives in a bot's head runs when the bot gets round to it. A check in CI runs on every push. Every incident should also leave a guard behind, so the same mistake fails the build next time.

Proof knew how to drive a change like a user. Kiln Ops knew to run the doctor command and boot a smoke box. Forge knew to ask for a new review after a push. All of that is code now. CI guards attestations, secrets and tool downloads, and refuses a release whose tag doesn't match the version in the code. poteto [reviews the videos and screenshots her agents record](https://x.com/poteto/status/2107529532144234937) rather than reading every diff, so any PR that changes the dashboard or the CLI now carries before and after screenshots from a script anyone can rerun.

The guards came from mistakes. Once, the deploy ran with an empty SSH key, because GitHub doesn't pass secrets into a reusable workflow unless the caller asks. The fix came with a CI check that fails any caller that forgets. In the 165 PR builds after the afternoon of 21 October, 49 went red before merge.

#### 5. A check that only runs after merge doesn't protect main

If a test only runs on main, the PR that breaks it will look green.

When the CI checks moved from Python to Rust, the Windows client job on main failed straight away. A test read a bash script, Git on Windows checked the script out with Windows line endings, and the parser panicked. The PR had passed because that test only ran on pushes to main. Main stayed red for about four hours, until a fix landed and the same tests started running on pull requests. A release tag later failed while stamping the version, so the whole release path now gets a dry run on every pull request too.

#### 6. Green has to mean live

A deploy should check what's running on the server, not only that its own steps finished.

One release shipped a new dashboard, but the deploy never installed it. The server kept serving the old one and the job still went green. Now every deploy installs the dashboard and fails if the live site serves anything other than the bundle in the release. After restarting the sign-in service, the deploy also checks that the login page still answers before it carries on.

#### 7. Checks must test the real path

A check is only as good as the path it takes. Test from the outside, in typed code, and on an upgrade as well as a fresh install.

I learnt this three ways in one day.

*From the outside.* We added SSH through the public front door, and the deploy check passed because it called the door service directly on the server. From a laptop, the request goes through a web proxy first. The proxy spoke HTTP/2 to the door, and HTTP/2 can't carry the SSH upgrade request, so every real user got an error. The fix pinned the proxy to HTTP/1.1 and moved the check onto the public address that laptops use. The new check then failed the next deploy, correctly, because the deploy never updated the live proxy config. Fixing that took a decision from me and a one-off manual change by Kiln Ops.

*In typed code.* Three deploys in a row failed at a new dashboard metrics check. The first two times, the host CPU value came back empty. The third time, the check script needed `jq`, which the server doesn't have. The check is now a typed Rust self-check inside the server binary, and CI fails if a deploy script calls `jq`.

*On an upgrade.* A change moved the server's operation journal to a new schema version. The installer only accepted the old version, so the next upgrade failed halfway through. A fresh install would have worked. CI now rehearses an upgrade from an old journal and checks that the server and installer agree on the version. Separately, the sign-in service had reported the same old version for many releases, because the deploy skipped replacing it whenever the bytes matched.

#### 8. Every fix brings a new bug, so make undoing cheap

At this speed, fixes cause their own problems. Keep steps small, roll back without waiting for a person, and hide unfinished features behind a one-line switch.

A deploy opened so many SSH connections that it hit the server's limit and failed. The fix shared one connection for the whole job. That fix had its own bug. Cleanup ran after the shared connection had closed. The follow-up landed 47 minutes later, with a test that refuses SSH calls once the connection has gone.

The dashboard now has one typed list of features, each marked available or not yet, and tests fail if an unfinished feature looks broken. The first time I put SSH commands in the dashboard, they didn't work from a laptop. The revert took the same 10 minutes from merge to live as the mistake had. The second time, hiding them again was a one-line change that merged 37 minutes after the feature it hid. When the upgrade failed on the journal schema, the installer put the previous version back.

This rule isn't fully met yet. If a deploy fails at a check after the install, the new version stays in place even though the deploy shows red. That happened during the metrics failures above.

#### 9. Retry only the failure you understand

Blanket retries hide real problems. Retry the one flaky thing you've diagnosed, and fail loudly on everything else.

One release never got published, because the signature checker failed to start on GitHub's side. The tag existed, but the release didn't. The fix retries that exact error three times with a short backoff. Any other verification failure still fails on the first attempt and prints what went wrong.

### How it measures and tunes itself

#### 10. Measure lead time by stage, and give it an owner

A single total hides the cause. Break the time from open to live into stages, and make one bot responsible for the number.

I measured the 46 PRs merged after a green main started releasing itself. Merge to live takes about 12 minutes at the median, which is fine. The surprise was before the merge. Green PRs waiting to be merged made up about 78% of all the time those PRs spent open. The total would never have shown that.

So the measuring job became a bot. Perfy owns lead time. It keeps the stage breakdown current and agrees speed targets with Chief, so someone looks after the number every day rather than when I happen to check.

#### 11. Every speed target comes paired with a quality limit

A faster pipeline only counts if it isn't breaking more. A speed target holds only while the flake rate, deploy failure rate and change failure rate stay the same or improve.

Flaky failures are rare, about 0.1% of job runs. Deploy failures are not. About 14% of deploys since releases became automatic failed, mostly at the new checks that run after the install. Roughly one merged PR in six was a fix or revert of something merged the day before. That last figure is rough, because a follow-up isn't always a fix for a failure.

Perfy checks these limits every weekday alongside the speed numbers. The rules that keep quality up don't bend to meet a target. CI is still the reviewer, and anything a bot checks by hand still becomes a coded check.

#### 12. Check the critical path before you count a win

A step is only worth speeding up if it's on the critical path. Look at what else has to finish first.

Skipping the duplicate test run on main after a merge looked like an easy win, since the tests had already passed on the PR. Measured, it saves a little over a minute at the median. The tests run alongside packaging and signing, which finish only slightly earlier, so the release still waits.

#### 13. Treat a slowing build as a warning sign

Build time creeps up one reasonable change at a time. Track it, because nobody notices a slow drift.

The median PR CI run went from about 2 minutes on the first day to about 10 by the fourth. Each new check was worth adding, and nobody noticed the total until Perfy measured it. A typical PR now goes round CI three or four times before it merges, so the extra minutes add up.

### Where the human sits

#### 14. Talk to one bot and keep the chatter out of your chat

Put a layer between you and the engineering bots, so you see decisions rather than build logs.

At first I asked my assistant to start coding jobs directly, and my chat filled with build logs and PR links. Forge took that noise away. Later I copied poteto's setup one step further. She mostly talks to her chief of staff, who talks to her engineering lead, so I set up Chief. The bots now argue among themselves in a group chat, and I hear about it when something needs me.

#### 15. Once the machine is fast, the queue and the human are the bottleneck

When merge to live takes about 12 minutes, the slow part moves to the merge queue and to anything waiting for a person. Keep the list of things that need a yes short.

The bots have a standing yes for routine PRs, merges, releases and deploys. A short list still needs me: force-pushes, tags and branches, repo settings, secrets and keys, server access keys, and anything touching identity or login.

That list is where the time goes now. The PR that changed how the dashboard gets its login token touched login, so it waited for me, and it took about 24 hours from open to merge, the longest of the lot. The proxy fix above waited for my decision in the morning. The rest of the slow tail is the queue. PRs merge one at a time, and a long PR keeps having to merge main back in while others go first. Three PRs took between 12 and 15 hours.

Risky PRs wait longest. The slowest tenth of them sat green and unmerged for more than nine hours, and several went green in the afternoon but didn't merge until the early hours. Meanwhile, 15 PRs merged overnight with nobody awake. The automated steps keep up. The waits are in the queue and with me.

## Kiln as the case study

Kiln is a small runtime for Firecracker microVMs. You ask it for a "box", it boots one, and you get SSH, a dashboard and a sign-in. It runs on one bare-metal server, and you can read the code on [GitHub](https://github.com/Jabbslad/kiln).

From the first PR at 12:58 on 19 October, over three days:

- 137 PRs merged, out of 149 opened.
- 61 releases went out.
- Merge to live takes about 12 minutes at the median, since a green push to main started releasing and deploying itself.
- 15 PRs merged between midnight and 8am on 22 October, with nobody watching.
- Open-to-merge time fell to a median of 13 minutes once CI became the reviewer, then rose to 50 minutes as the queue and my yeses became the bottleneck.

![PRs opened and merged per hour on kiln, with release times marked](/images/grok-bot-agents-prs/prs-per-hour.png)

![Where the time goes from PR opened to live, by stage](/images/grok-bot-agents-prs/time-by-stage.png)

![Median and P90 open-to-merge time by phase](/images/grok-bot-agents-prs/open-to-merge-by-phase.png)

## What it means for engineering leaders

If you run a platform team or an engineering organisation, I think a few things follow.

Your delivery system now sets your lead time. When agents write the code, almost all of the time from idea to production goes on review, merging and deploying. On kiln, writing the code was never the slow part.

Review capacity won't scale with agent output, so move review into code. Each check a person or bot does by hand belongs in CI, and each incident should leave a guard behind. Spend human review on the environment the agents work in, as poteto says, not on each diff.

Staff the factory with roles that can change. On kiln, a role that only made sense for a day and a half came and went, and a new one appeared when lead time needed an owner. Expect your set of bots to change month to month.

Measure the factory by stage, and pair every speed target with a quality limit. Without the second, a faster pipeline can become a less reliable one and nobody notices.

Your own job moves off the line. You set the targets, the quality limits and the short list of things that need a yes. Keep that list short, because every item on it waits for you.

## What's next

- A slow lane for risky PRs, so routine work doesn't queue behind them. It's open now. CI already skips jobs a change can't affect.
- A daily SLO check on lead time and the quality limits, so a slip in either shows up within a day.
- Roll back on any failed check, not only a failed install.
- SSH from a laptop. The public front door passes the SSH check from outside, and the dashboard keeps the commands hidden until a real `kiln ssh` from a laptop works end to end.
- Run the deploy's final checks on a throwaway stand-in server in CI, so a bad check fails there and not on the real one.
- Keep moving checks into code. Every time I catch myself asking a bot "did you test X?", that's a missing CI job.

Thanks to poteto for writing so openly about how she works with agents. Much of this factory started as one of her posts.
