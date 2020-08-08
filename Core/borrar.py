from multiprocessing import Process, Queue, Value
from time import sleep, time

class Hijo():
    mensaje:str='Original'
    #def __init__(self):
    #    self.qq = Queue()

    def start(self, q:Queue):
        self.qq = q
        espera = 10
        while True:
            for _ in range(espera):
                if not self.qq.empty():
                    msj = self.qq.get()
                    print(self.mensaje, msj)
                sleep(1)
            print('Esperando...')
            #sleep(espera)

class Padre():
    def __init__(self):
        pass
    def start(self):
        h = Hijo()
        h.mensaje = 'H de padre'
        self.qq = Queue()
        proc = Process(target=h.start, args=(self.qq,))
        proc.start()
        i : int = 0
        while True:
            print('Padre', i)
            self.qq.put(i)
            i += 1
            sleep(5)


if __name__ == "__main__":
    Padre().start()
    