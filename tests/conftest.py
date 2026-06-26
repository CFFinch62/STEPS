"""Pytest Configuration and Shared Fixtures for Steps Tests.

This module provides fixtures used across unit, integration,
and end-to-end tests.
"""

import pytest
from pathlib import Path
from typing import Callable, Dict, List, Optional

# Import Steps modules (will be available after we implement them)
# For now, we import what we have
from steps.errors import SourceLocation
from steps.types import (
    StepsValue, StepsNumber, StepsText, StepsBoolean,
    StepsList, StepsTable, StepsNothing, make_value
)


def mock_location(
    file: str = "test.step",
    line: int = 1,
    column: int = 1
) -> SourceLocation:
    """Create a mock source location for testing."""
    return SourceLocation(
        file=Path(file),
        line=line,
        column=column
    )


@pytest.fixture
def location() -> Callable[..., SourceLocation]:
    """Fixture to create source locations."""
    return mock_location


@pytest.fixture
def tmp_project(tmp_path: Path) -> Callable[[str, Dict[str, str]], Path]:
    """Create a temporary Steps project directory.
    
    Usage:
        project = tmp_project("my_project", {
            "my_project.building": "building: my_project\\n    floors:\\n        floor: main\\n            step: hello\\n\\n    exit\\n",
            "main/hello.step": "step: hello\\n    belongs to: main\\n    ..."
        })
    
    Returns the path to the project directory.
    """
    def _create_project(name: str, files: Dict[str, str]) -> Path:
        project_dir = tmp_path / name
        project_dir.mkdir(parents=True, exist_ok=True)
        
        for filepath, content in files.items():
            full_path = project_dir / filepath
            full_path.parent.mkdir(parents=True, exist_ok=True)
            full_path.write_text(content)
        
        return project_dir
    
    return _create_project


@pytest.fixture
def make_steps_value() -> Callable:
    """Fixture to create Steps values from Python values."""
    return make_value


# Test data helpers

def minimal_building(name: str = "test", floors: dict = None) -> str:
    """Return minimal building source code.
    
    Args:
        name: Building name
        floors: Optional dict of {floor_name: [step_names]} for inline declarations
    """
    if floors:
        floors_section = "    floors:\n"
        for floor_name, steps in floors.items():
            floors_section += f"        floor: {floor_name}\n"
            for step in steps:
                floors_section += f"            step: {step}\n"
        return f"""building: {name}

{floors_section}
    exit
"""
    return f"""building: {name}

    exit
"""


def minimal_step(name: str = "test_step", floor: str = "main") -> str:
    """Return minimal step source code."""
    return f"""step: {name}
    belongs to: {floor}
    expects: nothing
    returns: nothing

    do:
        display "hello"
"""


def simple_floor(name: str = "main", steps: Optional[List[str]] = None) -> str:
    """Return simple floor source code."""
    if steps is None:
        steps = ["test_step"]
    
    step_lines = "\n".join(f"    step: {s}" for s in steps)
    return f"""floor: {name}

{step_lines}
"""


@pytest.fixture
def sample_sources() -> Dict[str, Callable[..., str]]:
    """Fixture providing sample source code generators."""
    return {
        "building": minimal_building,
        "step": minimal_step,
        "floor": simple_floor,
    }
