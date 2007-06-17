#!/usr/bin/env python

import os, cPickle
def run_in_separate_process(f, *args, **kwds):
    pread, pwrite = os.pipe()
    pid = os.fork()
    if pid > 0:
        os.close(pwrite)
        os.fdopen(pread, 'rb') as f:
            status, result = cPickle.load(f)
        os.waitpid(pid, 0)
        if status == 0:
            return result
        else:
            raise result
    else: 
        os.close(pread)
        try:
            result = f(*args, **kwds)
            status = 0
        except Exception, exc:
            result = exc
            status = 1
        os.fdopen(pwrite, 'wb') as f:
            try:
                cPickle.dump((status,result), f, cPickle.HIGHEST_PROTOCOL)
            except cPickle.PicklingError, exc:
                cPickle.dump((2,exc), f, cPickle.HIGHEST_PROTOCOL)
        f.close()
        os._exit(0)

#an example of use
def treble(x):
    return 3 * x

def main():
    #calling directly
    print treble(4)
    #calling in separate process
    print run_in_separate_process(treble, 4)
