"""System operations — sleep, keyboard polling, terminal restore.

These builtins support interactive CLI/TUI programs that need
non-blocking keyboard input and timed delays.
"""

import sys
import time
from typing import Optional

from ..types import StepsValue, StepsNumber, StepsText, StepsNothing
from ..errors import StepsTypeError, StepsRuntimeError, ErrorCode, SourceLocation


# ---------------------------------------------------------------------------
# sleep
# ---------------------------------------------------------------------------

def system_sleep(
    duration: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsNothing:
    """Pause execution for *duration* seconds (float)."""
    if not isinstance(duration, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"sleep requires a number (seconds), got {duration.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint='Use: call sleep with 0.2'
        )
    time.sleep(max(0.0, float(duration.value)))
    return StepsNothing()


# ---------------------------------------------------------------------------
# Non-blocking keyboard input
# ---------------------------------------------------------------------------

_terminal_original_settings = None
_terminal_in_cbreak = False


def _ensure_cbreak() -> None:
    """Switch stdin to cbreak mode (character-at-a-time, no echo)."""
    global _terminal_original_settings, _terminal_in_cbreak
    if _terminal_in_cbreak:
        return
    try:
        import termios
        import tty
        import atexit
        fd = sys.stdin.fileno()
        _terminal_original_settings = termios.tcgetattr(fd)
        tty.setcbreak(fd)
        _terminal_in_cbreak = True
        atexit.register(_restore_terminal_internal)
    except (ImportError, OSError, ValueError):
        pass  # not a real terminal — silently degrade


def _restore_terminal_internal() -> None:
    """Restore the terminal to its original settings."""
    global _terminal_original_settings, _terminal_in_cbreak
    if _terminal_original_settings is not None:
        try:
            import termios
            fd = sys.stdin.fileno()
            termios.tcsetattr(fd, termios.TCSADRAIN, _terminal_original_settings)
        except (ImportError, OSError, ValueError):
            pass
    _terminal_in_cbreak = False
    _terminal_original_settings = None


def system_poll_key(
    location: Optional[SourceLocation] = None
) -> StepsText:
    """Return one key character if available, or \"\" if nothing pressed.

    Non-blocking — returns immediately.
    """
    try:
        import select
        _ensure_cbreak()
        if select.select([sys.stdin], [], [], 0)[0]:
            ch = sys.stdin.read(1)
            return StepsText(ch)
        return StepsText("")
    except (ImportError, OSError, ValueError):
        return StepsText("")


def system_restore_terminal(
    location: Optional[SourceLocation] = None
) -> StepsNothing:
    """Restore the terminal to normal line-buffered mode.

    Call this before exiting a TUI program so the user's shell
    behaves normally again.
    """
    _restore_terminal_internal()
    return StepsNothing()
