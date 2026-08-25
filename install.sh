#!/usr/bin/env bash
set -Eeuo pipefail

APP_ID="projectgrafkom"
APP_NAME="Project Grafkom"
SOURCE_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

XDG_DATA_HOME="${XDG_DATA_HOME:-"$HOME/.local/share"}"
XDG_BIN_HOME="${XDG_BIN_HOME:-"$HOME/.local/bin"}"

INSTALL_DIR="$XDG_DATA_HOME/$APP_ID"
BIN_PATH="$XDG_BIN_HOME/$APP_ID"
DESKTOP_DIR="$XDG_DATA_HOME/applications"
DESKTOP_FILE="$DESKTOP_DIR/$APP_ID.desktop"
ICON_DIR="$XDG_DATA_HOME/icons/hicolor/scalable/apps"
ICON_FILE="$ICON_DIR/$APP_ID.svg"

log() {
    printf '[%s] %s\n' "$APP_NAME" "$1"
}

die() {
    printf '[%s] Error: %s\n' "$APP_NAME" "$1" >&2
    exit 1
}

install_system_packages() {
    if ! command -v dnf >/dev/null 2>&1; then
        log "dnf tidak ditemukan. Lewati pemasangan paket sistem."
        return
    fi

    if command -v python3 >/dev/null 2>&1 \
        && python3 -m pip --version >/dev/null 2>&1 \
        && { python3 -m venv --help >/dev/null 2>&1 || python3 -m virtualenv --version >/dev/null 2>&1; }; then
        return
    fi

    log "Memasang paket sistem Fedora yang dibutuhkan."
    sudo dnf install -y python3 python3-pip python3-virtualenv desktop-file-utils
}

copy_project_files() {
    log "Menyalin aplikasi ke $INSTALL_DIR."
    rm -rf "$INSTALL_DIR"
    mkdir -p "$INSTALL_DIR"

    cp "$SOURCE_DIR/ProjectGrafkom.py" "$INSTALL_DIR/"

    if [[ -f "$SOURCE_DIR/requirements.txt" ]]; then
        cp "$SOURCE_DIR/requirements.txt" "$INSTALL_DIR/requirements.txt"
    elif [[ -f "$SOURCE_DIR/requierement.txt" ]]; then
        cp "$SOURCE_DIR/requierement.txt" "$INSTALL_DIR/requirements.txt"
    else
        die "File requirements.txt atau requierement.txt tidak ditemukan."
    fi
}

create_virtualenv() {
    log "Membuat virtualenv Python."
    python3 -m venv "$INSTALL_DIR/.venv" || python3 -m virtualenv "$INSTALL_DIR/.venv"

    log "Memasang dependensi Python."
    "$INSTALL_DIR/.venv/bin/python" -m pip install --upgrade pip
    "$INSTALL_DIR/.venv/bin/python" -m pip install -r "$INSTALL_DIR/requirements.txt"
}

install_launcher() {
    log "Membuat command launcher: $BIN_PATH."
    mkdir -p "$XDG_BIN_HOME"
    cat > "$BIN_PATH" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
APP_DIR="$INSTALL_DIR"
cd "\$APP_DIR"
exec "\$APP_DIR/.venv/bin/python" "\$APP_DIR/ProjectGrafkom.py" "\$@"
EOF
    chmod +x "$BIN_PATH"
}

install_icon() {
    log "Memasang ikon aplikasi."
    mkdir -p "$ICON_DIR"
    cat > "$ICON_FILE" <<'EOF'
<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 128 128">
  <rect width="128" height="128" rx="22" fill="#f0f4f8"/>
  <rect x="20" y="22" width="88" height="66" rx="6" fill="#ffffff" stroke="#263238" stroke-width="6"/>
  <path d="M35 74 57 44 75 64 91 38" fill="none" stroke="#2d6db5" stroke-width="8" stroke-linecap="round" stroke-linejoin="round"/>
  <circle cx="42" cy="98" r="8" fill="#e53935"/>
  <rect x="56" y="90" width="16" height="16" rx="2" fill="#43a047"/>
  <path d="M86 90 98 106H74z" fill="#f9a825"/>
</svg>
EOF
}

install_desktop_entry() {
    log "Membuat desktop entry: $DESKTOP_FILE."
    mkdir -p "$DESKTOP_DIR"
    cat > "$DESKTOP_FILE" <<EOF
[Desktop Entry]
Type=Application
Name=$APP_NAME
Comment=Aplikasi menggambar vektor untuk Grafika Komputer
Exec=$BIN_PATH
Icon=$ICON_FILE
Terminal=false
Categories=Graphics;Education;Qt;
StartupNotify=true
EOF
    chmod 644 "$DESKTOP_FILE"

    if command -v desktop-file-validate >/dev/null 2>&1; then
        desktop-file-validate "$DESKTOP_FILE"
    fi

    if command -v update-desktop-database >/dev/null 2>&1; then
        update-desktop-database "$DESKTOP_DIR" >/dev/null 2>&1 || true
    fi
}

uninstall_app() {
    log "Menghapus instalasi user-local."
    rm -rf "$INSTALL_DIR"
    rm -f "$BIN_PATH" "$DESKTOP_FILE" "$ICON_FILE"
    log "Selesai uninstall."
}

main() {
    case "${1:-install}" in
        install)
            install_system_packages
            copy_project_files
            create_virtualenv
            install_launcher
            install_icon
            install_desktop_entry
            log "Instalasi selesai."
            log "Jalankan dari menu aplikasi, atau dengan command: $APP_ID"
            ;;
        uninstall)
            uninstall_app
            ;;
        *)
            die "Penggunaan: ./install.sh [install|uninstall]"
            ;;
    esac
}

main "$@"
