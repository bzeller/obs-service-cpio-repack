#
# spec file for package obs-service-cpio-repack
#
# Copyright (c) 2025 SUSE LLC
#
# All modifications and additions to the file contributed by third parties
# remain the property of their copyright owners, unless otherwise agreed
# upon. The license for this file, and modifications and additions to the
# file, is the same license as for the pristine package itself (unless the
# license for the pristine package is not an Open Source License, in which
# case the license is the MIT License). An "Open Source License" is a
# license that conforms to the Open Source Definition (Version 1.9)
# published by the Open Source Initiative.

Name:           obs-service-cpio-repack
Version:        0.1.0
Release:        0
Summary:        OBS source service: repack an obscpio as a versioned source tarball
License:        GPL-2.0-or-later
URL:            https://github.com/bzeller/obs-service-cpio-repack
BuildArch:      noarch

# Sources are maintained directly in OBS — no SCM service needed for this
# small self-contained package.
Source0:        cpio_repack
Source1:        cpio_repack.service

# rpmspec is provided by rpm-build
Requires:       python3
Requires:       rpm-build
Requires:       cpio
# zstd is only required when compression=zst is used; listed as a soft dep
Recommends:     zstd

%description
An OBS source service for use with mode="buildtime".

Reads the Name and Version tags from a spec file via rpmspec (honouring
all RPM macros including %%include chains), then repacks an obscpio archive
produced by obs_scm as a conventionally named
<name>-<version>.tar.<compression> source tarball.

The top-level directory inside the archive is renamed to <name>-<version>
before packing, matching the layout expected by %%autosetup / %%setup -n.

No server-side installation or administrator privileges are required.
Any OBS project can use this service by adding:

  BuildRequires: obs-service-cpio-repack

to the consuming spec file and using mode="buildtime" in _service.

%prep
# nothing to prepare — sources are plain files

%build
# nothing to build — pure Python, no compilation

%install
install -D -m 0755 %{SOURCE0} %{buildroot}%{_prefix}/lib/obs/service/cpio_repack
install -D -m 0644 %{SOURCE1} %{buildroot}%{_prefix}/lib/obs/service/cpio_repack.service

%check
python3 -m py_compile %{SOURCE0}

%files
%{_prefix}/lib/obs/service/cpio_repack
%{_prefix}/lib/obs/service/cpio_repack.service

%changelog
