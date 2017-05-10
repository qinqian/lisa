O=bPlusTree.o bbiRead.o bbiWrite.o bits.o cirTree.o common.o dystring.o hash.o localmem.o udc.o portimpl.o memalloc.o dlist.o linefile.o pipeline.o verbose.o options.o net.o internet.o https.o base64.o errAbort.o osunix.o hmmstats.o cheapcgi.o mime.o obscure.o hex.o wildcmp.o intExp.o kxTok.o servBrcMcw.o servcl.o servCrunx.o servcis.o servmsII.o servpws.o zlibFace.o sqlNum.o bwgQuery.o


CC=gcc
ifeq (${MACHTYPE},)
    MACHTYPE:=$(shell uname -m)
    #MACHTYPE:=$(shell arch)
#    $(info MACHTYPE was empty, set to: ${MACHTYPE})
endif
ifneq (,$(findstring -,$(MACHTYPE)))
#    $(info MACHTYPE has - sign ${MACHTYPE})
    MACHTYPE:=$(shell uname -m)
#    $(info MACHTYPE has - sign set to: ${MACHTYPE})
endif

HG_DEFS=-D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -D_GNU_SOURCE -DMACHTYPE_${MACHTYPE}
#HG_DEFS=-D_FILE_OFFSET_BITS=64 -D_LARGEFILE_SOURCE -D_GNU_SOURCE 
HG_INC=-I../inc -I../../inc -I../../../inc -I../../../../inc -I../../../../../inc

# to check for Mac OSX Darwin specifics:
UNAME_S := $(shell uname -s)
# to check for builds on hgwdev
FULLWARN = $(shell uname -n)

# autodetect if openssl is installed
ifeq (${SSLDIR},)
  SSLDIR = /usr/include/openssl
endif
ifeq (${USE_SSL},)
  ifneq ($(wildcard ${SSLDIR}),)
     USE_SSL=1
  endif
endif


# libssl: disabled by default
ifeq (${USE_SSL},1)
    ifneq (${SSL_DIR}, "/usr/include/openssl")
      ifneq ($(UNAME_S),Darwin)
        L+=-L${SSL_DIR}/lib
      endif
        HG_INC+=-I${SSL_DIR}/include
    endif
    # on hgwdev, already using the static library with mysqllient.
    ifeq (${FULLWARN},hgwdev)
       L+=/usr/lib64/libssl.a /usr/lib64/libcrypto.a -lkrb5
    else
       L+=-lssl -lcrypto
    endif
    HG_DEFS+=-DUSE_SSL
endif

# pass through COREDUMP
ifneq (${COREDUMP},)
    HG_DEFS+=-DCOREDUMP
endif


SYS = $(shell uname -s)
#SYS = $(shell arch)

ifeq (${HG_WARN},)
  ifeq (${SYS},Darwin)
      HG_WARN = -Wall -Wno-unused-variable -Wno-deprecated-declarations
      HG_WARN_UNINIT=
  else
    ifeq (${SYS},SunOS)
      HG_WARN = -Wall -Wformat -Wimplicit -Wreturn-type
      HG_WARN_UNINIT=-Wuninitialized
    else
      ifeq (${FULLWARN},hgwdev)
        HG_WARN = -Wall -Werror -Wformat -Wformat-security -Wimplicit -Wreturn-type -Wempty-body
        HG_WARN_UNINIT=-Wuninitialized
      else
        HG_WARN = -Wall -Wformat -Wimplicit -Wreturn-type
        HG_WARN_UNINIT=-Wuninitialized
      endif
    endif
  endif
  # -Wuninitialized generates a warning without optimization
  ifeq ($(findstring -O,${COPT}),-O)
     HG_WARN += ${HG_WARN_UNINIT}
  endif
endif

# this is to hack around many make files not including HG_WARN in
# the link line
CFLAGS += ${HG_WARN}

ifeq (${SCRIPTS},)
    SCRIPTS=${HOME}/bin/scripts
endif

# avoid an extra leading slash when DESTDIR is empty
ifeq (${DESTDIR},)
  DESTBINDIR=${BINDIR}
else
  DESTBINDIR=${DESTDIR}/${BINDIR}
endif


MKDIR=mkdir -p
ifeq (${STRIP},)
   STRIP=true
endif
CVS=cvs
GIT=git

# portable naming of compiled executables: add ".exe" if compiled on 
# Windows (with cygwin).
ifeq (${OS}, Windows_NT)
  AOUT=a
  EXE=.exe
else
  AOUT=a.out
  EXE=
endif


%.o: %.c
	${CC} ${COPT} ${CFLAGS} ${HG_DEFS} ${LOWELAB_DEFS} ${HG_WARN} ${HG_INC} ${XINC} -o $@ -c $<

#$(MACHTYPE)/libjkweb.so: $(O)
libjkweb.so: $(O)
	$(CC) $(O) -dynamiclib -o libjkweb.so -lm -lssl -lz  -lcrypto

# jshint: off unless JSHINT is already in environment
ifeq (${JSHINT},)
    JSHINT=true
endif

