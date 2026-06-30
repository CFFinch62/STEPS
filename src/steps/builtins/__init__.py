"""Steps Builtins Package - Built-in Operations and Functions.

This package provides built-in operations that are used by the interpreter
to implement Steps language features. The package is organized into modules
by category for maintainability.
"""

# Core utilities
from .core import _validate_type

# Type checking operations
from .core import (
    type_of,
    is_number,
    is_text,
    is_boolean,
    is_list,
    is_table,
    is_nothing,
)

# Type conversion operations
from .conversion import (
    convert_to_number,
    convert_to_text,
    convert_to_boolean,
    format_number_string,
)

# Arithmetic operations
from .arithmetic import (
    add_numbers,
    subtract_numbers,
    multiply_numbers,
    divide_numbers,
    modulo_numbers,
    negate_number,
)

# Comparison and boolean operations
from .comparison import (
    equals,
    not_equals,
    less_than,
    greater_than,
    less_than_or_equal,
    greater_than_or_equal,
    boolean_and,
    boolean_or,
    boolean_not,
)

# Text operations
from .text import (
    text_concatenate,
    text_split,
    text_length,
    text_character_at,
    text_contains,
    text_starts_with,
    text_ends_with,
    text_slice,
    text_lowercase,
    text_uppercase,
    text_trim,
    text_index_of,
    text_replace,
    text_characters,
)

# Collection operations (lists and tables)
from .collections import (
    list_add,
    list_remove,
    list_get,
    list_contains,
    table_get,
    table_set,
    table_has_key,
)

# Random operations
from .random import (
    random_int,
    random_choice,
)

# List aggregate math operations
from .list_math import (
    list_min,
    list_max,
    list_sum,
)

# Advanced math functions (roots, trig, log)
from .math_functions import (
    math_square,
    math_sqrt,
    math_pow,
    math_pi,
    math_sin,
    math_cos,
    math_tan,
    math_asin,
    math_acos,
    math_atan,
    math_atan2,
    math_degrees,
    math_radians,
    math_log,
    math_log10,
    math_log2,
    math_exp,
)

# Date and time functions
from .datetime_functions import (
    time_now,
    date_today,
    date_diff,
)

# File I/O operations
from .io import (
    read_file,
    write_file,
    append_file,
    file_exists,
    read_csv,
    write_csv,
)

# TUI operations
from .tui import (
    tui_box,
    tui_line,
    tui_banner,
    tui_center_text,
    tui_pad_text,
    tui_progress_bar,
    tui_move_cursor,
    tui_set_color,
    tui_reset_color,
    tui_hide_cursor,
    tui_show_cursor,
)

# System operations
from .system import (
    system_sleep,
    system_poll_key,
    system_restore_terminal,
)

# Serial port operations
from .serial import (
    serial_open,
    serial_read_line,
    serial_close,
)

# Native functions registry - callable from Steps code
from .registry import NATIVE_FUNCTIONS

# For backward compatibility, expose everything at package level
__all__ = [
    # Core
    '_validate_type',
    'type_of',
    'is_number',
    'is_text',
    'is_boolean',
    'is_list',
    'is_table',
    'is_nothing',
    # Conversion
    'convert_to_number',
    'convert_to_text',
    'convert_to_boolean',
    'format_number_string',
    # Arithmetic
    'add_numbers',
    'subtract_numbers',
    'multiply_numbers',
    'divide_numbers',
    'modulo_numbers',
    'negate_number',
    # Comparison
    'equals',
    'not_equals',
    'less_than',
    'greater_than',
    'less_than_or_equal',
    'greater_than_or_equal',
    'boolean_and',
    'boolean_or',
    'boolean_not',
    # Text
    'text_concatenate',
    'text_split',
    'text_length',
    'text_character_at',
    'text_contains',
    'text_starts_with',
    'text_ends_with',
    'text_slice',
    'text_lowercase',
    'text_uppercase',
    'text_trim',
    'text_index_of',
    'text_replace',
    'text_characters',
    # Collections
    'list_add',
    'list_remove',
    'list_get',
    'list_contains',
    'table_get',
    'table_set',
    'table_has_key',
    # Random
    'random_int',
    'random_choice',
    # List math
    'list_min',
    'list_max',
    'list_sum',
    # Math functions
    'math_square',
    'math_sqrt',
    'math_pow',
    'math_pi',
    'math_sin',
    'math_cos',
    'math_tan',
    'math_asin',
    'math_acos',
    'math_atan',
    'math_atan2',
    'math_degrees',
    'math_radians',
    'math_log',
    'math_log10',
    'math_log2',
    'math_exp',
    # I/O
    'read_file',
    'write_file',
    'append_file',
    'file_exists',
    'read_csv',
    'write_csv',
    # TUI
    'tui_box',
    'tui_line',
    'tui_banner',
    'tui_center_text',
    'tui_pad_text',
    'tui_progress_bar',
    'tui_move_cursor',
    'tui_set_color',
    'tui_reset_color',
    'tui_hide_cursor',
    'tui_show_cursor',
    # System
    'system_sleep',
    'system_poll_key',
    'system_restore_terminal',
    # Serial
    'serial_open',
    'serial_read_line',
    'serial_close',
    # Date and time functions
    'time_now',
    'date_today',
    'date_diff',
    # Registry
    'NATIVE_FUNCTIONS',
]

