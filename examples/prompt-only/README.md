# Stage A — Prompt only

[`naive_monitor.ino`](naive_monitor.ino) is what you get from
[the vague prompt](vague_prompt.md) alone, with no clarification and no
Spec Kit workflow. It is left exactly as first produced — not fixed, not
polished — because the bugs it contains are the whole point.

It is intentionally excluded from the PlatformIO build (see
`firmware/platformio.ini`, which never references this folder): it is a
teaching artifact, not something meant to run.

## What the prompt never said, and what got invented instead

| Missing decision | What the code silently assumed |
|---|---|
| Which sensor? | DHT22, arbitrarily |
| Sampling interval? | 1 second, arbitrarily |
| What counts as "too high"? | A hardcoded `30`, with no unit confirmed and no domain reasoning |
| What happens exactly at the threshold? | `>` was picked over `>=` with no discussion |
| When does the warning clear? | As soon as the value drops back under the threshold — no hysteresis |
| Sensor failure behavior? | Prints "Sensor error" on the OLED; Serial still prints `nan`; no defined recovery |
| Board-specific wiring | Uses the *generic* ESP32 I2C pins (21/22) — wrong for this board |
| Display power | Never enables `Vext` (GPIO36), which the Heltec WiFi Kit V3 requires to power the OLED at all |
| Testability | None of the decision logic is separated from `loop()`, so none of it can be unit tested |

## Why this matters

Every row above is a real product decision. The AI did not fail to write
C++ — it wrote confident, plausible-looking C++ for a product that was
never actually defined. Two of these mistakes (missing `Vext`, wrong I2C
pins) would produce a **blank screen** on the real board, and the person
running it would have no way to tell whether that's a hardware fault, a
wiring fault, or a specification gap.

The hysteresis gap is the clearest example: nothing here is "wrong" C++,
but the resulting behavior (the warning flickers on and off right at the
threshold) is very likely not what anyone actually wants, and the prompt
never said so either way.

Continue to [`../../specs/`](../../specs) to see how the Spec Kit workflow
surfaces and resolves every one of these gaps before any of this code is
treated as final, and to [`../speckit-driven/`](../speckit-driven) for the
resulting implementation.
