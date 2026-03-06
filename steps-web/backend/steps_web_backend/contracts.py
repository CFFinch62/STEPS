from __future__ import annotations

from dataclasses import asdict, dataclass, field
from typing import Any, Optional

from steps.errors import StepsError


@dataclass
class PlaygroundDiagnostic:
    code: str
    message: str
    file: Optional[str] = None
    line: Optional[int] = None
    column: Optional[int] = None
    hint: str = ""

    @classmethod
    def from_steps_error(cls, error: StepsError) -> "PlaygroundDiagnostic":
        return cls(
            code=error.code,
            message=error.message,
            file=str(error.file) if error.file else None,
            line=error.line,
            column=error.column,
            hint=error.hint,
        )


@dataclass
class PlaygroundRequest:
    step_source: str
    input_lines: list[str] = field(default_factory=list)
    include_wrapper: bool = False


@dataclass
class PlaygroundResponse:
    ok: bool
    mode: str
    output: str = ""
    output_lines: list[str] = field(default_factory=list)
    diagnostics: list[PlaygroundDiagnostic] = field(default_factory=list)
    wrapper_files: dict[str, str] = field(default_factory=dict)
    meta: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        data = asdict(self)
        data["diagnostics"] = [asdict(item) for item in self.diagnostics]
        return data