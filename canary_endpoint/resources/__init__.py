from ..constants import OK


class Resource(object):
    """
    Represents a Resource with a status.

    "status" may be one of:

    - "ok", the resource is available
    - "warning", the resource may not be available
    " "error", the resource is unavailable
    """
    def __init__(self, name, description, **kwargs):
        self.name = name
        self.description = description

    def check(self):
        return {'description': self.description, 'status': OK}
