# Local release process

- Goal: publish the approved 1.0.0/build 3 release and register the matching local app.
- Scope: existing pagination changes, version metadata, release notes, GitHub PR/tag/release, and `/Applications/Notion2PDF.app`.
- Completion: merged main, matching remote tag and published release, removed work branch, installed version and LaunchServices registration confirmed.
- Exclusions: private document uploads, standalone packaging, signing/notarization, new external Notion tests, and interactive GUI tests.
- Verification: local Python/shell/plist checks, existing document evidence and unchanged renderer output, build/version checks, remote Git post-read, and installed app metadata.

`dist/Notion2PDF.app/Contents/Info.plist` is the version authority. Update `CFBundleShortVersionString` and increment `CFBundleVersion`; record changes and limits under `docs/releases/`. Build and inspect the scoped diff before committing. Publish a work-branch PR, merge only with user authorization, and tag the exact merged commit. Publish release notes with the matching tag; do not upload ignored output/tmp or private inputs. Remove only the merged work branch and prune stale remote-tracking references.

Run `zsh scripts/install_macos_app.sh` from the merged checkout. The installer preserves the previous local bundle, copies the repository bundle, records its project root in the installed plist, and registers it with LaunchServices. This local launcher depends on the checkout and its `.venv`; it is not a self-contained binary. Check `--version`, the root setting, launcher/icon equality, and the LaunchServices entry. Version probing does not launch GUI or contact Notion. A new interactive conversion is a separate verification step.
