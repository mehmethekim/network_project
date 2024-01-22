from fifo_scheduler import FIFOScheduler
from pifo_scheduler import PIFOScheduler
from drr_scheduler import DRRScheduler
from dr_pifo_scheduler import DRPIFOScheduler
NUM_PORTS = 4

scheduler = DRPIFOScheduler(NUM_PORTS)
#scheduler = PIFOScheduler(NUM_PORTS)
scheduler.start_simulation()
scheduler.plot_data()

