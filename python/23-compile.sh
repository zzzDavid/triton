

mkdir -p build
cd build

PYTHON_ROOT=`pip3 show pybind11 | grep Location | awk '{print $2}'`

cmake /home/nz264/scratch/triton \
    -DLLVM_ENABLE_WERROR=ON \
    -DCMAKE_LIBRARY_OUTPUT_DIRECTORY=/home/nz264/scratch/triton/python/build/lib.linux-x86_64-cpython-311/triton/_C \
    -DTRITON_BUILD_TUTORIALS=OFF \
    -DTRITON_BUILD_PYTHON_MODULE=ON \
    -DPython3_EXECUTABLE:FILEPATH=/home/nz264/anaconda3/envs/air/bin/python \
    -DCMAKE_VERBOSE_MAKEFILE:BOOL=ON \
    -DPYTHON_INCLUDE_DIRS=/home/nz264/anaconda3/envs/air/include/python3.11 \
    -DPYBIND11_INCLUDE_DIR=/home/nz264/anaconda3/envs/air/lib/python3.11/site-packages/pybind11/include \
    -DLLVM_INCLUDE_DIRS=/home/nz264/scratch/mlir-air/utils/llvm/build/include \
    -DLLVM_LIBRARY_DIR=/home/nz264/scratch/mlir-air/utils/llvm/build/lib \
    -DCMAKE_BUILD_TYPE=TritonRelBuildWithAsserts

# cmake --build . --config TritonRelBuildWithAsserts -j96