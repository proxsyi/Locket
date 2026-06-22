# Changelog

All notable changes to this project are documented here. Versioning follows SemVer.

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
