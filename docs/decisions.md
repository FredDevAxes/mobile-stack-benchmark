# Implementation decisions

The monorepo uses Python's standard library to orchestrate native tools. A Node
workspace runner would not build Swift, Gradle or Dart itself, so adding Turborepo
would introduce a second layer without removing platform-specific work.
The existing toolchain pilot is retained locally, excluded from Git: it contains
host-specific traces and different smoke applications, not benchmark results.

Each application uses its platform's lazy list and local key-value persistence.
Transitions use explicit rectangle interpolation instead of experimental shared
element APIs. React Native uses its built-in Animated API with the JavaScript
driver for layout properties; this choice and its limitations are part of the
experiment. Reanimated is not required by the contract and is not included.

Official references examined on 2026-10-14:
- [Flutter profiling](https://docs.flutter.dev/perf/ui-performance): simulated
  and Debug execution does not represent physical-device Release performance.
- [React Native Animated](https://reactnative.dev/docs/animated): native driver
  restrictions matter for an animation of width, height and position.
- [Compose animation specifications](https://developer.android.com/develop/ui/compose/animation/customize).
- [SwiftUI timing curves](https://developer.apple.com/documentation/swiftui/animation/timingcurve(_:_:_:_:duration:)).

Generated platform scaffolds are adapted from the local official Flutter and
React Native templates. Frameworks and dependencies retain their original
licenses; see THIRD_PARTY.md. No client assets or code are used.

## Dependency reproduction checks

Writing Gradle locks was insufficient on the reference toolchain: consuming the
new lock failed on the metadata-only `kotlin-stdlib-common` module. Compose now
omits that module from lock validation and forces its version to 2.2.10; all other
resolved modules remain locked. The build is verified without `--write-locks`.
See [Gradle's documented exclusion mechanism](https://docs.gradle.org/current/userguide/dependency_locking.html#sec:ignoring_dependencies).
The custom transition uses Compose animation-core, already required by the
foundation widgets; no animation-only full animation library is added to S.

The iOS deployment target is 18.0 in all three implementations. The AsyncStorage
resource pod's older target was rejected by Xcode 27, so the RN post-install hook
sets every pod target to 18.0. This does not claim backward compatibility with
older OS versions or physical-device execution.

## S/A source separation

Shared screens are maintained as canonical A source. The root build orchestration
projects S by removing source-rectangle measurement and image interpolation,
replacing the detail with fixed geometry, and selecting the instant navigation
module. Inspection controls are removed from production builds. These are source
projections, not runtime switches. The exact generated UI can be inspected with
`python3 scripts/export_sources.py S`; `scripts/source_mode.py` defines every
transformation and rejects missing source markers. Flutter S also excludes its
ticker mixin. Swift uses a separate prepared file; other native tools read a
serialized temporary projection, which is restored even when a build fails.
Always use root commands when reproducing the comparison.

## Artifact and verification corrections

Inspecting the entire Flutter APK showed that `--target-platform android-arm64`
limited the engine but retained foreign-ABI libraries from a persistence plugin.
The pinned Flutter plugin also overwrites default ABI filters. The root build
therefore produces/selects the complete arm64 split APK, and the collector rejects
any APK containing a foreign native ABI. Earlier multi-ABI smoke artifacts are
not size-comparison results.

The inspection-only motion label reads the actual framework flag, rather than a
forced app toggle. The UI verification runner changes only dedicated virtual-device
settings, verifies the instant branch, then restores normal animation. It does
not supply a common input timestamp or physical-device timing evidence.

SwiftUI measures the tapped card's rectangle directly. A clipped automation tap
can still hit the fixed catalogue header; the scroll flow taps the lower photo
region. Earlier scroll failures and an unexplained Flutter capture/scroll attempt
are retained in trial summaries; a retry passing is not proof of its original cause.


The scrolled-card flow now waits for animation settling and uses the detail's
unique description. A product title also exists in the list, so it was not a
sufficient assertion of navigation. The driver's stabilization and conditional
tap retry follow [Maestro's documented wait strategy](https://docs.maestro.dev/maestro-flows/flow-control-and-logic/wait-commands).
Only the current execution's screenshots are exported. Earlier unsuccessful
attempts remain in the trial record.

React Native's modal accessibility flag correctly hides background siblings in
production, but it also hid inspection controls placed beside the detail. The
inspection projection removes that flag; the catalogue stays hidden and normal
S/A keep the original modal behavior. This projection is excluded from size and
memory artifacts.

A generated `.xcode.env.local` referenced Node 25.6 while the protocol declared
24.13. The reference shell was also using 25.6. Those initial size records are
retained as [exploratory history](../results/history/node25-exploratory-builds.json).
Before the verified milestone, every artifact was rebuilt with Node 24.13 selected.
The root RN build validates the executable version and writes its path to the
ignored local Xcode environment; build records store the actual Node/Python
versions. All eight formatted production application projections remained
identical through these tooling corrections.

The final reduced-motion probe exposed a Flutter 3.47 distinction: iOS Reduce
Motion sets `AccessibilityFeatures.reduceMotion`, while Android Remove animations
sets `disableAnimations`. The app checks both engine flags and observes live
accessibility changes. The distinction is documented by [Flutter](https://api.flutter.dev/flutter/widgets/MediaQueryData/disableAnimations.html).
The verification runner restarts the dedicated simulator after changing its
setting, then the probe validates the actual engine flag after launch.

A SwiftUI reduced-motion attempt exposed an unchanged first card tap after
launch: the engine flag was reduced, but the catalogue remained visible. The
common probe now waits for a stable frame and retries only if the tap changes
nothing, following the same documented driver strategy as the scroll flow.
The failed attempt is retained; this does not establish its underlying cause.

On RN Android, UIAutomator returned the disabled catalogue's favorite node even
while the detail was visible (`important-for-accessibility=false`). A plain
label selector tapped its background coordinates, leaving the detail favorite
unchanged. The common F2 flow now anchors the favorite button below the unique
detail description, using [Maestro relational selectors](https://docs.maestro.dev/reference/selectors/relational-selectors).
This verifies the intended detail action without changing application code or
relabeling earlier successful flows. The unsuccessful attempt is retained.

The final timeline review exposed SwiftUI's implicit disabled-button dimming in
the background catalogue, before the programmed backdrop fade. The catalogue
now blocks hit testing while detail is active, retaining accessibility hiding
without changing image colors. This visual correction is rebuilt and verified
only for SwiftUI; Android diagnostics and the other app sources are unchanged.
