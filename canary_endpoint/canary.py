from .constants import OK, WARNING, ERROR
from .decorators import timed
from .resources.projects import Project, GitProject


class Canary(object):
    """
    Reports the status of a project and its dependencies.
    """
    project_class = Project

    def __init__(self, name, version=None, root=None, resources=None):
        self.project = self.project_class(name, version=version, root=root)
        self.resources = resources or []

    @timed
    def check(self):
        metadata = self.project.check()
        resources = {r.name: r.check() for r in self.resources}
        status = self.get_worst_status(results=resources.values())
        return dict(metadata, status=status, resources=resources)

    def get_worst_status(self, results):
        status = OK
        for result in results:
            resource_status = result.setdefault('status', OK)
            if resource_status == ERROR:
                return ERROR
            elif status == OK and resource_status == WARNING:
                status = WARNING

        return status


class GitCanary(Canary):
    """
    Reports the status and revision of a Git project and dependencies.
    """
    project_class = GitProject
