# Reproduce the lab

Run commands from the repository root unless a working directory is shown.
Use a disposable clone for experiments: build preparation temporarily projects
shared screen sources, serializes access with a local lock, then restores them.
Do not edit an app while a root command is active. Archives for S and A are kept
separately, so one build never serves as both measured variants.

## 1. Prerequisites

The full six-target workflow needs macOS, Xcode 27.0 and its iOS 26.5 simulator
runtime, Android SDK command-line tools and the API 35 arm64 emulator image.
The reference host is an M1 Pro Mac with 16 GiB RAM and macOS 26.6.2.
Linux can build/test Android and JS/Dart logic; iOS requires Xcode on macOS.
Hosted CI uses macOS 26/Ubuntu 24.04 and records its actual SDK output.

Install the versions in [toolchain.json](../toolchain.json): Node 24.13.0,
Python 3.12.9, JDK 17.0.11, Ruby 3.3.6, Bundler 2.6.2, CocoaPods 1.16.2,
Flutter 3.47.7/Dart 3.13.5, cloc 2.10 and gitleaks 8.30.1. Use your usual
version manager or the official distributions. The reference Flutter Android
build selected Android Studio's JDK 25.0.3; CI also compiles it with JDK 17.
This difference is recorded, not used to combine CI sizes with local sizes.
FFmpeg is required only for composing demonstration videos. No account, API key,
backend, paid service or store signing credential is needed to run the apps.

Configure this terminal only, adapting the two installation paths:

```sh
export ANDROID_HOME="$HOME/Library/Android/sdk"
export JAVA_HOME="/path/to/jdk-17.0.11/Contents/Home"
export PATH="$JAVA_HOME/bin:$ANDROID_HOME/platform-tools:$ANDROID_HOME/emulator:$ANDROID_HOME/cmdline-tools/latest/bin:$PATH"
export MAESTRO_CLI_NO_ANALYTICS=1
export MAESTRO_CLI_ANALYSIS_NOTIFICATION_DISABLED=true
```

Select Ruby 3.3.6 and Node 24.13.0 in this terminal. Confirm `ruby --version`,
`node --version`, `java -version`, `xcodebuild -version` and `python3 --version`.
If several Ruby installations exist, put the selected installation's `bin`
directory on PATH; setting a version variable without its manager's shim does
not switch the executable. Keep developer keys/certificates outside Git.

## 2. Clone and install locked dependencies

```sh
git clone https://github.com/FredDevAxes/mobile-stack-benchmark.git
cd mobile-stack-benchmark
git checkout v0.1.0-virtual-devices
python3 -m venv .work/venv
.work/venv/bin/pip install -r requirements.lock
export PATH="$PWD/.work/venv/bin:$PATH"
mkdir -p .local
git clone --depth 1 --branch 3.47.7 https://github.com/flutter/flutter.git .local/flutter
test "$(git -C .local/flutter rev-parse HEAD)" = abaf9c523780a608bd46686fd5e53740a07077f8
export PATH="$PWD/.local/flutter/bin:$PATH"
flutter --version
python3 scripts/setup_tools.py
python3 scripts/check_assets.py
python3 scripts/prepare.py A
```

`setup_tools.py` verifies the checked-in hashes for ktlint and Maestro before
extracting them. Maestro uses local virtual-device tooling and may initialize
its user cache on first launch. No Maestro cloud upload or AI analysis is used.

Install Android packages, accepting their vendor licenses after reviewing them:

```sh
sdkmanager 'platform-tools' 'emulator' 'platforms;android-36' 'build-tools;36.0.0' 'ndk;27.1.12297006' 'ndk;28.2.13676358' 'system-images;android-35;google_apis_playstore;arm64-v8a'
```

For Flutter and React Native:

```sh
cd apps/flutter
flutter pub get --enforce-lockfile
cd ../react-native
npm ci
bundle _2.6.2_ install
cd ios
bundle _2.6.2_ exec pod install --deployment
cd ../../..
```

Run pod installation **from the iOS directory**: autolinking depends on that
working directory. Android-only reproduction can omit Ruby/pod installation.
Compose and SwiftUI do not require npm. Gradle wrappers verify their distribution
hashes and consume committed dependency locks for Compose/RN; Swift's core
package has no external packages. Flutter pub dependencies and its SDK/plugin
sources are pinned; native plugin dependencies also follow their Gradle declarations.
Reproduction does not promise byte-identical archives or permanently fixed hosted
runner images. See [decisions](decisions.md) for lock exceptions and deployment targets.

## 3. Checks

On a host with all four toolchains:

```sh
ruff check scripts
ruff format --check scripts
python3 scripts/check_assets.py
python3 scripts/lab.py lint
python3 scripts/lab.py test
gitleaks git --redact --no-banner
```

`lab.py lint` runs Dart format/analyze, ESLint/TypeScript/Prettier,
ktlint/Android lint, and strict swift-format. `lab.py test` runs Flutter tests,
Jest, both Compose flavor unit suites and Swift core XCTest. These tests check
fixed data, filtering/order and favorites logic; they are not UI coverage by
themselves. Native SDK compilation covers the retained platform scaffolds.
Python uses Ruff. Use `--stack flutter`, `--stack react-native`, `--stack compose`
or `--stack swift` to run one project. `.github/workflows/checks.yml` runs lint,
tests, secret scanning and supported S/A compilation on pushes and PRs.
Virtual-device flows run locally; CI does not claim physical-device or UI timing coverage.

## 4. Build S and A

```sh
python3 scripts/build_matrix.py
```

This builds 18 serial outputs: 12 comparable device artifacts plus six simulator
apps. It takes time; keep the host plugged in and avoid competing builds. To
build one target instead:

```sh
python3 scripts/lab.py build --stack compose --platform android --variant S
python3 scripts/lab.py build --stack compose --platform android --variant A
python3 scripts/lab.py build --stack flutter --platform simulator --variant A
python3 scripts/lab.py build --stack react-native --platform device --variant S
python3 scripts/lab.py build --stack swift --platform device --variant A
```

Flutter/RN support `android`, `simulator`, `device`; Compose supports `android`;
SwiftUI supports `simulator`, `device`. Select S/A explicitly. Android builds are
Release arm64-v8a, with local development signing (no private key committed).
iOS device `.app` bundles are unsigned arm64 Release and cannot be treated as
verified device installations or exported IPAs. SwiftUI/RN simulator builds are
optimized; Flutter simulator is Debug because the tested SDK rejects its other
modes there. RN embeds JavaScript/Hermes and needs no running Metro server.

Archives and source hashes are under `.work/artifacts/<stack>/<variant>/`.
React Native root builds reject an unexpected Node version and refresh the ignored
Xcode `NODE_BINARY` setting from that selected executable. This prevents an old
pilot/CocoaPods-generated path from silently overriding the declared version.

Source separation can be inspected independently:

```sh
python3 scripts/export_sources.py S
python3 scripts/export_sources.py A
```

Generated S has no custom timer or image coordinate interpolation; A adds it.
Never run arbitrary framework build commands over canonical A to measure S:
root preparation is part of this experiment's build contract.

## 5. Run and verify on iOS Simulator

Choose an iPhone 17 Pro running iOS 26.5 from `xcrun simctl list devices available`.
Use its actual identifier rather than copying a host-specific identifier:

```sh
export LAB_IOS_DEVICE="your-simulator-identifier"
xcrun simctl boot "$LAB_IOS_DEVICE"
xcrun simctl bootstatus "$LAB_IOS_DEVICE" -b
xcrun simctl status_bar "$LAB_IOS_DEVICE" override --time '9:41' --batteryState charged --batteryLevel 100
python3 scripts/build_matrix.py --inspection
python3 scripts/verify_matrix.py --platform ios --device "$LAB_IOS_DEVICE"
```

If already booted, skip `simctl boot`. The matrix installs each archived artifact,
resets this lab's fictional favorites, runs catalogue/scroll flows for both
variants, then records A demos and five deterministic A stages. Inspection builds
also expose `Motion: reduced/animated`, which reads the real framework/OS flag.
The script temporarily changes Reduce Motion and restarts the dedicated simulator
to apply its accessibility preference. It verifies the instant branch's navigation, and restores animated mode in a `finally` block.
This does not measure exact input latency. The probe is excluded from production.

To install and open a single app yourself:

```sh
xcrun simctl install "$LAB_IOS_DEVICE" .work/artifacts/swift/A/simulator.app
xcrun simctl launch "$LAB_IOS_DEVICE" dev.devaxes.catalogue.swift
```

SwiftUI ID: `dev.devaxes.catalogue.swift`; Flutter: `dev.devaxes.flutterPilot`.
RN retains the pilot target name `PilotRN`; read its identifier with
`/usr/libexec/PlistBuddy -c 'Print CFBundleIdentifier' .work/artifacts/react-native/A/simulator.app/Info.plist`.

## 6. Run and verify on Android

Shut down the simulator before runtime diagnostics. Create a dedicated AVD using
the Pixel 6 profile, API 35 Google Play arm64 image, 1080×2400 pixels and 420 dpi.
The reference AVD is named LabPilot_API35; it is a virtual environment, not a Pixel 6 result.

```sh
xcrun simctl shutdown "$LAB_IOS_DEVICE"
mkdir -p .local/avd
export ANDROID_AVD_HOME="$PWD/.local/avd"
avdmanager create avd -n LabPilot_API35 -k 'system-images;android-35;google_apis_playstore;arm64-v8a' -d pixel_6
```

Before launching, set `PlayStore.enabled = no` in
`.local/avd/LabPilot_API35.avd/config.ini` to match the diagnostic environment.
Then launch with 2 GiB RAM and four CPUs:

```sh
emulator -avd LabPilot_API35 -port 5580 -memory 2048 -cores 4 -no-window -no-audio -no-snapshot -gpu host > .work/emulator.log 2>&1 &
adb -s emulator-5580 wait-for-device
adb -s emulator-5580 shell getprop sys.boot_completed
```

Wait until the last command returns `1`. Confirm `adb shell wm size` and
`adb shell wm density`; do not silently use a different density for the reference
geometry. If the emulator is already running, do not launch a second instance.
A graphical emulator is also usable for manual review; no window is needed for
Maestro. Use default text scale, portrait and light mode. The UI matrix explicitly
sets all three animation scales to 1, tests 0 for reduced motion, then restores 1.

```sh
python3 scripts/verify_matrix.py --platform android --device emulator-5580
adb -s emulator-5580 install -r .work/artifacts/compose/A/android.apk
adb -s emulator-5580 shell am start -n dev.devaxes.catalogue/.MainActivity
```

Android IDs: Compose `dev.devaxes.catalogue`, Flutter `dev.devaxes.flutter_pilot`,
RN `com.pilotrn`. Run a single recorded flow with:

```sh
python3 scripts/verify.py --stack compose --platform android --variant A --device emulator-5580 --flow catalogue
```

Flows: `catalogue`, `scroll`, `android-back` (Android only), `demo`, `progress`
and `reduced-motion`; `navigation-guard` exercises button back on iOS.
The timeline and reduced-motion flows require separately archived inspection builds.
Repeated-input/system-back flow verifies successful navigation but does not
promise sub-frame placement of input by the automation driver.

## 7. Collect and render results

Keep builds and screen recording separate from memory diagnostics. Stop other
benchmark processes, keep only the Android AVD active, and use the actual final
Release artifacts. The optional memory run takes roughly half an hour:

```sh
python3 scripts/collect_environment.py
python3 scripts/diagnose_android.py --device emulator-5580
python3 scripts/collect_builds.py
python3 scripts/collect_code.py
python3 scripts/collect_trials.py
python3 scripts/collect_scroll.py
python3 scripts/check_geometry.py
python3 scripts/compose_videos.py
python3 scripts/acceptance.py
python3 scripts/report.py
```

The memory driver alternates stacks and S/A across three series. Each runs a first
cycle separately, 5 warmups, 30 cycles, and one second of stable rest. It preserves
meminfo and gfxinfo output; PSS snapshots are before/after a series, not sampled
on every frame. No common jank ranking is derived from gfxinfo. Geometry is
segmented from source image colors and checked against an independent Bézier
solver within 2 logical units. It verifies bounds/corner samples and a source landmark for centered uniform
cover crop, not text metrics
or real-time duration. `report.py` refuses mixed revisions within a stack or dirty size artifacts. Each
stack retains its actual verified source revision; later changes to another stack
do not relabel earlier artifacts.
Results are JSON, XML, PNG, text traces and MP4, with artifact hashes and commands.
Raw local tool logs stay in `.work/`; publish only sanitized evidence.

## Troubleshooting

- A stale or inaccessible selector is a driver failure, not a zero measurement.
  Inspect local `run.log`, commands and hierarchy in `.work/verification/`.
  A scroll target can be clipped behind the fixed header, or a tap can arrive
  while the list is settling. The common flow waits for stabilization, taps the
  lower photo region with retry if unchanged, and asserts the unique detail body. Keep failed attempts through `collect_trials.py`.
- Old Gradle metadata locks need the documented Compose stdlib-common exclusion;
  do not rewrite all locks to hide a failure. Ordinary builds consume existing locks.
- Pod installation from the wrong directory breaks autolinking. Confirm Ruby and
  CocoaPods versions and use the iOS directory.
- `sdkmanager`, Ruby or Flutter missing from PATH is an installation problem;
  do not add private host paths to the repository. Generated app assets and
  selected transition files are restored by `prepare.py`.
- iOS simulator Release/Profile rejection in Flutter is expected in the tested
  version. Use Debug to verify UI and device Release only to compare bundle size.
- Do not interpret the programmed 400 ms duration, driver waits, virtual model
  names or a video frame rate as physical-device performance.

If a previous local pilot uses a different Android development signing key,
installation can report `INSTALL_FAILED_UPDATE_INCOMPATIBLE`. On the dedicated
lab AVD only, uninstall the named fictional lab package before retrying (for
example `adb -s emulator-5580 uninstall com.pilotrn`). This deletes its sample
favorites. Do not apply this cleanup to unrelated apps or personal devices.
UI-driver startup was verified with JDK 17; select that Java runtime before
Maestro instead of relying on a different system Java installation.
