# Spec-Driven Development with AI

Speaker transcript, slide by slide, generated from `presentation/content/deck.yaml` (the same text as the speaker notes). Times are the slide budget and the elapsed time at the end of the slide.

Deck: `presentation/speckit-workshop.pptx`

### 1. Spec-Driven Development with AI

`[0:30] [@0:30]`

Welcome. AI means artificial intelligence, and today is about one idea: when you build software with an AI coding assistant like Claude Code or Codex, write down what you want before it writes the code. That is Spec-Driven Development, or SDD. A spec is simply a written description of what the software should do.

### 2. One prompt, many hidden questions

`[1:00] [@1:30]`

> 💡 **Tip:** List three questions the AI would have to guess, and answer them before prompting.

Analogy: ordering a birthday cake by saying only "make it nice". You get a cake, but every decision you skipped, the baker made for you.

The slide shows the request in short. The real prompt, word for word, was: "Build an application for a Heltec WiFi Kit V3 that reads a sensor, shows the value on the display, and shows a warning when the value is too high." Nothing else. It sounds complete.

Now count the hidden questions. What does "too hot" mean? At the number, or just above it? If the temperature hovers at the edge, does the warning flicker? Which sensor, and what if it stops answering?

The AI will not stop and ask. It answers every one of them anyway, silently, by guessing. This talk is about making those guesses visible.

### 3. From prompt to spec

`[0:00] [@1:30]`

Transition: Why a fast, literal AI needs written intent

### 4. The intent gap: SDLC vs ADLC

`[2:00] [@3:30]`

Analogy: a very fast translator who never asks what you meant. Every word you say is translated perfectly, including the words you got wrong.

Start with the old way. For decades software followed the SDLC, the software development life cycle: requirements, design, code, test, release. People did every step, and slowly. The documents written at the start drifted out of date, but the slowness hid the problem, because a confused developer could walk over and ask.

The new way is sometimes called the ADLC, roughly "agentic development life cycle". It is an emerging term, not an industry standard yet, but it is useful. An agent is an AI that can edit files and run commands on its own. It writes the code in minutes, and it builds from exactly what you typed. Put simply, SDLC optimizes for human coordination; ADLC optimizes for autonomous execution with human oversight.

Both share one unsolved problem: does what got built match what was intended? In the old world, requirement documents went stale before the ink dried. In early AI coding, the answer was "prompt harder". Neither worked reliably.

So here is the intent gap: what you meant and what you typed are not the same thing. Humans used to fill that gap with conversation. The agent fills it with guesses, at high speed. The faster the builder, the faster that gap grows.

The fix sounds almost boring: write the intent down first, in a form both people and the AI can read, and keep it up to date. Everything else today builds on that.

Source: https://vimal-dwarampudi.medium.com/spec-driven-ai-bmad-speckit-gsd-superpowers-2cae4512819a

### 5. Vibe coding vs SDD

`[2:30] [@6:00]`

> 💡 **Tip:** Explore with vibe coding; switch to a spec once the code has to last.

Analogy: a napkin sketch versus an architect's blueprint. Both are drawings. You would never build a house from the napkin, and you would never draw a blueprint just to try out an idea.

Vibe coding is the napkin. The term describes a way of working where you describe what you want, accept whatever the AI produces, run it, and keep prompting until it seems to work. You never really read the code. Your decisions live in a chat history that nobody, including you, will ever reread.

And honestly, that is fine for a lot of things: a throwaway prototype, a script you will run once, checking whether an idea is even possible.

Spec-driven development is the blueprint. You write the intent down first, you review it, and only then do you let the AI generate the code. The decisions live in plain files inside the project, next to the code, where the whole team can read them, review them, and change them.

The difference shows up a month later. With vibe coding, someone asks why the warning triggers at 27 degrees, and the honest answer is: the AI picked it. With a spec, you open a file and the decision is there, with the reason next to it.

So this is not good versus bad. It is a choice, and one question decides it: will this code need to survive? If yes, it deserves a spec.

Point at the picture. On the left, a loop with no exit: prompt, the AI writes code, you accept or reject, and round again. Nothing is written down outside the chat. On the right, a line that goes somewhere: spec, plan, tasks, code, a review against the spec, and only then ship. Every one of the first four steps leaves a file behind.

That is the tip on the slide: explore with vibe coding, and switch to a spec the moment the code has to last.

Source (diagram adapted from): https://vimal-dwarampudi.medium.com/spec-driven-ai-bmad-speckit-gsd-superpowers-2cae4512819a

### 6. SDD: the spec is the source of truth

`[2:00] [@8:00]`

> 💡 **Tip:** Fix the spec first when code and spec disagree, then regenerate the code.

Analogy: a restaurant kitchen cooking from one recipe card. If the dish comes out wrong, you do not just fix the plate; you fix the recipe, so tomorrow's dish is right too.

SDD makes the spec the source of truth. Not the code, and not the chat. The code is something the AI generates from the spec, and can generate again.

The work moves through stages. The constitution comes first: the project's house rules, written once. In our hardware project, one rule is that the decision logic must be testable without the board. Then specify: what should the system do, for whom, and how will we know it works? Then plan: how will we build it? Then tasks: a numbered to-do list. Then implement: the AI writes the code.

Spec Kit, GitHub's free toolkit that we will meet properly on slide 11, adds two checkpoints that matter a lot, drawn on the diagram as gates. Clarify asks you the questions the spec left open, one at a time, and records your answers. Analyze cross-checks the documents against each other before any code exists.

Then the loop. When you learn something while building, a requirement changes or a test reveals a gap, you do not quietly patch the code. You update the spec, and regenerate from there. Think of it as a feedback loop, with the constitution as a rail running underneath every stage.

The constitution is not paperwork. Every later stage is checked against it, so you write the rules once and the AI respects them everywhere.

The tip is the habit that makes all of this work: when the code and the spec disagree, fix the spec first.

Source: https://vimal-dwarampudi.medium.com/spec-driven-ai-bmad-speckit-gsd-superpowers-2cae4512819a

### 7. Context is everything

`[0:00] [@8:00]`

Transition: What the AI sees, and what it forgets

### 8. Context engineering: what the AI sees

`[1:30] [@9:30]`

> 💡 **Tip:** Point the agent at the exact files it needs, not the whole project.

Analogy: packing a small backpack for a day hike. You cannot take the whole house, so what you choose to pack decides how the day goes.

Here is the intuition. The AI does not remember your project the way you do. At any moment it only sees what is on its desk: your instructions, the files it opened, and the conversation so far. That desk has a fixed size. The formal name is the context window, measured in tokens, which are roughly pieces of words.

Everything the AI produces comes from what is on that desk. If an important decision is not on it, the AI does not know the decision exists. If the desk is buried in irrelevant files and old chat, the important thing is still there, just harder to notice.

Context engineering is the skill of choosing what goes on the desk, on purpose: the spec, the plan, the two or three files that actually matter, and nothing else. It is the bigger cousin of prompt engineering. Prompt engineering is about how you phrase one request; context engineering is about everything the AI can see when it answers.

This is also why SDD helps. A short spec and plan are the perfect things to put on the desk: dense, current and relevant.

Rule of thumb: less but relevant beats more but noisy. And the tip: point the agent at the exact files it needs, instead of saying "look at the whole project".

### 9. Context rot: when the AI forgets

`[2:30] [@12:00]`

> 💡 **Tip:** Start a fresh session when the AI forgets earlier decisions, and hand it the spec.

Analogy: a whiteboard in a long meeting. By hour two it is full, the decision from minute five is squeezed into a corner under three other diagrams, and people start contradicting it without noticing.

That is what happens in a long AI session. The context window keeps filling with old messages, failed attempts and files you no longer need. The early decisions are still technically there, but they get buried and quietly ignored.

This has a name: context rot. And it is not just a feeling. In July 2025, researchers at Chroma, Kelly Hong, Anton Troynikov and Jeff Huber, tested 18 AI models and found that performance becomes less reliable as the input gets longer, even on simple tasks. An earlier paper by Nelson Liu and colleagues, "Lost in the Middle", showed that models use information at the start and the end of a long input much better than information in the middle.

So quality drops long before the window is full, and a bigger window does not make the problem go away.

What helps? Keep sessions short and focused. Write decisions into files, not only into the chat. And when the AI starts forgetting what you agreed, do not argue with it: start a fresh session and hand it the spec. A tool called GSD does this automatically for every task; we will meet it on slide 16.

Sources:

https://www.trychroma.com/research/context-rot

https://arxiv.org/abs/2307.03172

### 10. Four tools, two layers

`[0:00] [@12:00]`

Transition: Spec Kit, Superpowers, BMAD and GSD

### 11. Spec Kit: the living spec

`[1:30] [@13:30]`

Analogy: getting a building permit. Each office stamps a different form, and each stamp exists to catch a different kind of mistake before anyone pours concrete.

Spec Kit is GitHub's open-source toolkit for spec-driven development. Spec Kit organizes documents. The documents are the engine: each stage reads the previous document and writes the next one, all as plain Markdown files inside your project.

Walk the row of commands. The dashed ones, clarify and analyze, are optional but worth it. The constitution, set up once per project, catches rules being broken silently. Specify writes the spec, and clarify then asks you the questions it left open, so requirements are decided instead of guessed. Plan and tasks turn the spec into a design and a numbered to-do list, which catches a wrong design or missing steps. Analyze cross-checks all the documents against each other and against the constitution; it catches documents that disagree. Implement writes the code and the tests by following the task list, so the code stays tied to the spec. Everything lands in one folder per feature, specs/ and the feature name, which travels with the branch.

The idea to remember: every stage catches a different kind of mistake, and each one is cheap to fix at that stage and expensive later.

Spec Kit works with several AI coding assistants, including Claude Code and Codex, and its files do not depend on any one of them. Switch assistants mid-project and the spec stays.

This is the tool we used in the case study, so you will see these stages for real in a few minutes.

Source: https://github.com/github/spec-kit · docs: https://github.github.io/spec-kit/

### 12. Spec Kit in a nutshell: one cake order

`[1:30] [@15:00]`

> 💡 **Tip:** Read your spec like a stranger; every question they would ask belongs in clarify.

Analogy: the birthday cake from the start of the talk, but this time ordered properly.

Here is Spec Kit in a nutshell, with one cake. The constitution is the bakery's house rules: no nuts, ever. Every order has to obey it.

Specify writes the order: chocolate, twelve people, "Happy 8th, Noa", Friday at five. What and for whom, not how to bake it.

Clarify asks what the order left open. Any allergies? Yes, one guest is gluten-free. Without that question, the baker guesses.

Plan decides how: two layers, a 20 centimetre tin, gluten-free flour. Tasks turns the plan into steps: bake, make the cream, assemble, write the text.

Analyze reads everything side by side before anyone turns the oven on, and finds a clash: the order says twelve people, but a 20 centimetre tin feeds about eight. Fixing that on paper takes a minute; finding it on Friday ruins the party.

Implement bakes, ticking off each task against the order.

Every step wrote something down. That is the whole idea of Spec Kit.

### 13. Same seven steps, real project

`[1:30] [@16:30]`

> 💡 **Tip:** Learn the steps on a toy example before you use them on real code.

Analogy: the same recipe card, now used for a real dish.

Now the same seven steps on a real project: the Heltec firmware you will see in detail in Part 4. Read each row as cake on the left, firmware on the right.

The constitution: no nuts, ever, becomes "the decision logic must be testable without the board". Specify: twelve people on Friday becomes "read the sensor, show the value, warn when it is too hot". Clarify: the gluten-free guest becomes the exact thresholds, warn above 27 degrees and clear below 25.

Plan: the tin and the layers become a design that keeps the decision logic apart from the hardware code. Tasks: numbered steps, with the tests written first.

Analyze: the tin that was too small becomes two requirements that disagreed, show an error after one failed read or after three. It was caught on paper, before any code.

Implement: the cake is the firmware, built, with eleven of eleven tests passing.

Remember the cake, and you remember Spec Kit.

Source: https://github.com/ronyronen/speckit-claude-presentation/tree/main/specs/001-heltec-monitor

### 14. Superpowers: discipline the AI can't skip

`[1:30] [@18:00]`

> 💡 **Tip:** Ask for a failing test first, then only the code that makes it pass.

Analogy: a pilot's pre-flight checklist. Pilots are not short on skill. They read the checklist out loud on every flight because skipped steps are how accidents happen.

Superpowers, created by Jesse Vincent, starts from a simple insight: the problem with AI coding is not intelligence, it is discipline. It is a library of skills, written procedures, that the agent must follow.

Its README describes a seven-step workflow, and that is the picture. Brainstorming asks you questions before any design. A git worktree gives the work its own isolated branch. The plan splits it into small tasks. A fresh subagent takes each task. Then come TDD, code review, and finishing with a merge or a PR. The strictest part is TDD, test-driven development: first write a test that fails, then write just enough code to make it pass. Superpowers enforces this literally: code written before its test gets deleted.

Then the work passes two reviews: first, does it match the spec? Second, is the code itself good?

On adoption: the repository has over 300,000 GitHub stars as of November 2026 (github.com/obra/superpowers).

Tip: ask for a failing test first, then only the code that makes it pass.

Source: https://github.com/obra/superpowers

### 15. BMAD: an AI agile team

`[1:30] [@19:30]`

> 💡 **Tip:** Borrow only the roles you miss; a small project rarely needs the whole team.

Analogy: a film crew. The director, the camera operator and the editor each have one clear job, and they pass the work along in a known order.

Where Spec Kit organizes documents, BMAD organizes agents. BMAD stands for Breakthrough Method for Agile AI-Driven Development. Its organizing idea is the agile team. Instead of one general-purpose AI assistant, you get several specialized agent roles, such as an analyst, a product manager, an architect, a developer and a tester. Each has a narrow job and its own focused context.

The key feature is the handoff. Each role produces a written document, a brief, a requirements document, an architecture, user stories, and passes it to the next role. That leaves an audit trail of every decision.

Walk the picture left to right: four phases, analysis, planning, solutioning and implementation. In each column, the agents on top write the document underneath, and that document is what the next phase starts from. The amber lane at the bottom is the quick flow: for a bug fix or a small feature you skip the first three phases and go straight to a short spec, a story and a review.

In my reading, BMAD fits bigger projects that need serious planning up front. On a small project the full crew is overkill, which is the tip: borrow only the roles you actually miss.

Source: https://github.com/bmad-code-org/BMAD-METHOD · docs: https://docs.bmad-method.org/

### 16. Four metaphors, two layers

`[2:00] [@21:30]`

Analogy: building a house needs an architect and a site foreman. The architect decides what to build; the foreman keeps the work on track every day. Neither replaces the other.

Here are the four frameworks on one picture, each with its metaphor. Spec Kit is the living document. Superpowers is discipline. BMAD is the team. GSD, short for "Get Sh*t Done", is fresh context: every task gets a new agent with a clean context window, so long projects never rot; there is a backup slide on it if anyone asks.

They sit in two layers. The top layer is planning and governance: what are we building, why, and under which rules? That is Spec Kit and BMAD. The bottom layer is execution discipline: how do we build it reliably, for hours, without the AI drifting or skipping tests? That is Superpowers and GSD.

This is the most useful idea here: these tools are not competitors. Planning tools do not solve context rot; a planning agent can drift in a long session like any other. And none of the planning tools enforce TDD at the moment the code is written.

There is real overlap too. Spec Kit's acceptance checklist is a light quality gate, and BMAD has a tester role, so on smaller projects with careful human review, the planning layer may be enough on its own.

Some practitioners go further and argue that mature teams are converging on all four. That is an opinion. I would rather give you a rule for deciding, and that is the next slide.

Source: https://vimal-dwarampudi.medium.com/spec-driven-ai-bmad-speckit-gsd-superpowers-2cae4512819a

### 17. Decision rule: which layers do you need?

`[2:30] [@24:00]`

> 💡 **Tip:** Start with one planning tool; add a layer only when you feel its pain.

Analogy: choosing a vehicle. You do not buy a truck for a short commute, and you do not move house on a bicycle. The trip decides the vehicle.

Here is a practical decision rule, drawn as two simple tracks. Start with a planning tool, for example Spec Kit, then ask three questions.

First track, the discipline layer, Superpowers. Question one: does your team have a strong TDD habit that survives deadline pressure? If no, add Superpowers and let the tool enforce it. If yes, skip it.

Second track, the context layer, GSD. Question two: are your AI sessions long, hours of work on their own? If yes, add GSD, because you will hit context rot. If no, ask question three: does a human review the output after each phase? If nobody does, add GSD. If you review every phase, skip it; each review is a natural checkpoint.

Let's try the rule on the project you are about to see, the Heltec temperature monitor. Question one: a strong TDD habit? Here the habit was written into the project's constitution: Principle II says every threshold and state change needs a test written before or alongside the code. So the discipline track says: skip Superpowers. Question two: were the sessions long? No; each Spec Kit stage was a short, focused session. Question three: did a human review each phase? Yes; I read and approved every document before the next stage started. So the context track says: skip GSD too. Spec Kit alone, plus a human, was the right size for that job.

One more honest answer: sometimes you need none of this. Adapted from the companion textbook's chapter "When Not to Use Spec Kit" (docs/textbook.md, section 22): skip the spec for throwaway experiments you will delete, for trivial and unambiguous changes like renaming a variable, and when you do not yet know what is technically possible and need to explore first. That is research, not specification.

Spec-driven development earns its cost when getting the requirement wrong is expensive.

Tip: start with one planning tool, and add a layer only when you feel its pain.

Source: https://vimal-dwarampudi.medium.com/spec-driven-ai-bmad-speckit-gsd-superpowers-2cae4512819a

### 18. A real case study

`[0:00] [@24:00]`

Transition: Heltec WiFi Kit V3 firmware, built with Spec Kit

### 19. Heltec board + DHT22: implicit vs explicit

`[1:30] [@25:30]`

Analogy: see slide 2, the cake order. Same request, now with the real answers written down.

Let's watch the theory work on something real. The board is a Heltec WiFi Kit V3: a small ESP32-S3 microcontroller board with a tiny built-in 0.96-inch OLED screen, an organic LED display. It has no temperature sensor of its own, which is the first thing the vague prompt left open. We wired a DHT22, a cheap temperature and humidity sensor, to pin 4, a general-purpose input/output pin.

On the left is everything the one-line prompt said: show the temperature, warn when it is too hot. And nothing at all about failures.

On the right is what the spec says after the Spec Kit stages: read the DHT22 every two seconds, temperature only. Enter WARNING above 27 °C, return to OK only below 25 °C. After three failed reads in a row, show SENSOR ERROR instead of a frozen number.

The firmware also supports a BME280 sensor, chosen at build time, but everything you will see today ran on the DHT22.

### 20. Specify: hysteresis decided, not guessed

`[1:30] [@27:00]`

> 💡 **Tip:** Ask about the edges: exactly at the threshold, sensor missing, first boot.

Analogy: a home thermostat. The heating turns on at 19 degrees and off at 21, not both at 20, otherwise it would click on and off all day.

Writing the code for a warning is trivial; deciding it is the hard part. With a single threshold, a reading hovering at the limit would flip the warning on and off every two seconds.

The specify stage turned "too hot" into an explicit band: one number to switch the warning on, a lower one to switch it off, and in between the state stays as it was. That gap is called hysteresis. On the slide they are FR-003 and FR-004; FR means functional requirement, numbered so tests and tasks can point to it.

Then clarify asked what nobody had thought about: what happens at exactly the threshold? Our answer: strictly. Exactly 27.0 does not trigger; exactly 25.0 does not clear.

The first band was 30 and 28 °C. During hardware bring-up we lowered it so a cupped hand can trigger the warning, and recorded that as a new clarification, not a quiet code edit.

Tip: ask about the edges, exactly at the threshold, sensor missing, first boot.

### 21. Plan + tested logic (11/11)

`[1:30] [@28:30]`

Analogy: a flight simulator. Pilots practise their decisions without a real plane; we test our decision logic without the real board.

The plan's most important choice came straight from the constitution: keep the decision logic, the state machine that picks OK, WARNING or SENSOR ERROR, separate from all hardware code. The sensor, the screen and the serial output are thin adapters around it: small pieces of code whose only job is to talk to the hardware and pass plain numbers in and out, with no decisions of their own.

That separation pays off immediately. The logic has eleven unit tests that run on a laptop with no board attached. They check every rule we just decided: warning strictly above 27, exactly 27 does nothing, clears strictly below 25, no toggling anywhere inside the band, three failures to enter SENSOR ERROR, and recovery afterwards.

The command on the slide, pio, is PlatformIO's command-line tool; "native" means run the tests on this computer instead of the board. Result: 11 out of 11 pass. The output on the slide is shortened; the full run lists all eleven.

Without the plan stage, the easy path is to call the sensor library straight from the logic, and then nothing can be tested without hardware on the desk.

### 22. What /speckit-analyze caught

`[1:30] [@30:00]`

Analogy: a proofreader who reads chapter 2 and chapter 9 side by side, and notices they describe two different endings.

Analyze does not read code. It cross-checks every requirement, success criterion and task against each other, and against the constitution.

In this project it found a real contradiction, marked HIGH. During clarify we had decided that a single glitch should not declare the sensor dead: three failed reads in a row are needed. But an older success criterion in the same file still promised the error would be visible within one reading. Two sentences, one file, two different devices.

We fixed the wording to "within three readings" before any code was written. Analyze also flagged two medium gaps: the "never crash" rule had no automated test, and the hardware-free rule was not checked automatically. We added tasks for both.

None of these is a coding bug. They are disagreements in our own requirements, caught while fixing them cost one sentence.

### 23. Behavior: OK and WARNING on the board

`[2:00] [@32:00]`

> 💡 **Tip:** Photograph real hardware results; reviewers trust a photo faster than a log.

Analogy: see slide 20, the thermostat. These photos show it working.

Pause about 10 seconds on each photo so people can read the screen.

This is the real board with the DHT22 wired up. On the left, normal room temperature: the screen shows OK and 24.0 degrees.

On the right, I warmed the sensor with my hand. Look closely at the number: 26.6 degrees, and the screen still says WARNING. A beginner might call that a bug, because 26.6 is below the 27-degree threshold. It is not a bug; it is the spec. The reading went above 27, the warning switched on, and it stays on until the temperature drops below 25. That is the hysteresis band from three slides ago, visible on real hardware.

This is why the photos matter. The unit tests proved the logic on a laptop; the photos prove the same behavior on the physical device, with the real sensor. We use photos instead of a live demo on purpose: they never fail on stage.

And what did we not need? GSD or Superpowers. The sessions were short and a human reviewed every stage, so the decision rule says skip GSD. And the constitution already required tests first (Principle II), so the Superpowers question also says skip.

Tip: photograph real hardware results; reviewers trust a photo faster than a log.

### 24. Working as a team

`[0:00] [@32:00]`

Transition: Branches, pull requests and shared specs on GitHub

### 25. main vs dev: published vs draft

`[1:30] [@33:30]`

> 💡 **Tip:** Keep main always working: merge into it only after the tests pass.

Analogy: a newspaper. The printed edition is what readers see, and it must always be right. The draft desk is where the messy work happens.

Some vocabulary first. Git is the tool that tracks every version of your files. GitHub is the website where a team shares a Git repository, or repo: the project folder with its full history. A branch is a parallel copy of the project where you can work without disturbing anyone else.

Two branches matter here. main is the published edition: always working, always safe to hand to someone. dev is the draft desk: work lands there first, gets combined, and gets checked.

The team rule: merge into main only after the tests pass and the work is verified. To merge means bringing the changes from one branch into another.

The diagram is this repo's real history, as an illustration: issue #2 is a to-do card asking for DHT22 support, and PR #3 is the change that delivered it; more on both next slide. To be clear, this was a one-person project, early work went straight to main, there is no automated test server, and main is not locked. A real team would add those.

Tip: keep main always working, and merge into it only after the tests pass.

### 26. Issues and pull requests

`[1:30] [@35:00]`

> 💡 **Tip:** Write 'Fixes #2' in the PR into main; GitHub then closes the issue on merge.

Analogy: a work order and a signed delivery note. The work order says what is needed and why; the delivery note shows exactly what was done, and someone signs it before it is accepted.

An issue is the work order: a card on GitHub describing a bug or an enhancement, and why it matters. A pull request, or PR, is the delivery note: a set of changes you propose, which someone reviews before it is merged. Changes land through PRs, never by pushing straight into main.

Follow the real chain on the diagram. Issue number 2 asked for DHT22 support, because the original sensor was not available. The work happened on a feature branch called 001-heltec-monitor-dht22-sensor. PR number 3 merged it into dev. Then PR number 4 carried it from dev into main. PRs 1 and 5 through 7 are other dev-to-main merges.

Here is a small surprise: issue 2 is still open. GitHub only closes an issue automatically when a PR or commit that says "Fixes #2" lands on the default branch, here main. Nobody wrote "Fixes #2". And even if PR 3 had said it, GitHub would have ignored it, because PR 3 targeted dev, not the default branch.

Tip: write "Fixes #2" in the PR that goes into main, and GitHub then closes the issue on merge.

### 27. Shared repo, shared specs/

`[2:00] [@37:00]`

> 💡 **Tip:** Review the spec changes first in every pull request, then the code.

Analogy: a shared lab notebook. Every scientist writes down what they are trying and why, so nobody repeats an experiment or undoes someone else's.

A repo shared by more than one developer has one big risk: people do not know what the others are doing. Two people fix the same bug, or one quietly undoes another's decision.

The specs folder is the answer. Every feature gets its own folder, like specs/001-heltec-monitor in this repo. Inside are the spec, the clarifications with their answers, the plan, the task list and the analysis report. Before you start work, you read the folder. Before you change a decision, you see why it was made.

And the specs travel in the same pull request as the code they describe. The reviewer sees the change in intent and the change in code together, and can ask: does this code do what the spec now says?

Imagine a second developer joining tomorrow. They would open specs/002 for their own feature, on their own branch, and everyone could read it in the PR before a line of code merged.

Each Spec Kit stage of this repo is also tagged in Git and on GitHub, from 01-start to 09-hardware-verified, so you can replay how the spec grew.

Tip: in every pull request, review the spec changes first, then the code.

### 28. What's next

`[0:00] [@37:00]`

Transition: Skills, teams of skills, one constitution

### 29. Skills: recipe cards for the AI

`[1:00] [@38:00]`

> 💡 **Tip:** Turn the instruction you repeat most often into your first skill.

What's next, not day one: once the basics feel normal, these three ideas are where teams go.

Analogy: a recipe card you can hand to any new cook. You write it once, and every cook makes the dish the same way.

A skill is exactly that for an AI agent: a written procedure, saved as a file, that the agent loads only when it needs it. "How we write a spec." "How we review a pull request." "How we release."

You have already met skills today. In this project, Spec Kit's stages are installed as skills for the assistant, and Superpowers is essentially a library of skills.

Write a skill once and you can share it across projects and teammates, so everyone's agent follows the same steps.

Tip: turn the instruction you repeat most often into your first skill.

### 30. Teams of skills: the /team example

`[1:00] [@39:00]`

Analogy: a small band. The drummer, the bassist and the singer each know their part, and the band leader settles the arguments.

Skills can also define roles, and roles can work as a team. This talk is the example. It was planned by three AI roles: an architect who coordinated, a product owner who wrote the brief, and a senior developer who estimated the work and checked the facts. The architect passed messages between them and made the call when they disagreed; I approved every scope decision.

That team caught real problems: an inflated star count in a source, an archived GSD repository, and slides naming the wrong sensor. It also negotiated the cuts that fit this talk into 45 minutes.

This was a custom setup on my machine, not a product you can download, but the pattern is reusable.

### 31. One constitution for many projects

`[1:00] [@40:00]`

> 💡 **Tip:** Keep the constitution short; rules nobody reads are rules nobody follows.

Analogy: the house rules on the fridge. Every flatmate follows the same rules, and a new flatmate reads them on day one.

A constitution is a project's house rules. Our Heltec project has five principles, such as "decision logic is hardware-independent" and "every threshold decision is explicit".

The next step is one constitution shared across projects and teams: testing rules, naming, security, review. In Spec Kit each project keeps its own constitution file, so sharing is a team practice rather than a built-in feature: keep a template, copy it into every new project as the starting point, then add the project's own rules.

Tip: keep the constitution short; rules nobody reads are rules nobody follows.

### 32. Takeaways

`[1:30] [@41:30]`

> 💡 **Tip:** Write a one-page spec before your next AI coding session, starting tomorrow.

Analogy: measure twice, cut once.

Five things to take home. One: write the intent down before the AI writes the code. The spec, not the chat, is the source of truth.

Two: keep the AI's desk tidy. Context rots in long sessions, so keep sessions short and keep decisions in files.

Three: pick your layers by pain. Start with planning; add context isolation or enforced discipline only when you actually feel those problems.

Four, from the case study: on the Heltec project, Spec Kit plus a human reviewing each stage was enough. Specify and clarify pinned down the hysteresis band, analyze caught a contradiction before any code existed, and eleven tests plus two photos proved the behavior.

Five: make it a team sport, with issues, branches, pull requests and a shared specs folder, so everyone can see what everyone else is building and why.

And one thing to do tomorrow, the tip: before your next AI coding session, write a one-page spec. Who is it for, what should it do, and how will you know it works?

### 33. References

`[0:30] [@42:00]`

Everything from today is in this talk's repository: the firmware, the full specs folder and both decks, English and Hebrew. Leave this slide up while people photograph it.

This talk: https://github.com/ronyronen/speckit-claude-presentation

Article: https://vimal-dwarampudi.medium.com/spec-driven-ai-bmad-speckit-gsd-superpowers-2cae4512819a

Spec Kit: https://github.com/github/spec-kit

BMAD: https://github.com/bmad-code-org/BMAD-METHOD

GSD: https://github.com/open-gsd/gsd-core

Superpowers: https://github.com/obra/superpowers

Context rot: https://www.trychroma.com/research/context-rot

Lost in the Middle: https://arxiv.org/abs/2307.03172

Where to go next: the last backup slide has a learning path, and the repo README has the full reading list.

### 34. Questions?

`[3:00] [@45:00]`

Repeat each question before answering it, so the whole room hears it.

Likely questions:

"Isn't this just waterfall again?" No. Waterfall freezes the document; here the spec is living, and the feedback loop updates it whenever you learn something.

"Which tool should I start with?" One planning tool; Spec Kit is the one I used here. Then use the decision rule for the rest.

"Does it work with my assistant?" Spec Kit supports several assistants, and its files do not depend on any one of them.

"How long did the Heltec spec take?" Specify through implement all ran on one day, 2026-09-10, per the tags and commit dates in the repo.

If time runs out, point to the references slide and the repo.

---

## Backup slides (not timed)

### 35. Backup slides

`[backup, not timed]`

backup, not timed. Transition: Details for the questions

### 36. Backup: each stage catches a mistake

`[backup, not timed]`

backup, not timed. Use only if someone asks how each stage pays for itself.

Clarify settled the exact edges of the hysteresis band (strictly above, strictly below). Plan, following the constitution, kept the state machine free of hardware calls, which is what made the 11 laptop tests possible. Analyze found that success criterion SC-004 contradicted requirement FR-005 before any code existed.

### 37. Backup: overlap and gaps

`[backup, not timed]`

backup, not timed. For questions comparing the tools.

The argument: planning frameworks solve "what to build"; GSD and Superpowers solve "how to build it reliably for hours". On small projects with careful human review, the planning layer's light gates may be enough. None of the four replaces a human reviewer, and hardware testing is still on you.

### 38. Backup: GSD, a fresh start for every task

`[backup, not timed]`

> 💡 **Tip:** Write decisions into files, not the chat, so a fresh session can pick them up.

backup, not timed. Use if someone asks about long sessions or GSD (slides 16 and 17 mention it).

Analogy: a relay race. No runner tries to run the whole marathon; each one starts fresh, takes the baton, and runs one leg at full speed.

GSD is short for a blunt phrase, "Get Sh*t Done", and at heart it is a context engineering tool. Its insight is the one from the context rot slide (slide 9): quality drops as the window fills, so never let it fill.

Every task gets a new, clean context: a fresh agent that only sees what that task needs. Independent tasks can run side by side in parallel waves; dependent ones wait. Your main session stays small while the helpers do the heavy lifting. The gsd-core README describes this as a fresh 200,000-token context per task; that number is the project's own claim.

The project's memory lives in files, not in one long chat, and that is what lets each fresh runner pick up the baton.

One practical note: the original repository, gsd-build/get-shit-done, is now archived, and its README points to open-gsd/gsd-core. The original project was published under the name TÂCHES.

Sources:

https://github.com/open-gsd/gsd-core

https://github.com/gsd-build/get-shit-done

### 39. Backup: starting a Spec Kit project

`[backup, not timed]`

backup, not timed. Show only if someone wants to try it tonight. The full setup steps are in the repo README and in docs/textbook.md, chapter 5.

### 40. Backup: how the tools relate

`[backup, not timed]`

backup, not timed. Use with slide 16. Spec Kit is not an AI itself: it sets up templates and commands, and an AI assistant such as Claude Code or Codex runs them. The specs and constitution are plain files, so you can switch assistants mid-project.

### 41. Backup: VS Code extensions

`[backup, not timed]`

> 💡 **Tip:** Keep the spec open in a preview pane while the agent works.

backup, not timed. For the hands-on crowd. The full extension list is in the repo README, section 5.

### 42. Backup: git checkpoints per stage

`[backup, not timed]`

backup, not timed. Tags make each stage easy to replay: 03-spec-created still has open questions, 04-spec-clarified has the answers, 07-analysis-complete shows the contradiction found, 08-implemented has 11/11 tests passing, and 09-hardware-verified is the DHT22 run on the board.

### 43. Backup: where to go next

`[backup, not timed]`

> 💡 **Tip:** Learn one layer at a time: a spec first, tools only when you feel the pain.

backup, not timed. A learning path for after the talk, in order.

1. The textbook in this repo explains everything from today in long form: https://github.com/ronyronen/speckit-claude-presentation/blob/main/docs/textbook.md

2. Replay the case study by checking out the tags one by one, from 01-start to 09-hardware-verified, and read what changed at each stage.

3. Spec Kit docs and quick start: https://github.github.io/spec-kit/ · GitHub's introduction: https://github.blog/ai-and-ml/generative-ai/spec-driven-development-with-ai-get-started-with-a-new-open-source-toolkit/

4. Superpowers: https://github.com/obra/superpowers · installing Claude Code plugins: https://code.claude.com/docs/en/plugins

5. Fundamentals: Anthropic, "Effective context engineering for AI agents": https://www.anthropic.com/engineering/effective-context-engineering-for-ai-agents · Liu et al., "Lost in the Middle": https://arxiv.org/abs/2307.03172 · Chroma, "Context Rot": https://www.trychroma.com/research/context-rot · Martin Fowler's site on SDD tools: https://martinfowler.com/articles/exploring-gen-ai/sdd-3-tools.html · Claude Code best practices: https://www.anthropic.com/engineering/claude-code-best-practices

6. The other layers when you need them: BMAD https://docs.bmad-method.org/ · GSD https://github.com/open-gsd/gsd-core
