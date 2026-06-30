# Steps Instruments — Task Tracker

## Phase 1: Native Builtins
- `[x]` Create `src/steps/builtins/system.py` (sleep, poll_key, restore_terminal)
- `[x]` Create `src/steps/builtins/serial.py` (serial_open, serial_read_line, serial_close)
- `[x]` Add TUI cursor/color functions to `src/steps/builtins/tui.py`
- `[x]` Register all new builtins in `registry.py`
- `[x]` Export from `__init__.py`

## Phase 2: Steps Instrument Program (Minimal)
- `[x]` Create project folder + building file
- `[x]` Create nmea floor steps (parse_sentence, parse_rmc, parse_dpt, parse_mwv, parse_hdt, parse_mtw, nmea_field)
- `[x]` Create simulator floor step (sim_generate)
- `[x]` Create rendering floor step (draw_display)
- `[x]` Test in simulator mode — WORKING ✅

## Bugs Found & Fixed
- `[x]` Fix interpreter riser context bug — nested step calls clobbered `_current_risers`, breaking riser resolution after the first call
