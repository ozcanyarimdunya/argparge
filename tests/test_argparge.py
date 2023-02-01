import contextlib
import logging
import textwrap
import unittest
from io import StringIO

from argparge import Application
from argparge import Command
from argparge import ParentCommand

logger = logging.getLogger()


class TestApplication(unittest.TestCase):
    def test_add_commands(self):
        class Cmd1(Command):  # noqa
            name = "cmd1"

        class Cmd2(Command):  # noqa
            name = "cmd2"

        cmd1 = Cmd1()
        cmd2 = Cmd2()
        app = Application()
        app.add_commands(cmd1, cmd2)
        self.assertEqual(app._commands, [cmd1, cmd2])

    def test_run(self):
        # Create a dummy Command class that prints a message when its
        # handle method is called
        class TestCommand(Command):
            name = "test"

            def add_arguments(self, parser: "Command"):
                pass

            def handle(self, **arguments):
                logger.info("Test command executed")

        app = Application()
        app.add_commands(TestCommand())

        # Capture the output of the TestCommand's handle method
        with self.assertLogs(level="INFO") as cm:
            app.run(args=["test"])
        self.assertEqual(cm.output, ["INFO:root:Test command executed"])

    def test_parent(self):
        class C1(Command):
            name = "c1"

            def add_arguments(self, parser: "Command"): ...

            def handle(self, **arguments): ...

        class C2(Command):
            name = "c2"

            def add_arguments(self, parser: "Command"): ...

            def handle(self, **arguments): ...

        app = Application(prog="test")
        app.add_commands(
            ParentCommand(
                C1(),
                C2(),
                name="p",
            )
        )

        err = StringIO()

        with contextlib.redirect_stderr(err):
            with self.assertRaises(SystemExit):
                app.run(args=["p"])
            self.assertEqual(
                textwrap.dedent("""\
                USAGE: test p [-h] <command> ...

                OPTIONAL ARGUMENTS:
                  -h, --help  show this help message and exit

                AVAILABLE COMMANDS:
                  <command>
                    c1        c1
                    c2        c2
                """),
                err.getvalue()
            )
