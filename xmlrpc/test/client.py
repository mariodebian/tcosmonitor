#!/usr/bin/env python2.4
import xmlrpclib
from time import time, sleep
import sys
import threading

def howmany():
    return ( time() - start )


# Create an object to represent our server.
#server_url = 'http://192.168.0.10:8080/RPC2';

#server_url = 'http://192.168.0.11:8080/RPC2';
#server_url = 'http://192.168.0.6:8080/RPC2';
server_url = 'http://localhost:8080/RPC2';
server_url = 'http://192.168.0.100:8080/RPC2';

server = xmlrpclib.Server(server_url);


result = server.tcos.version("")
print "PYTHON::version is=%s" %(result)

#result = server.tcos.info("get_client")
#print "PYTHON::get_client is=%s" %(result)

result = server.tcos.standalone("get_server")
print "PYTHON::get_server is=%s" %(result)

#result = server.tcos.info("get_process")
#print "PYTHON::get_process is=%s" %(result)

#result = server.tcos.dbus("--auth='root:root' --type='exec' --text='xterm' --username='mario'", "root", "root")
#print "PYTHON::dbus is=%s" %(result)

#result = server.tcos.standalone("get_process")
#print "PYTHON::get_process is=%s" %(result)

#print "PYTHON devicesctl.sh =%s" %(server.tcos.exe("soundctl.sh --showcontrols", "root", "root"))
#print server.tcos.screenshot("10", "root", "root")

sys.exit(0)


#print "PYTHON client type=%s" %(server.tcos.info("get_client"))
#print "PYTHON client type=%s" %(server.tcos.info("get_process"))

#server.tcos.screenshot("65")
#sys.exit(0)
#sleep(1)


#auth=server.tcos.login("root", "root2")
#print "PYTHON screenshot =%s" %(server.tcos.exe("screenshot.sh", "root", "root"))


#result = server.tcos.xorg("get", "", "root", "root")
#print "PYTHON::xorg is=%s" %(result)

#result = server.tcos.screenshot("90", "root", "root")
#result = server.tcos.exe("scrot", "root", "root")
#print "PYTHON::screenshot is=%s" %(result)

#result = server.tcos.sound("--showcontrols", "", "root", "root")
#print "PYTHON::xorg is=%s" %(result)

#result = server.tcos.sound("--getmute", "Master", "root", "root")
#print "PYTHON::xorg is=%s" %(result)

result = server.tcos.devices("--showlocaldisks", "", "root", "root")
print "PYTHON::xorg is=%s" %(result)

sys.exit(0)

#result = server.tcos.xorg("change", "--xdriver=sis --xres=800x600")
#print "PYTHON::xorg is=%s" %(result)

#result = server.tcos.xorg("new", "--xdriver=vesa --xres=10024x768")
#print "PYTHON::xorg is=%s" %(result)

auth=server.tcos.login("user", "pass")
server.tcos.kill("Xorg")

result = server.tcos.xorg("get", "")
print "PYTHON::xorg is=%s" %(result)

result = server.tcos.xorg("new", "--xdriver=vesa --xres=1024x768")
print "PYTHON::xorg is=%s" %(result)

result = server.tcos.xorg("get", "")
print "PYTHON::xorg is=%s" %(result)


sys.exit(0)

class ClientThread (threading.Thread):
    def __init__(self):
        self.done=True
        self.stopthread = threading.Event()
        print ("Thread system init")

    def run(self, action, params):
                #print "run() exec=%s params=%s" %(action, params)
                #if not self.stopthread.isSet():
                if self.done:
                  self.done=False
                  print ("THREAD: doing jobs")
                  apply(action, params)
                  self.done=True
                  return

    def start(self):
        self.stopthread.clear()
        return
    def stop(self):
                self.stopthread.set()
                return

    def status(self):
        if self.done:
            print ("THREAD FREE")
        else:
            print ("THREAD BUSSY")
        return self.done


def howmany():
    return ( time() - start )

start=time()


print "\n\n\n"


"""
def get_version():
    result = server.tcos.version()
    print "PYTHON::version is=%s" %(result)

for i in range(10):
    th=ClientThread()
    th.run( get_version , [] )
    th.status()

print "waiting!!!"
sleep(5)
sys.exit(0)
"""
"""
def exec_app(app, num):
    auth=server.tcos.login("user", "pass")
    server.tcos.exe(app)
    print "PYTHON::exe(%d) " %(num)

for i in range(5):
    th=ClientThread()
    th.run ( exec_app, ['/usr/bin/xterm', i] )

print "waiting !!!!!!!!!!!!!!"
sleep(2)
sys.exit(0)
"""



#auth=server.tcos.login("user", "pass")
#print "PYTHON::AUTH:: \"%s\"" %(auth)

#result = server.tcos.exe("xterm")
#print "PYTHON::exe is=%s" %(result)

sys.exit()

"""
print "PYTHON::info(modules_loaded)=\"%s\"" % ( server.tcos.info("modules_loaded").replace('\n', '') )
print "\n"
print "PYTHON::info(modules_notfound)=\"%s\"" % ( server.tcos.info("modules_notfound").replace('\n', '') )

print "PYTHON::info(pci_all)=\"%s\"" % ( server.tcos.pci("pci_all").replace('\n', '') )
for pci in server.tcos.pci("pci_all").replace('\n', '').split(' '):
	if pci != "":
		print "PYTHON::info(pci bus=%s)=\"%s\"" % ( pci, server.tcos.pci(pci).replace('\n', '') )
	

sys.exit(0)
"""


print "PYTHON::info(cpu_model)=\"%s\"" % ( server.tcos.info("cpu_model").replace('\n', '') )
print "PYTHON::info(cpu_speed)=\"%s\"" % ( server.tcos.info("cpu_speed").replace('\n', '') )
print "PYTHON::info(cpu_vendor)=\"%s\"" % ( server.tcos.info("cpu_vendor").replace('\n', '') )
print "\n"
print "PYTHON::info(ram_total)=\"%s\"" % ( server.tcos.info("ram_total").replace('\n', '') )
print "PYTHON::info(ram_free)=\"%s\"" % ( server.tcos.info("ram_free").replace('\n', '') )
print "PYTHON::info(ram_used)=\"%s\"" % ( server.tcos.info("ram_used").replace('\n', '') )
print "PYTHON::info(ram_active)=\"%s\"" % ( server.tcos.info("ram_active").replace('\n', '') )
print "\n"
print "PYTHON::info(swap_avalaible)=\"%s\"" % ( server.tcos.info("swap_avalaible").replace('\n', '') )
print "PYTHON::info(swap_total)=\"%s\"" % ( server.tcos.info("swap_total").replace('\n', '') )
print "PYTHON::info(swap_used)=\"%s\"" % ( server.tcos.info("swap_used").replace('\n', '') )
print "PYTHON::info(swap_free)=\"%s\"" % ( server.tcos.info("swap_free").replace('\n', '') )
print "\n"
print "PYTHON::info(tcos_date)=\"%s\"" % ( server.tcos.info("tcos_date").replace('\n', '') )
print "PYTHON::info(tcos_generation_date)=\"%s\"" % ( server.tcos.info("tcos_generation_date").replace('\n', '') )
print "PYTHON::info(tcos_version)=\"%s\"" % ( server.tcos.info("tcos_version").replace('\n', '') )
print "\n"
print "PYTHON::info(network_hostname)=\"%s\"" % ( server.tcos.info("network_hostname").replace('\n', '') )
print "PYTHON::info(network_ip)=\"%s\"" % ( server.tcos.info("network_ip").replace('\n', '') )
print "PYTHON::info(network_mac)=\"%s\"" % ( server.tcos.info("network_mac").replace('\n', '') )
print "PYTHON::info(network_mask)=\"%s\"" % ( server.tcos.info("network_mask").replace('\n', '') )
print "PYTHON::info(network_rx)=\"%s\"" % ( server.tcos.info("network_rx").replace('\n', '') )
print "PYTHON::info(network_tx)=\"%s\"" % ( server.tcos.info("network_tx").replace('\n', '') )


#auth=server.tcos.login("user", "pass")
#print "PYTHON::AUTH:: \"%s\"" %(auth)

#start=time()
#result = server.tcos.version()
#print "PYTHON::version is=%s" %(result)
#print "PYTHON::time to get version %s\n\n" %( howmany() )

#start=time()
#result = server.tcos.info("cpu_model")
#print "PYTHON::cpu_model is=%s" %(result)
#print "PYTHON::time to get cpu_model %s\n\n" %( howmany() )

#print "\n\t AGAIN\n"
#result = server.tcos.version()
#print "PYTHON::version is=%s" %(result)


"""
start=time()
result = server.tcos.exe("startlocalx")
print "Exec return=%s" %(result)
print "time to get exec %f\n\n" %( howmany() )

start=time()
try:
	result = server.tcos.status("tilda")
	print "PYTHON::Tilda status is=%s" %(result)
except:
	print "Error loading tilda status\n"
	result=-1

print "PYTHON::time to get status %f\n" %( howmany() )
if result == "1":
	print "\t\tTilda is running\n"
elif result == "0":
	print "\t\tTilda is not running\n"
else:
	print "\tERROR loading status of tilda\n"


start=time()
result = server.tcos.status("evolution")
print "PYTHON::Evolution status is=%s" %(result)
print "PYTHON::time to get status %f\n\n" %( howmany() )

start=time()
result = server.tcos.status("apache2")
print "PYTHON::Apache2 status is=%s" %(result)
print "PYTHON::time to get status %f\n\n" %( howmany() )

start=time()
result = server.tcos.status("app-no-runnning")
print "PYTHON::app-no-runnning status is=%s" %(result)
print "PYTHON::time to get status %f\n\n" %( howmany() )
"""



#start=time()
#result = server.system.listMethods()
#print result
#print "PYTHON::time to get methods %f\n\n" %( howmany() )

#start=time()
# Call the server and get our result.
#result = server.sample.add(5, 10)
#print "PYTHON::Sum=%d" %(result)
#print "PYTHON::time to get sum %f\n\n" %( howmany() )


#start=time()
#result = server.sample.echo("hi")
#print "PYTHON::Echo return=%s" %(result)
#print "PYTHON::time to get echo %f\n\n" %( howmany() )



