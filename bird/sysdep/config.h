/*
 *	This file contains all parameters dependent on the
 *	operating system and build-time configuration.
 */

#ifndef _BIRD_CONFIG_H_
#define _BIRD_CONFIG_H_

/* BIRD version */
#define BIRD_VERSION "1.3.4"

/* Include parameters determined by configure script */
#include "sysdep/autoconf.h"

/* Include OS configuration file as chosen in autoconf.h */
#include SYSCONF_INCLUDE

#ifndef MACROS_ONLY

/*
 *  Of course we could add the paths to autoconf.h, but autoconf
 *  is stupid and puts make-specific substitutious to the paths.
 */
#include "sysdep/paths.h"

/* Types */
typedef signed INTEGER_8 s8;
typedef unsigned INTEGER_8 u8;
typedef INTEGER_16 s16;
typedef unsigned INTEGER_16 u16;
typedef INTEGER_32 s32;
typedef unsigned INTEGER_32 u32;
typedef INTEGER_64 s64;
typedef unsigned INTEGER_64 u64;
typedef u8 byte;
typedef u16 word;

#endif

/* Path to configuration file */
#ifdef IPV6
#  ifdef DEBUGGING
#    define PATH_CONFIG "bird6.conf"
#    define PATH_CONTROL_SOCKET "bird6.ctl"
#  else
#    define PATH_CONFIG PATH_CONFIG_DIR "/bird6.conf"
#    define PATH_CONTROL_SOCKET PATH_CONTROL_SOCKET_DIR "/bird6.ctl"
#  endif
#else
#  ifdef DEBUGGING
#    define PATH_CONFIG "bird.conf"
#    define PATH_CONTROL_SOCKET "bird.ctl"
#  else
#    define PATH_CONFIG PATH_CONFIG_DIR "/bird.conf"
#    define PATH_CONTROL_SOCKET PATH_CONTROL_SOCKET_DIR "/bird.ctl"
#  endif
#endif

#endif
