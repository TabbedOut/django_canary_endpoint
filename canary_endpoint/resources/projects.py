import subprocess

from ..constants import ERROR
from . import Resource


class GitMixin(object):
    """
    Wraps a project check to include the current Git revision.
    """
    def check(self):
        result = super(GitMixin, self).check()
        try:
            revision = self.get_revision()
            return dict(result, revision=revision)
        except (OSError, subprocess.CalledProcessError) as e:
            return dict(result, revision=None, status=ERROR, error=str(e))

    def get_revision(self):
        command = ('git', 'rev-parse', 'HEAD')
        return subprocess.check_output(command, cwd=self.root).strip()


class Project(Resource):
    """
    Checks the status of a project.
    """
    def __init__(self, name, root, version=None, **kwargs):
        self.name = name
        self.root = root
        self.version = version

    def check(self):
        return {'name': self.name, 'version': self.get_version()}

    def get_version(self):
        return self.version


class GitProject(GitMixin, Project):
    """
    Checks the status of a Git project.
    """
    pass
