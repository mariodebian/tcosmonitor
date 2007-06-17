import os, sys
from threading import *
import time

def log( message ):
    print ( "%d %s" % (os.getpid(), message) )


if __name__ == "__main__":
    log( "is parent" )
    t = Thread()
    t.start()
    # t.join() # OPTION 1

    childPID = os.fork()
    if childPID == 0:
        c=0
        while 1:
            log( "is child" )
            if c > 4:
                log ("child finished !!")
                break
            time.sleep(1)
            c=c+1
        

    log( "threads: %s" % str(enumerate()) )

    if childPID == 0:
        os._exit(0) # OPTION 2
        pass

    else:
        while 1:
            t.join()
            #os.kill( childPID, 15 ) # OPTION 3
            log( "parent done waiting for %s, now waiting for %d" %
                 (t.getName(), childPID) )
            try:
                os.waitpid(childPID, 0)
            except:
                break
        
    log( "exiting" )
