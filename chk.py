import ast
import importlib.util
import re
import subprocess
import sys
from pathlib import Path

IGNORE_DIRS = {"venv", "__pycache__", ".git", "node_modules"}


def short_path(path, base):
    return str(Path(path).relative_to(base))


def auto_fix_code():
    print("🔧 Auto-fixing code with autopep8, autoflake, isort, black...\n")
    subprocess.run(
        ["autopep8", "--in-place", "--recursive", "--aggressive", "--aggressive", "."],
        check=True,
    )
    subprocess.run(
        [
            "autoflake",
            "--in-place",
            "--recursive",
            "--remove-all-unused-imports",
            "--remove-unused-variables",
            "--ignore-init-module-imports",
            ".",
        ],
        check=True,
    )
    subprocess.run(["isort", "."], check=True)
    subprocess.run(["black", "--fast", "."], check=True)
    print("✅ Auto-fix completed.\n")


def check_syntax(file_path, base_path):
    try:
        with open(file_path, "r", encoding="utf-8") as file:
            source = file.read()
        ast.parse(source, filename=file_path)
        return None
    except SyntaxError as e:
        return f"[SyntaxError] {
            short_path(
                file_path,
                base_path)}:{
            e.lineno} - {
                e.msg}"


def check_imports(file_path, base_path):
    errors = []
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            tree = ast.parse(f.read(), filename=file_path)
    except Exception:
        return []

    short = short_path(file_path, base_path)

    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                if not module_exists(alias.name, base_path):
                    errors.append(
                        f"[ImportError] {short}:{node.lineno} - Cannot import '{alias.name}'"
                    )
        elif isinstance(node, ast.ImportFrom):
            module = node.module
            level = node.level
            full_module = resolve_relative_import(file_path, base_path, level, module)
            if full_module and not module_exists(full_module, base_path):
                errors.append(
                    f"[ImportError] {short}:{
                        node.lineno} - Cannot import from '{full_module}'"
                )
    return errors


def resolve_relative_import(file_path, base_path, level, module):
    rel_path = Path(file_path).relative_to(base_path)
    parent_parts = rel_path.parts[:-level]
    if module:
        parts = parent_parts + tuple(module.split("."))
    else:
        parts = parent_parts
    return ".".join(parts)


def module_exists(module_name, base_path):
    try:
        if str(base_path) not in sys.path:
            sys.path.insert(0, str(base_path))
        return importlib.util.find_spec(module_name) is not None
    except Exception:
        return False


def clean_flake8_line(line, base_path):
    parts = line.split(":")
    if len(parts) >= 3:
        file_path, lineno, *_ = parts
        short = short_path(file_path, base_path)
        msg = ":".join(parts[3:]).strip()
        msg = " ".join(msg.split()[1:])  # Remove code like "F821"
        return f"[flake8] {short}:{lineno} - {msg}"
    return line.strip()


def check_with_flake8(repo_path):
    try:
        result = subprocess.run(
            ["flake8", "--ignore=E501,W503,E302,E305", str(repo_path)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        output = result.stdout.strip()
        if output:
            return [clean_flake8_line(line, repo_path) for line in output.splitlines()]
        return []
    except FileNotFoundError:
        return ["[flake8] ERROR - flake8 not installed. Run 'pip install flake8'."]
    except Exception as e:
        return [f"[flake8] ERROR - {str(e)}"]


def fix_fstrings_without_placeholders(repo_path):
    print("🔧 Fixing f-strings missing placeholders...\n")
    # matches "..." or '...'
    fstring_pattern = re.compile(r'(f)(["\'])(.*?)(\2)')

    for py_file in Path(repo_path).rglob("*.py"):
        if any(part in IGNORE_DIRS for part in py_file.parts):
            continue

        changed = False
        lines = py_file.read_text(encoding="utf-8").splitlines()

        for i, line in enumerate(lines):
            # Search all f-strings in the line
            matches = list(fstring_pattern.finditer(line))
            new_line = line
            for m in reversed(matches):  # reverse to not mess up indices if multiple
                f_prefix, quote, content, _ = m.groups()
                # If no braces {}, remove leading f
                if "{" not in content and "}" not in content:
                    start, end = m.span(1)  # span of the "f"
                    new_line = new_line[:start] + new_line[start + 1 :]
                    changed = True
            lines[i] = new_line

        if changed:
            py_file.write_text("\n".join(lines), encoding="utf-8")
            print(f"Fixed f-string in: {py_file.relative_to(repo_path)}")

    print("✅ f-string fix done.\n")


def scan_repo(repo_path):
    repo_path = Path(repo_path).resolve()
    print(f"🔍 Scanning Python files in: {repo_path.name}/\n")

    errors = []

    for py_file in repo_path.rglob("*.py"):
        if any(part in IGNORE_DIRS for part in py_file.parts):
            continue

        syntax_error = check_syntax(py_file, repo_path)
        if syntax_error:
            errors.append(syntax_error)

        import_errors = check_imports(py_file, repo_path)
        errors.extend(import_errors)

    flake8_errors = check_with_flake8(repo_path)
    errors.extend(flake8_errors)

    if errors:
        print("❌ Issues found:\n")
        for err in errors:
            print(err)
        sys.exit(1)
    else:
        print("✅ All files passed syntax, import, and static analysis checks.\n")


if __name__ == "__main__":
    try:
        auto_fix_code()
        fix_fstrings_without_placeholders(".")
        scan_repo(".")
    except subprocess.CalledProcessError as e:
        print(f"⚠️  Auto-fix tool failed: {e}")
        sys.exit(1)
