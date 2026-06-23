# Changelog

All notable changes to this project are documented here. Versioning follows SemVer.

## v0.2.4 - 2026-06-23
### Added
- Added `docs/STATUS.md` with current shipped state, runtime behavior, verified installs, known bugs, and next planned work

### Changed
- README and architecture docs now point to the current status document and accurately call out that instant-login rotation still needs verification on Lauren's Mac

## v0.2.3 - 2026-06-23
### Added
- Login LaunchAgent now checks for updates first, then rotates and writes the lock-screen note immediately
- Installer cleans up known legacy lock-screen LaunchAgents and files from earlier private builds

### Fixed
- Deploy helper now uses an interactive SSH session so the remote sudo password prompt works during install

## v0.2.0 - 2026-06-23
### Added
- Login-triggered rotation picks a different note whenever the login LaunchAgent runs
- Separate 60-second sync agent keeps manual Live changes flowing without rotating every minute
- Hourly self-updater checks public GitHub tags, downloads newer versions, and reinstalls while preserving local config

## v0.1.4 - 2026-06-22
### Fixed
- LaunchAgent now refreshes every 60 seconds; the installer was still shipping the old 1800 second interval

## v0.1.3 - 2026-06-22
### Added
- Agent enforces a single live note every run: unchecks extras (newest edit wins) and auto-checks the least recently shown note when none are live

## v0.1.2 - 2026-06-22
### Fixed
- Bootstrap packager now resolves the agent source at the repo root instead of inside bootstrap

## v0.1.1 - 2026-06-22
### Changed
- Lowered the lock screen refresh interval from 30 minutes to 1 minute

## v0.1.0 - 2026-06-22
### Added
- Notion-backed lock screen note delivery (one shared database, Live checkbox picks the active note)
- Bootstrap startup package that verifies the Notion token plus database id and builds the partner package
- macOS partner agent installed as a LaunchAgent at login with a 30 minute refresh interval
- Scoped single-command sudoers rule for writing the login window text
- Setup guide, architecture doc, and uninstall script
