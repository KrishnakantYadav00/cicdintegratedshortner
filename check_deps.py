#!/usr/bin/env python3
"""
Checks that everything needed to run/develop this project is installed.
Usage: python check_deps.py
Exits non-zero (and prints what's missing) if anything fails,
so it can also be dropped into CI as a fast pre-flight step.
"""
import importlib
import importlib.metadata
import subprocess
import sys

REQUIRED_MODULES = [
    ("flask", "Flask"),
    ("flask_sqlalchemy", "Flask-SQLAlchemy"),
    ("gunicorn", "gunicorn"),
]

OPTIONAL_MODULES = [
    ("psycopg2", "psycopg2-binary (PostgreSQL production support)"),
]

DEV_MODULES = [
    ("pytest", "pytest"),
    ("pytest_cov", "pytest-cov"),
    ("flake8", "flake8"),
]

MIN_PYTHON = (3, 10)


def check_python_version():
    ok = sys.version_info >= MIN_PYTHON
    label = f"Python >= {'.'.join(map(str, MIN_PYTHON))}"
    print(f"[{'OK' if ok else 'FAIL'}] {label} (found {sys.version.split()[0]})")
    return ok


def check_module(import_name, display_name, required=True):
    try:
        importlib.import_module(import_name)
        try:
            pkg_name = import_name.replace("_", "-")
            version = importlib.metadata.version(pkg_name)
        except Exception:
            version = "installed"
        print(f"[OK] {display_name} ({version})")
        return True
    except ImportError:
        status = "FAIL" if required else "OPTIONAL"
        print(f"[{status}] {display_name} not installed")
        return not required


def check_git():
    try:
        subprocess.run(
            ["git", "--version"], capture_output=True, check=True, text=True
        )
        print("[OK] git available")
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("[FAIL] git not found on PATH")
        return False


def main():
    print("== Runtime ==")
    results = [check_python_version()]

    print("\n== Required packages ==")
    for import_name, display_name in REQUIRED_MODULES:
        results.append(check_module(import_name, display_name, required=True))

    print("\n== Optional packages (Production Drivers) ==")
    for import_name, display_name in OPTIONAL_MODULES:
        check_module(import_name, display_name, required=False)

    print("\n== Dev/test packages ==")
    for import_name, display_name in DEV_MODULES:
        results.append(check_module(import_name, display_name, required=True))

    print("\n== Tooling ==")
    results.append(check_git())

    print()
    if all(results):
        print("All dependencies present. You're good to go.")
        sys.exit(0)
    else:
        print("Missing dependencies detected.")
        print("Fix with: pip install -r requirements-dev.txt")
        sys.exit(1)


if __name__ == "__main__":
    main()
