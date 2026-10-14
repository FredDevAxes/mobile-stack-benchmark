# Working on this lab

All repository content, commits and public discussions must be in English.
Original code and artwork are MIT; preserve third-party licenses.
Implement only the hiking catalogue defined in docs/protocol.md.
Keep shared data and artwork authoritative in shared/. Generated asset copies
must be regenerated with scripts/assets.py and verified by checksum.
Build targets and run their linters and tests before committing changes.
Keep S (instant) and A (animated) independently buildable. Animation-only code
must be absent from S builds; a runtime switch alone is insufficient.
Record actual results with revision, command, environment and raw evidence.
Never replace unavailable measurements with zero or compare Debug and Release
performance. Do not rank Android against iOS or claim physical-device results.
Never commit credentials, signing keys, host paths or pilot logs. Scan staged
changes and history with gitleaks before publishing. Use targeted English commits.
