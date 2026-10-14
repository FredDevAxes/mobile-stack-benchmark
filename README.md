# Mobile Stack Benchmark

How much implementation work and build size does one animated catalogue add to
Flutter, React Native, Compose and SwiftUI? This lab builds the same offline
hiking catalogue in four stacks, with instant (S) and animated (A) navigation.

Status: implementation in progress. The existing local pilot demonstrated the six
toolchain targets, but its smoke apps are not comparable results. No performance
ranking or verified catalogue milestone is claimed yet.

The [protocol](docs/protocol.md) defines functionality and geometry before results
are collected. The [technical decisions](docs/decisions.md) explain the approach.
Shared fictional data and original artwork live in `shared/`; platform applications
will live in `apps/`, orchestration in `scripts/`, evidence in `results/`.

Original code and assets are [MIT](LICENSE). [Third-party credits](THIRD_PARTY.md)
retain the frameworks' own licenses.
