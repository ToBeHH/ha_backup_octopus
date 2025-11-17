"""Handler registry for backup integration.

Expose AVAILABLE_HANDLERS so the integration can discover handler classes
without knowing implementation details.
"""
from .wled import WLEDBackupHandler

AVAILABLE_HANDLERS = [WLEDBackupHandler]
