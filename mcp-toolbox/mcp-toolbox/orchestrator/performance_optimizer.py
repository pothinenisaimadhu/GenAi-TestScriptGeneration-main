"""Performance optimization utilities for the multi-agent pipeline"""

import asyncio
import time
from typing import Dict, List, Any, Optional
from dataclasses import dataclass

@dataclass
class PerformanceMetrics:
    """Performance metrics tracking"""
    start_time: float
    end_time: Optional[float] = None
    operation_name: str = ""
    success: bool = True
    error_message: Optional[str] = None
    
    @property
    def duration(self) -> float:
        if self.end_time:
            return self.end_time - self.start_time
        return time.time() - self.start_time

class PerformanceOptimizer:
    """Optimize pipeline performance with intelligent resource management"""
    
    def __init__(self):
        self.metrics: List[PerformanceMetrics] = []
        self.active_operations: Dict[str, PerformanceMetrics] = {}
        
    def start_operation(self, operation_name: str) -> str:
        """Start tracking an operation"""
        operation_id = f"{operation_name}_{int(time.time() * 1000)}"
        metric = PerformanceMetrics(
            start_time=time.time(),
            operation_name=operation_name
        )
        self.active_operations[operation_id] = metric
        return operation_id
    
    def end_operation(self, operation_id: str, success: bool = True, error: str = None):
        """End tracking an operation"""
        if operation_id in self.active_operations:
            metric = self.active_operations[operation_id]
            metric.end_time = time.time()
            metric.success = success
            metric.error_message = error
            
            self.metrics.append(metric)
            del self.active_operations[operation_id]
    
    def get_performance_summary(self) -> Dict[str, Any]:
        """Get performance summary"""
        if not self.metrics:
            return {"total_operations": 0}
        
        successful_ops = [m for m in self.metrics if m.success]
        failed_ops = [m for m in self.metrics if not m.success]
        
        return {
            "total_operations": len(self.metrics),
            "successful_operations": len(successful_ops),
            "failed_operations": len(failed_ops),
            "success_rate": len(successful_ops) / len(self.metrics),
            "avg_duration": sum(m.duration for m in self.metrics) / len(self.metrics),
            "total_duration": sum(m.duration for m in self.metrics),
            "operation_breakdown": self._get_operation_breakdown()
        }
    
    def _get_operation_breakdown(self) -> Dict[str, Dict[str, float]]:
        """Get breakdown by operation type"""
        breakdown = {}
        
        for metric in self.metrics:
            op_name = metric.operation_name
            if op_name not in breakdown:
                breakdown[op_name] = {
                    "count": 0,
                    "total_duration": 0.0,
                    "avg_duration": 0.0,
                    "success_rate": 0.0
                }
            
            breakdown[op_name]["count"] += 1
            breakdown[op_name]["total_duration"] += metric.duration
            
        # Calculate averages and success rates
        for op_name in breakdown:
            op_metrics = [m for m in self.metrics if m.operation_name == op_name]
            successful = [m for m in op_metrics if m.success]
            
            breakdown[op_name]["avg_duration"] = breakdown[op_name]["total_duration"] / breakdown[op_name]["count"]
            breakdown[op_name]["success_rate"] = len(successful) / len(op_metrics)
        
        return breakdown

class ResourceManager:
    """Manage system resources and prevent overload"""
    
    def __init__(self, max_concurrent_operations: int = 5):
        self.max_concurrent = max_concurrent_operations
        self.semaphore = asyncio.Semaphore(max_concurrent_operations)
        self.active_operations = 0
    
    async def acquire_resource(self, operation_name: str = "unknown"):
        """Acquire resource for operation"""
        await self.semaphore.acquire()
        self.active_operations += 1
        print(f"INFO: Resource acquired for {operation_name} ({self.active_operations}/{self.max_concurrent} active)")
    
    def release_resource(self, operation_name: str = "unknown"):
        """Release resource after operation"""
        self.semaphore.release()
        self.active_operations -= 1
        print(f"INFO: Resource released for {operation_name} ({self.active_operations}/{self.max_concurrent} active)")
    


class CircuitBreaker:
    """Circuit breaker pattern for external service calls"""
    
    def __init__(self, failure_threshold: int = 5, recovery_timeout: int = 60):
        self.failure_threshold = failure_threshold
        self.recovery_timeout = recovery_timeout
        self.failure_count = 0
        self.last_failure_time = 0
        self.state = "CLOSED"  # CLOSED, OPEN, HALF_OPEN
    
    async def call(self, func, *args, **kwargs):
        """Execute function with circuit breaker protection"""
        if self.state == "OPEN":
            if time.time() - self.last_failure_time > self.recovery_timeout:
                self.state = "HALF_OPEN"
                print("INFO: Circuit breaker: Attempting recovery")
            else:
                raise Exception("Circuit breaker is OPEN - service unavailable")
        
        try:
            result = await func(*args, **kwargs)
            
            if self.state == "HALF_OPEN":
                self.state = "CLOSED"
                self.failure_count = 0
                print("INFO: Circuit breaker: Service recovered")
            
            return result
            
        except Exception as e:
            self.failure_count += 1
            self.last_failure_time = time.time()
            
            if self.failure_count >= self.failure_threshold:
                self.state = "OPEN"
                print(f"WARNING: Circuit breaker: OPEN due to {self.failure_count} failures")
            
            raise e

# Global instances
performance_optimizer = PerformanceOptimizer()
resource_manager = ResourceManager(max_concurrent_operations=3)
circuit_breaker = CircuitBreaker(failure_threshold=3, recovery_timeout=30)