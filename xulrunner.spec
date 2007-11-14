%define desktop_file_utils_version 0.9
%define nspr_version 4.6
%define nss_version 3.11.1
%define cairo_version 0.5
%define builddir %{_builddir}/mozilla
%define build_devel_package 1

%define official_branding 0


Summary:        XUL Runtime for Gecko Applications
Name:           xulrunner
Version:        1.9
Release:        0.alpha9.3%{?dist}
URL:            http://www.mozilla.org/projects/xulrunner/
License:        MPLv1.1 or GPLv2+ or LGPLv2+
Group:          Applications/Internet
%if %{official_branding}
%define tarball xulrunner-%{version}-source.tar.bz2
%else
%define tarball xulrunner-20071029.tar.bz2
%endif
Source0:        %{tarball}
Source10:       %{name}-mozconfig
Source12:       %{name}-redhat-default-prefs.js
#Source20:       %{name}.desktop
#Source21:       %{name}.sh.in
Source23:       %{name}.1
Source100:      find-external-requires
Source101:      add-gecko-provides.in

# build patches
Patch1:         firefox-2.0-link-layout.patch
Patch2:         camellia256.patch
Patch3:         xulrunner-compile.patch
Patch4:         mozilla-build.patch

# customization patches
Patch21:        firefox-0.7.3-psfonts.patch

# local bugfixes
Patch41:        firefox-2.0.0.4-undo-uriloader.patch
Patch42:        firefox-1.1-uriloader.patch

# font system fixes

# Other
Patch104:       mozilla-firefox-head.ppc64.patch
Patch105:       mozilla-xpcom.patch
Patch106:       mozilla-sqlite-build.patch

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
BuildRequires:  desktop-file-utils
BuildRequires:  gtk2-devel
BuildRequires:  gnome-vfs2-devel
BuildRequires:  libgnome-devel
BuildRequires:  libgnomeui-devel
BuildRequires:  krb5-devel
BuildRequires:  pango-devel
BuildRequires:  freetype-devel >= 2.1.9
BuildRequires:  libXt-devel
BuildRequires:  libXrender-devel
BuildRequires:  system-bookmarks
BuildRequires:  curl-devel

Requires:       nspr >= %{nspr_version}
Requires:       nss >= %{nss_version}
Requires:       desktop-file-utils >= %{desktop_file_utils_version}
Requires:       system-bookmarks
Obsoletes:      phoenix, mozilla-firebird, MozillaFirebird
#Obsoletes:      mozilla <= 37:1.7.13
#Obsoletes:      firefox < 2.1
Provides:       webclient
Provides:       gecko-libs = %{version}

%define _use_internal_dependency_generator 0

%if %{build_devel_package}
%define __find_provides %{_builddir}/add-gecko-provides
%else
%define __find_requires %{SOURCE100}
%endif

%description
XULRunner provides the XUL Runtime environment for Gecko applications.

%if %{build_devel_package}
%package devel
Summary: Development files for Gecko
Group: Development/Libraries
#Obsoletes: mozilla-devel
#Obsoletes: firefox-devel < 2.1
Requires: xulrunner = %{version}-%{release}
Requires: nspr-devel >= %{nspr_version}
Requires: nss-devel >= %{nss_version}
Provides: gecko-devel = %{version}

%description devel
Gecko development files.
%endif

#---------------------------------------------------------------------

%prep
%setup -q -n mozilla
%patch1   -p1 -b .link-layout
%patch2   -R -p1 -b .camellia256
%patch3   -p1
%patch4   -p1

%patch104 -p0 -b .ppc64

# Install missing *.pc files
pushd xulrunner/installer

# Copy as xpcom
cp libxul.pc.in mozilla-xpcom.pc.in
cp libxul-embedding.pc.in mozilla-embedding.pc.in

# Copy to expected xulrunner-*.pc
cp mozilla-js.pc.in xulrunner-js.pc.in
cp mozilla-plugin.pc.in xulrunner-plugin.pc.in
cp mozilla-xpcom.pc.in xulrunner-xpcom.pc.in
cp mozilla-embedding.pc.in xulrunner-embedding.pc.in
popd

%patch105 -p1 -b .pkg
%patch106 -p1 -b .sqlite


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
INTERNAL_GECKO=`./config/milestone.pl --topsrcdir=.`
MOZ_APP_DIR=%{_libdir}/%{name}-${INTERNAL_GECKO}

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

export LDFLAGS="-Wl,-rpath,${MOZ_APP_DIR}"
export MAKE="gmake %{moz_make_flags}"
make -f client.mk build

#---------------------------------------------------------------------

%install
%{__rm} -rf $RPM_BUILD_ROOT

INTERNAL_GECKO=`./config/milestone.pl --topsrcdir=.`
INTERNAL_APP_NAME=%{name}-${INTERNAL_GECKO}
MOZ_APP_DIR=%{_libdir}/${INTERNAL_APP_NAME}

DESTDIR=$RPM_BUILD_ROOT make install

%{__mkdir_p} $RPM_BUILD_ROOT/${MOZ_APP_DIR} \
             $RPM_BUILD_ROOT%{_datadir}/idl/${INTERNAL_APP_NAME} \
             $RPM_BUILD_ROOT%{_includedir}/${INTERNAL_APP_NAME}
%{__install} -p -d dist/sdk/include $RPM_BUILD_ROOT%{_includedir}/${INTERNAL_APP_NAME}
%{__install} -p -d dist/sdk/idl $RPM_BUILD_ROOT%{_datadir}/idl/${INTERNAL_APP_NAME}
%{__install} -p dist/sdk/bin/* $RPM_BUILD_ROOT/$MOZ_APP_DIR
%{__install} -p dist/sdk/lib/* $RPM_BUILD_ROOT/$MOZ_APP_DIR

%{__mkdir_p} $RPM_BUILD_ROOT{%{_libdir},%{_bindir},%{_datadir}/applications}

#desktop-file-install --vendor mozilla \
#  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
#  --add-category WebBrowser \
#  --add-category Network \
#  %{SOURCE20} 

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

# own mozilla plugin dir (#135050)
%{__mkdir_p} $RPM_BUILD_ROOT%{_libdir}/mozilla/plugins

# Prepare our devel package
%if %{build_devel_package}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_NAME}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_datadir}/idl/${INTERNAL_APP_NAME}
%{__mkdir_p} $RPM_BUILD_ROOT/%{_libdir}/pkgconfig
%{__cp} -rL dist/include/* \
  $RPM_BUILD_ROOT/%{_includedir}/${INTERNAL_APP_NAME}
%{__cp} -rL dist/idl/* \
  $RPM_BUILD_ROOT/%{_datadir}/idl/${INTERNAL_APP_NAME}
install -c -m 755 dist/bin/xpcshell \
  dist/bin/xpidl \
  dist/bin/xpt_dump \
  dist/bin/xpt_link \
  $RPM_BUILD_ROOT/${MOZ_APP_DIR}
%endif

# GRE stuff
#%ifarch x86_64 ia64 ppc64 s390x
#%define gre_conf_file gre64.conf
#%else
#%define gre_conf_file gre.conf
#%endif

#%{__mkdir_p} $RPM_BUILD_ROOT/etc/gre.d/
#%{__cat} > $RPM_BUILD_ROOT/etc/gre.d/%{gre_conf_file} << EOF
#[%{version}]
#GRE_PATH=${MOZ_APP_DIR}
#EOF

GECKO_VERSION=$(./config/milestone.pl --topsrcdir='.')
%{__cat} %{SOURCE101} | %{__sed} -e "s/@GECKO_VERSION@/$GECKO_VERSION/g" > \
                        %{_builddir}/add-gecko-provides
chmod 700 %{_builddir}/add-gecko-provides
                        
# Copy over the LICENSE
install -c -m 644 LICENSE $RPM_BUILD_ROOT${MOZ_APP_DIR}

# ghost files
%{__mkdir_p} $RPM_BUILD_ROOT${MOZ_APP_DIR}/components
touch $RPM_BUILD_ROOT${MOZ_APP_DIR}/components/compreg.dat
touch $RPM_BUILD_ROOT${MOZ_APP_DIR}/components/xpti.dat

# remove unused files
rm -rf $RPM_BUILD_ROOT/etc/gre.d
rm -rf $RPM_BUILD_ROOT/usr/lib/xulrunner-1.9a9pre/crashreporter
rm -rf $RPM_BUILD_ROOT/usr/lib/xulrunner-1.9a9pre/crashreporter.ini

rm -rf $RPM_BUILD_ROOT${MOZ_APP_DIR}/*.a

rm -rf $RPM_BUILD_ROOT${MOZ_APP_DIR}/bin
rm -rf $RPM_BUILD_ROOT${MOZ_APP_DIR}/lib
rm -rf $RPM_BUILD_ROOT${MOZ_APP_DIR}/include
rm -rf $RPM_BUILD_ROOT${MOZ_APP_DIR}/idl

rm -rf $RPM_BUILD_ROOT${MOZ_APP_DIR}/sdk/lib
ln -s ${MOZ_APP_DIR} $RPM_BUILD_ROOT${MOZ_APP_DIR}/sdk/lib

#---------------------------------------------------------------------

%clean
%{__rm} -rf $RPM_BUILD_ROOT

#---------------------------------------------------------------------

%post
#update-desktop-database %{_datadir}/applications

%postun
#update-desktop-database %{_datadir}/applications

%preun
# is it a final removal?
if [ $1 -eq 0 ]; then
  %{__rm} -rf ${MOZ_APP_DIR}/components
fi

%files
%defattr(-,root,root,-)
%{_bindir}/xulrunner
#%exclude %{_bindir}/xulrunner-config
%{_mandir}/man1/*
%{_libdir}/mozilla
#%dir /etc/gre.d
#/etc/gre.d/%{gre_conf_file}
%dir %{_libdir}/%{name}-*
%{_libdir}/%{name}-*/LICENSE
%{_libdir}/%{name}-*/README.txt
%{_libdir}/%{name}-*/chrome
%{_libdir}/%{name}-*/dictionaries
%dir %{_libdir}/%{name}-*/components
%ghost %{_libdir}/%{name}-*/components/compreg.dat
%ghost %{_libdir}/%{name}-*/components/xpti.dat
%{_libdir}/%{name}-*/components/*.xpt
%{_libdir}/%{name}-*/components/*.js
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

# XXX See if these are needed still
%{_libdir}/%{name}-*/updater*

%if %{build_devel_package}
%files devel
%defattr(-,root,root)
%{_datadir}/idl/%{name}-*
%{_includedir}/%{name}-*
%dir %{_libdir}/%{name}-*
%{_libdir}/%{name}-*/xpcshell
%{_libdir}/%{name}-*/xpicleanup
%{_libdir}/%{name}-*/xpidl
%{_libdir}/%{name}-*/xpt_dump
%{_libdir}/%{name}-*/xpt_link
%{_libdir}/%{name}-*/xpcom-config.h
%{_libdir}/%{name}-*/sdk/*
%{_libdir}/pkgconfig/*.pc
%endif

#---------------------------------------------------------------------

%changelog
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
