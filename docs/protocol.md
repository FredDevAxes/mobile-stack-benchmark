# Catalogue experiment — protocol 0.1

Four implementations, six targets: Flutter and React Native on Android/iOS,
Compose on Android and SwiftUI on iOS. Compare within each platform only.
200 ordered fictional products share 20 original 640 × 400 RGB PNG illustrations.
No network, random runtime data, authentication or checkout.

## Functional contract

A lazy single-column list shows image, name, category, EUR price and favorite.
Search applies a case-insensitive name substring only after pressing Search.
Favorites only combines with search. Clear filters restores all 200 products.
Favorites persist as IDs; search and scroll reset on process restart. Opening a
favorite and removing it while filtered returns with a fade if its source has
disappeared. Card favorite taps never navigate. List state survives detail visits.
Back handles Android system navigation. Repeated taps during a transition are
ignored; one back received during opening is queued. Reduced motion is instant.

## Visual reference

Portrait, light theme, system font, white background. Content area excludes system
safe insets. Catalogue toolbar: 52 logical units; search: 44; filter row: 40.
List starts at y=136. Card margin 16; image width = content width − 32, height 180,
radius 16; text area 72; card spacing 16. Detail image starts at y=52, full width,
height 280, radius 0. Text margin 16. Card labels: title 18, category/price 14;
detail title 24, body 16. Native text rasterization may differ.

A moves the visible decoded image between these rectangles over 400 ms using
cubic Bézier (0.4, 0, 0.2, 1), centered cover crop, without distortion. Background
opacity follows progress; detail text fades from 35% to 100% of elapsed time.
Reverse follows the same geometry. Deterministic progress captures at 0, 25, 50,
75 and 100% are instrumentation, excluded from diagnostics. Geometry tolerance:
2 logical units, without requiring identical text antialiasing.
S physically excludes custom animation code at build preparation time.

## Verification

F1: known search, empty result, clear. F2: add favorite, filter, open, remove,
return, relaunch, confirm persistence. F3: open/close, repeated taps and system
back. V1: first card open and return, unchanged favorite state. Verify reduced
motion separately. Record failures as observations, never silently exclude them.

## Measurements

Release arm64-only APK bytes, separately from AAB bytes. Unsigned device arm64
Release .app logical file bytes, separately from simulator bundles and IPA.
Record shrinking, stripping, signing, architecture and dependency settings.
S/A totals and A−S are build-specific, not an intrinsic engine weight.
Count formatted code using cloc 2.10, excluding generated copies, dependencies,
resources and build output; separate UI, logic, platform, tests, instrumentation
and configuration. Shared mobile code is counted once, native code separately.
LOC does not measure quality or productivity.

Virtual devices validate behavior and visual equivalence. Flutter iOS simulator
is Debug-only in the tested SDK. No cross-stack iOS performance ranking is valid.
Diagnostics require proven render coverage and a common metric. If unavailable,
record the reason. V1 diagnostic plan: first transition separately, then 5 warmup
cycles, 30 recorded cycles, 3 series per target/variant; 1 second rest in stable
states, rotate stack order, no recording during measurement. Do not publish
programmed duration as measured speed. D1 scrolling and D2 process launch remain
secondary and require an explicitly validated protocol before measurement.
