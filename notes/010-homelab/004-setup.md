---
title: Setup
---
## Intro

This note walks through turning a spare machine into a headless Ubuntu Server LTS box you administer over SSH. The hardware does not matter much — an x86 mini PC, an old laptop, a tower with a dead GPU, or an ARM board like a Raspberry Pi all end up in the same place. Only the flashing step and the image file differ.

Target state at the end of this note:

- Ubuntu Server 26.04 LTS ("Resolute Raccoon") installed on internal storage.
- Reachable over SSH with key-only login, on a fixed IP.
- Firewalled, patching itself, with a clock that is correct.
- Clean base ready for Docker or Kubernetes(k3s).

> [!NOTE]
> 26.04 LTS was released 23 April 2026 and gets free security updates until April 2031, extended to April 2036 with a free Ubuntu Pro subscription. Pick the LTS, never the interim release (25.10, 26.10 …) — interim releases are supported for 9 months only, which means a forced reinstall every year.

## Hardware Checklist

| Item | Notes |
| --- | --- |
| Server machine | Any 64-bit x86 (amd64) or ARM (arm64) box. 2 GB RAM / 5 GB disk is the official minimum; 8 GB RAM and a 128 GB SSD is a comfortable floor for containers. |
| USB stick | 4 GB or larger. **Everything on it gets destroyed.** |
| Second computer | To download and flash the image, and to SSH in afterwards. |
| Keyboard + monitor | Needed for the BIOS/UEFI menu and the installer only. Unplug both after setup. |
| Wired ethernet | Strongly preferred. Wi-Fi on a server means a flaky, disappearing SSH target. |

Old laptops make good first servers: built-in UPS (the battery), quiet, low power. Their catch is the lid switch, handled in [Laptop and Power Behaviour](#laptop-and-power-behaviour).

## What is Flashing and Why

An `.iso` is not a normal file you copy — it is a **byte-for-byte image of a whole disk**, including its partition table and bootloader. Flashing means writing those bytes to the USB stick starting at sector 0, so the stick becomes a clone of that disk.

Why a plain copy fails:

- **Firmware does not read your filesystem.** At power-on, the UEFI firmware looks for an EFI System Partition and a boot file at a fixed location (`/EFI/BOOT/BOOTX64.EFI`). Drag-and-dropping `ubuntu.iso` onto the stick puts one large file inside the stick's existing filesystem. The boot structures stay buried inside it, so firmware finds nothing bootable.
- **The image brings its own partition table.** Ubuntu ships a *hybrid* ISO that boots on both legacy BIOS and UEFI. That dual layout lives in the first sectors of the image — outside any file — so it can only arrive by raw write.
- **Raw writes are destructive and privileged.** Flashing overwrites the partition table, so the stick's old contents are gone, and the OS requires admin rights to write a block device directly. That is why every tool below asks for a password and shows a scary confirmation.

The same logic applies to `.img.xz` images for ARM boards; those are pre-installed system images rather than installers, so the flashed card *is* the finished system.

> [!WARNING]
> Flashing writes to whatever device you select. Selecting your own laptop's disk destroys it, and there is no undo. Confirm the device by size and name before every write.

## Pick a Flashing Tool

| Tool | Version | Platform | Use it when |
| --- | --- | --- | --- |
| [Rufus](https://rufus.ie/) | 4.15 | Windows | Default on Windows. Fastest, handles ISO quirks, portable single `.exe`. |
| [balenaEtcher](https://etcher.balena.io/) | 2.1.6 | Windows / macOS / Linux | You want one simple GUI everywhere: pick image, pick drive, flash. |
| [Raspberry Pi Imager](https://www.raspberrypi.com/software/) | 2.0.10 | Windows / macOS / Linux | Flashing SD cards or ARM `.img.xz` images. 2.0 adds a setup wizard that pre-seeds cloud-init (hostname, user, SSH key, Wi-Fi) before first boot. |
| [Ventoy](https://www.ventoy.net/) | 1.1.17 | Windows / Linux | You install OSes often. Installed once to the stick, then you just copy `.iso` files onto it and choose at boot — no reflashing per image. |
| `dd` | built in | macOS / Linux | You are already in a terminal and want no extra software. |

Any of them produce the same bootable stick. Rufus for Windows, `dd` or Etcher for macOS, Pi Imager for cards.

## Download and Verify the Image

Grab the server image for your architecture:

- x86: [`ubuntu-26.04-live-server-amd64.iso`](https://releases.ubuntu.com/26.04/) (~2.7 GiB) — the installer image.
- ARM boards / SBC: `ubuntu-26.04-preinstalled-server-arm64+raspi.img.xz` from [cdimage](https://cdimage.ubuntu.com/ubuntu/releases/26.04/release/) — no installer, boots straight into a running system.

```shell
cd ~/Downloads
curl -O https://releases.ubuntu.com/26.04/ubuntu-26.04-live-server-amd64.iso
curl -O https://releases.ubuntu.com/26.04/SHA256SUMS
curl -O https://releases.ubuntu.com/26.04/SHA256SUMS.gpg
```

### Step 1: Check the Checksum

A truncated or corrupted download produces an installer that fails halfway, usually with a confusing error. Comparing hashes takes ten seconds.

```shell
# macOS
shasum -a 256 --ignore-missing -c SHA256SUMS

# Linux
sha256sum --ignore-missing -c SHA256SUMS
```

Expected output:

```text
ubuntu-26.04-live-server-amd64.iso: OK
```

### Step 2: Check the Signature (Optional but Cheap)

The checksum only proves the file matches `SHA256SUMS`. Verifying the GPG signature proves `SHA256SUMS` itself came from Canonical, which matters when you download from a random mirror.

```shell
gpg --keyid-format long --keyserver hkp://keyserver.ubuntu.com \
  --recv-keys 0x46181433FBB75451 0xD94AA3F0EFE21092
gpg --keyid-format long --verify SHA256SUMS.gpg SHA256SUMS
```

Look for `Good signature from "Ubuntu CD Image Automatic Signing Key"` with fingerprint `8439 38DF 228D 22F7 B374 2BC0 D94A A3F0 EFE2 1092`.

> [!NOTE]
> `gpg: WARNING: This key is not certified with a trusted signature!` is expected — you never signed Canonical's key personally. The fingerprint matching is the check that counts.

## Flash the Stick

### Rufus (Windows)

1. Insert the USB stick and run `rufus-4.15.exe`.
2. **Device**: select the stick — verify by capacity, not by drive letter.
3. **Boot selection**: `SELECT` and choose the ISO.
4. **Partition scheme**: `GPT`, **Target system**: `UEFI (non CSM)`. Use `MBR` + `BIOS or UEFI` only for pre-2012 hardware.
5. `START`. If asked about downloading Syslinux/GRUB files, allow it.
6. Wait for `READY`, then `CLOSE` and eject.

### balenaEtcher (any OS)

1. `Flash from file` → the ISO.
2. `Select target` → the stick. Etcher hides system disks by default, which is the main reason to prefer it if `dd` makes you nervous.
3. `Flash!`, enter your password, wait for validation to finish.

### Raspberry Pi Imager (SD cards, ARM images)

1. `CHOOSE DEVICE` → your board, or `No filtering` for the generic `.img.xz`.
2. `CHOOSE OS` → `Other general-purpose OS` → `Ubuntu` → `Ubuntu Server 26.04 LTS (64-bit)`, or `Use custom` for a downloaded file.
3. `CHOOSE STORAGE` → the card.
4. In `OS customisation`, set hostname, username, password, and paste your SSH public key, then enable SSH. This writes cloud-init user-data to the boot partition so the board comes up headless — no monitor needed at all.
5. `WRITE`.

### dd (macOS)

```shell
# 1. Identify the stick — note the disk number, e.g. disk4
diskutil list

# 2. Unmount it (but do not eject it)
diskutil unmountDisk /dev/disk4

# 3. Write the image to the RAW device (/dev/rdiskN is much faster than /dev/diskN)
sudo dd if=ubuntu-26.04-live-server-amd64.iso of=/dev/rdisk4 bs=4m

# 4. Eject
diskutil eject /dev/disk4
```

> [!NOTE]
> macOS `dd` prints nothing while working. Press `Ctrl+T` to print progress. A 2.7 GiB write takes roughly 2–5 minutes on USB 3.

### dd (Linux)

```shell
# 1. Identify the stick by size and model
lsblk -o NAME,SIZE,MODEL,MOUNTPOINTS

# 2. Write, then flush kernel buffers before unplugging
sudo dd if=ubuntu-26.04-live-server-amd64.iso of=/dev/sdX bs=4M status=progress oflag=sync
sync
```

Replace `sdX` with the whole device (`sdb`), never a partition (`sdb1`).

## Prepare BIOS/UEFI on the Server

Reboot the target machine and hold the setup key during power-on — `F2`, `F10`, `F12`, `Del`, or `Esc` depending on vendor. Then:

- **Boot order**: put the USB stick first, or use the one-time boot menu.
- **Secure Boot**: leave it **on**. Ubuntu's bootloader and kernel are signed by Canonical, so it boots fine. Only third-party out-of-tree drivers require turning it off.
- **Fast Boot / Ultra Fast Boot**: turn **off**, otherwise USB devices are not enumerated early enough to boot from.
- **Restore on AC Power Loss**: set to `Power On` (sometimes `Last State`). Without this, the server stays dark after a power cut until you walk over and press the button.
- **Virtualisation** (`VT-x`, `AMD-V`, `SVM`, plus `VT-d`/`IOMMU`): enable if you plan on VMs.
- **Wake-on-LAN**: enable if you want to power the box up remotely later.

Save, exit, and boot the stick. After a few seconds you land on the installer's language screen.

## Run the Installer

The installer is `subiquity`, a text UI driven with arrow keys, `Tab`, `Space`, and `Enter`. Screens in order:

1. **Language** — English keeps log messages searchable.
2. **Installer update** — accept if offered; it pulls bug fixes for the installer itself.
3. **Keyboard layout** — set it correctly now or the password you type at first login will not be the one you set.
4. **Type of install** — `Ubuntu Server` (full). The `minimized` variant strips tooling meant for interactive administration, which is the opposite of what a homelab wants.
5. **Network** — the installer tries DHCP on wired interfaces. Let it, and pin a static address after first boot (below); doing it here works too but is fiddlier in a text UI. Note the assigned IP shown on this screen.
6. **Proxy** — leave empty unless your network requires one.
7. **Mirror** — geolocated automatically. Leave as-is; a wrong mirror only slows downloads.
8. **Storage** — `Use an entire disk`. Two decisions:
   - **Set up this disk as an LVM group**: yes. LVM lets you grow, shrink, and snapshot volumes later without reinstalling.
   - **Encrypt the LVM group with LUKS**: only if the machine could be stolen. An encrypted server cannot boot unattended — it waits at a passphrase prompt after every power cut, which defeats a headless box.
9. **Confirm destructive action** — the last exit before the disk is wiped. Re-read the device name.
10. **Profile** — your name, a **server hostname** (used everywhere afterwards: `nas`, `lab01`), username, password. This user is an administrator with `sudo`.
11. **Ubuntu Pro** — skip here, attach later in one command.
12. **SSH** — check `Install OpenSSH server`. Then set `Import SSH identity` to `from GitHub` and enter your GitHub username to pull your public keys. Importing a key disables password authentication automatically.
13. **Featured snaps** — select nothing. Install what you need later, from the repo you actually want it from.
14. **Install log** — wait for `Reboot Now`, then pull the USB stick when prompted.

> [!NOTE]
> No SSH keys on GitHub yet? Generate a pair on your laptop first — see [Git & GitHub Setup](../002-devops/001-git-github/001-setup.md#ssh-key-authentication) — and push the public key there before you reach this screen. Otherwise you fall back to password login and have to run `ssh-copy-id` afterwards.

## First Login

On the server console, log in and find its address:

```shell
ip -brief address
hostnamectl
```

From your laptop:

```shell
ssh <username>@<ip-address>
```

If you skipped the key import, copy your key over now and never type that password again:

```shell
ssh-copy-id <username>@<ip-address>
```

Unplug the monitor and keyboard. Everything below is over SSH.

## Baseline Hardening and Housekeeping

Run these once, in order. Each is small and independently useful.

### Patch Everything

```shell
sudo apt update && sudo apt full-upgrade -y
sudo reboot        # only if /var/run/reboot-required exists
```

Check whether a reboot is actually needed:

```shell
ls /var/run/reboot-required 2>/dev/null && cat /var/run/reboot-required.pkgs
```

### Hostname and Timezone

```shell
sudo hostnamectl set-hostname lab01
sudo timedatectl set-timezone Asia/Seoul
timedatectl status
```

26.04 uses **chrony** as the time daemon (it replaced `systemd-timesyncd` for new installs) with authenticated NTP against Canonical's servers. Confirm sync:

```shell
chronyc tracking
```

### Static IP with Netplan

A server whose address moves is a server you cannot find. Either reserve a DHCP lease on your router (simplest, keeps config in one place) or pin it on the host. For the latter, find the interface name and write a new Netplan file — do not edit the cloud-init one:

```shell
ip -brief link
```

```shell
sudo tee /etc/netplan/99-homelab.yaml > /dev/null <<'EOF'
network:
  version: 2
  renderer: networkd
  ethernets:
    enp1s0:
      dhcp4: false
      addresses:
        - 192.168.0.50/24
      routes:
        - to: default
          via: 192.168.0.1
      nameservers:
        addresses: [192.168.0.1, 1.1.1.1]
EOF
sudo chmod 600 /etc/netplan/99-homelab.yaml
```

Apply with the safety net — `netplan try` reverts automatically after 120 seconds if you do not confirm, so a typo cannot lock you out:

```shell
sudo netplan try
```

> [!NOTE]
> Netplan warns about world-readable config because these files can hold Wi-Fi secrets. The `chmod 600` above is what silences it.

### Lock Down SSH

Never edit `/etc/ssh/sshd_config` directly; drop a file into the include directory so package upgrades stay conflict-free.

```shell
sudo tee /etc/ssh/sshd_config.d/99-homelab.conf > /dev/null <<'EOF'
PermitRootLogin no
PasswordAuthentication no
KbdInteractiveAuthentication no
EOF
sudo sshd -t && sudo systemctl reload ssh
```

`sshd -t` validates the config first — reloading a broken config is how people lose access to headless machines.

> [!WARNING]
> Confirm key-based login works in a **second** terminal before closing your current session. With `PasswordAuthentication no` and no working key, your only way back in is a physical keyboard.

26.04 ships OpenSSH 10.2, which drops DSA keys entirely and negotiates post-quantum key exchange (`mlkem768x25519-sha256`) by default. `PerSourcePenalties` is also on by default, temporarily blocking addresses that keep failing authentication — useful, and one reason `fail2ban` is now optional rather than essential.

### Firewall

```shell
sudo ufw allow OpenSSH
sudo ufw enable
sudo ufw status verbose
```

Order matters: allow SSH *before* enabling, or you cut your own connection.

### Automatic Security Updates

```shell
sudo apt install -y unattended-upgrades
sudo dpkg-reconfigure --priority=low unattended-upgrades
```

Optionally let it reboot itself in the small hours when a kernel update requires it:

```shell
sudo tee /etc/apt/apt.conf.d/52homelab-reboot > /dev/null <<'EOF'
Unattended-Upgrade::Automatic-Reboot "true";
Unattended-Upgrade::Automatic-Reboot-Time "04:30";
EOF
```

Dry-run to see what it would do:

```shell
sudo unattended-upgrade --dry-run --debug
```

### Attach Ubuntu Pro (Free)

Free for personal use on up to 5 machines. It extends security coverage from 5 to 10 years, adds ESM for the much larger `universe` repository, and enables Livepatch (kernel patches without reboots — now on ARM64 too). Get a token from [ubuntu.com/pro/dashboard](https://ubuntu.com/pro/dashboard):

```shell
sudo pro attach <your-token>
sudo pro status
```

## Laptop and Power Behaviour

If the server is a laptop, it will suspend when you close the lid and vanish from the network. Tell `logind` to ignore the lid:

```shell
sudo mkdir -p /etc/systemd/logind.conf.d
sudo tee /etc/systemd/logind.conf.d/99-homelab.conf > /dev/null <<'EOF'
[Login]
HandleLidSwitch=ignore
HandleLidSwitchDocked=ignore
HandleLidSwitchExternalPower=ignore
EOF
sudo systemctl restart systemd-logind
```

For any headless machine, mask sleep outright:

```shell
sudo systemctl mask sleep.target suspend.target hibernate.target hybrid-sleep.target
```

## 26.04 LTS Specifics Worth Knowing

Coming from 24.04 or from older tutorials, these changes bite:

- **`sudo` is now `sudo-rs`**, a Rust reimplementation. It reads the same `/etc/sudoers` and `/etc/sudoers.d/`, so ordinary use is identical. Exotic options may be unsupported; the original is still installed as `sudo.ws`.
- **Core utilities come from `rust-coreutils`** (uutils). GNU versions remain available with a `gnu` prefix, e.g. `gnuls`, `gnusort`. Scripts relying on GNU-only flags may need it. To switch the whole system:

  ```shell
  # GNU
  sudo apt install coreutils-from-gnu --allow-remove-essential
  # back to Rust
  sudo apt install coreutils-from-uutils --allow-remove-essential
  ```

  `cp`, `mv`, and `rm` are still GNU implementations regardless.
- **cgroup v1 is gone** (systemd 259). Any container runtime or tooling still expecting the legacy hierarchy will not start. Current Docker and k3s are fine.
- **`/tmp` is a tmpfs**, so it lives in RAM and is wiped on reboot. Do not stage a 40 GB restore there.
- **APT 3** removed `apt-key`. Third-party repos must place their key in `/etc/apt/keyrings/` and reference it with `signed-by=`.
- **System V init script support is deprecated** — this is the last LTS that honours it. Write systemd units.
- **`amd64v3` packages are opt-in** and build for the `x86-64-v3` microarchitecture (roughly any AMD64 CPU from the last decade). Free performance if your hardware qualifies:

  ```shell
  echo 'APT::Architecture-Variants "amd64v3";' | sudo tee /etc/apt/apt.conf.d/99enable-amd64v3
  sudo apt update && sudo apt upgrade
  ```

- **The real-time kernel is free** in 26.04, outside Ubuntu Pro. Irrelevant for most homelabs, handy for audio or industrial I/O.

## Where to Go Next

Container runtime, from Docker's own repo (it resolves to the `resolute` suite for 26.04):

```shell
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.asc] \
https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo usermod -aG docker $USER   # log out and back in to take effect
```

Or skip straight to the orchestrator this section uses:

```shell
curl -sfL https://get.k3s.io | sh -
sudo k3s kubectl get nodes
```

> [!NOTE]
> Adding your user to the `docker` group is equivalent to giving it root — the daemon runs as root and the socket is the API. Fine on a homelab you own, not fine on a shared host.

## Repeatable Installs (Optional)

Building more than one node? Do not click through the installer repeatedly. Subiquity reads a cloud-init **autoinstall** file, so an identical node can be provisioned unattended: put `user-data` and an empty `meta-data` in the root of a second USB stick labelled `CIDATA`, boot the normal installer stick alongside it, and the install runs with no keyboard input.

The lazy way to author that file is to install one machine by hand, then copy the config it wrote:

```shell
sudo cat /var/log/installer/autoinstall-user-data
```

Edit the hostname, user, and SSH keys, and reuse it for the rest of the fleet.

## References

- Ubuntu Server installation tutorial: https://documentation.ubuntu.com/server/tutorial/basic-installation/
- Installer screen-by-screen guide: https://canonical-subiquity.readthedocs-hosted.com/en/latest/tutorial/screen-by-screen.html
- Ubuntu 26.04 LTS release notes: https://documentation.ubuntu.com/release-notes/26.04/
- Summary for LTS users (24.04 → 26.04 changes): https://documentation.ubuntu.com/release-notes/26.04/summary-for-lts-users/
- How to verify your Ubuntu download: https://ubuntu.com/tutorials/how-to-verify-ubuntu
- Netplan reference: https://netplan.readthedocs.io/
- Autoinstall reference: https://canonical-subiquity.readthedocs-hosted.com/en/latest/reference/autoinstall-reference.html
- Ubuntu Pro (free for personal use): https://ubuntu.com/pro

***

[Last modified: 2026-08-14]{.note-modified}
