from scheduler import BaseScheduler
import time
MIN_BYTE_SEND = 10

class DRRScheduler(BaseScheduler):
    def __init__(self,num_of_input_ports=4, quantum=100, initial_deficit=0):
        super().__init__("DRR",num_of_input_ports)
        self.quantum = quantum
        self.deficits = [initial_deficit] * num_of_input_ports  # Initialize deficits for each input port
    
    def serve_packets(self):
        served_packets = []
        # Serve packets from the head of the output queue
        with self.lock:
            served_bytes = 0
            while served_bytes < self.num_of_input_ports * self.distribution_mean * self.packet_length:
                if self.output_queue.empty():
                    break
                packet = self.output_queue.get()  # Get the packet from the output queue
                if not packet.is_done():
                    serving_amount = min(MIN_BYTE_SEND, packet.size - packet.served_size)
                    packet.serve(serving_amount)
                    served_bytes += serving_amount
                    self.deficits[packet.incoming_port] -= serving_amount
                
                if packet.is_done():
                    packet.serve_time = int(time.time() * 1000)
                    served_packets.append(packet)
                else:
                    self.output_queue.put(packet)
        return served_packets
    
    def schedule(self):
        # Iterate over input queues and serve packets based on DRR
        for i in range(self.num_of_input_ports):
            while not self.input_queues[i].empty() and self.deficits[i] >= MIN_BYTE_SEND:
                selected_packet = self.input_queues[i].get()  # Dequeue the packet
                serving_amount = min(self.quantum, selected_packet.size - selected_packet.served_size)
                selected_packet.serve(serving_amount)
                self.output_queue.put(selected_packet)  # Enqueue the packet to the output queue
                self.deficits[i] -= serving_amount
    
    def are_all_input_queues_empty(self):
        # Check if all input queues are empty
        return all(input_queue.empty() for input_queue in self.input_queues)