
#from Misc import singleton
from multiprocessing import Process, Value, Array, Queue
from multiprocessing.sharedctypes import copy
from time import time, sleep

#@singleton
class cola:
      __instance = None
      @staticmethod 
      def getInstance():
            """ Static access method. """
            if cola.__instance == None:
                  cola()
            return cola.__instance

      def __init__(self):
            print('Iniciado')
            """ Virtually private constructor. """
            if cola.__instance != None:
                  raise Exception("This class is a singleton!")
            else:
                  cola.__instance = self
            
            self.elemetos = []
            self.iniciado = False

      def proceso(self):
            if not self.iniciado:
                  self.iniciado = True
                  for i in range(10):
                        self.elemetos.append(i)
                        #print(len(self.elemetos))
                        sleep(0.3)

      def tam(self):
            return len(self.elemetos)

def lanzar(nom, proc, queue):
      print(nom,'carga cola', nom)
      q = queue.get()
      c = q.getInstance()
      print(c)
      if proc:
            c.proceso()
      for _ in range(5):
            print(nom, c.tam())
            sleep(1)
      print('Fin del', nom)


if __name__ == "__main__":
      queue = Queue()
      c = cola()    
      queue.put(c)
      p1 = Process(target=lanzar, args=('Hilo 1', True, queue,))
      #p1.daemon = True
      p1.start()
      
      queue.put(c)
      p2 = Process(target=lanzar, args=('Hilo 2', False, queue,))
      #p2.daemon = True
      p2.start() 

