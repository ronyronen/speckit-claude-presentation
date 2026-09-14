# Contract: Serial diagnostic line

This device exposes exactly one external interface: a Serial line printed
once per sampling cycle (every 2 seconds, FR-006 — uniform across both
supported sensors, see GitHub issue #2). This is the "contract" for that
line — anything reading Serial output (a human, a script, a future log
collector) can rely on this format, regardless of which sensor is
fitted.

## Format

```text
<millis>,<state>,<temperature_or_dash>
```

- `millis`: `unsigned long`, milliseconds since boot (from `millis()`)
- `state`: one of `OK`, `WARNING`, `SENSOR_ERROR`
- `temperature_or_dash`: the current or last-valid temperature in °C with
  one decimal place (e.g. `26.4`), or `-` if no valid reading has ever
  been obtained yet (only possible in `SENSOR_ERROR` immediately after
  boot)

## Examples

```text
2000,OK,26.4
4000,OK,26.5
...
32000,WARNING,31.2
...
90000,SENSOR_ERROR,31.2
```

The `31.2` in the last line is the last valid reading, still reported
per FR-009 even though the current state is `SENSOR_ERROR` — Serial never
goes silent just because the sensor failed (Constitution Principle V).

## Non-goals

- Not JSON, not versioned, not intended for machine parsing beyond a
  simple CSV split — this is a diagnostic aid for the workshop and for
  debugging on a bench, not a product API.
