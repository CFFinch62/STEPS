# Steps Instruments — Walkthrough

## Summary

Built a working NMEA 0183 marine instrument TUI program in Steps(V2). Extended the interpreter with 11 new native builtins, fixed a riser context bug, updated all documentation, and produced a Linux release build.

---

## Phase 1: Interpreter Extensions

### New Builtin Modules

#### [NEW] [system.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/src/steps/builtins/system.py)
- `sleep(duration)` — pauses execution for N seconds (float)
- `poll_key()` — non-blocking keyboard read via `termios`/`select`
- `restore_terminal()` — restores normal terminal mode

#### [NEW] [serial.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/src/steps/builtins/serial.py)
- `serial_open(port, baud)` — opens serial port, returns integer handle
- `serial_read_line(handle)` — non-blocking line read
- `serial_close(handle)` — closes port and frees handle

#### [MODIFY] [tui.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/src/steps/builtins/tui.py)
5 new ANSI escape functions: `move_cursor`, `set_color`, `reset_color`, `hide_cursor`, `show_cursor`

#### [MODIFY] [registry.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/src/steps/builtins/registry.py)
All 11 new functions registered (56 total native functions).

#### [MODIFY] [__init__.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/src/steps/builtins/__init__.py)
Exports updated for new modules.

### Interpreter Bugfix

#### [MODIFY] [interpreter.py](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/src/steps/interpreter.py)
**Bug:** Nested step calls clobbered `_current_risers`, breaking riser resolution after the first call.
**Fix:** Save/restore `_current_risers` with a `finally` block.

---

## Phase 2: Instrument Program

```
projects/steps_instruments/
├── steps_instruments.building     # Entry point + main loop
├── nmea/                          # NMEA parsing floor
│   ├── nmea_field.step
│   ├── parse_sentence.step        # Dispatcher
│   ├── parse_rmc.step             # Position + SOG/COG
│   ├── parse_dpt.step             # Depth
│   ├── parse_mwv.step             # Wind
│   ├── parse_hdt.step             # Heading
│   └── parse_mtw.step             # Water temperature
├── simulator/
│   └── sim_generate.step          # Sine-wave NMEA generator
└── rendering/
    └── draw_display.step          # TUI dashboard (uses riser)
```

---

## Phase 3: Documentation Updates

#### [MODIFY] [STDLIB.md](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/docs/STDLIB.md)
Added three new sections with full examples:
- **TUI Cursor and Color Control** (move_cursor, set_color, etc.)
- **System Floor** (sleep, poll_key, restore_terminal)
- **Serial Floor** (serial_open, serial_read_line, serial_close)

#### [MODIFY] [LANGUAGE-REFERENCE.md](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/docs/LANGUAGE-REFERENCE.md)
Added function tables for System, Serial, and TUI Cursor/Color sections.

#### [MODIFY] [QUICK-REFERENCE.md](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/docs/QUICK-REFERENCE.md)
Added quick-reference code snippets for cursor/color, system, and serial functions under Console Control.

---

## Phase 4: Build System Updates (pyserial dependency)

All build files updated with `--hidden-import "serial"`:

| File | Change |
|------|--------|
| [pyproject.toml](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/pyproject.toml) | Added `serial` optional dependency group |
| [steps.spec](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/steps.spec) | Added `'serial'` to hiddenimports |
| [StepsIDE.spec](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/StepsIDE.spec) | Added `'serial'` to hiddenimports |
| [build_release.sh](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/build_release.sh) | Added `--hidden-import "serial"` to both commands |
| [build_interpreter.sh](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/build_interpreter.sh) | Added `--hidden-import "serial"` |
| [build_mac_intel.sh](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/build_mac_intel.sh) | Added `--hidden-import "serial"` to both commands |
| [build_release.bat](file:///home/chuck/Dropbox/Programming/Languages_and_Code/Programming_Projects/Programming_Tools/LANGUAGES/STEPSv2/build_release.bat) | Added `--hidden-import "serial"` to both commands |

---

## Phase 5: Linux Release Build

- ✅ Build completed successfully
- ✅ `dist/linux/StepsIDE/StepsIDE` — IDE application (directory bundle)
- ✅ `dist/linux/steps` — CLI interpreter (8.1 MB single binary)
- ✅ Compiled interpreter validates the instruments project: `6 floor(s), 18 step(s)`

### How to test

```bash
# With the compiled binary:
cd STEPSv2
dist/linux/steps run projects/steps_instruments

# Or from source:
source venv/bin/activate
PYTHONPATH=src python -m steps.main run projects/steps_instruments
```

Press `q` to exit cleanly.
