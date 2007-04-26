import gobject
import gtk
import math

w = gtk.Window()
darea = gtk.DrawingArea()
w.add(darea)
w.show_all()
w.connect("destroy", lambda w: gtk.main_quit())

offset = 0

NPOINTS = 5

def darea_expose(darea, event):
    global offset
    cr = darea.window.cairo_create()
    radius = (1.5 + math.sin(3*offset))/2
    ro = radius*.4*min(darea.allocation.height, darea.allocation.height)
    ri = .3*ro
    cr.translate(darea.allocation.width/2, darea.allocation.height/2)
    outer = [(ro, offset + 2*math.pi/NPOINTS*i) for i in range(NPOINTS)]
    inner = [(ri, offset + 2*math.pi/NPOINTS*i + 2*math.pi/(2*NPOINTS)) for i in range(NPOINTS)]
    cr.new_path()
    for i, ((r1, theta1), (r2, theta2)) in enumerate(zip(outer, inner)):
        if i:
            cr.line_to(r1*math.cos(theta1), r1*math.sin(theta1))
            cr.line_to(r2*math.cos(theta2), r2*math.sin(theta2))
        else:
            cr.move_to(r1*math.cos(theta1), r1*math.sin(theta1))
            cr.line_to(r2*math.cos(theta2), r2*math.sin(theta2))
    cr.close_path()
    cr.set_source_rgb(1, 1, 0)
    cr.fill_preserve()
    cr.set_source_rgb(1, 0, 0)
    cr.set_line_width(min(darea.allocation.height, darea.allocation.height)*.01)
    cr.stroke()
    
def timeout_cb():
    global offset
    offset += math.pi/50
    if offset > 2*math.pi:
        offset -= 2*math.pi
    darea.queue_draw()
    return True
    
darea.connect("expose-event", darea_expose)
darea.realize()
darea.window.set_background(darea.style.black)
gobject.timeout_add(30, timeout_cb)

gtk.main()

