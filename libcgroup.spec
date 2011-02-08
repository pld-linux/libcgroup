Summary:	Tools and library to control and monitor control groups
Summary(pl.UTF-8):	Narzędzia i biblioteka do kontrolowania i monitorowania grup kontroli
Name:		libcgroup
Version:	0.37
Release:	2
License:	LGPL v2+
Group:		Libraries
Source0:	http://downloads.sourceforge.net/libcg/%{name}-%{version}.tar.bz2
# Source0-md5:	beecca8770155afa62981076e96d4c9c
Source1:	cgconfig.init
Source2:	cgred.init
URL:		http://libcg.sourceforge.net/
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libstdc++-devel
BuildRequires:	pam-devel
Requires(post):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires:	procps
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_exec_prefix	%{nil}
%define		_libdir		%{_prefix}/%{_lib}

%description
Control groups infrastructure. The tools and library help manipulate,
control, administrate and monitor control groups and the associated
controllers.

%description -l pl.UTF-8
Ten pakiet stanowi infrastrukturę grup kontroli (cgroups). Narzędzia i
biblioteka pomagają modyfikować, sterować, administrować i
modyfikować grupy kontroli i powiązane z nimi kontrolery.

%package devel
Summary:	Header files for cgroup library
Summary(pl.UTF-8):	Pliki nagłówkowe biblioteki cgroup
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
It provides API to create/delete and modify cgroup nodes. It will also
in the future allow creation of persistent configuration for control
groups and provide scripts to manage that configuration.

%description devel -l pl.UTF-8
Ten pakiet udostępnia API do tworzenia, usuwania i modyfikowania
węzłów cgroup. W przyszłości pozwoli także na tworzenie trwałej
konfiguracji grup kontroli i udostępni skrypty do zarządzania taką
konfiguracją.

%package -n pam-pam_cgroup
Summary:	PAM module for libcgroup
Summary(pl.UTF-8):	Moduł PAM dla libcgroup
Group:		Libraries
Requires:	%{name} = %{version}-%{release}
Obsoletes:	libcgroup-pam

%description -n pam-pam_cgroup
PAM module for libcgroup.

%description -n pam-pam_cgroup -l pl.UTF-8
Moduł PAM dla libcgroup.

%prep
%setup -q

%build
%configure \
	--disable-silent-rules \
	--enable-initscript-install \
	--enable-pam-module-dir=/%{_lib}/security

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/sysconfig

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/cgconfig
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/cgred

cp -a samples/cgred.conf $RPM_BUILD_ROOT/etc/sysconfig/cgred.conf
cp -a samples/cgconfig.sysconfig $RPM_BUILD_ROOT/etc/sysconfig/cgconfig
cp -a samples/cg{config,rules,snapshot_blacklist}.conf $RPM_BUILD_ROOT%{_sysconfdir}

mv -f $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so{.*.*.*,}
mv $RPM_BUILD_ROOT%{_libdir}/libcgroup.so.* $RPM_BUILD_ROOT/%{_lib}
ln -snf ../../%{_lib}/$(basename $RPM_BUILD_ROOT/%{_lib}/libcgroup.so.*.*.*) $RPM_BUILD_ROOT%{_libdir}/libcgroup.so

%{__rm} $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so.*
%{__rm} $RPM_BUILD_ROOT{/%{_lib}/security,%{_libdir}}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

#%%pre
#getent group cgred >/dev/null || groupadd cgred

%post
/sbin/ldconfig
/sbin/chkconfig --add cgred
/sbin/chkconfig --add cgconfig

%preun
if [ $1 = 0 ]; then
	%service cgred stop
	%service cgconfig stop
	/sbin/chkconfig --del cgconfig
	/sbin/chkconfig --del cgred
fi

%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc README README_daemon
%attr(754,root,root) /etc/rc.d/init.d/cg*
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cg*
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cg*.conf

%attr(755,root,root) /bin/cg*
%attr(755,root,root) /bin/lscgroup
%attr(755,root,root) /bin/lssubsys
%attr(755,root,root) /sbin/cg*

%attr(755,root,root) /%{_lib}/libcgroup.so.*.*.*
%attr(755,root,root) %ghost /%{_lib}/libcgroup.so.1

%{_mandir}/man1/ls*.1*
%{_mandir}/man1/cg*.1*
%{_mandir}/man5/cg*.5*
%{_mandir}/man8/cg*.8*

%files -n pam-pam_cgroup
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/security/pam_cgroup.so

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcgroup.so
%{_includedir}/libcgroup
%{_includedir}/libcgroup.h
%{_pkgconfigdir}/libcgroup.pc
