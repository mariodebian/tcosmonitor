# -*- coding: UTF-8 -*-

from time import sleep

from threading import Thread


class Workers:
    def __init__(self, main, target, args, multi=False, dog=True):
        self.dog=dog
        self.main=main
        self.target=target
        self.args=args
        if self.main.worker_running == True:
            print "worker() other work pending"
        else:
            print "worker() no other jobs"
            self.th=Thread(target=self.target, args=(self.args) )
            self.__stop=True
    
    def start_watch_dog(self, dog_thread):
        if not self.dog:
            print "start_watch_dog() dog DISABLED"
            return
        print "start_watch_dog() starting watch dog"
        watch_dog=Thread(target=self.watch_dog, args=([dog_thread]) )
        watch_dog.start()

    def watch_dog(self, dog_thread):
        print "watch_dog()  __init__ "
        dog_thread.join()
        self.set_finished()
        print "watch_dog() FINISHED"
        
    def start(self):
        if not self.dog:
            self.th.start()
        else:
            
            if self.main.worker_running == False:
                self.th.start()     # start thread
                self.set_started()  # config var as started
                self.start_watch_dog(self.th) # start watch_dog
            else:
                print "worker() other work pending... not starting"
    
    def set_finished(self):
        self.__finished = True
        self.__stop=False
        self.main.worker_running=False

    def set_started(self):
        self.__finished=False
        self.__stop=False
        self.main.worker_running=True


class Prueba:
    def __init__(self):
        self.worker_running=False

    def con_perro(self):
        # ejecución con perro guardian
        self.worker=Workers(self, target=self.hacer_algo, args=(["soy el proc 1"]) )
        self.worker.start()

        # lanzamos un nuevo proceso despues de 2 seg
        sleep(2)
        self.worker=Workers(self, target=self.hacer_algo, args=(["soy el proc 2"]) )
        self.worker.start()

    def sin_perro(self):
        # ejecución con perro guardian
        self.worker=Workers(self, target=self.hacer_algo, args=(["soy el proc 1"]), dog=False)
        self.worker.start()

        # lanzamos un nuevo proceso despues de 2 seg
        sleep(2)
        self.worker=Workers(self, target=self.hacer_algo, args=(["soy el proc 2"]), dog=False)
        self.worker.start()
    
    def hacer_algo(self, arg1):
        print "::::::::::::::haciendo algo....arg1=\"%s\"" %(arg1)
        sleep(4)
        print "::::::::::::::hemos acabado arg1=\"%s\"" %(arg1)
        # avisamos a worker que hemos acabado (por si no tenemos perro)
        self.worker.set_finished()

if __name__ == "__main__":
    print "CON PERROS"
    Prueba().con_perro()
    sleep(10)
    print "\n\nAHORA SIN PERROS"
    Prueba().sin_perro()
    sleep(10)
