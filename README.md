# Mobile Stack Benchmark

The same hiking catalogue, built with Flutter, React Native, Jetpack Compose and
SwiftUI. Each implementation has an instant version (**S**) and an animated
version (**A**), so you can inspect what the transition adds to the code and build.

The apps search 200 fictional products, save favorites locally and open a product
from a scrolling list. A moves its image into the detail screen over a programmed
400 ms, then returns to the same card. Twenty original illustrations are shared
by all apps. Everything works offline.

This milestone covers **four implementations and six virtual-device targets**.
The [results](results/REPORT.md) include within-platform S/A build sizes,
formatted-source counts, functional checks, five-stage image geometry checks,
demonstrations and explicitly limited runtime diagnostics.
Use tag **`v0.1.0-virtual-devices`** to retrieve this evidence and its source.

In this catalogue, A adds 54 maintained application lines in Flutter, 48 in
React Native and 105 across Compose and SwiftUI together. The measured A−S
package change ranges from 0 to 15,560 bytes. The [tables and method](results/REPORT.md)
show what those counts include; they do not measure development time or runtime speed.

![Five stages of the Android transition](results/figures/android-timeline.png)

[Android three-app video](results/visuals/android/comparison.mp4) ·
[iOS three-app video](results/visuals/ios/comparison.mp4) ·
[All results and limitations](results/REPORT.md)

Videos illustrate behavior; panels start at recording time and gestures are not
synchronized. They do not establish a performance ranking. Flutter's tested iOS
simulator supports Debug only, so its runtime diagnostics are not ranked against
React Native or SwiftUI Release. iOS size comparisons use separately compiled
unsigned **device** Release bundles. No physical phone or store download is measured.

## Start here

The complete workflow needs a Mac with Xcode and Android tools. Android-only
builds can run on Linux. No backend or secret is required. Follow the
[step-by-step reproduction guide](docs/REPRODUCE.md) for exact versions,
installation, building, running the apps and collecting evidence.

Once its setup steps are complete, these root commands run all four projects:

```sh
python3 scripts/check_assets.py
python3 scripts/lab.py lint
python3 scripts/lab.py test
python3 scripts/build_matrix.py
```

Build just one variant and target with:

```sh
python3 scripts/lab.py build --stack compose --platform android --variant A
```

S physically excludes the custom animation timer, coordinate measurement and
interpolation. Production builds also exclude inspection controls. Always use
root commands when comparing sizes; [source projection](docs/decisions.md#sa-source-separation)
is part of the build. Archives are separated under `.work/artifacts/`.

## Applications and evidence

| Project | Targets | App guide |
| --- | --- | --- |
| Flutter / Dart | Android and iOS | [Flutter](apps/flutter/README.md) |
| React Native / TypeScript, Hermes, Fabric | Android and iOS | [React Native](apps/react-native/README.md) |
| Kotlin / Jetpack Compose | Android | [Compose](apps/compose/README.md) |
| Swift / SwiftUI | iOS | [SwiftUI](apps/swift/README.md) |

This is a monorepo because all apps implement one contract. A small Python runner
coordinates each ecosystem's own tools; it does not replace Gradle, Flutter,
Node or Swift. `shared/` holds canonical data/artwork, `verification/` the common
UI flows, `scripts/` the orchestration/collectors, and `results/` retained evidence.
The unrelated smoke-app pilot stays local and is excluded from the comparison.

- [Protocol and visual reference](docs/protocol.md)
- [Implementation and dependency decisions](docs/decisions.md)
- [Pinned toolchain](toolchain.json)
- [Build/source identities](results/builds.json), [code manifest](results/code.json),
  [environment](results/environment.json), [source equivalence](results/source-equivalence.json),
  [retained driver attempts](results/trials.json)
- [CI workflow](.github/workflows/checks.yml) and [actual runs](https://github.com/FredDevAxes/mobile-stack-benchmark/actions)

## Checks and scope

Dart format/analyze, ESLint/TypeScript/Prettier, ktlint/Android lint,
swift-format and Ruff cover the maintained projects/tooling. Unit suites verify
data, filtering and favorite logic; local Maestro flows verify installed S/A
apps, scroll state, persistence, back and reduced-motion handling. CI runs
linters, tests, secret scanning and supported compilation on every push and PR.
Earlier CI/driver failures remain part of the history; the milestone records the
successful checks instead of claiming every historical attempt passed.

Build size and line counts describe this small implementation. They do not measure
code quality, delivery cost or every stack's performance. The current locked RN
tooling tree still has inherited audit advisories; details and practical limits
are in the [report](results/REPORT.md#limits-and-dependencies). This is an
inspectable lab, not a production security or accessibility certification.

All original code and artwork across the monorepo use the [MIT license](LICENSE).
Frameworks, dependencies and adapted templates retain their
[third-party licenses and credits](THIRD_PARTY.md).
