#!/usr/bin/env bash
set -euo pipefail

# quick_start.sh
# Small helper script to prepare the development environment for monsoon.
# It checks for a suitable Python executable, creates a virtualenv, installs
# requirements and optionally runs the application.

REQ_PY_MAJOR=3
REQ_PY_MINOR=10
VENV_DIR=.venv

info() { echo "[INFO] $*"; }
warn() { echo "[WARN] $*"; }
err() { echo "[ERROR] $*"; exit 1; }

find_python() {
  # Prefer the Windows launcher 'py' first (it can select minor versions), then python3, then python
  for cmd in py python3 python; do
    if command -v "$cmd" >/dev/null 2>&1; then
      echo "$cmd"
      return 0
    fi
  done
  return 1
}

check_python_version() {
  pycmd="$1"
  ver=$($pycmd -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}')")
  maj=$(echo "$ver" | cut -d. -f1)
  min=$(echo "$ver" | cut -d. -f2)
  if [ "$maj" -lt "$REQ_PY_MAJOR" ] || { [ "$maj" -eq "$REQ_PY_MAJOR" ] && [ "$min" -lt "$REQ_PY_MINOR" ]; }; then
    return 1
  fi
  return 0
}

print_activation_help() {
  cat <<EOF
Activation commands (pick one based on your shell/OS):
 - bash / macOS / WSL:   source ./env/bin/activate
 - Windows PowerShell:   .\env\Scripts\Activate.ps1
 - Windows cmd.exe:      .\env\Scripts\activate.bat
 - Windows (Git Bash):   source ./env/Scripts/activate
EOF
}

main() {
  info "Checking for Python >= ${REQ_PY_MAJOR}.${REQ_PY_MINOR}..."
  pycmd=$(find_python || true)
  if [ -z "${pycmd}" ]; then
    warn "No python executable found on PATH."
    echo "Please install Python ${REQ_PY_MAJOR}.${REQ_PY_MINOR} or newer from https://www.python.org/downloads/ or use your OS package manager."
    exit 2
  fi

  if ! check_python_version "$pycmd"; then
    warn "Found $($pycmd -V 2>&1) but it's older than required ${REQ_PY_MAJOR}.${REQ_PY_MINOR}."
    echo "Please install an appropriate Python version (see https://www.python.org/downloads/)."
    exit 3
  fi

  info "Using python: $(command -v "$pycmd") ($($pycmd -V 2>&1))"

  # Prefer .venv directory by convention, fall back to env for compatibility
  if [ -d "$VENV_DIR" ]; then
    info "Virtual environment '$VENV_DIR' already exists."
  elif [ -d env ]; then
    VENV_DIR=env
    info "Found existing virtual environment 'env' - will use that."
  else
    info "Creating virtual environment '$VENV_DIR'..."
    $pycmd -m venv "$VENV_DIR"
  fi

  echo
  print_activation_help
  echo

  read -p "Would you like this script to activate the venv and install requirements now? [y/N] " -r
  if [[ "$REPLY" =~ ^[Yy]$ ]]; then
    # Try to activate in the current shell if running under bash; otherwise provide instructions.
    if [ -n "${BASH_VERSION-}" ]; then
      # shell is bash-like and can source
      # Try Unix-style venv activation first, then Windows-style
      if [ -f "$VENV_DIR/bin/activate" ]; then
        source "$VENV_DIR/bin/activate"
      else
        # For Windows git-bash / msys
        source "$VENV_DIR/Scripts/activate" 2>/dev/null || true
      fi
      info "Installing requirements..."
      pip install -r ./requirements.txt
      info "You can run the app with: python ./src/monsoon.py"
      read -p "Run monsoon now? [y/N] " -r
      if [[ "$REPLY" =~ ^[Yy]$ ]]; then
        python ./src/monsoon.py
      fi
    else
      echo
      warn "This script cannot reliably activate the virtualenv for non-bash shells."
      echo "Please run the appropriate activation command from above in your shell, then run:"
      echo "  pip install -r ./requirements.txt"
      echo "  python ./src/monsoon.py"
    fi
  else
    info "Skipped automatic activation/install. To set up manually, run:"
    echo "  python -m venv env"
    print_activation_help
    echo "  pip install -r ./requirements.txt"
    echo "  python ./src/monsoon.py"
  fi
}

main "$@"
