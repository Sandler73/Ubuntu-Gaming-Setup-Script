# Quick Start Guide v2.1

**Get gaming on Linux in under 30 minutes**

This guide walks you through your first installation, from download to playing games.

---

## 📋 Before You Begin

### Prerequisites Checklist

- [ ] Debian-based Linux (Ubuntu 20.04+, Mint 20+, Debian 11+)
- [ ] Sudo/root access
- [ ] Internet connection (stable)
- [ ] 10GB+ free disk space
- [ ] Terminal access (Ctrl+Alt+T)

### Know Your Hardware

**Check your GPU:**
```bash
lspci | grep -i vga
```

**Running in VM?** The script auto-detects VMware, VirtualBox, KVM, Hyper-V.

---

## 🚀 Three Installation Paths

### Path A: Interactive (Recommended for Beginners)
**Time:** 30-45 minutes | **Control:** Full | **Safety:** Highest

### Path B: Automated (Experienced Users)
**Time:** 15-20 minutes | **Control:** Minimal | **Safety:** Test with dry-run first

### Path C: Test First (Cautious Users)
**Time:** 5 min test + 30 min install | **Control:** Full | **Safety:** Maximum

---

## 🎯 Path A: Interactive Installation

### Step 1: Download

```bash
cd ~/Downloads
wget https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/debian_gaming_setup.py
```

### Step 2: Run

```bash
sudo python3 debian_gaming_setup.py
```

### Step 3: Follow Prompts

The script will:
1. **Detect your system** - Shows GPU, distribution, VM status
2. **Update packages** - Updates system (5-10 minutes)
3. **Detect hardware** - Identifies GPU vendor
4. **Ask about drivers** - Install NVIDIA/AMD/Intel/VM tools?
5. **Ask about platforms** - Install Steam, Lutris, etc?
6. **Ask about tools** - Discord, OBS, controllers?
7. **Show summary** - Display what was installed
8. **Offer reboot** - Required for drivers

**Example prompts you'll see:**

```
✓ NVIDIA GPU detected
Install NVIDIA drivers? (y/n): y

✓ Steam already installed (version: 1.0.0.78)
Update available: 1.0.0.78 → 1.0.0.79
Update Steam? (y/n): y

Install Lutris? (y/n): y
Install Heroic Games Launcher? (y/n): y
Install SOBER (Roblox on Linux)? (y/n): n
Install Waydroid (Android container)? (y/n): n
```

**What to answer:**
- **GPU Drivers:** `y` (if not in VM)
- **Steam:** `y` (essential for gaming)
- **Lutris:** `y` (for Epic, GOG, etc.)
- **GameMode:** `y` (performance boost)
- **MangoHud:** `y` (FPS counter)
- **SOBER:** `y` if you play Roblox
- **Waydroid:** `y` if you want Android apps
- **Optimizations:** `y` (desktop), `n` (laptop)

### Step 4: Reboot

```bash
sudo reboot
```

**Required for:** GPU drivers, kernel parameters, CPU governor

### Step 5: Verify

**Check GPU drivers:**
```bash
# NVIDIA
nvidia-smi

# AMD/Intel
glxinfo | grep "OpenGL renderer"
```

### Step 6: Configure Steam

1. Open Steam
2. Go to **Settings** → **Compatibility**
3. Enable **"Enable Steam Play for all other titles"**
4. Select **Proton Experimental**
5. Click **OK** and restart Steam

### Step 7: Play!

**Test games:**
- **Native:** Counter-Strike 2 (free), Portal 2
- **Proton:** Stardew Valley, Terraria, Hades

---

## ⚡ Path B: Automated Installation

### NVIDIA Gaming PC (Complete)

```bash
wget https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/debian_gaming_setup.py

sudo python3 debian_gaming_setup.py -y \
    --nvidia \
    --all-platforms \
    --wine \
    --ge-proton \
    --gamemode \
    --mangohud \
    --gwe \
    --vkbasalt \
    --discord \
    --obs \
    --controllers \
    --essential \
    --codecs \
    --optimize \
    --launcher

sudo reboot
```

### AMD Gaming PC

```bash
sudo python3 debian_gaming_setup.py -y \
    --amd \
    --all-platforms \
    --wine \
    --ge-proton \
    --gamemode \
    --mangohud \
    --vkbasalt \
    --discord \
    --essential \
    --codecs \
    --optimize

sudo reboot
```

### Intel Laptop (Battery-Friendly)

```bash
sudo python3 debian_gaming_setup.py -y \
    --intel \
    --steam \
    --lutris \
    --gamemode \
    --mangohud \
    --essential

sudo reboot
```

### Virtual Machine

```bash
sudo python3 debian_gaming_setup.py -y \
    --vm-tools \
    --steam \
    --lutris \
    --gamemode \
    --essential

# Don't forget to enable 3D acceleration in VM settings!
sudo reboot
```

### Specialized: Roblox Player

```bash
sudo python3 debian_gaming_setup.py -y \
    --sober \
    --essential \
    --controllers

# No reboot needed (Flatpak only)
```

### Specialized: Mobile Gaming

```bash
sudo python3 debian_gaming_setup.py -y \
    --waydroid \
    --controllers \
    --essential

# Requires Wayland session
sudo reboot
```

---

## 🧪 Path C: Test First (Dry-Run)

### Step 1: Test Installation

```bash
wget https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/debian_gaming_setup.py

sudo python3 debian_gaming_setup.py --dry-run \
    --nvidia \
    --all-platforms \
    --optimize
```

**You'll see:**
```
════════════════════════════════════════
DRY RUN MODE - No changes will be made
════════════════════════════════════════

[DRY RUN] Would execute: apt-get update
[DRY RUN] Would execute: apt-get upgrade -y
[DRY RUN] Would install: nvidia-driver-*
[DRY RUN] Would install: steam-installer
...
```

### Step 2: Review Output

Look for:
- ✓ Components that would be installed
- ✓ Commands that would be executed
- ⚠️ Any warnings or potential issues

### Step 3: Run For Real

```bash
# If everything looks good, run without --dry-run
sudo python3 debian_gaming_setup.py -y \
    --nvidia \
    --all-platforms \
    --optimize

sudo reboot
```

---

## 🎮 After Installation

### 1. Essential Post-Install Steps

**Configure Steam (Required):**
1. Launch Steam
2. Settings → Compatibility
3. Enable Steam Play for all titles
4. Select Proton Experimental
5. Restart Steam

**Configure vkBasalt (Optional):**
```bash
# Already configured by script, but you can customize
nano ~/.config/vkBasalt/vkBasalt.conf
```

Enable for games:
```
# Steam launch options:
ENABLE_VKBASALT=1 %command%
```

**Configure MangoHud (Optional):**
```bash
mkdir -p ~/.config/MangoHud
nano ~/.config/MangoHud/MangoHud.conf
```

Example config:
```ini
fps
frame_timing=1
cpu_temp
gpu_temp
position=top-left
```

Enable for games:
```
# Steam launch options:
mangohud %command%
```

### 2. Use Performance Launcher

```bash
# The script created this for you
~/launch-game.sh steam
~/launch-game.sh lutris

# Or system-wide (if you chose that option)
launch-game steam
```

**What it does:**
- ✓ Enables GameMode
- ✓ Sets CPU to performance mode
- ✓ Adjusts process priority
- ✓ Restores settings after game exits

### 3. Install Your First Game

**Recommended first games:**

**Native Linux (Easy):**
- Counter-Strike 2 (free) - FPS
- Portal 2 - Puzzle
- Dota 2 (free) - MOBA
- Team Fortress 2 (free) - FPS

**Proton (Test Compatibility):**
- Stardew Valley - Low requirement, works great
- Terraria - 2D, excellent performance
- Hades - 3D but optimized
- Hollow Knight - 2D platformer

**How to install:**
1. Open Steam
2. Search for game
3. Click Install
4. Wait for download
5. Click Play!

### 4. Test Performance Overlay

```bash
# Launch game with MangoHud
# In Steam: Right-click game → Properties → Launch Options
mangohud %command%

# Or use performance launcher
~/launch-game.sh steam
```

**You should see:**
- FPS counter
- Frame time graph
- GPU usage
- CPU usage
- Temperatures

**Toggle on/off:** Shift+F12 (default)

---

## 🐛 Common First-Time Issues

### Issue: "Must be run with sudo"

**Solution:**
```bash
sudo python3 debian_gaming_setup.py
```
Always use `sudo`.

### Issue: Steam won't launch

**Solutions:**
```bash
# Run from terminal to see errors
steam

# Clear cache
rm -rf ~/.steam/steam/appcache/

# Reinstall
sudo apt-get install --reinstall steam-installer
```

### Issue: No GPU detected

**Check:**
```bash
lspci | grep -i vga
```

**If NVIDIA:**
```bash
sudo python3 debian_gaming_setup.py --nvidia
```

**If AMD:**
```bash
sudo python3 debian_gaming_setup.py --amd
```

### Issue: Proton games won't start

**Solutions:**
1. Verify Proton is enabled in Steam settings
2. Try different Proton version (Properties → Compatibility)
3. Check ProtonDB: https://www.protondb.com
4. View logs: `~/.steam/steam/logs/`

### Issue: Low FPS / Poor Performance

**Checks:**
1. Verify GPU drivers loaded:
   ```bash
   nvidia-smi  # NVIDIA
   glxinfo | grep renderer  # AMD/Intel
   ```

2. Use performance launcher:
   ```bash
   ~/launch-game.sh steam
   ```

3. Enable GameMode in game settings

4. Check if running on integrated GPU (laptops):
   ```bash
   prime-select query  # NVIDIA laptops
   ```

### Issue: Controller not detected

**Check:**
```bash
ls /dev/input/js*
jstest /dev/input/js0
```

**Fix:**
```bash
sudo python3 debian_gaming_setup.py --controllers
```

### Issue: Waydroid won't start

**Requirements:**
- Wayland session (check: `echo $XDG_SESSION_TYPE`)
- Kernel modules loaded

**Initialize:**
```bash
sudo waydroid init
waydroid session start
waydroid show-full-ui
```

---

## 📊 Verification Checklist

After installation, verify:

- [ ] System rebooted
- [ ] GPU drivers working (`nvidia-smi` or `glxinfo`)
- [ ] Steam launches
- [ ] Proton enabled in Steam settings
- [ ] At least one game installed
- [ ] Game launches and runs
- [ ] Performance overlay shows (if MangoHud installed)
- [ ] Logs show no critical errors
- [ ] Performance launcher works

**Check logs:**
```bash
cat ~/gaming_setup_logs/gaming_setup_*.log | tail -100
grep ERROR ~/gaming_setup_logs/gaming_setup_*.log
```

---

## 🎯 Next Steps

### Learn More

1. **ProtonDB** - Check game compatibility
   - https://www.protondb.com
   - Community fixes and tips
   
2. **Lutris** - Install non-Steam games
   - https://lutris.net/games
   - One-click installers
   
3. **MangoHud Configuration**
   - https://github.com/flightlessmango/MangoHud
   - Customize overlay
   
4. **GE-Proton** - Custom Proton builds
   - Already installed by script
   - Select in game properties

### Advanced Configuration

See [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md) for:
- All CLI options explained
- Advanced optimizations
- Per-game configurations
- Troubleshooting guide
- Virtual machine tips

---

## 🆘 Getting Help

### Self-Help Resources

1. **Check logs first:**
   ```bash
   cat ~/gaming_setup_logs/gaming_setup_*.log
   ```

2. **Search ProtonDB** for game-specific issues

3. **Review documentation:**
   - [README.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/README.md) - Overview
   - [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md) - Complete reference
   - [CHANGELOG.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CHANGELOG.md) - Recent changes

### Report Issues

If you encounter problems:
1. Note your Linux distribution and version
2. Note your GPU model
3. Save relevant log excerpts
4. Report on GitHub Issues

**Include:**
- Distribution: `lsb_release -a`
- GPU: `lspci | grep -i vga`
- Logs: `~/gaming_setup_logs/gaming_setup_*.log`

---

## 📝 Quick Command Reference

```bash
# Installation
sudo python3 debian_gaming_setup.py              # Interactive
sudo python3 debian_gaming_setup.py --dry-run    # Test
sudo python3 debian_gaming_setup.py -y [OPTIONS] # Automated

# Post-Installation
nvidia-smi                           # Check NVIDIA driver
glxinfo | grep "OpenGL renderer"     # Check AMD/Intel
~/launch-game.sh steam               # Launch with optimizations

# Configuration
nano ~/.config/MangoHud/MangoHud.conf    # MangoHud settings
nano ~/.config/vkBasalt/vkBasalt.conf    # vkBasalt settings

# Troubleshooting
cat ~/gaming_setup_logs/gaming_setup_*.log  # View logs
steam                                        # Run Steam from terminal
```

---

## ✅ Success!

**You're now ready to game on Linux!** 🎮

- Drivers installed and working
- Gaming platforms configured
- Performance tools enabled
- Ready to play

**Enjoy your games!**

---

**Questions?** See [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md) for detailed help.

**Version:** 2.1.0 | Updated: January 2026
