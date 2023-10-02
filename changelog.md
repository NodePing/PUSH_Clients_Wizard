# Changelog

All notable changes to this project will be documented in this file.

## [2023-10-02]

* PyInquirer stopped working with newer versions of Python, switch to InquirerPy
* Ensure Wizard works with change to POSIX PUSH client
* Some small bug fixes

## [2020-06-27]

### Added

Powershell and POSIX can setup:
- net_utilization
- cpu_utilization
- disk_utilization
- ram_utilization

## [2020-01-13]

### Added
- POSIX client can be set up with the memavail module

## [2019-12-19]

### Added
- httpcheck creation support
- smartctl creation support for POSIX
- zpool creation support for POSIX

### Changed
- Cleaned up the code to make it easier to manage
