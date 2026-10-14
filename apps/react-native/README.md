# React Native catalogue

One TypeScript app targets Android and iOS with the Community CLI, Hermes and
Fabric. Local favorites use AsyncStorage. A uses React Native Animated's
JavaScript driver because the transition changes layout properties. S excludes
both the custom clock and rectangle measurement/interpolation code.

From the repository root, after the [toolchain setup](../../README.md):

```sh
cd apps/react-native
npm ci
bundle _2.6.2_ install
cd ios
bundle _2.6.2_ exec pod install --deployment
cd ../../..
python3 scripts/lab.py lint --stack react-native
python3 scripts/lab.py test --stack react-native
python3 scripts/lab.py build --stack react-native --platform android --variant S
python3 scripts/lab.py build --stack react-native --platform android --variant A
python3 scripts/lab.py build --stack react-native --platform simulator --variant A
python3 scripts/lab.py build --stack react-native --platform device --variant A
```

Select S or A for each target. Root builds archive outputs in
`.work/artifacts/react-native/<variant>/`; JavaScript is embedded, with no Metro
server needed to run these Release apps. Root commands apply source projection;
`python3 scripts/export_sources.py S` makes the baseline readable separately.
The original pilot's internal `PilotRN` target and `com.pilotrn` identifier are
retained; the visible app is Trail catalogue.

ESLint, Prettier and TypeScript cover maintained JS/TS; SDK compilers check native
scaffolds. Jest checks data, filtering, order and currency formatting. Maestro
checks the installed app. Original code is [MIT](../../LICENSE); adapted template
and dependency [notices](../../THIRD_PARTY.md) are retained.
