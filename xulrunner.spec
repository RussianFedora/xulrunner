%define nspr_version 4.6.99
%define nss_version 3.11.99
%define cairo_version 0.5

%define official_branding 0

%define version_internal  1.9pre

Summary:        XUL Runtime for Gecko Applications
Name:           xulrunner
Version:        1.9
Release:        0.beta2.14.nightly20080121%{?dist}
URL:            http://www.mozilla.org/projects/xulrunner/
License:        MPLv1.1 or GPLv2+ or LGPLv2+
Group:          Applications/Internet
%if %{official_branding}
%define tarball xulrunner-%{version}-source.tar.bz2
%else
%define tarball mozilla-20080121.tar.bz2
%endif
Source0:        %{tarball}
Source10:       %{name}-mozconfig
Source12:       %{name}-redhat-default-prefs.js
#Source21:       %{name}.sh.in
Source23:       %{name}.1
Source100:      find-external-requires

# build patches
Patch4:         mozilla-build.patch
Patch5:         xulrunner-path.patch
Patch6:         xulrunner-version.patch

# customization patches
Patch21:        firefox-0.7.3-psfonts.patch

# local bugfixes
Patch41:        firefox-2.0.0.4-undo-uriloader.patch
Patch42:        firefox-1.1-uriloader.patch

# font system fixes

# Other
Patch107:       mozilla-pkgconfig.patch

%if %{official_branding}
# Required by Mozilla Corporation


%else
# Not yet approved by Mozillla Corporation


%endif

# ---------------------------------------------------

BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires:  nspr-devel >= %{nspr_version}
BuildRequires:  nss-devel >= %{nss_version}
BuildRequires:  cairo-devel >= %{cairo_version}
BuildRequires:  libpng-devel, libjpeg-devel
BuildRequires:  zlib-devel, zip
BuildRequires:  libIDL-devel
BuildRequires:  gtk2-devel
BuildRequires:  gnome-vfs2-devel
BuildRequires:  libgnome-devel
BuildRequires:  libgnomeui-devel
BuildRequires:  krb5-devel
BuildRequires:  pango-devel
BuildRequires:  freetype-devel >= 2.1.9
BuildRequires:  libXt-devel
BuildRequires:  libXrender-devel
BuildRequires:  curl-devel

Requires:       nspr >= %{nspr_version}
Requires:       nss >= %{nss_version}
Provides:       gecko-libs = %{version}

#define _use_internal_dependency_generator 0
#define __find_requires %{SOURCE100}

%description
XULRunner provides the XUL Runtime environment for Gecko applications.

%package devel
Summary: Development files for Gecko
Group: Development/Libraries
Obsoletes: mozilla-devel
Obsoletes: firefox-devel < 2.1
Requires: xulrunner = %{version}-%{release}
Requires: nspr-devel >= %{nspr_version}
Requires: nss-devel >= %{nss_version}
Provides: gecko-devel = %{version}

%description devel
Gecko development files.

%package devel-unstable
Summary: Development files for Gecko, which are not considered stable
Group: Development/Libraries
Requires: xulrunner-devel = %{version}-%{release}
Provides: gecko-devel-unstable = %{version}

%description devel-unstable
Unstable files for use with development of Gecko applications.  These headers
are not frozen and APIs can change at any time, so should not be relied on.

#---------------------------------------------------------------------

%prep
%setup -q -n mozilla
%patch4   -p1
%patch5   -p1
%patch6   -p1 -b .ver

%patch107 -p1 -b .pk


# For branding specific patches.

%if %{official_branding}
# Required by Mozilla Corporation


%else
# Not yet approved by Mozilla Corporation


%endif

%{__rm} -f .mozconfig
%{__cp} %{SOURCE10} .mozconfig
%if %{official_branding}
%{__cat} %{SOURCE11} >> .mozconfig
%endif

#---------------------------------------------------------------------

%build
INTERNAL_GECKO=%{version_internal}
MOZ_APP_DIR=%{_libdir}/%{name}-${INTERNAL_GECKO}

# Mozilla builds with -Wall with exception of a few warnings which show up
# everywhere in the code; so, don't override that.
MOZ_OPT_FLAGS=$(echo $RPM_OPT_FLAGS | %{__sed} -e 's/-Wall//')
%ifarch ppc64
# temporary workaround for https://bugzilla.mozilla.org/show_bug.cgi?id=412220
MOZ_OPT_FLAGS="$MOZ_OPT_FLAGS -mno-fp-in-toc -mno-sum-in-toc"
%endif

export RPM_OPT_FLAGS=$MOZ_OPT_FLAGS
export PREFIX='%{_prefix}'
export LIBDIR='%{_libdir}'

%ifarch ppc ppc64 s390 s390x
%define moz_make_flags -j1
%else
%define moz_make_flags %{?_smp_mflags}
%endif

export LDFLAGS="-Wl,-rpath,${MOZ_APP_DIR}"
export MAKE="gmake %{moz_make_flags}"
make -f client.mk build

#---------------------------------------------------------------------

%install
%{__rm} -rf $RPM_BUILD_ROOT

INTERNAL_GECKO=%{version_internal}

INTERNAL_APP_NAME=%{name}-${INTERNAL_GECKO}
MOZ_APP_DIR=%{_libdir}/${INTERNAL_APP_NAME}

INTERNAL_APP_SDK_NAME=%{name}-sdk-${INTERNAL_GECKO}
MOZ_APP_SDK_DIR=%{_libdir}/${INTERNAL_APP_SDK_NAME}

DESTDIR=$RPM_BUILD_ROOT make install

%{__mkdir_p} $RPM_BUILD_ROOT/${MOZ_APP_DIR} \
             $RPM_BUILD_ROOT%{_datadir}/idl/${INTERNAL_APP_SDK_NAME} \
             $RPM_BUILD_ROOT%{_includedir}/${INTERNAL_APP_SDK_NAME}
#%{__install} -p -d dist/sdk/include $RPM_BUILD_ROOT%{_includedir}/${INTERNAL_APP_SDK_NAME}
#%{__install} -p -d dist/sdk/idl $RPM_BUILD_ROOT%{_datadir}/idl/${INTERNAL_APP_SDK_NAME}
#%{__install} -p dist/sdk/bin/* $RPM_BUILD_ROOT/$MOZ_APP_DIR
#%{__install} -p dist/sdk/lib/* $RPM_BUILD_ROOT/$MOZ_APP_SDK_DIR
%{__install} -p dist/sdk/bin/regxpcom $RPM_BUILD_ROOT/$MOZ_APP_DIR

%{__mkdir_p} $RPM_BUILD_ROOT{%{_libdir},%{_bindir},%{_datadir}/applications}

# set up our default preferences
%{__cat} %{SOURCE12} | %{__sed} -e 's,RPM_VERREL,%{version}-%{release},g' > rh-default-prefs
%{__install} -p -D -m 644 rh-default-prefs $RPM_BUILD_ROOT/${MOZ_APP_DIR}/defaults/pref/all-redhat.js
%{__rm} rh-default-prefs

%{__install} -p -D -m 644 %{SOURCE23} $RPM_BUILD_ROOT%{_mandir}/man1/%{name}.1

%{__rm} -f $RPM_BUILD_ROOT${MOZ_APP_DIR}/%{name}-config

cd $RPM_BUILD_ROOT${MOZ_APP_DIR}/chrome
find . -name "*" -type d -maxdepth 1 -exec %{__rm} -rf {} \;
cd -

%if %{official_branding}
%{__mkdir_p} $RPM_BUILD_ROOT${MOZ_APP_DIR}/chrome/icons/default/
%{__cp} other-licenses/branding/%{name}/default.xpm \
        $RPM_BUILD_ROOT${MOZ_APP_DIR}/chrome/icons/default/ 
%{__cp} other-licenses/branding/%{name}/default.xpm \
        $RPM_BUILD_ROOT${MOZ_APP_DIR}/icons/
%endif


# system extensions and plugins support
%{__mkdir_p} $RPM_BUILD_ROOT%{_datadir}/mozilla/extensions
%{__mkdir_p} $RPM_BUILD_ROOT%{_libdir}/mozilla/extensions
%{__mkdir_p} $RPM_BUILD_ROOT%{_libdir}/mozilla/plugins
%{__mkdir_p} $RPM_BUILD_ROOT%{_sysconfdir}/skel/.mozilla/extensions
%{__mkdir_p} $RPM_BUILD_ROOT%{_sysconfdir}/skel/.mozilla/plugins


# Prepare our devel package
%{__mkdir_p} $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_datadir}/idl/${INTERNAL_APP_SDK_NAME}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/pkgconfig

%{__cp} -rL dist/include/* \
  $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}
#%{__cp} -rL dist/idl/* \
#  $RPM_BUILD_ROOT/%{_datadir}/idl/${INTERNAL_APP_SDK_NAME}
#%{__mv} $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_NAME}/* \
#  $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_SDK_NAME}
#%{__mv} $RPM_BUILD_ROOT/%{_datadir}/idl/${INTERNAL_APP_NAME}/* \
#  $RPM_BUILD_ROOT/%{_datadir}/idl/${INTERNAL_APP_SDK_NAME}

install -c -m 755 dist/bin/xpcshell \
  dist/bin/xpidl \
  dist/bin/xpt_dump \
  dist/bin/xpt_link \
  $RPM_BUILD_ROOT/${MOZ_APP_DIR}

%{__rm} -rf $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_NAME}
%{__rm} -rf $RPM_BUILD_ROOT/%{_datadir}/idl/${INTERNAL_APP_NAME}

%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/include
ln -s  %{_includedir}/${INTERNAL_APP_SDK_NAME}/unstable \
       $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/include
%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/idl
ln -s  %{_datadir}/idl/${INTERNAL_APP_SDK_NAME}/unstable \
       $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/idl

%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/include
ln -s  %{_includedir}/${INTERNAL_APP_SDK_NAME}/stable \
       $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/include
%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/idl
ln -s  %{_datadir}/idl/${INTERNAL_APP_SDK_NAME}/stable \
       $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/idl

%{__rm} -rf $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/lib/*.so
pushd $RPM_BUILD_ROOT${MOZ_APP_DIR}
for i in *.so; do
    ln -s ${MOZ_APP_DIR}/$i $RPM_BUILD_ROOT${MOZ_APP_SDK_DIR}/sdk/lib/$i
done
popd

# GRE stuff
%ifarch x86_64 ia64 ppc64 s390x
%define gre_conf_file gre64.conf
%else
%define gre_conf_file gre.conf
%endif

MOZILLA_GECKO_VERSION=`./config/milestone.pl --topsrcdir=.`
%{__mv} $RPM_BUILD_ROOT/etc/gre.d/$MOZILLA_GECKO_VERSION".system.conf" \
        $RPM_BUILD_ROOT/etc/gre.d/%{gre_conf_file}
chmod 644 $RPM_BUILD_ROOT/etc/gre.d/%{gre_conf_file}

# Library path
%ifarch x86_64 ia64 ppc64 s390x
%define ld_conf_file xulrunner-64.conf
%else
%define ld_conf_file xulrunner-32.conf
%endif

%{__mkdir_p} $RPM_BUILD_ROOT/etc/ld.so.conf.d
%{__cat} > $RPM_BUILD_ROOT/etc/ld.so.conf.d/%{ld_conf_file} << EOF
${MOZ_APP_DIR}
EOF
                        
# Copy over the LICENSE
install -c -m 644 LICENSE $RPM_BUILD_ROOT${MOZ_APP_DIR}

# ghost files
%{__mkdir_p} $RPM_BUILD_ROOT${MOZ_APP_DIR}/components
touch $RPM_BUILD_ROOT${MOZ_APP_DIR}/components/compreg.dat
touch $RPM_BUILD_ROOT${MOZ_APP_DIR}/components/xpti.dat

#---------------------------------------------------------------------

%clean
%{__rm} -rf $RPM_BUILD_ROOT

#---------------------------------------------------------------------

%post
/sbin/ldconfig

%postun
/sbin/ldconfig

%preun
# is it a final removal?
if [ $1 -eq 0 ]; then
  %{__rm} -rf ${MOZ_APP_DIR}/components
fi

%files
%defattr(-,root,root,-)
%{_bindir}/xulrunner
%{_mandir}/man1/*
%{_libdir}/mozilla
%{_datadir}/mozilla
%dir /etc/gre.d
/etc/gre.d/%{gre_conf_file}
%dir %{_libdir}/%{name}-*
%exclude %dir %{_libdir}/%{name}-sdk-*
%{_libdir}/%{name}-*/LICENSE
%{_libdir}/%{name}-*/README.txt
%{_libdir}/%{name}-*/chrome
%{_libdir}/%{name}-*/dictionaries
%dir %{_libdir}/%{name}-*/components
%ghost %{_libdir}/%{name}-*/components/compreg.dat
%ghost %{_libdir}/%{name}-*/components/xpti.dat
%{_libdir}/%{name}-*/components/*
%{_libdir}/%{name}-*/defaults
%{_libdir}/%{name}-*/greprefs
%{_libdir}/%{name}-*/icons
%{_libdir}/%{name}-*/modules
%{_libdir}/%{name}-*/plugins
%{_libdir}/%{name}-*/res
%{_libdir}/%{name}-*/*.so
%{_libdir}/%{name}-*/mozilla-xremote-client
%{_libdir}/%{name}-*/run-mozilla.sh
%{_libdir}/%{name}-*/regxpcom
%{_libdir}/%{name}-*/xulrunner
%{_libdir}/%{name}-*/xulrunner-bin
%{_libdir}/%{name}-*/xulrunner-stub
%{_libdir}/%{name}-*/platform.ini
%{_libdir}/%{name}-*/dependentlibs.list
%{_sysconfdir}/ld.so.conf.d/xulrunner*.conf
%{_sysconfdir}/skel/.mozilla


# XXX See if these are needed still
%{_libdir}/%{name}-*/updater*

%files devel
%defattr(-,root,root)
%dir %{_datadir}/idl/%{name}*%{version_internal}
%{_datadir}/idl/%{name}*%{version_internal}/stable
%{_includedir}/%{name}*%{version_internal}
%exclude %{_includedir}/%{name}*%{version_internal}/unstable
%dir %{_libdir}/%{name}-*
%dir %{_libdir}/%{name}-sdk-*
%dir %{_libdir}/%{name}-sdk-*/sdk
%{_libdir}/%{name}-*/xpcshell
%{_libdir}/%{name}-*/xpicleanup
%{_libdir}/%{name}-*/xpidl
%{_libdir}/%{name}-*/xpt_dump
%{_libdir}/%{name}-*/xpt_link
%{_libdir}/%{name}-sdk-*/*.h
%{_libdir}/%{name}-sdk-*/sdk/*
%exclude %{_libdir}/pkgconfig/*unstable*.pc
%exclude %{_libdir}/pkgconfig/*gtkmozembed*.pc
%{_libdir}/pkgconfig/*.pc

%files devel-unstable
%defattr(-,root,root)
%{_datadir}/idl/%{name}*%{version_internal}/unstable
%{_includedir}/%{name}*%{version_internal}/unstable
%dir %{_libdir}/%{name}-sdk-*
%{_libdir}/%{name}-sdk-*/*
%exclude %{_libdir}/%{name}-sdk-*/*.h
%exclude %{_libdir}/%{name}-sdk-*/sdk
%{_libdir}/pkgconfig/*unstable*.pc
%{_libdir}/pkgconfig/*gtkmozembed*.pc

#---------------------------------------------------------------------

%changelog
* Wed Jan 25 2008 Martin Stransky <stransky@redhat.com> 1.9-0.beta2.14
- rebuild agains new nss
- enabled gnome vfs

* Wed Jan 23 2008 Martin Stransky <stransky@redhat.com> 1.9-0.beta2.13
- fixed stable pkg-config files (#429654)
- removed sqlite patch

* Mon Jan 21 2008 Christopher Aillon <caillon@redhat.com> 1.9-0.beta2.12
- Update to latest trunk (2008-01-21)

* Tue Jan 15 2008 Christopher Aillon <caillon@redhat.com> 1.9-0.beta2.11
- Update to latest trunk (2008-01-15)
- Now with system extensions directory support

* Sat Jan 13 2008 Christopher Aillon <caillon@redhat.com> 1.9-0.beta2.10
- Update to latest trunk (2008-01-13)
- Use CFLAGS instead of configure arguments
- Random cleanups: BuildRequires, scriptlets, prefs, etc.

* Sat Jan 12 2008 Christopher Aillon <caillon@redhat.com> 1.9-0.beta2.9
- Provide gecko-devel-unstable as well

* Wed Jan 9 2008 Martin Stransky <stransky@redhat.com> 1.9-0.beta2.8
- divided devel package to devel and devel-unstable

* Mon Jan 7 2008 Martin Stransky <stransky@redhat.com> 1.9-0.beta2.7
- removed fedora specific pkg-config files
- updated to the latest trunk (2008-01-07)
- removed unnecessary patches
- fixed idl dir (#427965)

* Thu Jan 3 2008 Christopher Aillon <caillon@redhat.com> 1.9-0.beta2.6
- Re-enable camellia256 support now that NSS supports it

* Thu Jan 3 2008 Martin Stransky <stransky@redhat.com> 1.9-0.beta2.5
- updated to the latest trunk (2008-01-03)

* Mon Dec 24 2007 Christopher Aillon <caillon@redhat.com> 1.9-0.beta2.4
- Don't Provide webclient (xulrunner is not itself a webclient)
- Don't Obsolete old firefox, only firefox-devel
- Kill legacy obsoletes (phoenix, etc) that were never in rawhide

* Thu Dec 21 2007 Martin Stransky <stransky@redhat.com> 1.9-0.beta2.3
- added java and plugin subdirs to plugin includes

* Thu Dec 20 2007 Martin Stransky <stransky@redhat.com> 1.9-0.beta2.2
- dependency fixes, obsoletes firefox < 3 and firefox-devel now

* Wed Dec 12 2007 Martin Stransky <stransky@redhat.com> 1.9-0.beta2.1
- updated to Beta 2.
- moved SDK to xulrunner-sdk

* Thu Dec 06 2007 Martin Stransky <stransky@redhat.com> 1.9-0.beta1.4
- fixed mozilla-plugin.pc (#412971)

* Tue Nov 27 2007 Martin Stransky <stransky@redhat.com> 1.9-0.beta1.3
- export /etc/gre.d/gre.conf (it's used by python gecko applications)

* Mon Nov 26 2007 Martin Stransky <stransky@redhat.com> 1.9-0.beta1.2
- added xulrunner/js include dir to xulrunner-js

* Tue Nov 20 2007 Martin Stransky <stransky@redhat.com> 1.9-0.beta1.1
- update to beta 1

* Mon Nov 19 2007 Martin Stransky <stransky@redhat.com> 1.9-0.alpha9.6
- packed all gecko libraries (#389391)

* Thu Nov 15 2007 Martin Stransky <stransky@redhat.com> 1.9-0.alpha9.5
- registered xulrunner libs system-wide
- added xulrunner-gtkmozembed.pc

* Wed Nov 14 2007 Martin Stransky <stransky@redhat.com> 1.9-0.alpha9.4
- added proper nss/nspr dependencies

* Wed Nov 14 2007 Martin Stransky <stransky@redhat.com> 1.9-0.alpha9.3
- more build fixes, use system nss libraries

* Tue Nov 6 2007 Martin Stransky <stransky@redhat.com> 1.9-0.alpha9.2
- build fixes

* Tue Oct 30 2007 Martin Stransky <stransky@redhat.com> 1.9-0.alpha9.1
- updated to the latest trunk

* Thu Sep 20 2007 David Woodhouse <dwmw2@infradead.org> 1.9-0.alpha7.4
- build fixes for ppc/ppc64

* Tue Sep 20 2007 Martin Stransky <stransky@redhat.com> 1.9-0.alpha7.3
- removed conflicts with the current gecko-based apps
- added updated ppc64 patch

* Tue Sep 18 2007 Martin Stransky <stransky@redhat.com> 1.9-0.alpha7.2
- build fixes

* Wed Sep  5 2007 Christopher Aillon <caillon@redhat.com> 1.9-0.alpha7.1
- Initial cut at XULRunner 1.9 Alpha 7
- Temporarily revert camellia 256 support since our nss doesn't support it yet
