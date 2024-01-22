from scheduler import BaseScheduler
import time
MIN_BYTE_SEND = 10

class PIFOScheduler(BaseScheduler):
    def __init__(self,num_of_input_ports=4):
        super().__init__("PIFO",num_of_input_ports)
        self.tokens = [10] * num_of_input_ports  # Initialize tokens for each input port
    
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
                    self.tokens[packet.incoming_port] -= 1  # Increase tokens for the served port
                
                if packet.is_done():
                    packet.serve_time = int(time.time() * 1000)
                    served_packets.append(packet)
                else:
                    self.output_queue.put(packet)
                served_bytes += MIN_BYTE_SEND
        return served_packets
    
    def schedule(self):
        # Iterate over input queues and find the input port based on tokens
        scheduled_packet_count = 0
        
        while scheduled_packet_count < self.num_of_input_ports * self.distribution_mean:
            selected_queue = self.token_based_selection()
            
            if selected_queue is not None:
                selected_packet = self.input_queues[selected_queue].get()  # Dequeue the packet
                self.output_queue.put(selected_packet)  # Enqueue the packet to the output queue
                self.tokens[selected_queue] += 1  # Decrease tokens for the selected port
                scheduled_packet_count += 1
    
    def token_based_selection(self):
        # Perform token-based selection by selecting the input port with the most tokens
        selected_queue = None
        if self.is_any_input_queue_non_empty():
            selected_queue = max(range(self.num_of_input_ports), key=lambda i: self.tokens[i])
        return selected_queue
    def is_any_input_queue_non_empty(self):
        # Check if all input queues are not empty
        return any(not input_queue.empty() for input_queue in self.input_queues)
