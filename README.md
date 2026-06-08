# obs-service-cpio-repack

An [OBS source service](https://openbuildservice.org/help/manuals/obs-user-guide/cha-obs-source-services) that repacks an `obscpio` archive produced by `obs_scm` into a conventionally named `<name>-<version>.tar.<compression>` source tarball, where `name` and `version` are read directly from the spec file using `rpmspec`.

## Problem it solves

`obs_scm` produces an `obscpio` archive whose version component is derived from git metadata (commit timestamp, hash, or nearest tag). When the authoritative version lives inside the repository itself — for example in a `%include`d `.inc` file or as RPM `%define` macros — `obs_scm` has no way to read it at fetch time.

This service runs at `buildtime`, after all source files are present, and uses `rpmspec` to evaluate the spec file with full macro expansion. The resulting tarball has the correct `<name>-<version>` top-level directory and filename, exactly as `%autosetup` expects.

## How it works

1. Resolves the `--archive` glob to a single `.obscpio` file.
2. Resolves the `--spec` glob to a single `.spec` file.
3. Runs `rpmspec --define "_sourcedir <cwd>" -q --queryformat '%{NAME} %{VERSION}'` against the spec — honouring all RPM macros including `%include` chains.
4. Extracts the obscpio into a temporary directory.
5. Renames the top-level directory to `<name>-<version>` if it differs.
6. Packs the result as `<name>-<version>.tar.<compression>` using a staging temp file in `outdir` for atomic placement.
7. Skips writing if an identical tarball already exists in the working directory (mirrors `obs-service-recompress` idempotency behaviour).

All files referenced by `%include` directives in the spec must already be present flat in the working directory. Use `obs_scm` + `extract_file` before this service to ensure they are available.

## Usage

In your `_service` file, replace the `tar` + `recompress` pair with:

```xml
<service name="cpio_repack" mode="buildtime">
  <param name="archive">mypackage-*.obscpio</param>
  <param name="spec">mypackage.spec</param>
  <param name="compression">bz2</param>
</service>
```

Add to your spec file:

```spec
BuildRequires: obs-service-cpio-repack
```

### Parameters

| Parameter | Default | Description |
|---|---|---|
| `archive` | `*.obscpio` | Glob matching the input `.obscpio` file. Must resolve to exactly one file. |
| `spec` | `*.spec` | Glob matching the spec file to query for `Name` and `Version`. Must resolve to exactly one file. |
| `compression` | `bz2` | Output compression format: `gz`, `bz2`, `xz`, or `zst`. |

## Requirements

| Dependency | Provided by |
|---|---|
| `python3` | `python3` |
| `rpmspec` | `rpm-build` |
| `cpio` | `cpio` |
| `zstd` | `zstd` (only needed when `compression=zst`) |

## Typical `_service` file

```xml
<services>
  <service name="obs_scm">
    <param name="scm">git</param>
    <param name="url">https://github.com/example/mypackage.git</param>
    <param name="revision">main</param>
    <param name="filename">mypackage</param>
  </service>

  <!-- Extract spec and any %include'd files flat to the package root -->
  <service name="extract_file">
    <param name="archive">mypackage-*.obscpio</param>
    <param name="files">*/packaging/mypackage.spec</param>
    <param name="outfilename">mypackage.spec</param>
  </service>

  <service name="extract_file">
    <param name="archive">mypackage-*.obscpio</param>
    <param name="files">*/packaging/mypackage-version.inc</param>
    <param name="outfilename">mypackage-version.inc</param>
  </service>

  <!-- Repack obscpio as a versioned tarball using version from the spec -->
  <service name="cpio_repack" mode="buildtime">
    <param name="archive">mypackage-*.obscpio</param>
    <param name="spec">mypackage.spec</param>
    <param name="compression">bz2</param>
  </service>
</services>
```
