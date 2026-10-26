# SideLinker Homebrew Tap

Official Homebrew Cask tap for **SideLinker Mac**.

> **Status: preparation only.** [SideLinker-Home Releases](https://github.com/wberry9813/SideLinker-Home/releases) already contains official SideLinker Mac DMGs (latest verified listing: `v1.0.5`, `SideLinker-Mac-1.0.5-23.dmg`). An installable `Casks/sidelinker.rb` has **not yet been activated**: the DMG's installed app path, signature/notarization and install/upgrade behavior still need release-operator verification. The separate legacy `SideLinker` repo is not the release source.

## Planned install and upgrade commands

After release-operator validation of an existing SideLinker-Home Mac DMG and activation of the cask:

```sh
brew tap wberry9813/sidelinker
brew install --cask sidelinker
```

```sh
brew update
brew upgrade --cask sidelinker
```

Uninstall:

```sh
brew uninstall --cask sidelinker
```

The cask installs the **same notarized SideLinker Mac.app** offered through direct download. Homebrew is only an optional distribution channel; Free/Pro access is determined by SideLinker, not by Homebrew.

## Maintainer release workflow

1. In private `SideLinker-Source`, prepare and test the macOS release. The current `scripts/notarize.sh --scheme "SideLinker Mac"` workflow already produces signed/notarized `SideLinker-Mac-VERSION-BUILD.dmg` plus a `.sha256` file. Verify the DMG actually contains `SideLinker Mac.app`, the signature and notarization, and the embedded Direct helper and permissions before shipping.
2. Use the *public* [SideLinker-Home Releases](https://github.com/wberry9813/SideLinker-Home/releases) as the single release source, with tag `vVERSION` (for example the existing `v1.0.5`). Publish **the exact validated DMG bytes** there when preparing future versions. Do not use assets from `wberry9813/SideLinker` (legacy SidecarLauncher), the private source repository, mutable branch URLs, or the pre-staple upload ZIP.
3. Check the release asset is publicly downloadable and matches the local DMG's SHA-256. Then in this repository run:
   ```sh
   python3 scripts/render-cask.py \
     --version VERSION \
     --url "https://github.com/wberry9813/SideLinker-Home/releases/download/vVERSION/SideLinker-Mac-VERSION-BUILD.dmg" \
     --dmg "/absolute/path/to/SideLinker-Mac-VERSION-BUILD.dmg"
   ```
   The script validates the URL/tag/filename and computes SHA-256 from the file. It will create `Casks/sidelinker.rb` only when explicitly run. No placeholder value is ever published in the active Casks directory.
4. Review the generated cask; run `ruby -c Casks/sidelinker.rb`, `brew style --cask sidelinker`, `brew audit --cask --strict sidelinker` as applicable, then test installation, `brew upgrade --cask sidelinker`, and uninstall in a safe test environment **without an active SideLinker session**. Verify the installed bundle ID, signature, helper identity, permissions, and no surprise user-data deletion.
5. Commit and push the cask update only after the above release/installation checks pass. Keep release assets immutable: a changed DMG requires a new release/version and new hash.

## Scope and safety

- This tap installs a prebuilt macOS `.app` **via Cask**, not a CLI Formula and not a build from source.
- Homebrew does **not** manage SideLinker's Direct Engine, launchd registrations, TCC permissions, login items or connected display sessions. Those remain application responsibilities.
- The Cask intentionally has no `zap` stanza or destructive postflight hooks. Uninstalling the app does not imply deleting pairing data, application preferences, purchases or service registrations.
- Only the `SideLinker Mac` (non-Free DMG) product is planned here. `SideLinker-Home` also publishes a separate `SideLinker-Mac-Free-*.dmg`, which this cask intentionally does not install. The legacy `wberry9813/SideLinker` repository must never be used as this tap's download source.
- If the macOS application update flow or app name changes, re-check Cask behavior before releasing.

See [the template](templates/sidelinker.rb.in) and [renderer](scripts/render-cask.py).
