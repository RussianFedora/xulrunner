%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%define nss_version 3.10
%define cairo_version 1.3.12
%define prerelease a5pre
%define alphatag 20070519cvs

Summary:        XUL Runner
Name:           xulrunner
Version:        1.9
Release:        0.1.%{prerelease}.%{alphatag}
URL:            http://dev.laptop.org/~marco/xulrunner-1.9a5pre-cvs20070519.tar.bz2
License:        MPL/LGPL
Group:          Applications/Internet
Source0:        xulrunner-%{version}%{prerelease}-cvs20070519.tar.bz2
Source10:       xulrunner-mozconfig
Source12:       xulrunner-olpc-default-prefs.js

# build patches

# patches from upstream (Patch100+)
Patch201:       xulrunner-1.9a3pre-dpi.patch
Patch202:       xulrunner-1.9a5pre-build.patch
Patch203:       firefox-0.7.3-psfonts.patch

# ---------------------------------------------------

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  nss-devel >= %{nss_version}
BuildRequires:  cairo-devel >= %{cairo_version}
BuildRequires:  libpng-devel, libjpeg-devel
BuildRequires:  zlib-devel, zip
BuildRequires:  libIDL-devel
BuildRequires:  gtk2-devel
BuildRequires:  krb5-devel
BuildRequires:  pango-devel
BuildRequires:  freetype-devel >= 2.1.9
BuildRequires:  libXt-devel
BuildRequires:  libXrender-devel
BuildRequires:  python-devel
BuildRequires:  nspr-devel

Requires:       nss >= %{nss_version}
Requires:       pkgconfig

Provides:       gecko-libs = %{version}
%define mozappdir %{_libdir}/%{name}-%{version}

%description
XULRunner is a Mozilla runtime package that can be used to bootstrap XUL+XPCOM
applications that are as rich as Firefox and Thunderbird. It will provide
mechanisms for installing, upgrading, and uninstalling these applications.
XULRunner will also provide libxul, a solution which allows the embedding
of Mozilla technologies in other projects and products.

%package devel
Summary: Libraries and headers for gecko-embed
Group: Development/Libraries
Requires: %name = %{version}
Provides: gecko-devel = %{version}

%description devel
XUL Runner devel is...

%prep
%setup -q -n mozilla

%patch201 -p0 -b .dpi
%patch202 -p0 -b .build
%patch203 -p1 -b .psfonts

%{__rm} -f .mozconfig
%{__cp} %{SOURCE10} .mozconfig

cat << EOF >> .mozconfig
ac_add_options --with-default-mozilla-five-home=%{_libdir}/xulrunner-%{version} 
EOF

%build
# Build with -Os as it helps the browser; also, don't override mozilla's warning
# level; they use -Wall but disable a few warnings that show up _everywhere_
MOZ_OPT_FLAGS=$(echo $RPM_OPT_FLAGS | %{__sed} -e 's/-O2/-Os/' -e 's/-Wall//')

export RPM_OPT_FLAGS=$MOZ_OPT_FLAGS
export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'

%ifarch ppc ppc64 s390 s390x
%define moz_make_flags -j1
%else
%define moz_make_flags %{?_smp_mflags}
%endif

export LDFLAGS="-Wl,-rpath,%{mozappdir}"
MAKE="gmake %{?_smp_mflags}" 
make -f client.mk build

%install
rm -rf $RPM_BUILD_ROOT
make install DESTDIR=$RPM_BUILD_ROOT
rm -f %{buildroot}%{_libdir}/xulrunner-%{version}%{prerelease}/sdk/*.so

# set up our default preferences
%{__cp} %{SOURCE12} $RPM_BUILD_ROOT/%{mozappdir}/greprefs/all-olpc.js
%{__cp} %{SOURCE12} $RPM_BUILD_ROOT/%{mozappdir}/defaults/pref/all-olpc.js

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc LICENSE LEGAL
%{_bindir}/xulrunner
%{_libdir}/xulrunner-%{version}%{prerelease}/chrome
%{_libdir}/xulrunner-%{version}%{prerelease}/components
%{_libdir}/xulrunner-%{version}%{prerelease}/defaults
%{_libdir}/xulrunner-%{version}%{prerelease}/dictionaries
%{_libdir}/xulrunner-%{version}%{prerelease}/greprefs
%{_libdir}/xulrunner-%{version}%{prerelease}/icons
%{_libdir}/xulrunner-%{version}%{prerelease}/plugins
%{_libdir}/xulrunner-%{version}%{prerelease}/res
%{_libdir}/xulrunner-%{version}%{prerelease}/*.so
%{_libdir}/xulrunner-%{version}%{prerelease}/mozilla-xremote-client
%{_libdir}/xulrunner-%{version}%{prerelease}/regxpcom
%{_libdir}/xulrunner-%{version}%{prerelease}/run-mozilla.sh
%{_libdir}/xulrunner-%{version}%{prerelease}/updater
%{_libdir}/xulrunner-%{version}%{prerelease}/xp*
%{_libdir}/xulrunner-%{version}%{prerelease}/xulrunner*
%{python_sitearch}/xpcom

%files devel
%defattr(-, root, root)
%{_bindir}/xulrunner-config
%{_libdir}/xulrunner-%{version}%{prerelease}/sdk
%{_libdir}/pkgconfig/*
%{_includedir}/xulrunner-%{version}%{prerelease}
%{_datadir}/idl/xulrunner-%{version}%{prerelease}
%{_datadir}/aclocal/nspr.m4

%changelog
* Fri Jun 22 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9-0.1.a5pre.20070519cvs
- Fix release scheme
- Fix URL
- Temporarily disable system nspr

* Thu Jun 21 2007 John (J5) Palmieri <johnp@redhat.com> 1.9-5.a5pre.cvs20070519.1
- add firefox-0.7.3-psfonts.patch
- fix provides typo
- fix up mozconfig 

* Tue Jun 19 2007 John (J5) Palmieri <johnp@redhat.com> 1.9-4.a5pre.cvs20070519.1
- remove pango patches
- build with system nspr
- add default pref file so we don't try to autoupdate new xulrunners

* Tue Jun 19 2007 John (J5) Palmieri <johnp@redhat.com> 1.9-3.a5pre.cvs20070519.1
- Add provides on gecko
- use -rpath in build
- remove pragma visibility patch

* Fri Jun 15 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9-2.a5pre.cvs20070519.1
- Various rpmlint fixes

* Mon May 28 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a5pre-1.cvs20070519.1
- Drop gre installation. Use "make install". Build pyxpcom.

* Wed May  9 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a5pre-1.cvs20070509.1
- Update snapshot and add patch to expose dirprovider setter

* Thu Mar 29 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a3pre-2.cvs20070314.7
- Slightly improved patch for window.innerWidth and window.innerHeight

* Thu Mar 29 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a3pre-2.cvs20070314.6
- Add patch to fix window.innerWidth and window.innerHeight (#375519)

* Fri Mar 23 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a3pre-2.cvs20070314.5
- Add patch to unbreak the filechooser

* Thu Mar 22 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a3pre-2.cvs20070314.4
- Better dpi patch

* Wed Mar 21 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a3pre-2.cvs20070314.3
- Remove the dpi patch

* Wed Mar 21 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a3pre-2.cvs20070314.2
- Add patches to fix text selection and dpi

* Wed Mar 14 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a3pre-2.cvs20070314.1
- Update to cvs20070314

* Mon Feb  8 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a3pre-1.cvs20070208.1
- Update to 1.9a3pre

* Mon Feb  5 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a2-1.cvs20070129.2
- Add a gre configuration file

* Mon Jan 29 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9a2-1
- Update to 1.9 cvs

* Thu Dec 21 2006 Marco Pesenti Gritti <mpg@redhat.com> 1.8.0.4-4
- Do not strip symbols

* Thu Oct 18 2006 Marco Pesenti Gritti <mpg@redhat.com> 1.8.0.4-3
- Enable the cookie extension

* Wed Oct  4 2006 Marco Pesenti Gritti <mpg@redhat.com> 1.8.0.4-2
- Make xulruner-devel depend on nspr-devel

* Tue Sep 12 2006 Marco Pesenti Gritti <mpg@redhat.com> 1.8.0.4-1
- Update to final 1.8.0.4

* Mon May 17 2006 Marco Pesenti Gritti <mpg@redhat.com> 1.8.0.4-0.cvs20060505.3
- Remove the requires/provide custom stuff

* Tue May 16 2006 David Zeuthen <davidz@redhat.com> 1.8.0.4-0.cvs20060505.2
- Build with --disable-gnomeui --disable-gnomevfs and drop BuildRequires
- gnome-vfs2-devel, ligbnome-devel, libgnomeui-devel

* Wed May 10 2006 Marco Pesenti Gritti <mpg@redhat.com> 1.8.0.4-0.cvs20060505.1
- Disable pyxpcom since we dont use it and is broken

* Mon May 8 2006 Marco Pesenti Gritti <mpg@redhat.com> 1.8.0.cvs20060505-1
- Move the cvs version to release tag

* Mon May 8 2006 Marco Pesenti Gritti <mpg@redhat.com> 1.8.0.cvs20060505-1
- Update source to MOZILLA_1.8.0_BRANCH
