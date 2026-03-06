from __future__ import annotations

from pathlib import Path

PLAYGROUND_NAME = "playground"
PLAYGROUND_STEP_NAME = "main"


def normalize_step_source(source: str) -> str:
    cleaned = source.replace("\r\n", "\n").strip("\ufeff\n")
    if not cleaned:
        raise ValueError("PLAY001: step_source is required.")

    lines = cleaned.split("\n")
    if lines[0].strip() != f"step: {PLAYGROUND_STEP_NAME}":
        raise ValueError("PLAY002: the editor must start with `step: main`.")

    rebuilt = [f"step: {PLAYGROUND_STEP_NAME}", f"    belongs to: {PLAYGROUND_NAME}"]
    for line in lines[1:]:
        stripped = line.strip().lower()
        is_top_level_belongs = (
            line.startswith("    ")
            and not line.startswith("        ")
            and stripped.startswith("belongs to:")
        )
        if not is_top_level_belongs:
            rebuilt.append(line)

    return "\n".join(rebuilt).rstrip() + "\n"


def build_wrapper_files(step_source: str) -> dict[str, str]:
    normalized_step = normalize_step_source(step_source)
    return {
        f"{PLAYGROUND_NAME}.building": (
            f"building: {PLAYGROUND_NAME}\n"
            f"    call {PLAYGROUND_STEP_NAME}\n"
            "    exit\n"
        ),
        f"{PLAYGROUND_NAME}/{PLAYGROUND_NAME}.floor": (
            f"floor: {PLAYGROUND_NAME}\n"
            f"    step: {PLAYGROUND_STEP_NAME}\n"
        ),
        f"{PLAYGROUND_NAME}/{PLAYGROUND_STEP_NAME}.step": normalized_step,
    }


def write_wrapper_files(project_dir: Path, files: dict[str, str]) -> None:
    for relative_path, content in files.items():
        file_path = project_dir / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(content, encoding="utf-8")