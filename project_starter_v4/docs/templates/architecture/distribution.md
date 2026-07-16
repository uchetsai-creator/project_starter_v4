# Distribution

<!--
  For: Library / SDK and CLI Tool projects
  Replaces: deployment.md (libraries and CLIs are not "deployed" — they are distributed)
  Purpose: Documents how the package is built, published, and installed by end users.
  Update when: Build process changes, a new registry is added or removed,
               installation instructions change, or CI/CD pipeline changes.
-->

## Package Identity

| Property | Value |
|---|---|
| Package name | [e.g., `my-library`, `my-cli`] |
| Registry | [npm / PyPI / crates.io / GitHub Releases / Homebrew / etc.] |
| Registry URL | [Direct link to the package page] |
| Source repository | [GitHub / GitLab URL] |

---

## Build

**Prerequisites:**

```bash
# Install build tools
[command — e.g., npm install / pip install build / cargo build]
```

**Build command:**

```bash
[build command — e.g., npm run build / python -m build / cargo build --release]
```

**Output:**

| Artifact | Path | Description |
|---|---|---|
| [Library bundle / Binary] | `[dist/index.js / dist/*.whl / target/release/binary]` | [What it is] |
| [Type declarations] | `[dist/index.d.ts]` | [TypeScript types — if applicable] |

---

## Publish

**Authentication:**

```bash
# Authenticate with the registry before publishing
[auth command — e.g., npm login / twine upload requires PYPI_TOKEN env var]
```

**Publish command:**

```bash
[publish command — e.g., npm publish / twine upload dist/* / cargo publish]
```

**Required before publishing:**
- Version bumped in `[pyproject.toml / package.json / Cargo.toml]`
- `CHANGELOG.md` updated (see `docs/specs/release-guide.md`)
- All tests passing
- Git tag created and pushed

---

## Installation (end user)

```bash
# npm
npm install [package-name]

# PyPI
pip install [package-name]

# Homebrew (if applicable)
brew install [formula-name]

# Binary download (if applicable)
curl -L [release URL] | tar xz
```

---

## CI/CD Pipeline

| Stage | Trigger | Action |
|---|---|---|
| Test | Every PR and push | Run full test suite |
| Build | Every merge to `main` | Build distributable artifact |
| Publish | Git tag `v*` pushed | Publish to registry |

CI configuration: [`[link to CI config — .github/workflows/*.yml / .gitlab-ci.yml]`]

---

## Release Artifacts

For each GitHub/GitLab release, attach:

| File | Description |
|---|---|
| `[package-name]-[version].tar.gz` | Source archive |
| `[binary-name]-linux-x86_64` | Linux binary (if CLI) |
| `[binary-name]-darwin-arm64` | macOS ARM binary (if CLI) |
| `[binary-name]-windows-x86_64.exe` | Windows binary (if CLI) |

Checksums (`SHA256SUMS`) must be attached alongside binaries.
