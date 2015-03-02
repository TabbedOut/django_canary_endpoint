from django.test import SimpleTestCase

from canary_endpoint.constants import ERROR
from canary_endpoint.mocks import MockTestCaseMixin, MockGitMixin
from canary_endpoint.resources.projects import GitProject


class GitProjectTestCase(MockTestCaseMixin, MockGitMixin, SimpleTestCase):
    def test_checks_status(self):
        self.mock_git_revision('f1o2o3\n')
        project = GitProject('foo', root='/foo', version='1.2.3')
        result = project.check()
        self.assertEqual(result, {
            'name': 'foo',
            'version': '1.2.3',
            'revision': 'f1o2o3',
        })
        command = ('git', 'rev-parse', 'HEAD')
        self.mock_git_output.assert_called_once_with(command, cwd='/foo')

    def test_reports_error_on_error(self):
        self.mock_git_error()
        project = GitProject('foo', root='/foo', version='1.2.3')
        result = project.check()
        self.assertEqual(result['status'], ERROR)
        self.assertEqual(result['revision'], None)
        self.assertEqual(
            result['error'],
            "Command 'foo' returned non-zero exit status 1"
        )

    def test_reports_error_on_git_not_found(self):
        self.mock_git_not_found()
        project = GitProject('foo', root='/foo', version='1.2.3')
        result = project.check()
        self.assertEqual(result['status'], ERROR)
        self.assertEqual(result['revision'], None)
        self.assertEqual(result['error'], 'command not found: git')
