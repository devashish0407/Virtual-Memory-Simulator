from simulator.core import VirtualMemorySimulator
from utils.input_parser import parse_reference_string

def run_multi_simulation(ref_str, vm_size, pm_size, pg_size):
    algos = ["FIFO", "LRU", "Optimal"]
    simulators = {}
    
    parsed_ref = parse_reference_string(ref_str)
    
    for algo in algos:
        simulators[algo] = VirtualMemorySimulator(vm_size, pm_size, pg_size, algo)
        simulators[algo].run_simulation(parsed_ref)

    return simulators

def run_single_simulation(ref_str, vm_size, pm_size, pg_size, algorithm):
    sim = VirtualMemorySimulator(vm_size, pm_size, pg_size, algorithm)
    parsed_ref = parse_reference_string(ref_str)
    sim.run_simulation(parsed_ref)
    return sim