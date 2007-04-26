/*# exe.c method that exec an app 2006-09-09 14:22:40 mariodebian $
#
# This file is part of tcosxmlrpc.
#
# tcosxmlrpc is free software; you can redistribute it and/or modify
# it under the terms of the GNU Lesser General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
#
# tcosxmlrpc is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
# General Public License for more details.
#
# You should have received a copy of the GNU Lesser General Public License
# along with tcosxmlrpc; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA 02111-1307
# USA.
*/

#include <stdio.h>
int snprintf(char *str, size_t size, const char *format, ...);

#include "exe.h"


char full_path[BSIZE];


char 
*get_full_path(char *bin)
{
  FILE *fp;
  int i;
  char line[BSIZE];
  char cmd[BSIZE];
  /* clear string */
  strcpy(full_path, "");
  sprintf( cmd, "which %s", bin);
  fp =(FILE*) popen(cmd, "r");
  if(fp == NULL)
  {
     fprintf(stderr, "tcosxmlrpc::get_full_path(%s), error opening pointer\n", bin);
     return(full_path);
  }	
  fgets(line, sizeof line, fp);

  for (i = 0; i < strlen(line)-1; i++)
   {
     sprintf( full_path , "%s%c", full_path, line[i] );
   }
  #ifdef DEBUG
  fprintf(stderr, "tcosxmlrpc::get_full_path(%s)=%s\n", bin, full_path);
  #endif
  pclose(fp);
  return(full_path);
}

void 
job_exe( char *cmd )
{
  FILE *fp; 
  char job[BUFF_SIZE];

  snprintf( (char*) &job, BUFF_SIZE, "%s %s", CMD_WRAPPER, get_full_path(cmd) );

  #ifdef DEBUG
    fprintf(stderr, "xmlrpc::job_exe() exec=> \"%s\"\n", job);
  #endif


    fp=(FILE*)popen(job, "r");
    pclose(fp);
/*
  if ( system(job) == -1 )
	fprintf(stderr, "xmlrpc::job_exe() ERROR !!!\n");
*/
    #ifdef DEBUG
       fprintf(stderr, "xmlrpc::job_exe() EXEC !!!\n");
    #endif
    return;
}

void 
kill_exe( char *cmd )
{
  FILE *fp;
  char job[BUFF_SIZE];

  snprintf( (char*) &job, BUFF_SIZE, "killall %s", cmd );

  #ifdef DEBUG
    fprintf(stderr, "xmlrpc::kill_exe() exec=> \"%s\"\n", job);
  #endif

    fp=(FILE*)popen(job, "r");
    pclose(fp);
}



static xmlrpc_value *
tcos_exe(xmlrpc_env *env, xmlrpc_value *in, void *ud)
{
     char *s;
     char *user;
     char *pass;
     char *login_ok;


   #ifdef DEBUG
     fprintf(stderr, "tcosxmlrpc::tcos_exe() Init \n");
   #endif

     xmlrpc_parse_value(env, in, "(sss)", &s, &user, &pass);
     if (env->fault_occurred)
        return xmlrpc_build_value(env, "s", "error: params error");

  
  /* need login first */
  login_ok=validate_login(user,pass);
  if( strcmp(login_ok,  LOGIN_OK ) != 0 )
    return xmlrpc_build_value(env, "s", login_ok );


   #ifdef DEBUG
     fprintf(stderr, "tcosxmlrpc::tcos_exe s=\"%s\" \n", s);
   #endif

     job_exe(s);

     return xmlrpc_build_value(env, "s", s);
}


static xmlrpc_value *
tcos_kill(xmlrpc_env *env, xmlrpc_value *in, void *ud)
{
     char *s;
     char *user;
     char *pass;
     char *login_ok;

   #ifdef DEBUG
     fprintf(stderr, "tcosxmlrpc::tcos_kill() Init \n");
   #endif

     xmlrpc_parse_value(env, in, "(sss)", &s, &user, &pass);
     if (env->fault_occurred)
        return xmlrpc_build_value(env, "s", "error: params error");;

  /* need login first */
  login_ok=validate_login(user,pass);
  if( strcmp(login_ok,  LOGIN_OK ) != 0 )
    return xmlrpc_build_value(env, "s", login_ok );

   #ifdef DEBUG
     fprintf(stderr, "tcosxmlrpc::tcos_kill s=\"%s\" \n", s);
   #endif

     kill_exe(s);

     return xmlrpc_build_value(env, "s", s);
}


