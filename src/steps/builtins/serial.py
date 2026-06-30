"""Serial port operations for NMEA 0183 data.

Wraps pyserial to provide open / read-line / close primitives
callable from Steps code.  pyserial is imported lazily so the
interpreter still works when it is not installed — only LIVE-mode
serial reading will fail.
"""

from typing import Dict, Optional

from ..types import StepsValue, StepsNumber, StepsText, StepsNothing
from ..errors import StepsTypeError, StepsRuntimeError, ErrorCode, SourceLocation


# ---------------------------------------------------------------------------
# Handle registry — maps integer handles to open Serial objects
# ---------------------------------------------------------------------------

_serial_handles: Dict[int, object] = {}
_next_handle: int = 0


# ---------------------------------------------------------------------------
# serial_open
# ---------------------------------------------------------------------------

def serial_open(
    port: StepsValue,
    baud: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsNumber:
    """Open a serial port and return an integer handle.

    Steps usage::

        call serial_open with "/dev/ttyUSB0", 4800 storing result in handle
    """
    global _next_handle

    try:
        import serial as _pyserial
    except ImportError:
        raise StepsRuntimeError(
            code=ErrorCode.E407,
            message="pyserial is not installed.  Run:  pip install pyserial",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Install pyserial to use serial port features."
        )

    if not isinstance(port, StepsText):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"serial_open port must be text, got {port.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint='Use: call serial_open with "/dev/ttyUSB0", 4800'
        )

    if not isinstance(baud, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"serial_open baud must be a number, got {baud.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint='Use: call serial_open with "/dev/ttyUSB0", 4800'
        )

    port_str = port.value
    baud_int = int(baud.value)

    try:
        ser = _pyserial.Serial(port_str, baud_int, timeout=0)
        handle = _next_handle
        _next_handle += 1
        _serial_handles[handle] = ser
        return StepsNumber(handle)
    except _pyserial.SerialException as exc:
        raise StepsRuntimeError(
            code=ErrorCode.E407,
            message=f"Could not open serial port '{port_str}': {exc}",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Check that the port exists and is not in use."
        )


# ---------------------------------------------------------------------------
# serial_read_line
# ---------------------------------------------------------------------------

def serial_read_line(
    handle: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsText:
    """Non-blocking read of one line from an open serial port.

    Returns the line (stripped) or \"\" if nothing is available yet.
    """
    if not isinstance(handle, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"serial_read_line handle must be a number, got {handle.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Pass the handle returned by serial_open."
        )

    h = int(handle.value)
    if h not in _serial_handles:
        raise StepsRuntimeError(
            code=ErrorCode.E407,
            message=f"Invalid serial handle: {h}",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="The port may have been closed."
        )

    ser = _serial_handles[h]
    try:
        if ser.in_waiting > 0:
            raw = ser.readline()
            line = raw.decode("ascii", errors="replace").strip()
            return StepsText(line)
        return StepsText("")
    except Exception:
        return StepsText("")


# ---------------------------------------------------------------------------
# serial_close
# ---------------------------------------------------------------------------

def serial_close(
    handle: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsNothing:
    """Close a previously opened serial port."""
    if not isinstance(handle, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"serial_close handle must be a number, got {handle.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Pass the handle returned by serial_open."
        )

    h = int(handle.value)
    if h in _serial_handles:
        try:
            _serial_handles[h].close()
        except Exception:
            pass
        del _serial_handles[h]
    return StepsNothing()
