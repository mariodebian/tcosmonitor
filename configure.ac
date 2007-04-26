#                                               -*- Autoconf -*-
# Process this file with autoconf to produce a configure script.

AC_PREREQ(2.60a)
AC_INIT(TcosMonitor, 0.0.15, mariodebian (at) gmail (dot) com)
AC_CONFIG_SRCDIR([xmlrpc/tcosxmlrpc.c])
AC_CONFIG_HEADER([config.h.in])

# Checks for programs.
AC_PROG_AWK
AC_PROG_CC
AC_PROG_INSTALL
AC_PROG_MAKE_SET

# Checks for libraries.
# FIXME: Replace `main' with a function in `-lX11':
AC_CHECK_LIB([X11], [main])
# FIXME: Replace `main' with a function in `-lXaw':
AC_CHECK_LIB([Xaw], [main])
# FIXME: Replace `main' with a function in `-lcrypt':
AC_CHECK_LIB([crypt], [main])

# Checks for header files.
AC_PATH_X
AC_HEADER_DIRENT
AC_HEADER_STDC
AC_CHECK_HEADERS([fcntl.h shadow.h stdlib.h string.h strings.h unistd.h])

# Checks for typedefs, structures, and compiler characteristics.
AC_C_CONST
AC_TYPE_SIZE_T

# Checks for library functions.
AC_FUNC_MEMCMP
AC_CHECK_FUNCS([gethostname getpass getspnam setenv strstr strtol])

AC_CONFIG_FILES([Makefile
                 busybox/Makefile
                 dbus/Makefile
                 lockscreen/Makefile
                 udev/Makefile
                 xmlrpc/Makefile
                 xmlrpc/md5/Makefile])
AC_OUTPUT
