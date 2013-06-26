%define	rcver	rc1
Summary:	Tools and library to control and monitor control groups
Summary(pl.UTF-8):	Narzędzia i biblioteka do kontrolowania i monitorowania grup kontroli
Name:		libcgroup
Version:	0.40
Release:	0.%{rcver}.2
License:	LGPL v2+
Group:		Libraries
Source0:	http://downloads.sourceforge.net/libcg/%{name}-%{version}.%{rcver}.tar.bz2
# Source0-md5:	979624adc559f534b34099f4dba7576d
Source1:	cgconfig.init
Source2:	cgred.init
Source3:	cgconfig.service
Source4:	cgred.service
Source5:	cgred.sysconfig
Patch0:		%{name}-pam.patch
Patch1:		%{name}-conf.patch
URL:		http://libcg.sourceforge.net/
BuildRequires:	autoconf >= 2.61
BuildRequires:	automake
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libstdc++-devel
BuildRequires:	libtool
BuildRequires:	pam-devel
BuildRequires:	rpmbuild(macros) >= 1.626
Requires(post):	/sbin/ldconfig
Requires(post,preun):	/sbin/chkconfig
Requires(postun):	/usr/sbin/groupdel
Requires(pre):	/usr/bin/getgid
Requires(pre):	/usr/sbin/groupadd
Requires(post,preun,postun):	systemd-units >= 38
Requires:	procps
Requires:	rc-scripts
Requires:	systemd-units >= 38
Provides:	group(cgred)
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_exec_prefix	%{nil}
%define		_libdir		%{_prefix}/%{_lib}

%description
Control groups infrastructure. The tools and library help manipulate,
control, administrate and monitor control groups and the associated
controllers.

%description -l pl.UTF-8
Ten pakiet stanowi infrastrukturę grup kontroli (cgroups). Narzędzia i
biblioteka pomagają modyfikować, sterować, administrować i modyfikować
grupy kontroli i powiązane z nimi kontrolery.

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
%setup -q -n %{name}-%{version}.%{rcver}
%patch0 -p1
%patch1 -p1

%build
%{__libtoolize}
%{__aclocal}
%{__autoconf}
%{__automake}
%configure \
	--disable-silent-rules \
	--enable-initscript-install \
	--enable-pam-module-dir=/%{_lib}/security \
	--enable-opaque-hierarchy="name=systemd"

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{/etc/sysconfig,%{systemdunitdir}}

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

install %{SOURCE1} $RPM_BUILD_ROOT/etc/rc.d/init.d/cgconfig
install %{SOURCE2} $RPM_BUILD_ROOT/etc/rc.d/init.d/cgred

install %{SOURCE3} $RPM_BUILD_ROOT%{systemdunitdir}/cgconfig.service
install %{SOURCE4} $RPM_BUILD_ROOT%{systemdunitdir}/cgred.service

install %{SOURCE5} $RPM_BUILD_ROOT/etc/sysconfig/cgred
cp -a samples/cg{config,rules,snapshot_blacklist}.conf $RPM_BUILD_ROOT%{_sysconfdir}

mv $RPM_BUILD_ROOT%{_libdir}/libcgroup.so.* $RPM_BUILD_ROOT/%{_lib}
ln -snf ../../%{_lib}/$(basename $RPM_BUILD_ROOT/%{_lib}/libcgroup.so.*.*.*) $RPM_BUILD_ROOT%{_libdir}/libcgroup.so

%{__rm} $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.la
%{__rm} $RPM_BUILD_ROOT%{_libdir}/*.la

%clean
rm -rf $RPM_BUILD_ROOT

%pre
%groupadd -g 261 -r -f cgred

%post
/sbin/ldconfig
/sbin/chkconfig --add cgred
/sbin/chkconfig --add cgconfig
if [ ! -f /var/lock/subsys/cgconfig ]; then
	echo 'Run "/sbin/service cgconfig start" to setup cgroup rules.'
fi
if [ ! -f /var/lock/subsys/cgred ]; then
	echo 'Run "/sbin/service cgred start" to start control group rules daemon.'
fi
NORESTART=1
%systemd_post cgconfig.service
%systemd_post cgred.service

%preun
if [ $1 = 0 ]; then
	%service cgred stop
	%service cgconfig stop
	/sbin/chkconfig --del cgconfig
	/sbin/chkconfig --del cgred
fi
%systemd_preun cgconfig.service
%systemd_preun cgred.service

%postun
/sbin/ldconfig
if [ "$1" = "0" ]; then
	%groupremove cgred
fi
%systemd_reload

%triggerpostun -- %{name} < 0.38-0.rc1.1
if [ -f /etc/sysconfig/cgred.conf.rpmsave ]; then
	. /etc/sysconfig/cgred.conf.rpmsave
	OPTIONS=
	[ -n "$NODAEMON" ] && OPTIONS="$OPTIONS $NODAEMON"
	[ -n "$LOG" ] && OPTIONS="$OPTIONS $LOG"
	if [ -n "$LOG_FILE" ]; then
		OPTIONS="$OPTIONS -f $LOG_FILE"
	else
		OPTIONS="$OPTIONS -s"
	fi
	[ -n "$SOCKET_USER" ] && OPTIONS="$OPTIONS -u $SOCKET_USER"
	if [ -n "$SOCKET_GROUP" ]; then
		OPTIONS="$OPTIONS -g $SOCKET_GROUP"
	else
		OPTIONS="$OPTIONS -g cgred"
	fi
	echo >>/etc/sysconfig/cgred
	echo "# Added by rpm trigger" >>/etc/sysconfig/cgred
	echo "OPTIONS=\"$OPTIONS\"" >>/etc/sysconfig/cgred
fi
%systemd_trigger cgconfig.service
%systemd_trigger cgred.service

%files
%defattr(644,root,root,755)
%doc README README_daemon
%attr(754,root,root) /etc/rc.d/init.d/cgconfig
%attr(754,root,root) /etc/rc.d/init.d/cgred
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cgred
%config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/cg*.conf
%{systemdunitdir}/cgconfig.service
%{systemdunitdir}/cgred.service
%attr(755,root,root) /%{_lib}/libcgroup.so.*.*.*
%attr(755,root,root) %ghost /%{_lib}/libcgroup.so.1
%attr(755,root,root) /bin/cgclassify
%attr(755,root,root) /bin/cgcreate
%attr(755,root,root) /bin/cgdelete
%attr(755,root,root) /bin/cgexec
%attr(755,root,root) /bin/cgget
%attr(755,root,root) /bin/cgset
%attr(755,root,root) /bin/cgsnapshot
%attr(755,root,root) /bin/lscgroup
%attr(755,root,root) /bin/lssubsys
%attr(755,root,root) /sbin/cgclear
%attr(755,root,root) /sbin/cgconfigparser
%attr(755,root,root) /sbin/cgrulesengd
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
