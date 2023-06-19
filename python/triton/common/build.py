import contextlib
import functools
import io
import os
import shutil
import subprocess
import sys
import sysconfig

import setuptools


# TODO: is_hip shouldn't be here
def is_hip():
    import torch
    return torch.version.hip is not None


@functools.lru_cache()
def libcuda_dirs():
    locs = subprocess.check_output(["whereis", "libcuda.so"]).decode().strip().split()[1:]
    return [os.path.dirname(loc) for loc in locs]


@functools.lru_cache()
def rocm_path_dir():
    return os.getenv("ROCM_PATH", default="/opt/rocm")


@contextlib.contextmanager
def quiet():
    old_stdout, old_stderr = sys.stdout, sys.stderr
    sys.stdout, sys.stderr = io.StringIO(), io.StringIO()
    try:
        yield
    finally:
        sys.stdout, sys.stderr = old_stdout, old_stderr


def _build(name, src, srcdir):
    if is_hip():
        hip_lib_dir = os.path.join(rocm_path_dir(), "lib")
        hip_include_dir = os.path.join(rocm_path_dir(), "include")
    else:
        cuda_lib_dirs = libcuda_dirs()
        base_dir = os.path.join(os.path.dirname(__file__), os.path.pardir)
        cuda_path = os.path.join(base_dir, "third_party", "cuda")

        cu_include_dir = os.path.join(cuda_path, "include")
        triton_include_dir = os.path.join(os.path.dirname(__file__), "include")
        cuda_header = os.path.join(cu_include_dir, "cuda.h")
        triton_cuda_header = os.path.join(triton_include_dir, "cuda.h")
        if not os.path.exists(cuda_header) and os.path.exists(triton_cuda_header):
            cu_include_dir = triton_include_dir
    suffix = sysconfig.get_config_var('EXT_SUFFIX')
    so = os.path.join(srcdir, '{name}{suffix}'.format(name=name, suffix=suffix))
    # try to avoid setuptools if possible
    cc = os.environ.get("CC")
    if cc is None:
        # TODO: support more things here.
        clang = shutil.which("clang")
        gcc = shutil.which("gcc")
        cc = gcc if gcc is not None else clang
        if cc is None:
            raise RuntimeError("Failed to find C compiler. Please specify via CC environment variable.")
    # This function was renamed and made public in Python 3.10
    if hasattr(sysconfig, 'get_default_scheme'):
        scheme = sysconfig.get_default_scheme()
    else:
        scheme = sysconfig._get_default_scheme()
    # 'posix_local' is a custom scheme on Debian. However, starting Python 3.10, the default install
    # path changes to include 'local'. This change is required to use triton with system-wide python.
    if scheme == 'posix_local':
        scheme = 'posix_prefix'
    py_include_dir = sysconfig.get_paths(scheme=scheme)["include"]

    if is_hip():
        ret = subprocess.check_call([cc, src, f"-I{hip_include_dir}", f"-I{py_include_dir}", f"-I{srcdir}", "-shared", "-fPIC", f"-L{hip_lib_dir}", "-lamdhip64", "-o", so])
    else:
        cc_cmd = [cc, src, "-O3", f"-I{cu_include_dir}", f"-I{py_include_dir}", f"-I{srcdir}", "-shared", "-fPIC", "-lcuda", "-o", so]
        cc_cmd += [f"-L{dir}" for dir in cuda_lib_dirs]
        ret = subprocess.check_call(cc_cmd)

    if ret == 0:
        return so
    # fallback on setuptools
    extra_compile_args = []
    library_dirs = cuda_lib_dirs
    include_dirs = [srcdir, cu_include_dir]
    libraries = ['cuda']
    # extra arguments
    extra_link_args = []
    # create extension module
    ext = setuptools.Extension(
        name=name,
        language='c',
        sources=[src],
        include_dirs=include_dirs,
        extra_compile_args=extra_compile_args + ['-O3'],
        extra_link_args=extra_link_args,
        library_dirs=library_dirs,
        libraries=libraries,
    )
    # build extension module
    args = ['build_ext']
    args.append('--build-temp=' + srcdir)
    args.append('--build-lib=' + srcdir)
    args.append('-q')
    args = dict(
        name=name,
        ext_modules=[ext],
        script_args=args,
    )
    with quiet():
        setuptools.setup(**args)
    return so
