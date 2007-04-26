#include <stdio.h>
#include <stdlib.h>
#include <errno.h>
#include <unistd.h>
#include <dirent.h>
#include <fcntl.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <X11/Xlib.h>
#include <X11/Xauth.h>

#include "xauth.h"

int
handle_xauth( char *cookie , char *servername)
{
  char hostname[BSIZE];
  char displayname[BSIZE];
  Display* displ;
  int found = 0, i;
  char cmd[BSIZE];

#ifdef DEBUG
  fprintf( stderr, "handle_auth() cookie=%s server=%s\n" ,cookie, servername );
#endif

    if ( strcmp (servername, "") == 0 )
       gethostname(hostname, BSIZE);
    else
       sprintf(hostname, "%s" ,servername);

    sprintf ( (char*) cmd, "xauth -f /tmp/.tmpxauth add %s:0 MIT-MAGIC-COOKIE-1 %s", hostname, cookie);

#ifdef DEBUG
    fprintf( stderr, "handle_xauth() cmd=\"%s\"\n", cmd );
#endif

    unlink("/tmp/.tmpxauth");
    system(cmd);

    setenv("XAUTHORITY", "/tmp/.tmpxauth", 1);          /* for XOpenDisplay */

#ifdef DEBUG
    fprintf ( stderr, "handle_xauth() XAUTHORITY=%s \n", getenv("XAUTHORITY")  );
#endif

    for (i = 0; i < 1; i++) {
      sprintf(displayname, "%s:%d", hostname, i);               /* displayify it */

#ifdef DEBUG
      printf( "handle_xauth() trying to connect to %s\n", displayname );
#endif

      displ = XOpenDisplay(displayname);

      if (displ) {
        found++;
        XCloseDisplay(displ);                           /* close display */
        break;
      }
    } /* end of for */

    unlink(XauFileName());                              /* delete file */

    if (!found) {
#ifdef DEBUG
      fprintf ( stderr, "error openning DISPLAY \n" );
#endif
      return(XAUTH_ERROR);
    }
  
#ifdef DEBUG
  fprintf ( stderr, "handle_xauth() AUTH ok.\n" );
#endif
  return(XAUTH_OK);
}



static xmlrpc_value *
tcos_xauth(xmlrpc_env *env, xmlrpc_value *in, void *ud)
 {
  char *cookie;
  char *hostname;
  int xauth_ok;
  

  /* read what option and cmdline params need */
  xmlrpc_parse_value(env, in, "(ss)", &cookie, &hostname);
  if (env->fault_occurred)
        return xmlrpc_build_value(env, "s", "params error");

   /* need login first */
  xauth_ok=handle_xauth(cookie,hostname);
  if( xauth_ok != XAUTH_OK )
    return xmlrpc_build_value(env, "s", "xauth: access denied" );

  return xmlrpc_build_value(env, "s", "xauth: access OK " );
}






/*
int main( int argc, char **argv ) {
  if(argc != 3) {
    printf( "Need 2 arguments, first cookie, last hostname to connect.\n" );
    return(1);
  }
  printf ( "main() argv=%s\n" , argv[1] );
  printf( "handle_auth()  cookie=%s hostname=%s\n" , argv[1] , argv[2] );
  handle_xauth( argv[1] , argv[2] );
  return(0);
}
*/
