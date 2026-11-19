#!/usr/bin/env bash
# Install or upgrade btc-ticker on a Raspberry Pi.
#
# Run from a checkout as the user the service should run as (not root):
#   ./deploy/install.sh                 # fresh install
#   git pull && ./deploy/install.sh     # upgrade
#
# Safe to run repeatedly: each step only changes what is not already in place.
# sudo is used only for system steps (apt, raspi-config, groups, systemd).

set -euo pipefail

# Parse English output regardless of the system locale.
export LC_ALL=C

SERVICE=btcticker
UNIT_DEST=/etc/systemd/system/${SERVICE}.service
HEALTH_TIMEOUT=30

# lgpio has no wheel for Python 3.13 on Pi OS (aarch64 or armv7l) on PyPI or
# piwheels, so pip compiles it from the sdist. The sdist bundles the lgpio C
# sources and SWIG output, so it needs a C toolchain and the Python headers,
# but neither swig nor liblgpio-dev.
APT_BASE_DEPS=(python3-venv git)
APT_BUILD_DEPS=(gcc libc6-dev python3-dev)

OBSOLETE_PY_PKGS=(pigpio RPi.GPIO numpy)
OBSOLETE_APT_PKGS=(pigpio pigpiod python3-pigpio)

FORCE=0
KEEP_PIGPIOD=0
REBOOT_NEEDED=0
RELOGIN_NEEDED=0

APP_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
APP_USER="$(id -un)"
VENV="$APP_DIR/.venv"
PIP=("$VENV/bin/python" -m pip)

log() { printf '==> %s\n' "$*"; }
warn() { printf 'WARNING: %s\n' "$*" >&2; }
die() {
    printf 'ERROR: %s\n' "$*" >&2
    exit 1
}

usage() {
    cat <<EOF
Usage: $(basename "$0") [--force] [--keep-pigpiod] [--help]

Installs or upgrades btc-ticker from this checkout ($APP_DIR):
system packages, SPI, gpio/spi group membership, the Python venv,
the systemd unit, and removal of the obsolete pigpio daemon.

Options:
  --force          Skip the Raspberry Pi model check.
  --keep-pigpiod   Leave pigpiod and its apt packages alone (for Pis where
                   something else still needs it).
  -h, --help       Show this help.
EOF
}

parse_args() {
    while (($#)); do
        case "$1" in
            --force) FORCE=1 ;;
            --keep-pigpiod) KEEP_PIGPIOD=1 ;;
            -h | --help)
                usage
                exit 0
                ;;
            *)
                usage >&2
                die "unknown option: $1"
                ;;
        esac
        shift
    done
}

apt_installed() {
    # No pipe into grep -q: under pipefail an early grep exit can SIGPIPE
    # dpkg-query and make an installed package look missing.
    local status
    status="$(dpkg-query -W -f='${Status}' "$1" 2>/dev/null)" || return 1
    [[ $status == "install ok installed" ]]
}

# 1. Preflight
preflight() {
    log "Preflight"
    [[ $EUID -ne 0 ]] || die "run as the normal user, not root; sudo is used where needed"

    local model=""
    [[ -r /proc/device-tree/model ]] && model="$(tr -d '\0' </proc/device-tree/model)"
    if [[ $model != *"Raspberry Pi"* ]]; then
        if ((FORCE)); then
            warn "not a Raspberry Pi (${model:-unknown model}); continuing because of --force"
        else
            warn "this does not look like a Raspberry Pi (${model:-unknown model})"
            die "rerun with --force to install anyway"
        fi
    fi

    command -v python3 >/dev/null || die "python3 not found"
    python3 -c 'import sys; sys.exit(sys.version_info < (3, 13))' ||
        die "python3 >= 3.13 required, found $(python3 -V 2>&1)"

    log "App dir: $APP_DIR, user: $APP_USER, model: ${model:-unknown}"
}

# 2. System packages
install_system_packages() {
    log "System packages"
    local wanted=("${APT_BASE_DEPS[@]}" "${APT_BUILD_DEPS[@]}")

    local missing=() pkg
    for pkg in "${wanted[@]}"; do
        apt_installed "$pkg" || missing+=("$pkg")
    done

    if ((${#missing[@]} == 0)); then
        log "All present: ${wanted[*]}"
        return
    fi
    log "Installing: ${missing[*]}"
    sudo apt-get update -q
    sudo apt-get install -y --no-install-recommends "${missing[@]}"
}

# 3. SPI
enable_spi() {
    log "SPI"
    if command -v raspi-config >/dev/null; then
        if [[ $(sudo raspi-config nonint get_spi) == 1 ]]; then
            log "Enabling SPI"
            sudo raspi-config nonint do_spi 0
            REBOOT_NEEDED=1
        else
            log "SPI already enabled"
        fi
    elif [[ -e /dev/spidev0.0 ]]; then
        log "SPI available (/dev/spidev0.0)"
    else
        warn "raspi-config not found and /dev/spidev0.0 missing;" \
            "enable SPI (dtparam=spi=on in config.txt) and reboot"
    fi
}

# 4. Groups
ensure_groups() {
    log "Groups"
    local groups missing=() g
    groups=" $(id -nG "$APP_USER") "
    for g in gpio spi; do
        [[ $groups == *" $g "* ]] || missing+=("$g")
    done
    if ((${#missing[@]} == 0)); then
        log "$APP_USER is already in gpio and spi"
        return
    fi
    local joined
    joined="$(
        IFS=,
        echo "${missing[*]}"
    )"
    log "Adding $APP_USER to: $joined"
    sudo usermod -aG "$joined" "$APP_USER"
    RELOGIN_NEEDED=1
}

# 5. Python env
install_python_env() {
    log "Python environment"
    if [[ ! -x $VENV/bin/python ]]; then
        log "Creating $VENV"
        python3 -m venv "$VENV"
    fi
    "${PIP[@]}" install -q -U pip
    # -U so an existing venv picks up new versions and security floors.
    (cd "$APP_DIR" && "${PIP[@]}" install -U -e ".[rpi]")
}

# 6. Remove obsolete Python packages from the venv
remove_obsolete_python_packages() {
    log "Obsolete Python packages"
    local removed=() pkg info required_by
    for pkg in "${OBSOLETE_PY_PKGS[@]}"; do
        info="$("${PIP[@]}" show "$pkg" 2>/dev/null)" || continue
        required_by="$(sed -n 's/^Required-by:[[:space:]]*//p' <<<"$info")"
        if [[ -n $required_by ]]; then
            log "Keeping $pkg (required by: $required_by)"
            continue
        fi
        "${PIP[@]}" uninstall -y -q "$pkg"
        removed+=("$pkg")
    done
    if ((${#removed[@]})); then
        log "Removed: ${removed[*]}"
    else
        log "Nothing to remove"
    fi
}

# Escape a string for use as a sed replacement with / as the delimiter.
sed_escape() {
    printf '%s' "$1" | sed -e 's/[\/&\\]/\\&/g'
}

# 7. Service unit
install_service() {
    log "Service unit"
    # Rendered in memory, so no temp file is left behind if a step fails.
    local rendered
    rendered="$(sed -e "s/@USER@/$(sed_escape "$APP_USER")/g" \
        -e "s/@APP_DIR@/$(sed_escape "$APP_DIR")/g" \
        "$APP_DIR/deploy/systemd/${SERVICE}.service.in")"

    if [[ -f $UNIT_DEST && "$(<"$UNIT_DEST")" == "$rendered" ]]; then
        log "Unit unchanged: $UNIT_DEST"
    else
        log "Installing $UNIT_DEST"
        printf '%s\n' "$rendered" | sudo tee "$UNIT_DEST" >/dev/null
        sudo chown root:root "$UNIT_DEST"
        sudo chmod 644 "$UNIT_DEST"
        sudo systemctl daemon-reload
    fi

    sudo systemctl enable --quiet "$SERVICE"
    if ((REBOOT_NEEDED)); then
        log "Not starting $SERVICE: SPI needs a reboot first"
        return
    fi
    log "Restarting $SERVICE"
    # A failed start is reported by the health check below.
    sudo systemctl restart "$SERVICE" || true
}

print_pending_notices() {
    ((REBOOT_NEEDED)) && warn "SPI was just enabled: reboot (sudo reboot) before the display will work"
    ((RELOGIN_NEEDED)) && warn "$APP_USER was added to the gpio/spi groups: log out and back in for your shell to pick this up"
    return 0
}

# 8. Health check
health_check() {
    log "Waiting up to ${HEALTH_TIMEOUT}s for $SERVICE to become active"
    local i
    for ((i = 0; i < HEALTH_TIMEOUT; i++)); do
        systemctl is-active --quiet "$SERVICE" && break
        sleep 1
    done
    # Re-check after a short pause to catch a crash right after READY=1.
    if systemctl is-active --quiet "$SERVICE" && sleep 5 &&
        systemctl is-active --quiet "$SERVICE"; then
        log "$SERVICE is active"
    else
        warn "$SERVICE did not start; pigpiod was left untouched"
        journalctl -u "$SERVICE" -n 40 --no-pager || true
        print_pending_notices
        exit 1
    fi

    # FIFOs left in the checkout by lgpio runs without LG_WD (e.g. a hand
    # test); the unit now points LG_WD at /run/btcticker.
    local stale
    stale="$(find "$APP_DIR" -maxdepth 1 -type p -name '.lgd-nfy*' -print -delete)"
    [[ -z $stale ]] || log "Removed stale lgpio FIFOs: $(tr '\n' ' ' <<<"$stale")"
}

# 9. Remove pigpiod (only after a healthy start on lgpio)
remove_pigpiod() {
    log "pigpiod"
    if ((KEEP_PIGPIOD)); then
        log "Skipped (--keep-pigpiod)"
        return
    fi

    local changed=0
    if systemctl cat pigpiod.service >/dev/null 2>&1 &&
        { systemctl is-enabled --quiet pigpiod || systemctl is-active --quiet pigpiod; }; then
        log "Stopping and disabling pigpiod"
        sudo systemctl disable --now --quiet pigpiod
        changed=1
    fi

    local installed=() pkg
    for pkg in "${OBSOLETE_APT_PKGS[@]}"; do
        apt_installed "$pkg" && installed+=("$pkg")
    done
    if ((${#installed[@]})); then
        local would_remove extra=()
        would_remove="$(apt-get -s remove "${installed[@]}" | sed -n 's/^Remv \([^ ]*\).*/\1/p')"
        for pkg in $would_remove; do
            [[ " ${installed[*]} " == *" $pkg "* ]] || extra+=("$pkg")
        done
        if ((${#extra[@]})); then
            warn "removing ${installed[*]} would also remove: ${extra[*]}"
            warn "not removing any apt packages. Decide yourself, e.g.:"
            warn "  sudo apt-get remove ${installed[*]}"
            return
        fi
        log "Removing apt packages: ${installed[*]}"
        sudo apt-get remove -y "${installed[@]}"
        changed=1
    fi

    ((changed)) || log "Nothing to remove"
}

# 10. Summary
summary() {
    log "Summary"
    "${PIP[@]}" show btcticker 2>/dev/null | grep -E '^(Name|Version):' || true
    systemctl status "$SERVICE" --no-pager -n 5 || true
    log "Follow the logs with: journalctl -u $SERVICE -f"
    print_pending_notices
}

main() {
    parse_args "$@"
    preflight
    install_system_packages
    enable_spi
    ensure_groups
    install_python_env
    remove_obsolete_python_packages
    install_service
    if ((REBOOT_NEEDED)); then
        # The service cannot open /dev/spidev until after a reboot, so a health
        # check would always fail; pigpiod stays until a healthy start.
        warn "skipping the health check and pigpiod removal until after the reboot;"
        warn "reboot, then rerun ./deploy/install.sh to finish"
    else
        health_check
        remove_pigpiod
    fi
    summary
}

main "$@"
