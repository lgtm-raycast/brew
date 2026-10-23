/// <reference types="@raycast/api">

/* 🚧 🚧 🚧
 * This file is auto-generated from the extension's manifest.
 * Do not modify manually. Instead, update the `package.json` file.
 * 🚧 🚧 🚧 */

/* eslint-disable @typescript-eslint/ban-types */

type ExtensionPreferences = {
  /** Custom Brew Executable Path - Set this if your brew executable is in a non-standard location */
  "customBrewPath"?: string,
  /** Terminal Application - The terminal application/emulator to use when using any Run in Terminal action. */
  "terminalApp": "alacritty" | "ghostty" | "hyper" | "iterm" | "kitty" | "terminal" | "warp" | "wezterm",
  /** Upgrades - Include auto-updating casks when upgrading or checking for outdated items. */
  "greedyUpgrades": boolean,
  /** Uninstall - Run cask uninstall with the --zap option for a more complete uninstallation of files associated with cask.
WARNING: This may remove files shared with other applications. */
  "zapCask"?: boolean,
  /** Homebrew Options - Homebrew enables parallel downloads by default. Enable this option to disable concurrent downloads if you experience issues. */
  "disableDownloadConcurrency": boolean,
  /** Lists - Show pinned formulae and casks at the top of Show Installed and Show Upgrades, rather than at the bottom. Pinned packages are excluded from upgrades until you unpin them. */
  "pinnedFirst": boolean,
  /** Window Behavior - Close the Raycast window after performing actions like install, uninstall, or upgrade. */
  "closeAfterAction": boolean,
  /** Debug Logging - Show detailed logs in the console for debugging. */
  "verboseLogging": boolean
}

/** Preferences accessible in all the extension's commands */
declare type Preferences = ExtensionPreferences

declare namespace Preferences {
  /** Preferences accessible in the `installed` command */
  export type Installed = ExtensionPreferences & {}
  /** Preferences accessible in the `search` command */
  export type Search = ExtensionPreferences & {
  /** Search View - Display a metadata panel next to the search results list showing details for the selected package. */
  "showMetadataPanel": boolean
}
  /** Preferences accessible in the `outdated` command */
  export type Outdated = ExtensionPreferences & {}
  /** Preferences accessible in the `show-vulnerabilities` command */
  export type ShowVulnerabilities = ExtensionPreferences & {}
  /** Preferences accessible in the `run-doctor` command */
  export type RunDoctor = ExtensionPreferences & {}
  /** Preferences accessible in the `adopt-apps` command */
  export type AdoptApps = ExtensionPreferences & {}
  /** Preferences accessible in the `upgrade` command */
  export type Upgrade = ExtensionPreferences & {}
  /** Preferences accessible in the `manage-services` command */
  export type ManageServices = ExtensionPreferences & {}
  /** Preferences accessible in the `manage-taps` command */
  export type ManageTaps = ExtensionPreferences & {}
  /** Preferences accessible in the `services-menu` command */
  export type ServicesMenu = ExtensionPreferences & {}
  /** Preferences accessible in the `clean-up` command */
  export type CleanUp = ExtensionPreferences & {
  /** Clean up - Include --prune=all when cleaning files & packages from cache.
This option bypasses the 120 days threshold. */
  "withoutThreshold": boolean
}
  /** Preferences accessible in the `clear-cache` command */
  export type ClearCache = ExtensionPreferences & {}
}

declare namespace Arguments {
  /** Arguments passed to the `installed` command */
  export type Installed = {}
  /** Arguments passed to the `search` command */
  export type Search = {
  /** Query */
  "search": string
}
  /** Arguments passed to the `outdated` command */
  export type Outdated = {}
  /** Arguments passed to the `show-vulnerabilities` command */
  export type ShowVulnerabilities = {}
  /** Arguments passed to the `run-doctor` command */
  export type RunDoctor = {}
  /** Arguments passed to the `adopt-apps` command */
  export type AdoptApps = {}
  /** Arguments passed to the `upgrade` command */
  export type Upgrade = {}
  /** Arguments passed to the `manage-services` command */
  export type ManageServices = {}
  /** Arguments passed to the `manage-taps` command */
  export type ManageTaps = {
  /** user/repo */
  "tap": string
}
  /** Arguments passed to the `services-menu` command */
  export type ServicesMenu = {}
  /** Arguments passed to the `clean-up` command */
  export type CleanUp = {}
  /** Arguments passed to the `clear-cache` command */
  export type ClearCache = {}
}

