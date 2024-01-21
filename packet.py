# packet.py

class Packet:
    def __init__(self, incoming_port, size, arrival_time, id):
        self.incoming_port = incoming_port
        self.size = size
        self.served_size = 0
        self.arrival_time = arrival_time
        self.id = id
        self.serve_time = 0
    def serve(self,amount):
        if self.served_size + amount > self.size:
            raise ValueError("Cannot serve this much amount")
        self.served_size += amount
    def is_done(self):
        return self.served_size >= self.size
    def __str__(self):
        return "Packet:"+str(self.id)+" From:" + str(self.incoming_port) + ",sz:" + str(self.size) + ",served:" + str(self.served_size)