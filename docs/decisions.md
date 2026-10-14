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
