%define indexhtml file:///usr/share/doc/HTML/index.html
%define default_bookmarks_file %{_datadir}/bookmarks/default-bookmarks.html
%define desktop_file_utils_version 0.9
%define nspr_version 4.6
%define nss_version 3.11.1
%define cairo_version 0.5
%define builddir %{_builddir}/mozilla
%define build_devel_package 1

%define official_branding 0

ExcludeArch: ppc64

Summary:        XUL Runtime for Gecko Applications
Name:           xulrunner
Version:        1.9
Release:        0.alpha7.1%{?dist}
URL:            http://www.mozilla.org/projects/xulrunner/
License:        MPL/LGPL
Group:          Applications/Internet
%if %{official_branding}
%define tarball xulrunner-%{version}-source.tar.bz2
%else
%define tarball xulrunner-1.9a7-source.tar.bz2
%endif
Source0:        %{tarball}
Source10:       %{name}-mozconfig
Source12:       %{name}-redhat-default-prefs.js
#Source20:       %{name}.desktop
#Source21:       %{name}.sh.in
#Source22:       firefox.png
Source23:       %{name}.1
#Source50:       firefox-xremote-client.sh.in
Source100:      find-external-requires

# build patches
Patch1:         firefox-2.0-link-layout.patch

# customization patches
Patch21:        firefox-0.7.3-psfonts.patch

# local bugfixes
Patch41:        firefox-2.0.0.4-undo-uriloader.patch
Patch42:        firefox-1.1-uriloader.patch

# font system fixes

# Other
Patch104:       firefox-1.5-ppc64.patch

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
Obsoletes:      mozilla <= 37:1.7.13
Obsoletes:      firefox < 2.1
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
Obsoletes: mozilla-devel
Obsoletes: firefox-devel < 2.1
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
#%patch3  -p1
#%patch4  -p1
#%patch5  -p1 -b .visibility

#%patch20 -p0
#%patch21 -p1 -b .psfonts
#%patch22 -p0 -b .default-applications
#%patch40 -p1 -b .bullet-bill
#%patch41 -p1 -b .undo-uriloader
#%patch42 -p0 -b .uriloader
#%patch81 -p1 -b .nopangoxft
#%patch82 -p1 -b .pango-mathml
#%patch83 -p1 -b .pango-cursor-position
#%patch84 -p0 -b .pango-printing

#%patch100 -p1 -b .thread-cleanup
#%patch102 -p0 -b .theme-change
%patch104 -p1 -b .ppc64

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

# set up our default bookmarks
cp %{default_bookmarks_file} $RPM_BUILD_DIR/mozilla/profile/defaults/bookmarks.html


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

#DESTDIR=$RPM_BUILD_ROOT make install
%{__mkdir_p} $RPM_BUILD_ROOT/${MOZ_APP_DIR} \
             $RPM_BUILD_ROOT%{_datadir}/idl/${INTERNAL_APP_NAME} \
             $RPM_BUILD_ROOT%{_includedir}/${INTERNAL_APP_NAME}
%{__install} -p -d dist/sdk/include $RPM_BUILD_ROOT%{_includedir}/${INTERNAL_APP_NAME}
%{__install} -p -d dist/sdk/idl $RPM_BUILD_ROOT%{_datadir}/idl/${INTERNAL_APP_NAME}
%{__install} -p dist/sdk/bin/* $RPM_BUILD_ROOT/$MOZ_APP_DIR
%{__install} -p dist/sdk/lib/* $RPM_BUILD_ROOT/$MOZ_APP_DIR

%{__mkdir_p} $RPM_BUILD_ROOT{%{_libdir},%{_bindir},%{_datadir}/applications}

#%{__install} -p -D %{SOURCE22} $RPM_BUILD_ROOT%{_datadir}/pixmaps/%{name}.png

#desktop-file-install --vendor mozilla \
#  --dir $RPM_BUILD_ROOT%{_datadir}/applications \
#  --add-category WebBrowser \
#  --add-category Network \
#  %{SOURCE20} 

%if 0
# set up the xulrunner start script
%{__cat} %{SOURCE21} | %{__sed} -e 's,FIREFOX_VERSION,%{version},g' > \
  $RPM_BUILD_ROOT%{_bindir}/xulrunner
%{__chmod} 755 $RPM_BUILD_ROOT%{_bindir}/xulrunner
%endif

# set up our default preferences
%{__cat} %{SOURCE12} | %{__sed} -e 's,RPM_VERREL,%{version}-%{release},g' > rh-default-prefs
%{__cp} rh-default-prefs $RPM_BUILD_ROOT/${MOZ_APP_DIR}/defaults/pref/all-redhat.js
%{__rm} rh-default-prefs

# set up our default bookmarks
%{__rm} -f $RPM_BUILD_ROOT${MOZ_APP_DIR}/defaults/profile/bookmarks.html
ln -s %{default_bookmarks_file} $RPM_BUILD_ROOT${MOZ_APP_DIR}/defaults/profile/bookmarks.html

%{__cat} %{SOURCE50} | %{__sed} -e "s,FFDIR,${MOZ_APP_DIR},g" -e 's,LIBDIR,%{_libdir},g' > \
  $RPM_BUILD_ROOT${MOZ_APP_DIR}/firefox-xremote-client

%{__chmod} 755 $RPM_BUILD_ROOT${MOZ_APP_DIR}/firefox-xremote-client
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
install -c -m 644 build/unix/*.pc \
  $RPM_BUILD_ROOT/%{_libdir}/pkgconfig
%endif

# GRE stuff
%ifarch x86_64 ia64 ppc64 s390x
%define gre_conf_file gre64.conf
%else
%define gre_conf_file gre.conf
%endif

%{__mkdir_p} $RPM_BUILD_ROOT/etc/gre.d/
%{__cat} > $RPM_BUILD_ROOT/etc/gre.d/%{gre_conf_file} << EOF
[%{version}]
GRE_PATH=${MOZ_APP_DIR}
EOF

# Copy over the LICENSE
install -c -m 644 LICENSE $RPM_BUILD_ROOT${MOZ_APP_DIR}

# ghost files
touch $RPM_BUILD_ROOT${MOZ_APP_DIR}/components/compreg.dat
touch $RPM_BUILD_ROOT${MOZ_APP_DIR}/components/xpti.dat

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
%exclude %{_bindir}/xulrunner-config
%{_datadir}/pixmaps/%{name}.png
%{_mandir}/man1/*
%{_libdir}/mozilla
%dir /etc/gre.d
/etc/gre.d/%{gre_conf_file}

%dir %{_libdir}/%{name}-*
%{_libdir}/%{name}-*/LICENSE
%{_libdir}/%{name}-*/chrome
%{_libdir}/%{name}-*/dictionaries
%dir %{_libdir}/%{name}-*/components
%ghost %{_libdir}/%{name}-*/components/compreg.dat
%ghost %{_libdir}/%{name}-*/components/xpti.dat
%{_libdir}/%{name}-*/components/*.so
%{_libdir}/%{name}-*/components/*.xpt
%{_libdir}/%{name}-*/components/*.js
%{_libdir}/%{name}-*/crashreporter
%{_libdir}/%{name}-*/defaults
%{_libdir}/%{name}-*/greprefs
%{_libdir}/%{name}-*/icons
%{_libdir}/%{name}-*/modules
%{_libdir}/%{name}-*/plugins
%{_libdir}/%{name}-*/res
%{_libdir}/%{name}-*/*.so
%{_libdir}/%{name}-*/firefox-xremote-client
%{_libdir}/%{name}-*/mozilla-xremote-client
%{_libdir}/%{name}-*/run-mozilla.sh
%{_libdir}/%{name}-*/regxpcom
%{_libdir}/%{name}-*/xulrunner-bin
%{_libdir}/%{name}-*/xulrunner-stub

# XXX See if these are needed still
%{_libdir}/%{name}-*/updater*

%if %{build_devel_package}
%files devel
%defattr(-,root,root)
%{_datadir}/idl/%{name}-*
%{_includedir}/%{name}-*
%{_libdir}/%{name}-*/xpcshell
%{_libdir}/%{name}-*/xpicleanup
%{_libdir}/%{name}-*/xpidl
%{_libdir}/%{name}-*/xpt_dump
%{_libdir}/%{name}-*/xpt_link
%{_libdir}/pkgconfig/%{name}-xpcom.pc
%{_libdir}/pkgconfig/%{name}-plugin.pc
%{_libdir}/pkgconfig/%{name}-js.pc
%exclude %{_libdir}/pkgconfig/%{name}-nspr.pc
%exclude %{_libdir}/pkgconfig/%{name}-nss.pc
%endif

#---------------------------------------------------------------------

%changelog
* Wed Sep  5 2007 Christopher Aillon <caillon@redhat.com> 1.9-0.alpha7.1
- Initial cut at XULRunner 1.9 Alpha 7
