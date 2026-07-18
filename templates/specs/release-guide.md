# Release Guide

<!--
  For: Library / SDK projects, CLI Tool projects
  Purpose: Documents how to build, test, version, and publish a release.
           Also defines the deprecation policy and changelog format.
  Update when: The release process changes, a new registry is added,
               or the versioning or deprecation policy changes.
-->

## Versioning Policy

This project follows [Semantic Versioning 2.0.0](https://semver.org): `MAJOR.MINOR.PATCH`

| Change type | Version bump | Example |
|---|---|---|
| Breaking change to public API | MAJOR | `1.x.x` → `2.0.0` |
| New public symbol, backward-compatible | MINOR | `1.2.x` → `1.3.0` |
| Bug fix, internal change | PATCH | `1.2.3` → `1.2.4` |

**Breaking change definition:** any change that requires callers to update their code.
This includes: removing a public symbol, changing a function signature, changing return type, changing error types, changing behaviour that callers depend on.

**Pre-release:** `1.0.0-beta.1`, `1.0.0-rc.1` — not stable, callers must pin exact version.

---

## Release Checklist

Run this checklist before every release.

### 1. Code quality

- [ ] All tests pass: `[test command]`
- [ ] No linting errors: `[lint command]`
- [ ] Public API surface reviewed — any unintended exports?
- [ ] `docs/specs/public-api.md` up to date with all changes in this release

### 2. Changelog

- [ ] `CHANGELOG.md` has an entry for the new version (see format below)
- [ ] Breaking changes are in the `### Breaking` section with migration instructions
- [ ] Deprecations are listed with the target removal version

### 3. Version bump

```bash
# Bump version in the canonical location
# e.g., package.json / pyproject.toml / Cargo.toml / go.mod
[version bump command]
```

- [ ] Version updated in: `[list all files that contain the version number]`
- [ ] Git tag created: `git tag v[VERSION]`

### 4. Build

```bash
[build command]
# e.g., npm run build / python -m build / cargo build --release
```

- [ ] Build succeeds with no warnings
- [ ] Built artifact smoke-tested: `[smoke test command]`

### 5. Publish

```bash
[publish command]
# e.g., npm publish / twine upload dist/* / cargo publish
```

- [ ] Published to [npm / PyPI / crates.io / GitHub Releases]
- [ ] Published version is installable: `[install command from registry]`

### 6. Post-release

- [ ] Git tag pushed: `git push origin v[VERSION]`
- [ ] GitHub Release created with changelog entry as body
- [ ] Dependent projects notified if breaking change

---

## Changelog Format

File: `CHANGELOG.md` at repo root. Newest version at top.

```markdown
## [1.3.0] — 2024-06-01

### Added
- `new_function()` — [description]

### Changed
- `existing_function()` now returns `NewType` instead of `OldType`

### Deprecated
- `old_function()` — use `new_function()` instead. Will be removed in v2.0.0.

### Fixed
- [Bug description] — [link to issue]

### Breaking
- None

---

## [1.2.1] — 2024-05-15
...
```

---

## Deprecation Policy

1. A symbol is deprecated by adding a `@deprecated` annotation (or equivalent) and a changelog entry.
2. The deprecation entry must state the **version when it will be removed**.
3. The deprecated symbol must remain functional for at least **one minor version** before removal.
4. Removal is a MAJOR version bump.

```python
import warnings

def old_function():
    warnings.warn(
        "old_function() is deprecated. Use new_function() instead. "
        "Will be removed in v2.0.0.",
        DeprecationWarning,
        stacklevel=2,
    )
    return new_function()
```
