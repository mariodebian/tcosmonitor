/* validate throught /etc/tcospasswd */

/*validate-tcos.c validate throught /etc/tcospasswd  2006-09-09 14:22:40 mariodebian $
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

#define _GNU_SOURCE
#include <string.h>

#include <pwd.h>
#include <sys/types.h>

#include "validate.h"


void
split_login( struct info *login )
{
int i;
char *p;
  p = strtok (login->line,":");
  i=0;
  while (p != NULL)
  {
    if(i==0){
      login->user=p;
      i++;
    }
    else if(i==1){
      login->pass=p;
      i++;
    }
    p = strtok (NULL, "");
  }
 /* clean last char of password */
 login->pass[strlen(login->pass)-1]='\0';
}




char *validate_tcos(char *user, char *pass)
{
  /*struct passwd *pwd;*/
  char *cryptpass;
  FILE *fp;
  char line[BSIZE];
  struct info *login;
  fp = fopen ("/etc/tcospasswd", "r" );
  if (fp == NULL) {
     dbgtcos("error validate_tcos(): file /etc/tcospasswd not exists.\n");
     return (char*) LOGIN_ERROR;
  }

  fgets( line, sizeof line, fp);
  strcpy(login->line, line);
  split_login(login);

  #ifdef VISIBLE_PASSWD 
    dbgtcos( "validate_tcos() user=\"%s\" pass=\"%s\"\n", login->user, login->pass);
  #endif
  
  dbgtcos( "validate_tcos() check users user=\"%s\" my_user=\"%s\"\n", user, login->user);

  if ( strcmp(login->user, user) != 0 ) {
     dbgtcos("error validate_passwd(): BAD USER.\n");  
     return LOGIN_NOUSER;
  }

  cryptpass=crypt(pass, PASS_ID );

  #ifdef VISIBLE_PASSWD 
    dbgtcos("info validate_passwd(): the_pass=%s my_pass=%s \n", login->pass, cryptpass);
  #endif

  if ( strcmp(login->pass, cryptpass) == 0 ) {
     dbgtcos("info validate_passwd(): LOGIN OK.\n");
     return LOGIN_OK;
  }
  dbgtcos("info validate_passwd(): BAD PASSWORD.\n");
  return LOGIN_NOPASS;
}



#ifndef HAVE_MAIN
int main() {
  char *username;
  char *password;
  username = "root";
  password = "root";
  printf("main() user=%s pass=%s\n", username, password );
  printf("main() ?= %s.\n", validate_tcos(username, password) );

  return 0;
}
#endif



