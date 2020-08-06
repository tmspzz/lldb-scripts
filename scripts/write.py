#!/usr/bin/python

# ---------------------------------------------------------------------
# Be sure to add the python path that points to the LLDB shared library.
#
# # To use this in the embedded python interpreter using "lldb" just
# import it with the full path using the "command script import"
# command
#   (lldb) command script import /path/to/cmdtemplate.py
# ---------------------------------------------------------------------

from __future__ import print_function

import inspect
import lldb
import argparse
import shlex
import sys
import os


class WriteCommand:
    program = 'write'

    @classmethod
    def register_lldb_command(cls, debugger, module_name):
        parser = cls.create_options()
        cls.__doc__ = parser.format_help()
        # Add any commands contained in this module to LLDB
        command = 'command script add -c %s.%s %s' % (module_name,
                                                      cls.__name__,
                                                      cls.program)
        debugger.HandleCommand(command)
        print('The "{0}" command has been installed, type "help {0}" or "{0} '
              '--help" for detailed help.'.format(cls.program))

    @classmethod
    def create_options(cls):

        description = ('This commands writes the output of any other command to file')

        
        parser = argparse.ArgumentParser(
            description=description,
            prog=cls.program)
        parser.add_argument('-p', '--base-path', default="~/Desktop/", type=str)
        parser.add_argument('filename')
        parser.add_argument('command', nargs='+')

        return parser

    def get_short_help(self):
        return "Writes to file the output of any other command"

    def get_long_help(self):
        return self.help_string

    def __init__(self, debugger, unused):
        self.parser = self.create_options()
        self.help_string = self.parser.format_help()

    def __call__(self, debugger, command, exe_ctx, result):
        # Use the Shell Lexer to properly parse up command options just like a
        # shell would
        command_args = shlex.split(command)
        try:
            args = self.parser.parse_args(command_args)
            args.command = ' '.join(args.command)
        except:
            # if you don't handle exceptions, passing an incorrect argument to
            # the OptionParser will cause LLDB to exit (courtesy of OptParse
            # dealing with argument errors by throwing SystemExit)
            result.SetError("option parsing failed")
            return
        
        # Run the command and store the result

        debugger.GetCommandInterpreter().HandleCommand(args.command, result)

        # Get the output even
        output = result.GetOutput() or result.GetError()
        file_path = args.base_path + args.filename
        self.write_to_file(file_path, output)

    def write_to_file(self, filename, output):
        """Write the output to the given file, headed by the command"""
        path = os.path.expanduser(filename) 
        f = open(path, 'w')
        f.write(output)


def __lldb_init_module(debugger, dict):
    # Register all classes that have a register_lldb_command method
    for _name, cls in inspect.getmembers(sys.modules[__name__]):
        if inspect.isclass(cls) and callable(getattr(cls,
                                                     "register_lldb_command",
                                                     None)):
            cls.register_lldb_command(debugger, __name__)