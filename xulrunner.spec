%{!?python_sitearch: %define python_sitearch %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib(1)")}

%define nss_version 3.10
%define cairo_version 1.3.12
%define prerelease b1

Summary:        XUL Runner
Name:           xulrunner
Version:        1.9
Release:        0.11.%{prerelease}%{?dist}
URL:            http://www.mozilla.org
License:        MPL/LGPL
Group:          Applications/Internet
Source0:        http://dev.laptop.org/pub/sugar/xulrunner/xulrunner-%{version}%{prerelease}.tar.bz2
Source10:       xulrunner-mozconfig
Source12:       xulrunner-olpc-default-prefs.js

Patch1:         xulrunner-1.9a6-no-native-theme.patch
Patch2:         xulrunner-1.9a3pre-dpi.patch
Patch3:         xulrunner-1.9a5pre-build.patch
Patch4:         xulrunner-1.9a6-xds.patch

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
BuildRequires:  curl-devel

Requires:       nss >= %{nss_version}
Requires:       pkgconfig

Provides:       gecko-libs = %{version}
%define mozappdir %{_libdir}/%{name}-%{version}%{prerelease}

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
%setup -q -n xulrunner-%{version}%{prerelease}

%patch1 -p0 -b .no-native-theme
%patch2 -p0 -b .dpi
%patch3 -p0 -b .build
%patch4 -p0 -b .xds

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

# own mozilla plugin dir (#135050)
%{__mkdir_p} $RPM_BUILD_ROOT%{_libdir}/mozilla/plugins

# set up our default preferences
%{__cp} %{SOURCE12} $RPM_BUILD_ROOT/%{mozappdir}/greprefs/all-olpc.js
%{__cp} %{SOURCE12} $RPM_BUILD_ROOT/%{mozappdir}/defaults/pref/all-olpc.js

%clean
%{__rm} -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root,-)
%doc LICENSE LEGAL
%{_bindir}/xulrunner
%{_sysconfdir}/gre.d/*.system.conf
%{_libdir}/mozilla
%{_libdir}/xulrunner-%{version}%{prerelease}

%files devel
%defattr(-, root, root)
%{_libdir}/pkgconfig/*.pc
%{_datadir}/idl/xulrunner-%{version}%{prerelease}
%{_libdir}/xulrunner-devel-%{version}%{prerelease}
%{_includedir}/xulrunner-%{version}%{prerelease}

%changelog
* Wed Nov 21 2007 Marco Pesenti Gritti <mpg@redhat.com> - 1.9-0.11.b1
- Update to 1.9b1

* Wed Oct 10 2007 Marco Pesenti Gritti <mpg@redhat.com> - 1.9-0.10.a9
- Upgrade to an a9 snapshot

* Mon Sep 17 2007 Marco Pesenti Gritti <mpg@redhat.com> - 1.9-0.9.a6
- Downgrade the source to pre6, add a patch for XdndDirectSave support

* Thu Aug 23 2007 Marco Pesenti Gritti <mpg@redhat.com> - 1.9-0.8.20070820cvs
- Own mozilla plugin dir

* Wed Aug 22 2007 Marco Pesenti Gritti <mpg@redhat.com> - 1.9-0.7.20070820cvs
- Update the pyxpcom build patch
- Adapt to the new build installation

* Mon Aug 20 2007 John (J5) Palmieri <johnp@redhat.com> - 1.9-0.6.20070820cvs
- new HEAD snapshot build
- remove ps-font patch as it no longer applies

* Sat Jul 21 2007 Marco Pesenti Gritti <mpg@redhat.com> - 1.9-0.5.a6
- Better no theme patch to preserve native scrollbars.

* Wed Jul 18 2007 Marco Pesenti Gritti <mpg@redhat.com> - 1.9-0.4.a6
- Add patch to disable native theme

* Tue Jul 10 2007 Marco Pesenti Gritti <mpg@redhat.com> - 1.9-0.3.a6
- Require curl-devel for airbag
- Disable system png for now, it misses APNG
- Disable system nss for now
- Update to a6
- Add some missing files

* Wed Jun 27 2007 Marco Pesenti Gritti <mpg@redhat.com> - 1.9-0.2.a5pre.20070519cvs
- Install the static libraries in lib/xulrunner-*

* Fri Jun 22 2007 Marco Pesenti Gritti <mpg@redhat.com> 1.9-0.1.a5pre.20070519cvs
- Fix release scheme
- Fix URL
- Temporarily disable system nspr
- Own mozilla plugin dir

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
