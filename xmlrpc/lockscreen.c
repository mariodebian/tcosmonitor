/*# lockscreen.c method that lock unlock and get status of screen 2006-09-09 14:22:40 mariodebian $
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


static xmlrpc_value *
tcos_lockscreen(xmlrpc_env *env, xmlrpc_value *in, void *ud)
 {
  char *user;
  char *pass;
  char *login_ok;
  
   /* Parse app string */
   xmlrpc_parse_value(env, param_array, "(ss)", &user, &pass);
   if (env->fault_occurred)
        return xmlrpc_build_value(env, "s", "params error");

  /* need login first */
  login_ok=validate_login(user,pass);
  if( strcmp(login_ok,  LOGIN_OK ) != 0 )
    return xmlrpc_build_value(env, "s", login_ok );


  job_exe("lockscreen");
  return xmlrpc_build_value(env, "s", "OK" );  
}

static xmlrpc_value *
tcos_unlockscreen(xmlrpc_env *env, xmlrpc_value *in, void *ud)
 {
  char *user;
  char *pass;
  char *login_ok;

   /* Parse app string */
   xmlrpc_parse_value(env, param_array, "(ss)", &user, &pass);
   if (env->fault_occurred)
        return xmlrpc_build_value(env, "s", "params error");

   /* need login first */
  login_ok=validate_login(user,pass);
  if( strcmp(login_ok,  LOGIN_OK ) != 0 )
    return xmlrpc_build_value(env, "s", login_ok );

  job_exe("killall lockscreen");
  return xmlrpc_build_value(env, "s", "OK" );  
}




