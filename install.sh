#!/bin/sh
# datasage installer
# Usage (curl):  curl -fsSL https://raw.githubusercontent.com/otsolaue/datasage/main/install.sh | sh
# Usage (wget):  wget -qO- https://raw.githubusercontent.com/otsolaue/datasage/main/install.sh | sh
# Usage (local): ./install.sh --local
# Usage (backend): ./install.sh --backend anthropic   (anthropic | openai | ollama | all)
set -e

PACKAGE_NAME="datasage"
BACKEND="anthropic"
LOCAL_INSTALL=false

_next_is_backend=false
for arg in "$@"; do
    if [ "$_next_is_backend" = true ]; then
        BACKEND="$arg"
        _next_is_backend=false
        continue
    fi
    case "$arg" in
        --local)   LOCAL_INSTALL=true ;;
        --backend) _next_is_backend=true ;;
    esac
done

# ── Colors ────────────────────────────────────────────────────────────────────
if [ -t 1 ]; then
    _ESC="$(printf '\033')"
    C_GREEN="${_ESC}[32m"
    C_DIM="${_ESC}[2m"
    C_ERR="${_ESC}[91m"
    C_RST="${_ESC}[0m"
else
    C_GREEN= C_DIM= C_ERR= C_RST=
fi

step()  { printf "  ${C_GREEN}%-14s${C_RST}%s\n" "$1" "$2"; }
err()   { printf "  ${C_ERR}error:${C_RST} %s\n" "$1" >&2; exit 1; }

printf "\n${C_GREEN}  🌿 datasage installer${C_RST}\n\n"

# ── Detect Python ─────────────────────────────────────────────────────────────
PYTHON=""
for candidate in python3 python; do
    if command -v "$candidate" >/dev/null 2>&1; then
        ver=$("$candidate" -c "import sys; print(sys.version_info[:2])" 2>/dev/null)
        case "$ver" in
            "(3, 1"[0-3]*)
                PYTHON="$candidate"
                break
                ;;
        esac
    fi
done
[ -z "$PYTHON" ] && err "Python 3.10–3.13 is required. Please install it and re-run."
step "Python" "$($PYTHON --version)"

# ── Create venv ───────────────────────────────────────────────────────────────
VENV_DIR="$HOME/.datasage/venv"
if [ ! -d "$VENV_DIR" ]; then
    step "Creating" "virtual environment at $VENV_DIR"
    "$PYTHON" -m venv "$VENV_DIR"
fi
PIP="$VENV_DIR/bin/pip"
DATASAGE="$VENV_DIR/bin/datasage"

# ── Install ───────────────────────────────────────────────────────────────────
step "Upgrading" "pip"
"$PIP" install --quiet --upgrade pip

if [ "$LOCAL_INSTALL" = true ]; then
    step "Installing" "$PACKAGE_NAME[$BACKEND] (local)"
    "$PIP" install --quiet -e ".[$BACKEND]"
else
    step "Installing" "$PACKAGE_NAME[$BACKEND]"
    "$PIP" install --quiet "$PACKAGE_NAME[$BACKEND]"
fi

# ── Done ──────────────────────────────────────────────────────────────────────
printf "\n${C_GREEN}  ✓ datasage installed!${C_RST}\n\n"
printf "  To launch:\n"
printf "    ${C_DIM}source $VENV_DIR/bin/activate${C_RST}\n"
printf "    ${C_DIM}datasage run${C_RST}\n\n"
printf "  Or without activating:\n"
printf "    ${C_DIM}$DATASAGE run${C_RST}\n\n"
