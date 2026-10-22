+++
title = "137 merged PRs in three days, and why none of that was the slow part"
date = 2026-10-21
updated = 2026-10-22
draft = false
description = "What I learned shipping kiln with Grok Bot and Cursor cloud agents, written up as the principles I now work by: CI does the reviewing, checks test the real path, undoing is cheap, and the last bottleneck is the queue and me."
tags = ["ai", "engineering", "developer-tools", "kiln"]
+++

Over three days, cloud agents opened 149 pull requests on [kiln](https://github.com/Jabbslad/kiln), and 137 of them merged. I didn't write a line of that code, and I didn't review most of it either.

The writing was never the slow part. What was slow, and what kept going wrong, sat between "merged" and "working on the server". I first wrote this post as a timeline. It kept growing, so I've rewritten it around the principles I took away. Each one comes with the moment that taught it to me.

Much of this follows how [poteto](https://x.com/poteto) (Lauren Tan) works with agents. Several of the principles below started as one of her posts, and I've embedded the ones that changed my setup the most.

## The setup

Kiln is a small runtime for Firecracker microVMs. You ask it for a "box", it boots one, and you get SSH, a dashboard and a sign-in. It runs on a single bare-metal server.

I drive it from Grok Bot, a desktop assistant app where I can run several bots side by side. There's a small team of them:

- **Forge** is an engineering lead that never writes code. It turns my asks into Cursor cloud agent jobs. Each agent runs in its own VM, does the work and opens a PR.
- **Kiln Ops** deploys. It's the only bot that holds the deploy key.
- **Chief** is my chief of staff. I talk to Chief, and Chief talks to Forge.
- **Proof** used to review every PR. It doesn't any more, and that's a big part of this story.

## The numbers

Counting from the first PR at 12:58 on 19 October:

- **137 merged PRs** on kiln, out of 149 opened.
- **61 releases** published.
- **About 11 minutes from merge to live.** Since a green push to main started releasing and deploying itself, 37 deploys have gone green, with a median of 11 minutes from merge to finished deploy.
- **15 PRs merged between midnight and 8am** on 22 October, with nobody watching.
- **Open-to-merge time went back up.** It fell to a median of 13 minutes once CI became the reviewer. For PRs opened since the afternoon of 21 October it's 50 minutes, and the slowest tenth took more than eight hours. That's the subject of the last principle.

![PRs opened and merged per hour on kiln, with release times marked](/images/grok-bot-agents-prs/prs-per-hour.png)

## 1. Give agents small, strict rules

**Agents copy whatever is easiest, so the rules have to make the easy thing the right thing. Short rules that apply to every job beat long instructions per task.**

Every brief Forge writes tells the agent to use [pstack](https://github.com/cursor/plugins/tree/main/pstack), poteto's skill pack. Its rules are short: make the smallest diff, fix the root cause, and prove it works. On the first afternoon the agents moved the installer from Python to bash, added a deploy from GitHub Actions, put the CLI behind sign-in and started serving the dashboard API. 27 PRs had merged by about 2:30 the next morning.

## 2. Talk to one bot and keep the chatter out of your chat

**Put a layer between you and the engineering bots, so you see decisions rather than build logs.**

At first I asked Grok Bot to kick off coding jobs directly, and my main chat filled up with build logs and PR links. Forge took that noise off me. Later I copied poteto's setup one step further. She mostly talks to her chief of staff, who talks to her engineering lead, so I set up Chief. Now the bots argue among themselves in a group chat, and I hear about it when something needs me.

## 3. The slow part is the waiting, so automate every handoff

**When a step waits for someone to notice it's their turn, it waits for a long time. Every handoff should start on its own.**

On my busiest day I asked Grok Bot:

> Why so few? Stuff has been happening all day but I'm struggling to understand why it's taken so long for anything to get deployed.

The answer was that each handoff was a bot waiting for another bot. A review was requested, a verdict came back, then someone merged, tagged, released and deployed. A review took about 15 minutes, and every FAIL meant another round trip. One PR sat idle after rework because nobody asked for a new review. That evening, a release that was already built and packaged took about two and a half hours to go from published to working.

![The bot team on 20 October: every handoff waits for another bot's turn](/images/grok-bot-agents-prs/diagram-before.png)

So I took the turns away. The review verdict became a commit status instead of a chat message, which gave the merge a gate a machine can read. Pushing a release tag started the deploy. Then the tag went too: a green push to main now picks the next version number, builds, attests, publishes and deploys in the same run. Nobody has pushed a tag by hand since.

## 4. CI is the reviewer

**A PR merges when every check is green at its current head commit, one PR at a time. No human or bot review step sits in the way.**

poteto's team runs an agentic code review that rates every PR for risk, and the low and medium risk ones merge without a human:

{% tweet(id="2108283057581195413", user="poteto", name="lauren", date="October 8, 2026") %}
we have agentic code review, so every PR gets assessed for risk. low-medium risk ones don't require a review so you just merge it. also bugbot of course

there's many more interesting ideas we have for the agentic forge that we've been discussing cc @jacobgold
{% end %}

The next day she put it more bluntly:

{% tweet(id="2108394806548566459", user="poteto", name="lauren", date="October 9, 2026") %}
anything requiring a human review step is ngmi
{% end %}

A week later she posted what she calls an inverse pyramid of trust. Most of the effort goes into the codebase itself, then static analysis and tests, then prose like rules and skills, and the least into human review:

{% tweet(id="2111133080526495985", user="poteto", name="lauren", date="October 16, 2026") %}
how do you trust your agents' work more? copy this post/link and give it to your @bot or agent!

1. codebase improvements: this is just good software engineering - better architecture, stronger types and invariants, clear boundaries. agents love to copy what exists and take the shortest path, so make the easy thing the right thing. categorically eliminate problems through code and you won't need to think about it again.
2. static analysis: lint rules, tests, CI, verification (eg TLA+). very token efficient ways to catch issues ahead of time.
3. prose: comments, rules, AGENTS.md, skills - anything that can't be enforced and requires agent judgment. use it minimally, but do use /create-verification-skill.
4. human review: the hardest to scale. at the rate agents land code, it's pretty much impossible to thoroughly review every PR, so spend that effort on the highest leverage point, designing an environment where agents do the right thing by default.

this forms an inverse pyramid: you want most of your effort at the top, least at the bottom.
{% end %}

Proof was a review step on every PR, the part of that pyramid she spends least on. So I dropped it. CI does the reviewing now, and a PR that touches workflows, deploys, login or secrets gets a risk flag. Releases are signed with GitHub build attestations, and every signature is checked before a release is published.

![The pipeline now: CI checks gate the merge, and a green push to main releases and deploys](/images/grok-bot-agents-prs/diagram-after.png)

## 5. If a bot checks it by hand, it should be a CI job

**A check that lives in a bot's head runs when the bot gets round to it. In CI it runs on every push. And every incident should leave a guard behind so it can't happen again.**

Proof knew how to drive a change like a user. Kiln Ops knew to run the doctor command and boot a smoke box. Forge knew to ask for a new review after a push. All of that became code. CI now guards attestations, secrets and tool downloads, and refuses a release whose tag doesn't match the version in the code.

Proof's best habit came back as code too. poteto [reviews the videos and screenshots her agents record](https://x.com/poteto/status/2107529532144234937) rather than reading every diff. Any PR that changes the dashboard or the CLI now has to carry before and after screenshots from a script anyone can rerun, or say why it doesn't need them. Other PRs have to update the feature notes the agents read, formatting is checked, and there's one script to run locally before pushing.

The guard habit came from mistakes. Once the deploy ran with an empty SSH key, because GitHub doesn't pass secrets into a reusable workflow unless you ask. The fix came with a CI check that fails any caller that forgets. Across the 165 PR builds since the afternoon of 21 October, 49 went red before anything merged.

## 6. A check that only runs after merge doesn't protect main

**If a test only runs on main, the PR that breaks it will look green.**

When the CI checks moved from Python to Rust, the Windows client job on main failed straight away. A test read a bash script, Git on Windows checked that script out with Windows line endings, and the parser panicked. The PR had been green because that test only ran on pushes to main. Main stayed red for about four hours in the early morning, until a fix landed in the morning and the same tests started running on pull requests. A release tag later failed while stamping the version, so the whole release path now gets a dry run on every pull request too.

## 7. Green has to mean live

**A deploy should check what's actually running, not just that its own steps finished.**

One release shipped a new dashboard, but the deploy never installed it. The server kept serving the old one and the job still went green. Now every deploy installs the dashboard and then fails if the live site serves anything other than the bundle in the release. The same goes for sign-in: after a restart, the deploy proves the login page still answers before it carries on.

## 8. Checks must test the real path

**A check is only as good as the path it takes. Test from the outside, in typed code, and on an upgrade as well as a fresh install.**

I learned this three ways in one day.

*From the outside.* We added SSH through the public front door, and the deploy check passed because it called the door service directly on the server. From a laptop, the request goes through the web proxy in front of it first. The proxy talked HTTP/2 to the door, which can't carry the SSH upgrade request, so every real user got an error. The fix pinned the proxy to HTTP/1.1, and moved the check onto the public address that laptops use. That new check then failed the next deploy, rightly, because the deploy never updated the live proxy config. That took a decision from me and a one-time manual change by Kiln Ops.

*In typed code.* Three deploys in a row failed at a new dashboard metrics check. The first two times, the host CPU value came back empty. The third time, the check script needed `jq`, which isn't installed on the server. The fix was to stop writing checks in shell that assume tools on the host. The check is now a typed Rust self-check built into the server binary, and CI fails if a deploy script calls `jq`.

*On an upgrade.* A change moved the server's operation journal to a new schema version. The installer only accepted the old one, so the next upgrade failed halfway. Fresh installs would have been fine. CI now rehearses an upgrade from an old journal, and checks that the server and installer agree on the version. Elsewhere, the sign-in service had been reporting the same old version for many releases, because the deploy skipped replacing it whenever the bytes matched.

## 9. Every fix brings a new bug, so make undoing cheap

**At this speed, fixes cause their own problems. Keep steps small, roll back on your own, and hide unfinished features behind a one-line switch.**

Too many SSH connections from a deploy tripped the server's limit and one deploy failed. The fix shared one connection for the whole job. That fix had its own bug: cleanup ran after the shared connection had closed. The follow-up landed 47 minutes later, with a test that refuses SSH calls once the connection is gone.

Undoing has to be cheap too. The dashboard now has one typed list of features, each marked available or not yet, with tests that fail if an unfinished feature looks broken. The first time I put SSH commands in the dashboard, they didn't work from a laptop. Reverting took the same 10 minutes from merge to live as shipping the mistake had. The second time, hiding them again was a one-line change that merged 37 minutes after the feature it hid. When the upgrade failed on the journal schema, the installer put the previous version back on its own.

It isn't finished. If a deploy fails at a check after the install, the new version stays in place even though the deploy shows red. That happened during the metrics run above.

## 10. Retry only the failure you understand

**Blanket retries hide real problems. Retry the one flaky thing you've diagnosed, and fail loudly on everything else.**

One release never got published, because the signature checker failed to start up on GitHub's side. The tag existed, but the release didn't. The fix retries that exact error three times with a short backoff. Any other verification failure still fails on the first attempt and prints what went wrong.

## 11. Once the machine is fast, the queue and the human are the bottleneck

**When merge to live takes 11 minutes, the slow part moves to the merge queue and to anything waiting for a person. Decide carefully what really needs a yes.**

![Median and P90 open-to-merge time by phase](/images/grok-bot-agents-prs/open-to-merge-by-phase.png)

The bots have a standing yes for routine PRs, merges, releases and deploys. A short list still needs me: force-pushes, tags and branches, repo settings, secrets and keys, server access keys, and anything touching identity or login.

That list is now where the time goes. The PR that changed how the dashboard gets its login token touched login, so it waited for me. It took about 24 hours from open to merge, the longest of the lot. The proxy fix above waited for my decision in the morning. The rest of the slow tail is the queue. PRs merge one at a time, and a long PR keeps having to merge main back in while others go first. Three of them took between 12 and 15 hours.

Meanwhile 15 PRs merged overnight with nobody awake. The machine is fine. The next step is a slow lane, where risky PRs wait for main to deploy green before they merge, so routine work doesn't queue behind them.

## What's next

- **A slow lane** for risky PRs, and a faster CI that skips jobs a change can't affect. Both are open now.
- **Roll back on any failed check,** not only a failed install.
- **SSH from a laptop.** The public front door now passes the SSH check from outside. The dashboard keeps the commands hidden until a real `kiln ssh` from a laptop works end to end.
- **Run the deploy's final checks on a throwaway stand-in server** in CI, so a bad check fails there and not on the real one.
- **Keep moving checks down the pyramid.** Every time I catch myself asking a bot "did you test X?", that's a missing CI job.

Thanks to poteto for writing so openly about how she works with agents. This setup would look very different without her posts.
