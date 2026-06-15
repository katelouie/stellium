# Security Policy

## Supported Versions

| Version | Supported |
| ------- | --------- |
| 0.18.x  | Yes       |
| < 0.18  | No        |

## Reporting a Vulnerability

If you discover a security vulnerability in Stellium, please report it!

**Do not open a public GitHub issue for security vulnerabilities.**

Instead, please email **katelouie** (via [GitHub profile](https://github.com/katelouie)) or preferably use [GitHub's private vulnerability reporting](https://github.com/katelouie/stellium/security/advisories/new).

You can expect:

- An acknowledgment within 48 hours
- A fix timeline within 1 week for confirmed vulnerabilities
- Credit in the changelog (unless you prefer anonymity)

## Scope

Security concerns for Stellium primarily involve:

- File path handling (ephemeris paths, SVG output, PDF generation)
- Dependency vulnerabilities (`pyswisseph`, `typst`, etc.)
- Arbitrary code execution risks in any user-facing input paths
