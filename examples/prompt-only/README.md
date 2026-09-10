# Stage A — Prompt only

[`naive_monitor.ino`](naive_monitor.ino) is what a capable coding agent
reasonably produces from [the vague prompt](vague_prompt.md) alone, with
no clarification and no Spec Kit workflow. It is intentionally excluded
from the PlatformIO build (see `firmware/platformio.ini`, which never
references this folder): it is a teaching artifact, not something meant
to run.

## A note on methodology

An earlier version of this file also used the wrong I2C pins for the
OLED and never enabled `Vext`, presented as "realistic beginner
mistakes." That was misleading: those specific bugs were written in
deliberately, by hand, after the fact, to make the comparison against
the Spec Kit–driven version look more dramatic. That is not what this
example is for. The comparison needs to be something we can say
truthfully — "this is what the agent produced from the vague prompt" —
not something we shaped to make one side win.

**What this example is not claiming**: whether an AI agent gets a
specific board's pin wiring or power-sequencing right on the first try,
without being told to verify it, depends on what happened to be in that
model's training data for this particular board. That's a coin flip this
example has no business making a confident claim about, in either
direction — so `naive_monitor.ino` now uses the correct, verified Heltec
WiFi Kit V3 OLED pins and `Vext` sequencing (see
`specs/001-heltec-monitor/research.md`) rather than asserting a specific
wrong answer.

**What this example does claim**, and what actually can't be resolved by
an agent being more knowledgeable or more careful: the product decisions
below. No amount of hardware expertise tells you which sensor the user
wants, what temperature counts as "too high," or whether the warning
should have hysteresis — those are answers only a human stakeholder can
give, and the vague prompt never asked them.

## Implicit assumptions vs. explicit decisions

This is the real distinction, not "bad code vs. good code":

| What the prompt never said | What the code had to assume, because *something* has to go there |
|---|---|
| Which sensor? | DHT22 — a plausible default for "read a sensor," arbitrary either way |
| Sampling interval? | 1 second — arbitrary |
| What counts as "too high"? | A hardcoded `30`, no unit or domain reasoning confirmed |
| What happens exactly at the threshold? | `>` was picked over `>=`, with no discussion |
| When does the warning clear? | As soon as the value drops back under the threshold — no hysteresis, because hysteresis was never requested |
| Sensor failure behavior? | Prints "Sensor error" on the OLED; Serial still prints `nan`; no defined recovery, no debounce |
| Testability | None of the decision logic is separated from `loop()`, so none of it can be unit tested — nothing asked for that structure either |

Every row here is an **implicit assumption**: the prompt left a real
product decision unaddressed, and the agent filled it with something
reasonable-looking because the code has to do *something*. Compare this
against `specs/001-heltec-monitor/spec.md`'s `## Clarifications` section,
where the same decisions were made **explicitly**, with the reasoning
recorded, by the person who actually owns the answer.

The hysteresis row is the clearest example of the distinction the
workshop wants to make: nothing above is incorrect C++, and the
resulting behavior (the warning flickers right at the threshold) is a
completely legitimate, unforced consequence of the requirement simply
never having been stated — not a mistake, and not something "better
prompting" fixes on its own. It's the kind of gap that only gets closed
by someone deciding the answer, which is exactly what
`/speckit-clarify` exists to force before implementation rather than
after.

Continue to [`../../specs/`](../../specs) to see how the Spec Kit
workflow surfaces and resolves every one of these gaps, and to
[`../speckit-driven/`](../speckit-driven) for the resulting
implementation.
