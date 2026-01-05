# Debian-Based Gaming Setup Script v2.1

**A comprehensive automated gaming environment setup for Debian-based Linux distributions**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.6+](https://img.shields.io/badge/python-3.6+-blue.svg)](https://www.python.org/downloads/)
[![Ubuntu](https://img.shields.io/badge/Ubuntu-24.04%20%7C%2022.04%20%7C%2020.04-orange.svg)](https://ubuntu.com/)
[![Maintained](https://img.shields.io/badge/Maintained-Yes-green.svg)](https://github.com/Sandler73/Debian-Gaming-Setup-Project)

Transform your Debian-based Linux system into a complete gaming powerhouse with a single command. This script automates the installation and configuration of GPU drivers, gaming platforms, compatibility layers, performance tools, and system optimizations with both interactive and automated modes.

---

## 🌟 What's New in v2.1

- ✨ **SOBER** - Play Roblox on Linux
- ✨ **Waydroid** - Run Android apps and mobile games  
- ✨ **GreenWithEnvy** - NVIDIA GPU monitoring and overclocking
- ✨ **vkBasalt** - ReShade-like post-processing for Vulkan games
- ✨ **Mod Manager Tools** - Complete modding setup
- 🐛 **Ubuntu 24.04 Fixes** - Package compatibility resolved
- 📖 **Enhanced Documentation** - Complete usage guides

[See CHANGELOG.md for full details](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CHANGELOG.md)

---

## 🚀 Quick Start

### One-Command Installation

```bash
# Download
wget https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/debian_gaming_setup.py

# Interactive mode (recommended for first-time users)
sudo python3 debian_gaming_setup.py

# Or automated (NVIDIA example)
sudo python3 debian_gaming_setup.py -y \
    --nvidia --all-platforms --optimize --launcher
```

**That's it!** Reboot after installation and start gaming! 🎮

See [Quick_Start](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md) for detailed first-time setup guide.

---

## ⭐ Key Features

- ✅ **6 Gaming Platforms** - Steam, Lutris, Heroic, ProtonUp-Qt, Roblox (SOBER), Android (Waydroid)
- ✅ **All GPU Vendors** - NVIDIA, AMD, Intel with automatic detection
- ✅ **VM Support** - VMware, VirtualBox, KVM, Hyper-V, Xen
- ✅ **51+ CLI Arguments** - Full automation capabilities
- ✅ **Smart Prompts** - Shows versions, detects updates, intelligent recommendations
- ✅ **Dry-Run Mode** - Test before installing
- ✅ **Performance Tools** - GameMode, MangoHud, vkBasalt, CPU governor
- ✅ **Visual Enhancement** - vkBasalt post-processing, ReShade guidance
- ✅ **Comprehensive Logging** - Detailed logs with error tracking
- ✅ **10+ Distributions** - Ubuntu, Mint, Debian, Pop!_OS, Elementary, Zorin, Kali

---

## 📦 What Gets Installed

### Core Components
- **GPU Drivers** - NVIDIA/AMD/Intel or VM guest tools
- **Gaming Platforms** - Steam, Lutris, Heroic, ProtonUp-Qt
- **Compatibility** - Wine, Winetricks, GE-Proton
- **Performance** - GameMode, MangoHud, Goverlay
- **Utilities** - Discord, OBS, Mumble, controller support

### New in v2.1 ✨
- **SOBER** - Roblox on Linux via Flatpak
- **Waydroid** - Full Android container for mobile games
- **GreenWithEnvy** - NVIDIA GPU control and monitoring
- **vkBasalt** - Vulkan post-processing (ReShade-like)
- **Mod Managers** - MO2, Vortex, r2modman setup

[See complete list in Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md#component-details)

---

## 💻 Supported Systems

### Tested & Verified ✅
- Ubuntu 24.04, 22.04, 20.04
- Linux Mint 22, 21, 20
- Debian 12 (Bookworm), 11 (Bullseye)
- Pop!_OS 22.04+
- Elementary OS 7+
- Zorin OS 17+

### Hardware Support
- **Physical GPUs** - NVIDIA GeForce/Quadro/Tesla, AMD Radeon, Intel HD/Iris/Arc
- **Virtual Machines** - VMware, VirtualBox, KVM/QEMU, Hyper-V

[See full compatibility matrix](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md#supported-systems)

---

## 🎯 Usage Examples

### Complete Setups

**NVIDIA Gaming PC:**
```bash
sudo python3 debian_gaming_setup.py -y \
    --nvidia --all-platforms --wine --ge-proton \
    --gamemode --mangohud --gwe --vkbasalt \
    --discord --obs --optimize --launcher
```

**AMD Gaming PC:**
```bash
sudo python3 debian_gaming_setup.py -y \
    --amd --all-platforms --wine --ge-proton \
    --gamemode --mangohud --vkbasalt --optimize
```

**Virtual Machine:**
```bash
sudo python3 debian_gaming_setup.py -y \
    --vm-tools --steam --lutris --gamemode
```

### Specialized Setups

**Roblox Player:**
```bash
sudo python3 debian_gaming_setup.py -y --sober
```

**Mobile Gaming:**
```bash
sudo python3 debian_gaming_setup.py -y --waydroid --controllers
```

**Visual Enhancement:**
```bash
sudo python3 debian_gaming_setup.py -y --vkbasalt --reshade --mangohud
```

[See more examples in Usage_Guide.md](Usage_Guide.md#usage-examples)

---

## 🎛️ Command-Line Options

### Quick Reference
```
General:          -y, --yes, --dry-run, --verbose
GPU/Drivers:      --nvidia, --amd, --intel, --vm-tools
Platforms:        --steam, --lutris, --heroic, --sober, --waydroid
Compatibility:    --wine, --ge-proton
Performance:      --gamemode, --mangohud, --gwe
Graphics:         --vkbasalt, --reshade
Tools:            --discord, --obs, --mod-managers, --controllers
System:           --optimize, --launcher
```

[Complete CLI reference in Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md#command-line-options-reference)

---

## 🎮 Post-Installation

### Essential Steps

1. **Reboot** (required for drivers)
   ```bash
   sudo reboot
   ```

2. **Verify GPU drivers**
   ```bash
   nvidia-smi  # NVIDIA
   glxinfo | grep "OpenGL renderer"  # AMD/Intel
   ```

3. **Configure Steam**
   - Settings → Compatibility
   - Enable "Steam Play for all titles"
   - Select Proton Experimental

4. **Test with a game**
   - Native: Counter-Strike 2, Portal 2 (free)
   - Proton: Stardew Valley, Terraria

5. **Use performance launcher**
   ```bash
   ~/launch-game.sh steam
   ```

[Detailed post-install guide in Quick_Start.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md#after-installation)

---

## 📖 Documentation

| Document | Purpose | Best For |
|----------|---------|----------|
| [README.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/README.md) | Overview & quick start | Everyone |
| [Quick_Start.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md) | Step-by-step guide | First-time users |
| [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md) | Complete reference | All users |
| [CHANGELOG.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CHANGELOG.md) | Version history | Tracking changes |
| [CONTRIBUTING.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CONTRIBUTING.md) | Contribution guide | Contributors |
| [SECURITY.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/SECURITY.md) | Security policies | Reporting issues |

---

## 🐛 Troubleshooting

### Common Issues

**"Package has no installation candidate"**
```bash
sudo apt-get update && sudo apt-get upgrade
```

**NVIDIA driver not loading**
```bash
sudo apt-get install --reinstall nvidia-driver-*
sudo update-initramfs -u && sudo reboot
```

**Steam won't launch**
```bash
steam  # Run from terminal to see errors
rm -rf ~/.steam/steam/appcache/  # Clear cache
```

**Check logs**
```bash
cat ~/gaming_setup_logs/gaming_setup_*.log | tail -100
grep ERROR ~/gaming_setup_logs/gaming_setup_*.log
```

[Full troubleshooting guide in Usage_Guide.md](Usage_Guide.md#troubleshooting)

---

## 🤝 Contributing

Contributions welcome! See [CONTRIBUTING.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CONTRIBUTING.md) for guidelines.

**Quick steps:**
1. Fork repository
2. Create feature branch
3. Test with `--dry-run`
4. Submit pull request

**Areas needing help:**
- Testing on different distributions
- Additional platform support
- Documentation improvements
- Bug fixes

---

## 📊 Project Stats

- **3,341 lines** of Python code
- **51+ CLI arguments** for automation
- **6 gaming platforms** supported
- **15+ utilities** included
- **10+ distributions** tested
- **Active maintenance** ongoing

---

## 🌟 Acknowledgments

**Inspired by:**
- Original Ubuntu gaming setup script
- GameReady, linux-gaming, Gamebuntu projects

**Special thanks:**
- Valve (Steam, Proton)
- Lutris developers
- GloriousEggroll (GE-Proton)
- Feral Interactive (GameMode)
- MangoHud developers
- Open-source gaming community

---

## 📜 License

[MIT License](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/LICENSE) - Free to use, modify, and distribute.

---

## ⚠️ Disclaimer

This script makes system-level changes. Always:
- ✅ Backup important data
- ✅ Test with `--dry-run` first
- ✅ Review logs for errors
- ✅ Understand what's being installed

**Use at your own risk.** No warranty provided.

---

## 🚀 Get Started

```bash
# Download
wget https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/debian_gaming_setup.py

# Test (safe)
sudo python3 debian_gaming_setup.py --dry-run

# Install (interactive)
sudo python3 debian_gaming_setup.py

# Install (automated)
sudo python3 debian_gaming_setup.py -y --all-platforms --optimize
```

**Ready to game on Linux?** See [Quick_Start.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md)! 🎮

---

<div align="center">

**⭐ Star this repo if it helped you! ⭐**

Made with ❤️ for the Linux gaming community

**Version 2.1.0** | Updated January 2026

[Report Issue](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues) | [Request Feature](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues/new) | [Contribute](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/CONTRIBUTING.md)

</div>
