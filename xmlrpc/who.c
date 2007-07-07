/*# who.c method that get user connected to :0 2006-09-09 14:22:40 mariodebian $
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

#include "who.h"


static xmlrpc_value *
tcos_who(xmlrpc_env *env, xmlrpc_value *in, void *ud)
 {
  FILE *fp;
  char line[BIG_BUFFER];
  char *info;
  size_t *len;

  /* read what info search */
  xmlrpc_parse_value(env, in, "(s#)", &info, &len);

  dbgtcos("tcosxmlrpc::tcos_who() searching for who=\"%s\"\n", info);

  if ( strcmp(info, "get_user") == 0 )
      fp=(FILE*)popen(GET_USER, "r");

  /* default method = error */
  else
      return xmlrpc_build_value(env, "s", WHO_UNKNOW );

  if (fp == NULL)
	return xmlrpc_build_value(env, "s", WHO_UNKNOW );

  /* put error into line var */
  strcpy(line, WHO_ERROR);

  fgets( line, sizeof line, fp);

  dbgtcos("tcosxmlrpc::tcos_who() line=\"%s\"\n", line);

  pclose(fp);
  return xmlrpc_build_value(env, "s", line );  
}




