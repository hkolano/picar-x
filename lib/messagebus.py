from readerwriterlock import rwlock

class MessageBus():

    def __init__(self):
        self.lock = rwlock.RWLockWriteD()
        self.message = []

    def write_msg(self, msg):
        with self.lock.gen_wlock():
            self.message = msg 

    def read_msg(self):
        with self.lock.gen_rlock():
            msg = self.message
        return self.message