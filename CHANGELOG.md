# Changelog

All notable changes to the Debian-Based Gaming Setup Script will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.1.0] - 2026-01-05

### Added ✨
- **SOBER (Roblox on Linux)** - Full Roblox platform support via Flatpak
  - Smart installation with version checking
  - Automatic Flatpak setup
  - `--sober` CLI flag
- **Waydroid (Android Container)** - Run Android apps and mobile games
  - Wayland/X11 session detection
  - Automatic repository setup
  - Post-install instructions provided
  - `--waydroid` CLI flag
- **GreenWithEnvy (GWE)** - NVIDIA GPU control and monitoring
  - GPU vendor detection
  - Overclocking and fan control support
  - `--gwe` CLI flag
- **vkBasalt** - Vulkan post-processing layer (ReShade-like)
  - Automatic configuration file generation
  - CAS, FXAA, and other effects
  - Toggle key support (Home key default)
  - `--vkbasalt` CLI flag
- **ReShade Setup Information** - Comprehensive ReShade guidance for Linux
  - Multiple implementation options explained
  - Offers vkBasalt installation
  - `--reshade` CLI flag
- **Mod Manager Tools** - Game modding setup assistance
  - Mod Organizer 2 (via Lutris)
  - Vortex Mod Manager information
  - r2modman installation
  - `--mod-managers` CLI flag

### Fixed 🐛
- **Ubuntu 24.04 Compatibility**
  - Changed `linux-cpupower` to `linux-tools-generic` (package name fix)
  - Enhanced error handling for optional packages
  - Fallback logic for missing packages
- **MangoHud Installation on Ubuntu 24.04**
  - Added version detection before PPA usage
  - Default repository installation for Ubuntu 24.04+
  - PPA only used for older Ubuntu versions
  - Better error messages and manual installation guidance
- **Repository Cleanup**
  - Enhanced `clean_broken_repos()` to handle MangoHud PPAs
  - Automatic backup before removal
  - Both Lutris and MangoHud PPA cleanup

### Changed 🔄
- **--all-platforms flag** - Now excludes specialized platforms (SOBER, Waydroid)
- **Installation summary** - Added new tools (SOBER, GWE, vkBasalt, Waydroid)
- **Error handling** - Improved graceful degradation across all new features
- **Configuration system** - Added 6 new boolean flags to InstallationConfig

### Documentation 📖
- Created **NEW_FEATURES_EXPANSION.md** - Detailed documentation of v2.1 features
- Created **BUGFIX_CHANGELOG.md** - Ubuntu 24.04 compatibility fixes
- Updated **README.md** - Added all new platforms and utilities
- Enhanced **Usage_Guide.md** - Complete documentation for 51+ CLI options
- Updated **Quick_Start.md** - New platform examples

### Statistics 📊
- Lines of code: 3,341 (+414 from v2.0.1)
- CLI arguments: 51+ (+11 new flags)
- Major features: 33 (+8 new additions)
- Documentation: 2,700+ lines

---

## [2.0.1] - 2026-01-04

### Fixed 🐛
- **Ubuntu 24.04 Package Issues**
  - Fixed `linux-cpupower` package name (changed to `linux-tools-generic`)
  - Fixed MangoHud PPA issues on Ubuntu 24.04
  - Enhanced repository cleanup for broken PPAs

### Added
- Better error handling for package installation failures
- Fallback logic for optional packages
- Manual installation guidance when automated methods fail

### Documentation
- Created BUGFIX_CHANGELOG.md with detailed fix information
- Updated compatibility matrix for Ubuntu 24.04

---

## [2.0.0] - 2026-01-03

### Added ✨
- **CLI Automation System** - 40+ command-line arguments
  - `--dry-run` mode for safe testing
  - `--yes` flag for unattended installation
  - `--verbose` flag for debug output
  - Platform-specific flags (--nvidia, --amd, --intel, --vm-tools)
  - Tool-specific flags (--steam, --lutris, --heroic, etc.)
- **Multi-Distribution Support**
  - Ubuntu (20.04, 22.04, 24.04)
  - Linux Mint (20, 21, 22)
  - Debian (11, 12)
  - Pop!_OS, Elementary, Zorin, Kali
- **Enhanced System Detection**
  - Distribution family detection
  - Desktop environment detection
  - WSL detection
  - Extended VM type detection (Hyper-V, Xen, Parallels)
- **MangoHud Performance Overlay**
  - Automatic installation
  - Configuration guidance
  - Integration with performance launcher
- **Goverlay** - MangoHud GUI configuration tool
- **Mumble** - Voice chat for gaming
- **State Management System**
  - Installation state tracking (JSON)
  - Rollback framework (partial implementation)
  - Failed operations tracking
- **GE-Proton Auto-Installer**
  - Automatic latest version download from GitHub
  - Extraction to correct Steam directory
  - Proper ownership management
- **Enhanced Documentation**
  - Comprehensive README.md
  - Detailed Quick_Start.md
  - Complete Usage_Guide.md
  - COMPLETE_COMPARISON.md technical documentation

### Changed 🔄
- **InstallationConfig Dataclass** - Type-safe configuration system
- **Argument Parser** - Professional help formatting with examples
- **Error Handling** - Better error messages and graceful degradation
- **Package Management** - Enhanced version checking and update detection
- **Performance Launcher** - Improved error handling and feedback

### Preserved 💯
- All original functionality from v1.0
- Smart installation prompts with version checking
- Complete installation summary with actual versions
- 130-line performance launcher script
- Repository cleanup for broken PPAs
- VM-specific instructions and tips
- CPU governor sudo configuration
- All detection methods with cross-validation
- Complete error handling and logging

### Statistics 📊
- Lines of code: 2,927 (was ~1,000 in v1.0)
- CLI arguments: 40+
- Documentation: 2,721 lines across 3 primary docs

---

## [1.0.0] - 2025-12-15

### Initial Release 🎉

The original Ubuntu 24.04 gaming setup script with core functionality:

### Features
- **Interactive Installation** - User-friendly prompts
- **GPU Driver Installation**
  - NVIDIA proprietary drivers
  - AMD Mesa drivers
  - Intel Mesa drivers
- **VM Guest Tools**
  - VMware Tools
  - VirtualBox Guest Additions
  - KVM/QEMU tools
- **Gaming Platforms**
  - Steam
  - Lutris (via Flatpak)
  - Heroic Games Launcher
  - GameMode
- **Compatibility Layers**
  - Wine Staging
  - Winetricks
  - ProtonUp-Qt
- **Additional Tools**
  - Discord
  - OBS Studio
  - Controller support
- **System Optimizations**
  - sysctl gaming parameters
  - CPU performance governor
  - Performance launcher script
- **Essential Features**
  - Smart version checking
  - Installation summary with versions
  - Repository cleanup
  - Comprehensive logging

### Statistics
- Lines of code: ~1,000
- Supported platforms: 4 (Steam, Lutris, Heroic, Discord)
- Utilities: 8 tools

---

## Version History Summary

| Version | Date | Key Addition | Lines of Code |
|---------|------|-------------|---------------|
| 1.0.0 | 2025-12-15 | Initial release | ~1,000 |
| 2.0.0 | 2026-01-03 | CLI automation, multi-distro | 2,927 |
| 2.0.1 | 2026-01-04 | Ubuntu 24.04 fixes | 2,927 |
| 2.1.0 | 2026-01-05 | New platforms & utilities | 3,341 |

---

## Upgrade Notes

### From 2.0.x to 2.1.0

**No Breaking Changes** - All 2.0.x features preserved.

**New Features Available:**
```bash
# Try new platforms
sudo python3 debian_gaming_setup.py --sober
sudo python3 debian_gaming_setup.py --waydroid

# Try new utilities
sudo python3 debian_gaming_setup.py --gwe
sudo python3 debian_gaming_setup.py --vkbasalt
```

**Ubuntu 24.04 Users:**
- Package installation issues resolved
- MangoHud now installs from default repos
- No manual fixes needed

### From 1.0.0 to 2.x.x

**Major Changes:**
- 40+ CLI arguments added (backward compatible)
- Interactive mode still works exactly as before
- New features available via CLI flags
- Enhanced error handling and logging
- Multi-distribution support

**To Upgrade:**
1. Download new version
2. Run with your preferred method:
   - Interactive: `sudo python3 debian_gaming_setup.py`
   - Automated: `sudo python3 debian_gaming_setup.py -y [OPTIONS]`

---

## Future Roadmap

### Planned for v2.2.0
- [ ] Complete rollback implementation
- [ ] Flatpak fallback for more tools
- [ ] Pre-flight package availability check
- [ ] Distribution-specific package mapping
- [ ] Automated PPA availability checking

### Under Consideration
- [ ] GUI version of the script
- [ ] Integration tests for multiple distributions
- [ ] Package cache for known working configurations
- [ ] Custom kernel installation automation
- [ ] Game-specific optimizations database

---

## Contributing

See [CONTRIBUTING.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/CONTRIBUTING.md) for how to contribute to this project.

---

## Links

- **Repository:** [Debian-Gaming-Setup-Project](https://github.com/Sandler73/Debian-Gaming-Setup-Project)
- **Issues:** [Issues](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues)
- **Releases:** [Releases](https://github.com/Sandler73/Debian-Gaming-Setup-Project/releases)
- **Documentation:** See [README.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/README.md), [Quick_Start.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Quick_Start.md), and [Usage_Guide.md](https://github.com/Sandler73/Debian-Gaming-Setup-Project/blob/main/Usage_Guide.md)

---

**Keep gaming on Linux! 🎮**
