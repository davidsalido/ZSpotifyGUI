import sys
import traceback
import logging
from PyQt5.QtCore import QObject, pyqtSignal, QRunnable
from const import TRACKS, ARTISTS, ALBUMS, PLAYLISTS

logger = logging.getLogger(__name__)

class WorkerSignals(QObject):
    finished = pyqtSignal()
    error = pyqtSignal(tuple)
    update = pyqtSignal(object)
    result = pyqtSignal(object)

class MusicSignals(WorkerSignals):
    update = pyqtSignal(float, int, int)

class Worker(QRunnable):
    """
    First parameter is the function run by the worker thread. *args and *kwargs are passed to the that worker function.
    To add an update function, pass a kwarg with key "update" where the value is a function that will get connected
    to the worker update signal.
    """

    def __init__(self, fn, *args, **kwargs):
        super().__init__()
        self.fn = fn
        self.args = args
        self.kwargs = kwargs
        if "signals" in self.kwargs:
            self.signals =self.kwargs["signals"]
        else: self.signals = WorkerSignals()
        if "update" in self.kwargs.keys():
            self.signals.update.connect(self.kwargs["update"])

    def run(self):
        try:
            logger.info("Attempting to start worker thread.")
            if "update" in self.kwargs.keys():
                result = self.fn(
                    self.signals.update.emit, *self.args, **self.kwargs
                )
            else:
                result = self.fn(
                 *self.args, **self.kwargs
                )
        except:
            traceback.print_exc()
            exctype, value = sys.exc_info()[:2]
            logger.error(f"{exctype} : {value} - {traceback.format_exc()}")
            self.signals.error.emit((exctype, value, traceback.format_exc()))
        else:
            self.signals.result.emit(result)  # Return the result of the processing
        finally:
            self.signals.finished.emit()
