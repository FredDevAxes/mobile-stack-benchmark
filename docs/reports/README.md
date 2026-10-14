# Reports and use cases

[Project overview](../../README.md) · [Reproduction guide](../REPRODUCE.md)

This page indexes the published Mobile Stack Benchmark reports and the use cases
they examine. Each entry links to a verified milestone, its protocol and evidence.
There is currently one published report, covering virtual devices. No physical-device
campaign is included.

## Published reports

| Report | Use case | Environment and scope | Verified milestone |
| --- | --- | --- | --- |
| [Offline catalogue and image transition](https://github.com/FredDevAxes/mobile-stack-benchmark/blob/v0.1.0-virtual-devices/results/REPORT.md) | Search, persistent favorites and catalogue-to-detail navigation, with and without animation | Android emulator and iOS simulator: functionality, deterministic image geometry, Release package sizes, source counts and exploratory Android memory snapshots | [`v0.1.0-virtual-devices`](https://github.com/FredDevAxes/mobile-stack-benchmark/tree/v0.1.0-virtual-devices) |

The tagged report preserves the verified result. Its [working-tree copy](../../results/REPORT.md)
and the evidence links below also work when browsing a local clone. Earlier exploratory
build records are retained inside the report's history; they are not separate verified
comparative reports. The smoke-app pilot is excluded from this catalogue comparison.

## Use cases covered by the catalogue report

All four implementations use the same 200 fictional products and 20 original
illustrations. Flutter and React Native each cover Android and iOS; native coverage
uses Compose and SwiftUI respectively. S is instant navigation; A includes the
programmed 400 ms image transition.

| Use case | What the visitor can inspect | Evidence |
| --- | --- | --- |
| Search an offline catalogue | Apply a name query, show an empty result and restore the catalogue | [Functional checks](../../results/REPORT.md#functional-and-visual-verification), [F1 contract](../protocol.md#verification) |
| Keep favorites across a restart | Add and filter favorites, remove one from its detail and confirm local persistence | [Functional checks](../../results/REPORT.md#functional-and-visual-verification), [F2 contract](../protocol.md#verification) |
| Open a product and return to the list | Retain the scroll position; handle back and repeated input | [Functional checks](../../results/REPORT.md#functional-and-visual-verification), [scroll evidence](../../results/scroll.json) |
| Animate the product image into its detail | Compare five fixed stages, image bounds, rounded corners and centered crop | [Visual checks](../../results/REPORT.md#functional-and-visual-verification), [geometry evidence](../../results/geometry.json) |
| Honor reduced motion | Use instant navigation when the system requests reduced animations | [Per-target checks](../../results/REPORT.md#functional-and-visual-verification), [acceptance records](../../results/acceptance.json) |

The repeated-input driver does not prove the exact timing of a tap within the
400 ms transition. Scroll retention and reduced-motion checks are functional
verification, not scrolling performance or accessibility certification.

## Questions answered by the report

| Question | Available result | Boundary |
| --- | --- | --- |
| What does each app package, and what does animation add? | Release S/A sizes and A minus S, by platform | Android APK bytes and iOS unsigned device bundle bytes; not store downloads or installed size |
| How much application source is maintained? | Formatted S/A counts; shared code counted once, native code summed | Describes these implementations; not productivity, quality or maintenance cost |
| Do the apps implement the agreed experience? | 54 successful flows, 30 deterministic visual stages and 12 list-retention screenshot pairs | One reference virtual-device size per platform; image checks exclude text antialiasing and actual timing |
| What happened to Android process memory during repeated navigation? | Three before/after PSS snapshot pairs per stack and variant | Exploratory guest-process diagnostics; no physical-phone result, significance or leak conclusion |

Fluidity, input latency, usable startup time and physical-device memory remain
unmeasured or unavailable as a common comparison. The report's
[runtime diagnostics](../../results/REPORT.md#runtime-diagnostics) explain each gap.
Flutter runs in Debug on the tested iOS simulator; React Native and SwiftUI run in
Release, so there is no cross-stack iOS performance ranking.

## Read, watch or reproduce

- [Full report and limitations](../../results/REPORT.md)
- [Protocol and visual reference](../protocol.md)
- [Pinned setup, builds and checks](../REPRODUCE.md)
- [Android demonstration](../../results/visuals/android/comparison.mp4) and [iOS demonstration](../../results/visuals/ios/comparison.mp4)
- [Build identities](../../results/builds.json), [source counts](../../results/code.json), [environment](../../results/environment.json) and [retained attempts](../../results/trials.json)

Demonstration videos have unsynchronized gestures and are not timing experiments.
The original code and artwork use the [MIT license](../../LICENSE); retain the
[third-party licenses and credits](../../THIRD_PARTY.md).

Additional published reports should receive their own index entry, identifying the
use case, environment, protocol, verified revision and limitations. Keep existing
tagged reports available so results from different campaigns remain distinguishable.
