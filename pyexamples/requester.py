#!/usr/bin/env python

####################################
#Requester by Laramies             #
#Edge-security                     #
#www.edge-security.com             #
#Contact: laramies@edge-security.com
####################################
#Covered by GPL V2.0
#TODO Encoding problems.

import sys
import socket

try:
 import pygtk
except:
 print "Can't find Pygtk, please check if it is installed\n"
 pass

try:
 import gtk
 import gtk.glade
except:
 sys.exit(1)

def button1_clicked(self,widget):
	
	start,end = logwindow3.get_bounds()
	logwindow3.delete(start,end)
	start,end = logwindow2.get_bounds()
	logwindow2.delete(start,end)

def button_clicked(self,widget):
	prt = int(port.get_text())
	host = desthost.get_text()
	
	start,end = logwindow.get_bounds()
	req = logwindow.get_text(start,end)

	peticion = req
	peticion = peticion + "\r\n\r\n"
	skt = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
	skt.settimeout(8)
	
	
	try:
		skt.connect((host, prt))
	except socket.error,err:
		print "Error %s" % err[0]
		timed = ": Are you sure the port is open?\n"
		logwindow3.insert_at_cursor(err[0],len(err[0]))
		logwindow3.insert_at_cursor(timed,len(timed))
		return	
	if ssl.get_active():
		try:
			sslskt = socket.ssl(skt)
		except socket.sslerror, error:
			if error[0] != 8:
				print "Couldn't SSL connect socket [%s]" % str(error)
				logwindow3.insert_at_cursor(str(error),len(str(error)))
				return
	
		sslskt.write(peticion)
		res = sslskt.read()
		raw = res.encode("String_Escape")
	else:
		skt.send(peticion)
		res = skt.recv(10000)
		while 1:
			block = skt.recv(1024)
			if not block:
				break
			res += block

		raw= res.encode("String_Escape")
		
			
	pet = peticion
	sep0 ="#################################################################\n"
	sep = "\n-----------------------------------\n\n"
	rw  = "Raw response:\n\n"
	rp = "Clean response:\n\n"
	logwindow2.insert_at_cursor(pet,len(pet))
	logwindow2.insert_at_cursor(sep0,len(sep0))
	
	logwindow3.insert_at_cursor(sep0,len(sep0))
	logwindow3.insert_at_cursor(rw,len(rw))
	logwindow3.insert_at_cursor(raw,len(raw))
	logwindow3.insert_at_cursor(sep,len(sep))
	logwindow3.insert_at_cursor(rp,len(rp))
	logwindow3.insert_at_cursor(res,len(res))
	




	
textview = gtk.TextView()
textview.set_size_request(500,500)
textview.set_border_width(8)
entry = gtk.Entry()
otra = gtk.Entry()
textbuffer = textview.get_buffer()

requestscroll = gtk.ScrolledWindow()
requestscroll.set_shadow_type("GTK_SHADOW_IN")
requestscroll.add(textview)
requestscroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)

destlabel = gtk.Label("Host: ")
portlabel = gtk.Label("Port: ")
global desthost
global port

desthost = gtk.Entry()
port = gtk.Entry()
ssl = gtk.CheckButton("SSL")

win = gtk.Window()
win.set_title("Requester by Laramies")
win.resize(700,500)
win.connect('delete-event', gtk.main_quit)
button = gtk.Button("Send request")
button.connect("clicked", button_clicked, textbuffer )
button2 = gtk.Button("Clean boxes")
button2.connect("clicked", button1_clicked, textbuffer )

vbox = gtk.VBox()
vbox.set_border_width(5)
ha = gtk.HBox()
ha.set_size_request(700,20)

requ = gtk.HBox()
requ.set_size_request(700,200)
requ.pack_start(requestscroll)

vbox.pack_start(ha,expand=False)
vbox.pack_start(requ,expand=False)
ha.pack_start(destlabel)
ha.pack_start(desthost,padding=2)
ha.pack_start(portlabel)
ha.pack_start(port,padding=2)
ha.pack_start(ssl,padding=2)
ha.pack_start(button2,padding=2)
vbox.pack_start(button, False, padding=4)

#Request response windows###

textview2 = gtk.TextView()
textview2.set_size_request(500,100)
textview2.set_border_width(1)
textbuffer2 = textview2.get_buffer()

textview3 = gtk.TextView()
textview3.set_size_request(500,500)
textbuffer3 = textview3.get_buffer()

logwindowview=textview
logwindow=gtk.TextBuffer(None)
logwindowview.set_buffer(logwindow)

logwindowreq=textview2
logwindow2=gtk.TextBuffer(None)
logwindowreq.set_buffer(logwindow2)

logwindowres=textview3
logwindow3=gtk.TextBuffer(None)
logwindowres.set_buffer(logwindow3)


reqscroll = gtk.ScrolledWindow()
resscroll = gtk.ScrolledWindow()
reqscroll.set_shadow_type("GTK_SHADOW_IN")
resscroll.set_shadow_type("GTK_SHADOW_IN")
reqscroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
resscroll.set_policy(gtk.POLICY_AUTOMATIC,gtk.POLICY_AUTOMATIC)
reqscroll.add(textview2)
resscroll.add(textview3)

reqwin = gtk.HBox()
reqlab = gtk.Label("Request history:")
reqlabwin = gtk.HBox()
reswin = gtk.HBox()
reslab = gtk.Label("Response history:")
reslabwin = gtk.HBox()
reqlabwin.pack_start(reqlab)
reslabwin.pack_start(reslab)

reqwin.pack_start(reqscroll,padding=4)
reswin.pack_start(resscroll,padding=4)
vbox.pack_start(reqlabwin)
vbox.pack_start(reqwin)
vbox.pack_start(reslabwin)
vbox.pack_start(reswin)
###########################

hbox = gtk.HBox()
vbox.pack_start(hbox)

win.add(vbox)
win.show_all()
gtk.main()
