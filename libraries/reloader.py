import sublime
import sublime_plugin
import os
import threading
import builtins
import functools
import importlib
import sys
import types
from contextlib import contextmanager
from .stack_meter import StackMeter


def dprint(*args, fill=None, fill_width=60, **kwargs):
    if fill is not None:
        sep = str(kwargs.get('sep', ' '))
        caption = sep.join(args)
        args = "{0:{fill}<{width}}".format(caption and caption + sep,
                                           fill=fill, width=fill_width),
    print("[Deviot]", *args, **kwargs)


# check the link for comments
# https://github.com/divmain/GitSavvy/blob/599ba3cdb539875568a96a53fafb033b01708a67/common/util/reload.py
def reload_package(pkg_name, dummy=True):
    if pkg_name not in sys.modules:
        dprint("error:", pkg_name, "is not loaded.")
        return

    main = sys.modules[pkg_name]

    dprint("begin", fill='=')

    modules = {main.__name__: main}
    modules.update({name: module for name, module in sys.modules.items()
                    if name.startswith(pkg_name + ".")})
    for m in modules:
        if m in sys.modules:
            sublime_plugin.unload_module(modules[m])
            del sys.modules[m]

    try:
        with intercepting_imports(modules), \
                importing_fromlist_aggresively(modules):

            reload_plugin(main.__name__)
            reload_missing(modules)
    except:
        dprint("reload failed.", fill='-')
        raise
    if dummy:
        load_dummy()
    dprint("end", fill='-')


def load_dummy():
    """
    a hack to trigger automatic "reloading plugins"
    this is needed to ensure TextCommand's and WindowCommand's are ready.
    """
    dprint("installing dummy package")
    dummy = "_dummy_package"
    dummy_py = os.path.join(sublime.packages_path(), "%s.py" % dummy)
    open(dummy_py, "w").close()

    def remove_dummy(trial=0):
        if dummy in sys.modules:
            dprint("removing dummy package")
            if os.path.exists(dummy_py):
                os.unlink(dummy_py)
            after_remove_dummy()
        elif trial < 300:
            threading.Timer(0.1, lambda: remove_dummy(trial + 1)).start()
        else:
            if os.path.exists(dummy_py):
                os.unlink(dummy_py)

    condition = threading.Condition()

    def after_remove_dummy(trial=0):
        if dummy not in sys.modules:
            condition.acquire()
            condition.notify()
            condition.release()
        elif trial < 300:
            threading.Timer(0.1, lambda: after_remove_dummy(trial + 1)).start()

    threading.Timer(0.1, remove_dummy).start()
    condition.acquire()
    condition.wait(30)  # 30 seconds should be enough for all regular usages
    condition.release()


def reload_missing(modules):
    missing_modules = {name: module for name, module in modules.items()
                       if name not in sys.modules}
    if missing_modules:
        dprint("reload missing modules")
        for name in missing_modules:
            dprint("reloading missing module", name)
            try:
                importlib.import_module(name)
            except:
                dprint("fail to reload", name)


def reload_plugin(pkg_name):
    pkg_path = os.path.join(os.path.realpath(
        sublime.packages_path()), pkg_name)
    plugins = [pkg_name + "." + os.path.splitext(f)[0]
               for f in os.listdir(pkg_path) if f.endswith(".py")]
    for plugin in plugins:
        sublime_plugin.reload_plugin(plugin)


@contextmanager
def intercepting_imports(modules):
    finder = FilterFinder(modules)
    sys.meta_path.insert(0, finder)
    try:
        yield
    finally:
        if finder in sys.meta_path:
            sys.meta_path.remove(finder)


@contextmanager
def importing_fromlist_aggresively(modules):
    orig___import__ = builtins.__import__

    @functools.wraps(orig___import__)
    def __import__(name, globals=None, locals=None, fromlist=(), level=0):
        module = orig___import__(name, globals, locals, fromlist, level)
        if fromlist and module.__name__ in modules:
            if '*' in fromlist:
                fromlist = list(fromlist)
                fromlist.remove('*')
                fromlist.extend(getattr(module, '__all__', []))
            for x in fromlist:
                if isinstance(getattr(module, x, None), types.ModuleType):
                    from_name = '{}.{}'.format(module.__name__, x)
                    if from_name in modules:
                        importlib.import_module(from_name)
        return module

    builtins.__import__ = __import__
    try:
        yield
    finally:
        builtins.__import__ = orig___import__


class FilterFinder:

    def __init__(self, modules):
        self._modules = modules
        self._stack_meter = StackMeter()

    def find_module(self, name, path=None):
        if name in self._modules:
            return self

    def load_module(self, name):
        module = self._modules[name]
        sys.modules[name] = module  # restore the module back
        with self._stack_meter as depth:
            dprint("reloading", ('| ' * depth) + '|--', name)
            try:
                return module.__loader__.load_module(name)
            except:
                if name in sys.modules:
                    del sys.modules[name]  # to indicate an error
                raise
