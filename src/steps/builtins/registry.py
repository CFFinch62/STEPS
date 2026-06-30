"""Native Functions Registry.

These functions can be called directly from Steps code via the interpreter.
The interpreter checks this registry before looking for user-defined steps.
"""

from .random import random_int, random_choice
from .io import read_file, write_file, append_file, file_exists, read_csv, write_csv
from .text import (
    text_slice, text_lowercase, text_uppercase, text_trim,
    text_index_of, text_replace, text_characters
)
from .tui import (
    tui_box, tui_line, tui_banner, tui_center_text,
    tui_pad_text, tui_progress_bar,
    tui_move_cursor, tui_set_color, tui_reset_color,
    tui_hide_cursor, tui_show_cursor,
)
from .list_math import list_min, list_max, list_sum
from .collections import list_create
from .datetime_functions import time_now, date_today, date_diff
from .math_functions import (
    math_square, math_sqrt, math_pow, math_pi,
    math_sin, math_cos, math_tan,
    math_asin, math_acos, math_atan, math_atan2,
    math_degrees, math_radians,
    math_log, math_log10, math_log2, math_exp,
)
from .system import system_sleep, system_poll_key, system_restore_terminal
from .serial import serial_open, serial_read_line, serial_close

NATIVE_FUNCTIONS = {
    # Random functions
    "random_int": {
        "function": random_int,
        "params": ["min_val", "max_val"],
    },
    "random_choice": {
        "function": random_choice,
        "params": ["lst"],
    },
    # File I/O functions
    "read_file": {
        "function": read_file,
        "params": ["path"],
    },
    "write_file": {
        "function": write_file,
        "params": ["path", "content"],
    },
    "append_file": {
        "function": append_file,
        "params": ["path", "content"],
    },
    "file_exists": {
        "function": file_exists,
        "params": ["path"],
    },
    # CSV functions
    "read_csv": {
        "function": read_csv,
        "params": ["path"],
    },
    "write_csv": {
        "function": write_csv,
        "params": ["path", "data"],
    },
    # String functions
    "slice": {
        "function": text_slice,
        "params": ["text", "start", "end"],
    },
    "lowercase": {
        "function": text_lowercase,
        "params": ["text"],
    },
    "uppercase": {
        "function": text_uppercase,
        "params": ["text"],
    },
    "trim": {
        "function": text_trim,
        "params": ["text"],
    },
    "index_of": {
        "function": text_index_of,
        "params": ["text", "search"],
    },
    "replace": {
        "function": text_replace,
        "params": ["text", "old", "new"],
    },
    "characters": {
        "function": text_characters,
        "params": ["text"],
    },
    # TUI functions
    "box": {
        "function": tui_box,
        "params": ["content", "width"],
    },
    "line": {
        "function": tui_line,
        "params": ["width", "style"],
    },
    "banner": {
        "function": tui_banner,
        "params": ["title", "width"],
    },
    "center_text": {
        "function": tui_center_text,
        "params": ["text", "width"],
    },
    "pad_text": {
        "function": tui_pad_text,
        "params": ["text", "width", "align"],
    },
    "progress_bar": {
        "function": tui_progress_bar,
        "params": ["current", "total", "width"],
    },
    # List creation
    "create_list": {
        "function": list_create,
        "params": ["size", "value"],
    },
    # List aggregate functions
    "list_min": {
        "function": list_min,
        "params": ["lst"],
    },
    "list_max": {
        "function": list_max,
        "params": ["lst"],
    },
    "list_sum": {
        "function": list_sum,
        "params": ["lst"],
    },
    # Math: power / root
    "sqr": {
        "function": math_square,
        "params": ["n"],
    },
    "sqrt": {
        "function": math_sqrt,
        "params": ["n"],
    },
    "pow": {
        "function": math_pow,
        "params": ["base", "exp"],
    },
    "pi": {
        "function": math_pi,
        "params": [],
    },
    # Math: trigonometry
    "sin": {
        "function": math_sin,
        "params": ["n"],
    },
    "cos": {
        "function": math_cos,
        "params": ["n"],
    },
    "tan": {
        "function": math_tan,
        "params": ["n"],
    },
    "asin": {
        "function": math_asin,
        "params": ["n"],
    },
    "acos": {
        "function": math_acos,
        "params": ["n"],
    },
    "atan": {
        "function": math_atan,
        "params": ["n"],
    },
    "atan2": {
        "function": math_atan2,
        "params": ["y", "x"],
    },
    "degrees": {
        "function": math_degrees,
        "params": ["n"],
    },
    "radians": {
        "function": math_radians,
        "params": ["n"],
    },
    # Math: logarithms and exponentials
    "log": {
        "function": math_log,
        "params": ["n"],
    },
    "log10": {
        "function": math_log10,
        "params": ["n"],
    },
    "log2": {
        "function": math_log2,
        "params": ["n"],
    },
    "exp": {
        "function": math_exp,
        "params": ["n"],
    },
    # Date and time functions
    "time": {
        "function": time_now,
        "params": [],
    },
    "date": {
        "function": date_today,
        "params": [],
    },
    "date_diff": {
        "function": date_diff,
        "params": ["date1", "date2"],
    },
    # System functions
    "sleep": {
        "function": system_sleep,
        "params": ["duration"],
    },
    "poll_key": {
        "function": system_poll_key,
        "params": [],
    },
    "restore_terminal": {
        "function": system_restore_terminal,
        "params": [],
    },
    # Serial port functions
    "serial_open": {
        "function": serial_open,
        "params": ["port", "baud"],
    },
    "serial_read_line": {
        "function": serial_read_line,
        "params": ["handle"],
    },
    "serial_close": {
        "function": serial_close,
        "params": ["handle"],
    },
    # TUI cursor and color
    "move_cursor": {
        "function": tui_move_cursor,
        "params": ["row", "col"],
    },
    "set_color": {
        "function": tui_set_color,
        "params": ["r", "g", "b"],
    },
    "reset_color": {
        "function": tui_reset_color,
        "params": [],
    },
    "hide_cursor": {
        "function": tui_hide_cursor,
        "params": [],
    },
    "show_cursor": {
        "function": tui_show_cursor,
        "params": [],
    },
}

