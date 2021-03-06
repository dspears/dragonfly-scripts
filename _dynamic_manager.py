"""A command module for Dragonfly, for dynamically enabling/disabling
different grammars, and for enabling and disabling other features.

If a grammar is enabled that is conflicting with a previously enabled grammar,
the previously enabled grammar will be automatically disabled.
Each dynamic grammar module is responsible for keeping track of what other
modules is incompatible with.

Other features that can be enabled/disabled are Aenea, the client-server
connection to Linux. Note that a reload is required after changing Aenea state.

-----------------------------------------------------------------------------
Licensed under LGPL3

"""
import sys
import pkgutil

from dragonfly import (
    CompoundRule,
    MappingRule,
    RuleRef,
    Repetition,
    Function,
    IntegerRef,
    Dictation,
    Choice,
    Grammar
)

import lib.config
config = lib.config.get_config()
if config.get("aenea.enabled", False) == True:
    import aenea

import lib.sound as sound
import dynamics

moduleMapping = {}


def notify_module_enabled(moduleName, useSound=True):
    """Notifies the user that a dynamic module has been enabled."""
    print("==> Dynamic grammar enabled: %s" % moduleName)
    if useSound:
        sound.play(sound.SND_ACTIVATE)


def notify_module_disabled(moduleName, useSound=True):
    """Notifies the user that a dynamic module has been disabled."""
    print("<-- Dynamic grammar disabled: %s" % moduleName)
    if useSound:
        sound.play(sound.SND_DEACTIVATE)


def notify_module_action_aborted(message, useSound=True):
    """Notifies the user, with a custom message, that the action was not
    completed.

    """
    print(message)
    if useSound:
        sound.play(sound.SND_MESSAGE)


def notify(message="", useSound=True):
    """Notifies the user, with a custom message, that the action was not
    completed.

    """
    if message:
        print(message)
    if useSound:
        sound.play(sound.SND_DING)


def enable_module(module, useSound=True):
    """Enables the specified module. Disables conflicting modules."""
    if not module:
        return
    moduleName = module.DYN_MODULE_NAME
    disable_incompatible_modules(module)
    status = module.dynamic_enable()
    if status:
        notify_module_enabled(moduleName, useSound)
        config = lib.config.get_config()
        config["dynamics.%s" % moduleName] = True
        lib.config.save_config()
    else:
        notify_module_action_aborted("Dynamic grammar %s already enabled." %
            moduleName)


def disable_module(module, useSound=True):
    """Disabled the specified module."""
    if not module:
        return
    status = module.dynamic_disable()
    moduleName = module.DYN_MODULE_NAME
    if status:
        notify_module_disabled(moduleName, useSound)
        config = lib.config.get_config()
        config["dynamics.%s" % moduleName] = False
        lib.config.save_config()


def disable_incompatible_modules(enableModule):
    """Iterates through the list of incompatible modules and disables them."""
    global moduleMapping
    for moduleName in enableModule.INCOMPATIBLE_MODULES:
        module = moduleMapping.get(moduleName)
        if module:
            disable_module(module, useSound=True)


def import_dynamic_modules():
    global moduleMapping
    config = lib.config.get_config()
    path = dynamics.__path__
    prefix = dynamics.__name__ + "."
    print("Loading dynamic grammar modules:")
    for importer, package_name, _ in pkgutil.iter_modules(path, prefix):
        if package_name not in sys.modules:
            module = importer.find_module(package_name).load_module(
                package_name)
            moduleMapping[module.DYN_MODULE_NAME] = module
            enabled = config.get("dynamics.%s" % module.DYN_MODULE_NAME, False)
            print("    %s" % package_name)
            if enabled == True:
                enable_module(module, useSound=False)


import_dynamic_modules()


def disable_all_modules():
    """Iterates through the list of all dynamic modules and disables them."""
    global moduleMapping
    disableCount = 0
    config = lib.config.get_config()
    for moduleName, module in moduleMapping.items():
        status = module.dynamic_disable()
        if status:
            disableCount += 1
            config["dynamics.%s" % moduleName] = False
            notify_module_disabled(moduleName, useSound=False)
    if disableCount > 0:
        sound.play(sound.SND_DEACTIVATE)
        lib.config.save_config()
    print("----------- All dynamic modules disabled -----------\n")


def enable_aenea():
    config = lib.config.get_config()
    if config.get("aenea.enabled", False) == False:
        config["aenea.enabled"] = True
        lib.config.save_config()
        print("<<< Aenea enabled, reload required. >>>")
        print("<<< Don't forget, start the server and the client window. >>>")


def disable_aenea():
    config = lib.config.get_config()
    if config.get("aenea.enabled", False) == True:
        config["aenea.enabled"] = False
        lib.config.save_config()
        print("<<< Aenea disabled. >>>")


class SeriesMappingRule(CompoundRule):
    def __init__(self, mapping, extras=None, defaults=None):
        mapping_rule = MappingRule(mapping=mapping, extras=extras,
            defaults=defaults, exported=False)
        single = RuleRef(rule=mapping_rule)
        series = Repetition(single, min=1, max=16, name="series")

        compound_spec = "<series>"
        compound_extras = [series]
        CompoundRule.__init__(self, spec=compound_spec,
            extras=compound_extras, exported=True)

    def _process_recognition(self, node, extras):  # @UnusedVariable
        series = extras["series"]
        for action in series:
            action.execute()

series_rule = SeriesMappingRule(
    mapping={
        #"(enable|load) <module> grammar": Function(enable_module),
        #"(disable|unload) <module> grammar": Function(disable_module),
        #"(disable|unload) [all] dynamic grammars": Function(disable_all_modules),  # @IgnorePep8
        "[(start|switch to)] <module> mode": Function(enable_module),  # Too disruptive? Time will tell...    @IgnorePep8
        "(stop|end) <module> mode": Function(disable_module),
        "(stop|end) [all] dynamic modes": Function(disable_all_modules),
        "enable (Aenea|Linux connection)": Function(enable_aenea),
        "disable (Aenea|Linux connection)": Function(disable_aenea),
    },
    extras=[
        IntegerRef("n", 1, 100),
        Dictation("text"),
        Choice("module", moduleMapping),
    ],
    defaults={
        "n": 1
    }
)

context = None
if config.get("aenea.enabled", False) == True:
    context = aenea.global_context
grammar = Grammar("Dynamic manager", context=context)
grammar.add_rule(series_rule)
grammar.load()


notify()  # Notify that Dragonfly is ready with a sound.


def unload():
    """Unload function which will be called at unload time."""
    # Unload the dynamically loaded modules.
    global moduleMapping
    for module in moduleMapping.values():
        module.unload()

    global grammar
    if grammar:
        grammar.unload()
    grammar = None
