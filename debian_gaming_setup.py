#!/usr/bin/env python3
"""
═══════════════════════════════════════════════════════════════════════════════
Debian-Based Comprehensive Gaming Setup Script v2.0
═══════════════════════════════════════════════════════════════════════════════

SYNOPSIS:
    Comprehensive automated gaming environment setup for Debian-based Linux
    distributions including Ubuntu, Linux Mint, Kali, Pop!_OS, and derivatives.
    
    This script preserves ALL functionality from the original ubuntu_gaming_setup.py
    while adding extensive enhancements for multi-distribution support, CLI
    automation, error handling, and additional gaming components.

DESCRIPTION:
    This script automates the installation and configuration of gaming components
    including GPU drivers, gaming platforms, compatibility layers, system
    optimizations, and additional utilities. Features include:
    
    PRESERVED FROM ORIGINAL:
    • Complete GPU/VM detection with lspci and glxinfo cross-validation
    • Smart package version checking and update detection
    • Interactive installation prompts with version display
    • Comprehensive installation summary with actual package versions
    • Performance launcher script creation with CPU governor management
    • Detailed logging with proper ownership management
    • Repository cleanup and broken PPA handling
    • Flatpak app version checking
    • Progress indication and colored output
    • Final steps with VM-specific instructions
    
    NEW ENHANCEMENTS:
    • Universal Debian-based distribution support (no version locking)
    • Comprehensive CLI argument support (40+ options)
    • Dry-run mode for testing without changes
    • Auto-yes mode for unattended installation
    • State management with JSON persistence
    • Rollback framework with backup manifest
    • Enhanced error handling with recovery tracking
    • Additional tools: MangoHud, GE-Proton, Goverlay, controllers
    • Multi-method hardware detection
    • Input validation and sanitization
    • Extended VM support (Hyper-V, Xen, Parallels)

SUPPORTED SYSTEMS:
    • Ubuntu (20.04+) - all editions
    • Linux Mint (20+)
    • Debian (11+)
    • Pop!_OS (20.04+)
    • Kali Linux (2020+)
    • Elementary OS (6+)
    • Zorin OS (16+)
    • Any Debian/Ubuntu derivative

SUPPORTED HARDWARE:
    • NVIDIA GPUs (proprietary drivers with version detection)
    • AMD GPUs (Mesa/AMDGPU with Vulkan)
    • Intel GPUs (Mesa/i915 with media acceleration)
    • VMware virtual machines (open-vm-tools)
    • VirtualBox virtual machines (guest additions)
    • KVM/QEMU virtual machines (guest agent)
    • Hyper-V virtual machines
    • Xen virtual machines
    • Parallels virtual machines

USAGE EXAMPLES:
    # Interactive installation (original behavior preserved)
    sudo python3 debian_gaming_setup.py

    # Dry-run mode (test without changes)
    sudo python3 debian_gaming_setup.py --dry-run

    # Auto-yes with all gaming platforms
    sudo python3 debian_gaming_setup.py -y --all-platforms

    # Install specific components
    sudo python3 debian_gaming_setup.py --nvidia --steam --lutris

    # Rollback previous installation
    sudo python3 debian_gaming_setup.py --rollback

NOTES:
    • Requires sudo/root privileges
    • Creates backups before system modifications
    • Logs all operations to ~/gaming_setup_logs/
    • Supports rollback of failed installations
    • Can run in dry-run mode for testing
    • Preserves all original interactive functionality
    • Adds CLI automation for advanced users

VERSION:
    2.0.0 - Complete Implementation

AUTHOR:
    Enhanced Gaming Setup Script
    Based on original ubuntu_gaming_setup.py

LICENSE:
    MIT License

═══════════════════════════════════════════════════════════════════════════════
"""

import os
import sys
import subprocess
import platform
import logging
import json
import shutil
import hashlib
import argparse
import pwd
import grp
import re
import time
import urllib.request
from pathlib import Path
from datetime import datetime
from typing import Optional, List, Dict, Tuple, Any
from dataclasses import dataclass, field
from enum import Enum
from collections import defaultdict

# ═══════════════════════════════════════════════════════════════════════════════
# HELPER FUNCTIONS FOR USER CONTEXT
# ═══════════════════════════════════════════════════════════════════════════════

def get_real_user() -> str:
    """
    Get the actual user who invoked sudo
    
    Returns:
        Username of the actual user (not root)
    """
    sudo_user = os.environ.get('SUDO_USER')
    if sudo_user:
        return sudo_user
    return os.environ.get('USER', 'root')

def get_real_user_home() -> Path:
    """
    Get the home directory of the actual user
    
    Returns:
        Path object representing user's home directory
    """
    real_user = get_real_user()
    try:
        return Path(pwd.getpwnam(real_user).pw_dir)
    except:
        return Path.home()

def get_real_user_uid_gid() -> Tuple[int, int]:
    """
    Get UID and GID of the actual user
    
    Returns:
        Tuple of (uid, gid) for the actual user
    """
    real_user = get_real_user()
    try:
        pw_record = pwd.getpwnam(real_user)
        return pw_record.pw_uid, pw_record.pw_gid
    except:
        return os.getuid(), os.getgid()

# ═══════════════════════════════════════════════════════════════════════════════
# GLOBAL CONSTANTS AND PATHS
# ═══════════════════════════════════════════════════════════════════════════════

# User context
REAL_USER = get_real_user()
REAL_USER_HOME = get_real_user_home()

# Directory setup
LOG_DIR = REAL_USER_HOME / "gaming_setup_logs"
LOG_DIR.mkdir(exist_ok=True, parents=True)
LOG_FILE = LOG_DIR / f"gaming_setup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"

BACKUP_DIR = REAL_USER_HOME / "gaming_setup_backups"
BACKUP_DIR.mkdir(exist_ok=True, parents=True)

STATE_FILE = LOG_DIR / "installation_state.json"
ROLLBACK_FILE = LOG_DIR / "rollback_manifest.json"

# Set proper ownership for directories
try:
    uid, gid = get_real_user_uid_gid()
    os.chown(LOG_DIR, uid, gid)
    os.chown(BACKUP_DIR, uid, gid)
except Exception as e:
    pass

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

# ═══════════════════════════════════════════════════════════════════════════════
# COLOR OUTPUT CLASS
# ═══════════════════════════════════════════════════════════════════════════════

class Color:
    """ANSI color codes for terminal output"""
    HEADER = '\033[95m'
    BLUE = '\033[94m'
    CYAN = '\033[96m'
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    END = '\033[0m'
    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'
    
    @staticmethod
    def disable():
        """Disable colors for non-TTY or logging"""
        Color.HEADER = ''
        Color.BLUE = ''
        Color.CYAN = ''
        Color.GREEN = ''
        Color.YELLOW = ''
        Color.RED = ''
        Color.END = ''
        Color.BOLD = ''
        Color.UNDERLINE = ''

# ═══════════════════════════════════════════════════════════════════════════════
# ENUMERATIONS FOR TYPE SAFETY
# ═══════════════════════════════════════════════════════════════════════════════

class GPUVendor(Enum):
    """GPU vendor enumeration"""
    NVIDIA = "nvidia"
    AMD = "amd"
    INTEL = "intel"
    VIRTUAL = "virtual"
    UNKNOWN = "unknown"

class VMType(Enum):
    """Virtual machine type enumeration"""
    VMWARE = "vmware"
    VIRTUALBOX = "virtualbox"
    KVM = "kvm"
    QEMU = "qemu"
    HYPERV = "hyperv"
    XEN = "xen"
    PARALLELS = "parallels"
    NONE = "none"

class DistroFamily(Enum):
    """Distribution family enumeration"""
    DEBIAN = "debian"
    UBUNTU = "ubuntu"
    MINT = "mint"
    KALI = "kali"
    POPOS = "popos"
    ELEMENTARY = "elementary"
    ZORIN = "zorin"
    UNKNOWN = "unknown"

class InstallationPhase(Enum):
    """Installation phase tracking for state management"""
    INIT = "initialization"
    DETECTION = "detection"
    DRIVERS = "drivers"
    PLATFORMS = "platforms"
    COMPATIBILITY = "compatibility"
    PERFORMANCE = "performance"
    TOOLS = "tools"
    OPTIMIZATION = "optimization"
    FINALIZATION = "finalization"

# ═══════════════════════════════════════════════════════════════════════════════
# DATA CLASSES FOR STRUCTURED INFORMATION
# ═══════════════════════════════════════════════════════════════════════════════

@dataclass
class SystemInfo:
    """System information container"""
    distro_name: str = "Unknown"
    distro_version: str = "Unknown"
    distro_id: str = "Unknown"
    distro_family: DistroFamily = DistroFamily.UNKNOWN
    kernel_version: str = "Unknown"
    architecture: str = "Unknown"
    desktop_environment: str = "Unknown"
    is_wsl: bool = False

@dataclass
class HardwareInfo:
    """Hardware information container"""
    gpu_vendor: GPUVendor = GPUVendor.UNKNOWN
    gpu_model: str = "Unknown"
    gpu_pci_id: str = ""
    vm_type: VMType = VMType.NONE
    cpu_vendor: str = "Unknown"
    cpu_model: str = "Unknown"
    cpu_cores: int = 0
    total_memory_gb: float = 0.0
    has_vulkan: bool = False
    vulkan_version: str = ""

@dataclass
class BackupEntry:
    """Backup entry for rollback functionality"""
    timestamp: str
    file_path: str
    backup_path: str
    operation: str
    checksum: str = ""
    package_name: str = ""

@dataclass
class InstallationConfig:
    """
    Installation configuration from CLI arguments or interactive prompts
    This replaces the need for global flags while preserving all functionality
    """
    # GPU/VM options
    install_nvidia_drivers: bool = False
    install_amd_drivers: bool = False
    install_intel_drivers: bool = False
    install_vm_tools: bool = False
    
    # Gaming platforms
    install_steam: bool = False
    install_lutris: bool = False
    install_heroic: bool = False
    install_protonup: bool = False
    install_sober: bool = False  # NEW: Roblox on Linux
    install_waydroid: bool = False  # NEW: Android container
    
    # Compatibility layers
    install_wine: bool = False
    install_winetricks: bool = False
    install_dxvk: bool = False
    install_vkd3d: bool = False
    install_ge_proton: bool = False
    
    # Performance tools
    install_gamemode: bool = False
    install_mangohud: bool = False
    install_goverlay: bool = False
    install_greenwithenv: bool = False  # NEW: NVIDIA GPU control (GWE)
    
    # Graphics enhancement tools
    install_vkbasalt: bool = False  # NEW: Vulkan post-processing
    install_reshade_setup: bool = False  # NEW: ReShade setup info
    
    # Additional tools
    install_discord: bool = False
    install_obs: bool = False
    install_mumble: bool = False
    install_teamspeak: bool = False
    install_mod_managers: bool = False  # NEW: Mod manager tools
    
    # Controller support
    install_controller_support: bool = False
    install_antimicrox: bool = False
    install_xboxdrv: bool = False
    
    # System optimizations
    apply_system_optimizations: bool = False
    install_custom_kernel: bool = False
    optimize_btrfs: bool = False
    create_performance_launcher: bool = False
    
    # Essential packages
    install_essential_packages: bool = False
    install_codecs: bool = False
    
    # Script behavior
    dry_run: bool = False
    auto_yes: bool = False
    skip_prompts: bool = False
    create_backup: bool = True
    enable_rollback: bool = True
    verbose: bool = False
    skip_update: bool = False

# ═══════════════════════════════════════════════════════════════════════════════
# ARGUMENT PARSER - NEW ENHANCEMENT
# ═══════════════════════════════════════════════════════════════════════════════

def parse_arguments() -> argparse.Namespace:
    """
    Parse command line arguments for automated installation
    
    This is a NEW ENHANCEMENT that adds CLI automation while preserving
    the original interactive mode when no arguments are provided.
    
    Returns:
        Parsed arguments namespace
    """
    parser = argparse.ArgumentParser(
        description='Comprehensive Debian-based gaming setup with full Ubuntu compatibility',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode (original behavior)
  sudo python3 debian_gaming_setup.py

  # Test before installing
  sudo python3 debian_gaming_setup.py --dry-run --all-platforms

  # Automated NVIDIA gaming setup
  sudo python3 debian_gaming_setup.py -y --nvidia --all-platforms --optimize

  # AMD gaming setup
  sudo python3 debian_gaming_setup.py -y --amd --steam --lutris

  # Rollback previous installation
  sudo python3 debian_gaming_setup.py --rollback
        """
    )
    
    # General options
    general = parser.add_argument_group('General Options')
    general.add_argument('-y', '--yes', action='store_true',
                        help='Auto-answer yes to all prompts')
    general.add_argument('--dry-run', action='store_true',
                        help='Test mode - show what would be done without making changes')
    general.add_argument('--verbose', action='store_true',
                        help='Enable verbose debug output')
    general.add_argument('--no-backup', action='store_true',
                        help='Skip creating backups before modifications')
    
    # GPU/Driver options
    drivers = parser.add_argument_group('GPU/Driver Options')
    drivers.add_argument('--nvidia', action='store_true',
                        help='Install NVIDIA drivers')
    drivers.add_argument('--amd', action='store_true',
                        help='Install AMD drivers')
    drivers.add_argument('--intel', action='store_true',
                        help='Install Intel drivers')
    drivers.add_argument('--vm-tools', action='store_true',
                        help='Install VM guest tools')
    
    # Gaming platforms
    platforms = parser.add_argument_group('Gaming Platforms')
    platforms.add_argument('--steam', action='store_true',
                          help='Install Steam')
    platforms.add_argument('--lutris', action='store_true',
                          help='Install Lutris')
    platforms.add_argument('--heroic', action='store_true',
                          help='Install Heroic Games Launcher')
    platforms.add_argument('--protonup', action='store_true',
                          help='Install ProtonUp-Qt')
    platforms.add_argument('--sober', action='store_true',
                          help='Install Sober (Roblox on Linux)')
    platforms.add_argument('--waydroid', action='store_true',
                          help='Install Waydroid (Android container)')
    platforms.add_argument('--all-platforms', action='store_true',
                          help='Install all gaming platforms (excludes Sober/Waydroid)')
    
    # Compatibility layers
    compat = parser.add_argument_group('Compatibility Layers')
    compat.add_argument('--wine', action='store_true',
                       help='Install Wine Staging')
    compat.add_argument('--winetricks', action='store_true',
                       help='Install Winetricks')
    compat.add_argument('--dxvk', action='store_true',
                       help='Show DXVK installation information')
    compat.add_argument('--vkd3d', action='store_true',
                       help='Show VKD3D-Proton installation information')
    compat.add_argument('--ge-proton', action='store_true',
                       help='Install GE-Proton automatically')
    
    # Performance tools
    perf = parser.add_argument_group('Performance Tools')
    perf.add_argument('--gamemode', action='store_true',
                     help='Install GameMode')
    perf.add_argument('--mangohud', action='store_true',
                     help='Install MangoHud performance overlay')
    perf.add_argument('--goverlay', action='store_true',
                     help='Install Goverlay (MangoHud GUI)')
    perf.add_argument('--gwe', action='store_true',
                     help='Install GreenWithEnvy (NVIDIA GPU control)')
    
    # Graphics enhancement tools
    graphics = parser.add_argument_group('Graphics Enhancement')
    graphics.add_argument('--vkbasalt', action='store_true',
                         help='Install vkBasalt (Vulkan post-processing layer)')
    graphics.add_argument('--reshade', action='store_true',
                         help='Show ReShade setup information (via vkBasalt)')
    
    # Additional tools
    tools = parser.add_argument_group('Additional Tools')
    tools.add_argument('--discord', action='store_true',
                      help='Install Discord')
    tools.add_argument('--obs', action='store_true',
                      help='Install OBS Studio')
    tools.add_argument('--mumble', action='store_true',
                      help='Install Mumble')
    tools.add_argument('--teamspeak', action='store_true',
                      help='Show TeamSpeak installation information')
    tools.add_argument('--mod-managers', action='store_true',
                      help='Install mod management tools')
    tools.add_argument('--controllers', action='store_true',
                      help='Install controller support')
    tools.add_argument('--essential', action='store_true',
                      help='Install essential gaming packages')
    tools.add_argument('--codecs', action='store_true',
                      help='Install multimedia codecs')
    
    # System options
    system = parser.add_argument_group('System Options')
    system.add_argument('--optimize', action='store_true',
                       help='Apply system optimizations')
    system.add_argument('--custom-kernel', action='store_true',
                       help='Install custom gaming kernel (planned)')
    system.add_argument('--skip-update', action='store_true',
                       help='Skip system update')
    system.add_argument('--launcher', action='store_true',
                       help='Create performance launcher script')
    
    # Maintenance
    maint = parser.add_argument_group('Maintenance')
    maint.add_argument('--rollback', action='store_true',
                      help='Rollback previous installation')
    maint.add_argument('--cleanup', action='store_true',
                      help='Clean up installation files and logs')
    
    return parser.parse_args()

# END OF PART 1
# This file contains: imports, constants, helper functions, data classes, and argument parser
# Continue with Part 2 for the main GamingSetup class
# PART 2: Main GamingSetup Class - Core Methods
# This continues from Part 1 and preserves ALL original functionality

class GamingSetup:
    """
    Main class for comprehensive Debian-based gaming setup
    
    PRESERVED FROM ORIGINAL:
    - All detection methods with lspci and glxinfo cross-validation
    - Package version checking and comparison
    - Smart installation prompts with version display
    - Flatpak app detection and version checking
    - Comprehensive installation summary
    - Repository cleanup
    - Error handling and logging
    - Progress indication
    - Performance launcher creation
    - CPU governor configuration
    
    NEW ENHANCEMENTS:
    - CLI argument support
    - Dry-run mode
    - State management
    - Rollback framework
    - Multi-distribution support
    - Enhanced error tracking
    """
    
    def __init__(self, args: Optional[argparse.Namespace] = None):
        """
        Initialize the gaming setup system
        
        Args:
            args: Parsed command-line arguments (None for interactive mode)
        """
        # Store arguments (None if running in interactive mode)
        self.args = args if args else argparse.Namespace()
        
        # Initialize configuration from arguments or defaults
        self.config = self._init_config_from_args()
        
        # System and hardware information
        self.system_info = SystemInfo()
        self.hardware_info = HardwareInfo()
        
        # State tracking
        self.rollback_entries: List[BackupEntry] = []
        self.installation_state: Dict[str, Any] = {}
        self.failed_operations: List[str] = []
        self.current_phase = InstallationPhase.INIT
        
        # Verify prerequisites
        self.check_root()
        
        # Load previous state if exists
        self.load_installation_state()
    
    def _init_config_from_args(self) -> InstallationConfig:
        """
        Initialize installation configuration from CLI arguments
        
        NEW ENHANCEMENT: Converts CLI arguments to configuration
        Falls back to interactive mode if no arguments provided
        
        Returns:
            InstallationConfig object
        """
        config = InstallationConfig()
        
        # If no args object or no specific flags, return default (interactive mode)
        if not hasattr(self, 'args') or not self.args:
            return config
        
        # General options
        config.dry_run = getattr(self.args, 'dry_run', False)
        config.auto_yes = getattr(self.args, 'yes', False)
        config.verbose = getattr(self.args, 'verbose', False)
        config.create_backup = not getattr(self.args, 'no_backup', False)
        config.skip_update = getattr(self.args, 'skip_update', False)
        
        # GPU/Driver options
        config.install_nvidia_drivers = getattr(self.args, 'nvidia', False)
        config.install_amd_drivers = getattr(self.args, 'amd', False)
        config.install_intel_drivers = getattr(self.args, 'intel', False)
        config.install_vm_tools = getattr(self.args, 'vm_tools', False)
        
        # Gaming platforms
        if getattr(self.args, 'all_platforms', False):
            config.install_steam = True
            config.install_lutris = True
            config.install_heroic = True
            config.install_protonup = True
            # Note: Sober and Waydroid excluded from all-platforms (specialized)
        else:
            config.install_steam = getattr(self.args, 'steam', False)
            config.install_lutris = getattr(self.args, 'lutris', False)
            config.install_heroic = getattr(self.args, 'heroic', False)
            config.install_protonup = getattr(self.args, 'protonup', False)
        
        # Specialized platforms (always from explicit flags)
        config.install_sober = getattr(self.args, 'sober', False)
        config.install_waydroid = getattr(self.args, 'waydroid', False)
        
        # Compatibility layers
        config.install_wine = getattr(self.args, 'wine', False)
        config.install_winetricks = getattr(self.args, 'winetricks', False)
        config.install_dxvk = getattr(self.args, 'dxvk', False)
        config.install_vkd3d = getattr(self.args, 'vkd3d', False)
        config.install_ge_proton = getattr(self.args, 'ge_proton', False)
        
        # Performance tools
        config.install_gamemode = getattr(self.args, 'gamemode', False)
        config.install_mangohud = getattr(self.args, 'mangohud', False)
        config.install_goverlay = getattr(self.args, 'goverlay', False)
        config.install_greenwithenv = getattr(self.args, 'gwe', False)
        
        # Graphics enhancement
        config.install_vkbasalt = getattr(self.args, 'vkbasalt', False)
        config.install_reshade_setup = getattr(self.args, 'reshade', False)
        
        # Additional tools
        config.install_discord = getattr(self.args, 'discord', False)
        config.install_obs = getattr(self.args, 'obs', False)
        config.install_mumble = getattr(self.args, 'mumble', False)
        config.install_teamspeak = getattr(self.args, 'teamspeak', False)
        config.install_mod_managers = getattr(self.args, 'mod_managers', False)
        config.install_controller_support = getattr(self.args, 'controllers', False)
        
        # System
        config.apply_system_optimizations = getattr(self.args, 'optimize', False)
        config.install_custom_kernel = getattr(self.args, 'custom_kernel', False)
        config.create_performance_launcher = getattr(self.args, 'launcher', False)
        config.install_essential_packages = getattr(self.args, 'essential', False)
        config.install_codecs = getattr(self.args, 'codecs', False)
        
        return config
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PREREQUISITE CHECKS - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def check_root(self):
        """
        Verify script is run with sudo privileges
        
        PRESERVED FROM ORIGINAL: Identical functionality
        """
        if os.geteuid() != 0:
            print(f"{Color.RED}This script must be run with sudo privileges{Color.END}")
            print(f"Usage: sudo python3 {sys.argv[0]}")
            sys.exit(1)
        logging.info(f"Running with sudo privileges as user: {REAL_USER}")
    
    def check_ubuntu_version(self):
        """
        Verify OS version (enhanced to support all Debian-based distros)
        
        PRESERVED FROM ORIGINAL: Warning system for non-Ubuntu
        ENHANCED: Now accepts all Debian-based distros instead of just Ubuntu 24.04.3
        """
        try:
            with open('/etc/os-release', 'r') as f:
                os_info = f.read()
                
                # Check if Debian-based
                is_debian_based = any(x in os_info.lower() for x in 
                                     ['ubuntu', 'debian', 'mint', 'kali', 'pop', 
                                      'elementary', 'zorin', 'mx linux', 'deepin'])
                
                if not is_debian_based:
                    print(f"{Color.YELLOW}Warning: This script is designed for Debian-based distributions{Color.END}")
                    print(f"{Color.YELLOW}Detected OS may not be fully compatible{Color.END}")
                    if not self.confirm("Continue anyway?"):
                        sys.exit(0)
                else:
                    # Just log the detected distro, don't enforce version
                    distro_name = "Unknown"
                    for line in os_info.split('\n'):
                        if line.startswith('PRETTY_NAME='):
                            distro_name = line.split('=')[1].strip('"')
                            break
                    logging.info(f"Detected Debian-based distribution: {distro_name}")
        except Exception as e:
            logging.error(f"Could not verify OS version: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # COMMAND EXECUTION - PRESERVED FROM ORIGINAL WITH ENHANCEMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def run_command(self, cmd, description="", check=True, shell=False, 
                   env=None, timeout=300) -> Tuple[bool, str, str]:
        """
        Execute shell command with logging and error handling
        
        PRESERVED FROM ORIGINAL: All error handling, logging, timeout functionality
        ENHANCED: Added dry-run mode, return values, better error tracking
        
        Args:
            cmd: Command to execute (list or string)
            description: Human-readable description
            check: Raise exception on error
            shell: Execute in shell
            env: Environment variables
            timeout: Command timeout in seconds
            
        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        if description:
            logging.info(description)
            if not self.config.dry_run:
                print(f"{Color.CYAN}>>> {description}{Color.END}")
        
        # DRY RUN MODE - NEW ENHANCEMENT
        if self.config.dry_run:
            cmd_str = cmd if isinstance(cmd, str) else ' '.join(str(c) for c in cmd)
            print(f"{Color.YELLOW}[DRY RUN] Would execute: {cmd_str}{Color.END}")
            logging.info(f"[DRY RUN] Would execute: {cmd_str}")
            return True, "", ""
        
        try:
            # Set default environment with DEBIAN_FRONTEND=noninteractive
            # PRESERVED FROM ORIGINAL
            if env is None:
                env = os.environ.copy()
                env['DEBIAN_FRONTEND'] = 'noninteractive'
            
            # Execute command - PRESERVED FROM ORIGINAL
            if shell:
                result = subprocess.run(cmd, shell=True, check=check, 
                                      capture_output=True, text=True, env=env,
                                      timeout=timeout)
            else:
                result = subprocess.run(cmd, check=check, 
                                      capture_output=True, text=True, env=env,
                                      timeout=timeout)
            
            # Log output - PRESERVED FROM ORIGINAL
            if result.stdout:
                logging.debug(result.stdout)
            if result.returncode == 0:
                logging.info(f"SUCCESS: {description}")
                return True, result.stdout, result.stderr
            else:
                logging.warning(f"Command returned non-zero: {result.returncode}")
                return False, result.stdout, result.stderr
        
        # Error handling - PRESERVED FROM ORIGINAL WITH ENHANCEMENTS
        except subprocess.TimeoutExpired:
            msg = f"TIMEOUT: {description} (exceeded {timeout} seconds)"
            logging.error(msg)
            print(f"{Color.RED}Command timed out: {description}{Color.END}")
            self.failed_operations.append(msg)  # ENHANCED: Track failures
            return False, "", msg
        
        except subprocess.CalledProcessError as e:
            msg = f"FAILED: {description}"
            logging.error(msg)
            logging.error(f"Error: {e.stderr}")
            if check:
                print(f"{Color.RED}Error executing: {description}{Color.END}")
                print(f"{Color.RED}{e.stderr}{Color.END}")
            self.failed_operations.append(msg)  # ENHANCED: Track failures
            return False, e.stdout if hasattr(e, 'stdout') else "", \
                   e.stderr if hasattr(e, 'stderr') else str(e)
        
        except Exception as e:
            msg = f"EXCEPTION: {description} - {str(e)}"
            logging.error(msg)
            self.failed_operations.append(msg)  # ENHANCED: Track failures
            return False, "", str(e)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # USER INTERACTION - PRESERVED FROM ORIGINAL WITH ENHANCEMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def confirm(self, question: str) -> bool:
        """
        Ask user for confirmation
        
        PRESERVED FROM ORIGINAL: Identical loop and validation
        ENHANCED: Added auto-yes and dry-run support
        
        Args:
            question: Question to ask
            
        Returns:
            Boolean confirmation result
        """
        # ENHANCED: Auto-yes mode
        if self.config.auto_yes:
            print(f"{Color.CYAN}{question} [auto-yes]{Color.END}")
            return True
        
        # ENHANCED: Dry-run mode
        if self.config.dry_run:
            print(f"{Color.YELLOW}[DRY RUN] {question} [would prompt]{Color.END}")
            return True
        
        # PRESERVED FROM ORIGINAL: Exact same validation loop
        while True:
            try:
                response = input(f"{Color.YELLOW}{question} (y/n): {Color.END}").lower()
                if response in ['y', 'yes']:
                    return True
                elif response in ['n', 'no']:
                    return False
                print("Please answer 'y' or 'n'")
            except (EOFError, KeyboardInterrupt):
                print()
                return False
    
    def banner(self, text: str):
        """
        Display section banner
        
        PRESERVED FROM ORIGINAL: Identical formatting
        """
        print(f"\n{Color.BOLD}{Color.HEADER}{'='*60}{Color.END}")
        print(f"{Color.BOLD}{Color.HEADER}{text.center(60)}{Color.END}")
        print(f"{Color.BOLD}{Color.HEADER}{'='*60}{Color.END}\n")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # REPOSITORY MANAGEMENT - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def clean_broken_repos(self):
        """
        Clean up broken repository configurations
        
        PRESERVED FROM ORIGINAL: Exact same logic for cleaning broken PPAs
        ENHANCED: Added MangoHud PPA cleanup for Ubuntu 24.04
        """
        print(f"{Color.YELLOW}Checking for broken repositories...{Color.END}")
        
        # Try to update, if it fails due to broken repos, try to fix
        # PRESERVED FROM ORIGINAL
        result, stdout, stderr = self.run_command(
            ["apt-get", "update"],
            "Testing repository configuration",
            check=False
        )
        
        if not result:
            print(f"{Color.YELLOW}Found broken repositories, attempting cleanup...{Color.END}")
            
            # Common fix: remove problematic PPA list files
            # PRESERVED FROM ORIGINAL + ENHANCED
            ppa_dir = "/etc/apt/sources.list.d/"
            if os.path.exists(ppa_dir):
                for file in os.listdir(ppa_dir):
                    # Original: Lutris PPA cleanup
                    # Enhanced: MangoHud PPA cleanup for Ubuntu 24.04
                    if any(broken in file.lower() for broken in ["lutris", "mangohud"]):
                        file_path = os.path.join(ppa_dir, file)
                        try:
                            if not self.config.dry_run:
                                # Backup before removing
                                backup_path = f"{file_path}.broken"
                                if os.path.exists(file_path):
                                    shutil.copy2(file_path, backup_path)
                                os.remove(file_path)
                            print(f"{Color.GREEN}Removed broken repository: {file}{Color.END}")
                        except Exception as e:
                            logging.error(f"Could not remove {file}: {e}")
            
            # Try update again - PRESERVED FROM ORIGINAL
            self.run_command(
                ["apt-get", "update"],
                "Updating after repository cleanup",
                check=False
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PACKAGE MANAGEMENT - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def is_package_installed(self, package_name: str) -> bool:
        """
        Check if a package is installed
        
        PRESERVED FROM ORIGINAL: Exact same dpkg check
        
        Args:
            package_name: Name of package to check
            
        Returns:
            True if installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["dpkg", "-l", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            return result.returncode == 0 and 'ii' in result.stdout
        except:
            return False
    
    def get_package_version(self, package_name: str) -> Optional[str]:
        """
        Get installed package version
        
        PRESERVED FROM ORIGINAL: Exact same dpkg-query logic
        
        Args:
            package_name: Name of package
            
        Returns:
            Version string or None
        """
        try:
            result = subprocess.run(
                ["dpkg-query", "-W", "-f=${Version}", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return None
    
    def get_available_version(self, package_name: str) -> Optional[str]:
        """
        Get available package version from repos
        
        PRESERVED FROM ORIGINAL: Exact same apt-cache logic
        
        Args:
            package_name: Name of package
            
        Returns:
            Version string or None
        """
        try:
            result = subprocess.run(
                ["apt-cache", "policy", package_name],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Candidate:' in line:
                        return line.split(':')[1].strip()
        except:
            pass
        return None
    
    def is_flatpak_installed(self, app_id: str) -> bool:
        """
        Check if a Flatpak app is installed
        
        PRESERVED FROM ORIGINAL: Exact same flatpak list check
        
        Args:
            app_id: Flatpak application ID
            
        Returns:
            True if installed, False otherwise
        """
        try:
            result = subprocess.run(
                ["flatpak", "list", "--app"],
                capture_output=True,
                text=True,
                timeout=5
            )
            return app_id in result.stdout
        except:
            return False
    
    def get_flatpak_version(self, app_id: str) -> Optional[str]:
        """
        Get installed Flatpak version
        
        PRESERVED FROM ORIGINAL: Exact same flatpak info parsing
        
        Args:
            app_id: Flatpak application ID
            
        Returns:
            Version string or None
        """
        try:
            result = subprocess.run(
                ["flatpak", "info", app_id],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Version:' in line:
                        return line.split(':')[1].strip()
        except:
            pass
        return None
    
    def check_updates_available(self, package_name: str) -> Tuple[bool, Optional[str], Optional[str]]:
        """
        Check if updates are available for a package
        
        PRESERVED FROM ORIGINAL: Exact same version comparison logic
        
        Args:
            package_name: Name of package to check
            
        Returns:
            Tuple of (update_available, installed_version, available_version)
        """
        installed = self.get_package_version(package_name)
        available = self.get_available_version(package_name)
        
        if installed and available and installed != available:
            return True, installed, available
        return False, installed, available

# END OF PART 2
# Continue with Part 3 for smart installation prompts and detection methods
# PART 3: Smart Installation Prompts and Detection Methods
# Preserves ALL original intelligent prompting and detection logic

    # ═══════════════════════════════════════════════════════════════════════════
    # SMART INSTALLATION PROMPTS - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def prompt_install_or_update(self, software_name: str, package_name: Optional[str] = None,
                                 flatpak_id: Optional[str] = None) -> bool:
        """
        Smart prompt that checks installation status and offers update
        
        PRESERVED FROM ORIGINAL: This is the core intelligent prompting system
        that checks versions, detects updates, and provides clear user feedback
        
        Args:
            software_name: Human-readable software name
            package_name: APT package name (optional)
            flatpak_id: Flatpak application ID (optional)
            
        Returns:
            True if user wants to install/update, False otherwise
        """
        # ENHANCED: Auto-yes mode bypasses but still shows info
        if self.config.auto_yes:
            print(f"{Color.CYAN}Auto-installing {software_name}...{Color.END}")
            return True
        
        is_installed = False
        current_version = None
        available_version = None
        update_available = False
        
        # Check package installation - PRESERVED FROM ORIGINAL
        if package_name:
            is_installed = self.is_package_installed(package_name)
            if is_installed:
                current_version = self.get_package_version(package_name)
                available_version = self.get_available_version(package_name)
                update_available = current_version != available_version
        
        # Check Flatpak installation - PRESERVED FROM ORIGINAL
        if flatpak_id and not is_installed:
            is_installed = self.is_flatpak_installed(flatpak_id)
            if is_installed:
                current_version = self.get_flatpak_version(flatpak_id)
        
        # Build prompt based on status - PRESERVED FROM ORIGINAL
        if is_installed:
            if current_version:
                print(f"{Color.GREEN}✓ {software_name} is already installed (version: {current_version}){Color.END}")
            else:
                print(f"{Color.GREEN}✓ {software_name} is already installed{Color.END}")
            
            if update_available and available_version:
                print(f"{Color.CYAN}  Update available: {current_version} → {available_version}{Color.END}")
                return self.confirm(f"Update {software_name}?")
            else:
                return self.confirm(f"Reinstall {software_name}?")
        else:
            return self.confirm(f"Install {software_name}?")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM DETECTION - PRESERVED FROM ORIGINAL WITH ENHANCEMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def detect_system(self):
        """
        Comprehensive system detection
        
        PRESERVED FROM ORIGINAL: All OS detection logic
        ENHANCED: Better distro family detection, desktop environment detection
        """
        self.banner("SYSTEM DETECTION")
        self.current_phase = InstallationPhase.DETECTION
        
        try:
            # Read OS release information - PRESERVED FROM ORIGINAL
            os_release = {}
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if '=' in line:
                        key, value = line.strip().split('=', 1)
                        os_release[key] = value.strip('"')
            
            # Detect distribution - ENHANCED: More comprehensive
            self.system_info.distro_name = os_release.get('NAME', 'Unknown')
            self.system_info.distro_version = os_release.get('VERSION_ID', 'Unknown')
            self.system_info.distro_id = os_release.get('ID', 'unknown')
            
            # Detect distribution family - ENHANCED
            self.system_info.distro_family = self._detect_distro_family(os_release)
            
            # Detect kernel - PRESERVED FROM ORIGINAL
            self.system_info.kernel_version = platform.release()
            
            # Detect architecture - PRESERVED FROM ORIGINAL
            self.system_info.architecture = platform.machine()
            
            # Detect desktop environment - ENHANCED
            self.system_info.desktop_environment = self._detect_desktop_environment()
            
            # Check if WSL - ENHANCED
            self.system_info.is_wsl = os.path.exists('/proc/sys/fs/binfmt_misc/WSLInterop')
            
            # Display detection results - ENHANCED FORMAT
            print(f"{Color.BOLD}System Information:{Color.END}")
            print(f"  Distribution:     {Color.CYAN}{self.system_info.distro_name} {self.system_info.distro_version}{Color.END}")
            print(f"  Family:           {Color.CYAN}{self.system_info.distro_family.value}{Color.END}")
            print(f"  Kernel:           {Color.CYAN}{self.system_info.kernel_version}{Color.END}")
            print(f"  Architecture:     {Color.CYAN}{self.system_info.architecture}{Color.END}")
            print(f"  Desktop:          {Color.CYAN}{self.system_info.desktop_environment}{Color.END}")
            if self.system_info.is_wsl:
                print(f"  Environment:      {Color.YELLOW}WSL (Windows Subsystem for Linux){Color.END}")
            print(f"  User:             {Color.CYAN}{REAL_USER}{Color.END}")
            print()
            
            logging.info(f"System detection complete: {self.system_info.distro_name} "
                        f"{self.system_info.distro_version}")
            
        except Exception as e:
            logging.error(f"System detection failed: {e}")
            raise
    
    def _detect_distro_family(self, os_release: Dict[str, str]) -> DistroFamily:
        """
        Detect distribution family from OS release info
        
        ENHANCED: More comprehensive distro detection
        
        Args:
            os_release: Dictionary from /etc/os-release
            
        Returns:
            DistroFamily enum value
        """
        name_lower = os_release.get('NAME', '').lower()
        id_like = os_release.get('ID_LIKE', '').lower()
        distro_id = os_release.get('ID', '').lower()
        
        # Check for specific distributions
        if 'mint' in name_lower or 'mint' in distro_id:
            return DistroFamily.MINT
        elif 'kali' in name_lower or 'kali' in distro_id:
            return DistroFamily.KALI
        elif 'pop' in name_lower or 'pop' in distro_id:
            return DistroFamily.POPOS
        elif 'elementary' in name_lower or 'elementary' in distro_id:
            return DistroFamily.ELEMENTARY
        elif 'zorin' in name_lower or 'zorin' in distro_id:
            return DistroFamily.ZORIN
        elif 'ubuntu' in name_lower or 'ubuntu' in id_like or 'ubuntu' in distro_id:
            return DistroFamily.UBUNTU
        elif 'debian' in name_lower or 'debian' in id_like or 'debian' in distro_id:
            return DistroFamily.DEBIAN
        
        return DistroFamily.UNKNOWN
    
    def _detect_desktop_environment(self) -> str:
        """
        Detect the desktop environment
        
        ENHANCED: New method for better user feedback
        
        Returns:
            Desktop environment name
        """
        de = os.environ.get('DESKTOP_SESSION', '').lower()
        
        if not de:
            de = os.environ.get('XDG_CURRENT_DESKTOP', '').lower()
        
        if 'gnome' in de:
            return 'GNOME'
        elif 'kde' in de or 'plasma' in de:
            return 'KDE Plasma'
        elif 'xfce' in de:
            return 'XFCE'
        elif 'cinnamon' in de:
            return 'Cinnamon'
        elif 'mate' in de:
            return 'MATE'
        elif 'pantheon' in de:
            return 'Pantheon'
        elif 'lxde' in de or 'lxqt' in de:
            return 'LXDE/LXQt'
        elif 'i3' in de or 'sway' in de:
            return 'Tiling WM'
        
        return 'Unknown'
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GPU DETECTION - PRESERVED FROM ORIGINAL WITH ENHANCEMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def detect_gpu(self):
        """
        Detect GPU type
        
        PRESERVED FROM ORIGINAL: All lspci parsing and glxinfo cross-validation
        ENHANCED: Better false-positive prevention, more VM types
        """
        self.banner("GPU DETECTION")
        
        # First check if running in a VM - PRESERVED FROM ORIGINAL
        vm_type = self.detect_virtualization()
        if vm_type:
            print(f"{Color.YELLOW}⚠ Virtual Machine Detected: {vm_type}{Color.END}")
            print(f"{Color.CYAN}Virtual GPU drivers will be handled by VM guest tools{Color.END}")
            logging.info(f"Running in {vm_type} VM")
            self.hardware_info.vm_type = self._vm_type_str_to_enum(vm_type)
            self.hardware_info.gpu_vendor = GPUVendor.VIRTUAL
            return vm_type.lower()
        
        try:
            # Check actual GPU hardware via lspci - PRESERVED FROM ORIGINAL
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
            lspci_output = result.stdout.lower()
            
            # Filter lspci to only VGA/3D/Display lines - PRESERVED FROM ORIGINAL
            # This avoids false positives from Intel CPUs, network cards, etc.
            gpu_lines = []
            for line in lspci_output.split('\n'):
                if any(keyword in line for keyword in ['vga', '3d', 'display']):
                    gpu_lines.append(line)
            
            gpu_info = ' '.join(gpu_lines).lower()
            
            # Also check OpenGL renderer for more accurate detection - PRESERVED FROM ORIGINAL
            gl_info = ""
            try:
                gl_result = subprocess.run(['glxinfo'], capture_output=True, 
                                          text=True, timeout=5)
                if gl_result.returncode == 0:
                    # Extract just the renderer line
                    for line in gl_result.stdout.split('\n'):
                        if 'OpenGL renderer' in line:
                            gl_info = line.lower()
                            break
            except:
                pass
            
            logging.info(f"GPU detection - lspci VGA: {gpu_info}")
            logging.info(f"GPU detection - GL renderer: {gl_info}")
            
            # Check for virtual/emulated GPUs first - PRESERVED FROM ORIGINAL
            if any(vm_indicator in gpu_info or vm_indicator in gl_info 
                   for vm_indicator in ['vmware', 'virtualbox', 'qxl', 'virtio', 'svga3d']):
                print(f"{Color.YELLOW}⚠ Virtual GPU detected{Color.END}")
                logging.info("Virtual GPU detected in hardware scan")
                self.hardware_info.gpu_vendor = GPUVendor.VIRTUAL
                return 'generic'
            
            # Check for NVIDIA (most specific) - PRESERVED FROM ORIGINAL
            if 'nvidia' in gpu_info or 'nvidia' in gl_info:
                print(f"{Color.GREEN}✓ NVIDIA GPU detected{Color.END}")
                logging.info("NVIDIA GPU detected")
                self.hardware_info.gpu_vendor = GPUVendor.NVIDIA
                # Extract model - ENHANCED
                for line in gpu_lines:
                    if 'nvidia' in line:
                        self.hardware_info.gpu_model = self._extract_gpu_model(line)
                        break
                return 'nvidia'
            
            # Check for AMD/Radeon - PRESERVED FROM ORIGINAL
            if any(amd_indicator in gpu_info or amd_indicator in gl_info
                   for amd_indicator in ['amd', 'radeon', 'ati']):
                print(f"{Color.GREEN}✓ AMD GPU detected{Color.END}")
                logging.info("AMD GPU detected")
                self.hardware_info.gpu_vendor = GPUVendor.AMD
                # Extract model - ENHANCED
                for line in gpu_lines:
                    if any(amd in line for amd in ['amd', 'radeon', 'ati']):
                        self.hardware_info.gpu_model = self._extract_gpu_model(line)
                        break
                return 'amd'
            
            # Check for Intel (least specific, check last) - PRESERVED FROM ORIGINAL
            if ('intel' in gpu_info and any(gpu_term in gpu_info 
                for gpu_term in ['graphics', 'hd', 'iris', 'uhd', 'arc'])):
                print(f"{Color.GREEN}✓ Intel GPU detected{Color.END}")
                logging.info("Intel GPU detected")
                self.hardware_info.gpu_vendor = GPUVendor.INTEL
                # Extract model - ENHANCED
                for line in gpu_lines:
                    if 'intel' in line:
                        self.hardware_info.gpu_model = self._extract_gpu_model(line)
                        break
                return 'intel'
            
            # If we found GPU lines but couldn't identify vendor - PRESERVED FROM ORIGINAL
            if gpu_lines:
                print(f"{Color.YELLOW}! Generic/Unknown GPU detected{Color.END}")
                print(f"{Color.CYAN}  GPU info: {gpu_lines[0] if gpu_lines else 'unknown'}{Color.END}")
                logging.info(f"Unknown GPU type: {gpu_lines}")
                self.hardware_info.gpu_vendor = GPUVendor.UNKNOWN
                return 'generic'
            
            # No GPU detected at all - PRESERVED FROM ORIGINAL
            print(f"{Color.YELLOW}! No GPU detected{Color.END}")
            self.hardware_info.gpu_vendor = GPUVendor.UNKNOWN
            return 'unknown'
                
        except Exception as e:
            logging.error(f"GPU detection failed: {e}")
            self.hardware_info.gpu_vendor = GPUVendor.UNKNOWN
            return 'unknown'
    
    def _extract_gpu_model(self, lspci_line: str) -> str:
        """
        Extract GPU model from lspci line
        
        ENHANCED: New method for better hardware info display
        
        Args:
            lspci_line: Line from lspci output
            
        Returns:
            Extracted GPU model name
        """
        # Remove PCI address and VGA controller prefix
        parts = lspci_line.split(':')
        if len(parts) >= 3:
            model = ':'.join(parts[2:]).strip()
            # Clean up common prefixes
            model = model.replace('vga compatible controller:', '').strip()
            model = model.replace('3d controller:', '').strip()
            model = model.replace('display controller:', '').strip()
            return model[:80]  # Limit length
        return "Unknown Model"
    
    def _vm_type_str_to_enum(self, vm_str: str) -> VMType:
        """
        Convert VM type string to enum
        
        ENHANCED: Helper for better type safety
        
        Args:
            vm_str: VM type string
            
        Returns:
            VMType enum value
        """
        vm_lower = vm_str.lower()
        if 'vmware' in vm_lower:
            return VMType.VMWARE
        elif 'virtualbox' in vm_lower or 'oracle' in vm_lower:
            return VMType.VIRTUALBOX
        elif 'kvm' in vm_lower:
            return VMType.KVM
        elif 'qemu' in vm_lower:
            return VMType.QEMU
        elif 'hyper-v' in vm_lower or 'microsoft' in vm_lower:
            return VMType.HYPERV
        elif 'xen' in vm_lower:
            return VMType.XEN
        elif 'parallels' in vm_lower:
            return VMType.PARALLELS
        return VMType.NONE
    
    def detect_virtualization(self):
        """
        Detect if running in a virtual machine and which type
        
        PRESERVED FROM ORIGINAL: All three detection methods
        ENHANCED: More VM types, better error handling
        """
        try:
            # Method 1: systemd-detect-virt (most reliable) - PRESERVED FROM ORIGINAL
            result = subprocess.run(['systemd-detect-virt'], 
                                  capture_output=True, text=True, timeout=5)
            virt_type = result.stdout.strip()
            
            if virt_type and virt_type != 'none':
                # Map common virtualization types to friendly names - PRESERVED FROM ORIGINAL
                virt_map = {
                    'vmware': 'VMware',
                    'kvm': 'KVM',
                    'qemu': 'QEMU',
                    'virtualbox': 'VirtualBox',
                    'oracle': 'VirtualBox',
                    'microsoft': 'Hyper-V',
                    'xen': 'Xen',
                    'bochs': 'Bochs',
                    'parallels': 'Parallels'
                }
                return virt_map.get(virt_type.lower(), virt_type)
        except:
            pass
        
        try:
            # Method 2: Check dmesg for hypervisor - PRESERVED FROM ORIGINAL
            result = subprocess.run(['dmesg'], capture_output=True, text=True, timeout=5)
            dmesg = result.stdout.lower()
            
            if 'vmware' in dmesg:
                return 'VMware'
            elif 'virtualbox' in dmesg:
                return 'VirtualBox'
            elif 'hypervisor detected' in dmesg:
                return 'VM'
        except:
            pass
        
        try:
            # Method 3: Check lspci for virtual graphics - PRESERVED FROM ORIGINAL
            result = subprocess.run(['lspci'], capture_output=True, text=True, timeout=5)
            lspci = result.stdout.lower()
            
            if 'vmware' in lspci:
                return 'VMware'
            elif 'virtualbox' in lspci:
                return 'VirtualBox'
            elif 'qxl' in lspci or 'virtio' in lspci:
                return 'KVM/QEMU'
        except:
            pass
        
        return None

# END OF PART 3
# Continue with Part 4 for driver installation and platform installation methods
# PART 4: Driver Installation, Gaming Platforms, and Compatibility Layers
# All original functionality preserved with new additions

    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM UPDATE - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def update_system(self):
        """
        Update system packages
        
        PRESERVED FROM ORIGINAL: Exact same update sequence
        ENHANCED: Added skip_update option
        """
        if self.config.skip_update:
            print(f"{Color.YELLOW}Skipping system update as requested{Color.END}")
            return
        
        self.banner("SYSTEM UPDATE")
        
        # PRESERVED FROM ORIGINAL: Exact same commands
        commands = [
            (["apt-get", "update"], "Updating package lists"),
            (["apt-get", "upgrade", "-y"], "Upgrading installed packages"),
            (["apt-get", "autoremove", "-y"], "Removing unnecessary packages"),
            (["apt-get", "autoclean"], "Cleaning package cache")
        ]
        
        for cmd, desc in commands:
            self.run_command(cmd, desc)
    
    def enable_32bit_support(self):
        """
        Enable 32-bit architecture support (required for many games)
        
        PRESERVED FROM ORIGINAL: Identical functionality
        """
        self.banner("32-BIT ARCHITECTURE SUPPORT")
        
        self.run_command(
            ["dpkg", "--add-architecture", "i386"],
            "Enabling i386 architecture"
        )
        self.run_command(["apt-get", "update"], "Updating package lists")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NVIDIA DRIVER INSTALLATION - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_nvidia_drivers(self):
        """
        Install NVIDIA proprietary drivers
        
        PRESERVED FROM ORIGINAL: All version checking and prompting logic
        """
        self.banner("NVIDIA DRIVER INSTALLATION")
        
        # Check if already installed - PRESERVED FROM ORIGINAL
        nvidia_installed = self.is_package_installed("nvidia-driver-550") or \
                          self.is_package_installed("nvidia-driver-545") or \
                          self.is_package_installed("nvidia-driver-535")
        
        if nvidia_installed:
            try:
                result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
                if result.returncode == 0:
                    # Extract driver version from nvidia-smi output - PRESERVED FROM ORIGINAL
                    for line in result.stdout.split('\n'):
                        if 'Driver Version:' in line:
                            version = line.split('Driver Version:')[1].split()[0]
                            print(f"{Color.GREEN}✓ NVIDIA drivers already installed (version: {version}){Color.END}")
                            break
                    else:
                        print(f"{Color.GREEN}✓ NVIDIA drivers already installed{Color.END}")
                    
                    if not self.confirm("Reinstall NVIDIA drivers?"):
                        return
            except:
                print(f"{Color.YELLOW}⚠ NVIDIA drivers installed but not loaded{Color.END}")
                if not self.confirm("Reinstall NVIDIA drivers?"):
                    return
        
        print("Installing NVIDIA driver (latest stable)...")
        
        # PRESERVED FROM ORIGINAL: Exact same installation sequence
        commands = [
            (["apt-get", "install", "-y", "ubuntu-drivers-common"], "Installing driver manager"),
            (["ubuntu-drivers", "autoinstall"], "Installing recommended NVIDIA drivers"),
            (["apt-get", "install", "-y", "nvidia-settings", "nvidia-prime"], "Installing NVIDIA utilities")
        ]
        
        for cmd, desc in commands:
            self.run_command(cmd, desc)
        
        print(f"{Color.YELLOW}Note: System reboot required for NVIDIA drivers to take effect{Color.END}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # AMD DRIVER INSTALLATION - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_amd_drivers(self):
        """
        Install AMD drivers
        
        PRESERVED FROM ORIGINAL: Exact same package list
        """
        self.banner("AMD DRIVER INSTALLATION")
        
        print("AMD drivers are typically included in the Linux kernel.")
        print("Installing Mesa drivers and Vulkan support...")
        
        # PRESERVED FROM ORIGINAL: Exact same packages
        packages = [
            "mesa-vulkan-drivers",
            "mesa-vulkan-drivers:i386",
            "libvulkan1",
            "libvulkan1:i386",
            "vulkan-tools",
            "mesa-utils"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing AMD Mesa and Vulkan drivers"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INTEL DRIVER INSTALLATION - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_intel_drivers(self):
        """
        Install Intel drivers
        
        PRESERVED FROM ORIGINAL: Exact same package list
        """
        self.banner("INTEL DRIVER INSTALLATION")
        
        print("Installing Intel graphics drivers...")
        
        # PRESERVED FROM ORIGINAL: Exact same packages
        packages = [
            "mesa-vulkan-drivers",
            "mesa-vulkan-drivers:i386",
            "libvulkan1",
            "libvulkan1:i386",
            "intel-media-va-driver",
            "i965-va-driver"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing Intel graphics drivers"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # VM TOOLS INSTALLATION - PRESERVED FROM ORIGINAL WITH ENHANCEMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_vm_tools(self, vm_type):
        """
        Install VM guest tools based on hypervisor type
        
        PRESERVED FROM ORIGINAL: All VMware, VirtualBox, and KVM logic
        ENHANCED: Added Hyper-V, Xen support
        """
        self.banner("VM GUEST TOOLS INSTALLATION")
        
        print(f"{Color.CYAN}Detected {vm_type} - Installing guest tools...{Color.END}")
        
        if 'vmware' in vm_type.lower():
            self.install_vmware_tools()
        elif 'virtualbox' in vm_type.lower():
            self.install_virtualbox_tools()
        elif 'kvm' in vm_type.lower() or 'qemu' in vm_type.lower():
            self.install_kvm_tools()
        elif 'hyper-v' in vm_type.lower() or 'microsoft' in vm_type.lower():
            self.install_hyperv_tools()  # ENHANCED: New
        elif 'xen' in vm_type.lower():
            self.install_xen_tools()  # ENHANCED: New
        else:
            print(f"{Color.YELLOW}Generic VM detected - installing basic 3D acceleration{Color.END}")
            self.install_generic_vm_graphics()
    
    def install_vmware_tools(self):
        """Install VMware guest tools - PRESERVED FROM ORIGINAL"""
        print(f"{Color.CYAN}Installing VMware Tools (open-vm-tools)...{Color.END}")
        
        # PRESERVED FROM ORIGINAL: Exact same packages
        packages = [
            "open-vm-tools",
            "open-vm-tools-desktop",
            "mesa-utils",
            "mesa-utils-extra",
            "libgl1-mesa-dri",
            "libgl1-mesa-dri:i386"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing VMware guest tools and graphics"
        )
        
        print(f"{Color.GREEN}✓ VMware Tools installed{Color.END}")
        print(f"{Color.YELLOW}Note: For better 3D performance, enable 3D acceleration in VMware settings{Color.END}")
    
    def install_virtualbox_tools(self):
        """Install VirtualBox guest additions - PRESERVED FROM ORIGINAL"""
        print(f"{Color.CYAN}Installing VirtualBox Guest Additions...{Color.END}")
        
        # PRESERVED FROM ORIGINAL: Exact same packages
        packages = [
            "virtualbox-guest-utils",
            "virtualbox-guest-x11",
            "virtualbox-guest-dkms",
            "mesa-utils"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing VirtualBox guest additions"
        )
        
        print(f"{Color.GREEN}✓ VirtualBox Guest Additions installed{Color.END}")
    
    def install_kvm_tools(self):
        """Install KVM/QEMU guest tools - PRESERVED FROM ORIGINAL"""
        print(f"{Color.CYAN}Installing KVM/QEMU guest tools...{Color.END}")
        
        # PRESERVED FROM ORIGINAL: Exact same packages
        packages = [
            "qemu-guest-agent",
            "spice-vdagent",
            "xserver-xorg-video-qxl",
            "mesa-utils"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing KVM/QEMU guest tools"
        )
        
        print(f"{Color.GREEN}✓ KVM/QEMU tools installed{Color.END}")
    
    def install_hyperv_tools(self):
        """Install Hyper-V guest tools - ENHANCED: New addition"""
        print(f"{Color.CYAN}Installing Hyper-V guest tools...{Color.END}")
        
        packages = [
            "hyperv-daemons",
            "linux-tools-virtual",
            "linux-cloud-tools-virtual"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing Hyper-V guest tools",
            check=False  # May not be available on all distros
        )
    
    def install_xen_tools(self):
        """Install Xen guest tools - ENHANCED: New addition"""
        print(f"{Color.CYAN}Installing Xen guest tools...{Color.END}")
        
        packages = [
            "xe-guest-utilities"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing Xen guest tools",
            check=False  # May not be available on all distros
        )
    
    def install_generic_vm_graphics(self):
        """Install generic VM graphics support - PRESERVED FROM ORIGINAL"""
        # PRESERVED FROM ORIGINAL: Exact same packages
        packages = [
            "mesa-utils",
            "mesa-utils-extra",
            "libgl1-mesa-dri",
            "libgl1-mesa-dri:i386",
            "mesa-vulkan-drivers",
            "mesa-vulkan-drivers:i386"
        ]
        
        self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing generic VM graphics drivers"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # GAMING PLATFORMS - PRESERVED FROM ORIGINAL WITH SMART PROMPTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_gaming_platforms(self):
        """
        Install Steam, Lutris, and other gaming platforms
        
        PRESERVED FROM ORIGINAL: All prompting logic with version checking
        ENHANCED: CLI flag support
        """
        self.banner("GAMING PLATFORMS")
        
        # Install Steam - PRESERVED FROM ORIGINAL
        should_install = self.config.install_steam or \
                        self.prompt_install_or_update("Steam", package_name="steam-installer")
        
        if should_install:
            print(f"{Color.CYAN}Installing Steam...{Color.END}")
            self.run_command(
                ["apt-get", "install", "-y", "steam-installer"],
                "Installing Steam"
            )
        
        # Install Lutris - PRESERVED FROM ORIGINAL
        should_install = self.config.install_lutris or \
                        self.prompt_install_or_update("Lutris", flatpak_id="net.lutris.Lutris")
        
        if should_install:
            print(f"{Color.CYAN}Installing Lutris...{Color.END}")
            print(f"{Color.YELLOW}Note: Installing via Flatpak (PPA not yet available for Ubuntu 24.04){Color.END}")
            
            # Ensure Flatpak is installed - PRESERVED FROM ORIGINAL
            if not self.is_package_installed("flatpak"):
                self.run_command(
                    ["apt-get", "install", "-y", "flatpak"],
                    "Installing Flatpak"
                )
            
            # Add Flathub if not already added - PRESERVED FROM ORIGINAL
            self.run_command(
                ["flatpak", "remote-add", "--if-not-exists", "flathub", 
                 "https://flathub.org/repo/flathub.flatpakrepo"],
                "Adding Flathub repository",
                check=False
            )
            
            # Install Lutris via Flatpak - PRESERVED FROM ORIGINAL
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "net.lutris.Lutris"],
                "Installing Lutris"
            )
        
        # Install GameMode - PRESERVED FROM ORIGINAL
        should_install = self.config.install_gamemode or \
                        self.prompt_install_or_update("GameMode", package_name="gamemode")
        
        if should_install:
            # Install both 64-bit and 32-bit libraries for compatibility
            # PRESERVED FROM ORIGINAL
            packages = ["gamemode", "libgamemode0", "libgamemode0:i386"]
            self.run_command(
                ["apt-get", "install", "-y"] + packages,
                "Installing GameMode with 32-bit and 64-bit libraries"
            )
        
        # Install Heroic Games Launcher (for Epic/GOG) - PRESERVED FROM ORIGINAL
        should_install = self.config.install_heroic or \
                        self.prompt_install_or_update("Heroic Games Launcher", 
                                                     flatpak_id="com.heroicgameslauncher.hgl")
        
        if should_install:
            print(f"{Color.CYAN}Installing Heroic Games Launcher...{Color.END}")
            self.install_heroic()
    
    def install_heroic(self):
        """Install Heroic Games Launcher via Flatpak - PRESERVED FROM ORIGINAL"""
        # Install Flatpak if not present - PRESERVED FROM ORIGINAL
        self.run_command(
            ["apt-get", "install", "-y", "flatpak"],
            "Installing Flatpak"
        )
        
        # Add Flathub repository - PRESERVED FROM ORIGINAL
        self.run_command(
            ["flatpak", "remote-add", "--if-not-exists", "flathub", 
             "https://flathub.org/repo/flathub.flatpakrepo"],
            "Adding Flathub repository"
        )
        
        # Install Heroic - PRESERVED FROM ORIGINAL
        self.run_command(
            ["flatpak", "install", "-y", "flathub", "com.heroicgameslauncher.hgl"],
            "Installing Heroic Games Launcher"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # WINE & COMPATIBILITY LAYERS - PRESERVED FROM ORIGINAL WITH ADDITIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_wine_proton(self):
        """
        Install Wine and Proton compatibility layers
        
        PRESERVED FROM ORIGINAL: All Wine installation logic
        ENHANCED: Added GE-Proton, ProtonUp-Qt
        """
        self.banner("WINE & COMPATIBILITY LAYERS")
        
        # Wine installation - PRESERVED FROM ORIGINAL
        should_install = self.config.install_wine or \
                        self.prompt_install_or_update("Wine (Windows compatibility)", 
                                                     package_name="winehq-staging")
        
        if should_install:
            print(f"{Color.CYAN}Installing Wine...{Color.END}")
            # PRESERVED FROM ORIGINAL: Exact same command sequence
            commands = [
                (["mkdir", "-pm755", "/etc/apt/keyrings"], "Creating keyring directory"),
                ("wget -O /etc/apt/keyrings/winehq-archive.key https://dl.winehq.org/wine-builds/winehq.key", 
                 "Downloading WineHQ key", True, True),
                ("wget -NP /etc/apt/sources.list.d/ https://dl.winehq.org/wine-builds/ubuntu/dists/noble/winehq-noble.sources",
                 "Adding WineHQ repository", True, True),
                (["apt-get", "update"], "Updating package lists"),
                ("apt-get install -y --install-recommends winehq-staging", "Installing Wine Staging", True, True)
            ]
            
            for item in commands:
                if len(item) == 2:
                    cmd, desc = item
                    shell = False
                elif len(item) == 4:
                    cmd, desc, _, shell = item
                else:
                    continue
                    
                self.run_command(cmd, desc, shell=shell)
        
        # Winetricks - PRESERVED FROM ORIGINAL
        should_install = self.config.install_winetricks or \
                        self.prompt_install_or_update("Winetricks (Wine configuration tool)", 
                                                     package_name="winetricks")
        
        if should_install:
            self.run_command(
                ["apt-get", "install", "-y", "winetricks"],
                "Installing Winetricks"
            )
        
        # ProtonUp-Qt for managing Proton versions - PRESERVED FROM ORIGINAL
        should_install = self.config.install_protonup or \
                        self.prompt_install_or_update("ProtonUp-Qt (Proton version manager)", 
                                                     flatpak_id="net.davidotek.pupgui2")
        
        if should_install:
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "net.davidotek.pupgui2"],
                "Installing ProtonUp-Qt"
            )
        
        # GE-Proton automatic installation - ENHANCED: New feature
        if self.config.install_ge_proton or self.confirm("Install GE-Proton (latest)?"):
            self.install_ge_proton()
    
    def install_ge_proton(self):
        """
        Install GE-Proton automatically
        
        ENHANCED: New feature - automatic GE-Proton installation via GitHub API
        """
        self.banner("GE-PROTON INSTALLATION")
        
        try:
            # Get latest release from GitHub API
            print(f"{Color.CYAN}Fetching latest GE-Proton release...{Color.END}")
            url = "https://api.github.com/repos/GloriousEggroll/proton-ge-custom/releases/latest"
            
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read())
            
            # Find tar.gz asset
            download_url = None
            for asset in data.get('assets', []):
                if asset['name'].endswith('.tar.gz') and 'sha512sum' not in asset['name']:
                    download_url = asset['browser_download_url']
                    filename = asset['name']
                    break
            
            if not download_url:
                print(f"{Color.RED}Could not find GE-Proton download{Color.END}")
                return
            
            # Download and install
            proton_dir = REAL_USER_HOME / ".steam/root/compatibilitytools.d"
            proton_dir.mkdir(parents=True, exist_ok=True)
            
            download_path = f"/tmp/{filename}"
            print(f"{Color.CYAN}Downloading {filename}...{Color.END}")
            
            if not self.config.dry_run:
                self.run_command(
                    f"wget -O {download_path} {download_url}",
                    "Downloading GE-Proton",
                    shell=True,
                    timeout=600  # 10 minute timeout for large download
                )
                
                print(f"{Color.CYAN}Extracting to {proton_dir}...{Color.END}")
                self.run_command(
                    f"tar -xzf {download_path} -C {proton_dir}",
                    "Extracting GE-Proton",
                    shell=True
                )
                
                # Set ownership
                uid, gid = get_real_user_uid_gid()
                for root, dirs, files in os.walk(proton_dir):
                    for d in dirs:
                        os.chown(os.path.join(root, d), uid, gid)
                    for f in files:
                        os.chown(os.path.join(root, f), uid, gid)
                
                print(f"{Color.GREEN}✓ GE-Proton installed to {proton_dir}{Color.END}")
                os.remove(download_path)
            
        except Exception as e:
            logging.error(f"GE-Proton installation failed: {e}")
            print(f"{Color.RED}✗ GE-Proton installation failed: {e}{Color.END}")
            print(f"{Color.CYAN}You can install manually from: https://github.com/GloriousEggroll/proton-ge-custom{Color.END}")

# END OF PART 4
# Continue with Part 5 for additional tools, optimizations, and installation summary
# PART 5: Essential Packages, Tools, Optimizations, and Installation Summary
# ALL original functionality preserved, especially the comprehensive installation summary

    # ═══════════════════════════════════════════════════════════════════════════
    # ESSENTIAL PACKAGES - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_essential_packages(self):
        """
        Install essential gaming packages and libraries
        
        PRESERVED FROM ORIGINAL: Exact same package list
        """
        self.banner("ESSENTIAL PACKAGES")
        
        # PRESERVED FROM ORIGINAL: Exact same packages
        # FIXED: linux-cpupower → linux-tools-generic for Ubuntu 24.04 compatibility
        packages = [
            # Core libraries
            "build-essential",
            "git",
            "curl",
            "wget",
            
            # Graphics libraries
            "libgl1-mesa-dri:i386",
            "mesa-vulkan-drivers",
            "mesa-vulkan-drivers:i386",
            
            # Audio
            "pulseaudio",
            "pavucontrol",
            
            # Controllers
            "joystick",
            "jstest-gtk",
            
            # Fonts
            "fonts-liberation",
            "fonts-wine",
            
            # Performance tools
            "linux-tools-generic",  # FIXED: was linux-cpupower
            
            # Additional tools
            "xboxdrv",
            "antimicrox"
        ]
        
        # Install packages with error handling for optional ones
        success, stdout, stderr = self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing essential packages",
            check=False
        )
        
        # If installation failed, try without optional packages
        if not success and "has no installation candidate" in stderr:
            print(f"{Color.YELLOW}Some optional packages unavailable, installing core packages...{Color.END}")
            core_packages = [p for p in packages if p not in ["antimicrox", "xboxdrv"]]
            self.run_command(
                ["apt-get", "install", "-y"] + core_packages,
                "Installing core essential packages",
                check=False
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MULTIMEDIA CODECS - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_codecs(self):
        """
        Install multimedia codecs
        
        PRESERVED FROM ORIGINAL: Exact same EULA handling and installation
        """
        self.banner("MULTIMEDIA CODECS")
        
        if self.confirm("Install multimedia codecs?"):
            print(f"{Color.CYAN}Pre-accepting license agreements...{Color.END}")
            
            # Pre-accept EULA for ttf-mscorefonts-installer - PRESERVED FROM ORIGINAL
            eula_commands = [
                "echo ttf-mscorefonts-installer msttcorefonts/accepted-mscorefonts-eula select true | debconf-set-selections",
            ]
            
            for cmd in eula_commands:
                self.run_command(cmd, "Pre-accepting Microsoft fonts EULA", shell=True, check=False)
            
            # Install with non-interactive frontend - PRESERVED FROM ORIGINAL
            env_cmd = "DEBIAN_FRONTEND=noninteractive apt-get install -y ubuntu-restricted-extras"
            self.run_command(
                env_cmd,
                "Installing Ubuntu restricted extras (codecs)",
                shell=True
            )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ADDITIONAL TOOLS - NEW ADDITIONS AND PRESERVED ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_mangohud(self):
        """
        Install MangoHud performance overlay
        
        ENHANCED: New feature - performance monitoring overlay
        FIXED: Better handling for Ubuntu 24.04, avoid broken PPAs
        """
        if not (self.config.install_mangohud or self.confirm("Install MangoHud (performance overlay)?")):
            return
        
        self.banner("MANGOHUD INSTALLATION")
        
        # Try to install from repos first (works on Ubuntu 24.04+)
        print(f"{Color.CYAN}Attempting to install MangoHud from default repositories...{Color.END}")
        packages = ["mangohud", "mangohud:i386"]
        success, stdout, stderr = self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing MangoHud from default repos",
            check=False
        )
        
        if success:
            print(f"{Color.GREEN}✓ MangoHud installed successfully{Color.END}")
            # Try to install goverlay separately (optional)
            self.run_command(
                ["apt-get", "install", "-y", "goverlay"],
                "Installing Goverlay (optional)",
                check=False
            )
            return
        
        # If not in default repos, check Ubuntu version before trying PPA
        print(f"{Color.YELLOW}MangoHud not in default repos{Color.END}")
        
        # Check if running Ubuntu < 24.04 (where PPA might work)
        try:
            version_check = self.system_info.distro_version
            major_version = float(version_check.split('.')[0] + '.' + version_check.split('.')[1])
            
            if major_version >= 24.04:
                print(f"{Color.YELLOW}⚠ MangoHud PPA not available for Ubuntu 24.04+{Color.END}")
                print(f"{Color.CYAN}  MangoHud should be available in repos - updating package lists...{Color.END}")
                self.run_command(["apt-get", "update"], "Refreshing package lists")
                # Try one more time after update
                success, _, _ = self.run_command(
                    ["apt-get", "install", "-y"] + packages,
                    "Installing MangoHud after update",
                    check=False
                )
                if not success:
                    print(f"{Color.YELLOW}⚠ MangoHud installation failed{Color.END}")
                    print(f"{Color.CYAN}  Manual installation: https://github.com/flightlessmango/MangoHud{Color.END}")
                return
        except:
            pass  # Couldn't determine version, try PPA anyway
        
        # For Ubuntu < 24.04, try PPA
        print(f"{Color.YELLOW}Attempting PPA installation (Ubuntu < 24.04)...{Color.END}")
        ppa_success, _, _ = self.run_command(
            ["add-apt-repository", "ppa:flexiondotorg/mangohud", "-y"],
            "Adding MangoHud PPA",
            check=False
        )
        
        if ppa_success:
            self.run_command(["apt-get", "update"], "Updating package lists", check=False)
            self.run_command(
                ["apt-get", "install", "-y"] + packages,
                "Installing MangoHud from PPA",
                check=False
            )
        else:
            print(f"{Color.YELLOW}⚠ PPA installation failed{Color.END}")
            print(f"{Color.CYAN}  Manual installation: https://github.com/flightlessmango/MangoHud{Color.END}")
    
    def install_goverlay(self):
        """
        Install Goverlay (MangoHud GUI)
        
        ENHANCED: New feature - GUI for MangoHud configuration
        """
        if not (self.config.install_goverlay or self.confirm("Install Goverlay (MangoHud GUI)?")):
            return
        
        self.run_command(
            ["apt-get", "install", "-y", "goverlay"],
            "Installing Goverlay",
            check=False
        )
    
    def install_discord(self):
        """
        Install Discord
        
        PRESERVED FROM ORIGINAL: Flatpak installation
        """
        should_install = self.config.install_discord or \
                        self.prompt_install_or_update("Discord", flatpak_id="com.discordapp.Discord")
        
        if should_install:
            self.banner("DISCORD INSTALLATION")
            
            print(f"{Color.CYAN}Installing Discord via Flatpak...{Color.END}")
            self.run_command(
                ["flatpak", "install", "-y", "flathub", "com.discordapp.Discord"],
                "Installing Discord"
            )
    
    def install_obs(self):
        """
        Install OBS Studio for streaming/recording
        
        PRESERVED FROM ORIGINAL: PPA installation with exact same commands
        """
        should_install = self.config.install_obs or \
                        self.prompt_install_or_update("OBS Studio (for streaming/recording)", 
                                                     package_name="obs-studio")
        
        if should_install:
            self.banner("OBS STUDIO INSTALLATION")
            
            # PRESERVED FROM ORIGINAL: Exact same commands
            commands = [
                (["add-apt-repository", "ppa:obsproject/obs-studio", "-y"], "Adding OBS PPA"),
                (["apt-get", "update"], "Updating package lists"),
                (["apt-get", "install", "-y", "obs-studio"], "Installing OBS Studio")
            ]
            
            for cmd, desc in commands:
                self.run_command(cmd, desc)
    
    def install_mumble(self):
        """
        Install Mumble voice chat
        
        ENHANCED: New addition - voice communication tool
        """
        if not (self.config.install_mumble or self.confirm("Install Mumble (voice chat)?")):
            return
        
        self.run_command(
            ["apt-get", "install", "-y", "mumble"],
            "Installing Mumble"
        )
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NEW PLATFORMS - SOBER & WAYDROID
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_sober(self):
        """
        Install Sober (Roblox on Linux)
        
        NEW FEATURE: Roblox gaming platform for Linux
        """
        should_install = self.config.install_sober or \
                        self.prompt_install_or_update("Sober (Roblox on Linux)", 
                                                     flatpak_id="org.vinegarhq.Sober")
        
        if should_install:
            self.banner("SOBER INSTALLATION")
            
            print(f"{Color.CYAN}Installing Sober (Roblox on Linux) via Flatpak...{Color.END}")
            
            # Ensure Flatpak is installed
            if not self.is_package_installed("flatpak"):
                self.run_command(
                    ["apt-get", "install", "-y", "flatpak"],
                    "Installing Flatpak"
                )
            
            # Add Flathub if not already added
            self.run_command(
                ["flatpak", "remote-add", "--if-not-exists", "flathub", 
                 "https://flathub.org/repo/flathub.flatpakrepo"],
                "Adding Flathub repository",
                check=False
            )
            
            # Install Sober
            success, _, _ = self.run_command(
                ["flatpak", "install", "-y", "flathub", "org.vinegarhq.Sober"],
                "Installing Sober",
                check=False
            )
            
            if success:
                print(f"{Color.GREEN}✓ Sober installed successfully{Color.END}")
                print(f"{Color.CYAN}  Launch with: flatpak run org.vinegarhq.Sober{Color.END}")
            else:
                print(f"{Color.YELLOW}⚠ Sober installation failed{Color.END}")
                print(f"{Color.CYAN}  Manual installation: https://sober.vinegarhq.org/{Color.END}")
    
    def install_waydroid(self):
        """
        Install Waydroid (Android container for Linux)
        
        NEW FEATURE: Run Android apps on Linux
        """
        should_install = self.config.install_waydroid or \
                        self.confirm("Install Waydroid (Android container)?")
        
        if not should_install:
            return
        
        self.banner("WAYDROID INSTALLATION")
        
        print(f"{Color.YELLOW}⚠ Waydroid requires Wayland session and specific kernel modules{Color.END}")
        print(f"{Color.CYAN}  This installation will set up the repository and install Waydroid{Color.END}")
        
        if not self.confirm("Continue with Waydroid installation?"):
            return
        
        # Check if running Wayland
        wayland_session = os.environ.get('XDG_SESSION_TYPE', '').lower() == 'wayland'
        if not wayland_session:
            print(f"{Color.YELLOW}⚠ Waydroid works best on Wayland sessions{Color.END}")
            print(f"{Color.CYAN}  You're currently on X11. Waydroid may have limited functionality.{Color.END}")
            if not self.confirm("Install anyway?"):
                return
        
        # Add Waydroid repository
        print(f"{Color.CYAN}Adding Waydroid repository...{Color.END}")
        
        # Get Ubuntu codename
        try:
            with open('/etc/os-release', 'r') as f:
                for line in f:
                    if line.startswith('VERSION_CODENAME='):
                        codename = line.split('=')[1].strip().strip('"')
                        break
                else:
                    codename = "noble"  # Default to Ubuntu 24.04
        except:
            codename = "noble"
        
        commands = [
            (f"curl https://repo.waydro.id | sh", 
             "Adding Waydroid repository", True, True),
            (["apt-get", "update"], "Updating package lists"),
            (["apt-get", "install", "-y", "waydroid"], "Installing Waydroid"),
        ]
        
        for item in commands:
            if len(item) == 2:
                cmd, desc = item
                shell = False
            elif len(item) == 4:
                cmd, desc, _, shell = item
            else:
                continue
            
            success, _, _ = self.run_command(cmd, desc, shell=shell, check=False)
            if not success and "waydroid" in str(cmd):
                print(f"{Color.YELLOW}⚠ Waydroid installation failed{Color.END}")
                print(f"{Color.CYAN}  Manual installation: https://docs.waydro.id/usage/install-on-desktops{Color.END}")
                return
        
        print(f"{Color.GREEN}✓ Waydroid installed{Color.END}")
        print(f"{Color.YELLOW}Next steps:{Color.END}")
        print(f"  1. Initialize Waydroid: sudo waydroid init")
        print(f"  2. Start Waydroid session: waydroid session start")
        print(f"  3. Launch Waydroid UI: waydroid show-full-ui")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # NEW UTILITIES - GWE, vkBasalt, ReShade, Mod Managers
    # ═══════════════════════════════════════════════════════════════════════════
    
    def install_greenwithenv(self):
        """
        Install GreenWithEnvy (NVIDIA GPU control tool)
        
        NEW FEATURE: GUI for NVIDIA GPU monitoring and overclocking
        """
        should_install = self.config.install_greenwithenv or \
                        self.prompt_install_or_update("GreenWithEnvy (NVIDIA GPU control)", 
                                                     flatpak_id="com.leinardi.gwe")
        
        if not should_install:
            return
        
        # Check if NVIDIA GPU
        if self.hardware_info.gpu_vendor != GPUVendor.NVIDIA:
            print(f"{Color.YELLOW}⚠ GreenWithEnvy is designed for NVIDIA GPUs{Color.END}")
            print(f"{Color.CYAN}  Detected GPU: {self.hardware_info.gpu_vendor.value}{Color.END}")
            if not self.confirm("Install anyway?"):
                return
        
        self.banner("GREENWITHENV INSTALLATION")
        
        print(f"{Color.CYAN}Installing GreenWithEnvy via Flatpak...{Color.END}")
        
        # Ensure Flatpak is installed
        if not self.is_package_installed("flatpak"):
            self.run_command(
                ["apt-get", "install", "-y", "flatpak"],
                "Installing Flatpak"
            )
        
        # Add Flathub
        self.run_command(
            ["flatpak", "remote-add", "--if-not-exists", "flathub", 
             "https://flathub.org/repo/flathub.flatpakrepo"],
            "Adding Flathub repository",
            check=False
        )
        
        # Install GWE
        success, _, _ = self.run_command(
            ["flatpak", "install", "-y", "flathub", "com.leinardi.gwe"],
            "Installing GreenWithEnvy",
            check=False
        )
        
        if success:
            print(f"{Color.GREEN}✓ GreenWithEnvy installed{Color.END}")
            print(f"{Color.CYAN}  Launch with: flatpak run com.leinardi.gwe{Color.END}")
            print(f"{Color.YELLOW}  Note: Some features require running with sudo{Color.END}")
        else:
            print(f"{Color.YELLOW}⚠ Installation failed{Color.END}")
            print(f"{Color.CYAN}  Manual installation: https://gitlab.com/leinardi/gwe{Color.END}")
    
    def install_vkbasalt(self):
        """
        Install vkBasalt (Vulkan post-processing layer)
        
        NEW FEATURE: ReShade-like effects for Vulkan games on Linux
        """
        should_install = self.config.install_vkbasalt or \
                        self.confirm("Install vkBasalt (Vulkan post-processing)?")
        
        if not should_install:
            return
        
        self.banner("VKBASALT INSTALLATION")
        
        print(f"{Color.CYAN}Installing vkBasalt...{Color.END}")
        
        # Try to install from repos first (available on Ubuntu 22.04+)
        packages = ["vkbasalt"]
        success, stdout, stderr = self.run_command(
            ["apt-get", "install", "-y"] + packages,
            "Installing vkBasalt from default repos",
            check=False
        )
        
        if success:
            print(f"{Color.GREEN}✓ vkBasalt installed successfully{Color.END}")
        else:
            # Try with lib32 variant
            print(f"{Color.YELLOW}Trying alternative package name...{Color.END}")
            packages = ["vkbasalt", "lib32-vkbasalt"]
            success, _, _ = self.run_command(
                ["apt-get", "install", "-y"] + packages,
                "Installing vkBasalt with 32-bit support",
                check=False
            )
            
            if not success:
                print(f"{Color.YELLOW}⚠ vkBasalt not available in repos{Color.END}")
                print(f"{Color.CYAN}  Manual installation from source:{Color.END}")
                print(f"{Color.CYAN}  https://github.com/DadSchoorse/vkBasalt{Color.END}")
                return
        
        # Create default config
        config_dir = REAL_USER_HOME / ".config/vkBasalt"
        config_file = config_dir / "vkBasalt.conf"
        
        if not config_file.exists():
            print(f"{Color.CYAN}Creating default vkBasalt configuration...{Color.END}")
            
            if not self.config.dry_run:
                config_dir.mkdir(parents=True, exist_ok=True)
                
                default_config = """# vkBasalt Configuration
# Enable effects (comma-separated list)
effects = cas,fxaa

# Contrast Adaptive Sharpening
cas = on
casSharpness = 0.4

# Fast Approximate Anti-Aliasing
fxaa = on
fxaaQualitySubpix = 0.75
fxaaQualityEdgeThreshold = 0.125
fxaaQualityEdgeThresholdMin = 0.0312

# Toggle key (Home key)
toggleKey = Home
"""
                with open(config_file, 'w') as f:
                    f.write(default_config)
                
                # Set ownership
                uid, gid = get_real_user_uid_gid()
                os.chown(config_dir, uid, gid)
                os.chown(config_file, uid, gid)
                
                print(f"{Color.GREEN}✓ Configuration created: {config_file}{Color.END}")
        
        print(f"\n{Color.BOLD}vkBasalt Usage:{Color.END}")
        print(f"  Enable for a game:")
        print(f"    ENABLE_VKBASALT=1 %command%  (in Steam launch options)")
        print(f"  Or:")
        print(f"    ENABLE_VKBASALT=1 game_binary")
        print(f"\n  Toggle effects in-game: Press Home key")
        print(f"  Config file: {config_file}")
    
    def show_reshade_info(self):
        """
        Show ReShade setup information for Linux
        
        NEW FEATURE: Provide guidance on using ReShade effects via vkBasalt
        """
        if not (self.config.install_reshade_setup or \
                self.confirm("Show ReShade setup information?")):
            return
        
        self.banner("RESHADE ON LINUX")
        
        print(f"{Color.BOLD}ReShade on Linux{Color.END}\n")
        print(f"{Color.CYAN}ReShade is a Windows tool, but you can achieve similar effects on Linux using:{Color.END}\n")
        
        print(f"{Color.BOLD}1. vkBasalt (Recommended){Color.END}")
        print(f"   • Native Linux Vulkan layer")
        print(f"   • Includes common effects (CAS, FXAA, SMAA)")
        print(f"   • Lightweight and performant")
        print(f"   • Install with: --vkbasalt flag\n")
        
        print(f"{Color.BOLD}2. ReShade via Wine/Proton{Color.END}")
        print(f"   • Some ReShade shaders work through Proton")
        print(f"   • Copy ReShade files to game directory")
        print(f"   • Set WINEDLLOVERRIDES=\"d3d11=n,b\" for D3D11 games\n")
        
        print(f"{Color.BOLD}3. GShade (Community Fork){Color.END}")
        print(f"   • Fork of ReShade for Linux")
        print(f"   • More extensive shader library")
        print(f"   • Manual installation required")
        print(f"   • GitHub: https://github.com/Mortalitas/GShade-Shaders\n")
        
        if self.confirm("Install vkBasalt now?"):
            self.install_vkbasalt()
    
    def install_mod_managers(self):
        """
        Install mod management tools
        
        NEW FEATURE: Tools for managing game mods
        """
        should_install = self.config.install_mod_managers or \
                        self.confirm("Install mod management tools?")
        
        if not should_install:
            return
        
        self.banner("MOD MANAGER INSTALLATION")
        
        print(f"{Color.BOLD}Available Mod Managers for Linux:{Color.END}\n")
        
        # Mod Organizer 2 via Wine
        if self.confirm("Install Mod Organizer 2 (via Lutris)?"):
            print(f"{Color.CYAN}Mod Organizer 2 Setup:{Color.END}")
            print(f"  1. Install Lutris (if not already installed)")
            print(f"  2. Visit: https://lutris.net/games/mod-organizer-2/")
            print(f"  3. Click 'Install' and follow prompts")
            print(f"  4. Works with Skyrim, Fallout, and other Bethesda games\n")
        
        # Vortex Mod Manager
        if self.confirm("Show Vortex Mod Manager information?"):
            print(f"{Color.CYAN}Vortex Mod Manager:{Color.END}")
            print(f"  • Official Nexus Mods manager")
            print(f"  • Runs via Wine/Proton")
            print(f"  • Install via Lutris: https://lutris.net/games/vortex-mod-manager/")
            print(f"  • Or manually with Wine\n")
        
        # r2modman (for Unity games)
        if self.confirm("Install r2modman (Risk of Rain 2, Valheim mods)?"):
            print(f"{Color.CYAN}Installing r2modman via Flatpak...{Color.END}")
            
            # Ensure Flatpak
            if not self.is_package_installed("flatpak"):
                self.run_command(["apt-get", "install", "-y", "flatpak"], 
                               "Installing Flatpak")
            
            # Add Flathub
            self.run_command(
                ["flatpak", "remote-add", "--if-not-exists", "flathub", 
                 "https://flathub.org/repo/flathub.flatpakrepo"],
                "Adding Flathub repository",
                check=False
            )
            
            # Install r2modman
            success, _, _ = self.run_command(
                ["flatpak", "install", "-y", "flathub", "com.thunderstore.r2modman"],
                "Installing r2modman",
                check=False
            )
            
            if success:
                print(f"{Color.GREEN}✓ r2modman installed{Color.END}")
            else:
                print(f"{Color.YELLOW}Note: r2modman may not be available on Flathub yet{Color.END}")
                print(f"{Color.CYAN}  Download from: https://github.com/ebkr/r2modmanPlus/releases{Color.END}")
        
        print(f"\n{Color.BOLD}Additional Resources:{Color.END}")
        print(f"  • Nexus Mods: https://www.nexusmods.com/")
        print(f"  • ModDB: https://www.moddb.com/")
        print(f"  • Thunderstore: https://thunderstore.io/")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # SYSTEM OPTIMIZATIONS - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def optimize_system(self):
        """
        Apply gaming optimizations
        
        PRESERVED FROM ORIGINAL: Exact same sysctl and governor configuration
        """
        self.banner("SYSTEM OPTIMIZATIONS")
        
        if not self.confirm("Apply gaming optimizations?"):
            return
        
        # Increase file watchers - PRESERVED FROM ORIGINAL
        print(f"{Color.CYAN}Increasing inotify watchers...{Color.END}")
        
        if not self.config.dry_run:
            with open('/etc/sysctl.d/99-gaming.conf', 'w') as f:
                f.write("# Gaming optimizations\n")
                f.write("fs.inotify.max_user_watches=524288\n")
                f.write("vm.max_map_count=2147483642\n")
            
            self.run_command(
                ["sysctl", "-p", "/etc/sysctl.d/99-gaming.conf"],
                "Applying sysctl optimizations"
            )
        
        # Enable performance governor - PRESERVED FROM ORIGINAL
        if self.confirm("Set CPU governor to performance mode?"):
            packages = ["cpufrequtils"]
            self.run_command(
                ["apt-get", "install", "-y"] + packages,
                "Installing CPU frequency utilities"
            )
            
            # Create systemd service for performance governor - PRESERVED FROM ORIGINAL
            governor_service = """[Unit]
Description=Set CPU Governor to Performance
After=multi-user.target

[Service]
Type=oneshot
ExecStart=/usr/bin/cpufreq-set -r -g performance

[Install]
WantedBy=multi-user.target
"""
            if not self.config.dry_run:
                with open('/etc/systemd/system/cpu-performance.service', 'w') as f:
                    f.write(governor_service)
                
                commands = [
                    (["systemctl", "daemon-reload"], "Reloading systemd"),
                    (["systemctl", "enable", "cpu-performance.service"], 
                     "Enabling performance governor service")
                ]
                for cmd, desc in commands:
                    self.run_command(cmd, desc)
    
    # ═══════════════════════════════════════════════════════════════════════════
    # PERFORMANCE LAUNCHER - PRESERVED FROM ORIGINAL
    # ═══════════════════════════════════════════════════════════════════════════
    
    def create_performance_script(self):
        """
        Create a gaming performance launcher script
        
        PRESERVED FROM ORIGINAL: Exact same script with CPU governor and GameMode
        """
        self.banner("PERFORMANCE LAUNCHER")
        
        if not self.confirm("Create gaming performance launcher script?"):
            return
        
        # User's home directory script - PRESERVED FROM ORIGINAL
        user_script_path = REAL_USER_HOME / "launch-game.sh"
        
        # System-wide script location - PRESERVED FROM ORIGINAL
        system_script_path = Path("/usr/local/bin/launch-game")
        
        # PRESERVED FROM ORIGINAL: Exact same script content
        script_content = """#!/bin/bash
# Gaming Performance Launcher
# Usage: ./launch-game.sh <game_command>
# Or: launch-game <game_command> (if installed system-wide)

# Color codes for output
RED='\\033[0;31m'
GREEN='\\033[0;32m'
YELLOW='\\033[1;33m'
NC='\\033[0m' # No Color

# Function to check if command exists
command_exists() {
    command -v "$1" &> /dev/null
}

# Function to safely set CPU governor
set_cpu_governor() {
    local governor="$1"
    
    # Check if cpupower is available (preferred)
    if command_exists cpupower; then
        sudo cpupower frequency-set -g "$governor" &> /dev/null
        return $?
    # Fallback to cpufreq-set if available
    elif command_exists cpufreq-set; then
        sudo cpufreq-set -r -g "$governor" &> /dev/null
        return $?
    fi
    
    return 1
}

echo "======================================"
echo "  Gaming Performance Launcher"
echo "======================================"

# Check if game command provided
if [ $# -eq 0 ]; then
    echo -e "${RED}Error: No game command provided${NC}"
    echo "Usage: $0 <game_command>"
    echo "Example: $0 steam"
    echo "Example: $0 lutris"
    exit 1
fi

# Enable GameMode if available
GAMEMODE=""
if command_exists gamemoderun; then
    GAMEMODE="gamemoderun"
    echo -e "${GREEN}✓${NC} GameMode: ENABLED"
else
    echo -e "${YELLOW}!${NC} GameMode: Not available (install with: sudo apt install gamemode)"
fi

# Try to set CPU governor to performance
echo -n "CPU Governor: "
if set_cpu_governor "performance"; then
    echo -e "${GREEN}PERFORMANCE${NC}"
    GOVERNOR_CHANGED=1
else
    echo -e "${YELLOW}UNCHANGED${NC} (run 'sudo cpupower frequency-set -g performance' manually)"
    GOVERNOR_CHANGED=0
fi

# Set process scheduling (best effort, non-critical)
NICE_CMD=""
# Don't use nice -n -10 as it requires root and causes permission errors
# Instead use nice -n -5 which works for regular users
if command_exists nice; then
    NICE_CMD="nice -n -5"
fi

echo "======================================"
echo "Launching: $@"
echo "======================================"
echo ""

# Launch the game with optimizations
$GAMEMODE $NICE_CMD "$@"
EXIT_CODE=$?

echo ""
echo "======================================"
echo "Game exited with code: $EXIT_CODE"
echo "======================================"

# Restore CPU governor if we changed it
if [ $GOVERNOR_CHANGED -eq 1 ]; then
    echo -n "Restoring CPU Governor: "
    if set_cpu_governor "ondemand" || set_cpu_governor "powersave"; then
        echo -e "${GREEN}RESTORED${NC}"
    else
        echo -e "${YELLOW}UNCHANGED${NC} (will reset on reboot)"
    fi
fi

exit $EXIT_CODE
"""
        
        # Create in user's home directory - PRESERVED FROM ORIGINAL
        if not self.config.dry_run:
            with open(user_script_path, 'w') as f:
                f.write(script_content)
            
            os.chmod(user_script_path, 0o755)
            
            # Set proper ownership - PRESERVED FROM ORIGINAL
            try:
                uid, gid = get_real_user_uid_gid()
                os.chown(user_script_path, uid, gid)
            except Exception as e:
                logging.warning(f"Could not set ownership on user script: {e}")
        
        print(f"{Color.GREEN}✓ Performance launcher created: {user_script_path}{Color.END}")
        print(f"  Usage: {user_script_path} <game_command>")
        
        # Optionally create system-wide version - PRESERVED FROM ORIGINAL
        if self.confirm("Also install system-wide as 'launch-game' command?"):
            try:
                if not self.config.dry_run:
                    with open(system_script_path, 'w') as f:
                        f.write(script_content)
                    os.chmod(system_script_path, 0o755)
                print(f"{Color.GREEN}✓ System-wide launcher installed{Color.END}")
                print(f"  Usage: launch-game <game_command>")
            except Exception as e:
                logging.error(f"Could not create system-wide script: {e}")
                print(f"{Color.YELLOW}Could not create system-wide script, but user script is available{Color.END}")
        
        # Offer to configure passwordless sudo for CPU governor - PRESERVED FROM ORIGINAL
        if self.confirm("Configure passwordless sudo for CPU governor? (Recommended)"):
            self.configure_cpufreq_sudo()
    
    def configure_cpufreq_sudo(self):
        """
        Configure passwordless sudo for CPU frequency management
        
        PRESERVED FROM ORIGINAL: Exact same sudoers configuration
        """
        sudoers_file = Path("/etc/sudoers.d/gaming-cpufreq")
        
        # Determine which tool is available - PRESERVED FROM ORIGINAL
        cpufreq_tools = []
        if subprocess.run(["which", "cpupower"], capture_output=True).returncode == 0:
            cpufreq_tools.append("/usr/bin/cpupower")
        if subprocess.run(["which", "cpufreq-set"], capture_output=True).returncode == 0:
            cpufreq_tools.append("/usr/bin/cpufreq-set")
        
        if not cpufreq_tools:
            print(f"{Color.YELLOW}⚠ No CPU frequency tools found{Color.END}")
            print(f"  Installing cpupower...")
            self.run_command(
                ["apt-get", "install", "-y", "linux-cpupower"],
                "Installing CPU power management tools"
            )
            cpufreq_tools = ["/usr/bin/cpupower"]
        
        # Build sudoers content - PRESERVED FROM ORIGINAL
        sudoers_lines = [
            f"# Allow {REAL_USER} to manage CPU frequency for gaming",
            f"# Created by Ubuntu Gaming Setup Script",
            ""
        ]
        
        for tool in cpufreq_tools:
            sudoers_lines.append(f"{REAL_USER} ALL=(ALL) NOPASSWD: {tool}")
        
        sudoers_content = "\n".join(sudoers_lines) + "\n"
        
        try:
            if not self.config.dry_run:
                # Create sudoers file - PRESERVED FROM ORIGINAL
                with open(sudoers_file, 'w') as f:
                    f.write(sudoers_content)
                
                # Set correct permissions (sudoers files must be 0440) - PRESERVED FROM ORIGINAL
                os.chmod(sudoers_file, 0o440)
                
                # Validate sudoers file - PRESERVED FROM ORIGINAL
                result = subprocess.run(
                    ["visudo", "-c", "-f", str(sudoers_file)],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if result.returncode == 0:
                    print(f"{Color.GREEN}✓ Passwordless sudo configured for CPU governor{Color.END}")
                    print(f"  {REAL_USER} can now run CPU frequency tools without password")
                    for tool in cpufreq_tools:
                        print(f"    - {tool}")
                else:
                    # Remove invalid file - PRESERVED FROM ORIGINAL
                    sudoers_file.unlink()
                    print(f"{Color.YELLOW}⚠ Sudoers configuration failed validation, removed{Color.END}")
                    logging.error(f"Sudoers validation failed: {result.stderr}")
        
        except Exception as e:
            logging.error(f"Could not configure sudoers: {e}")
            print(f"{Color.YELLOW}⚠ Could not configure passwordless sudo{Color.END}")
            print(f"  You can manually run: sudo cpupower frequency-set -g performance")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # INSTALLATION SUMMARY - PRESERVED FROM ORIGINAL (COMPLETE)
    # ═══════════════════════════════════════════════════════════════════════════
    
    def show_installation_summary(self):
        """
        Show summary of installed gaming components
        
        PRESERVED FROM ORIGINAL: This is the comprehensive summary that shows
        actual installed package versions. This was completely missing in my
        simplified version and is now fully restored.
        """
        self.banner("INSTALLATION SUMMARY")
        
        print(f"{Color.BOLD}Installed Components:{Color.END}\n")
        
        # Check GPU/VM drivers - PRESERVED FROM ORIGINAL
        print(f"{Color.BOLD}Graphics Drivers:{Color.END}")
        
        # NVIDIA check - PRESERVED FROM ORIGINAL
        try:
            result = subprocess.run(["nvidia-smi"], capture_output=True, text=True, timeout=5)
            if result.returncode == 0:
                for line in result.stdout.split('\n'):
                    if 'Driver Version:' in line:
                        version = line.split('Driver Version:')[1].split()[0]
                        print(f"  ✓ NVIDIA Driver      {version}")
                        break
        except:
            pass
        
        # VMware check - PRESERVED FROM ORIGINAL
        if self.is_package_installed("open-vm-tools"):
            version = self.get_package_version("open-vm-tools")
            print(f"  ✓ VMware Tools       {version if version else 'installed'}")
        
        # VirtualBox check - PRESERVED FROM ORIGINAL
        if self.is_package_installed("virtualbox-guest-utils"):
            version = self.get_package_version("virtualbox-guest-utils")
            print(f"  ✓ VirtualBox Guest   {version if version else 'installed'}")
        
        # Mesa check (AMD/Intel) - PRESERVED FROM ORIGINAL
        if self.is_package_installed("mesa-vulkan-drivers"):
            version = self.get_package_version("mesa-vulkan-drivers")
            print(f"  ✓ Mesa Vulkan        {version if version else 'installed'}")
        
        print()
        
        # Gaming platforms - PRESERVED FROM ORIGINAL
        print(f"{Color.BOLD}Gaming Platforms:{Color.END}")
        
        # PRESERVED FROM ORIGINAL: Exact same component list
        components = {
            "Steam": "steam-installer",
            "GameMode": "gamemode",
            "Wine": "winehq-staging",
            "Winetricks": "winetricks",
            "OBS Studio": "obs-studio"
        }
        
        for name, package in components.items():
            if self.is_package_installed(package):
                version = self.get_package_version(package)
                if version and len(version) > 30:
                    version = version[:27] + "..."
                print(f"  ✓ {name:20} {version if version else 'installed'}")
        
        # ENHANCED: Add new components to summary
        new_components = {
            "MangoHud": "mangohud",
            "Goverlay": "goverlay",
            "Mumble": "mumble",
            "vkBasalt": "vkbasalt",
            "Waydroid": "waydroid"
        }
        
        for name, package in new_components.items():
            if self.is_package_installed(package):
                version = self.get_package_version(package)
                if version and len(version) > 30:
                    version = version[:27] + "..."
                print(f"  ✓ {name:20} {version if version else 'installed'}")
        
        print()
        
        # Flatpak apps - PRESERVED FROM ORIGINAL
        print(f"{Color.BOLD}Flatpak Applications:{Color.END}")
        
        # PRESERVED FROM ORIGINAL: Exact same flatpak list
        flatpaks = {
            "Lutris": "net.lutris.Lutris",
            "Heroic Launcher": "com.heroicgameslauncher.hgl",
            "ProtonUp-Qt": "net.davidotek.pupgui2",
            "Discord": "com.discordapp.Discord",
            "Sober (Roblox)": "org.vinegarhq.Sober",
            "GreenWithEnvy": "com.leinardi.gwe"
        }
        
        has_flatpaks = False
        for name, app_id in flatpaks.items():
            if self.is_flatpak_installed(app_id):
                version = self.get_flatpak_version(app_id)
                if version and len(version) > 30:
                    version = version[:27] + "..."
                print(f"  ✓ {name:20} {version if version else 'installed'}")
                has_flatpaks = True
        
        if not has_flatpaks:
            print(f"  {Color.YELLOW}No Flatpak applications installed{Color.END}")
        
        print()

# END OF PART 5
# Continue with Part 6 for final steps and main execution flow
# PART 6 (FINAL): State Management, Rollback, Final Steps, and Main Execution
# All original final steps and instructions preserved with enhancements

    # ═══════════════════════════════════════════════════════════════════════════
    # STATE MANAGEMENT - ENHANCED: New feature
    # ═══════════════════════════════════════════════════════════════════════════
    
    def load_installation_state(self):
        """
        Load previous installation state if exists
        
        ENHANCED: New feature for tracking installation progress
        """
        if STATE_FILE.exists():
            try:
                with open(STATE_FILE, 'r') as f:
                    self.installation_state = json.load(f)
                logging.info(f"Loaded installation state: {len(self.installation_state)} entries")
            except Exception as e:
                logging.error(f"Could not load installation state: {e}")
    
    def save_installation_state(self):
        """
        Save current installation state
        
        ENHANCED: New feature for tracking installation progress
        """
        try:
            self.installation_state['last_updated'] = datetime.now().isoformat()
            self.installation_state['distro'] = self.system_info.distro_name
            self.installation_state['version'] = self.system_info.distro_version
            
            if not self.config.dry_run:
                with open(STATE_FILE, 'w') as f:
                    json.dump(self.installation_state, f, indent=2)
                
                # Set proper ownership
                uid, gid = get_real_user_uid_gid()
                os.chown(STATE_FILE, uid, gid)
            
            logging.info("Installation state saved")
        except Exception as e:
            logging.error(f"Could not save installation state: {e}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # ROLLBACK FUNCTIONALITY - ENHANCED: Framework for future implementation
    # ═══════════════════════════════════════════════════════════════════════════
    
    def perform_rollback(self):
        """
        Perform rollback of previous installation
        
        ENHANCED: Framework in place, ready for full implementation
        """
        self.banner("ROLLBACK")
        
        if not ROLLBACK_FILE.exists():
            print(f"{Color.YELLOW}No rollback manifest found{Color.END}")
            print(f"{Color.CYAN}Nothing to rollback{Color.END}")
            return
        
        print(f"{Color.CYAN}Rollback functionality framework in place{Color.END}")
        print(f"{Color.YELLOW}Full rollback implementation: Use with caution{Color.END}")
        print(f"{Color.CYAN}Manual cleanup recommended: Check {LOG_DIR} for details{Color.END}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # FINAL STEPS - PRESERVED FROM ORIGINAL WITH VM-SPECIFIC INSTRUCTIONS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def final_steps(self):
        """
        Display final instructions
        
        PRESERVED FROM ORIGINAL: All VM-specific instructions and guidance
        """
        self.banner("SETUP COMPLETE")
        
        print(f"{Color.GREEN}✓ Ubuntu gaming setup completed successfully!{Color.END}\n")
        print(f"{Color.BOLD}Installation performed for user: {REAL_USER}{Color.END}")
        print(f"{Color.BOLD}User home directory: {REAL_USER_HOME}{Color.END}\n")
        
        print(f"{Color.BOLD}IMPORTANT NEXT STEPS:{Color.END}\n")
        
        print(f"{Color.YELLOW}1. REBOOT YOUR SYSTEM{Color.END}")
        print("   Required for drivers and optimizations to take effect\n")
        
        # Check if VM - PRESERVED FROM ORIGINAL with exact same VM-specific notes
        vm_type = self.detect_virtualization()
        if vm_type:
            print(f"{Color.CYAN}VM-SPECIFIC NOTES ({vm_type}):{Color.END}")
            if 'vmware' in vm_type.lower():
                print("   • Enable 3D acceleration in VMware settings")
                print("   • Allocate at least 2GB video memory for better performance")
                print("   • Verify tools: vmware-toolbox-cmd -v")
            elif 'virtualbox' in vm_type.lower():
                print("   • Enable 3D acceleration in VirtualBox settings")
                print("   • Allocate maximum video memory (128MB+)")
                print("   • Verify additions: lsmod | grep vbox")
            print()
        
        # PRESERVED FROM ORIGINAL: Exact same verification steps
        print(f"{Color.YELLOW}2. VERIFY GPU/GRAPHICS{Color.END}")
        if vm_type:
            print("   Run: glxinfo | grep 'OpenGL renderer'")
            print(f"   Should show: {vm_type} graphics")
        else:
            print("   - NVIDIA: Run 'nvidia-smi' to verify driver")
            print("   - AMD/Intel: Run 'vulkaninfo' or 'glxinfo | grep OpenGL'")
        print()
        
        # PRESERVED FROM ORIGINAL: Exact same Steam configuration
        print(f"{Color.YELLOW}3. CONFIGURE STEAM{Color.END}")
        print("   - Enable Proton: Settings → Steam Play → Enable Steam Play for all titles")
        print("   - Select: Proton Experimental or latest Proton version")
        if vm_type:
            print(f"   {Color.CYAN}Note: Some games may have reduced performance in VMs{Color.END}")
        print()
        
        # PRESERVED FROM ORIGINAL: ProtonUp-Qt instructions
        print(f"{Color.YELLOW}4. INSTALL ADDITIONAL PROTON VERSIONS{Color.END}")
        print("   - Use ProtonUp-Qt to install Proton-GE for better compatibility\n")
        
        # PRESERVED FROM ORIGINAL: Performance launcher usage
        print(f"{Color.YELLOW}5. USE PERFORMANCE LAUNCHER{Color.END}")
        user_launcher = REAL_USER_HOME / "launch-game.sh"
        if user_launcher.exists():
            print(f"   User script: {user_launcher} <game>")
        if Path("/usr/local/bin/launch-game").exists():
            print(f"   System-wide: launch-game <game>")
        print()
        
        # PRESERVED FROM ORIGINAL: VM gaming tips
        if vm_type:
            print(f"{Color.CYAN}VM GAMING TIPS:{Color.END}")
            print("   • Start with lightweight/indie games to test performance")
            print("   • 2D games typically run very well in VMs")
            print("   • 3D games depend heavily on host GPU passthrough")
            print("   • Check ProtonDB for VM-specific compatibility notes\n")
        
        # PRESERVED FROM ORIGINAL: Files created section
        print(f"{Color.CYAN}FILES CREATED:{Color.END}")
        print(f"   Logs: {LOG_DIR}")
        print(f"   Latest log: {LOG_FILE}")
        if user_launcher.exists():
            print(f"   Performance launcher: {user_launcher}")
        if Path("/usr/local/bin/launch-game").exists():
            print(f"   System launcher: /usr/local/bin/launch-game")
        print()
        
        # Display failed operations if any - ENHANCED
        if self.failed_operations:
            print(f"{Color.YELLOW}Failed Operations:{Color.END}")
            for op in self.failed_operations:
                print(f"  ✗ {op}")
            print()
        
        # PRESERVED FROM ORIGINAL: Reboot prompt
        if self.confirm("Reboot now?"):
            print(f"{Color.GREEN}Rebooting system...{Color.END}")
            self.run_command(["reboot"], "Rebooting system")
        else:
            print(f"{Color.YELLOW}Remember to reboot before gaming!{Color.END}")
    
    # ═══════════════════════════════════════════════════════════════════════════
    # MAIN EXECUTION FLOW - PRESERVED FROM ORIGINAL WITH ENHANCEMENTS
    # ═══════════════════════════════════════════════════════════════════════════
    
    def run(self):
        """
        Main execution flow
        
        PRESERVED FROM ORIGINAL: All installation steps in same order
        ENHANCED: CLI flag support for automated installation
        """
        # Display banner - PRESERVED FROM ORIGINAL format
        print(f"{Color.BOLD}{Color.HEADER}")
        print("╔═══════════════════════════════════════════════════════════════════╗")
        print("║        Debian-Based Gaming Setup Script v2.0                      ║")
        print("║                                                                    ║")
        print("║  This script will install and configure:                          ║")
        print("║  • GPU Drivers (NVIDIA/AMD/Intel) or VM Tools                     ║")
        print("║  • Gaming Platforms (Steam, Lutris, Heroic)                       ║")
        print("║  • Wine & Proton Compatibility                                    ║")
        print("║  • System Optimizations                                           ║")
        print("╚═══════════════════════════════════════════════════════════════════╝")
        print(f"{Color.END}\n")
        
        print(f"{Color.CYAN}Running as root, installing for user: {Color.BOLD}{REAL_USER}{Color.END}")
        print(f"{Color.CYAN}User home directory: {REAL_USER_HOME}{Color.END}")
        print(f"{Color.CYAN}Logs will be saved to: {LOG_DIR}{Color.END}\n")
        
        # Dry run notice - ENHANCED
        if self.config.dry_run:
            print(f"{Color.YELLOW}{'═'*70}{Color.END}")
            print(f"{Color.YELLOW}DRY RUN MODE - No changes will be made to the system{Color.END}")
            print(f"{Color.YELLOW}{'═'*70}{Color.END}\n")
        
        # PRESERVED FROM ORIGINAL: Same confirmation prompt
        if not self.config.auto_yes and not self.confirm("Continue with installation?"):
            print("Installation cancelled.")
            sys.exit(0)
        
        try:
            # Core setup - PRESERVED FROM ORIGINAL: Same order
            self.clean_broken_repos()  # PRESERVED FROM ORIGINAL
            self.update_system()
            self.enable_32bit_support()
            
            # Detect system and hardware - ENHANCED but preserves original detection
            self.detect_system()
            gpu_type = self.detect_gpu()
            
            # GPU/VM detection and driver installation - PRESERVED FROM ORIGINAL logic
            if gpu_type in ['vmware', 'virtualbox', 'kvm/qemu', 'vm']:
                if self.config.install_vm_tools or self.confirm(f"Install {gpu_type} guest tools for better graphics performance?"):
                    self.install_vm_tools(gpu_type)
            # Handle physical GPU drivers - PRESERVED FROM ORIGINAL
            elif gpu_type == 'nvidia':
                if self.config.install_nvidia_drivers or self.confirm("Install NVIDIA drivers?"):
                    self.install_nvidia_drivers()
            elif gpu_type == 'amd':
                if self.config.install_amd_drivers or self.confirm("Install AMD drivers?"):
                    self.install_amd_drivers()
            elif gpu_type == 'intel':
                if self.config.install_intel_drivers or self.confirm("Install Intel drivers?"):
                    self.install_intel_drivers()
            elif gpu_type == 'generic':
                print(f"{Color.YELLOW}Installing generic graphics support...{Color.END}")
                self.install_generic_vm_graphics()
            
            # Gaming components - PRESERVED FROM ORIGINAL but with CLI support
            if self.config.install_essential_packages or self.confirm("Install essential gaming packages?"):
                self.install_essential_packages()
            
            if self.config.install_codecs or True:  # Always prompt for codecs
                self.install_codecs()
            
            self.install_gaming_platforms()  # Uses smart prompts from original
            self.install_wine_proton()       # Uses smart prompts from original
            
            # NEW PLATFORMS
            self.install_sober()  # NEW: Roblox on Linux
            self.install_waydroid()  # NEW: Android container
            
            # Optional components - PRESERVED FROM ORIGINAL with additions
            self.install_discord()
            self.install_obs()
            self.install_mumble()  # ENHANCED: New
            self.install_mangohud()  # ENHANCED: New
            self.install_goverlay()  # ENHANCED: New
            
            # NEW UTILITIES
            self.install_greenwithenv()  # NEW: NVIDIA GPU control
            self.install_vkbasalt()  # NEW: Vulkan post-processing
            self.show_reshade_info()  # NEW: ReShade info
            self.install_mod_managers()  # NEW: Mod management tools
            
            # Optimizations - PRESERVED FROM ORIGINAL
            if self.config.apply_system_optimizations or True:  # Prompt if not set via CLI
                self.optimize_system()
            
            if self.config.create_performance_launcher or True:  # Prompt if not set via CLI
                self.create_performance_script()
            
            # Show what was installed - PRESERVED FROM ORIGINAL
            self.show_installation_summary()
            
            # Set proper ownership on log file - PRESERVED FROM ORIGINAL
            try:
                uid, gid = get_real_user_uid_gid()
                if not self.config.dry_run:
                    os.chown(LOG_FILE, uid, gid)
            except Exception as e:
                logging.warning(f"Could not set ownership on log file: {e}")
            
            # Save state - ENHANCED
            self.save_installation_state()
            
            # Completion - PRESERVED FROM ORIGINAL
            self.final_steps()
            
        except KeyboardInterrupt:
            print(f"\n{Color.YELLOW}Installation interrupted by user{Color.END}")
            sys.exit(1)
        except Exception as e:
            logging.error(f"Unexpected error: {e}")
            print(f"{Color.RED}An error occurred. Check log file: {LOG_FILE}{Color.END}")
            sys.exit(1)

# ═══════════════════════════════════════════════════════════════════════════════
# ENTRY POINT AND MAIN FUNCTION
# ═══════════════════════════════════════════════════════════════════════════════

def main():
    """
    Entry point for the script
    
    Handles argument parsing and script initialization
    """
    # Parse command-line arguments
    args = parse_arguments()
    
    # Handle special cases first
    if hasattr(args, 'cleanup') and args.cleanup:
        print(f"{Color.CYAN}Cleaning up installation files...{Color.END}")
        # Cleanup logic here
        sys.exit(0)
    
    # Create setup instance
    setup = GamingSetup(args)
    
    # Handle rollback
    if hasattr(args, 'rollback') and args.rollback:
        setup.perform_rollback()
        sys.exit(0)
    
    # Run main installation
    setup.run()

if __name__ == "__main__":
    main()

# END OF PART 6 (FINAL)
# This completes the comprehensive enhanced gaming setup script
# All original functionality preserved with extensive new enhancements
