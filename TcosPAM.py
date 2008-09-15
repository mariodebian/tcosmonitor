# -*- coding: UTF-8 -*-
##########################################################################
# TcosMonitor writen by MarioDebian <mariodebian@gmail.com>
#
# TcosMonitor version __VERSION__
#
# Copyright (c) 2006 Mario Izquierdo <mariodebian@gmail.com>
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 59 Temple Place - Suite 330, Boston, MA
# 02111-1307, USA.
###########################################################################

import PAM


def auth(user, password):
    class AuthConv:
        def __init__(self, password):
            self.password = password

        def __call__(self, auth, query_list, userData):
            resp = []
            for query, qt in query_list:
                if qt == PAM.PAM_PROMPT_ECHO_ON:
                    resp.append((self.password, 0))
                elif qt == PAM.PAM_PROMPT_ECHO_OFF:
                    resp.append((self.password, 0))
                elif qt == PAM.PAM_PROMPT_ERROR_MSG or type == PAM.PAM_PROMPT_TEXT_INFO:
                    print query
                    resp.append(('', 0))
                else:
                    return None
            return resp


    auth = PAM.pam()
    auth.start("passwd")
    auth.set_item(PAM.PAM_USER, user)
    auth.set_item(PAM.PAM_CONV, AuthConv(password))
    try:
        auth.authenticate()
        auth.acct_mgmt()
        return True
    except PAM.error, resp:
        if resp[1] == 9:
            print "error: TcosPAM error in pam connection. Are you root?"
        else:
            print "error: TcosPAM user:%s error:%s" % (user, resp)
        return False


if __name__ == '__main__':
    print auth("test", "test")
