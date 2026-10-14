# Flutter catalogue

Dart/Flutter provides one implementation for Android and iOS. Both navigation
variants use the same product data and local favorites. A adds an explicit
400 ms rectangle transition; S excludes its timer, ticker and geometry code.

Run these commands from the repository root after the [root setup](../../README.md):

```sh
python3 scripts/prepare.py A
cd apps/flutter
flutter pub get --enforce-lockfile
cd ../..
python3 scripts/lab.py lint --stack flutter
python3 scripts/lab.py test --stack flutter
python3 scripts/lab.py build --stack flutter --platform android --variant S
python3 scripts/lab.py build --stack flutter --platform android --variant A
python3 scripts/lab.py build --stack flutter --platform simulator --variant A
python3 scripts/lab.py build --stack flutter --platform device --variant A
```

Select either S or A for each build. Android and unsigned iOS device artifacts
are Release; the tested iOS simulator supports Debug only. Archives are kept in
`.work/artifacts/flutter/<variant>/`. Use root build commands for comparisons:
they remove inspection-only controls and select the physical source variant.
`python3 scripts/export_sources.py S` exports the derived source for review.

`flutter analyze` and `dart format` cover Dart; platform scaffolds are compiled
with their SDK tools. Unit tests cover the dataset, search and favorite filtering.
The common Maestro flows check the actual app. Original code is [MIT](../../LICENSE);
upstream [notices](../../THIRD_PARTY.md) remain applicable.
