---
repo: flashattention
commit: 73c992c8ca746935548df620ef3c1b6238fe6e68
source_version: 73c992c
document: build-and-entrypoints.md
status: source-backed
---

# Build And Entrypoints

Source snapshot: `flashattention` commit
`73c992c8ca746935548df620ef3c1b6238fe6e68`.

## Package Build

`setup.py` is the primary build entrypoint. It uses setuptools and
`torch.utils.cpp_extension` to build CUDA/ROCm extensions, reads the package
long description from `README.md`, and controls build behavior through
environment variables (`flashattention@73c992c:setup.py`).

Important build controls:

- `BUILD_TARGET=auto|cuda|rocm` selects target platform behavior.
- `FLASH_ATTENTION_FORCE_BUILD=TRUE` forces local compilation instead of trying
  prebuilt wheels.
- `FLASH_ATTENTION_SKIP_CUDA_BUILD=TRUE` allows source distribution style builds
  without CUDA compilation.
- `FLASH_ATTENTION_FORCE_CXX11_ABI=TRUE` controls ABI compatibility.
- `FLASH_ATTENTION_TRITON_AMD_ENABLE=TRUE` selects ROCm Triton backend instead
  of CK path.
- `FLASH_ATTN_CUDA_ARCHS` controls CUDA architectures; default handling includes
  `80;90;100;110;120`.

## Runtime Entrypoints

- Python package import: `flash_attn/__init__.py`.
- Main user-facing API definitions: `flash_attn/flash_attn_interface.py`.
- C++/CUDA binding: `csrc/flash_attn/flash_api.cpp`.
- Hopper interface: `hopper/flash_attn_interface.py`.
- CUTE interface: `flash_attn/cute/interface.py`.

## Kernel Generation

The generated kernel surface is controlled by:

- `csrc/flash_attn/src/generate_kernels.py#Kernel`
- `csrc/flash_attn/src/generate_kernels.py#get_all_kernels`
- `hopper/generate_kernels.py#Kernel`
- `hopper/generate_kernels.py#get_all_kernels`

These scripts are the source-backed place to inspect which kernel families are
materialized for a snapshot (`flashattention@73c992c`).

## Tests and Benchmarks

- Public API correctness: `tests/test_flash_attn.py`,
  `tests/test_flash_attn_ck.py`, `tests/test_flash_attn_triton_amd.py`.
- CUTE path tests: `tests/cute/`.
- Hopper path tests: `hopper/test_flash_attn.py` and related Hopper test files.
- Performance references: `benchmarks/benchmark_attn.py` and Hopper benchmark
  files under `hopper/`.
