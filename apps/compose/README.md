# Compose catalogue

Kotlin and Jetpack Compose implement the Android target. Favorites are stored in
SharedPreferences. The `instant` and `animated` Gradle flavors select separate
navigation modules; root commands also remove animation-only source geometry
from S. A uses animation-core's 400 ms linear clock with the common Bézier curve.

From the repository root after [setup](../../README.md):

```sh
python3 scripts/lab.py lint --stack compose
python3 scripts/lab.py test --stack compose
python3 scripts/lab.py build --stack compose --platform android --variant S
python3 scripts/lab.py build --stack compose --platform android --variant A
```

Outputs are `.work/artifacts/compose/<variant>/android.apk`. They are arm64-only,
R8-minified Release APKs signed with a local development key. Root commands
produce the benchmark baseline; `python3 scripts/export_sources.py S` exports
its exact UI source. ktlint covers Kotlin/build scripts; Android Lint covers the
app. JUnit checks the model; the shared Maestro flows check the installed UI.

Gradle locks are committed. The metadata-only Kotlin common module is excluded
from lock validation but explicitly forced to 2.2.10, as explained in the
[reproduction decisions](../../docs/decisions.md). Original code is
[MIT](../../LICENSE), with [upstream credits](../../THIRD_PARTY.md).
