---
repo: flashattention
commit: 73c992c8ca746935548df620ef3c1b6238fe6e68
source_version: 73c992c
document: architecture.md
status: source-backed
---

# Architecture

Source snapshot: `flashattention` commit
`73c992c8ca746935548df620ef3c1b6238fe6e68`.

## Boundary Model

FlashAttention is organized as a thin Python API over compiled attention
kernels. The root package exports stable Python functions, while the heavy
compute path is delegated to `flash_attn_2_cuda` or ROCm/Triton-compatible
implementations depending on runtime/build environment
(`flashattention@73c992c:flash_attn/__init__.py`,
`flashattention@73c992c:flash_attn/flash_attn_interface.py`).

The Python interface normalizes tensor contiguity, exposes torch custom ops,
computes fake outputs for tracing/compile, and routes real work to
`flash_attn_gpu.fwd`, `flash_attn_gpu.varlen_fwd`, and backward equivalents
(`flashattention@73c992c:flash_attn/flash_attn_interface.py#_flash_attn_forward`,
`flashattention@73c992c:flash_attn/flash_attn_interface.py#_flash_attn_backward`).

## Kernel Boundary

`csrc/flash_attn/flash_api.cpp` is the C++ binding layer. It checks device and
shape preconditions, populates `Flash_fwd_params` and `Flash_bwd_params`, and
records strides, batch/head dimensions, cumulative sequence length pointers,
dropout state, causal/local-window flags, softcap, and ALiBi metadata before
dispatching kernels (`flashattention@73c992c:csrc/flash_attn/flash_api.cpp`).

Kernel specialization is generated rather than hand-enumerated. The classic
CUDA path uses `csrc/flash_attn/src/generate_kernels.py`, and the Hopper path
uses `hopper/generate_kernels.py`; both define a `Kernel` abstraction and
`get_all_kernels` discovery/generation flow
(`flashattention@73c992c:csrc/flash_attn/src/generate_kernels.py#Kernel`,
`flashattention@73c992c:hopper/generate_kernels.py#Kernel`).

## Python Subsystems

- `flash_attn/flash_attn_interface.py` owns the stable public functions,
  custom op wrappers, packed/varlen variants, and KV-cache decode API.
- `flash_attn/cute/` contains CUTE DSL implementations and interfaces for newer
  kernel experiments, including `flash_attn_func` and `flash_attn_varlen_func`
  in `flash_attn/cute/interface.py`.
- `flash_attn/modules/`, `flash_attn/layers/`, and `flash_attn/models/` provide
  reference integration points for MHA blocks, rotary embeddings, BERT/GPT/LLaMA
  style models, and training-oriented examples.
- `flash_attn/ops/` contains adjacent fused operations such as dense, activation,
  layer norm, and RMSNorm helpers that share the package/build surface.

## Dependency Notes

The build script chooses CUDA vs ROCm behavior from environment variables such
as `BUILD_TARGET`, `FLASH_ATTENTION_TRITON_AMD_ENABLE`,
`FLASH_ATTENTION_FORCE_BUILD`, `FLASH_ATTENTION_SKIP_CUDA_BUILD`, and
`FLASH_ATTN_CUDA_ARCHS`
(`flashattention@73c992c:setup.py`). This makes build behavior a first-class
part of the architecture, not just packaging metadata.
