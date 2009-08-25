%define soversion 1.0.34

Summary:	Tools and libraries to control and monitor control groups
Name:		libcgroup
Version:	0.34
Release:	1
License:	LGPLv2+
Group:		Development/Libraries
Source0:	http://dl.sourceforge.net/libcg/%{name}-%{version}.tar.bz2
# Source0-md5:	681c751d1a1ea78615094007d39db6cb
URL:		http://libcg.sourceforge.net/
BuildRequires:	flex
BuildRequires:	pam-devel
Requires(post):	chkconfig, /sbin/service
Requires(preun):	/sbin/chkconfig
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Control groups infrastructure. The tools and library help manipulate,
control, administrate and monitor control groups and the associated
controllers.

%package devel
Summary:	Development libraries to develop applications that utilize control groups
Group:		Development/Libraries
Requires:	libcgroup = %{version}-%{release}

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
install -d $RPM_BUILD_ROOT/%{_initrddir}
cp scripts/init.d/cgconfig $RPM_BUILD_ROOT/%{_initrddir}/cgconfig
cp scripts/init.d/cgred $RPM_BUILD_ROOT/%{_initrddir}/cgred

# install config files
install -d $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig
cp samples/cgred.conf $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/cgred.conf
cp samples/cgconfig.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgconfig.conf
cp samples/cgrules.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgrules.conf

# sanitize pam module, we need only pam_cgroup.so in the right directory
install -d $RPM_BUILD_ROOT/%{_lib}/security
mv -f $RPM_BUILD_ROOT/%{_lib}/pam_cgroup.so.*.*.* $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so
rm -f $RPM_BUILD_ROOT/%{_lib}/pam_cgroup*

# move the devel stuff to %{_prefix}
install -d $RPM_BUILD_ROOT/%{_libdir}
mv -f $RPM_BUILD_ROOT/%{_lib}/libcgroup.la $RPM_BUILD_ROOT/%{_libdir}
rm -f $RPM_BUILD_ROOT/%{_lib}/libcgroup.so
ln -sf ../../%{_lib}/libcgroup.so.%{soversion} $RPM_BUILD_ROOT/%{_libdir}/libcgroup.so

%clean
rm -rf $RPM_BUILD_ROOT

%post
/sbin/ldconfig
/sbin/chkconfig --add cgred
/sbin/chkconfig --add cgconfig

%preun
if [ $1 = 0 ]; then
    %service cgred stop > /dev/null 2>&1 || :
    %service cgconfig stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del cgconfig
    /sbin/chkconfig --del cgred
fi

%postun -p /sbin/ldconfig

%files
%defattr(644,root,root,755)
%doc INSTALL README_daemon
%config(noreplace) %verify(not md5 mtime size) /etc/sysconfig/cgred.conf
%config(noreplace) %{_sysconfdir}/cgconfig.conf
%config(noreplace) %{_sysconfdir}/cgrules.conf
%attr(755,root,root) /%{_lib}/libcgroup.so.*
/bin/cgexec
/bin/cgclassify
/sbin/cgconfigparser
/sbin/cgrulesengd
%attr(644, root, root) %{_mandir}/man1/*
%attr(644, root, root) %{_mandir}/man5/*
%attr(644, root, root) %{_mandir}/man8/*
%attr(755,root,root) %{_initrddir}/cgconfig
%attr(755,root,root) %{_initrddir}/cgred
%attr(755,root,root) /%{_lib}/security/pam_cgroup.so

%files devel
%defattr(644,root,root,755)
%{_includedir}/libcgroup.h
%{_libdir}/libcgroup.*
%doc INSTALL
