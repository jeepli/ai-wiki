---
repo: flashinfer
commit: 4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5
source_version: 4a4e36d
document: build-and-entrypoints.md
status: source-backed
---

# Build And Entrypoints

Source snapshot: `flashinfer` commit
`4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5`.

## Package Build

`pyproject.toml` defines the project as `flashinfer-python`, uses Python
`>=3.10,<4.0`, and selects a custom build backend named `build_backend` with
`backend-path = ["."]` (`flashinfer@4a4e36d:pyproject.toml`). Package data
includes generated build metadata, `csrc/**`, `include/**`, and vendored
CUTLASS/spdlog/CCCL headers via `flashinfer.data`.

Build-system requirements include setuptools, packaging, and `apache-tvm-ffi`.
Optional dependency groups include `cu12`, `cu13`, and `nvep`; `nvep` is tied to
MoE expert-parallel transport dependencies such as CUDA Python, NCCL, and NIXL
(`flashinfer@4a4e36d:pyproject.toml`).

## Runtime Entrypoints

- Console script: `flashinfer = flashinfer.__main__:cli`.
- Main import surface: `flashinfer/__init__.py`.
- JIT registry: `flashinfer/jit/core.py`.
- Attention wrappers: `flashinfer/decode.py`, `flashinfer/prefill.py`,
  `flashinfer/cascade.py`, `flashinfer/mla/`.
- KV-cache page helpers: `flashinfer/page.py`.

## Native Entrypoints

- Header API: `include/flashinfer/`.
- Native source: `csrc/`.
- Cubin package: `flashinfer-cubin/`.
- JIT cache package: `flashinfer-jit-cache/`.

The Blackwell FMHA and MLA device headers are high-signal entrypoints for
kernel-level inspection:

- `include/flashinfer/attention/blackwell/device/fmha.hpp#FMHA`
- `include/flashinfer/attention/blackwell/device/sm100_mla.hpp#MLA`

## Tests and Benchmarks

Use `tests/attention/`, `tests/gemm/`, `tests/moe/`, `tests/norm/`,
`tests/quantization`-adjacent files, `tests/autotuner/`, `tests/cli/`, and
`benchmarks/` for validation and performance references. The benchmark
`benchmarks/test_flashinfer_benchmark.py` exercises
`BatchPrefillWithPagedKVCacheWrapper`-style routines
(`flashinfer@4a4e36d:benchmarks/test_flashinfer_benchmark.py`).
