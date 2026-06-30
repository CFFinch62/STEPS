"""TUI (Text User Interface) operations for console graphics.

Provides functions for drawing boxes, lines, banners, and other text-based
UI elements using Unicode box-drawing characters.
"""

import sys
from typing import Optional

from ..types import StepsValue, StepsNumber, StepsText, StepsNothing
from ..errors import StepsTypeError, StepsRuntimeError, ErrorCode, SourceLocation


# =============================================================================
# Box Drawing Characters
# =============================================================================

# Single line box characters
SINGLE_BOX = {
    "tl": "┌",  # top-left
    "tr": "┐",  # top-right
    "bl": "└",  # bottom-left
    "br": "┘",  # bottom-right
    "h": "─",   # horizontal
    "v": "│",   # vertical
}

# Double line box characters
DOUBLE_BOX = {
    "tl": "╔",
    "tr": "╗",
    "bl": "╚",
    "br": "╝",
    "h": "═",
    "v": "║",
}

# Line styles
LINE_STYLES = {
    "single": "─",
    "double": "═",
    "dashed": "╌",
    "thick": "━",
}


# =============================================================================
# Native TUI Functions
# =============================================================================

def tui_box(
    content: StepsValue,
    width: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsText:
    """Draw a single-line box around text content.
    
    Args:
        content: Text to display inside the box
        width: Total width of the box (including borders)
        
    Returns:
        Multi-line text string with the box
    """
    if not isinstance(width, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"Box width must be a number, got {width.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Use: call box with \"Hello\", 30"
        )
    
    content_str = content.as_text().value
    w = max(int(width.value), len(content_str) + 4)  # Minimum width to fit content
    inner_width = w - 2  # Account for side borders
    
    b = SINGLE_BOX
    
    # Build the box
    top = b["tl"] + b["h"] * inner_width + b["tr"]
    content_padded = content_str.center(inner_width)
    middle = b["v"] + content_padded + b["v"]
    bottom = b["bl"] + b["h"] * inner_width + b["br"]
    
    return StepsText(f"{top}\n{middle}\n{bottom}")


def tui_line(
    width: StepsValue,
    style: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsText:
    """Draw a horizontal line.
    
    Args:
        width: Width of the line
        style: Line style - "single", "double", "dashed", or "thick"
        
    Returns:
        Text string with the line
    """
    if not isinstance(width, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"Line width must be a number, got {width.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Use: call line with 40, \"single\""
        )
    
    style_str = style.as_text().value.lower()
    
    if style_str not in LINE_STYLES:
        raise StepsRuntimeError(
            code=ErrorCode.E401,
            message=f"Unknown line style '{style_str}'.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint=f"Valid styles: {', '.join(LINE_STYLES.keys())}"
        )
    
    char = LINE_STYLES[style_str]
    w = int(width.value)
    
    return StepsText(char * w)


def tui_banner(
    title: StepsValue,
    width: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsText:
    """Draw a decorative banner with a centered title.
    
    Uses double-line box characters for a bold appearance.
    
    Args:
        title: Title text for the banner
        width: Total width of the banner
        
    Returns:
        Multi-line text string with the banner
    """
    if not isinstance(width, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"Banner width must be a number, got {width.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Use: call banner with \"My App\", 40"
        )
    
    title_str = title.as_text().value
    w = max(int(width.value), len(title_str) + 4)
    inner_width = w - 2
    
    b = DOUBLE_BOX
    
    # Build the banner
    top = b["tl"] + b["h"] * inner_width + b["tr"]
    title_padded = title_str.center(inner_width)
    middle = b["v"] + title_padded + b["v"]
    bottom = b["bl"] + b["h"] * inner_width + b["br"]
    
    return StepsText(f"{top}\n{middle}\n{bottom}")


def tui_center_text(
    text: StepsValue,
    width: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsText:
    """Center text within a given width.
    
    Args:
        text: Text to center
        width: Total width to center within
        
    Returns:
        Centered text with padding
    """
    if not isinstance(width, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"Width must be a number, got {width.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Use: call center_text with \"Hello\", 40"
        )
    
    text_str = text.as_text().value
    w = int(width.value)
    
    return StepsText(text_str.center(w))


def tui_pad_text(
    text: StepsValue,
    width: StepsValue,
    align: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsText:
    """Pad text to a specific width with alignment.
    
    Args:
        text: Text to pad
        width: Total width
        align: Alignment - "left", "right", or "center"
        
    Returns:
        Padded text
    """
    if not isinstance(width, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"Width must be a number, got {width.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Use: call pad_text with \"Hello\", 20, \"left\""
        )
    
    text_str = text.as_text().value
    align_str = align.as_text().value.lower()
    w = int(width.value)
    
    if align_str == "left":
        return StepsText(text_str.ljust(w))
    elif align_str == "right":
        return StepsText(text_str.rjust(w))
    elif align_str == "center":
        return StepsText(text_str.center(w))
    else:
        raise StepsRuntimeError(
            code=ErrorCode.E401,
            message=f"Unknown alignment '{align_str}'.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Valid alignments: left, right, center"
        )


def tui_progress_bar(
    current: StepsValue,
    total: StepsValue,
    width: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsText:
    """Render a text-based progress bar.
    
    Args:
        current: Current progress value
        total: Total/maximum value
        width: Width of the progress bar (not including brackets)
        
    Returns:
        Progress bar text like "[████████░░░░░░░░] 50%"
    """
    if not isinstance(current, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"Current value must be a number, got {current.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Use: call progress_bar with 5, 10, 20"
        )
    
    if not isinstance(total, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"Total value must be a number, got {total.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Use: call progress_bar with 5, 10, 20"
        )
    
    if not isinstance(width, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"Width must be a number, got {width.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint="Use: call progress_bar with 5, 10, 20"
        )
    
    cur = float(current.value)
    tot = float(total.value)
    w = int(width.value)
    
    # Calculate percentage and filled portion
    if tot <= 0:
        percentage = 0
    else:
        percentage = min(100, max(0, (cur / tot) * 100))
    
    filled = int((percentage / 100) * w)
    empty = w - filled
    
    # Build the bar
    bar = "█" * filled + "░" * empty
    percent_str = f"{int(percentage)}%"
    
    return StepsText(f"[{bar}] {percent_str}")


# =============================================================================
# Cursor and Color Control (ANSI escape sequences)
# =============================================================================

def tui_move_cursor(
    row: StepsValue,
    col: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsNothing:
    """Move the terminal cursor to (row, col).  Both are 1-based."""
    if not isinstance(row, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"move_cursor row must be a number, got {row.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint='Use: call move_cursor with 1, 1'
        )
    if not isinstance(col, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"move_cursor col must be a number, got {col.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint='Use: call move_cursor with 1, 1'
        )
    r = int(row.value)
    c = int(col.value)
    sys.stdout.write(f"\033[{r};{c}H")
    sys.stdout.flush()
    return StepsNothing()


def tui_set_color(
    r: StepsValue,
    g: StepsValue,
    b: StepsValue,
    location: Optional[SourceLocation] = None
) -> StepsNothing:
    """Set the foreground text colour using 24-bit RGB values (0-255)."""
    if not isinstance(r, StepsNumber):
        raise StepsTypeError(
            code=ErrorCode.E302,
            message=f"set_color red must be a number, got {r.type_name()}.",
            file=location.file if location else None,
            line=location.line if location else 0,
            column=location.column if location else 0,
            hint='Use: call set_color with 255, 255, 255'
        )
    rv = max(0, min(255, int(r.value)))
    gv = max(0, min(255, int(g.value)))
    bv = max(0, min(255, int(b.value)))
    sys.stdout.write(f"\033[38;2;{rv};{gv};{bv}m")
    sys.stdout.flush()
    return StepsNothing()


def tui_reset_color(
    location: Optional[SourceLocation] = None
) -> StepsNothing:
    """Reset terminal colours and text attributes to defaults."""
    sys.stdout.write("\033[0m")
    sys.stdout.flush()
    return StepsNothing()


def tui_hide_cursor(
    location: Optional[SourceLocation] = None
) -> StepsNothing:
    """Hide the terminal cursor (for clean TUI rendering)."""
    sys.stdout.write("\033[?25l")
    sys.stdout.flush()
    return StepsNothing()


def tui_show_cursor(
    location: Optional[SourceLocation] = None
) -> StepsNothing:
    """Show the terminal cursor (call before exiting a TUI program)."""
    sys.stdout.write("\033[?25h")
    sys.stdout.flush()
    return StepsNothing()

