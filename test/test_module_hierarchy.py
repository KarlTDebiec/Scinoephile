#  Copyright 2017-2026 Karl T Debiec. All rights reserved. This software may be modified
#  and distributed under the terms of the BSD license. See the LICENSE file for details.
"""Tests of documented module hierarchy."""

from __future__ import annotations

import ast
from pathlib import Path

from scinoephile.common import package_root

_HIERARCHY_HEADER = "Package hierarchy (modules may import from any above):"


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


def test_hierarchy_declarations_require_standard_heading(tmp_path: Path):
    """Test incidental hierarchy prose is not parsed as a declaration."""
    package_dir_path = tmp_path / "example"
    package_dir_path.mkdir()
    init_path = package_dir_path / "__init__.py"
    init_path.write_text(
        '"""Example package.\n\nHierarchy notes:\n* child\n"""\n',
        encoding="utf-8",
    )
    (package_dir_path / "child.py").write_text(
        '"""Child module."""\n',
        encoding="utf-8",
    )

    assert get_module_hierarchy_violations(
        init_path,
        package_parent_path=tmp_path,
    ) == ["example/__init__.py: missing hierarchy block"]


def test_module_hierarchy_docs_are_authoritative():
    """Test package imports comply with declared module hierarchies."""
    violations: list[str] = []
    for init_path in sorted(package_root.rglob("__init__.py")):
        violations.extend(get_module_hierarchy_violations(init_path))

    assert not violations, "\n\n".join(violations)


def test_module_import_style_rules(tmp_path: Path):
    """Test import style distinguishes modules, packages, and facades."""
    package_dir_path = tmp_path / "example"
    fixture_sources = {
        "__init__.py": "",
        "shared.py": 'value = "shared"\n',
        "core/__init__.py": (
            "from .errors import PublicError\n\n"
            "class HiddenError(Exception):\n"
            "    pass\n\n"
            '__all__ = ["PublicError"]\n'
        ),
        "core/errors.py": (
            'class PublicError(Exception):\n    pass\n\n__all__ = ["PublicError"]\n'
        ),
        "core/llms/__init__.py": "",
        "feature/__init__.py": "",
        "feature/prompts.py": "FIELDS = {}\n",
        "feature/sibling/__init__.py": (
            "class HiddenSibling:\n"
            "    pass\n\n"
            "class Sibling:\n"
            "    pass\n\n"
            '__all__ = ["Sibling"]\n'
        ),
        "feature/sibling/models.py": "MODEL = object()\n",
    }
    for relative_path, source in fixture_sources.items():
        file_path = package_dir_path / relative_path
        file_path.parent.mkdir(parents=True, exist_ok=True)
        file_path.write_text(source, encoding="utf-8")

    cases = [
        ("feature/local_relative.py", "from .prompts import FIELDS\n", None),
        (
            "feature/local_absolute.py",
            "from example.feature.prompts import FIELDS\n",
            "imports rooted in the current package must be relative",
        ),
        (
            "feature/local_absolute_plain.py",
            "import example.feature.prompts\n",
            "imports rooted in the current package must be relative",
        ),
        ("feature/parent_absolute.py", "from example.shared import value\n", None),
        ("feature/parent_absolute_plain.py", "import example.shared\n", None),
        (
            "feature/parent_relative.py",
            "from ..shared import value\n",
            "relative imports may not climb to parent packages",
        ),
        (
            "feature/sibling_absolute.py",
            "from example.feature.sibling import Sibling\n",
            "imports rooted in the current package must be relative",
        ),
        (
            "feature/sibling_relative.py",
            "from .sibling import Sibling\n",
            None,
        ),
        (
            "feature/sibling_module_relative.py",
            "from .sibling.models import MODEL\n",
            None,
        ),
        (
            "feature/sibling_module_absolute.py",
            "from example.feature.sibling.models import MODEL\n",
            "imports rooted in the current package must be relative",
        ),
        (
            "feature/sibling_private_relative.py",
            "from .sibling import HiddenSibling\n",
            "package facade imports must name exports listed in __all__",
        ),
        (
            "feature/child_alias_relative.py",
            "from . import sibling\n",
            None,
        ),
        (
            "feature/child_alias_absolute.py",
            "from example.feature import sibling\n",
            "imports rooted in the current package must be relative",
        ),
        (
            "feature/public_facade.py",
            "from example.core import PublicError\n",
            None,
        ),
        (
            "feature/private_facade.py",
            "from example.core import HiddenError\n",
            "package facade imports must name exports listed in __all__",
        ),
        (
            "core/llms/concrete.py",
            "from example.core.errors import PublicError\n",
            None,
        ),
        (
            "core/llms/ancestor_facade.py",
            "from example.core import PublicError\n",
            "own ancestor package facades may not be used internally",
        ),
        (
            "core/llms/ancestor_facade_plain.py",
            "import example.core\n",
            "own ancestor package facades may not be used internally",
        ),
    ]
    for relative_path, source, expected_reason in cases:
        file_path = package_dir_path / relative_path
        file_path.write_text(source, encoding="utf-8")
        violations = get_import_style_violations(
            file_path,
            package_parent_path=tmp_path,
        )
        if expected_reason is None:
            assert violations == []
        else:
            assert len(violations) == 1
            assert expected_reason in violations[0]


def test_module_imports_follow_style_rules():
    """Test package imports make their concrete dependencies visible."""
    violations: list[str] = []
    for file_path in sorted(package_root.rglob("*.py")):
        violations.extend(get_import_style_violations(file_path))

    assert not violations, "\n".join(violations)


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
            if stripped_line == _HIERARCHY_HEADER:
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


def format_import_style_violation(
    file_path: Path,
    node: ast.Import | ast.ImportFrom,
    reason: str,
    *,
    package_parent_path: Path = package_root.parent,
) -> str:
    """Format one package import style violation.

    Arguments:
        file_path: Python file path
        node: import node
        reason: violation reason
        package_parent_path: parent path from which the package name begins
    Returns:
        formatted violation description
    """
    return (
        f"{file_path.relative_to(package_parent_path)}:{node.lineno}: {reason}: "
        f"{ast.unparse(node)}"
    )


def get_absolute_import_from_style_violations(
    file_path: Path,
    node: ast.ImportFrom,
    current_package_parts: list[str],
    root_package_name: str,
    *,
    package_parent_path: Path = package_root.parent,
) -> list[str]:
    """Get style violations from one absolute import-from statement.

    Arguments:
        file_path: Python file path
        node: absolute import-from node
        current_package_parts: dotted parts of the importing package
        root_package_name: source root package name
        package_parent_path: parent path from which the package name begins
    Returns:
        violation descriptions
    """
    module_name = node.module
    if module_name is None or not (
        module_name == root_package_name
        or module_name.startswith(f"{root_package_name}.")
    ):
        return []

    current_package_name = ".".join(current_package_parts)
    if module_name.startswith(f"{current_package_name}."):
        return [
            format_import_style_violation(
                file_path,
                node,
                "imports rooted in the current package must be relative",
                package_parent_path=package_parent_path,
            )
        ]

    target_path = get_module_source_path(
        module_name,
        package_parent_path=package_parent_path,
    )
    if target_path is None:
        return []
    if target_path.name != "__init__.py":
        return []

    target_module_parts = module_name.split(".")
    target_is_ancestor = (
        target_module_parts == current_package_parts[: len(target_module_parts)]
    )
    package_exports = get_package_exports(target_path)
    violations: list[str] = []
    for alias in node.names:
        child_target_path = get_module_source_path(
            f"{module_name}.{alias.name}",
            package_parent_path=package_parent_path,
        )
        if child_target_path is not None:
            if module_name == current_package_name:
                violations.append(
                    format_import_style_violation(
                        file_path,
                        node,
                        "imports rooted in the current package must be relative",
                        package_parent_path=package_parent_path,
                    )
                )
            continue
        if target_is_ancestor:
            violations.append(
                format_import_style_violation(
                    file_path,
                    node,
                    "own ancestor package facades may not be used internally",
                    package_parent_path=package_parent_path,
                )
            )
        elif package_exports is None or alias.name not in package_exports:
            violations.append(
                format_import_style_violation(
                    file_path,
                    node,
                    "package facade imports must name exports listed in __all__",
                    package_parent_path=package_parent_path,
                )
            )
    return violations


def get_absolute_import_style_violations(
    file_path: Path,
    node: ast.Import,
    current_package_parts: list[str],
    root_package_name: str,
    *,
    package_parent_path: Path = package_root.parent,
) -> list[str]:
    """Get style violations from one absolute import statement.

    Arguments:
        file_path: Python file path
        node: absolute import node
        current_package_parts: dotted parts of the importing package
        root_package_name: source root package name
        package_parent_path: parent path from which the package name begins
    Returns:
        violation descriptions
    """
    violations: list[str] = []
    current_package_name = ".".join(current_package_parts)
    for alias in node.names:
        if not (
            alias.name == root_package_name
            or alias.name.startswith(f"{root_package_name}.")
        ):
            continue

        if alias.name.startswith(f"{current_package_name}."):
            violations.append(
                format_import_style_violation(
                    file_path,
                    node,
                    "imports rooted in the current package must be relative",
                    package_parent_path=package_parent_path,
                )
            )
            continue

        target_path = get_module_source_path(
            alias.name,
            package_parent_path=package_parent_path,
        )
        if target_path is None:
            continue

        target_module_parts = alias.name.split(".")
        if (
            target_path.name == "__init__.py"
            and target_module_parts
            == (current_package_parts[: len(target_module_parts)])
        ):
            violations.append(
                format_import_style_violation(
                    file_path,
                    node,
                    "own ancestor package facades may not be used internally",
                    package_parent_path=package_parent_path,
                )
            )
    return violations


def get_import_style_violations(
    file_path: Path,
    *,
    package_parent_path: Path = package_root.parent,
) -> list[str]:
    """Get violations of package import style rules in one Python file.

    Arguments:
        file_path: Python file path
        package_parent_path: parent path from which the package name begins
    Returns:
        violation descriptions
    """
    relative_path = file_path.relative_to(package_parent_path)
    current_package_parts = list(relative_path.parent.parts)
    root_package_name = current_package_parts[0]
    tree = ast.parse(file_path.read_text(encoding="utf-8"))
    violations: list[str] = []

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            violations.extend(
                get_absolute_import_style_violations(
                    file_path,
                    node,
                    current_package_parts,
                    root_package_name,
                    package_parent_path=package_parent_path,
                )
            )
            continue

        if isinstance(node, ast.ImportFrom):
            if node.level:
                violations.extend(
                    get_relative_import_style_violations(
                        file_path,
                        node,
                        current_package_parts,
                        package_parent_path=package_parent_path,
                    )
                )
            else:
                violations.extend(
                    get_absolute_import_from_style_violations(
                        file_path,
                        node,
                        current_package_parts,
                        root_package_name,
                        package_parent_path=package_parent_path,
                    )
                )
    return violations


def get_relative_import_style_violations(
    file_path: Path,
    node: ast.ImportFrom,
    current_package_parts: list[str],
    *,
    package_parent_path: Path = package_root.parent,
) -> list[str]:
    """Get style violations from one relative import-from statement.

    Arguments:
        file_path: Python file path
        node: relative import-from node
        current_package_parts: dotted parts of the importing package
        package_parent_path: parent path from which the package name begins
    Returns:
        violation descriptions
    """
    current_package_name = ".".join(current_package_parts)
    if node.level != 1:
        return [
            format_import_style_violation(
                file_path,
                node,
                "relative imports may not climb to parent packages",
                package_parent_path=package_parent_path,
            )
        ]

    target_module_name = current_package_name
    if node.module:
        target_module_name = f"{target_module_name}.{node.module}"
    target_path = get_module_source_path(
        target_module_name,
        package_parent_path=package_parent_path,
    )
    package_exports: set[str] | None = None
    if target_path is not None and target_path.name == "__init__.py":
        package_exports = get_package_exports(target_path)

    violations: list[str] = []
    for alias in node.names:
        child_target_path = get_module_source_path(
            f"{target_module_name}.{alias.name}",
            package_parent_path=package_parent_path,
        )
        if child_target_path is not None:
            continue
        if target_path is None or target_path.name != "__init__.py":
            continue
        if package_exports is None or alias.name not in package_exports:
            violations.append(
                format_import_style_violation(
                    file_path,
                    node,
                    "package facade imports must name exports listed in __all__",
                    package_parent_path=package_parent_path,
                )
            )
    return violations


def get_module_source_path(
    module_name: str,
    *,
    package_parent_path: Path = package_root.parent,
) -> Path | None:
    """Get the source path for an importable module or package.

    Arguments:
        module_name: absolute dotted module name
        package_parent_path: parent path from which the package name begins
    Returns:
        module file or package `__init__.py` path, if present
    """
    target_path = package_parent_path.joinpath(*module_name.split("."))
    module_path = target_path.with_suffix(".py")
    if module_path.exists():
        return module_path

    init_path = target_path / "__init__.py"
    if init_path.exists():
        return init_path
    return None


def get_package_exports(init_path: Path) -> set[str] | None:
    """Get literal public exports declared by a package.

    Arguments:
        init_path: package `__init__.py` path
    Returns:
        public export names, or None if no literal `__all__` is declared
    """
    tree = ast.parse(init_path.read_text(encoding="utf-8"))
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id == "__all__"
            for target in node.targets
        ):
            continue
        if not isinstance(node.value, (ast.List, ast.Tuple, ast.Set)):
            return None
        exports: set[str] = set()
        for element in node.value.elts:
            if not isinstance(element, ast.Constant) or not isinstance(
                element.value, str
            ):
                return None
            exports.add(element.value)
        return exports
    return None


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
