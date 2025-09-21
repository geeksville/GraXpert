# TODO

Note: this document is currently a virtually unstructured pile of notes for @geeksville's work
on graxpert.  You can probably ignore it

# Changelist

* Intel OpenVINO AI acceleration support added by FIXME (this should allow **much** faster processing on AVX2/VNNI capable Intel CPUs - including the N100/N300 CPUs often used in telescope miniPCs).  On even a low-end N300 CPU (with a crummy iGPU) my benchmark test shows it as a 5x speedup.
* GPU acceleration for AMD GPUs (a 15x speedup vs CPU processing: 15 minute runs (on a 16 core CPU) become 1 minute (using less than 1 core))
* Failures in processing using GPU acceleration automatically failback to using the CPU instead and print a warning message to the logs.
* In addition to the old package options, graxpert is now available on pypi for easy install with "pip install graxpert" on Windows, Mac-OS, or Linux.
* Fix a number of resource leaks while the app was running.
* Previously most failures inside of graxpert would cause the app to appear to hang.  This is now fixed, the app will exit with an exception message instead.  Please report any failures you encounter by filing a github issue at FIXME.
* The -cli command line flag is no longer required (but will be ignored if you still use it).  Just pass in command line arguments as you wish (see README.md for documentation)

# Test commands

PYTHONPATH=. python graxpert/main.py -cmd background-extraction -output /tmp/testout tests/test_images/real_crummy.fits

FIXME - follow in instructions for vc 14 runtime install, after enabling ssh
py -m pip install //host.lan/Data/dist/graxpert-3.2.0a0.dev1-py3-none-any.whl[cuda]


graxpert -cmd background-extraction -output /tmp/testout tests/test_images/real_crummy.fits

!todo: test fedora failure and use that as an example of try/catch gpu fallback
!todo: see if openvino can live together with cuda - NO IT CANT
todo: basic os-x testing of dmg install
todo: basic os-x testing of python install
todo: windows testing of exe install (at least include cuda)
!todo: linux testing of appimage install
todo: test all release builds
fix python package license warnings
todo: pypi release
todo: appimage etc... release

>  Please consider submitting your AppImage to AppImageHub, the crowd-sourced
central directory of available AppImages, by opening a pull request
at https://github.com/AppImage/appimage.github.io

todo add https://onnxruntime.ai/docs/execution-providers/OpenVINO-ExecutionProvider.html#requirements windows instructions
I think just:
pip install openvino==2025.3.0
but also these very painful user steps
https://docs.openvino.ai/2025/get-started/install-openvino/install-openvino-archive-windows.html

# prebuild wheels so that 

user doesn't need this crap:

      creating build\lib.win-amd64-cpython-313\pykrige\lib
      copying src\pykrige\lib\__init__.py -> build\lib.win-amd64-cpython-313\pykrige\lib
      running build_ext
      building 'pykrige.lib.cok' extension
      error: Microsoft Visual C++ 14.0 or greater is required. Get it with "Microsoft C++ Build Tools": https://visualstudio.microsoft.com/visual-cpp-build-tools/
      [end of output]


Yes, your instinct is exactly right. Forcing users to install a full C++ build environment is a poor experience. The standard and correct way to solve this is to **build and distribute pre-compiled wheels** for Windows.

A Python wheel (`.whl`) is a package format that can include pre-compiled extension modules (like the one `PyKrige` needs). When a Windows user runs `pip install graxpert`, pip will see the available wheels on PyPI, find the one that matches their Python version and system architecture (e.g., Python 3.11 on 64-bit Windows), and download it. This completely bypasses the need for a local compiler.

-----

### \#\# The Solution: Use `cibuildwheel`

The best tool for this job is **`cibuildwheel`**. It's designed to be run in a CI/CD environment (like GitHub Actions) to automatically build and test wheels for all major operating systems and Python versions. Since you're already using GitHub, integrating this into your release workflow is the ideal solution.

Here's how to adapt your existing release process:

#### 1\. Modify Your GitHub Actions Workflow

You'll need to add a new job to your `.github/workflows/build-release.yml` file. This job will run on a Windows virtual machine, install the necessary dependencies, and then use `cibuildwheel` to build the wheels for all the Python versions you support.

Here is a job you can add to your workflow file:

```yaml
# In .github/workflows/build-release.yml

jobs:
  # ... (keep your existing build jobs) ...

  build_windows_wheels:
    name: Build Windows wheels
    runs-on: windows-latest

    steps:
      - uses: actions/checkout@v3

      - name: Set up Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11' # A version to run cibuildwheel itself

      - name: Install cibuildwheel
        run: python -m pip install cibuildwheel

      - name: Build wheels
        run: python -m cibuildwheel --output-dir wheelhouse
        # This tells cibuildwheel to find your setup.py and build wheels
        # for all supported Python versions on Windows.

      - name: Upload artifacts
        uses: actions/upload-artifact@v3
        with:
          name: windows-wheels
          path: ./wheelhouse/*.whl
```

#### 2\. Publish to PyPI

Finally, you'll need another job that runs after all the build jobs are complete. This job will download all the artifacts (your Linux AppImages, Mac builds, and now your new Windows wheels) and upload them all to PyPI using a tool like `twine`.

This ensures that when a user on any OS runs `pip install`, the correct pre-built binary or wheel is available for them. Your `setup.py` is already well-configured to be used by `cibuildwheel`, so you likely won't need to change it.

# why does covolution run slow (runs out of VRAM)?

2025-07-28 15:28:31,227 MainProcess root INFO     Progress: 36%
2025-07-28 15:28:31,420 MainProcess root INFO     Available inference providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
2025-07-28 15:28:31,420 MainProcess root INFO     Used inference providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
MIOpen(HIP): Warning [IsEnoughWorkspace] [GetSolutionsFallback AI] Solver <GemmBwdRest>, workspace required: 67108864, provided ptr: 0x7fc959400800 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [EvaluateInvokers] Solver <GemmBwdRest>, workspace required: 67108864, provided ptr: 0x7fc959400800 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [GetSolutionsFallback AI] Solver <GemmBwdRest>, workspace required: 134217728, provided ptr: 0x7fc953400400 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [EvaluateInvokers] Solver <GemmBwdRest>, workspace required: 134217728, provided ptr: 0x7fc953400400 size: 33554432
MIOpen(HIP): Warning [IsEnoughWorkspace] [GetSolutionsFallback AI] Solver <GemmBwdRest>, workspace required: 268435456, provided ptr: 0x7fc953400000 size: 33554

I thought the problem is related to batch_size.  Trid different values as an experiment but didn't seem to change much
https://github.com/ROCm/MIOpen/issues/2981

Do incrmental tuning on model partitioning
https://github.com/ROCm/MIOpen/blob/develop/docs/conceptual/tuningdb.rst

export MIOPEN_FIND_MODE=3
export MIOPEN_FIND_ENFORCE=3
export MIOPEN_USER_DB_PATH="/workspaces/graxpert/mitune"

# windows and macos testing
https://github.com/dockur/windows
https://github.com/dockur/macos

# version
use PEP440 convention for my fork graxpert-3.2.0a0+geeksville

# rpm
sudo dnf install qt5-qtbase-gui qt5-qtx11extras 
openssl-libs ffmpeg-libs libjpeg-turbo 
libtiff libpng xz-libs libgfortran libquadmath libuuid libxkbcommon-x11

# test cuda stuff

Missing dependencies:
? libcublas.so.12
? libcublasLt.so.12
? libcudart.so.12
? libcudnn.so.9
? libcufft.so.11
? libcurand.so.10
? libnvinfer.so.10
? libnvinfer_plugin.so.10
? libnvonnxparser.so.10
? libnvrtc.so.12
This is not necessarily a problem - the dependencies may not be needed on this platform.

# building for pypi
python -m build

test pypi upload
python3 -m twine upload --repository testpypi dist/graxpert-3.2.0a0-py3-none-any.whl dist/graxpert-3.2.0a0.tar.gz 
python3 -m twine upload --repository testpypi dist/graxpert-3.2.0a0.dev4-py3-none-any.whl dist/graxpert-3.2.0a0.dev4.tar.gz 

test install locally
following works on fedora now if you manually install gcc.
pip install --user ~/development/telescope/graxpert/dist/graxpert-3.2.0a0.dev0-py3-none-any.whl

FIXME fix executable pip wrapper creation

apt install python3-tkinter

install instructions:

# Installs the base application with CPU support
pip install graxpert

# Installs the base app PLUS the ROCm-specific package

sudo dnf install rocm
sudo apt install rocm-libs

pip install graxpert[openvino]
pip install graxpert[rocm]
pip install --user --break-system-packages ~/development/telescope/graxpert/dist/graxpert-3.2.0a0.dev1-py3-none-any.whl[rocm] -f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.3/

pipx install ~/development/telescope/graxpert/dist/graxpert-3.1.0rc2.dev250919173048-py3-none-any.whl[rocm] --pip-args="-f https://repo.radeon.com/rocm/manylinux/rocm-rel-6.4.3/"

pipx install ~/development/telescope/graxpert/dist/graxpert-3.1.0rc2.dev250919182618-py3-none-any.whl[rocm] --pip-args="-f https://repo.radeon.com/rocm/manylinux/rocm-rel-7.0/"

strace -o run.strace python3 -c "import onnxruntime; print(onnxruntime.get_available_providers())"

# app timing

test timing with and without gpu acceleration



# appimage

FIXME: make command line work - test with exe first
FIXME: shrink exe

size with rocm and gpu: 5496M	exe.linux-x86_64-3.12/
size with those removed: 532M	exe.linux-x86_64-3.12/

with just the gpu code added (no amd): 982M	exe.linux-x86_64-3.12/
allmost all of that extra 500MB is:
➜  ls -l exe.linux-x86_64-3.12/lib/onnxruntime/capi/
.rwxr-xr-x@ 408M kevinh  6 Sep 16:11 libonnxruntime_providers_cuda.so

and the extra rocm stuff also:
 ls -l exe.linux-x86_64-3.12/lib/onnxruntime/capi/
.rw-r--r--@  174 kevinh  6 Sep 16:22 __init__.pyc
.rw-r--r--@  177 kevinh  6 Sep 16:22 _ld_preload.pyc
.rw-r--r--@ 1.2k kevinh  6 Sep 16:22 _pybind_state.pyc
.rw-r--r--@  284 kevinh  6 Sep 16:22 build_and_package_info.pyc
.rw-r--r--@ 160M kevinh  5 Aug 16:31 libamd_comgr.so.3.0.60403
.rw-r--r--@  28M kevinh  6 Sep 16:20 libamdhip64.so.6.4.60403
.rw-r--r--@ 101k kevinh 25 Jul 13:37 libdrm.so.2.124.0
.rw-r--r--@  73k kevinh  6 Sep 16:20 libdrm_amdgpu.so.1.124.0
.rw-r--r--@ 1.4M kevinh  6 Sep 16:21 libhipblas.so.2.4.60403
.rw-r--r--@ 7.7M kevinh  6 Sep 16:20 libhipblaslt.so.0.12.60403
.rw-r--r--@  78k kevinh  6 Sep 16:21 libhipfft.so.0.1.60403
.rw-r--r--@ 916k kevinh  5 Aug 16:37 libhiprtc.so.6.4.60403
.rw-r--r--@ 3.5M kevinh  6 Sep 16:20 libhsa-runtime64.so.1.15.60403
.rw-r--r--@  75M kevinh  5 Aug 23:40 libmigraphx.so.2012000.0.60403
.rw-r--r--@ 586k kevinh  6 Sep 16:20 libmigraphx_c.so.3.0.60403
.rw-r--r--@ 5.3M kevinh  6 Sep 16:20 libmigraphx_onnx.so.2012000.0.60403
.rw-r--r--@ 3.5M kevinh  6 Sep 16:20 libmigraphx_tf.so.2012000.0.60403
.rw-r--r--@ 707M kevinh  6 Sep 16:21 libMIOpen.so.1.0.60403
.rwxr-xr-x@  25M kevinh  6 Sep 16:18 libonnxruntime.so.1.21.0
.rwxr-xr-x@  20M kevinh  6 Sep 16:11 libonnxruntime.so.1.22.0
.rwxr-xr-x@  21M kevinh  6 Sep 11:08 libonnxruntime.so.1.22.1
.rwxr-xr-x@ 408M kevinh  6 Sep 16:11 libonnxruntime_providers_cuda.so
.rwxr-xr-x@ 585k kevinh  6 Sep 16:20 libonnxruntime_providers_migraphx.so
.rwxr-xr-x@ 1.2G kevinh  6 Sep 16:22 libonnxruntime_providers_rocm.so
.rwxr-xr-x@  16k kevinh  6 Sep 16:18 libonnxruntime_providers_shared.so
.rwxr-xr-x@ 736k kevinh  6 Sep 16:11 libonnxruntime_providers_tensorrt.so
.rw-r--r--@ 1.7G kevinh  6 Sep 16:21 librccl.so.1.0.60403
.rw-r--r--@  60M kevinh  6 Sep 16:20 librocblas.so.4.4.60403
.rw-r--r--@  11M kevinh  6 Sep 16:21 librocfft.so.0.1.60403
.rw-r--r--@  15k kevinh  5 Aug 16:19 librocm-core.so.1.0.60403
.rwxr-xr-x@ 1.5M kevinh  6 Sep 16:18 librocm_smi64-f954cc49.so.7.7.60403
.rw-r--r--@ 1.4M kevinh  5 Aug 16:20 librocm_smi64.so.7.7.60403
.rw-r--r--@ 559k kevinh  5 Aug 16:20 librocprofiler-register.so.0.4.0
.rw-r--r--@ 732M kevinh  6 Sep 16:21 librocsolver.so.0.4.60403
.rw-r--r--@ 339k kevinh  6 Sep 16:21 libroctracer64.so.4.1.60403
.rw-r--r--@  15k kevinh  5 Aug 16:40 libroctx64.so.4.1.60403
drwxr-xr-x@    - kevinh  6 Sep 16:20 migraphx
.rw-r--r--@ 1.8k kevinh  6 Sep 16:22 onnxruntime_collect_build_info.pyc
.rw-r--r--@  55k kevinh  6 Sep 16:22 onnxruntime_inference_collection.pyc
.rw-r--r--@  27M kevinh  6 Sep 16:18 onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
.rw-r--r--@ 5.2k kevinh  6 Sep 16:22 onnxruntime_validation.pyc


FIXME fix bdist_rpm bdist_deb
FIXME test windows build
CURRENT TASK FIXME make app image build not so huge 1.2G!
FIXME rpm build has all sorts of crap in it - like .git, tests etc...
FIXME add this to " build_exe --optimize=1" similar to what RPM build does

Please consider submitting your AppImage to AppImageHub, the crowd-sourced
central directory of available AppImages, by opening a pull request
at https://github.com/AppImage/appimage.github.io

https://github.com/niess/python-appimage 
https://python-appimage.readthedocs.io/en/latest/apps/ 
https://docs.appimage.org/packaging-guide/from-source/linuxdeploy-user-guide.html

NOTE: windows build will fail if version starts with a v.

git tag -a 3.2.0.dev0 -m "WIP by @geeksville, testing/using release binaries"
git push origin --tags

sudo apt-get update && sudo apt-get install -y fuse

# fixing linux-exe build

1st build as if you were making a release:
python ./setup.py install_exe --install-dir=./dist/GraXpert-linux

then the following command currently crashes:
./dist/GraXpert-linux/GraXpert

when you try to do AI background removal

Main problem:
https://g.co/gemini/share/28a977637dae <- install_exe uses static reflection to find dependencies, but it misses rocblas because those are found at _PyRuntime

Secondary problem: rocblas_abort just kills the process, workaround is to run AI stuff in its own process
https://g.co/gemini/share/d95ec917a59d

2025-07-25 18:46:13,208 MainProcess root INFO     Providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']
2025-07-25 18:46:13,208 MainProcess root INFO     Used providers : ['ROCMExecutionProvider', 'CPUExecutionProvider']

rocBLAS error: Cannot read /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/rocblas/library/TensileLibrary.dat: Illegal seek for GPU arch : gfx1100
 List of available TensileLibrary Files : 

rocBLAS error: Could not initialize Tensile host:
filesystem error: directory iterator cannot open directory: No such file or directory [/workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/rocblas/library]
Aborted (core dumped)

Thread 1 "GraXpert" received signal SIGABRT, Aborted.
__pthread_kill_implementation (threadid=<optimized out>, signo=signo@entry=6, no_tid=no_tid@entry=0) at ./nptl/pthread_kill.c:44
44      ./nptl/pthread_kill.c: No such file or directory.
(gdb) bt
#0  __pthread_kill_implementation (threadid=<optimized out>, signo=signo@entry=6, no_tid=no_tid@entry=0) at ./nptl/pthread_kill.c:44
#1  0x00007ffff7d6af4f in __pthread_kill_internal (signo=6, threadid=<optimized out>) at ./nptl/pthread_kill.c:78
#2  0x00007ffff7d1bfb2 in __GI_raise (sig=sig@entry=6) at ../sysdeps/posix/raise.c:26
#3  0x00007ffff7d06472 in __GI_abort () at ./stdlib/abort.c:79
#4  0x00007ffda4656d9f in rocblas_abort_once() () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/librocblas.so.4.4.60401
#5  0x00007ffda4656d19 in rocblas_abort () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/librocblas.so.4.4.60401
#6  0x00007ffda43a3f22 in (anonymous namespace)::get_library_and_adapter(std::shared_ptr<Tensile::MasterSolutionLibrary<Tensile::ContractionProblem, Tensile::ContractionSolution> >*, std::shared_ptr<hipDeviceProp_tR0600>*, int) () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/librocblas.so.4.4.60401
#7  0x00007ffda43b4e4c in rocblas_status_ runContractionProblem<float, float, float, float, float, float>(RocblasContractionProblem<float, float, float, float, float, float> const&, rocblas_gemm_algo_, int)
    () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/librocblas.so.4.4.60401
#8  0x00007ffda4542914 in rocblas_status_ rocblas_internal_gemm_ex<false, float const*, float const*, float const*, float*>(_rocblas_handle*, rocblas_operation_, rocblas_operation_, int, int, int, float const*, float const*, long, int, long, float const*, long, int, long, float const*, float const*, long, int, long, float*, long, int, long, int, rocblas_gemm_algo_, int, rocblas_gemm_flags_) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/librocblas.so.4.4.60401
#9  0x00007ffda453e40b in rocblas_status_ gemm_ex_typecasting<false, float, float, float>(_rocblas_handle*, rocblas_operation_, rocblas_operation_, int, int, int, void const*, void const*, long, int, long, void const*, long, int, long, void const*, void const*, long, int, long, void*, long, int, long, int, rocblas_gemm_algo_, int, rocblas_gemm_flags_) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/librocblas.so.4.4.60401
#10 0x00007ffda453d83f in rocblas_status_ rocblas_gemm_ex_template<false>(_rocblas_handle*, rocblas_operation_, rocblas_operation_, int, int, int, void const*, void const*, rocblas_datatype_, long, int, long, void const*, rocblas_datatype_, long, int, long, void const*, void const*, rocblas_datatype_, long, int, long, void*, rocblas_datatype_, long, int, long, int, rocblas_datatype_, rocblas_gemm_algo_, int, unsigned int) () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/librocblas.so.4.4.60401
--Type <RET> for more, q to quit, c to continue without paging-- 
#11 0x00007ffda4525773 in rocblas_gemm_ex () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/librocblas.so.4.4.60401
#12 0x00007ffe067fa6e5 in miopen::CallGemm(miopen::Handle const&, miopen::GemmDescriptor, void const*, unsigned long, void const*, unsigned long, void*, unsigned long, miopen::GemmBackend_t) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/libMIOpen.so.1.0.60401
#13 0x00007ffe06432b4a in ?? () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/libMIOpen.so.1.0.60401
#14 0x00007ffe0671dcbd in ?? () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/libMIOpen.so.1.0.60401
#15 0x00007ffe0670fcae in miopen::ConvolutionDescriptor::ConvolutionForward(miopen::Handle const&, void const*, miopen::TensorDescriptor const&, void const*, miopen::TensorDescriptor const&, void const*, miopenConvFwdAlgorithm_t, void const*, miopen::TensorDescriptor const&, void*, void*, unsigned long) const () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/libMIOpen.so.1.0.60401
#16 0x00007ffe05796386 in miopenConvolutionForward () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/libMIOpen.so.1.0.60401
#17 0x00007ffe161e8894 in onnxruntime::rocm::Conv<float, false>::ComputeInternal(onnxruntime::OpKernelContext*) const ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/libonnxruntime_providers_rocm.so
#18 0x00007ffe161aad0c in onnxruntime::rocm::RocmKernel::Compute(onnxruntime::OpKernelContext*) const () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/libonnxruntime_providers_rocm.so
#19 0x00007ffff6745b0f in onnxruntime::ExecuteKernel(onnxruntime::StreamExecutionContext&, unsigned long, unsigned long, bool const&, onnxruntime::SessionScope&) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#20 0x00007ffff673ba8f in onnxruntime::LaunchKernelStep::Execute(onnxruntime::StreamExecutionContext&, unsigned long, onnxruntime::SessionScope&, bool const&, bool&) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#21 0x00007ffff67484f9 in onnxruntime::RunSince(unsigned long, onnxruntime::StreamExecutionContext&, onnxruntime::SessionScope&, bool const&, unsigned long) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#22 0x00007ffff6742f73 in onnxruntime::ExecuteThePlan(onnxruntime::SessionState const&, gsl::span<int const, 18446744073709551615ul>, gsl::span<OrtValue const, 18446744073709551615ul>, gsl::span<int const, 18446744073709551615ul>, std::vector<OrtValue, std::allocator<OrtValue> >&, std::unordered_map<unsigned long, std::function<onnxruntime::common::Status (onnxruntime::TensorShape const&, OrtDevice const&, OrtValue&, bool&)>, std::hash<unsigned long>, std::equal_to<unsigned long>, std::allocator<std::pair<unsigned long const, std::function<onnxruntime::common::Status (onnxruntime::TensorShape const&, OrtDevice const&, OrtValue&, bool&)> > > > const&, onnxruntime::logging::Logger const&, onnxruntime::DeviceStreamCollection const*, bool const&, bool, bool) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#23 0x00007ffff670234c in onnxruntime::utils::ExecuteGraphImpl(onnxruntime::SessionState const&, onnxruntime::FeedsFetchesManager const&, gsl::span<OrtValue const, 18446744073709551615ul>, std::vector<OrtValue, std::allocator<OrtValue> >&, std::unordered_map<unsigned long, std::function<onnxruntime::common::Status (onnxruntime::TensorShape const&, OrtDevice const&, OrtValue&, bool&)>, std::hash<unsigned long>, std::equal_to<unsigned long>, std::allocator<std::pair<unsigned long const, std::function<onnxruntime::common::Status (onnxruntime::TensorShape const&, OrtDevice const&, OrtValue&, bool&)> > > > const&, ExecutionMode, bool const&, onnxruntime::logging::Logger const&, onnxruntime::DeviceStreamCollection*, bool, onnxruntime::Stream*) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#24 0x00007ffff670593e in onnxruntime::utils::ExecuteGraph(onnxruntime::SessionState const&, onnxruntime::FeedsFetchesManager&, gsl::span<OrtValue const, 18446744073709551615ul>, std::vector<OrtValue, std::allocator<OrtValue> >&, ExecutionMode, bool const&, onnxruntime::logging::Logger const&, onnxruntime::DeviceStreamCollectionHolder&, bool, onnxruntime::Stream*) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#25 0x00007ffff6705cea in onnxruntime::utils::ExecuteGraph(onnxruntime::SessionState const&, onnxruntime::FeedsFetchesManager&, gsl::span<OrtValue const, 18446744073709551615ul>, std::vector<OrtValue, std::allocator<OrtValue> >&, ExecutionMode, OrtRunOptions const&, onnxruntime::DeviceStreamCollectionHolder&, onnxruntime::logging::Logger const&) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#26 0x00007ffff5d40ecc in onnxruntime::InferenceSession::Run(OrtRunOptions const&, gsl::span<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, 18446744073709551615ul>, gsl::span<OrtValue const, 18446744073709551615ul>, gsl::span<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, 18446744073709551615ul>, std::vector<OrtValue, std::allocator<OrtValue> >*, std::vector<OrtDevice, std::allocator<OrtDevice> > const*) [clone .localalias] ()
--Type <RET> for more, q to quit, c to continue without paging--
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#27 0x00007ffff5d425c7 in onnxruntime::InferenceSession::Run(OrtRunOptions const&, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, OrtValue, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, OrtValue> > > const&, gsl::span<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, 18446744073709551615ul>, std::vector<OrtValue, std::allocator<OrtValue> >*) () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#28 0x00007ffff5d4271a in onnxruntime::InferenceSession::Run(std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, OrtValue, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, OrtValue> > > const&, gsl::span<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, 18446744073709551615ul>, std::vector<OrtValue, std::allocator<OrtValue> >*) () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#29 0x00007ffff5ce30c4 in onnxruntime::python::addObjectMethods(pybind11::module_&, std::function<void (onnxruntime::InferenceSession*, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > >, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > > > > > const&)>)::{lambda(onnxruntime::python::PyInferenceSession*, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, std::map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, pybind11::object const, std::less<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, pybind11::object const> > > const&, OrtRunOptions*)#1}::operator()(onnxruntime::python::PyInferenceSession*, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, std::map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, pybind11::object const, std::less<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, pybind11::object const> > > const&, OrtRunOptions*) const [clone .isra.0] () from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#30 0x00007ffff5d03b2a in pybind11::cpp_function::initialize<onnxruntime::python::addObjectMethods(pybind11::module_&, std::function<void (onnxruntime::InferenceSession*, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > >, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > > > > > const&)>)::{lambda(onnxruntime::python::PyInferenceSession*, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, std::map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, pybind11::object co--Type <RET> for more, q to quit, c to continue without paging--
nst, std::less<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, pybind11::object const> > > const&, OrtRunOptions*)#1}, pybind11::list, onnxruntime::python::PyInferenceSession*, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, std::map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, pybind11::object const, std::less<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, pybind11::object const> > > const&, OrtRunOptions*, pybind11::name, pybind11::is_method, pybind11::sibling>(onnxruntime::python::addObjectMethods(pybind11::module_&, std::function<void (onnxruntime::InferenceSession*, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > >, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, std::unordered_map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::hash<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::equal_to<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > > > > > const&)>)::{lambda(onnxruntime::python::PyInferenceSession*, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, std::map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, pybind11::object const, std::less<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, pybind11::object const> > > const&, OrtRunOptions*)#1}&&, pybind11::list (*)(onnxruntime::python::PyInferenceSession*, std::vector<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, std::allocator<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > > > const&, std::map<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> >, pybind11::object const, std::less<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > >, std::allocator<std::pair<std::__cxx11::basic_string<char, std::char_traits<char>, std::allocator<char> > const, pybind11::object const> > > const&, OrtRunOptions*), pybind11::name const&, pybind11::is_method const&, pybind11::sibling const&)::{lambda(pybind11::detail::function_call&)#1}::_FUN(pybind11::detail::function_call&) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#31 0x00007ffff5c64f2f in pybind11::cpp_function::dispatcher(_object*, _object*, _object*) ()
   from /workspaces/graxpert/dist/GraXpert-linux/lib/onnxruntime/capi/onnxruntime_pybind11_state.cpython-312-x86_64-linux-gnu.so
#32 0x0000000000607773 in ?? ()
#33 0x000000000042bbd7 in _PyObject_MakeTpCall ()
#34 0x0000000000423f8b in _PyEval_EvalFrameDefault ()
#35 0x00000000005e959f in ?? ()
#36 0x000000000041f696 in _PyEval_EvalFrameDefault ()
#37 0x00000000005e959f in ?? ()
#38 0x00007ffff4d492de in ?? () from /workspaces/graxpert/dist/GraXpert-linux/lib/_tkinter.cpython-312-x86_64-linux-gnu.so
#39 0x00007fffa211c682 in TclNRRunCallbacks () from /workspaces/graxpert/dist/GraXpert-linux/lib/libtcl8-298ddd75.6.so
#40 0x00007fffa211e58e in ?? () from /workspaces/graxpert/dist/GraXpert-linux/lib/libtcl8-298ddd75.6.so
#41 0x00007fffa211edc3 in Tcl_EvalEx () from /workspaces/graxpert/dist/GraXpert-linux/lib/libtcl8-298ddd75.6.so
#42 0x00007fffa22dec75 in Tk_BindEvent () from /workspaces/graxpert/dist/GraXpert-linux/lib/libtk8-73f22597.6.so
#43 0x00007fffa22e3923 in TkBindEventProc () from /workspaces/graxpert/dist/GraXpert-linux/lib/libtk8-73f22597.6.so
--Type <RET> for more, q to quit, c to continue without paging--
#44 0x00007fffa22ebb9a in Tk_HandleEvent () from /workspaces/graxpert/dist/GraXpert-linux/lib/libtk8-73f22597.6.so
#45 0x00007fffa22ebdc0 in ?? () from /workspaces/graxpert/dist/GraXpert-linux/lib/libtk8-73f22597.6.so
#46 0x00007fffa21e6d49 in Tcl_ServiceEvent () from /workspaces/graxpert/dist/GraXpert-linux/lib/libtcl8-298ddd75.6.so
#47 0x00007fffa21e6fa5 in Tcl_DoOneEvent () from /workspaces/graxpert/dist/GraXpert-linux/lib/libtcl8-298ddd75.6.so
#48 0x00007ffff4d42c41 in ?? () from /workspaces/graxpert/dist/GraXpert-linux/lib/_tkinter.cpython-312-x86_64-linux-gnu.so
#49 0x00000000005f25f6 in ?? ()
#50 0x000000000042c291 in PyObject_Vectorcall ()
#51 0x0000000000423f8b in _PyEval_EvalFrameDefault ()
#52 0x00000000005e96cc in ?? ()
#53 0x000000000041f696 in _PyEval_EvalFrameDefault ()
#54 0x00000000004be754 in PyEval_EvalCode ()
#55 0x00000000004bbcc4 in ?? ()
#56 0x000000000060785f in ?? ()
#57 0x000000000042c291 in PyObject_Vectorcall ()
#58 0x0000000000423f8b in _PyEval_EvalFrameDefault ()
#59 0x000000000042de82 in PyObject_CallObject ()
#60 0x000000000041eacd in main ()

## Tell users required preinstalls for linux-exe builds

If you want to use AMD GPU acceleration you'll need to install for your OS (Fedora or Ubuntu etc...)
https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html

sudo dnf install libXrender mesa-libGL numactl-libs

sudo apt-get update && sudo apt-get install -y libxrender1 libgl1 libnuma1

# post 

Hi ya'll,

So I'm a noob at astrophoto/telescope stuff, but I've been worried about leaving my rig outside and unexpected rain or heavier than forecast winds.  I'm also a little bit of a geek so I was looking for something that would ring a loud alarm on my cellphone while I slumber.

I just got my first small rain and a proper prompt alarm so I thought I'd write this little recipe in case it is useful for others.

Required hw/software:

An "Ecowitt Wittboy GW2001" weather station ($200).  I suspect other options would work as well - as long as they have a feature that allows sending an email based on alarm thresholds.  This one was well reviewed and 'open' with no nasty subscription fees.  No moving parts.
Pushover.net app.  I've used them for years on many different projects - they are IMO non sleazy.  For small usage (i.e. this) it is free for the app and no subscription needed.  Android/iOS.  
Steps:

Install wittboy per directions (it connects to wifi).
Install pushover app on your phone and link it to your new pushover acct.
Go to pushover website (here) and have them create an email mailbox for your alerts.
Change the priority of the alert to 1 (high priority - so by default it will ring a loud alarm while you are sleeping).  Later you can easily enable/disable this behavior in the app when you are imaging/not-imaging.
(optional) Change "Replace URL" to the status page for your weather station (see below), it will look something like: https://www.ecowitt.net/home/index?id=xxxx 
Save that page and then copy the generated email address it makes (you will use this in the next step).  It will look something like xyzzy123@pomail.net.
Go to the ecowitt alarms page to add the alarm.  Have it email to the pomail addr and create two alarms: one for "Rainfall Piezo: Event is greater than 0.01 in" and one for "Wind: Wind Gust is greater than 15.0 mph".
(optional) in the pushover app you can assign a special alarm sound (or disable alarms when your telescope is not outside) and tell it to ignore do-not-disturb times as needed.
(optional and advanced) If you have a more customizable imaging controller (I'm currently just using an asiair - so not an option for me ...yet), Pushover has an easy URL based API so I bet you could have the the controller enable pushover alarms on/off any time imaging starts/stops.
YMMV but a very light sprinkling the other night promptly started my cellphone yelling at me.

# Bugs to fix

https://github.com/Steffenhir/GraXpert/issues/179

# Misc

podman build --network=slirp4netns --security-opt=label=disable --tag graxpertcmd .
podman run -it --rm graxpertcmd bash

docker run --rm \
  -v ~/Pictures/telescope:/data \
  your-image-name \
  --input /data/image.fits

must use abs path
  docker run -v /local/path/to/file1.txt:/container/path/to/file1.txt
-mount type=bind,src=.,dst=/project,ro,Z

sudo docker cp goofy_roentgen:/out_read.jpg .

docker run -v /local/path/to/file1.txt:/container/path/to/file1.txt
crashes with glibc malloc mem corruption
python -m graxpert.main /images/testdata/Stacked_492_M\ 13_20.0s_IRCUT_20250712-010002.fit --cli --ai_version 1.0.1 --correction Division --smoothing 0.1 --bg

--gpu false hides the problem
/usr/local/bin/python -m graxpert.main /images/testdata/Stacked_492_M\ 13_20.0s_IRCUT_20250712-010002.fit -cli -ai_version 1.0.1 -correction Division -smoothing 0.1
 -bg -gpu false -out /tmp/out.tiff

special options with files
--output x
--preferences_file x 
inputfilename

run_graxpert.sh srcfile --preferences_file --output outfile --otheroptions

to force a hang: select various different stretch options then do AI background extraction.

# Todo 

* build python binary package and use that in the container version
* distribute AI model files via ghcr
* make a top level github team 

# Old
per https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/quick-start.html

setup debian guest
wget https://repo.radeon.com/amdgpu-install/6.4.1/ubuntu/jammy/amdgpu-install_6.4.60401-1_all.deb
sudo apt install ./amdgpu-install_6.4.60401-1_all.deb
sudo apt update
# sudo apt install -y python3-setuptools python3-wheel
sudo usermod -a -G render,video $USER # Add the current user to the render and video groups
sudo apt install rocm




setup fedora host
per https://rocm.docs.amd.com/projects/install-on-linux/en/latest/install/prerequisites.html#group-permissions

either:

sudo usermod -a -G video,render $LOGNAME
echo 'ADD_EXTRA_GROUPS=1' | sudo tee -a /etc/adduser.conf
echo 'EXTRA_GROUPS=video' | sudo tee -a /etc/adduser.conf
echo 'EXTRA_GROUPS=render' | sudo tee -a /etc/adduser.conf

or:
/etc/udev/rules.d/70-amdgpu.rules
KERNEL=="kfd", MODE="0666"
SUBSYSTEM=="drm", KERNEL=="renderD*", MODE="0666"
/etc/udev/rules.d/70-amdgpu.rules

rocm-smi to test

Bus error (core dumped)
/usr/local/lib/python3.13/multiprocessing/resource_tracker.py:301: UserWarning: resource_tracker: There appear to be 1 leaked shared_memory objects to clean up at shutdown: {'/psm_a8d6015e'}
  warnings.warn(

Current thread 0x00007f0f013b8b80 (most recent call first):
  File "/workspaces/graxpert/graxpert/stretch.py", line 74 in stretch_all
  File "/workspaces/graxpert/graxpert/AstroImageRepository.py", line 85 in stretch_all
  File "/workspaces/graxpert/graxpert/application/app.py", line 560 in do_stretch
  File "/workspaces/graxpert/graxpert/application/app.py", line 549 in on_stretch_option_changed
  File "/workspaces/graxpert/graxpert/application/eventbus.py", line 21 in emit
  File "/workspaces/graxpert/graxpert/ui/statusbar.py", line 22 in <lambda>
  File "/usr/local/lib/python3.13/tkinter/__init__.py", line 2068 in __call__
  File "/usr/local/lib/python3.13/tkinter/__init__.py", line 427 in set
  File "/home/vscode/.local/lib/python3.13/site-packages/customtkinter/windows/widgets/ctk_optionmenu.py", line 381 in _dropdown_callback
  File "/home/vscode/.local/lib/python3.13/site-packages/customtkinter/windows/widgets/core_widget_classes/dropdown_menu.py", line 106 in _button_callback
  File "/home/vscode/.local/lib/python3.13/site-packages/customtkinter/windows/widgets/core_widget_classes/dropdown_menu.py", line 96 in <lambda>
  File "/usr/local/lib/python3.13/tkinter/__init__.py", line 2068 in __call__
  File "/usr/local/lib/python3.13/tkinter/__init__.py", line 1599 in mainloop
  File "/home/vscode/.local/lib/python3.13/site-packages/customtkinter/windows/ctk_tk.py", line 165 in mainloop
  File "/workspaces/graxpert/graxpert/main.py", line 187 in ui_main
  File "/workspaces/graxpert/graxpert/main.py", line 405 in main
  File "/workspaces/graxpert/graxpert/main.py", line 412 in <module>
  File "<frozen runpy>", line 88 in _run_code
  File "<frozen runpy>", line 198 in _run_module_as_main

  data.flags
  C_CONTIGUOUS : False
  F_CONTIGUOUS : False
  OWNDATA : True
  WRITEABLE : True
  ALIGNED : True
  WRITEBACKIFCOPY : False



## debugging native crashes in python
  
python3-dbg -m venv graxpert-env
source graxpert-env/bin/activate
python3-dbg -m pip install -r requirements.txt
python3-dbg -m graxpert.main
gdb --args graxpert-env/bin/python3 -m graxpert.main

### Sample crash

the differing flags don't matter, because even if I copy data.copy() doesn't help
copy.flags
  C_CONTIGUOUS : True
  F_CONTIGUOUS : False
  OWNDATA : False
  WRITEABLE : True
  ALIGNED : True
  WRITEBACKIFCOPY : False
data.flags
  C_CONTIGUOUS : False
  F_CONTIGUOUS : False
  OWNDATA : True
  WRITEABLE : True
  ALIGNED : True
  WRITEBACKIFCOPY : False


Thread 1 "python3" received signal SIGBUS, Bus error.
0x00007ffff506cbd5 in _aligned_strided_to_contig_size4 () from /workspaces/graxpert/graxpert-env/lib/python3.11/site-packages/numpy/_core/_multiarray_umath.cpython-311-x86_64-linux-gnu.so
(gdb) bt
#0  0x00007ffff506cbd5 in _aligned_strided_to_contig_size4 () from /workspaces/graxpert/graxpert-env/lib/python3.11/site-packages/numpy/_core/_multiarray_umath.cpython-311-x86_64-linux-gnu.so
#1  0x00007ffff512fb06 in raw_array_assign_array () from /workspaces/graxpert/graxpert-env/lib/python3.11/site-packages/numpy/_core/_multiarray_umath.cpython-311-x86_64-linux-gnu.so
#2  0x00007ffff5130857 in PyArray_AssignArray () from /workspaces/graxpert/graxpert-env/lib/python3.11/site-packages/numpy/_core/_multiarray_umath.cpython-311-x86_64-linux-gnu.so
#3  0x00007ffff51291b0 in PyArray_CopyObject () from /workspaces/graxpert/graxpert-env/lib/python3.11/site-packages/numpy/_core/_multiarray_umath.cpython-311-x86_64-linux-gnu.so
#4  0x00007ffff518bd3a in array_assign_subscript () from /workspaces/graxpert/graxpert-env/lib/python3.11/site-packages/numpy/_core/_multiarray_umath.cpython-311-x86_64-linux-gnu.so
#5  0x0000000000493272 in PyObject_SetItem (o=o@entry=<numpy.ndarray at remote 0x7ffff725f640>, key=key@entry=<slice at remote 0x7fffb2b94a50>, value=value@entry=<numpy.ndarray at remote 0x7fffb2bf6d40>)
    at ../Objects/abstract.c:212
#6  0x000000000057b4c3 in _PyEval_EvalFrameDefault (tstate=0xabf2d8 <_PyRuntime+166328>, frame=0x7ffff785fb98, throwflag=<optimized out>) at ../Python/ceval.c:2301
#7  0x000000000058a07b in _PyEval_EvalFrame (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, frame=frame@entry=0x7ffff785f8a8, throwflag=throwflag@entry=0) at ../Include/internal/pycore_ceval.h:73
#8  0x000000000058a17c in _PyEval_Vector (tstate=0xabf2d8 <_PyRuntime+166328>, func=0x7fffb2670940, locals=locals@entry=0x0, args=0x7fffb26d8e48, argcount=<optimized out>, kwnames=0x0)
    at ../Python/ceval.c:6435
#9  0x00000000004a9be2 in _PyFunction_Vectorcall (func=<optimized out>, stack=<optimized out>, nargsf=<optimized out>, kwnames=<optimized out>) at ../Objects/call.c:393
#10 0x00000000004a97e2 in _PyVectorcall_Call (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=0x4a9b95 <_PyFunction_Vectorcall>, callable=callable@entry=<function at remote 0x7fffb2670940>, 
    tuple=tuple@entry=('PY_VAR46', '', 'write'), kwargs=kwargs@entry=0x0) at ../Objects/call.c:245
#11 0x00000000004a9b2c in _PyObject_Call (tstate=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<function at remote 0x7fffb2670940>, args=args@entry=('PY_VAR46', '', 'write'), kwargs=kwargs@entry=0x0)
    at ../Objects/call.c:328
#12 0x00000000004a9b6f in PyObject_Call (callable=callable@entry=<function at remote 0x7fffb2670940>, args=args@entry=('PY_VAR46', '', 'write'), kwargs=kwargs@entry=0x0) at ../Objects/call.c:355
#13 0x000000000057835b in do_call_core (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=func@entry=<function at remote 0x7fffb2670940>, callargs=callargs@entry=('PY_VAR46', '', 'write'), 
    kwdict=kwdict@entry=0x0, use_tracing=0) at ../Python/ceval.c:7353
#14 0x0000000000588945 in _PyEval_EvalFrameDefault (tstate=0xabf2d8 <_PyRuntime+166328>, frame=0x7ffff785f830, throwflag=<optimized out>) at ../Python/ceval.c:5379
#15 0x000000000058a07b in _PyEval_EvalFrame (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, frame=frame@entry=0x7ffff785f830, throwflag=throwflag@entry=0) at ../Include/internal/pycore_ceval.h:73
#16 0x000000000058a17c in _PyEval_Vector (tstate=0xabf2d8 <_PyRuntime+166328>, func=0x7fffa25120a0, locals=locals@entry=0x0, args=0x7fffffffba00, argcount=<optimized out>, kwnames=0x0)
    at ../Python/ceval.c:6435
#17 0x00000000004a9be2 in _PyFunction_Vectorcall (func=<optimized out>, stack=<optimized out>, nargsf=<optimized out>, kwnames=<optimized out>) at ../Objects/call.c:393
--Type <RET> for more, q to quit, c to continue without paging--c
#18 0x00000000004abfe0 in _PyObject_VectorcallTstate (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<function at remote 0x7fffa25120a0>, args=args@entry=0x7fffffffba00, 
    nargsf=nargsf@entry=4, kwnames=kwnames@entry=0x0) at ../Include/internal/pycore_call.h:92
#19 0x00000000004ac10b in method_vectorcall (method=<optimized out>, args=0x7fffb26d9028, nargsf=<optimized out>, kwnames=0x0) at ../Objects/classobject.c:89
#20 0x00000000004a97e2 in _PyVectorcall_Call (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=0x4ac056 <method_vectorcall>, callable=callable@entry=<method at remote 0x7fffb2befd70>, 
    tuple=tuple@entry=('PY_VAR46', '', 'write'), kwargs=kwargs@entry=0x0) at ../Objects/call.c:245
#21 0x00000000004a9b2c in _PyObject_Call (tstate=0xabf2d8 <_PyRuntime+166328>, callable=<method at remote 0x7fffb2befd70>, args=args@entry=('PY_VAR46', '', 'write'), kwargs=kwargs@entry=0x0)
    at ../Objects/call.c:328
#22 0x00000000004a9b6f in PyObject_Call (callable=<optimized out>, args=args@entry=('PY_VAR46', '', 'write'), kwargs=kwargs@entry=0x0) at ../Objects/call.c:355
#23 0x00007ffff7192dea in PythonCmd (clientData=0x7fffb2be3d90, interp=0x2bef6c0, objc=<optimized out>, objv=0x2bf4020) at Modules/_tkinter.c:2233
#24 0x00007fffa1f1e0c8 in TclNRRunCallbacks () from /lib/x86_64-linux-gnu/libtcl8.6.so
#25 0x00007fffa1f1f3d3 in ?? () from /lib/x86_64-linux-gnu/libtcl8.6.so
#26 0x00007fffa1f1ee43 in Tcl_EvalEx () from /lib/x86_64-linux-gnu/libtcl8.6.so
#27 0x00007fffa20117fc in ?? () from /lib/x86_64-linux-gnu/libtcl8.6.so
#28 0x00007fffa2011f4b in TclCallVarTraces () from /lib/x86_64-linux-gnu/libtcl8.6.so
#29 0x00007fffa201a7b7 in ?? () from /lib/x86_64-linux-gnu/libtcl8.6.so
#30 0x00007fffa201a5f4 in Tcl_ObjSetVar2 () from /lib/x86_64-linux-gnu/libtcl8.6.so
#31 0x00007fffa201a523 in Tcl_SetVar2Ex () from /lib/x86_64-linux-gnu/libtcl8.6.so
#32 0x00007ffff7192b10 in SetVar (self=0x7fff3ce8be20, args=<optimized out>, flags=513) at Modules/_tkinter.c:1733
#33 0x00007ffff719383e in var_invoke (func=func@entry=0x7ffff7192a05 <SetVar>, selfptr=<_tkinter.tkapp at remote 0x7fff3ce8be20>, args=('PY_VAR46', '15% Bg, 3 sigma'), flags=flags@entry=513)
    at Modules/_tkinter.c:1712
#34 0x00007ffff71939f8 in Tkapp_GlobalSetVar (self=<optimized out>, args=<optimized out>) at Modules/_tkinter.c:1779
#35 0x00000000004b483e in method_vectorcall_VARARGS (func=<method_descriptor at remote 0x7fffa24fbbf0>, args=0x7ffff785f818, nargsf=<optimized out>, kwnames=<optimized out>) at ../Objects/descrobject.c:330
#36 0x00000000004a9f06 in _PyObject_VectorcallTstate (tstate=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<method_descriptor at remote 0x7fffa24fbbf0>, args=args@entry=0x7ffff785f818, 
    nargsf=9223372036854775811, kwnames=kwnames@entry=0x0) at ../Include/internal/pycore_call.h:92
#37 0x00000000004a9fd1 in PyObject_Vectorcall (callable=callable@entry=<method_descriptor at remote 0x7fffa24fbbf0>, args=args@entry=0x7ffff785f818, nargsf=<optimized out>, kwnames=kwnames@entry=0x0)
    at ../Objects/call.c:299
#38 0x0000000000585e6d in _PyEval_EvalFrameDefault (tstate=0xabf2d8 <_PyRuntime+166328>, frame=0x7ffff785f7b8, throwflag=<optimized out>) at ../Python/ceval.c:4772
#39 0x000000000058a07b in _PyEval_EvalFrame (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, frame=frame@entry=0x7ffff785f668, throwflag=throwflag@entry=0) at ../Include/internal/pycore_ceval.h:73
#40 0x000000000058a17c in _PyEval_Vector (tstate=0xabf2d8 <_PyRuntime+166328>, func=0x7fffb26720a0, locals=locals@entry=0x0, args=0xaa4f50 <_PyRuntime+58928>, argcount=<optimized out>, kwnames=0x0)
    at ../Python/ceval.c:6435
#41 0x00000000004a9be2 in _PyFunction_Vectorcall (func=<optimized out>, stack=<optimized out>, nargsf=<optimized out>, kwnames=<optimized out>) at ../Objects/call.c:393
#42 0x00000000004a97e2 in _PyVectorcall_Call (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=0x4a9b95 <_PyFunction_Vectorcall>, callable=callable@entry=<function at remote 0x7fffb26720a0>, 
    tuple=tuple@entry=(), kwargs=kwargs@entry=0x0) at ../Objects/call.c:245
#43 0x00000000004a9b2c in _PyObject_Call (tstate=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<function at remote 0x7fffb26720a0>, args=args@entry=(), kwargs=kwargs@entry=0x0)
    at ../Objects/call.c:328
#44 0x00000000004a9b6f in PyObject_Call (callable=callable@entry=<function at remote 0x7fffb26720a0>, args=args@entry=(), kwargs=kwargs@entry=0x0) at ../Objects/call.c:355
#45 0x000000000057835b in do_call_core (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=func@entry=<function at remote 0x7fffb26720a0>, callargs=callargs@entry=(), kwdict=kwdict@entry=0x0, 
    use_tracing=0) at ../Python/ceval.c:7353
#46 0x0000000000588945 in _PyEval_EvalFrameDefault (tstate=0xabf2d8 <_PyRuntime+166328>, frame=0x7ffff785f5f0, throwflag=<optimized out>) at ../Python/ceval.c:5379
#47 0x000000000058a07b in _PyEval_EvalFrame (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, frame=frame@entry=0x7ffff785f5f0, throwflag=throwflag@entry=0) at ../Include/internal/pycore_ceval.h:73
#48 0x000000000058a17c in _PyEval_Vector (tstate=0xabf2d8 <_PyRuntime+166328>, func=0x7fffa25120a0, locals=locals@entry=0x0, args=0x7fffffffc5f8, argcount=<optimized out>, kwnames=0x0)
    at ../Python/ceval.c:6435
#49 0x00000000004a9be2 in _PyFunction_Vectorcall (func=<optimized out>, stack=<optimized out>, nargsf=<optimized out>, kwnames=<optimized out>) at ../Objects/call.c:393
#50 0x00000000004abfe0 in _PyObject_VectorcallTstate (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<function at remote 0x7fffa25120a0>, args=args@entry=0x7fffffffc5f8, 
    nargsf=nargsf@entry=1, kwnames=kwnames@entry=0x0) at ../Include/internal/pycore_call.h:92
#51 0x00000000004ac197 in method_vectorcall (method=<optimized out>, args=0xaa4f50 <_PyRuntime+58928>, nargsf=<optimized out>, kwnames=0x0) at ../Objects/classobject.c:67
#52 0x00000000004a97e2 in _PyVectorcall_Call (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=0x4ac056 <method_vectorcall>, callable=callable@entry=<method at remote 0x7fffb26b12b0>, 
    tuple=tuple@entry=(), kwargs=kwargs@entry=0x0) at ../Objects/call.c:245
#53 0x00000000004a9b2c in _PyObject_Call (tstate=0xabf2d8 <_PyRuntime+166328>, callable=<method at remote 0x7fffb26b12b0>, args=args@entry=(), kwargs=kwargs@entry=0x0) at ../Objects/call.c:328
#54 0x00000000004a9b6f in PyObject_Call (callable=<optimized out>, args=args@entry=(), kwargs=kwargs@entry=0x0) at ../Objects/call.c:355
#55 0x00007ffff7192dea in PythonCmd (clientData=0x7fffb26ac160, interp=0x2bef6c0, objc=<optimized out>, objv=0x2bf3d60) at Modules/_tkinter.c:2233
#56 0x00007fffa1f1e0c8 in TclNRRunCallbacks () from /lib/x86_64-linux-gnu/libtcl8.6.so
#57 0x00007fffa211bb48 in ?? () from /lib/x86_64-linux-gnu/libtk8.6.so
#58 0x00007fffa211b3ca in ?? () from /lib/x86_64-linux-gnu/libtk8.6.so
#59 0x00007fffa1f1e0c8 in TclNRRunCallbacks () from /lib/x86_64-linux-gnu/libtcl8.6.so
#60 0x00007fffa1f1f3d3 in ?? () from /lib/x86_64-linux-gnu/libtcl8.6.so
#61 0x00007fffa1f1ee43 in Tcl_EvalEx () from /lib/x86_64-linux-gnu/libtcl8.6.so
#62 0x00007fffa20db3ca in Tk_BindEvent () from /lib/x86_64-linux-gnu/libtk8.6.so
#63 0x00007fffa20e33bb in TkBindEventProc () from /lib/x86_64-linux-gnu/libtk8.6.so
#64 0x00007fffa20ebc39 in Tk_HandleEvent () from /lib/x86_64-linux-gnu/libtk8.6.so
#65 0x00007fffa20ec320 in ?? () from /lib/x86_64-linux-gnu/libtk8.6.so
#66 0x00007fffa1fea92f in Tcl_ServiceEvent () from /lib/x86_64-linux-gnu/libtcl8.6.so
#67 0x00007fffa1feab46 in Tcl_DoOneEvent () from /lib/x86_64-linux-gnu/libtcl8.6.so
#68 0x00007ffff718f5a4 in _tkinter_tkapp_mainloop_impl (self=self@entry=0x7fff3ce8be20, threshold=threshold@entry=0) at Modules/_tkinter.c:2717
#69 0x00007ffff718f72f in _tkinter_tkapp_mainloop (self=0x7fff3ce8be20, args=0x7ffff785f5e8, nargs=<optimized out>) at Modules/clinic/_tkinter.c.h:532
#70 0x00000000004b47c4 in method_vectorcall_FASTCALL (func=<method_descriptor at remote 0x7fffa25085f0>, args=0x7ffff785f5e0, nargsf=<optimized out>, kwnames=<optimized out>) at ../Objects/descrobject.c:407
#71 0x00000000004a9f06 in _PyObject_VectorcallTstate (tstate=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<method_descriptor at remote 0x7fffa25085f0>, args=args@entry=0x7ffff785f5e0, 
    nargsf=9223372036854775810, kwnames=kwnames@entry=0x0) at ../Include/internal/pycore_call.h:92
#72 0x00000000004a9fd1 in PyObject_Vectorcall (callable=callable@entry=<method_descriptor at remote 0x7fffa25085f0>, args=args@entry=0x7ffff785f5e0, nargsf=<optimized out>, kwnames=kwnames@entry=0x0)
    at ../Objects/call.c:299
#73 0x0000000000585e6d in _PyEval_EvalFrameDefault (tstate=0xabf2d8 <_PyRuntime+166328>, frame=0x7ffff785f580, throwflag=<optimized out>) at ../Python/ceval.c:4772
#74 0x000000000058a07b in _PyEval_EvalFrame (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, frame=frame@entry=0x7ffff785f580, throwflag=throwflag@entry=0) at ../Include/internal/pycore_ceval.h:73
#75 0x000000000058a17c in _PyEval_Vector (tstate=0xabf2d8 <_PyRuntime+166328>, func=0x7fffa25103c0, locals=locals@entry=0x0, args=0x7fffffffd238, argcount=<optimized out>, kwnames=0x0)
    at ../Python/ceval.c:6435
#76 0x00000000004a9be2 in _PyFunction_Vectorcall (func=<optimized out>, stack=<optimized out>, nargsf=<optimized out>, kwnames=<optimized out>) at ../Objects/call.c:393
#77 0x00000000004abfe0 in _PyObject_VectorcallTstate (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<function at remote 0x7fffa25103c0>, args=args@entry=0x7fffffffd238, 
    nargsf=nargsf@entry=1, kwnames=kwnames@entry=0x0) at ../Include/internal/pycore_call.h:92
#78 0x00000000004ac197 in method_vectorcall (method=<optimized out>, args=0xaa4f50 <_PyRuntime+58928>, nargsf=<optimized out>, kwnames=0x0) at ../Objects/classobject.c:67
#79 0x00000000004a97e2 in _PyVectorcall_Call (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=0x4ac056 <method_vectorcall>, callable=callable@entry=<method at remote 0x7fff3f535550>, 
    tuple=tuple@entry=(), kwargs=kwargs@entry={}) at ../Objects/call.c:245
#80 0x00000000004a9b2c in _PyObject_Call (tstate=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<method at remote 0x7fff3f535550>, args=args@entry=(), kwargs=kwargs@entry={}) at ../Objects/call.c:328
#81 0x00000000004a9b6f in PyObject_Call (callable=callable@entry=<method at remote 0x7fff3f535550>, args=args@entry=(), kwargs=kwargs@entry={}) at ../Objects/call.c:355
#82 0x000000000057835b in do_call_core (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=func@entry=<method at remote 0x7fff3f535550>, callargs=callargs@entry=(), kwdict=kwdict@entry={}, use_tracing=0)
    at ../Python/ceval.c:7353
#83 0x0000000000588945 in _PyEval_EvalFrameDefault (tstate=0xabf2d8 <_PyRuntime+166328>, frame=0x7ffff785f4f0, throwflag=<optimized out>) at ../Python/ceval.c:5379
#84 0x000000000058a07b in _PyEval_EvalFrame (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, frame=frame@entry=0x7ffff785f1b8, throwflag=throwflag@entry=0) at ../Include/internal/pycore_ceval.h:73
#85 0x000000000058a17c in _PyEval_Vector (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=func@entry=0x7ffff76a0470, 
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': 'graxpert', '__loader__': <SourceFileLoader(name='graxpert.main', path='/workspaces/graxpert/graxpert/main.py') at remote 0x7ffff7810920>, '__spec__': <ModuleSpec(name='graxpert.main', loader=<...>, origin='/workspaces/graxpert/graxpert/main.py', loader_state=None, submodule_search_locations=None, _uninitialized_submodules=[], _set_fileattr=True, _cached='/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc') at remote 0x7ffff76806f0>, '__annotations__': {}, '__builtins__': <module at remote 0x7ffff7967830>, '__file__': '/workspaces/graxpert/graxpert/main.py', '__cached__': '/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc', 'os': <module at remote 0x7ffff779ba70>, 'platform': <module at remote 0x7ffff769d6d0>, 'sys': <module at remote 0x7ffff7957ad0>, 'argparse': <module at remote 0x7ffff769edb0>, 'logging': <module at remote 0x7ffff7756270>, 'multiprocessing': <module at remote 0x7ffff759ab10>, 're': <module at remote 0x7ffff76...(truncated), args=args@entry=0x0, argcount=argcount@entry=0, kwnames=kwnames@entry=0x0) at ../Python/ceval.c:6435
#86 0x000000000058a27a in PyEval_EvalCode (co=co@entry=<code at remote 0xb309a0>, 
    globals=globals@entry={'__name__': '__main__', '__doc__': None, '__package__': 'graxpert', '__loader__': <SourceFileLoader(name='graxpert.main', path='/workspaces/graxpert/graxpert/main.py') at remote 0x7ffff7810920>, '__spec__': <ModuleSpec(name='graxpert.main', loader=<...>, origin='/workspaces/graxpert/graxpert/main.py', loader_state=None, submodule_search_locations=None, _uninitialized_submodules=[], _set_fileattr=True, _cached='/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc') at remote 0x7ffff76806f0>, '__annotations__': {}, '__builtins__': <module at remote 0x7ffff7967830>, '__file__': '/workspaces/graxpert/graxpert/main.py', '__cached__': '/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc', 'os': <module at remote 0x7ffff779ba70>, 'platform': <module at remote 0x7ffff769d6d0>, 'sys': <module at remote 0x7ffff7957ad0>, 'argparse': <module at remote 0x7ffff769edb0>, 'logging': <module at remote 0x7ffff7756270>, 'multiprocessing': <module at remote 0x7ffff759ab10>, 're': <module at remote 0x7ffff76...(truncated), 
    locals=locals@entry={'__name__': '__main__', '__doc__': None, '__package__': 'graxpert', '__loader__': <SourceFileLoader(name='graxpert.main', path='/workspaces/graxpert/graxpert/main.py') at remote 0x7ffff7810920>, '__spec__': <ModuleSpec(name='graxpert.main', loader=<...>, origin='/workspaces/graxpert/graxpert/main.py', loader_state=None, submodule_search_locations=None, _uninitialized_submodules=[], _set_fileattr=True, _cached='/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc') at remote 0x7ffff76806f0>, '__annotations__': {}, '__builtins__': <module at remote 0x7ffff7967830>, '__file__': '/workspaces/graxpert/graxpert/main.py', '__cached__': '/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc', 'os': <module at remote 0x7ffff779ba70>, 'platform': <module at remote 0x7ffff769d6d0>, 'sys': <module at remote 0x7ffff7957ad0>, 'argparse': <module at remote 0x7ffff769edb0>, 'logging': <module at remote 0x7ffff7756270>, 'multiprocessing': <module at remote 0x7ffff759ab10>, 're': <module at remote 0x7ffff76...(truncated)) at ../Python/ceval.c:1154
#87 0x00000000005714f8 in builtin_exec_impl (module=module@entry=<module at remote 0x7ffff7967830>, source=<code at remote 0xb309a0>, 
    globals={'__name__': '__main__', '__doc__': None, '__package__': 'graxpert', '__loader__': <SourceFileLoader(name='graxpert.main', path='/workspaces/graxpert/graxpert/main.py') at remote 0x7ffff7810920>, '__spec__': <ModuleSpec(name='graxpert.main', loader=<...>, origin='/workspaces/graxpert/graxpert/main.py', loader_state=None, submodule_search_locations=None, _uninitialized_submodules=[], _set_fileattr=True, _cached='/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc') at remote 0x7ffff76806f0>, '__annotations__': {}, '__builtins__': <module at remote 0x7ffff7967830>, '__file__': '/workspaces/graxpert/graxpert/main.py', '__cached__': '/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc', 'os': <module at remote 0x7ffff779ba70>, 'platform': <module at remote 0x7ffff769d6d0>, 'sys': <module at remote 0x7ffff7957ad0>, 'argparse': <module at remote 0x7ffff769edb0>, 'logging': <module at remote 0x7ffff7756270>, 'multiprocessing': <module at remote 0x7ffff759ab10>, 're': <module at remote 0x7ffff76...(truncated), 
    locals={'__name__': '__main__', '__doc__': None, '__package__': 'graxpert', '__loader__': <SourceFileLoader(name='graxpert.main', path='/workspaces/graxpert/graxpert/main.py') at remote 0x7ffff7810920>, '__spec__': <ModuleSpec(name='graxpert.main', loader=<...>, origin='/workspaces/graxpert/graxpert/main.py', loader_state=None, submodule_search_locations=None, _uninitialized_submodules=[], _set_fileattr=True, _cached='/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc') at remote 0x7ffff76806f0>, '__annotations__': {}, '__builtins__': <module at remote 0x7ffff7967830>, '__file__': '/workspaces/graxpert/graxpert/main.py', '__cached__': '/workspaces/graxpert/graxpert/__pycache__/main.cpython-311.pyc', 'os': <module at remote 0x7ffff779ba70>, 'platform': <module at remote 0x7ffff769d6d0>, 'sys': <module at remote 0x7ffff7957ad0>, 'argparse': <module at remote 0x7ffff769edb0>, 'logging': <module at remote 0x7ffff7756270>, 'multiprocessing': <module at remote 0x7ffff759ab10>, 're': <module at remote 0x7ffff76...(truncated), closure=0x0) at ../Python/bltinmodule.c:1075
#88 0x00000000005715fb in builtin_exec (module=<module at remote 0x7ffff7967830>, args=<optimized out>, args@entry=0x7ffff785f180, nargs=nargs@entry=2, kwnames=kwnames@entry=0x0)
    at ../Python/clinic/bltinmodule.c.h:465
#89 0x00000000004ecae7 in cfunction_vectorcall_FASTCALL_KEYWORDS (func=<built-in method exec of module object at remote 0x7ffff7967830>, args=0x7ffff785f180, nargsf=<optimized out>, kwnames=0x0)
    at ../Objects/methodobject.c:443
#90 0x00000000004a9f06 in _PyObject_VectorcallTstate (tstate=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<built-in method exec of module object at remote 0x7ffff7967830>, 
    args=args@entry=0x7ffff785f180, nargsf=9223372036854775810, kwnames=kwnames@entry=0x0) at ../Include/internal/pycore_call.h:92
#91 0x00000000004a9fd1 in PyObject_Vectorcall (callable=callable@entry=<built-in method exec of module object at remote 0x7ffff7967830>, args=args@entry=0x7ffff785f180, nargsf=<optimized out>, 
    kwnames=kwnames@entry=0x0) at ../Objects/call.c:299
#92 0x0000000000585e6d in _PyEval_EvalFrameDefault (tstate=0xabf2d8 <_PyRuntime+166328>, frame=0x7ffff785f0d8, throwflag=<optimized out>) at ../Python/ceval.c:4772
#93 0x000000000058a07b in _PyEval_EvalFrame (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, frame=frame@entry=0x7ffff785f020, throwflag=throwflag@entry=0) at ../Include/internal/pycore_ceval.h:73
#94 0x000000000058a17c in _PyEval_Vector (tstate=0xabf2d8 <_PyRuntime+166328>, func=0x7ffff769bee0, locals=locals@entry=0x0, args=0x7ffff77ff1c8, argcount=<optimized out>, kwnames=0x0)
    at ../Python/ceval.c:6435
#95 0x00000000004a9be2 in _PyFunction_Vectorcall (func=<optimized out>, stack=<optimized out>, nargsf=<optimized out>, kwnames=<optimized out>) at ../Objects/call.c:393
#96 0x00000000004a97e2 in _PyVectorcall_Call (tstate=tstate@entry=0xabf2d8 <_PyRuntime+166328>, func=0x4a9b95 <_PyFunction_Vectorcall>, callable=callable@entry=<function at remote 0x7ffff769bee0>, 
    tuple=tuple@entry=('graxpert.main', True), kwargs=kwargs@entry=0x0) at ../Objects/call.c:245
#97 0x00000000004a9b2c in _PyObject_Call (tstate=0xabf2d8 <_PyRuntime+166328>, callable=callable@entry=<function at remote 0x7ffff769bee0>, args=args@entry=('graxpert.main', True), kwargs=kwargs@entry=0x0)
    at ../Objects/call.c:328
#98 0x00000000004a9b6f in PyObject_Call (callable=callable@entry=<function at remote 0x7ffff769bee0>, args=args@entry=('graxpert.main', True), kwargs=kwargs@entry=0x0) at ../Objects/call.c:355
#99 0x00000000005e8b9c in pymain_run_module (modname=<optimized out>, set_argv0=set_argv0@entry=1) at ../Modules/main.c:300
#100 0x00000000005e9567 in pymain_run_python (exitcode=exitcode@entry=0x7fffffffd99c) at ../Modules/main.c:595
#101 0x00000000005e97a9 in Py_RunMain () at ../Modules/main.c:680
#102 0x00000000005e97fe in pymain_main (args=args@entry=0x7fffffffd9e0) at ../Modules/main.c:710
#103 0x00000000005e9883 in Py_BytesMain (argc=<optimized out>, argv=<optimized out>) at ../Modules/main.c:734
#104 0x0000000000420fef in main (argc=<optimized out>, argv=<optimized out>) at ../Programs/python.c:15
