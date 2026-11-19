Runs the Bitcoin price ticker as a systemd service, so it starts on boot and restarts after a failure. `deploy/install.sh` renders and installs the unit for you; this page covers what it does, the manual path, migrating from pigpio and rollback.

# systemd service unit

![License](https://img.shields.io/badge/license-MIT-green)
![systemd](https://img.shields.io/badge/systemd-Type%3Dnotify-blue)

## With the installer (recommended)

From the repository root on the Pi, as the user the service should run as:

```bash
./deploy/install.sh
```

The installer renders `btcticker.service.in` with your user name and the repository path, installs it as `/etc/systemd/system/btcticker.service` (only if it changed), runs `daemon-reload`, enables and restarts the service, and waits until it reports `active`. Rerun it after every `git pull`.

## Manual installation

`btcticker.service.in` is a template with two placeholders:

| Placeholder | Replaced with | Example |
|---|---|---|
| `@USER@` | user the service runs as | `pi` |
| `@APP_DIR@` | absolute path of the repository | `/home/pi/raspberry/btc-ticker` |

Render and install it by hand (from the repository root, with the venv already set up via `pip install -e ".[rpi]"`):

```bash
sed -e "s|@USER@|$(id -un)|g" -e "s|@APP_DIR@|$PWD|g" \
    deploy/systemd/btcticker.service.in > "$TMPDIR/btcticker.service"
sudo install -m 644 "$TMPDIR/btcticker.service" /etc/systemd/system/btcticker.service
sudo systemctl daemon-reload

# Enable (start on boot) and start immediately
sudo systemctl enable --now btcticker

# Check status / logs
systemctl status btcticker
journalctl -u btcticker -f
```

(If `$TMPDIR` is unset, use `/tmp`. The `|` delimiter assumes neither value contains a `|`.)

To stop and disable auto-start:

```bash
sudo systemctl disable --now btcticker
```

The unit sets `LG_WD=/run/btcticker` (with `RuntimeDirectory=btcticker`) so lgpio writes its `.lgd-nfy*` notification FIFOs there instead of into the repository.

## Migrating from pigpio

Earlier versions drove the GPIO pins through the `pigpiod` daemon, which accepts unauthenticated GPIO commands on TCP port 8888. btc-ticker now uses gpiozero's lgpio backend, which needs no daemon.

On an existing install, `git pull && ./deploy/install.sh` migrates automatically:

- It removes `pigpio`, `RPi.GPIO` and `numpy` from the venv (unless another installed package still requires them) and installs `lgpio`.
- It replaces the old hand-copied unit with the rendered template.
- **Only after the service has started healthy on lgpio** (step 9 of the installer), it stops and disables `pigpiod` and removes the `pigpio`, `pigpiod` and `python3-pigpio` apt packages that are installed. It first simulates the removal; if apt would also remove any other package, it removes nothing, prints the list and leaves the decision to you.
- If the service doesn't come up, the installer prints the journal and leaves `pigpiod` untouched.
- If the installer had to enable SPI, it does not start the service or touch `pigpiod` on that run; reboot and run it again.

Pass `--keep-pigpiod` to skip the pigpiod step, for example when another program on the Pi still needs it.

## Rollback

To return to the pigpio-based version:

From the repository root, as the user the service runs as:

```bash
git checkout 6647587         # last commit before the lgpio migration
sudo apt install pigpio      # only if the installer removed it
sudo systemctl enable --now pigpiod
.venv/bin/python -m pip install -U -e ".[rpi]"
sed -e "s|^User=.*|User=$(id -un)|" -e "s|/home/pi/raspberry/btc-ticker|$PWD|g" \
    deploy/systemd/btcticker.service > "$TMPDIR/btcticker.service"
sudo install -m 644 "$TMPDIR/btcticker.service" /etc/systemd/system/btcticker.service
sudo systemctl daemon-reload
sudo systemctl restart btcticker
```

That commit (or any earlier known-good one) still contains `deploy/systemd/btcticker.service` and the pigpio-based `[rpi]` extra. Its unit hard-codes `User=pi` and `/home/pi/raspberry/btc-ticker`; the `sed` line swaps in your user and checkout path.

## Troubleshooting

| Symptom | Likely cause |
|---|---|
| Installer says the service did not start | Read the printed journal; fix the cause and rerun `./deploy/install.sh` (pigpiod was left as it was) |
| Installer refuses to remove the pigpio apt packages | apt would also remove other packages; review the printed list and remove manually if that's fine |
| `.lgd-nfy*` files appear in the repository | The service runs an old unit without `LG_WD`; rerun `./deploy/install.sh` |
| `status=200/CHDIR` or `203/EXEC` | `@APP_DIR@` or the venv path is wrong; rerun the installer from the repository root |

## License

MIT — see [LICENSE](../../LICENSE).
