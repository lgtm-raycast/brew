# Security policy

## Report a vulnerability

Use [private vulnerability reporting](https://github.com/lgtm-raycast/brew/security/advisories/new) (**Security →
Advisories → Report a vulnerability**). Include the affected downstream commit/release, macOS/Raycast versions,
reproduction steps and impact. Remove secrets from logs. Do not disclose exploit details in a public issue.

We maintain current main and the latest published downstream release. Older versions should update before requesting
support. Fixes are developed through protected PRs and coordinated with the reporter. We credit reporters who wish to be
named; response timing depends on maintainer availability.

## Downstream and upstream scope

Report vulnerabilities in this maintained edition here first. Link relevant upstream advisories where available; we
assess whether [Raycast Brew](https://github.com/raycast/extensions/tree/main/extensions/brew) or another dependency is
affected and coordinate any upstream report. Original authorship does not imply upstream support for this fork.

Dependencies are checked with OSV in CI; lintro checks code and secrets. Dependency alerts, private reporting and
available secret-scanning protections are enabled in repository settings. Renovate's shared configuration becomes
operational once its App is installed for this repository; configuration alone does not execute updates.

Follow the [organization security policy](https://github.com/lgtm-raycast/.github/blob/main/SECURITY.md) for shared
controls. All applicable checks and review threads must pass/resolve before merging. Users manage their own local
extension installations and updates.
