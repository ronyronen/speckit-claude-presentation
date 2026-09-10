# Spec Kit + Heltec WiFi Kit V3 Workshop

A beginner-friendly, hands-on workshop (in Hebrew) that teaches **Spec-Driven
Development** with **GitHub Spec Kit**, using **Claude Code** and **Codex** as
coding agents, on a real **Heltec WiFi Kit V3** hardware example.

> The problem is usually not that the AI cannot write the code.
> The problem is that the product behavior was not sufficiently defined.

This repository is the companion material for a live talk. It contains a
working firmware example, the full set of Spec Kit artifacts that produced
it, a standalone Markdown textbook, and everything needed to assemble the
Hebrew slide deck.

## Status

This repository is under active construction, one Spec Kit stage at a time.
Each stage is preserved as a Git tag so the workshop never depends on an AI
step completing live — see [Git checkpoints](#git-checkpoints) below.

## The example

**Heltec WiFi Kit V3** (ESP32-S3) + **BME280** environmental sensor, reading
temperature and driving the onboard 0.96" OLED, with a warning state that
uses **hysteresis** (`ON` above 30°C, `OFF` below 28°C) and explicit sensor
failure handling. See [firmware/README.md](firmware/README.md).

We start from an intentionally vague prompt:

```text
Build an application for a Heltec WiFi Kit V3 that reads a sensor,
shows the value on the display, and shows a warning when the value is too high.
```

...and use the Spec Kit workflow (`constitution → specify → clarify → plan →
tasks → analyze → implement`) to turn it into a fully specified, tested
firmware implementation. Compare [examples/prompt-only](examples/prompt-only)
(what you get from the vague prompt alone) with
[examples/speckit-driven](examples/speckit-driven) (the specified result) and
[specs/](specs) (the artifacts that got us there).

## Repository layout

```text
.
├── README.md
├── docs/                    # textbook, setup guides, images
│   └── textbook.md
├── presentation/            # source material for the Google Slides deck
├── firmware/                # PlatformIO project for Heltec WiFi Kit V3
├── specs/                   # Spec Kit artifacts (spec/plan/tasks/...)
├── .specify/                # Spec Kit project configuration (generated)
└── examples/
    ├── prompt-only/         # what a vague prompt produces, unedited
    └── speckit-driven/      # pointer to the final, specified result
```

## Git checkpoints

| Tag | Stage |
|---|---|
| `01-start` | Empty repository skeleton |
| `02-prompt-only` | Vague-prompt implementation, unedited |
| `03-spec-created` | `/speckit.specify` output |
| `04-spec-clarified` | `/speckit.clarify` output |
| `05-plan-created` | `/speckit.plan` output |
| `06-tasks-created` | `/speckit.tasks` output |
| `07-analysis-complete` | `/speckit.analyze` output |
| `08-implemented` | `/speckit.implement` output, builds cleanly |
| `09-hardware-verified` | Verified on physical Heltec WiFi Kit V3 |

## Learn more

- Full textbook: [docs/textbook.md](docs/textbook.md)
- VS Code setup: [docs/vscode.md](docs/vscode.md)
- JetBrains / CLion setup: [docs/jetbrains.md](docs/jetbrains.md)
- Claude Code workflow: [docs/claude-code.md](docs/claude-code.md)
- Codex workflow: [docs/codex.md](docs/codex.md)
- Troubleshooting: [docs/troubleshooting.md](docs/troubleshooting.md)
- Presentation outline (Hebrew): [presentation/presentation-outline.md](presentation/presentation-outline.md)
- Presentation link: _added once the Google Slides deck is published_

## References

- [Spec Kit](https://github.com/github/spec-kit)
- [Spec Kit documentation](https://github.github.io/spec-kit/)
- [Claude Code documentation](https://docs.claude.com/en/docs/claude-code)
- [Codex documentation](https://developers.openai.com/codex)
- [PlatformIO](https://platformio.org/)
- [Heltec WiFi Kit 32 (V3)](https://heltec.org/project/wifi-kit32-v3/)

## License

See [LICENSE](LICENSE).
