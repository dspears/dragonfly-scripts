from dragonfly import (
    Text,  # @UnusedImport
    Key,  # @UnusedImport
    Function,
    MappingRule,
    Grammar,
    Dictation,
    IntegerRef
)

import lib.config
config = lib.config.get_config()
if config.get("aenea.enabled", False) == True:
    from proxy_nicknames import Key, Text  # @Reimport
    import aenea

import lib.format
from lib.text import SCText

DYN_MODULE_TYPE = "programming_language"
DYN_MODULE_NAME = "javascript"
INCOMPATIBLE_MODULES = [
    'python',
    'html',
    'css'
]


def define_function(text):
    Text("function ").execute()
    lib.format.camel_case_text(text)
    Text("() {").execute()
    Key("left:3").execute()

def add_onclick(text):
    Text('// Onclick handler for ').execute()
    lib.format.camel_case_text(text)
    Text('\nvar ').execute()
    lib.format.camel_case_text(text)
    Text(' = getElementById("#').execute()
    lib.format.camel_case_text(text)
    Text('");\n').execute()
    lib.format.camel_case_text(text)
    Text('.onclick = function() {\n\n}').execute()
    Key('up').execute()
    Text('  ').execute()

rules = MappingRule(
    mapping={
        # Keywords:
        "and": Text(" && "),
        "assign": Text(" = "),
        "break": Text("break"),
        "case": Text("case "),
        "case <text>": SCText("case %(text)s"),
        "catch": Text("catch () {") + Key("left:3"),
        "comment": Text("// "),
        "comment <text>": SCText("// %(text)s"),
        "continue": Text("continue"),
        "close comment": Text(" */"),
        "debugger": Text("debugger"),
        "default": Text("default"),
#         "delete": Text("delete "),  # Messes with ordinary delete command.
        "do": Text("do {"),
        "equals": Text(" == "),
        "equals (strict|strictly|exact|exactly)": Text(" === "),
        "else": Text("else"),
        "else if": Text("else if () {") + Key("left:3"),
        "extends ": Text("extends "),
        "for": Text("for () {") + Key("left:3"),
        "for <text>": SCText("for (%(text)s) {") + Key("left:3"),
        "false": Text("false"),
        "finally": Text("finally {") + Key("enter"),
        "function": Text("function "),
        "function <text>": Function(define_function),
        "greater than": Text(" > "),
        "greater equals": Text(" >= "),
        "if": SCText("if (%(text)s) {") + Key("left"),
        "if <text>": Text("if () {") + Key("left"),
        "instanceof": Text("instanceof ") + Key("left"),
        "(int|I N T)": Text("int "),
        "(int|I N T) <text>": SCText("int %(text)s"),
        "in": Text("in "),
        "in <text>": SCText("in %(text)s"),
        "((jquery|jay query) (variable|var)|dollar paren)": Text("$()") + Key("left"),  # @IgnorePep8
        "less than": Text(" < "),
        "less equals": Text(" <= "),
        "(line end|end line)": Key("end") + Text(";") + Key("enter"),
        "(minus|subtract|subtraction)": Text(" - "),
        "(minus|subtract|subtraction) equals": Text(" -= "),
        "modulo": Key("space") + Key("percent") + Key("space"),
        "new": Text("new "),
        "not equals": Text(" != "),
        "not (strict|strictly|exact|exactly) equals": Text(" !== "),
        "open comment": Text("/* "),
        "or": Text(" || "),
        "object": Text("Object "),
        "(plus|add|addition)": Text(" + "),
        "(plus|add|addition) equals": Text(" += "),
        "reg exp": Text("RegExp"),
        "return": Text("return"),
        "return <text>": SCText("return %(text)s"),
        "string": Text("String"),
        "switch": Text("switch () {") + Key("left:3"),
        "switch <text>": SCText("switch (%(text)s) {") + Key("left:3"),
        "this": Text("this"),
        "throw": Text("throw "),
        "true": Text("true"),
        "try": Text("try {") + Key("enter"),
        "typeof": Text("typeof "),
        "toString": Text("toString()") + Key("left"),
        "(variable|var)": Text("var "),
        "(variable|var) <text>": SCText("var %(text)s"),
        "while": Text("while () {") + Key("left:3"),
        "while <text>": SCText("while (%(text)s) {") + Key("left:3"),
        "with": Text("with () {") + Key("left:3"),
        "with <text>": SCText("with (%(text)s) {") + Key("left:3"),
        # Global variables and objects.
        "window": Text("window"),
        "undefined": Text("undefined"),
        "JSON": Text("JSON"),
        # "add onclick handler for <text>": Text('var ')+camel_case_text(%(text)s)+Text(' = getElementById("#%(text)s");\n%(text)s.onclick = function() {\n\n}')+Key('up')+Key('tab'),
        "add onclick handler for <text>": Function(add_onclick),
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
grammar = Grammar("JavaScript grammar", context=context)
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
