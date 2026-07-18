# Compatibility Matrix

<!--
  For: Library / SDK projects, CLI Tool projects
  Purpose: Documents which runtime versions and peer dependencies are supported,
           and which combinations are known to work or fail.
  Update when: Support for a runtime version is added or dropped, a peer dependency
               version range changes, or a known incompatibility is discovered.
-->

## Supported Runtimes

| Runtime | Minimum version | Maximum tested | Status |
|---|---|---|---|
| [Node.js / Python / Go / JVM / etc.] | [e.g., 18.0] | [e.g., 22.x] | Active / Maintenance / Dropping in vX |

**End-of-life policy:** When a runtime version reaches official EOL, we drop support in the next MINOR release. No patch releases will be issued for EOL runtimes.

---

## Peer Dependencies

Peer dependencies are NOT bundled — callers must install them alongside this package.

| Package | Required version range | Notes |
|---|---|---|
| `[peer-dep-name]` | `>=2.0.0 <4.0.0` | [Why this range / any known issues at boundaries] |

**Strict peer resolution:** If your package manager enforces strict peer dependency checks, ensure your version falls within the declared range. Installing outside the range is unsupported.

---

## Compatibility Matrix

`✅` = tested and supported  `⚠️` = works but not officially tested  `❌` = known incompatibility  `—` = not applicable

| | [Runtime vX] | [Runtime vY] | [Runtime vZ] |
|---|---|---|---|
| **This package v1.x** | ✅ | ✅ | ⚠️ |
| **This package v2.x** | ❌ | ✅ | ✅ |

---

## Known Incompatibilities

| Combination | Issue | Workaround | Fixed in |
|---|---|---|---|
| [This package] v1.2 + [peer-dep] v3.5.0 | [Symptom description] | [Workaround if any] | v1.3.0 |

---

## Platform / OS Support

| Platform | Status | Notes |
|---|---|---|
| Linux (x86_64) | ✅ Supported | Primary CI target |
| macOS (x86_64 + ARM) | ✅ Supported | Tested on CI |
| Windows | ⚠️ Best-effort | Not in CI — community-reported issues accepted |

---

## Testing Policy

Every new release is tested against:
- All supported runtime versions in the matrix above
- Latest and minimum peer dependency versions

CI configuration: [`[link to CI config file]`]
