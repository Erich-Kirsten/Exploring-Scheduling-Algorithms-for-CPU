import random
from dataclasses import dataclass
from typing import List, Dict, Optional
import heapq
from collections import deque
import statistics

@dataclass
class Process:
    pid: int
    arrival_time: int
    burst_time: int
    priority: int
    remaining_time: int
    start_time: Optional[int] = None
    completion_time: Optional[int] = None
    
    @property
    def turnaround_time(self) -> Optional[int]:
        if self.completion_time is None:
            return None
        return self.completion_time - self.arrival_time
    
    @property
    def waiting_time(self) -> Optional[int]:
        if self.turnaround_time is None:
            return None
        return self.turnaround_time - self.burst_time

class Scheduler:
    def __init__(self, processes: List[Process]):
        self.original_processes = processes
        self.reset_processes()
        
    def reset_processes(self):
        """Reset processes to their initial state for new simulation"""
        self.processes = [
            Process(
                pid=p.pid,
                arrival_time=p.arrival_time,
                burst_time=p.burst_time,
                priority=p.priority,
                remaining_time=p.burst_time
            )
            for p in self.original_processes
        ]
        
    def get_metrics(self) -> Dict:
        """Calculate and return performance metrics"""
        completed_processes = [p for p in self.processes if p.completion_time is not None]
        
        if not completed_processes:
            return {
                "avg_turnaround_time": 0,
                "avg_waiting_time": 0,
                "throughput": 0,
                "cpu_utilization": 0
            }
            
        max_completion_time = max(p.completion_time for p in completed_processes)
        
        return {
            "avg_turnaround_time": statistics.mean(p.turnaround_time for p in completed_processes),
            "avg_waiting_time": statistics.mean(p.waiting_time for p in completed_processes),
            "throughput": len(completed_processes) / max_completion_time,
            "cpu_utilization": sum(p.burst_time for p in completed_processes) / max_completion_time * 100
        }

    def fcfs(self) -> Dict:
        """First Come First Served scheduling"""
        self.reset_processes()
        current_time = 0
        ready_queue = []
        completed_processes = []
        
        while len(completed_processes) < len(self.processes):
            # Add newly arrived processes to ready queue
            for process in self.processes:
                if process.arrival_time <= current_time and process not in completed_processes and process not in ready_queue:
                    ready_queue.append(process)
            
            if not ready_queue:
                current_time += 1
                continue
                
            # Get next process
            process = ready_queue.pop(0)
            
            # Set start time if not already set
            if process.start_time is None:
                process.start_time = current_time
                
            # Execute process
            current_time += process.remaining_time
            process.remaining_time = 0
            process.completion_time = current_time
            completed_processes.append(process)
            
        return self.get_metrics()

    def sjf_nonpreemptive(self) -> Dict:
        """Shortest Job First (non-preemptive) scheduling"""
        self.reset_processes()
        current_time = 0
        ready_queue = []
        completed_processes = []
        
        while len(completed_processes) < len(self.processes):
            # Add newly arrived processes to ready queue
            for process in self.processes:
                if process.arrival_time <= current_time and process not in completed_processes and process not in ready_queue:
                    ready_queue.append(process)
            
            if not ready_queue:
                current_time += 1
                continue
                
            # Sort ready queue by burst time
            ready_queue.sort(key=lambda x: x.remaining_time)
            
            # Get next process
            process = ready_queue.pop(0)
            
            # Set start time if not already set
            if process.start_time is None:
                process.start_time = current_time
                
            # Execute process
            current_time += process.remaining_time
            process.remaining_time = 0
            process.completion_time = current_time
            completed_processes.append(process)
            
        return self.get_metrics()

    def sjf_preemptive(self) -> Dict:
        """Shortest Job First (preemptive) scheduling"""
        self.reset_processes()
        current_time = 0
        ready_queue = []
        completed_processes = []
        
        while len(completed_processes) < len(self.processes):
            # Add newly arrived processes to ready queue
            for process in self.processes:
                if process.arrival_time <= current_time and process not in completed_processes and process not in ready_queue:
                    ready_queue.append(process)
            
            if not ready_queue:
                current_time += 1
                continue
                
            # Sort ready queue by remaining time
            ready_queue.sort(key=lambda x: x.remaining_time)
            
            # Get next process
            process = ready_queue[0]
            
            # Set start time if not already set
            if process.start_time is None:
                process.start_time = current_time
                
            # Execute process for 1 time unit
            process.remaining_time -= 1
            current_time += 1
            
            # If process is complete, move it to completed queue
            if process.remaining_time == 0:
                process.completion_time = current_time
                completed_processes.append(process)
                ready_queue.pop(0)
                
        return self.get_metrics()

    def round_robin(self, quantum: int = 2) -> Dict:
        """Round Robin scheduling"""
        self.reset_processes()
        current_time = 0
        ready_queue = deque()
        completed_processes = []
        
        while len(completed_processes) < len(self.processes):
            # Add newly arrived processes to ready queue
            for process in self.processes:
                if process.arrival_time <= current_time and process not in completed_processes and process not in ready_queue:
                    ready_queue.append(process)
            
            if not ready_queue:
                current_time += 1
                continue
                
            # Get next process
            process = ready_queue.popleft()
            
            # Set start time if not already set
            if process.start_time is None:
                process.start_time = current_time
                
            # Execute process for quantum or remaining time
            execution_time = min(quantum, process.remaining_time)
            process.remaining_time -= execution_time
            current_time += execution_time
            
            # If process is complete, move it to completed queue
            if process.remaining_time == 0:
                process.completion_time = current_time
                completed_processes.append(process)
            else:
                # Add back to ready queue
                ready_queue.append(process)
                
        return self.get_metrics()

    def priority_nonpreemptive(self) -> Dict:
        """Priority (non-preemptive) scheduling"""
        self.reset_processes()
        current_time = 0
        ready_queue = []
        completed_processes = []
        
        while len(completed_processes) < len(self.processes):
            # Add newly arrived processes to ready queue
            for process in self.processes:
                if process.arrival_time <= current_time and process not in completed_processes and process not in ready_queue:
                    ready_queue.append(process)
            
            if not ready_queue:
                current_time += 1
                continue
                
            # Sort ready queue by priority (lower number = higher priority)
            ready_queue.sort(key=lambda x: x.priority)
            
            # Get next process
            process = ready_queue.pop(0)
            
            # Set start time if not already set
            if process.start_time is None:
                process.start_time = current_time
                
            # Execute process
            current_time += process.remaining_time
            process.remaining_time = 0
            process.completion_time = current_time
            completed_processes.append(process)
            
        return self.get_metrics()

    def priority_preemptive(self) -> Dict:
        """Priority (preemptive) scheduling"""
        self.reset_processes()
        current_time = 0
        ready_queue = []
        completed_processes = []
        
        while len(completed_processes) < len(self.processes):
            # Add newly arrived processes to ready queue
            for process in self.processes:
                if process.arrival_time <= current_time and process not in completed_processes and process not in ready_queue:
                    ready_queue.append(process)
            
            if not ready_queue:
                current_time += 1
                continue
                
            # Sort ready queue by priority (lower number = higher priority)
            ready_queue.sort(key=lambda x: x.priority)
            
            # Get next process
            process = ready_queue[0]
            
            # Set start time if not already set
            if process.start_time is None:
                process.start_time = current_time
                
            # Execute process for 1 time unit
            process.remaining_time -= 1
            current_time += 1
            
            # If process is complete, move it to completed queue
            if process.remaining_time == 0:
                process.completion_time = current_time
                completed_processes.append(process)
                ready_queue.pop(0)
                
        return self.get_metrics()

    def multilevel_queue(self, quantum: int = 2) -> Dict:
        """Multilevel Queue scheduling with 3 priority queues"""
        self.reset_processes()
        current_time = 0
        # Create 3 priority queues (high, medium, low)
        queues = [deque(), deque(), deque()]
        completed_processes = []
        
        while len(completed_processes) < len(self.processes):
            # Add newly arrived processes to appropriate queue based on priority
            for process in self.processes:
                if process.arrival_time <= current_time and process not in completed_processes and not any(process in q for q in queues):
                    queue_index = min(process.priority // 4, 2)  # Map priority to queue index
                    queues[queue_index].append(process)
            
            # If all queues are empty, increment time
            if all(not q for q in queues):
                current_time += 1
                continue
            
            # Find highest priority non-empty queue
            queue_index = next(i for i, q in enumerate(queues) if q)
            process = queues[queue_index].popleft()
            
            # Set start time if not already set
            if process.start_time is None:
                process.start_time = current_time
            
            # Execute process according to queue rules
            if queue_index == 0:  # High priority: Run to completion
                execution_time = process.remaining_time
            else:  # Medium and low priority: Round robin
                execution_time = min(quantum, process.remaining_time)
                
            process.remaining_time -= execution_time
            current_time += execution_time
            
            # If process is complete, move it to completed queue
            if process.remaining_time == 0:
                process.completion_time = current_time
                completed_processes.append(process)
            else:
                # Add back to queue
                queues[queue_index].append(process)
                
        return self.get_metrics()

def generate_processes(num_processes: int) -> List[Process]:
    """Generate random processes for simulation"""
    processes = []
    for i in range(num_processes):
        processes.append(
            Process(
                pid=i,
                arrival_time=random.randint(0, 50),
                burst_time=random.randint(1, 20),
                priority=random.randint(0, 10),
                remaining_time=0
            )
        )
    return processes

def run_simulation():
    """Run simulation with all scheduling algorithms"""
    # Generate processes
    processes = generate_processes(20)
    scheduler = Scheduler(processes)
    
    # Run all algorithms and collect results
    results = {
        "FCFS": scheduler.fcfs(),
        "SJF (Non-preemptive)": scheduler.sjf_nonpreemptive(),
        "SJF (Preemptive)": scheduler.sjf_preemptive(),
        "Round Robin": scheduler.round_robin(quantum=2),
        "Priority (Non-preemptive)": scheduler.priority_nonpreemptive(),
        "Priority (Preemptive)": scheduler.priority_preemptive(),
        "Multilevel Queue": scheduler.multilevel_queue(quantum=2)
    }
    
    # Print results
    print("\nSimulation Results:")
    print("-" * 80)
    for algorithm, metrics in results.items():
        print(f"\n{algorithm}:")
        print(f"Average Turnaround Time: {metrics['avg_turnaround_time']:.2f} ms")
        print(f"Average Waiting Time: {metrics['avg_waiting_time']:.2f} ms")
        print(f"CPU Utilization: {metrics['cpu_utilization']:.2f}%")
        print(f"Throughput: {metrics['throughput']:.4f} processes/ms")

if __name__ == "__main__":
    run_simulation()