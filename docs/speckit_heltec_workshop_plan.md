# SpecKit Workshop / Presentation Project Plan

## 1. Goal

Create a practical beginner-friendly introduction to **GitHub Spec Kit** and **Spec-Driven Development**, showing how it is used together with **Claude Code** or **Codex**.

The workshop should be understandable to people who are new to Spec Kit and may also be relatively new to AI-assisted software development.

The core message is:

> AI can write code very quickly, but the harder problem is defining clearly what should be built. Spec Kit provides a structured path from an idea to an implementation.

The presentation should be in **Hebrew**, while technical terms, commands, filenames, and product names may remain in English.

Target length: **30 minutes or more**, with enough flexibility for discussion and a hardware demonstration.

---

## 2. Final Deliverables

The project should produce four coordinated deliverables.

### 2.1 Presentation

Create a Hebrew presentation in **Google Slides**.

The presentation should include:

- Clear visual storytelling.
- Screenshots from the real workflow.
- Images of the Heltec WiFi Kit V3.
- Architecture and workflow diagrams.
- Comparison tables.
- Links to the GitHub repository.
- Links to Spec Kit and relevant tools.
- Selected code snippets.
- QR code or short link to the companion repository if useful.

The presentation should be designed for a live talk, not as a detailed textbook.

---

### 2.2 Companion GitHub Repository

Create a public or shareable GitHub repository that contains the full workshop example and learning materials.

Suggested repository name:

```text
speckit-heltec-demo
```

Suggested structure:

```text
speckit-heltec-demo/
│
├── README.md
├── LICENSE
├── CONTRIBUTING.md
│
├── docs/
│   ├── textbook.md
│   ├── setup.md
│   ├── vscode.md
│   ├── jetbrains.md
│   ├── claude-code.md
│   ├── codex.md
│   ├── troubleshooting.md
│   └── images/
│
├── presentation/
│   ├── presentation-outline.md
│   ├── slide-links.md
│   └── assets/
│
├── firmware/
│   ├── src/
│   ├── include/
│   ├── test/
│   ├── platformio.ini
│   └── README.md
│
├── specs/
│   └── 001-heltec-monitor/
│       ├── spec.md
│       ├── plan.md
│       ├── tasks.md
│       ├── research.md
│       └── contracts/
│
├── .specify/
│
└── examples/
    ├── prompt-only/
    └── speckit-driven/
```

The actual `.specify/` and `specs/` structure should follow the version of Spec Kit used during implementation.

---

### 2.3 Markdown Textbook

Create a standalone learning guide in Markdown:

```text
docs/textbook.md
```

It should be detailed enough that a reader who did not attend the presentation can still follow the full process.

Suggested chapters:

1. Introduction to AI-Assisted Development
2. The Problem With Prompt-to-Code
3. What Is Spec-Driven Development?
4. What Is GitHub Spec Kit?
5. Installing Spec Kit
6. Development Environment
7. Using Spec Kit With Claude Code
8. Using Spec Kit With Codex
9. Constitution
10. Specify
11. Clarify
12. Plan
13. Tasks
14. Analyze
15. Implement
16. The Heltec WiFi Kit V3 Example
17. Full Walkthrough
18. Prompt-Only vs Spec-Driven Comparison
19. Common Mistakes
20. When Not to Use Spec Kit
21. Best Practices
22. Next Steps

The textbook should include:

- Commands.
- Screenshots.
- Short code snippets.
- Expected outputs.
- Explanations of generated artifacts.
- Links to the relevant files in the repository.
- Troubleshooting notes.
- Notes on Claude Code and Codex differences where relevant.

---

### 2.4 Working Hardware Example

Build a real example using:

**Heltec WiFi Kit V3**

The example should be deliberately simple from an electronics perspective but rich enough to demonstrate why a specification matters.

Recommended example:

## Heltec Environmental / Temperature Monitor

Core behavior:

- Read a sensor value.
- Display the current value on the onboard OLED.
- Display current system state.
- Send useful diagnostic information to Serial.
- Trigger a warning above a defined threshold.
- Clear the warning only below a lower threshold.
- Handle a sensor read failure safely and visibly.

Example hysteresis requirement:

```text
Warning ON:  temperature > 30°C
Warning OFF: temperature < 28°C
```

This requirement is useful pedagogically because it demonstrates that the difficult question is often not how to write the code, but how to define correct behavior.

The final code should compile and run on the physical Heltec WiFi Kit V3.

---

# 3. Presentation Story

The presentation should follow a story rather than simply explaining Spec Kit commands.

## 3.1 Opening — The Problem

Approximate time: **3–4 minutes**

Start with a simple prompt:

```text
Build an application for a Heltec WiFi Kit V3 that reads a sensor,
shows the value on the display, and shows a warning when the value is too high.
```

Ask:

**Is this enough information to build the correct product?**

Show some of the immediate unanswered questions:

- Which sensor?
- Which pin or interface?
- How often should it be sampled?
- What exactly is "too high"?
- What happens at exactly the threshold?
- When does the warning turn off?
- What happens if the sensor fails?
- What does the display show during an error?
- Should the last valid reading remain visible?
- What is logged to Serial?
- How will the behavior be tested?

Main message:

> The problem is not that Claude or Codex cannot write C++.
> The problem is that we have not yet defined the product.

---

## 3.2 Spec-Driven Development

Approximate time: **3–4 minutes**

Show:

```text
Idea
  ↓
Specification
  ↓
Clarification
  ↓
Technical Plan
  ↓
Tasks
  ↓
Implementation
  ↓
Validation
```

Explain that Spec-Driven Development moves important decisions before implementation.

---

## 3.3 What Is Spec Kit?

Approximate time: **4 minutes**

Introduce GitHub Spec Kit as a framework for structured AI-assisted development.

Show the high-level workflow:

```text
constitution
     ↓
specify
     ↓
clarify
     ↓
plan
     ↓
tasks
     ↓
analyze
     ↓
implement
```

Explain each command in one sentence.

Do not spend excessive time on syntax.

The goal is to explain the mental model.

---

## 3.4 Claude Code / Codex / IDE Relationship

Approximate time: **4 minutes**

Explain the separation of responsibilities:

```text
Spec Kit
Workflow + Specifications + Process
                ↓
Claude Code / Codex
Reasoning + Coding + Repository Operations
                ↓
IDE
Editing + Navigation + Debugging + Build + Terminal
                ↓
Repository
Specs + Code + Tests + Documentation
```

Important message:

> Spec Kit is not the coding agent.
> Claude Code or Codex performs the work.
> The IDE is the human workspace in which the repository, code, terminal, debugger, and extensions come together.

---

# 4. Development Environment and IDEs

## 4.1 Primary Recommendation — VS Code

Use **Visual Studio Code** as the primary environment in the workshop.

Reasons:

- Beginner friendly.
- Excellent Git integration.
- Strong terminal integration.
- Good support for PlatformIO.
- Easy to demonstrate Markdown, source code, Spec Kit artifacts, and Git in one interface.
- Works naturally with Claude Code and Codex CLI workflows.

Recommended VS Code setup should cover:

### Core

- Git integration.
- Integrated terminal.
- Markdown preview.
- C/C++ support.
- JSON/YAML support where needed.

### Embedded Development

Use **PlatformIO** if it proves reliable for the selected Heltec WiFi Kit V3 setup.

Recommended extension:

```text
PlatformIO IDE
```

Also consider:

```text
C/C++
GitLens
Markdown All in One
Error Lens
```

Only include plugins that materially improve the workshop. Avoid turning the environment setup into the main topic.

### AI Tools

The workshop should show how to work with:

- Claude Code.
- Codex.

Prefer CLI-driven workflows so the repository remains portable across editors.

If editor-specific Claude or Codex integrations are demonstrated, clearly distinguish them from the core Spec Kit workflow.

---

## 4.2 Secondary Recommendation — JetBrains

Include JetBrains as a secondary option.

The goal is not to teach both environments equally.

Use one slide or textbook section explaining that the workflow is repository-based and can also be used from JetBrains products.

Potential JetBrains environments may include:

- CLion for C/C++ / embedded-oriented development.
- IntelliJ-based products where appropriate.
- Integrated terminal for Claude Code or Codex commands.
- Git tools.
- Markdown support.

The important point is:

> The Spec Kit artifacts live in the repository, so they are not tied to VS Code.

The presentation should demonstrate VS Code, while the textbook should include a short JetBrains setup section.

---

# 5. Comparison Section

Approximate time: **5–6 minutes**

The comparison should have two levels.

## 5.1 Direct Prompting vs Spec Kit

This is the most important comparison.

| Topic | Direct Prompting | Spec Kit |
|---|---|---|
| Requirements | Usually stored in conversation | Stored as repository artifacts |
| Clarifications | Agent may assume | Explicit clarification stage |
| Architecture | Often evolves while coding | Planned before implementation |
| Tasks | Ad hoc | Structured task list |
| Traceability | Low | High |
| Review | Mostly code review | Spec + plan + tasks + code |
| Context transfer | Conversation-dependent | Repository-based |
| Claude/Codex switching | Can lose context | Core project context stays in repo |
| Repeatability | Low to medium | High |

Main message:

> Spec Kit converts important project context from temporary chat history into durable project artifacts.

---

## 5.2 Other Approaches

Briefly mention alternatives.

Suggested comparison:

- Direct prompting.
- GitHub Spec Kit.
- OpenSpec.
- BMAD or similar heavier agent workflows.

Do not turn the workshop into a complete framework survey.

Explain that Spec Kit is attractive because it sits between unstructured prompting and heavyweight multi-agent process frameworks.

---

# 6. Heltec Demo Flow

Approximate time: **8–12 minutes**

The hardware example should be the central demonstration.

## Stage A — Prompt Only

Show the original vague requirement.

Optionally preserve an example implementation generated from the vague prompt.

Purpose:

Show how many implementation decisions the AI must invent.

Store this version under something similar to:

```text
examples/prompt-only/
```

---

## Stage B — Specify

Create the first structured specification.

Example requirements:

```text
The device shall sample temperature once per second.

The current temperature shall be displayed on the OLED.

The system shall enter WARNING state when temperature exceeds 30°C.

The system shall leave WARNING state only when temperature falls below 28°C.

A failed sensor reading shall place the system into SENSOR_ERROR state.

The Serial interface shall output the reading and current state.
```

---

## Stage C — Clarify

Demonstrate questions such as:

```text
What should be displayed during sensor failure?

Should the last valid temperature remain on screen?

What should happen at exactly 30°C?

Should the warning state survive a temporary invalid sensor reading?

How frequently should Serial diagnostics be printed?
```

Use this stage to demonstrate that clarification is not bureaucracy.

It prevents hidden assumptions.

---

## Stage D — Plan

Show a simple architecture.

```text
Sensor
   ↓
Sensor Adapter
   ↓
Application State / Decision Logic
   ↓
 ┌─────────┬─────────┐
 ↓         ↓         ↓
OLED     Serial    Tests
```

Keep architecture intentionally simple.

---

## Stage E — Tasks

Example:

```text
T001 Configure Heltec WiFi Kit V3 project
T002 Implement sensor adapter
T003 Implement application state model
T004 Implement hysteresis logic
T005 Implement OLED rendering
T006 Implement Serial diagnostics
T007 Implement sensor failure behavior
T008 Add automated tests for thresholds
T009 Build firmware
T010 Verify behavior on physical hardware
```

---

## Stage F — Analyze

Show how Spec Kit can help detect mismatches among:

- Requirement.
- Plan.
- Tasks.
- Implementation intent.

Example:

```text
Specification requires hysteresis.
Tasks include only "warning threshold".
```

This is a useful example of a missing implementation obligation.

---

## Stage G — Implement

Use Claude Code or Codex to implement the planned tasks.

Avoid depending on a full live implementation during the presentation.

Prepare the completed result in advance.

---

## Stage H — Physical Demo

Run the application on the actual Heltec WiFi Kit V3.

Show:

```text
Temperature: 26.4 C
Status: OK
```

and later:

```text
Temperature: 31.2 C
Status: WARNING
```

Then demonstrate that the warning remains active until the lower threshold is crossed.

If possible, also demonstrate a simulated sensor failure.

---

# 7. Git History as a Teaching Tool

Prepare meaningful Git commits or tags.

Suggested checkpoints:

```text
01-start
02-prompt-only
03-spec-created
04-spec-clarified
05-plan-created
06-tasks-created
07-analysis-complete
08-implemented
09-hardware-verified
```

This makes the workshop deterministic.

During the talk, it should be possible to jump to any checkpoint without waiting for the AI.

---

# 8. Screenshots and Visual Assets

Capture real screenshots during preparation.

Required screenshots should include:

- Spec Kit website.
- Spec Kit GitHub project.
- Spec Kit installation.
- Repository initialization.
- VS Code project view.
- Claude Code using the repository.
- Codex using the same repository.
- `spec.md`.
- Clarification interaction.
- `plan.md`.
- `tasks.md`.
- Analyze result.
- Implementation.
- PlatformIO build.
- Serial output.
- Heltec OLED output.
- Git history/checkpoints.

Also create clean diagrams for:

### Prompt-driven workflow

```text
Prompt → AI → Code → Fix → Prompt → Fix
```

### Spec-driven workflow

```text
Idea → Spec → Clarify → Plan → Tasks → AI Agent → Code → Validate
```

### Tool relationship

```text
Spec Kit → Claude/Codex → IDE/Toolchain → Code/Hardware
```

---

# 9. Presentation Links

The Google Slides presentation should contain clickable links to:

- Spec Kit official website.
- Spec Kit GitHub repository.
- Workshop companion repository.
- Claude Code documentation.
- Codex documentation.
- VS Code.
- PlatformIO.
- Heltec WiFi Kit V3 documentation where relevant.

The companion repository README should link back to the presentation.

This creates two-way navigation:

```text
Presentation ↔ GitHub Repository ↔ Textbook
```

---

# 10. Suggested Presentation Timing

With the larger time allowance, target approximately **35 minutes**, while keeping a shorter 30-minute path available.

| Time | Topic |
|---:|---|
| 0–4 min | Prompt-to-code problem |
| 4–8 min | Spec-Driven Development |
| 8–12 min | What Spec Kit is |
| 12–16 min | Claude Code / Codex / IDE relationship |
| 16–21 min | Comparison |
| 21–31 min | Heltec + Spec Kit walkthrough |
| 31–34 min | Physical hardware demo |
| 34–35 min | Key takeaways |

If more time is available, discussion can happen naturally during the Heltec walkthrough.

---

# 11. Key Takeaways

The audience should leave with these ideas:

### 1.

**AI coding speed does not remove the need for clear requirements.**

### 2.

**Spec Kit provides a repeatable path from an idea to implementation.**

### 3.

**Claude Code and Codex are the agents; Spec Kit is the process and project structure.**

### 4.

**The specification, plan, and tasks live in the repository rather than disappearing inside a chat history.**

### 5.

**The best demonstration of Spec Kit is not that it generates code. It is that it forces important questions to be answered before the wrong code is written.**

---

# 12. Claude Code Handoff

The following instruction can be given directly to Claude Code to complete the project.

---

## Handoff Prompt for Claude Code

You are responsible for completing a full beginner-friendly educational project about GitHub Spec Kit and its use with Claude Code and Codex.

The target audience is new to Spec Kit and may also be new to structured AI-assisted development.

The project must use a real **Heltec WiFi Kit V3** hardware example.

The presentation language is **Hebrew**. Technical terms, filenames, commands, tool names, and code should remain in English where appropriate.

### Deliverables

Produce and maintain:

1. A companion GitHub repository.
2. A working Heltec WiFi Kit V3 firmware example.
3. A complete Spec Kit workflow for that example.
4. A Markdown textbook under `docs/textbook.md`.
5. Supporting setup documentation.
6. Screenshots and diagrams required for a Google Slides presentation.
7. A detailed slide-by-slide presentation outline in Hebrew.
8. A link/reference document for all presentation sources.
9. A set of deterministic Git checkpoints for use during the live presentation.

### Repository

Use a clean structure similar to:

```text
speckit-heltec-demo/
├── README.md
├── docs/
├── presentation/
├── firmware/
├── specs/
├── .specify/
└── examples/
```

Follow the actual current Spec Kit structure rather than forcing this structure when Spec Kit generates something different.

### Example

Implement a simple environmental/temperature monitoring application for Heltec WiFi Kit V3.

The final behavior must include:

- Sensor sampling.
- OLED display.
- Serial diagnostic output.
- Normal state.
- Warning state.
- Hysteresis.
- Sensor failure handling.
- Testable application logic.

Initial teaching prompt should intentionally be vague:

```text
Build an application for a Heltec WiFi Kit V3 that reads a sensor,
shows the value on the display, and shows a warning when the value is too high.
```

The Spec Kit process should expose the missing decisions.

A representative final rule is:

```text
Warning ON:  temperature > 30°C
Warning OFF: temperature < 28°C
```

### Spec Kit Workflow

Demonstrate and retain the artifacts produced by:

```text
constitution
specify
clarify
plan
tasks
analyze
implement
```

Do not treat these commands as the educational goal.

The educational goal is to demonstrate how the process reduces hidden assumptions.

### AI Agents

Document how the same repository can be used with:

- Claude Code.
- Codex.

Clearly distinguish:

```text
Spec Kit = workflow / project artifacts
Claude Code or Codex = coding agent
IDE = human development environment
```

### IDE

Use **VS Code** as the primary workshop environment.

Document a recommended minimal extension setup, including PlatformIO if it is the selected build system.

Also provide a shorter JetBrains section, with **CLion / JetBrains** as the secondary IDE path.

Keep the core workflow repository-based and editor-independent.

### Embedded Toolchain

Prefer PlatformIO if it supports the selected Heltec WiFi Kit V3 firmware setup reliably.

Do not select a sensor library, board framework, pin assignment, or hardware dependency purely from assumption.

Verify all hardware-specific details against current authoritative documentation before finalizing the code.

### Teaching Comparison

Prepare a direct comparison between:

1. Prompt-only AI development.
2. Spec Kit-driven development.

Also include a short contextual comparison with alternatives such as OpenSpec and BMAD, but do not let the framework comparison dominate the workshop.

### Git Checkpoints

Create meaningful commits or tags equivalent to:

```text
01-start
02-prompt-only
03-spec-created
04-spec-clarified
05-plan-created
06-tasks-created
07-analysis-complete
08-implemented
09-hardware-verified
```

The presentation must never depend on a long AI operation completing live.

Every important stage must already exist as a deterministic repository checkpoint.

### Markdown Textbook

Write `docs/textbook.md` as a standalone learning resource.

It should explain:

- Prompt-to-code limitations.
- Spec-Driven Development.
- GitHub Spec Kit.
- Installation.
- VS Code setup.
- JetBrains alternative.
- Claude Code workflow.
- Codex workflow.
- Constitution.
- Specify.
- Clarify.
- Plan.
- Tasks.
- Analyze.
- Implement.
- Full Heltec example.
- Comparison.
- Mistakes.
- Troubleshooting.
- Best practices.
- When not to use Spec Kit.

### Presentation Preparation

The final presentation itself will be created in **Google Slides**.

Prepare:

- `presentation/presentation-outline.md`
- `presentation/slide-links.md`
- reusable images/screenshots
- diagrams
- Hebrew slide copy
- speaker notes where useful

The presentation should target approximately 30–35 minutes.

Keep slides visual and concise.

Do not copy the textbook onto slides.

### Quality Standard

The repository must be usable after the presentation by someone who was not in the room.

A new user should be able to:

1. Clone it.
2. Understand the goal.
3. Read the Spec Kit artifacts.
4. Build the firmware.
5. Follow the Claude Code or Codex workflow.
6. Understand why the structured approach differs from direct prompting.

### Collaboration With ChatGPT

You may consult ChatGPT during the project for:

- Reviewing the teaching structure.
- Challenging product/specification decisions.
- Reviewing generated Spec Kit artifacts.
- Architecture review.
- Comparison framing.
- Hebrew presentation wording.
- Textbook editing.
- Slide content review.
- UX/readability review.
- Final consistency review.

When consulting ChatGPT, provide the relevant current repository files or diffs so the review is grounded in the actual project state.

Do not blindly accept suggestions from any AI agent. Treat disagreements as engineering/product decisions and resolve them against the stated educational goal and verified technical constraints.

### Final Validation

Before declaring the project complete, verify:

- Firmware builds cleanly.
- Hardware-specific assumptions are verified.
- The physical Heltec demo works.
- Spec, plan, tasks, and implementation agree.
- All presentation links work.
- Screenshots match the final repository state.
- Markdown renders correctly on GitHub.
- Commands in the textbook are reproducible.
- Claude Code instructions are reproducible.
- Codex instructions are reproducible.
- No critical presentation step requires live generation.
- The 30–35 minute presentation can be delivered from the prepared checkpoints.

---

# 13. Recommended Execution Order

Claude Code should complete the work in approximately this order:

```text
1. Verify hardware and toolchain
2. Bootstrap repository
3. Create minimal firmware baseline
4. Initialize Spec Kit
5. Create prompt-only reference
6. Run Spec Kit workflow
7. Implement final version
8. Validate on hardware
9. Create Git checkpoints
10. Write textbook
11. Capture screenshots
12. Prepare diagrams
13. Prepare Hebrew slide outline
14. Assemble Google Slides
15. Cross-check presentation, textbook, repo, and code
```

The hardware and toolchain should be validated early so the educational material is not built around an incorrect technical assumption.

---

# 14. Definition of Done

The project is complete when there is one coherent educational package:

```text
Google Slides Presentation
          ↕
GitHub Companion Repository
          ↕
Markdown Textbook
          ↕
Spec Kit Artifacts
          ↕
Claude Code / Codex Workflow
          ↕
Working Heltec WiFi Kit V3 Firmware
```

All parts must tell the same story and use the same example.

The project should teach **how to think before asking AI to code**, not merely how to invoke Spec Kit commands.
