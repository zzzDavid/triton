

mkdir -p build
cd build

# cmake /home/niansong/triton \
#     -DLLVM_ENABLE_WERROR=ON \
#     -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/home/niansong/triton/python/triton/_C \
#     -DTRITON_BUILD_TUTORIALS=OFF \
#     -DTRITON_BUILD_PYTHON_MODULE=ON \
#     -DPython3_EXECUTABLE:FILEPATH=/home/niansong/anaconda3/envs/air/bin/python \
#     -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
#     -DPYTHON_INCLUDE_DIRS=/home/niansong/anaconda3/envs/air/include/python3.11 \
#     -DLLVM_EXTERNAL_LIT=/home/niansong/anaconda3/envs/air/bin/lit \
#     -DPYBIND11_INCLUDE_DIR=/home/niansong/.triton/pybind11/pybind11-2.10.0/include \
#     -DLLVM_INCLUDE_DIRS=/home/niansong/mlir-air/utils/llvm/build/include \
#     -DLLVM_LIBRARY_DIR=/home/niansong/mlir-air/utils/llvm/build/lib \
#     -DCMAKE_BUILD_TYPE=TritonRelBuildWithAsserts

# cmake /home/niansong/triton \
#     -DLLVM_ENABLE_WERROR=ON \
#     -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/home/niansong/triton/python/build/lib.linux-x86_64-cpython-311/triton/_C \
#     -DTRITON_BUILD_TUTORIALS=OFF \
#     -DTRITON_BUILD_PYTHON_MODULE=ON \
#     -DPython3_EXECUTABLE:FILEPATH=/home/niansong/anaconda3/envs/air/bin/python \
#     -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
#     -DPYTHON_INCLUDE_DIRS=/home/niansong/anaconda3/envs/air/include/python3.11 \
#     -DLLVM_EXTERNAL_LIT=/home/niansong/anaconda3/envs/air/bin/lit \
#     -DPYBIND11_INCLUDE_DIR=/home/niansong/.triton/pybind11/pybind11-2.10.0/include \
#     -DLLVM_INCLUDE_DIRS=/home/niansong/.triton/llvm/llvm+mlir-17.0.0-x86_64-linux-gnu-ubuntu-18.04-release/include \
#     -DLLVM_LIBRARY_DIR=/home/niansong/.triton/llvm/llvm+mlir-17.0.0-x86_64-linux-gnu-ubuntu-18.04-release/lib \
#     -DCMAKE_BUILD_TYPE=TritonRelBuildWithAsserts

cmake /home/niansong/triton \
    -DLLVM_ENABLE_WERROR=ON \
    -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/home/niansong/triton/python/build/lib.linux-x86_64-cpython-311/triton/_C \
    -DTRITON_BUILD_TUTORIALS=OFF \
    -DTRITON_BUILD_PYTHON_MODULE=ON \
    -DPython3_EXECUTABLE:FILEPATH=/home/niansong/anaconda3/envs/air/bin/python \
    -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
    -DPYTHON_INCLUDE_DIRS=/home/niansong/anaconda3/envs/air/include/python3.11 \
    -DLLVM_EXTERNAL_LIT=/home/niansong/anaconda3/envs/air/bin/lit \
    -DPYBIND11_INCLUDE_DIR=/home/niansong/.triton/pybind11/pybind11-2.10.0/include \
    -DLLVM_INCLUDE_DIRS=/home/niansong/mlir-air/utils/llvm/build/include \
    -DLLVM_LIBRARY_DIR=/home/niansong/mlir-air/utils/llvm/build/lib \
    -DCMAKE_BUILD_TYPE=TritonRelBuildWithAsserts

# cmake --build . --config TritonRelBuildWithAsserts -j96