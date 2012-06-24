%define soversion 1.0.34

Name: libcgroup
Summary: Tools and libraries to control and monitor control groups
Group: Development/Libraries
Version: 0.34
Release:        1
License: LGPLv2+
URL: http://libcg.sourceforge.net/
Source0: http://downloads.sourceforge.net/libcg/%{name}-%{version}.tar.bz2
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildRequires: pam-devel
BuildRequires: byacc
BuildRequires: flex
BuildRequires: coreutils
Requires(post): chkconfig, /sbin/service
Requires(preun): /sbin/chkconfig

%description
Control groups infrastructure. The tools and library help manipulate, control,
administrate and monitor control groups and the associated controllers.

%package devel
Summary: Development libraries to develop applications that utilize control groups
Group: Development/Libraries
Requires: libcgroup = %{version}-%{release}

%description devel
It provides API to create/delete and modify cgroup nodes. It will also in the
future allow creation of persistent configuration for control groups and
provide scripts to manage that configuration.

%prep
%setup -q

%build
%configure --bindir=/bin --sbindir=/sbin --libdir=/%{_lib}

make %{?_smp_mflags}


%install
rm -rf $RPM_BUILD_ROOT
make DESTDIR=$RPM_BUILD_ROOT install

# install init scripts
mkdir -p $RPM_BUILD_ROOT/%{_initrddir}
cp scripts/init.d/cgconfig $RPM_BUILD_ROOT/%{_initrddir}/cgconfig
cp scripts/init.d/cgred $RPM_BUILD_ROOT/%{_initrddir}/cgred

# install config files
mkdir -p $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig
cp samples/cgred.conf $RPM_BUILD_ROOT/%{_sysconfdir}/sysconfig/cgred.conf
cp samples/cgconfig.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgconfig.conf
cp samples/cgrules.conf $RPM_BUILD_ROOT/%{_sysconfdir}/cgrules.conf

# sanitize pam module, we need only pam_cgroup.so in the right directory
mkdir -p $RPM_BUILD_ROOT/%{_lib}/security
mv -f $RPM_BUILD_ROOT/%{_lib}/pam_cgroup.so.*.*.* $RPM_BUILD_ROOT/%{_lib}/security/pam_cgroup.so
rm -f $RPM_BUILD_ROOT/%{_lib}/pam_cgroup*

# move the devel stuff to /usr
mkdir -p $RPM_BUILD_ROOT/%{_libdir}
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
    /sbin/service cgred stop > /dev/null 2>&1 || :
    /sbin/service cgconfig stop > /dev/null 2>&1 || :
    /sbin/chkconfig --del cgconfig
    /sbin/chkconfig --del cgred
fi

%postun -p /sbin/ldconfig

%files 
%defattr(-,root,root,-)
%config(noreplace) %{_sysconfdir}/sysconfig/cgred.conf
%config(noreplace) %{_sysconfdir}/cgconfig.conf
%config(noreplace) %{_sysconfdir}/cgrules.conf
/%{_lib}/libcgroup.so.*
/bin/cgexec
/bin/cgclassify
/sbin/cgconfigparser
/sbin/cgrulesengd
%attr(0644, root, root) %{_mandir}/man1/*
%attr(0644, root, root) %{_mandir}/man5/*
%attr(0644, root, root) %{_mandir}/man8/*
%attr(0755,root,root) %{_initrddir}/cgconfig
%attr(0755,root,root) %{_initrddir}/cgred
%attr(0755,root,root) /%{_lib}/security/pam_cgroup.so

%doc COPYING INSTALL README_daemon

%files devel
%defattr(-,root,root,-)
%{_includedir}/libcgroup.h
%{_libdir}/libcgroup.*
%doc COPYING INSTALL 


%changelog
* Tue Feb 24 2009 Balbir Singh <balbir@linux.vnet.ibm.com> 0.33-1
- Update to 0.33, spec file changes to add Makefiles and pam_cgroup module
* Fri Oct 10 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.32-1
- Update to latest upstream
* Thu Sep 11 2008 Dhaval Giani <dhaval@linux-vnet.ibm.com> 0.31-1
- Update to latest upstream
* Sat Aug 2 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.1c-3
- Change release to fix broken upgrade path
* Wed Jun 11 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.1c-1
- Update to latest upstream version
* Tue Jun 3 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1b-3
- Add post and postun. Also fix Requires for devel to depend on base n-v-r
* Sat May 31 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1b-2
- Fix makeinstall, Source0 and URL (review comments from Tom)
* Mon May 26 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1b-1
- Add a generatable spec file
* Tue May 20 2008 Balbir Singh <balbir@linux.vnet.ibm.com> 0.1-1
- Get the spec file to work
* Tue May 20 2008 Dhaval Giani <dhaval@linux.vnet.ibm.com> 0.01-1
- The first version of libcg
