# TODO
# - pldize initscripts
Summary:	Tools and libraries to control and monitor control groups
Name:		libcgroup
Version:	0.36.1
Release:	1
License:	LGPL v2+
Group:		Development/Libraries
Source0:	http://downloads.sourceforge.net/libcg/%{name}-%{version}.tar.bz2
# Source0-md5:	f8d842cdf9f80a64588870b706130191
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
%define		_libdir			%{_prefix}/%{_lib}

%description
Control groups infrastructure. The tools and library help manipulate,
control, administrate and monitor control groups and the associated
controllers.

%package devel
Summary:	Development libraries to develop applications that utilize control groups
Group:		Development/Libraries
Requires:	%{name} = %{version}-%{release}

%description devel
It provides API to create/delete and modify cgroup nodes. It will also
in the future allow creation of persistent configuration for control
groups and provide scripts to manage that configuration.

%prep
%setup -q

%build
%configure
%{__make}

%install
rm -rf $RPM_BUILD_ROOT
%{__make} install \
	DESTDIR=$RPM_BUILD_ROOT

# install init scripts
install -d $RPM_BUILD_ROOT/etc/rc.d/init.d
cp scripts/init.d/cgconfig $RPM_BUILD_ROOT/etc/rc.d/init.d/cgconfig
cp scripts/init.d/cgred $RPM_BUILD_ROOT/etc/rc.d/init.d/cgred

# install config files
install -d $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig
cp samples/cgred.conf $RPM_BUILD_ROOT%{_sysconfdir}/sysconfig/cgred.conf
cp samples/cgconfig.conf $RPM_BUILD_ROOT%{_sysconfdir}/cgconfig.conf
cp samples/cgrules.conf $RPM_BUILD_ROOT%{_sysconfdir}/cgrules.conf

# sanitize pam module, we need only pam_cgroup.so in the right directory
install -d $RPM_BUILD_ROOT/%{_lib}/security
mv -f $RPM_BUILD_ROOT%{_libdir}/pam_cgroup.so.*.*.* $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so
rm -f $RPM_BUILD_ROOT%{_libdir}/pam_cgroup*

# move library to /%{_lib}
install -d $RPM_BUILD_ROOT/%{_lib}
mv $RPM_BUILD_ROOT%{_libdir}/libcgroup.so.* $RPM_BUILD_ROOT/%{_lib}
ln -snf ../../%{_lib}/$(basename $RPM_BUILD_ROOT/%{_lib}/libcgroup.so.*.*.*) $RPM_BUILD_ROOT%{_libdir}/libcgroup.so

%clean
rm -rf $RPM_BUILD_ROOT

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
%doc INSTALL README_daemon
%config(noreplace) %{_sysconfdir}/cgconfig.conf
%config(noreplace) %{_sysconfdir}/cgrules.conf
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cgred.conf

%attr(755,root,root) /bin/cgclassify
%attr(755,root,root) /bin/cgcreate
%attr(755,root,root) /bin/cgdelete
%attr(755,root,root) /bin/cgexec
%attr(755,root,root) /bin/cgget
%attr(755,root,root) /bin/cgset
%attr(755,root,root) /bin/lscgroup
%attr(755,root,root) /bin/lssubsys
%attr(755,root,root) /sbin/cgclear
%attr(755,root,root) /sbin/cgconfigparser
%attr(755,root,root) /sbin/cgrulesengd

%attr(754,root,root) /etc/rc.d/init.d/cgconfig
%attr(754,root,root) /etc/rc.d/init.d/cgred
%attr(755,root,root) /%{_lib}/libcgroup.so.*.*.*
%attr(755,root,root) %ghost /%{_lib}/libcgroup.so.?
%attr(755,root,root) /%{_lib}/security/pam_cgroup.so

%{_mandir}/man1/cgclassify.1*
%{_mandir}/man1/cgclear.1*
%{_mandir}/man1/cgcreate.1*
%{_mandir}/man1/cgget.1*
%{_mandir}/man1/cgset.1*
%{_mandir}/man1/cgexec.1*
%{_mandir}/man5/cgconfig.conf.5*
%{_mandir}/man5/cgred.conf.5*
%{_mandir}/man5/cgrules.conf.5*
%{_mandir}/man8/cgconfigparser.8*
%{_mandir}/man8/cgrulesengd.8*

%files devel
%defattr(644,root,root,755)
%doc INSTALL
%attr(755,root,root) %{_libdir}/libcgroup.so
%{_libdir}/libcgroup.la
%{_includedir}/libcgroup.h
%{_includedir}/libcgroup
%{_pkgconfigdir}/libcgroup.pc
