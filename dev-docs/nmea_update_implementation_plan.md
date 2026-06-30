# Steps(V2) Marine Instruments — Feasibility Report

## Executive Summary

**Yes, Steps(V2) can do this** — but it needs a small number of targeted native builtins added to the interpreter first. The language's existing feature set covers ~80% of what's needed. The gaps are specific, well-defined, and modest to implement.

---

## Existing Implementations — Feature Comparison

I reviewed all three existing instrument programs to establish the target feature set:

### What They All Do

| Feature | BEAM | PLAIN | FORGE |
|---------|:----:|:-----:|:-----:|
| **NMEA 0183 sentence parsing** | ✅ | ✅ | ✅ |
| Full sentence coverage (GGA/RMC/GLL/DPT/DBT/MWV/VHW/HDT/MTW/VTG/GSV/GSA/ZDA/XTE/RMB) | ✅ | ✅ | ✅ |
| APB + BOD sentence support | ❌ | ✅ | ✅ |
| AIS target tracking (VDM payload decoding) | Simulated only | ✅ Full decode | ✅ Full decode |
| Position source priority (RMC > GGA > GLL fallback) | ✅ | ✅ | ✅ |
| **Built-in simulator** (SIM mode) | ✅ | ✅ | ✅ |
| Simulator produces realistic drifting values | ✅ | ✅ | ✅ |
| **Live serial port reading** | ✅ | ✅ | ✅ |
| Configurable port + baud rate | ✅ | ✅ | ✅ |
| **Instrument panels** (Position, Speed/COG, Depth/Temp, Heading, Wind) | ✅ | ✅ | ✅ |
| **AIS target list** with MMSI upsert ring buffer | ✅ | ✅ | ✅ |
| **NMEA sentence log** | ✅ | ✅ | ✅ |
| **Satellite status** (SNR bars, PRN table, DOP values) | ✅ | ✅ | ✅ |
| **Voyage data** (UTC, XTE, waypoint nav, autopilot) | ✅ | ✅ | ✅ |
| Tab-based display switching | ✅ | ✅ | ✅ |
| Pause/Resume data updates | ✅ | ✅ | ✅ |
| Clear all data | ✅ | ✅ | ✅ |
| **AIS radar display** (equirectangular projection) | ❌ | ❌ | ✅ |
| **Compass needle** (smoothly animated heading gauge) | ❌ | ❌ | ✅ |
| **Wind rose needle** (smoothly animated wind angle) | ❌ | ❌ | ✅ |

### Display Technology per Language

| Language | Display Type | Refresh Model |
|----------|-------------|---------------|
| **BEAM** | GUI (yabasic + BEAM toolkit) | Immediate-mode render loop |
| **PLAIN** | Full-color TUI (ANSI, cursor positioning, `draw_box`, `text_at`) | Event loop with `poll_key` |
| **FORGE** | GPU GUI (Raylib via `forge.gui`) | 60fps render loop |

---

## Steps(V2) — Current Capabilities Assessment

### ✅ What Steps Already Has

| Requirement | Steps Feature | Status |
|-------------|--------------|--------|
| String parsing (split, substring, etc.) | `split by`, `slice`, `index_of`, `replace`, `contains`, `starts with`, `ends with`, `character at`, `length of` | ✅ Fully capable |
| Numeric conversion | `as number`, `as text`, `as decimal(N)` | ✅ |
| Trigonometry (for simulator drift) | `sin`, `cos`, `atan2`, `pi`, `radians`, `degrees` | ✅ |
| Math functions | `sqrt`, `pow`, `abs`, `round`, `min`, `max`, `%` / `modulo` | ✅ |
| Lists + tables (for AIS ring buffer, log, etc.) | Lists, tables, `add to`, `remove from`, index access, table key access | ✅ |
| File I/O (for NMEA log-to-file) | `read_file`, `write_file`, `append_file`, `file_exists`, `read_csv`, `write_csv` | ✅ |
| TUI building blocks | `box`, `banner`, `line`, `center_text`, `pad_text`, `progress_bar` | ✅ Good foundation |
| Console clear | `clear console` (ANSI `\033[2J\033[H`) | ✅ |
| Display without newline | `indicate` statement | ✅ Critical for TUI |
| ANSI escape sequences | `\n`, `\t` escape support in text literals | ✅ |
| Control flow | `if/otherwise if/otherwise`, `repeat while`, `repeat for each`, `repeat N times` | ✅ |
| Error handling | `attempt: / if unsuccessful: / then continue:` | ✅ |
| Modular code structure | Buildings, Floors, Steps, Risers | ✅ |
| Timing | `time` (Unix timestamp float) | ✅ For sim timing |

### ❌ What Steps Is Missing (Gaps)

| Gap | Why It's Needed | Difficulty |
|-----|----------------|------------|
| **Serial port I/O** | Read NMEA sentences from `/dev/ttyUSB0` etc. in LIVE mode | Medium — requires `pyserial` native builtins |
| **Non-blocking keyboard input** | Poll for key presses without halting (switch tabs, pause, quit) | Medium — needs OS-level `termios`/`msvcrt` |
| **Sleep / delay** | Simulator tick pacing; prevent CPU spin in main loop | Easy — thin wrapper around `time.sleep()` |
| **Cursor positioning** (`text_at`) | Place text at specific (col, row) positions for TUI layout | Easy — ANSI `\033[row;colH` escape |
| **Color output** | Color-coded panels, sentence types in NMEA log | Easy — ANSI `\033[38;2;R;G;Bm` escapes |

> [!IMPORTANT]
> The first three gaps (serial I/O, non-blocking input, sleep) require new **native builtins** in the Python interpreter. They cannot be implemented in pure Steps code.
>
> The last two (cursor positioning, color output) *can* be done with ANSI escape sequences embedded in text strings today — but dedicated native builtins would make the code much cleaner and align with the patterns established in PLAIN's TUI.

---

## Proposed Approach

### Scope: CLI/TUI Instruments (Not GUI)

Given Steps' nature as a text-mode educational language, the target is a **terminal-based dashboard** similar to the PLAIN implementation — not a GUI. This is appropriate because:

- Steps has `clear console`, `indicate`, and TUI primitives (`box`, `banner`, `line`)
- The existing TUI builtins provide a strong foundation
- The building/floor/step architecture maps cleanly to the instrument program's modules

### Phase 1: Add Native Builtins (Interpreter Changes)

These would be added to `src/steps/builtins/` and registered in `registry.py`:

#### 1. `sleep` — Pause execution
```python
# New file: src/steps/builtins/system.py (or add to existing)
def system_sleep(duration: StepsValue, location=None) -> StepsNothing:
    """Sleep for N seconds (float)."""
    import time
    time.sleep(float(duration.value))
    return StepsNothing()
```
```steps
# Steps usage:
call sleep with 0.1    # 100ms delay
```

#### 2. `poll_key` — Non-blocking keyboard input
```python
def system_poll_key(location=None) -> StepsText:
    """Return the key pressed (or "" if none), non-blocking."""
    # Uses select/termios on Linux, msvcrt on Windows
```
```steps
# Steps usage:
call poll_key storing result in key_press
if key_press equals "q"
    exit
```

#### 3. Serial port functions
```python
def serial_open(port, baud, location=None) -> StepsNumber:
    """Open a serial port, return handle ID."""

def serial_read_line(handle, location=None) -> StepsText:
    """Read one line from serial port (non-blocking), return "" if nothing."""

def serial_close(handle, location=None) -> StepsNothing:
    """Close a serial port."""
```
```steps
# Steps usage:
call serial_open with "/dev/ttyUSB0", 4800 storing result in port_handle
call serial_read_line with port_handle storing result in nmea_line
call serial_close with port_handle
```

#### 4. TUI cursor positioning + color (optional but recommended)
```python
def tui_move_cursor(row, col, location=None) -> StepsNothing:
    """Move cursor to row, col (1-based)."""

def tui_set_color(r, g, b, location=None) -> StepsNothing:
    """Set foreground text color (RGB)."""

def tui_reset_color(location=None) -> StepsNothing:
    """Reset terminal colors to default."""
```

> [!NOTE]
> The cursor/color builtins are optional. The program *could* use raw ANSI escape sequences via `indicate`, but dedicated builtins would be cleaner and more educational — keeping the Steps code readable rather than littered with `"\033[38;2;..."` escape sequences.

### Phase 2: Steps Instrument Program

The program would follow the standard Steps project structure:

```
steps_instruments/
├── steps_instruments.building       # Entry point, main loop
├── nmea/                            # NMEA floor
│   ├── parse_sentence.step          # Main dispatcher (like ParseSentence)
│   ├── parse_gga.step               # GGA handler
│   ├── parse_rmc.step               # RMC handler
│   ├── parse_gll.step               # GLL handler
│   ├── parse_dpt.step               # DPT/DBT handler
│   ├── parse_mwv.step               # MWV handler
│   ├── parse_hdt.step               # HDT handler
│   ├── parse_mtw.step               # MTW handler
│   ├── parse_gsv.step               # GSV handler
│   ├── parse_gsa.step               # GSA handler
│   ├── parse_zda.step               # ZDA handler
│   ├── parse_xte.step               # XTE handler
│   ├── parse_rmb.step               # RMB handler
│   └── nmea_field.step              # Field extraction helper
├── simulator/                       # Simulator floor
│   ├── sim_tick.step                 # Advance simulator one tick
│   └── sim_drift.step               # Calculate drifting values
├── display/                         # Display floor
│   ├── draw_panels.step             # Instrument panels (Position, Speed, etc.)
│   ├── draw_nmea_log.step           # NMEA log tab
│   ├── draw_satellites.step         # Satellite tab
│   ├── draw_voyage.step             # Voyage data tab
│   ├── draw_ais.step                # AIS target list
│   └── draw_status_bar.step         # Status bar
└── data/                            # Data management floor
    ├── clear_data.step              # Reset all state
    └── update_ais.step              # AIS target upsert
```

### What the Steps Implementation Would Support

Given the CLI/TUI scope:

| Feature | Steps Version | Notes |
|---------|:------------:|-------|
| NMEA sentence parsing (all types) | ✅ | Pure Steps code — `split by ","` etc. |
| Position source priority | ✅ | Building-level globals |
| Built-in simulator | ✅ | Uses existing `sin`/`cos`/`pi` |
| Live serial reading | ✅ | Via new `serial_open`/`serial_read_line` builtins |
| Instrument panels (text-based) | ✅ | Using `box`/`banner` + cursor positioning |
| AIS target ring buffer | ✅ | List of tables with MMSI upsert |
| NMEA sentence log | ✅ | List with ring-buffer append |
| Satellite status (SNR text bars, DOP) | ✅ | Unicode block chars + `indicate` |
| Voyage data tab | ✅ | Text display |
| Tab switching (keyboard) | ✅ | Via `poll_key` |
| Pause/Resume/Clear | ✅ | Via `poll_key` |
| Color-coded display | ✅ | Via ANSI escapes or `tui_set_color` |
| AIS radar display | ❌ | Not feasible in text mode |
| Animated compass/wind needles | ❌ | Not feasible in text mode (FORGE-only) |

---

## Open Questions

> [!IMPORTANT]
> **Q1: Do you want me to implement the new builtins and build the program?**
> This would be a significant project. Phase 1 (builtins) is ~2-3 files changed. Phase 2 (the instruments program) is ~15-20 new `.step` files plus the `.building` file. I'd recommend doing it incrementally.

> [!IMPORTANT]
> **Q2: Should the cursor/color builtins be added as proper native functions, or is it acceptable to use raw ANSI escapes in text strings?**
> The PLAIN approach uses dedicated `text_at()`, `text_color_rgb()`, and `draw_box()` builtins, making the code very clean. Steps could go either way, but dedicated builtins would be more in keeping with the language's educational philosophy.

> [!IMPORTANT]
> **Q3: How much of the PLAIN feature set do you want?**
> - **Minimal**: Just the 5 instrument panels + simulator + NMEA log (achievable quickly)
> - **Full**: All panels + satellite tab + voyage tab + AIS + serial port + tab switching (matches PLAIN)

> [!IMPORTANT]
> **Q4: Does `pyserial` dependency concern you?**
> The serial port builtins would require `pip install pyserial`. This is a runtime dependency only needed for LIVE mode. The simulator would work without it. We could make it a soft/optional import.

---

## Verification Plan

### Automated Tests
- Unit tests for new builtins (`sleep`, `poll_key`, `serial_*`)
- Test NMEA parsing steps individually with known sentences
- Run the simulator mode and verify output matches expected values

### Manual Verification
- Run the full TUI dashboard in simulator mode
- Verify keyboard interaction (tab switching, pause, quit)
- If serial hardware is available, test LIVE mode with a real NMEA device
