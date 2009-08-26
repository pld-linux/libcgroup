Summary:	Tools and libraries to control and monitor control groups
Name:		libcgroup
Version:	0.34
Release:	1
License:	LGPL v2+
Group:		Development/Libraries
Source0:	http://dl.sourceforge.net/libcg/%{name}-%{version}.tar.bz2
# Source0-md5:	681c751d1a1ea78615094007d39db6cb
URL:		http://libcg.sourceforge.net/
BuildRequires:	flex
BuildRequires:	pam-devel
Requires(post):	/sbin/chkconfig
Requires(post):	/sbin/ldconfig
Requires(preun):	/sbin/chkconfig
Requires:	rc-scripts
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

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
%configure \
	--bindir=/bin \
	--sbindir=/sbin \
	--libdir=/%{_lib} \

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
mv -f $RPM_BUILD_ROOT/%{_lib}/pam_cgroup.so.*.*.* $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so
rm -f $RPM_BUILD_ROOT/%{_lib}/pam_cgroup*

# move the devel stuff to %{_prefix}
install -d $RPM_BUILD_ROOT%{_libdir}
mv -f $RPM_BUILD_ROOT/%{_lib}/libcgroup.la $RPM_BUILD_ROOT%{_libdir}
rm -f $RPM_BUILD_ROOT/%{_lib}/libcgroup.so
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
%attr(754,root,root) /etc/rc.d/init.d/cgconfig
%attr(754,root,root) /etc/rc.d/init.d/cgred
%attr(755,root,root) /%{_lib}/libcgroup.so.*.*.*
%attr(755,root,root) %ghost /%{_lib}/libcgroup.so.1
%attr(755,root,root) /%{_lib}/security/pam_cgroup.so
%attr(755,root,root) /bin/cgexec
%attr(755,root,root) /bin/cgclassify
%attr(755,root,root) /sbin/cgconfigparser
%attr(755,root,root) /sbin/cgrulesengd
%{_mandir}/man1/cgclassify.1*
%{_mandir}/man1/cgexec.1*
%{_mandir}/man5/cgconfig.conf.5*
%{_mandir}/man5/cgred.conf.5*
%{_mandir}/man5/cgrules.conf.5*
%{_mandir}/man8/cgconfigparser.8*
%{_mandir}/man8/cgrulesengd.8*

%files devel
%defattr(644,root,root,755)
%doc INSTALL
%{_includedir}/libcgroup.h
%{_libdir}/libcgroup.la
%{_libdir}/libcgroup.so
