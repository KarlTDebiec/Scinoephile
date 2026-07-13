#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of documented module hierarchy."""

from __future__ import annotations

import ast
from pathlib import Path

from scinoephile.common import package_root


def test_declared_module_hierarchy_may_be_stricter_than_import_graph(tmp_path: Path):
    """Test declared hierarchy need not be compacted to current imports."""
    package_dir_path = tmp_path / "example"
    package_dir_path.mkdir()
    init_path = package_dir_path / "__init__.py"
    init_path.write_text(
        '"""Example package.\n\n'
        "Package hierarchy (modules may import from any above):\n"
        "* foundation\n"
        "* feature\n"
        '"""\n',
        encoding="utf-8",
    )
    (package_dir_path / "feature.py").write_text(
        '"""Feature module with no current dependency on foundation."""\n',
        encoding="utf-8",
    )
    (package_dir_path / "foundation.py").write_text(
        '"""Foundation module."""\n',
        encoding="utf-8",
    )

    assert (
        get_module_hierarchy_violations(
            init_path,
            package_parent_path=tmp_path,
        )
        == []
    )


def test_module_hierarchy_docs_are_authoritative():
    """Test package imports comply with declared module hierarchies."""
    violations: list[str] = []
    for init_path in sorted(package_root.rglob("__init__.py")):
        violations.extend(get_module_hierarchy_violations(init_path))

    assert not violations, "\n\n".join(violations)


def test_resolve_import_from_modules_includes_absolute_package_aliases():
    """Test import-from package aliases resolve as candidate modules."""
    node = ast.parse("from scinoephile.core import llms, media").body[0]
    assert isinstance(node, ast.ImportFrom)

    imported_modules = resolve_import_from_modules(
        file_path=package_root / "core/cache/operations.py",
        node=node,
        root_package_parts=["scinoephile", "core"],
    )

    assert imported_modules == [
        "scinoephile.core",
        "scinoephile.core.llms",
        "scinoephile.core.media",
    ]


def test_resolve_import_from_modules_includes_relative_package_aliases():
    """Test relative import-from package aliases resolve as candidate modules."""
    node = ast.parse("from . import operations").body[0]
    assert isinstance(node, ast.ImportFrom)

    imported_modules = resolve_import_from_modules(
        file_path=package_root / "core/cache/cache_entry.py",
        node=node,
        root_package_parts=["scinoephile", "core", "cache"],
    )

    assert imported_modules == [
        "scinoephile.core.cache",
        "scinoephile.core.cache.operations",
    ]


def test_single_child_package_requires_hierarchy(tmp_path: Path):
    """Test packages with one child still require a hierarchy declaration."""
    package_dir_path = tmp_path / "example"
    package_dir_path.mkdir()
    init_path = package_dir_path / "__init__.py"
    init_path.write_text('"""Example package."""\n', encoding="utf-8")
    (package_dir_path / "child.py").write_text(
        '"""Child module."""\n',
        encoding="utf-8",
    )

    assert get_module_hierarchy_violations(
        init_path,
        package_parent_path=tmp_path,
    ) == ["example/__init__.py: missing hierarchy block"]


def get_child_names(package_dir_path: Path) -> list[str]:
    """Get direct child module and package names.

    Arguments:
        package_dir_path: package directory path
    Returns:
        sorted direct child names
    """
    child_names: list[str] = []
    for child_path in package_dir_path.iterdir():
        if child_path.name == "__init__.py":
            continue
        if child_path.is_file() and child_path.suffix == ".py":
            child_names.append(child_path.stem)
        elif child_path.is_dir() and (child_path / "__init__.py").exists():
            child_names.append(child_path.name)
    return sorted(child_names)


def get_package_dotted(
    package_dir_path: Path,
    *,
    package_parent_path: Path = package_root.parent,
) -> str:
    """Get dotted package name for a package directory.

    Arguments:
        package_dir_path: package directory path
        package_parent_path: parent path from which the package name begins
    Returns:
        dotted package name
    """
    return ".".join(package_dir_path.relative_to(package_parent_path).parts)


def get_documented_levels(init_path: Path) -> dict[int, list[str]] | None:
    """Get documented module hierarchy levels from a package docstring.

    Arguments:
        init_path: package `__init__.py` path
    Returns:
        documented hierarchy levels, or None if no hierarchy block is present
    """
    tree = ast.parse(init_path.read_text(encoding="utf-8"))
    docstring = ast.get_docstring(tree)
    if docstring is None:
        return None

    levels: dict[int, list[str]] = {}
    hierarchy_seen = False
    current_level: list[str] | None = None
    for line in docstring.splitlines():
        stripped_line = line.strip()
        if not hierarchy_seen:
            if "hierarchy" in stripped_line.lower():
                hierarchy_seen = True
            continue

        if stripped_line.startswith("* "):
            child_names = parse_hierarchy_line(stripped_line[2:])
            if not child_names:
                continue
            current_level = child_names
            levels[len(levels) + 1] = current_level
        elif current_level is not None and stripped_line.startswith("/ "):
            current_level.extend(parse_hierarchy_line(stripped_line[2:]))
        elif levels and not stripped_line:
            break
        elif levels:
            break

    if not levels:
        return None
    return levels


def parse_hierarchy_line(line: str) -> list[str]:
    """Parse one hierarchy bullet or continuation line.

    Arguments:
        line: hierarchy line
    Returns:
        child names documented on the line
    """
    return [part.strip() for part in line.split(" / ") if part.strip()]


def get_documented_level_violations(
    init_path: Path,
    child_names: list[str],
    documented_levels: dict[int, list[str]],
) -> list[str]:
    """Get violations in the documented hierarchy block itself.

    Arguments:
        init_path: package `__init__.py` path
        child_names: actual direct child names
        documented_levels: documented hierarchy levels
    Returns:
        violation descriptions
    """
    child_name_set = set(child_names)
    documented_names = [
        child_name
        for level_child_names in documented_levels.values()
        for child_name in level_child_names
    ]
    documented_name_set = set(documented_names)
    duplicate_names = sorted(
        {
            child_name
            for child_name in documented_names
            if documented_names.count(child_name) > 1
        }
    )
    missing_names = sorted(child_name_set - documented_name_set)
    extra_names = sorted(documented_name_set - child_name_set)

    violations: list[str] = []
    if duplicate_names:
        violations.append(
            f"{init_path.relative_to(package_root.parent)}: "
            "duplicated hierarchy entries: "
            f"{', '.join(duplicate_names)}"
        )
    if missing_names:
        violations.append(
            f"{init_path.relative_to(package_root.parent)}: "
            "missing hierarchy entries: "
            f"{', '.join(missing_names)}"
        )
    if extra_names:
        violations.append(
            f"{init_path.relative_to(package_root.parent)}: "
            "unknown hierarchy entries: "
            f"{', '.join(extra_names)}"
        )
    return violations


def get_sibling_import_edges(
    package_dir_path: Path,
    package_dotted: str,
    child_names: list[str],
) -> dict[str, set[str]]:
    """Build sibling import edges for a package.

    Arguments:
        package_dir_path: package directory path
        package_dotted: dotted package name
        child_names: direct child names
    Returns:
        map of importer child name to imported sibling child names
    """
    edges: dict[str, set[str]] = {child_name: set() for child_name in child_names}
    child_name_set = set(child_names)
    package_parts = package_dotted.split(".")

    for child_name in child_names:
        child_path = package_dir_path / child_name
        if child_path.is_dir():
            candidate_file_paths = sorted(child_path.rglob("*.py"))
        else:
            candidate_file_paths = [package_dir_path / f"{child_name}.py"]

        for file_path in candidate_file_paths:
            for imported_module in get_imported_modules(file_path, package_parts):
                imported_parts = imported_module.split(".")
                if imported_parts[: len(package_parts)] != package_parts:
                    continue
                if len(imported_parts) <= len(package_parts):
                    continue

                imported_child_name = imported_parts[len(package_parts)]
                if (
                    imported_child_name in child_name_set
                    and imported_child_name != child_name
                ):
                    edges[child_name].add(imported_child_name)

    return edges


def get_imported_modules(file_path: Path, root_package_parts: list[str]) -> list[str]:
    """Get absolute imported module names from one Python file.

    Arguments:
        file_path: Python file path
        root_package_parts: root package path parts
    Returns:
        absolute imported module names
    """
    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    imported_modules: list[str] = []
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imported_modules.extend(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom):
            imported_modules.extend(
                resolve_import_from_modules(
                    file_path=file_path,
                    node=node,
                    root_package_parts=root_package_parts,
                )
            )
    return imported_modules


def get_module_hierarchy_violations(
    init_path: Path,
    *,
    package_parent_path: Path = package_root.parent,
) -> list[str]:
    """Get violations of one package's declared module hierarchy.

    Arguments:
        init_path: package `__init__.py` path
        package_parent_path: parent path from which the package name begins
    Returns:
        violation descriptions
    """
    package_dir_path = init_path.parent
    child_names = get_child_names(package_dir_path)
    if not child_names:
        return []

    documented_levels = get_documented_levels(init_path)
    if documented_levels is None:
        return [
            f"{init_path.relative_to(package_parent_path)}: missing hierarchy block"
        ]

    violations = get_documented_level_violations(
        init_path=init_path,
        child_names=child_names,
        documented_levels=documented_levels,
    )
    if violations:
        return violations

    edges = get_sibling_import_edges(
        package_dir_path=package_dir_path,
        package_dotted=get_package_dotted(
            package_dir_path,
            package_parent_path=package_parent_path,
        ),
        child_names=child_names,
    )
    documented_level_by_child = {
        child_name: level
        for level, level_child_names in documented_levels.items()
        for child_name in level_child_names
    }
    violations.extend(
        get_import_order_violations(
            init_path=init_path,
            documented_level_by_child=documented_level_by_child,
            edges=edges,
        )
    )
    violations.extend(get_cycle_violations(init_path=init_path, edges=edges))
    return violations


def resolve_import_from_modules(
    file_path: Path,
    node: ast.ImportFrom,
    root_package_parts: list[str],
) -> list[str]:
    """Resolve an `ImportFrom` node to absolute module name candidates.

    Arguments:
        file_path: Python file path
        node: import-from node
        root_package_parts: root package path parts
    Returns:
        absolute module name candidates
    """
    if node.level == 0:
        if node.module is None:
            return []
        imported_module = node.module
    else:
        file_package_parts = get_file_package_parts(file_path)
        absolute_parent_len = len(file_package_parts) - node.level + 1
        if absolute_parent_len < len(root_package_parts):
            return []

        imported_parts = file_package_parts[:absolute_parent_len]
        if node.module:
            imported_parts.extend(node.module.split("."))
        imported_module = ".".join(imported_parts)

    imported_modules = [imported_module]
    imported_modules.extend(
        f"{imported_module}.{alias.name}" for alias in node.names if alias.name != "*"
    )
    return imported_modules


def get_file_package_parts(file_path: Path) -> list[str]:
    """Get the dotted package parts containing a Python file.

    Arguments:
        file_path: Python file path
    Returns:
        package name parts
    """
    relative_path = file_path.relative_to(package_root.parent)
    if file_path.name == "__init__.py":
        return list(relative_path.parent.parts)
    return list(relative_path.parent.parts)


def get_import_order_violations(
    init_path: Path,
    documented_level_by_child: dict[str, int],
    edges: dict[str, set[str]],
) -> list[str]:
    """Get hierarchy order violations for import edges.

    Arguments:
        init_path: package `__init__.py` path
        documented_level_by_child: documented level by child name
        edges: sibling import edges
    Returns:
        violation descriptions
    """
    violations: list[str] = []
    for importer_name, imported_names in sorted(edges.items()):
        importer_level = documented_level_by_child[importer_name]
        for imported_name in sorted(imported_names):
            imported_level = documented_level_by_child[imported_name]
            if importer_level <= imported_level:
                violations.append(
                    f"{init_path.relative_to(package_root.parent)}: "
                    f"{importer_name} imports {imported_name}, but "
                    f"{importer_name} is level {importer_level} and "
                    f"{imported_name} is level {imported_level}"
                )
    return violations


def get_cycle_violations(init_path: Path, edges: dict[str, set[str]]) -> list[str]:
    """Get import cycle violations.

    Arguments:
        init_path: package `__init__.py` path
        edges: sibling import edges
    Returns:
        violation descriptions
    """
    visited: set[str] = set()
    active: list[str] = []
    active_set: set[str] = set()
    cycles: set[tuple[str, ...]] = set()

    def visit(child_name: str):
        """Visit one child while tracking the active dependency stack.

        Arguments:
            child_name: child module or package name
        """
        visited.add(child_name)
        active.append(child_name)
        active_set.add(child_name)

        for imported_name in sorted(edges[child_name]):
            if imported_name in active_set:
                cycle_start_idx = active.index(imported_name)
                cycles.add(tuple(active[cycle_start_idx:] + [imported_name]))
            elif imported_name not in visited:
                visit(imported_name)

        active.pop()
        active_set.remove(child_name)

    for child_name in sorted(edges):
        if child_name not in visited:
            visit(child_name)

    return [
        f"{init_path.relative_to(package_root.parent)}: "
        f"import cycle: {' -> '.join(cycle)}"
        for cycle in sorted(cycles)
    ]
