from scheduler import BaseScheduler
import time
MIN_BYTE_SEND = 10

class DRPIFOScheduler(BaseScheduler):
    def __init__(self, num_of_input_ports=4, max_service_quality=10):
        super().__init__("DR_PIFO", num_of_input_ports)
        self.pifo = []  # Priority-based Queue (PIFO) for holding packets based on their rank
        self.service_qualities = [max_service_quality] * num_of_input_ports  # Initial service quality for each input port

    def serve_packets(self):
        served_packets = []
        # Serve packets from the head of the output queue
        with self.lock:
            served_bytes = 0
            while served_bytes < self.num_of_input_ports * self.distribution_mean * self.packet_length:
                if self.pifo:
                    packet = self.pifo.pop(0) 
                    serving_amount = min(MIN_BYTE_SEND, packet.size - packet.served_size)
                    packet.serve(serving_amount)
                    served_bytes += serving_amount

                    if not packet.is_done():
                        self.pifo.insert(0, packet)
                    else:
                        packet.serve_time = int(time.time() * 1000)
                        served_packets.append(packet)

        return served_packets

    def schedule(self):
        # Iterate over input queues and re-rank packets based on service quality
        for i in range(self.num_of_input_ports):
            while not self.input_queues[i].empty():
                packet = self.input_queues[i].get() 

                packet.rank = max(0, packet.rank - self.service_qualities[i])

                
                self.enqueue_to_pifo(packet)

    def enqueue_to_pifo(self, packet):
        
        index = 0
        while index < len(self.pifo) and packet.rank < self.pifo[index].rank:
            index += 1
        self.pifo.insert(index, packet)
