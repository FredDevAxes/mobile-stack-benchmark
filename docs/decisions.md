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
