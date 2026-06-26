"""Steps Loader - Project Discovery and File Loading.

The loader is responsible for:
- Discovering Steps project structure
- Loading and parsing building, floor, and step files
- Validating project structure
- Registering all components with the environment
"""

from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple, Union, cast

from .ast_nodes import BuildingNode, FloorNode, StepNode, RiserNode
from .environment import Environment, StepDefinition, RiserDefinition, FloorDefinition
from .errors import StepsError, StructureError, ErrorCode, SourceLocation
from .lexer import Lexer
from .parser import Parser, ParseResult


@dataclass
class LoadResult:
    """Result of loading a Steps project."""
    success: bool
    building: Optional[BuildingNode] = None
    errors: List[StepsError] = field(default_factory=list)

    def add_error(self, error: StepsError) -> None:
        self.errors.append(error)
        self.success = False


class Loader:
    """Loads Steps projects from the filesystem.
    
    A Steps project has the following structure:
    
    project_name/
    ├── project_name.building    # Entry point (includes floor declarations)
    ├── floor_one/
    │   ├── step_a.step
    │   └── step_b.step
    └── floor_two/
        └── step_c.step
    
    Floor declarations are specified in the building file via a 'floors:' section.
    If no 'floors:' section is present, step files are auto-discovered from
    subdirectories using the directory name as the floor name.
    """
    
    def __init__(self, project_path: Path):
        """Initialize the loader.
        
        Args:
            project_path: Path to the project directory
        """
        self.project_path = Path(project_path).resolve()
        self.errors: List[Exception] = []
    
    def load(self, environment: Environment) -> LoadResult:
        """Load the entire project into the environment.
        
        Args:
            environment: The environment to populate
        
        Returns:
            LoadResult with the building AST and any errors
        """
        result = LoadResult(success=True)
        
        # Validate project directory exists
        if not self.project_path.exists():
            result.add_error(StructureError(
                code=ErrorCode.E001,
                message=f"Project directory '{self.project_path}' does not exist.",
                file=self.project_path,
                line=0,
                column=0,
                hint="Check that the path is correct and the directory exists."
            ))
            return result
        
        if not self.project_path.is_dir():
            result.add_error(StructureError(
                code=ErrorCode.E001,
                message=f"'{self.project_path}' is not a directory.",
                file=self.project_path,
                line=0,
                column=0,
                hint="Steps projects must be directories, not single files."
            ))
            return result
        
        # Find the building file
        building_name = self.project_path.name
        building_file = self.project_path / f"{building_name}.building"
        
        if not building_file.exists():
            # Try to find any .building file
            building_files = list(self.project_path.glob("*.building"))
            if building_files:
                building_file = building_files[0]
                building_name = building_file.stem
            else:
                result.add_error(StructureError(
                    code=ErrorCode.E002,
                    message=f"No building file found in '{self.project_path}'.",
                    file=self.project_path,
                    line=0,
                    column=0,
                    hint=f"Create a file named '{building_name}.building' in the project directory."
                ))
                return result
        
        # Load the building file
        building_result = self._load_building(building_file)
        if not building_result.success:
            for error in building_result.errors:
                result.add_error(error)
            return result
        
        # Type narrow: at this point ast is BuildingNode since success is True
        building_node = cast(BuildingNode, building_result.ast)
        environment.building_name = building_node.name

        # Load standard library first (project floors can override)
        self._load_stdlib(environment)

        # Load floors and steps
        if building_node.floors:
            # Use explicit floor declarations from the building file
            for floor_node in building_node.floors:
                floor_dir = self.project_path / floor_node.name
                self._register_floor_and_steps(
                    floor_node, floor_dir, building_file, environment, result
                )
        else:
            # Auto-discover: scan subdirectories for .step files
            self._auto_discover_floors(environment, result)

        result.building = building_node
        return result
    
    def _register_floor_and_steps(
        self,
        floor_node: FloorNode,
        floor_dir: Path,
        building_file: Path,
        environment: Environment,
        result: LoadResult
    ) -> None:
        """Register a floor and load all its step files.
        
        Args:
            floor_node: The parsed floor declaration
            floor_dir: Directory containing the step files
            building_file: Path to the building file (for error reporting)
            environment: The environment to register into
            result: LoadResult for error accumulation
        """
        # Register the floor
        floor_def = FloorDefinition(
            name=floor_node.name,
            steps=floor_node.steps,
            file_path=building_file
        )
        environment.register_floor(floor_def)

        # Load each step file
        for step_name in floor_node.steps:
            step_file = floor_dir / f"{step_name}.step"
            if not step_file.exists():
                result.add_error(StructureError(
                    code=ErrorCode.E003,
                    message=f"Step file '{step_name}.step' not found in floor '{floor_node.name}'.",
                    file=building_file,
                    line=0,
                    column=0,
                    hint=f"Create the file '{step_file}' or remove '{step_name}' from the floor definition."
                ))
                continue
            
            step_result = self._load_step(step_file, environment)
            if not step_result.success:
                for error in step_result.errors:
                    result.add_error(error)
    
    def _auto_discover_floors(
        self,
        environment: Environment,
        result: LoadResult
    ) -> None:
        """Auto-discover floors by scanning subdirectories for .step files.
        
        Each subdirectory that contains .step files becomes a floor.
        Step files' 'belongs to:' declarations are used for floor assignment.
        """
        floor_dirs = sorted(
            d for d in self.project_path.iterdir()
            if d.is_dir() and not d.name.startswith('.')
        )
        
        for floor_dir in floor_dirs:
            step_files = sorted(floor_dir.glob("*.step"))
            if not step_files:
                continue
            
            floor_name = floor_dir.name
            step_names = [sf.stem for sf in step_files]
            
            # Register the floor
            floor_def = FloorDefinition(
                name=floor_name,
                steps=step_names,
                file_path=self.project_path / f"{self.project_path.name}.building"
            )
            environment.register_floor(floor_def)
            
            # Load each step
            for step_file in step_files:
                step_result = self._load_step(step_file, environment)
                if not step_result.success:
                    for error in step_result.errors:
                        result.add_error(error)
    
    def _get_stdlib_path(self) -> Path:
        """Get path to the bundled standard library."""
        return Path(__file__).parent / "stdlib"
    
    def _load_stdlib(self, environment: Environment) -> None:
        """Load the standard library floors.
        
        The stdlib is loaded first, so project floors can override
        stdlib definitions if they use the same names.
        
        Uses auto-discovery: each subdirectory becomes a floor,
        and all .step files within are registered as steps.
        """
        stdlib_path = self._get_stdlib_path()
        if not stdlib_path.exists():
            return  # No stdlib bundled, that's okay
        
        # Load each floor in stdlib via auto-discovery
        for floor_dir in sorted(stdlib_path.iterdir()):
            if not floor_dir.is_dir():
                continue
            
            step_files = sorted(floor_dir.glob("*.step"))
            if not step_files:
                continue
            
            floor_name = floor_dir.name
            step_names = [sf.stem for sf in step_files]
            
            # Register the floor
            floor_def = FloorDefinition(
                name=floor_name,
                steps=step_names,
                file_path=floor_dir
            )
            environment.register_floor(floor_def)
            
            # Silently load each step (no error propagation for stdlib)
            for step_file in step_files:
                self._load_step(step_file, environment)

    
    def _load_building(self, path: Path) -> ParseResult:
        """Load and parse a building file."""
        try:
            source = path.read_text(encoding='utf-8')
        except IOError as e:
            return ParseResult(
                ast=None,
                errors=[StructureError(
                    code=ErrorCode.E001,
                    message=f"Could not read building file: {e}",
                    file=path,
                    line=0,
                    column=0,
                    hint="Check file permissions and encoding."
                )]
            )
        
        lexer = Lexer(source, path)
        try:
            tokens = lexer.tokenize()
        except StepsError as e:
            return ParseResult(ast=None, errors=[e])
        except Exception as e:
            return ParseResult(ast=None, errors=[StructureError(
                code=ErrorCode.E001,
                message=f"Lexer error: {e}",
                file=path,
                line=0,
                column=0,
                hint="Check the file syntax."
            )])
        
        parser = Parser(tokens, path)
        return parser.parse_building()
    
    def _load_step(self, step_file: Path, environment: Environment) -> LoadResult:
        """Load and register a step."""
        result = LoadResult(success=True)
        
        try:
            source = step_file.read_text(encoding='utf-8')
        except IOError as e:
            result.add_error(StructureError(
                code=ErrorCode.E001,
                message=f"Could not read step file: {e}",
                file=step_file,
                line=0,
                column=0,
                hint="Check file permissions and encoding."
            ))
            return result
        
        lexer = Lexer(source, step_file)
        try:
            tokens = lexer.tokenize()
        except StepsError as e:
            result.add_error(e)
            return result
        except Exception as e:
            result.add_error(StructureError(
                code=ErrorCode.E001,
                message=f"Lexer error: {e}",
                file=step_file,
                line=0,
                column=0,
                hint="Check the file syntax."
            ))
            return result
        
        parser = Parser(tokens, step_file)
        parse_result = parser.parse_step()
        
        if not parse_result.success:
            for error in parse_result.errors:
                result.add_error(error)
            return result

        # Type narrow: at this point ast is StepNode since success is True
        step_node = cast(StepNode, parse_result.ast)

        # Convert risers to RiserDefinitions
        risers: Dict[str, RiserDefinition] = {}
        for riser in step_node.risers:
            risers[riser.name] = RiserDefinition(
                name=riser.name,
                parameters=[p.name for p in riser.expects],
                returns=riser.returns.name if riser.returns else None,
                declarations=riser.declarations,
                body=riser.body
            )
        
        # Register the step
        step_def = StepDefinition(
            name=step_node.name,
            belongs_to=step_node.belongs_to,
            parameters=[p.name for p in step_node.expects],
            returns=step_node.returns.name if step_node.returns else None,
            body=step_node.body,
            declarations=step_node.declarations,  # Include declarations from the step
            risers=risers,
            file_path=step_file
        )
        environment.register_step(step_def)
        
        return result


def load_project(project_path: Path) -> Tuple[Optional[BuildingNode], Environment, List[StepsError]]:
    """Convenience function to load a Steps project.

    Args:
        project_path: Path to the project directory

    Returns:
        Tuple of (building AST, environment, errors)
    """
    environment = Environment()
    loader = Loader(project_path)
    result = loader.load(environment)

    return result.building, environment, result.errors


def load_building_source(source: str, name: str = "main") -> Tuple[Optional[BuildingNode], List[StepsError]]:
    """Load a building from source code (for testing/REPL).

    Args:
        source: Building source code
        name: Building name

    Returns:
        Tuple of (building AST, errors)
    """
    from .parser import parse_building

    result = parse_building(source, Path(f"{name}.building"))
    # Cast is safe because parse_building returns a BuildingNode when successful
    building = cast(Optional[BuildingNode], result.ast) if result.success else None
    return building, list(result.errors)
