# AUTOGENERATED! DO NOT EDIT! File to edit: nbs/08_script.ipynb (unless otherwise specified).

__all__ = ['store_true', 'store_false', 'bool_arg', 'Param', 'anno_parser', 'args_from_prog', 'SCRIPT_INFO',
           'call_parse']

# Cell
import inspect,functools
import argparse
from .imports import *
from .utils import *

# Cell
def store_true():
    "Placeholder to pass to `Param` for `store_true` action"
    pass

# Cell
def store_false():
    "Placeholder to pass to `Param` for `store_false` action"
    pass

# Cell
def bool_arg(v):
    "Use as `type` for `Param` to get `bool` behavior"
    return str2bool(v)

# Cell
class Param:
    "A parameter in a function used in `anno_parser` or `call_parse`"
    def __init__(self, help=None, type=None, opt=True, action=None, nargs=None, const=None,
                 choices=None, required=None, default=None):
        if type==store_true:  type,action,default=None,'store_true' ,False
        if type==store_false: type,action,default=None,'store_false',True
        store_attr()

    def set_default(self, d):
        if self.default is None:
            if d==inspect.Parameter.empty: self.opt = False
            else: self.default = d
        if self.default is not None: self.help += f" (default: {self.default})"

    @property
    def pre(self): return '--' if self.opt else ''
    @property
    def kwargs(self): return {k:v for k,v in self.__dict__.items()
                              if v is not None and k!='opt' and k[0]!='_'}

# Cell
def anno_parser(func, prog=None, from_name=False):
    "Look at params (annotated with `Param`) in func and return an `ArgumentParser`"
    p = argparse.ArgumentParser(description=func.__doc__, prog=prog)
    for k,v in inspect.signature(func).parameters.items():
        param = func.__annotations__.get(k, Param())
        param.set_default(v.default)
        p.add_argument(f"{param.pre}{k}", **param.kwargs)
    p.add_argument(f"--pdb", help="Run in pdb debugger (default: False)", action='store_true')
    p.add_argument(f"--xtra", help="Parse for additional args (default: '')", type=str)
    return p

# Cell
def args_from_prog(func, prog):
    "Extract args from `prog`"
    if prog is None or '#' not in prog: return {}
    if '##' in prog: _,prog = prog.split('##', 1)
    progsp = prog.split("#")
    args = {progsp[i]:progsp[i+1] for i in range(0, len(progsp), 2)}
    for k,v in args.items():
        t = func.__annotations__.get(k, Param()).type
        if t: args[k] = t(v)
    return args

# Cell
SCRIPT_INFO = SimpleNamespace(func=None)

# Cell
def call_parse(func):
    "Decorator to create a simple CLI from `func` using `anno_parser`"
    mod = inspect.getmodule(inspect.currentframe().f_back)
    if not mod: return func

    @functools.wraps(func)
    def _f(*args, **kwargs):
        mod = inspect.getmodule(inspect.currentframe().f_back)
        if not mod: return func(*args, **kwargs)
        if not SCRIPT_INFO.func and mod.__name__=="__main__": SCRIPT_INFO.func = func.__name__
        p = anno_parser(func)
        args = p.parse_args().__dict__
        xtra = otherwise(args.pop('xtra', ''), eq(1), p.prog)
        tfunc = trace(func) if args.pop('pdb', False) else func
        tfunc(**merge(args, args_from_prog(func, xtra)))

    if mod.__name__=="__main__":
        setattr(mod, func.__name__, _f)
        SCRIPT_INFO.func = func.__name__
        return _f()
    else: return _f