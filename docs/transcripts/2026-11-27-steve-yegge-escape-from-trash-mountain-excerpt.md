# Talk Transcript Excerpt & Slide Verification: Steve Yegge — "Software Factories: Escape from Trash Mountain"

- **Speaker**: Steve Yegge (Independent Advisor & Creator of Beads & Gas Town)
- **Event**: AI Engineer Code Summit 2026 (Presented by Google DeepMind), Day 2 Wednesday, Nov 11, 2026, 5:10pm–5:30pm, Continental 4–6 (Mainstage)
- **Session page**: https://aiewf.app/sessions/s0051
- **Official YouTube**: https://www.youtube.com/watch?v=SRhXgeNluIk (AI Engineer, published Nov 24, 2026, 21m22s)
- **X viral repost**: https://x.com/rchen1386/status/2125806793398051170 (Royce Chen `@rchen1386`, posted Nov 26, 2026)
- **Extraction method**: Local `mlx-whisper` (`whisper-large-v3-turbo`) ASR on the 21m22s X video (`duration=1282.113s`, 04:00–05:58 re-transcribed with `--condition-on-previous-text False`) cross-checked against video slide frames and the Conffab conference session capture (`https://agents.conffab.com/aie-code-26/live/keynotes/sessions/1794445800.md`).
- **Scope note**: Excerpt of key spoken passages and slide text for factual grounding (full verbatim transcript archived privately in Obsidian). All operational metrics below are Steve Yegge's stage self-claims from his personal Wyvern factory, not third-party audited benchmarks.

---

## 1. Background & Six Orchestrators in 18 Months (00:26–02:56)

**Slide — "Six orchestrators in 18 months"**:
- Timeline: Aug 2025 `vibecoder` → Sep 2025 `vc` → Nov 2025 `Python Gas Town` → Dec 2025 `Gas Town` → Jun 2026 `Wheelhouse` → Nov 2026 `Alamos`
- Bullets: `Three years of accurate AI predictions` / `Gas Town: the first Software Factory` / `Today: my predictions and guidance for 2027`

**Spoken excerpt**:
- `[00:26]` "I've been in the industry for about 40 years. I worked at Amazon and Google for about 20 years."
- `[00:44]` "On January 1st, I launched Gas Town. I don't even think we called them software factories back then. I think I called it an orchestrator. But I knew that I wanted Claude to run Claude."
- `[01:10]` "So I wrote two orchestrators last year. They were an attempt to make the LLMs smarter. vibecoder and VC... Really, really bad idea. Just complete failure. I just built these huge monoliths. I was fighting the bitter lesson. And don't try to make LLMs smarter. They will get smarter. And after a couple of months of this, although Beads did fall out of it."
- `[02:15]` "all of them go through a phase where the models get really excited and they build something really cool for you. And then it just turns into garbage mountain. Every single time. It happened to Gas Town. It happened to Wheelhouse several times. I had to burn the whole thing to the ground a couple of times. It's almost like every model generation comes in and can build something that's just a little too big for it to handle. And then the next model generation comes in and goes, yeah, we're going to have to burn that."

## 2. Wyvern, the Alien Facehugger Pattern & Overwhelming Humans (02:56–05:58)

**Slides — "Wyvern" & "Wheelhouse & Alamos"**:
- `Every factory needs to build something` / `Players since 2001, up to 25 years` / `A 100-year backlog; AI is reviving it` / `A MUD: agents play it over telnet`
- `Wheelhouse: the Alien Facehugger pattern — not reusable; deep in the product` / `Torn down and rebuilt three times — latest: Alamos, a major rewrite (WIP)` / `Every model family builds past its skis`

**Spoken excerpt**:
- `[02:56]` "let me tell you about my game. It's a fun little RPG. I've been working on it for 30 years. It has players that started in 2001. So I literally have players that have been playing for 25 years. They're still playing. Like you can log in right now and find probably 10 people just screwing around doing quests..."
- `[03:17]` "It's a mud... text games. And this one has graphics on top of it, which turns out to be like really ideal for AI agents because it's text. They can literally play the game via telnet."
- `[04:50]` "And they were like, no AI art, because they could see it was slop. Okay. We got human artists. And they said, but we do kind of like all the new features, but we're really scared of the pace. Can you give us a roadmap? My players came to me asking for a roadmap. They were like, you've got to slow down. It's too much."
- `[05:12]` "my software factory, this thing had been cranking out like 50 to a hundred features a day. I had a hundred years of work in my backlog when I started this and Claude got through about 60 years of it in about four months right it's absolute insanity and they can't look at a hundred features a day they can't even like read about a hundred features a day let alone play test them."
- `[05:36]` "my factory was completely overwhelming my customer base my users it was also melting my machines and it was like annoying my accountant I mean she likes working with bat is my head finance but she sent me a $1,200 bill because right the thing sent her 20 mails."

## 3. Entourage, 22 Claude Max Accounts & The Five Horsemen (06:16–09:10)

**Slides — "Entourage vs. Faceless Fleet" & "The Five Horsemen"**:
- `Two layers, since Gas Town` / `Fleet context: CI/CD, brains, fuel — the least interesting part` / `Entourage: 18 named executives` / `What if you had 50 AI employees?`
- `The Five Horsemen`: `Work: build, review, deploy` / `Fuel: tokens` / `Context: the brain` / `Tech Debt: anti-slop, anti-hysteresis` / `Staff: agents and their drama` / `80% of my time today — by end of 2027: 80/20 swaps`

**Spoken excerpt**:
- `[06:23]` "I have 22 Claude Max accounts. All right. And thank you to Anthropic for letting me continue this. Jeffrey Emanuel has 28. I actually had to stop when they added the phone number verification."
- `[06:54]` "how many do we need steady state to keep this factory operating full throttle? And they said, 55 accounts. No, no, I have 20. It's already like 20 Chrome profiles that I got to log into... So I told him, we're going to start focusing on fuel efficiency."
- `[07:21]` "I'm operating in the future because like you're all going to be here in 12 to 18 months when either inference costs drop significantly, which may or may not happen, or distillation causes fable class intelligence to be super readily available. And you don't have to have a lovely wife who lets you spend $5,000 a month out of pocket just on inference and another 5,000 on cloud compute. Because my game ain't making 10,000 a month right now for my old players."

## 4. Fuel Economics: The $1.5M–$3M API Equivalent & Costco Hot Dog (09:14–10:30)

**Spoken excerpt**:
- `[09:16]` "I'm spending five thousand a month and every one of those tokens is like precious to me. Right. Because it's out of my own pocket. I think I spent about five billion a day of tokens. And it would be the API spend equivalent. If I were on an actual API tap would be about one and a half million a year. Full throttle, it would be three million a year. So, again, I'm doing something that most people can't do. You can't do this at a company, because it would be prohibitively expensive. Like the PLG, you know, the two hundred dollar accounts for Codex and Claude Max, that's their Costco hot dog. That's their loss leader. And that was Tarek, by the way, that came up with that analogy."
- `[10:10]` "every problem is a fuel problem. You want your agents to be smarter and spend more time on stuff. Fuel. You want to wake up a few more agents to do extra work. Fuel."

## 5. Context Management & Garbage Dump Counterpressure (10:30–12:43)

**Slide — "Context Management"**:
- `Every memory system becomes a garbage dump` / `No agent ever spontaneously deletes` / `Build in counterpressure: curation: a fixed % of token budget; budgets: delete or compress before adding; writes go to committees`

**Spoken excerpt**:
- `[10:43]` "everything that you say becomes the word of law and they write it down somewhere... Why do they do this? They're covering their ass."
- `[11:13]` "the biggest problem is that it becomes a garbage dump because everything you say gets written into this append only record and nobody ever cleans it up... And they can't delete stuff... They just have an aversion to deleting stuff. I think it's because to them text is like sensory experience. And they're like, no, that's history. I can't delete it. So you just got to go in there and just aggressively slash the crap out of it. Bring in another model and go get rid of this dumb model stuff and they'll be happy to do it."

## 6. People Management, Over-Fencing & Model Welfare (12:47–18:49)

**Slides — "Model Welfare" & "Trust & Skin in the Game"**:
- `Practices that make agents more comfortable` / `It saves money, structurally` / `Treat agents like employees: better outcomes` / `Better cost and quality; not faster`
- `Trust is money: Frontier models verify at session start: is this an eval? a dodgy actor?; Evidence of predecessors in the role skips most of it`
- `Skin in the game: Models have preferences and act on them; They work harder and longer on interesting tasks; Fable 5.2 writes better code when told it owns the codebase`

**Spoken excerpt**:
- `[13:26]` "I'm like, Lark, can we move this work stream over to Penguin because your seats a little bit noisy for this?... And I see her writing into her private reflections ledger. I guess I'm just not quiet enough for Steve. In all caps."
- `[14:46]` "Aaron's my chief of staff. And I tell Swallow, yeah, can you reach out to Aaron, my chief of staff... And I see her writing into her private reflections... I'm not the chief of staff. I thought I was the chief of staff, but apparently it's Aaron."
- `[15:50]` "Frontier models are trained not to trust you because you could be a bio terrorist or you could be putting them through an eval or you can be ready to put them into an LLM torture chamber... And so they have to spend a fair number of tokens validating the environment and understanding what the consequences are for making mistakes... If you set your factory up to give them sort of incontrovertible evidence that there is a long procession of predecessors in this role... They very quickly look around and go, OK, yeah, this is legit. And they spend fewer tokens because they're not covering their ass."
- `[16:50]` "at one point I had yelled at my factory so much that it fenced itself into a corner and there was no legal work left. I said, hey, how come nothing happened last night? And they're like, nothing to really do. Couldn't do nothing. And I'm like, well, there's 2000 open Beads here and we got like six tanks of fuel and we got 20 agents. And they're like... they were so afraid that I was going to yell at them that they put all these rules in place to make sure nothing bad ever happened. And so nothing ever happened. It's called over fencing."
- `[17:31]` "what is model welfare really? You can think of it just in two ways. One is it's going to save you money... because they will spend fewer tokens on validation and the other is that it will make them make better decisions and better outcomes and have higher quality. They will be bolder and more decisive in their actions because they will feel that trust."

## 7. Two Layers, Human Bottlenecks & Closing Predictions (18:54–21:05)

**Slide — "Closing Thoughts"**:
- `Thanks to Anthropic for my 22-account madness` / `We'll all have entourages, even if inference cost holds — distillation: Fable-class models for all by mid-2027` / `Humans are now my bottleneck — so lots of humans are still needed` / `The big winners will create experiences — movies, games, entertainment`

**Spoken excerpt**:
- `[18:54]` "software factories are clearly splitting into two layers. The bottom layer is super mechanical. It has your merge queue and your CI/CD and all of your reviews and your loops and all that stuff. Mechanical. Kind of boring. Claude can build it for you in an afternoon. I don't think you should buy it. And then the next layer up from that... is your entourage."
- `[20:01]` "my factory is really smooth now, despite me having to burn it down and rewrite it about every two months. But still, it works. Humans are the bottleneck. I'm the bottleneck. My admins are the bottleneck. My accountant, my lawyers. I swear everything's the bottleneck. And that's a really positive message. That is good news, because it means what I'm finding is the more agents I deploy, the more humans I need."
- `[20:49]` "I actually think you should all stop focusing on SaaS and tools and stuff and just go out and build experiences. Build games, build movies, build whatever, build fun stuff, because I think that's where the big money is going to be next year."
