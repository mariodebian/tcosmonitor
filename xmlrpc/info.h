/*info.h common headers  2006-09-09 14:22:40 mariodebian $
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

/* type of thin client (tcos, pxes, ltsp, unknow) */
#define GET_CLIENT "/sbin/getinfo.sh -t"

#define GET_PROCESS "/sbin/getinfo.sh -p"

/* CPU methods */
#define CPU_MODEL  "/sbin/getinfo.sh -i CPU_MODEL"
#define CPU_SPEED  "/sbin/getinfo.sh -i CPU_SPEED"
#define CPU_VENDOR "/sbin/getinfo.sh -i CPU_VENDOR"


/* RAM methods */
#define RAM_TOTAL  "/sbin/getinfo.sh -i RAM_TOTAL"
#define RAM_ACTIVE "/sbin/getinfo.sh -i RAM_ACTIVE"
#define RAM_FREE   "/sbin/getinfo.sh -i RAM_FREE"
#define RAM_USED   "/sbin/getinfo.sh -i RAM_USED"

/* SWAP methods*/
#define SWAP_AVALAIBLE "/sbin/getinfo.sh -i SWAP_AVALAIBLE"
#define SWAP_TOTAL     "/sbin/getinfo.sh -i SWAP_TOTAL"
#define SWAP_USED      "/sbin/getinfo.sh -i SWAP_USED"
#define SWAP_FREE      "/sbin/getinfo.sh -i SWAP_FREE"

/* DATE and version methods */
#define TCOS_DATE            "/sbin/getinfo.sh -i TCOS_DATE"
#define TCOS_GENERATION_DATE "/sbin/getinfo.sh -i TCOS_GENERATION_DATE"
#define TCOS_VERSION         "/sbin/getinfo.sh -i TCOS_VERSION"

/* KERNEL methods*/
#define KERNEL_VERSION          "/sbin/getinfo.sh -i KERNEL_VERSION"
#define KERNEL_COMPLETE_VERSION "/sbin/getinfo.sh -i KERNEL_COMPLETE_VERSION"


/* NETWORK methods */
#define NETWORK_HOSTNAME "/sbin/getinfo.sh -i NETWORK_HOSTNAME"
#define NETWORK_IP       "/sbin/getinfo.sh -i NETWORK_IP"
#define NETWORK_MAC      "/sbin/getinfo.sh -i NETWORK_MAC"
#define NETWORK_MASK     "/sbin/getinfo.sh -i NETWORK_MASK"
#define NETWORK_RX       "/sbin/getinfo.sh -i NETWORK_RX"
#define NETWORK_TX       "/sbin/getinfo.sh -i NETWORK_TX"


/* MODULES methods */
#define MODULES_LOADED       "/sbin/getinfo.sh -i MODULES_LOADED"
#define MODULES_NOTFOUND     "/sbin/getinfo.sh -i MODULES_NOTFOUND"

#define BIG_BUFFER 5000

/* messages */
#define INFO_UNKNOW "error: Unknow info request"
#define INFO_ERROR  "error: info command failure"


FILE *popen(const char *orden, const char *tipo);
int pclose(FILE *flujo);

