"""
Various utilities for the multiprocess invoker.
"""
from __future__ import division, print_function, with_statement

import uuid
from abc import ABCMeta, abstractmethod
from multiprocessing.synchronize import Lock

from metaopt.invoker.util.determine_worker_count import determine_worker_count
from metaopt.invoker.util.model import Release
from metaopt.invoker.util.worker import WorkerProcess
from metaopt.util.stoppable import Stoppable, stoppable_method, stopping_method
from metaopt.invoker.util.model import Task


class WorkerProcessProvider(object):
    """
    Keeps track of up to as many worker processes as there are CPUs.
    """

    # There are a fixed and limited number of CPUs on a computer.
    # These are a shared resource for all process provider instances.
    # So we keep them in a shared space, by implementing the borg pattern.
    _lock = Lock()
    _worker_processes = []

    def __init__(self, queue_tasks, queue_outcome, queue_status,
                 status_db):
        with self._lock:
            # use the given queues
            self._queue_outcome = queue_outcome
            self._queue_start = queue_status
            self._queue_task = queue_tasks
            # use up to all CPUs
            self._worker_count_max = determine_worker_count()
            self._status_db = status_db

    def provision(self, number_of_workers=1):
        """
        Provisions a given number worker processes for future use.
        """
        with self._lock:
            if self._worker_count_max < (len(self._worker_processes) +
                                     number_of_workers):
                raise IndexError("Cannot provision so many worker processes.")

            #worker_handles = []
            for _ in range(number_of_workers):
                worker_id = uuid.uuid4()
                worker_process = WorkerProcess(worker_id=worker_id,
                                           queue_tasks=self._queue_task,
                                           queue_outcome=self._queue_outcome,
                                           queue_status=self._queue_start)
                worker_process.daemon = True  # workers don't spawn processes
                worker_process.start()
                self._worker_processes.append(worker_process)

                #worker_handles.append(WorkerProcessHandle(worker_id))

    def release(self, task_id):
        """Releases a worker process given by id."""
        with self._lock:
            worker_id = self._status_db.get_worker_id(task_id=task_id)
            try:
                worker_process = self._get_worker_process_for_id(worker_id)
            except KeyError:
                # nothing to do
                return
            self._release(worker_process)

    def _release(self, worker_process):
        """Releases the given worker process."""

        # send kill signal and wait for the process to die
        assert worker_process.is_alive()
        worker_process.terminate()
        worker_process.join()

        try:
            task = self._status_db.get_running_task(worker_process.worker_id)
        except KeyError:
            # No task was started for this worker process, yet.
            # We still need to kill the worker process.
            # So construct an empty task to send in the Release message.
            task = Task(id=None, function=None,
                        args=None, kwargs=None)
        # send manually constructed error result
        release = Release(worker_id=worker_process.worker_id,
                          task=task)
        self._queue_outcome.put(release)

        # bookkeeping
        self._worker_processes.remove(worker_process)

    def release_all(self):
        """
        Releases all worker processes.
        """
        with self._lock:
            # copy worker processes so that _release does not modify
            worker_processes = self._worker_processes[:]
            for worker_process in worker_processes:
                self._release(worker_process)

    def _get_worker_process_for_id(self, worker_id):
        """Utility method to resolve a worker id to a worker process."""
        for worker_process in self._worker_processes:
            if worker_process.worker_id == worker_id:
                return worker_process
        raise KeyError("There is no worker with the given worker id: %s" % worker_id)

    @property
    def worker_count(self):
        """Returns the number of currently running worker processes."""
        with self._lock:
            return len(self._worker_processes)


class WorkerHandle(Stoppable):
    """Interface definition for worker handle implementations."""
    __metaclass__ = ABCMeta

    @abstractmethod
    def __init__(self):
        super(WorkerHandle, self).__init__()

    @stoppable_method
    @stopping_method
    def release(self):
        """Stops this worker."""
        raise NotImplementedError()  # Implementations need to overwrite


class WorkerProcessHandle(WorkerHandle):
    """A means to stop a worker."""

    def __init__(self, worker_id):
        super(WorkerProcessHandle, self).__init__()
        self._worker_id = worker_id

    @property
    def worker_id(self):
        """Property for the worker id attribute."""
        return self._worker_id

    @stoppable_method
    @stopping_method
    def release(self):
        """Stops this worker."""
        WorkerProcessProvider().release(self._worker_id)
