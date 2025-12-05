"""Handler registry for backup integration.

Expose AVAILABLE_HANDLERS so the integration can discover handler classes
without knowing implementation details.
"""
from .wled import WLEDBackupHandler
from .generic_download import GenericDownloadBackupHandler

AVAILABLE_HANDLERS = [WLEDBackupHandler, GenericDownloadBackupHandler]
