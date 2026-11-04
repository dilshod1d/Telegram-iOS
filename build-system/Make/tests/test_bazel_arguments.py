"""The advertised --bazelArguments option must reach the Bazel process unchanged."""

import contextlib
import io
import os
import sys
import types
import unittest
from unittest import mock

sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), '..'))

import Make


class BazelArgumentsTests(unittest.TestCase):
    def command_line(self, arguments=None):
        with mock.patch.object(Make, 'BuildEnvironment', return_value=types.SimpleNamespace(bazel_path='/tmp/bazel')):
            command = Make.BazelCommandLine('/tmp/bazel', False, False, '/tmp/cache', arguments)
        command.set_configuration('debug_sim_arm64')
        return command

    def test_build_test_and_query_keep_quoted_values_together(self):
        for method, args in [('invoke_build', []), ('invoke_test', ['//submodules/Postbox:PostboxTests']),
                             ('invoke_query', [['deps(//submodules/Postbox:Postbox)']])]:
            with self.subTest(method=method):
                command = self.command_line('--jobs=2 --define="description=People category"')
                with mock.patch.object(Make, 'call_executable') as run, contextlib.redirect_stdout(io.StringIO()):
                    getattr(command, method)(*args)
                tokens = run.call_args.args[0]
                self.assertIn('--jobs=2', tokens)
                self.assertIn('--define=description=People category', tokens)
                self.assertEqual(tokens.count('--jobs=2'), 1)

    def test_no_additional_arguments(self):
        self.assertEqual(self.command_line().get_additional_build_arguments(), [])

    def test_project_generation_forwards_additional_options(self):
        tokens = self.command_line('--jobs=2').get_project_generation_arguments()
        self.assertIn('--jobs=2', tokens)

    def test_existing_setter_is_honored(self):
        command = self.command_line()
        command.add_additional_args('--http_timeout_scaling=0.2')
        self.assertEqual(command.get_additional_build_arguments(), ['--http_timeout_scaling=0.2'])

    def test_test_command_forwards_cli_option(self):
        arguments = types.SimpleNamespace(overrideBazelVersion=False, overrideXcodeVersion=False,
                                         bazelUserRoot=None, bazelArguments='--jobs=2', cacheDir=None,
                                         cacheHost=None, target='//submodules/Postbox:PostboxTests')
        with mock.patch.object(Make.PostboxImportCheck, 'run', return_value=0), \
                mock.patch.object(Make, 'resolve_configuration'), \
                mock.patch.object(Make, 'BazelCommandLine') as command:
            Make.test('/tmp/bazel', arguments)
        self.assertEqual(command.call_args.kwargs['additional_args'], '--jobs=2')


if __name__ == '__main__':
    unittest.main()
