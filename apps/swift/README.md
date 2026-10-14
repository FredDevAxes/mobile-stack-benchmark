# SwiftUI catalogue

SwiftUI implements the iOS target. UserDefaults persists favorite IDs. A uses
CADisplayLink to evaluate the 400 ms curve and image rectangle. S has neither
that clock nor source-rectangle preferences/interpolation.

From the repository root with Xcode 27 selected:

```sh
xcrun swift-format lint --strict -r apps/swift
swift test --package-path apps/swift
python3 scripts/lab.py build --stack swift --platform simulator --variant S
python3 scripts/lab.py build --stack swift --platform simulator --variant A
python3 scripts/lab.py build --stack swift --platform device --variant S
python3 scripts/lab.py build --stack swift --platform device --variant A
```

The explicit packager compiles with `swiftc -O`, strips external debug symbols,
and copies the shared dataset/artwork. Simulator apps use local ad-hoc signing;
device bundles are unsigned. This is a minimal research app bundle rather than
an App Store export. Archives are `.work/artifacts/swift/<variant>/`.

The Swift package contains only the model, allowing XCTest on the build host.
The UI is compiled for iOS and checked with the common Maestro flows. Add
`--capture` to an A simulator build to enable deterministic inspection controls.
Original source is [MIT](../../LICENSE); Apple's SDK retains its own terms.
