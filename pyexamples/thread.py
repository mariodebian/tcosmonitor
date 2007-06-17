import threading
import time
import random 
import Queue


# define a class that subclasses Thread
class fibNext(threading.Thread):

  # define instance constructor
  def __init__(self):
     # no special initialization --- just call parent constructor
     threading.Thread.__init__(self) 

  # define run method (body of the thread)
  def run(self): 
     global workQ 
     print "thread", self.getName(), "starts"
     while True:
        f = workQ.get()
	if f == "quit":
	   workQ.put("quit")
	   break
        if len(f) >= 100:  
           workQ.put("quit")
           print "thread", self.getName(), "printing result", f
	   break
	f.append( f[-1] + f[-2] )
        print "thread", self.getName(), "computed Fib #", len(f)
        time.sleep(0.05 * random.random())
	workQ.put(f)
  
# initialize first two Fibonacci numbers
workQ = Queue.Queue()
workQ.put( [1,1] ) 

# construct a bunch of threads 
L = [] 
for i in range(5):
   L.append( fibNext() )

# then start each of the threads
for m in L:
   m.start()

# wait for them all to get done
for m in L:
   m.join()

