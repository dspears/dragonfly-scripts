from dragonfly import (
    Text,  # @UnusedImport
    Key,  # @UnusedImport
    Function,
    MappingRule,
    IntegerRef,
    Grammar,
    Dictation
)

import lib.config
config = lib.config.get_config()
if config.get("aenea.enabled", False) == True:
    from proxy_nicknames import Key, Text  # @Reimport
    import aenea

from lib.text import SCText


DYN_MODULE_NAME = "bash"
INCOMPATIBLE_MODULES = []


def directory_up(n):
    repeat = ['..' for i in range(n)]  # @UnusedVariable
    txt = "cd %s\n" % ("/".join(repeat))
    Text(txt).execute()


rules = MappingRule(
    mapping={
        # Commands and keywords:
        "sudo apt get update": Text("sudo apt-get update"),
        "apt cache search": Text("apt-cache search "),
        "apt cache search <text>": Text("apt-cache search %(text)s"),
        "sudo apt get install": Text("sudo apt-get install "),
        "sudo apt get install <text>": Text("sudo apt-get install %(text)s"),
        "(cat|C A T)": Text("cat "),
        "(cat|C A T) <text>": SCText("cat %(text)s"),
        "(change (directory|dir)|C D)": Text("cd "),
        "(change (directory|dir)|C D) <text>": SCText("cd %(text)s"),
        "[press] control break": Key("ctrl:down, c/10, ctrl:up"),
        "(copy|C P)": Text("cp "),
        "(copy|C P) recursive": Text("cp -r "),
        "(change mode)|C H mod": Text("chmod "),
        "diff": Text("diff "),
        "directory up <n> [times]": Function(directory_up),
        "D P K G": Text("dpkg "),
        "D P K G list": Text("dpkg -l "),
        "exit": Text("exit"),
        "find": Text("find . -name "),
        "find <text>": SCText("find . -name %(text)s"),
        "[go to] end of line": Key("c-e"),
        "[go to] start of line": Key("c-a"),
        "grep": Text("grep "),
        "grep <text>": SCText("grep %(text)s"),
        "grep recursive": Text("grep -rn \"\" *") + Key("left:3"),
        "grep recursive <text>": Text("grep -rn \"%(text)s\" *") + Key("left:3"),  # @IgnorePep8
        "ifconfig": Text("ifconfig "),
        "kill": Text("kill "),
        "kill (hard|[dash]9)": Text("kill -9 "),
        "kill line": Key("c-k"),
        "list files": Text("ls -la") + Key("enter"),
        "list files <text>": Text("ls -la %(text)s"),
        "list files time sort": Text("ls -lat") + Key("enter"),
        "make (directory|dir)": Text("mkdir "),
        "make (directory|dir) <text>": SCText("mkdir %(text)s"),
        "move": Text("mv "),
        "move <text>": SCText("mv %(text)s"),
        "pipe": Text(" | "),
        "ping": Text("ping "),
        "(print working directory|P W D)": Text("pwd") + Key("enter"),
        "P S": Text("ps -ef"),
        "(R M|remove file)": Text("rm "),
        "(R M|remove file) <text>": SCText("rm %(text)s"),
        "remove (directory|dir|folder|recursive)": Text("rm -rf "),
        "remove (directory|dir|folder|recursive) <text>": SCText("rm -rf %(text)s"),  # @IgnorePep8
        "(link|L N)": Text("ln "),
        "(secure copy|S C P)": Text("scp"),
        "(secure copy|S C P) <text>": SCText("scp %(text)"),
        "soft link": Text("ln -s "),
        "soft link <text>": SCText("ln -s %(text)"),
        "sudo": Text("sudo "),
        "tail": Text("tail "),
        "tail <text>": SCText("tail %(text)s"),
        "tail (F|follow)": Text("tail -f "),
        "tail (F|follow) <text>": SCText("tail -f %(text)s"),
        "telnet": Text("telnet "),
        "touch": Text("touch "),
        "touch <text>": SCText("touch %(text)s"),
        "vim": Text("vim "),
        "vim <text>": SCText("vim %(text)s"),
        "(W C|word count)": Text("wc "),
        "(W C|word count) lines": Text("wc -l "),
        "W get ": Text("wget "),
        "X M L lint": Text("xmllint "),
        "X M L lint <text>": SCText("xmllint %(text)s"),
        "X M L lint format": Text("xmllint -format "),
        "X M L lint format <text>": SCText("xmllint -format %(text)s"),
        "X M L lint schema": Text("xmllint -schema "),
        "X M L lint schema <text>": SCText("xmllint -schema %(text)s"),
    },
    extras=[
        IntegerRef("n", 1, 100),
        Dictation("text"),
    ],
    defaults={
        "n": 1
    }
)

context = None
if config.get("aenea.enabled", False) == True:
    context = aenea.global_context
grammar = Grammar("Python grammar", context=context)
grammar.add_rule(rules)
grammar.load()
grammar.disable()


def dynamic_enable():
    global grammar
    if grammar.enabled:
        return False
    else:
        grammar.enable()
        return True


def dynamic_disable():
    global grammar
    if grammar.enabled:
        grammar.disable()
        return True
    else:
        return False


# Unload function which will be called at unload time.
def unload():
    global grammar
    if grammar:
        grammar.unload()
    grammar = None
