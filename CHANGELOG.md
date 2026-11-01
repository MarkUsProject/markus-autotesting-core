# Changelog

## [unreleased]

- Raised the minimum supported Python version to 3.11.
- Pinned ruff to v0.17.1 in CI and pre-commit, and fixed new lint errors.
- Added version bounds (`>=0.20.0,<0.23`) to the `msgspec` dependency.
- Added decode-time validation of `uniqueItems` on `BaseTestData` fields (msgspec only emits it to the JSON schema).
- Changed the default of `BaseTesterSettings._env` from `None` to `{}`.
- Changed `BaseTesterSettings.tester_type` to return the struct's msgspec tag, so it matches the encoded `tester_type` when a subclass sets `tag=` explicitly.
- Rewrote the README with usage and development documentation.
- Ran the tests in CI on Python 3.11 to 3.15, and added a ruff formatting check to CI.
- Made `create_autotest_settings_class` raise `ValueError` when given no tester classes, and added tests for it.

## [0.1.0]

Initial release on PyPI.
