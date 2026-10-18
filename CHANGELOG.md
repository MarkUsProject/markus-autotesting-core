# Changelog

## [unreleased]

- Raised the minimum supported Python version to 3.11.
- Pinned ruff to v0.17.1 in CI and pre-commit, and fixed new lint errors.
- Added version bounds (`>=0.20.0,<0.23`) to the `msgspec` dependency.
- Added decode-time validation of `uniqueItems` on `BaseTestData` fields (msgspec only emits it to the JSON schema).
- Required `BaseTestData.category` to contain at least one category (`minItems: 1`).

## [0.1.0]

Initial release on PyPI.
