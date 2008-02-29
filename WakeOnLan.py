# Wake-On-LAN
#
# Copyright (C) 2002 by Micro Systems Marc Balmer
# Written by Marc Balmer, marc@msys.ch, http://www.msys.ch/
# This code is free software under the GPL

import struct, socket
import shared


def print_debug(txt):
    if shared.debug:
        print "%s::%s" %(__name__, txt)

def WakeOnLan(ethernet_address):
    errortxt=None
    # Construct a six-byte hardware address
    if not ethernet_address:
        print_debug("Not valid ethernet address: \"%s\""%ethernet_address)
        return False
    
    try:
        addr_byte = ethernet_address.split(':')
        hw_addr = struct.pack('BBBBBB', int(addr_byte[0], 16),
        int(addr_byte[1], 16),
        int(addr_byte[2], 16),
        int(addr_byte[3], 16),
        int(addr_byte[4], 16),
        int(addr_byte[5], 16))

        # Build the Wake-On-LAN "Magic Packet"...

        msg = '\xff' * 6 + hw_addr * 16

        # ...and send it to the broadcast address using UDP

        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(msg, ('<broadcast>', 9))
        s.close()
        print_debug("WakeOnLan() send to %s done"%ethernet_address)
        return True
    except Exception, err:
        print_debug("Exception error %s"%err)
        return False
    
    

# Example use
#WakeOnLan('0:3:93:81:68:b2') 
