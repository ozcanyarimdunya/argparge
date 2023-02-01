import argparse
from abc import abstractmethod


class HelpFormatter(argparse.HelpFormatter):
    def __init__(self, *args, **kwargs):
        kwargs.update(max_help_position=32, width=145)
        super().__init__(*args, **kwargs)

    def start_section(self, heading):
        super().start_section(heading=heading.upper())

    def add_usage(self, usage, actions, groups, prefix=None):
        if prefix is None:
            prefix = "USAGE: "
        super().add_usage(usage, actions, groups, prefix=prefix)


class Command(argparse.ArgumentParser):
    name = None
    help = None
    parent = False

    def __init__(self, *commands, **kwargs):
        self._commands = list(commands)
        assert self.name is not None, "Command name cannot be empty! Set 'name' variable {} class.".format(
            self.__class__.__name__
        )
        self.help = self.help or self.name
        self.kwargs = kwargs
        self.kwargs["description"] = kwargs.get("description", self.help)
        self.kwargs["formatter_class"] = kwargs.get("formatter_class", HelpFormatter)
        super().__init__(**kwargs)

    @abstractmethod
    def add_arguments(self, parser: "Command"): ...

    @abstractmethod
    def handle(self, **arguments): ...

    @property
    def commands(self):
        return self._commands


class ParentCommand(Command):
    parent = True

    def __init__(self, *commands, name, **kwargs):
        self.name = name
        self.help = kwargs.pop("help", name)
        super().__init__(*commands, **kwargs)
        self.kwargs["description"] = None

    def add_arguments(self, parser: "Command"): ...

    def handle(self, **arguments): ...


class Application(argparse.ArgumentParser):
    _mappings_key = "#><#"

    def __init__(self, *args, **kwargs):
        self._mappings = {}
        self._commands = []
        self.arguments = None
        kwargs["formatter_class"] = kwargs.get("formatter_class", HelpFormatter)
        super().__init__(*args, **kwargs)

    def add_commands(self, *commands):
        self._commands.extend(commands)

    def prepare(self, parent_parser, name, *commands):
        if not commands:
            return
        subparser = parent_parser.add_subparsers(title="available commands", metavar="<command>")
        for command in commands:
            parser = subparser.add_parser(command.name, help=command.help, **command.kwargs)
            command.add_arguments(parser)
            if name is None:
                whoami = command.name
            else:
                whoami = "{0}>{1}".format(name, command.name)
            parser.set_defaults(**{self._mappings_key: whoami})
            self._mappings[whoami] = {"command": command, "parser": parser}
            self.prepare(parser, whoami, *command.commands)

    def run(self, args=None):
        self.prepare(self, None, *self._commands)
        self.arguments = vars(self.parse_args(args))
        if not self.arguments:
            self.exit(message=self.format_help())
        subcommand = self.arguments.pop(self._mappings_key, None)
        if not subcommand:
            return
        command = self._mappings[subcommand]["command"]
        if command.parent:
            parser = self._mappings[subcommand]["parser"]
            self.exit(message=parser.format_help())
        command.handle(**self.arguments)
