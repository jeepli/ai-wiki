---
repo: flashinfer
commit: 4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5
source_version: 4a4e36d
document: architecture.md
status: source-backed
---

# Architecture

Source snapshot: `flashinfer` commit
`4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5`.

## Boundary Model

FlashInfer exposes Python wrappers for kernel families that serving engines can
call directly. The user-facing package is `flashinfer-python`, and the console
script is `flashinfer = flashinfer.__main__:cli`
(`flashinfer@4a4e36d:pyproject.toml`). Most public symbols are re-exported from
`flashinfer/__init__.py`, which makes the package surface a curated wrapper
layer rather than a single monolithic module.

The central attention design uses a planning phase and an execution phase.
`BatchDecodeWithPagedKVCacheWrapper.plan(...)` prepares metadata for paged
decode, then `run(...)` / `forward(...)` launches kernels over the planned
layout (`flashinfer@4a4e36d:flashinfer/decode.py#BatchDecodeWithPagedKVCacheWrapper`).
`BatchPrefillWithPagedKVCacheWrapper` mirrors the same structure for prefill
(`flashinfer@4a4e36d:flashinfer/prefill.py#BatchPrefillWithPagedKVCacheWrapper`).

## Kernel and Packaging Layers

Native implementation surfaces are split across headers and source:

- `include/flashinfer/attention/blackwell/device/fmha.hpp` defines Blackwell FMHA
  device-level types such as `FMHA` / `Kernel`.
- `include/flashinfer/attention/blackwell/device/sm100_mla.hpp` defines MLA
  device-level types such as `MLA` / `Kernel`.
- `csrc/` contains CUDA/C++ kernel families for attention, fused MoE, grouped
  GEMM, MHC, XQA, and NVFP4 attention.

JIT support is represented by `flashinfer/jit/core.py#JitSpec`,
`JitSpecRegistry`, and `FLASHINFER_JIT_DIR` in `flashinfer/jit/env.py`; packaged
JIT cache helpers live under `flashinfer-jit-cache/`
(`flashinfer@4a4e36d:flashinfer/jit/core.py`,
`flashinfer@4a4e36d:flashinfer/jit/env.py`).

## Subsystem Boundaries

- Attention: `decode.py`, `prefill.py`, `cascade.py`, `attention/`, `mla/`,
  `parallel_attention/`.
- KV cache: `page.py`, paged wrappers in `decode.py` and `prefill.py`, MLA cache
  helpers in `mla/`.
- Model-serving kernels beyond attention: `fused_moe/`, `gemm/`, `grouped_mm/`,
  `norm/`, `rope.py`, `sampling.py`, `logits_processor/`, `quantization/`.
- Build/runtime artifacts: `flashinfer-cubin/`, `flashinfer-jit-cache/`,
  `build_backend.py`, and package-data declarations in `pyproject.toml`.

## Dependency Notes

Optional dependencies `cu12` and `cu13` control CUTLASS DSL variants, and the
`nvep` extra controls runtime dependencies for MoE expert-parallel transport.
The build backend is a custom `build_backend` module with `backend-path = ["."]`
(`flashinfer@4a4e36d:pyproject.toml`).
