"""A command module for Dragonfly, for controlling notepad++.

-----------------------------------------------------------------------------
Licensed under the LGPL3.

"""
from dragonfly import (
    MappingRule,
    AppContext,
    IntegerRef,
    Grammar,
    Key,  # @UnusedImport
)

import lib.config
config = lib.config.get_config()
if config.get("aenea.enabled", False) == True:
    from proxy_nicknames import Key  # @Reimport
    from proxy_nicknames import AppContext as NixAppContext


rules = MappingRule(
    mapping={
        # Commands:
        "activate editor": Key("f12"),
        "apply (fix|correction)": Key("c-1"),
        "choose editor": Key("cs-e"),
        "close tab": Key("c-w"),
        "close all tab": Key("cs-w"),
        "debug": Key("f11"),
        "duplicate down [<n>]": Key("ca-down:%(n)d"),
        "duplicate up [<n>]": Key("ca-up:%(n)d"),
        "find and replace": Key("c-f"),
        "go back": Key("a-right"),
        "go forward": Key("a-left"),
        "go to line": Key("c-g"),
        "go to matching bracket": Key("cs-p"),
        "go to source": Key("f3"),
        "resume": Key("f8"),
        "step in [<n>]": Key("f5/50:%(n)d"),
        "step next [<n>]": Key("f6/50:%(n)d"),
        "step out [<n>]": Key("f7/50:%(n)d"),
        "move tab left [<n>]": Key("c-pgup/10:%(n)d"),
        "move tab right [<n>]": Key("c-pgdown/10:%(n)d"),
        "terminate": Key("c-f2"),  # Stop debug session.
        "terminate all launches": Key("ca-f9"),  # Will switch TTY in Linux!!
        "toggle breakpoint": Key("cs-b"),
        "toggle comment": Key("c-slash"),
        "toggle editor": Key("c-f6"),
        "toggle expand": Key("c-m"),
        "toggle perspective": Key("c-f8"),
        "toggle view": Key("c-f7"),
        "save file": Key("c-s"),
        "save all": Key("cs-s"),
        "show file menu": Key("apps"),
        "show system menu": Key("a-minus"),
        "show shortcuts": Key("cs-l"),
        "show file properties": Key("a-enter"),
        "show view menu": Key("c-f10"),
        "switch editor": Key("c-e"),
    },
    extras=[
        IntegerRef("n", 1, 100),
    ],
    defaults={
        "n": 1
    }
)
context = None
winContext1 = AppContext(executable="notepad++", title="Notepad++")
winContext2 = AppContext(executable="mynotepad", title="Notepad++")
winContext = winContext1 | winContext2
if config.get("aenea.enabled", False) == True:
    nixContext = NixAppContext(executable="java", title="Eclipse")
    context = winContext | nixContext
else:
    context = winContext
grammar = Grammar("Eclipse", context=context)
grammar.add_rule(rules)
grammar.load()


def unload():
    """Unload function which will be called at unload time."""
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
