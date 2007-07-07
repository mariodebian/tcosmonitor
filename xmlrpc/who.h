/*who.h common headers  2006-09-09 14:22:40 mariodebian $
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

/* xmlrpc methods to export thin client info */

#define GET_USER "who | awk '($2 ~ /:0/) {print $1}'"


/* messages */
#define WHO_UNKNOW "error: Unknow user"
#define WHO_ERROR  "error: who returned error"


FILE *popen(const char *orden, const char *tipo);
int pclose(FILE *flujo);

