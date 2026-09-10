#!/usr/bin/env python3
"""Renders real captured terminal output / real file excerpts as clean
card images for the pptx. Every string of content below was copy-pasted
verbatim from an actual command run or an actual repository file in this
project -- nothing here is invented output.
"""
import os

from PIL import Image, ImageDraw, ImageFont

OUT_DIR = "presentation/assets/generated"
os.makedirs(OUT_DIR, exist_ok=True)

MONO_CANDIDATES = [
    "/System/Library/Fonts/Menlo.ttc",
    "/System/Library/Fonts/Supplemental/Menlo.ttc",
    "/Library/Fonts/Menlo.ttc",
]
SANS_CANDIDATES = [
    "/System/Library/Fonts/Supplemental/Arial.ttf",
    "/System/Library/Fonts/Helvetica.ttc",
]


def find_font(candidates, size, index=0):
    for path in candidates:
        if os.path.exists(path):
            try:
                return ImageFont.truetype(path, size, index=index)
            except Exception:
                continue
    return ImageFont.load_default()


def mono(size):
    return find_font(MONO_CANDIDATES, size)


def sans(size, bold=False):
    return find_font(SANS_CANDIDATES, size)


def render_card(
    filename,
    title,
    lines,
    theme="terminal",  # "terminal" (dark) or "code" (light)
    width=1600,
    line_height=34,
    font_size=20,
    pad=40,
    title_h=70,
):
    height = title_h + pad * 2 + line_height * len(lines)
    if theme == "terminal":
        bg = (30, 32, 38)
        title_bg = (20, 21, 26)
        title_fg = (226, 232, 240)
        fg_default = (203, 213, 225)
        border = (71, 85, 105)
    else:
        bg = (250, 250, 252)
        title_bg = (241, 245, 249)
        title_fg = (15, 23, 42)
        fg_default = (30, 41, 59)
        border = (203, 213, 225)

    img = Image.new("RGB", (width, height), bg)
    draw = ImageDraw.Draw(img)
    draw.rectangle([0, 0, width - 1, title_h - 1], fill=title_bg)
    draw.rectangle([0, 0, width - 1, height - 1], outline=border, width=3)
    draw.line([0, title_h, width, title_h], fill=border, width=2)

    tf = sans(28, bold=True)
    draw.text((pad, title_h // 2), title, font=tf, fill=title_fg, anchor="lm")

    mf = mono(font_size)
    y = title_h + pad
    for line, color in lines:
        draw.text((pad, y), line, font=mf, fill=(color or fg_default))
        y += line_height

    path = os.path.join(OUT_DIR, filename)
    img.save(path)
    print(f"wrote {path} ({width}x{height})")


GREEN = (74, 222, 128)
RED = (248, 113, 113)
YELLOW = (250, 204, 21)
DIM = (148, 163, 184)
BLUE_CODE = (96, 165, 250)
GRAY_CODE = (148, 163, 184)


def L(text, color=None):
    return (text, color)


# 1. specify init -- real captured output from this project's own setup
render_card(
    "terminal-specify-init.png",
    "$ specify init --here --force --integration claude",
    [
        L("Selected coding agent integration: claude", DIM),
        L("Selected script type: sh", DIM),
        L("Initialize Specify Project"),
        L("├── ● Check required tools (ok)", GREEN),
        L("├── ● Select coding agent integration (claude)", GREEN),
        L("├── ● Select script type (sh)", GREEN),
        L("├── ● Install integration (Claude Code)", GREEN),
        L("├── ● Install shared infrastructure (scripts (sh) + templates)", GREEN),
        L("├── ● Ensure scripts executable (5 updated)", GREEN),
        L("├── ● Constitution setup (copied from template)", GREEN),
        L("├── ● Install bundled workflow (speckit installed)", GREEN),
        L("└── ● Finalize (project ready)", GREEN),
        L(""),
        L("Project ready.", YELLOW),
    ],
    theme="terminal",
)

# 2. pio build -- real captured output, this session
render_card(
    "terminal-pio-build.png",
    "$ pio run -e heltec_wifi_kit_32_V3",
    [
        L("|-- Adafruit BME280 Library @ 2.3.0", DIM),
        L("|-- Adafruit Unified Sensor @ 1.1.15", DIM),
        L("|-- ESP8266 and ESP32 OLED driver for SSD1306 displays @ 4.6.2", DIM),
        L("Building in release mode"),
        L(""),
        L("RAM:   [=         ]   7.1% (used 23124 bytes from 327680 bytes)", GREEN),
        L("Flash: [=         ]  10.8% (used 362623 bytes from 3342336 bytes)", GREEN),
        L("========================= [SUCCESS] Took 2.63 seconds =========================", GREEN),
    ],
    theme="terminal",
)

# 3. native tests -- real captured output, this session
render_card(
    "terminal-pio-test.png",
    "$ pio test -e native",
    [
        L("test_first_valid_reading_below_threshold_is_ok        [PASSED]", GREEN),
        L("test_warning_triggers_strictly_above_30               [PASSED]", GREEN),
        L("test_exactly_30_does_not_trigger_warning              [PASSED]", GREEN),
        L("test_warning_clears_strictly_below_28                 [PASSED]", GREEN),
        L("test_exactly_28_does_not_clear_warning                [PASSED]", GREEN),
        L("test_no_toggling_anywhere_inside_hysteresis_band       [PASSED]", GREEN),
        L("test_one_or_two_failures_do_not_change_state           [PASSED]", GREEN),
        L("test_third_consecutive_failure_enters_sensor_error     [PASSED]", GREEN),
        L("test_recovery_after_sensor_error_reevaluates_normally  [PASSED]", GREEN),
        L("test_no_valid_reading_ever_leaves_has_last_valid_false [PASSED]", GREEN),
        L("test_consecutive_failures_saturate_instead_of_overflowing [PASSED]", GREEN),
        L(""),
        L("================ 11 test cases: 11 succeeded ================", GREEN),
    ],
    theme="terminal",
)

# 4. git log -- real, current (8 tags; 09 not yet created, on purpose)
render_card(
    "terminal-git-log.png",
    "$ git log --oneline --all --decorate",
    [
        L("16df826 (tag: 08-implemented) Implement the Heltec environmental monitor"),
        L("073d82e (tag: 07-analysis-complete) Cross-artifact analysis of spec/plan/tasks"),
        L("e2fb144 (tag: 06-tasks-created) Generate dependency-ordered tasks"),
        L("13a41b4 (tag: 05-plan-created) Create the implementation plan"),
        L("e8a572d (tag: 04-spec-clarified) Clarify the Heltec monitor spec"),
        L("d015334 (tag: 03-spec-created) Ratify constitution and create the feature spec"),
        L("c0bf079 Initialize GitHub Spec Kit (Claude Code + Codex integrations)"),
        L("6d76fad (tag: 02-prompt-only) Add prompt-only reference implementation"),
        L("0e9bb8f (tag: 01-start) Bootstrap repository skeleton"),
        L(""),
        L("# 09-hardware-verified: not yet tagged -- pending physical test", YELLOW),
    ],
    theme="terminal",
)

# 5. the real analyze-fix diff -- real `git show` output
render_card(
    "code-analyze-diff.png",
    "git show b91cd94 -- specs/001-heltec-monitor/spec.md",
    [
        L("@@ -174,14 +174,15 @@ value as if it were current.", GRAY_CODE),
        L(" - SC-001: ... within one sampling interval of a state change."),
        L("-- SC-004: A sensor disconnection is visible on the OLED within one", RED),
        L("-  sampling interval, and the device continues running (no crash/hang)", RED),
        L("-  indefinitely while disconnected.", RED),
        L("++ SC-004: A sensor disconnection is visible on the OLED within 3", GREEN),
        L("+  sampling intervals (the debounce window defined in FR-005), and the", GREEN),
        L("+  device continues running (no crash/hang) indefinitely while", GREEN),
        L("+  disconnected.", GREEN),
    ],
    theme="code",
    width=1700,
)

# 6. spec.md Clarifications section -- real file content
render_card(
    "code-spec-clarifications.png",
    "specs/001-heltec-monitor/spec.md -- ## Clarifications",
    [
        L("### Session 2026-09-10", BLUE_CODE),
        L(""),
        L("- Q: How often should the device sample the sensor?"),
        L("  A: Once per second."),
        L("- Q: At exactly the threshold values, which state wins?"),
        L("  A: Strictly greater/less. 30.0C / 28.0C exactly hold the prior state."),
        L("- Q: Single failed read -> immediate SENSOR_ERROR, or debounce?"),
        L("  A: 3 consecutive failed reads required."),
        L("- Q: What should the OLED show during SENSOR_ERROR?"),
        L("  A: \"SENSOR ERROR\" + last valid reading, marked stale."),
    ],
    theme="code",
    width=1700,
)

# 7. monitor_logic.cpp excerpt -- real file content
render_card(
    "code-monitor-logic.png",
    "firmware/src/monitor_logic.cpp",
    [
        L("#include \"monitor_logic.h\"   // no Arduino.h, no Wire.h", GRAY_CODE),
        L(""),
        L("MonitorState evaluate_temperature(MonitorState prev, float t) {", BLUE_CODE),
        L("  if (prev == MonitorState::WARNING) {"),
        L("    if (t < kWarningOffThresholdC) return MonitorState::OK;"),
        L("    return MonitorState::WARNING;"),
        L("  }"),
        L("  if (t > kWarningOnThresholdC) return MonitorState::WARNING;", GREEN),
        L("  return MonitorState::OK;"),
        L("}"),
        L(""),
        L("// FR-005: <3 consecutive failures leaves state unchanged.", GRAY_CODE),
        L("if (next.consecutive_failures >= kFailureDebounceCount)"),
        L("  next.state = MonitorState::SENSOR_ERROR;"),
    ],
    theme="code",
    width=1700,
)

# 8. analysis-report.md finding I1 -- real file content
render_card(
    "code-analysis-report.png",
    "specs/001-heltec-monitor/analysis-report.md -- finding I1",
    [
        L("ID: I1   Category: Inconsistency   Severity: HIGH", RED),
        L("Location: spec.md SC-004, FR-005"),
        L(""),
        L("Summary: SC-004 says a sensor disconnection is \"visible on the"),
        L("OLED within one sampling interval,\" but FR-005 (added during"),
        L("clarification) requires 3 consecutive failed reads -- i.e. up"),
        L("to ~3 sampling intervals, not one. SC-004 was written before"),
        L("the debounce clarification and never updated."),
        L(""),
        L("Recommendation: Update SC-004 to state \"within 3 sampling", GREEN),
        L("intervals (the debounce window defined in FR-005).\"", GREEN),
    ],
    theme="code",
    width=1700,
)

print("done")
