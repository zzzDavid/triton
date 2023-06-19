"""isort:skip_file"""
__version__ = '2.1.0'

# ---------------------------------------
# Note: import order is significant here.

# TODO: torch needs to be imported first
# or pybind11 shows `munmap_chunk(): invalid pointer`
import torch  # noqa: F401

# submodules
from .runtime import (
    autotune,
    Config,
    heuristics,
    JITFunction,
    KernelInterface,
    reinterpret,
    TensorWrapper,
    OutOfResources,
    MockTensor,
)
from .runtime.jit import jit
from .compiler import compile, CompilationError
from . import language
from . import testing

__all__ = [
    "autotune",
    "cdiv",
    "CompilationError",
    "compile",
    "Config",
    "heuristics",
    "impl",
    "jit",
    "JITFunction",
    "KernelInterface",
    "language",
    "MockTensor",
    "next_power_of_2",
    "ops",
    "OutOfResources",
    "reinterpret",
    "runtime",
    "TensorWrapper",
    "testing",
]


# -------------------------------------
# misc. utilities that  don't fit well
# into any specific module
# -------------------------------------

def cdiv(x, y):
    return (x + y - 1) // y


def next_power_of_2(n):
    """Return the smallest power of 2 greater than or equal to n"""
    n -= 1
    n |= n >> 1
    n |= n >> 2
    n |= n >> 4
    n |= n >> 8
    n |= n >> 16
    n += 1
    return n
