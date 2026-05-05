import asyncio
import threading
import time
from collections import defaultdict
from typing import Any


class AnalysisEventBus:
    def __init__(self) -> None:
        self._subscribers: dict[int, list[asyncio.Queue]] = defaultdict(list)
        self._lock = threading.Lock()
        self._task_timestamps: dict[int, float] = {}

    def subscribe(self, task_id: int) -> asyncio.Queue:
        queue: asyncio.Queue = asyncio.Queue(maxsize=256)
        with self._lock:
            self._subscribers[task_id].append(queue)
            self._task_timestamps[task_id] = time.time()
        return queue

    def unsubscribe(self, task_id: int, queue: asyncio.Queue) -> None:
        with self._lock:
            if task_id in self._subscribers:
                self._subscribers[task_id] = [
                    q for q in self._subscribers[task_id] if q is not queue
                ]
                if not self._subscribers[task_id]:
                    del self._subscribers[task_id]
                    self._task_timestamps.pop(task_id, None)

    def publish(self, task_id: int, event: dict[str, Any]) -> None:
        with self._lock:
            for queue in self._subscribers.get(task_id, []):
                try:
                    queue.put_nowait(event)
                except asyncio.QueueFull:
                    pass

    def has_subscribers(self, task_id: int) -> bool:
        with self._lock:
            return len(self._subscribers.get(task_id, [])) > 0

    def cleanup_stale(self, max_age_seconds: float = 600) -> None:
        now = time.time()
        with self._lock:
            stale_ids = [
                tid
                for tid, ts in self._task_timestamps.items()
                if now - ts > max_age_seconds
            ]
            for tid in stale_ids:
                for queue in self._subscribers.pop(tid, []):
                    try:
                        queue.put_nowait({"type": "stale_cleanup"})
                    except asyncio.QueueFull:
                        pass
                self._task_timestamps.pop(tid, None)


event_bus = AnalysisEventBus()
