# Security Policy

## Supported Versions

| Version | Supported          | Security Updates |
| ------- | ------------------ | ---------------- |
| 2.1.x   | :white_check_mark: | Yes              |
| 2.0.x   | :white_check_mark: | Yes              |
| 1.x.x   | :x:                | No (Legacy)      |

**Current Stable Version:** 2.1.0

---

## Reporting a Vulnerability

We take security seriously. If you discover a security vulnerability, please report it responsibly.

### 📝 What to Include

Please provide:
1. **Description** of the vulnerability
2. **Steps to reproduce** the issue
3. **Potential impact** assessment
4. **Suggested fix** (if known)
5. **Your contact information** (for follow-up)

### 🔒 Responsible Disclosure

- **Do not** publicly disclose the vulnerability until we've addressed it
- We'll work with you to understand and resolve the issue
- We'll credit you in the security advisory (unless you prefer anonymity)
- We aim to provide a fix within 30 days

---

## Security Considerations

### ⚠️ Script Requires Root Access

This script requires `sudo` privileges to:
- Install system packages
- Modify system configurations
- Install GPU drivers
- Configure kernel parameters

**We recommend:**
- Review the script before running
- Use `--dry-run` mode first
- Check logs for suspicious activity

### 🔍 What the Script Accesses

**File System:**
- `/etc/apt/` - Repository configuration
- `/etc/sysctl.d/` - Kernel parameters
- `/etc/sudoers.d/` - CPU governor permissions
- `~/.config/` - User configurations
- `~/.steam/` - Steam installation

**Network Access:**
- Package repositories (APT)
- Flathub (for Flatpak apps)
- GitHub API (for GE-Proton)
- WineHQ repository
- Official distribution repositories

**No External Data Collection:**
- Script does not phone home
- No analytics or tracking
- No personal data transmitted
- All operations are local

### 🛡️ Security Features

**Built-in Protections:**
- ✅ No arbitrary code execution from user input
- ✅ Validates package sources before installation
- ✅ Creates backups before modifications
- ✅ Comprehensive logging of all operations
- ✅ Sudo timeout for sensitive operations
- ✅ Validates sudoers file syntax before applying

**Verification:**
- Package signatures verified by APT
- Flatpak apps verified by Flathub
- GitHub releases verified via HTTPS

---

## Known Security Limitations

### 1. Third-Party Repositories

The script adds the following repositories:
- **WineHQ** - wine.org official repository
- **OBS Studio PPA** - Launchpad PPA
- **Waydroid** - waydro.id official repository

**Risk:** Compromised repositories could serve malicious packages  
**Mitigation:** Only uses official, well-known repositories

### 2. Flatpak Applications

Flatpak apps run in sandboxes but may request permissions:
- File system access
- Network access
- Device access (GPU, audio)

**Risk:** Malicious Flatpak app could abuse permissions  
**Mitigation:** Only installs from Flathub (verified apps)

### 3. GitHub Downloads

GE-Proton is downloaded from GitHub releases.

**Risk:** Man-in-the-middle attack or compromised GitHub account  
**Mitigation:** Downloaded via HTTPS, GitHub's security measures

### 4. Sudo Configuration

Script can configure passwordless sudo for CPU frequency control.

**Risk:** Could be abused if user account is compromised  
**Mitigation:** 
- Only allows specific commands (`cpupower`, `cpufreq-set`)
- Validates sudoers syntax before applying
- User is prompted for confirmation

---

## Best Practices for Users

### Before Running

1. ✅ **Review the script** - Read the code to understand what it does
2. ✅ **Use dry-run mode** - Test with `--dry-run` flag first
3. ✅ **Backup your data** - Create system backup before major changes
4. ✅ **Check source** - Download from official repository only
5. ✅ **Verify integrity** - Check file hash if provided

### During Installation

1. ✅ **Monitor output** - Watch for unexpected behavior
2. ✅ **Check logs** - Review `~/gaming_setup_logs/` for issues
3. ✅ **Don't interrupt** - Let the script complete to avoid partial installs

### After Installation

1. ✅ **Review logs** - Check for warnings or errors
2. ✅ **Verify packages** - Confirm installed packages are legitimate
3. ✅ **Test in isolation** - Try one feature at a time initially
4. ✅ **Report issues** - Notify us of any suspicious behavior

---

## Security Update Policy

### Critical Security Issues
- **Response Time:** 24-48 hours
- **Fix Timeline:** Emergency patch within 7 days
- **Notification:** GitHub Security Advisory + email to users

### High Priority Issues
- **Response Time:** 48-72 hours
- **Fix Timeline:** Patch in next minor release (2-4 weeks)
- **Notification:** GitHub Security Advisory

### Medium/Low Priority Issues
- **Response Time:** 1 week
- **Fix Timeline:** Next regular release
- **Notification:** Mentioned in CHANGELOG.md

---

## Secure Usage Guidelines

### Recommended Practices

**✅ DO:**
- Download from official repository only
- Verify script before running
- Use `--dry-run` to test
- Keep your system updated
- Review logs regularly
- Report suspicious behavior

**❌ DON'T:**
- Run scripts from untrusted sources
- Skip system updates
- Ignore warning messages
- Run as root unnecessarily (use sudo)
- Disable security features

### Environment-Specific Considerations

**Production Systems:**
- Test on non-production system first
- Use `--dry-run` mode
- Schedule during maintenance windows
- Have rollback plan ready

**Development Systems:**
- Still use caution with root access
- Review logs for unexpected behavior
- Keep backups of important projects

**Virtual Machines:**
- Snapshot before running
- Test in isolated VM first
- Verify network restrictions work

---

## Dependency Security

### Package Sources

All packages come from trusted sources:
- **Ubuntu/Debian repositories** - Official, signed packages
- **Launchpad PPAs** - Community repositories (verified)
- **Flathub** - Verified Flatpak applications
- **GitHub Releases** - HTTPS, official project accounts

### Known Vulnerabilities

We monitor:
- Ubuntu Security Notices
- Debian Security Advisories
- CVE databases
- GitHub Security Advisories

**Found vulnerability in dependency?** Report it to us and the upstream project.

---

## Incident Response

### If You Suspect Compromise

1. **Stop the script** immediately (Ctrl+C)
2. **Disconnect from network** (if actively compromised)
3. **Preserve evidence** - Don't delete logs
4. **Review logs** - Check `~/gaming_setup_logs/`
5. **Report to us**
6. **System scan** - Run antivirus/malware scan
7. **Change passwords** - If credentials may be compromised

### What We'll Do

1. **Acknowledge** report within 48 hours
2. **Investigate** the issue thoroughly
3. **Develop fix** if vulnerability confirmed
4. **Release patch** as soon as possible
5. **Publish advisory** with details and mitigation
6. **Credit reporter** (unless anonymous preferred)

---

## Security Audit

### Self-Audit Checklist

You can verify security by checking:

- [ ] Script source code is readable
- [ ] No obfuscated code
- [ ] No network calls except to known repositories
- [ ] No data exfiltration
- [ ] Proper error handling
- [ ] Input validation present
- [ ] Sudo usage is minimal and specific
- [ ] Backups created before changes
- [ ] Comprehensive logging enabled

### Professional Audit

We welcome security researchers to:
- Review the code
- Perform penetration testing
- Suggest improvements
- Report findings responsibly

---

## Legal

### Responsible Disclosure

We follow responsible disclosure practices:
- We won't take legal action against researchers acting in good faith
- We'll work with you to understand and fix issues
- We'll credit you appropriately in security advisories

### Scope

**In Scope:**
- Security vulnerabilities in script code
- Privilege escalation issues
- Code injection possibilities
- Authentication/authorization bypasses
- Data exposure issues

**Out of Scope:**
- Vulnerabilities in dependencies (report to upstream)
- Social engineering attacks
- Physical security issues
- Denial of service (local script)

---

## Contact

**General Issues:** [Issues](https://github.com/Sandler73/Debian-Gaming-Setup-Project/issues)

**GPG Key:** Available on request  

**Response Times:**
- Critical: 24 hours
- High: 48 hours
- Medium: 1 week

---

## Updates

This security policy is reviewed quarterly and updated as needed.

**Last Updated:** January 2026  
**Next Review:** April 2026  
**Version:** 2.1.0

---

**Thank you for helping keep this project secure! 🔒**
