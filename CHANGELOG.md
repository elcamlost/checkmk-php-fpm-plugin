# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).

## [Unreleased]

## [2.3.1] - 2026-04-12

### Fixed
- Pools listening on TCP sockets (`host:port`) are now discovered and monitored ([#44](https://github.com/elcamlost/checkmk-php-fpm-plugin/pull/44))

## [2.3.0] - 2026-03-29

### Added
- New metrics `memory_total_rss` and `memory_avg_rss` added. ([#40](https://github.com/elcamlost/checkmk-php-fpm-plugin/pull/40))

## [2.2.0] - 2026-03-29

### Added
- Support `pm.status_listen` socket (PHP-FPM 8.1+) for status requests ([#36](https://github.com/elcamlost/checkmk-php-fpm-plugin/pull/36))
- Disambiguate pools with duplicate names across multiple PHP-FPM instances ([#37](https://github.com/elcamlost/checkmk-php-fpm-plugin/pull/37))

### Fixed
- Config files and process paths containing non-ASCII characters no longer crash the agent plugin ([#34](https://github.com/elcamlost/checkmk-php-fpm-plugin/pull/34))

## [2.1.0] - 2026-03-29

### Changed
- Migrate to new plugin API (`cmk.agent_based.v2`, `cmk.rulesets.v1`, `cmk.graphing.v1`) — compatible with Checkmk 2.3+
- Replace Docker-based packaging with `package.py` script

### Added
- Graphing definitions for all metrics
- Unit tests
- CI workflow

### Fixed
- `accepted_conn_per_sec` levels now correctly applied (key mismatch with ruleset fixed)
- `version.min_required` set to `2.3.0p1`

## [2.0.0] - 2025-05-15

### Changed
- Migrate to Checkmk 2.0 plugin API (thanks @moschlar)

### Added
- Configurable levels (thanks @moschlar)

## [1.0.0] - 2022-03-04

### Added
- Autodiscovery support

### Fixed
- Checkmk 2.x compatibility

## [0.2.0] - 2020-05-02

### Added
- TCP socket support (thanks @simon-mueller)

### Fixed
- Man page

## [0.1.0] - 2020-03-18

### Added
- Initial release with Unix socket support
