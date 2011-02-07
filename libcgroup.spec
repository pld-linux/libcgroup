# TODO
# - pldize initscripts
Summary:	Tools and libraries to control and monitor control groups
Name:		libcgroup
Version:	0.37
Release:	1
License:	LGPL v2+
Group:		Development/Libraries
Source0:	http://downloads.sourceforge.net/libcg/%{name}-%{version}.tar.bz2
# Source0-md5:	beecca8770155afa62981076e96d4c9c
URL:		http://libcg.sourceforge.net/
BuildRequires:	bison
BuildRequires:	flex
BuildRequires:	libstdc++-devel
BuildRequires:	pam-devel
Requires(post):	/sbin/chkconfig
Requires(post):	/sbin/ldconfig
Requires(preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%define		_exec_prefix	/
%define		_libdir		%{_prefix}/%{_lib}

%description
Control groups infrastructure. The tools and library help manipulate,
control, administrate and monitor control groups and the associated
controllers.

%package devel
Summary:	Development libraries for %{name}
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
It provides API to create/delete and modify cgroup nodes. It will also
in the future allow creation of persistent configuration for control
groups and provide scripts to manage that configuration.

%package pam
Summary:	PAM module for %{name}
Group:		Libraries
Requires:	%{name} = %{version}-%{release}

%description pam
PAM module for %{name}.

%prep
%setup -q

%build
%configure \
	--enable-initscript-install \
	--enable-pam-module-dir=/%{_lib}/security

%{__make}

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/etc/sysconfig

%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

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
%attr(755,root,root) %ghost /%{_lib}/libcgroup.so.?

%{_mandir}/man1/ls*.1*
%{_mandir}/man1/cg*.1*
%{_mandir}/man5/cg*.5*
%{_mandir}/man8/cg*.8*

%files pam
%defattr(644,root,root,755)
%attr(755,root,root) /%{_lib}/security/pam_cgroup.so

%files devel
%defattr(644,root,root,755)
%attr(755,root,root) %{_libdir}/libcgroup.so
%{_includedir}/libcgroup
%{_includedir}/libcgroup.h
%{_pkgconfigdir}/libcgroup.pc
