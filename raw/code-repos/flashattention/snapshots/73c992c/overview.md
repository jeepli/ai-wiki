---
repo: flashattention
commit: 73c992c8ca746935548df620ef3c1b6238fe6e68
source_version: 73c992c
document: overview.md
status: source-backed
---

# Overview

FlashAttention is tracked here as an attention-kernel source snapshot for
IO-aware exact attention, PyTorch-facing APIs, CUDA/C++ kernels, Hopper-era
kernels, and Triton/ROCm fallback paths. Source: `flashattention` commit
`73c992c8ca746935548df620ef3c1b6238fe6e68`; declared role in
`code-repos.yml`; public package metadata in
`external-repos/flashattention/flash_attn/__init__.py`.

## Directory Map

- `flash_attn/` is the Python package. It exposes user-facing functions from
  `flash_attn/flash_attn_interface.py`, plus modules, layers, losses, model
  examples, utility code, and CUTE DSL experiments under `flash_attn/cute/`
  (`flashattention@73c992c:flash_attn/__init__.py`,
  `flashattention@73c992c:flash_attn/flash_attn_interface.py`,
  `flashattention@73c992c:flash_attn/cute/interface.py`).
- `csrc/flash_attn/` is the CUDA/C++ extension boundary. The binding file
  `csrc/flash_attn/flash_api.cpp` validates tensors, fills
  `Flash_fwd_params` / `Flash_bwd_params`, and connects Python calls to
  compiled kernels (`flashattention@73c992c:csrc/flash_attn/flash_api.cpp`).
- `csrc/flash_attn/src/generate_kernels.py` and `hopper/generate_kernels.py`
  generate kernel instantiations for the classic CUDA path and newer Hopper
  path (`Kernel`, `get_all_kernels` symbols in both files).
- `hopper/` contains a separate interface and generated kernels for newer GPU
  targets, including extended forward signatures with paged cache, descale
  tensors, scheduler metadata, and split controls
  (`flashattention@73c992c:hopper/flash_attn_interface.py#_flash_attn_forward`).
- `tests/`, `hopper/test_flash_attn.py`, and `benchmarks/` provide correctness
  and performance coverage for public functions such as `flash_attn_func`,
  `flash_attn_varlen_func`, and `flash_attn_with_kvcache`
  (`flashattention@73c992c:tests/test_flash_attn.py`,
  `flashattention@73c992c:benchmarks/benchmark_attn.py`).

## Main Subsystems

- Public API: `flash_attn/__init__.py` re-exports
  `flash_attn_func`, packed QKV/KV variants, varlen variants, and
  `flash_attn_with_kvcache` from `flash_attn.flash_attn_interface`.
- PyTorch op layer: `flash_attn/flash_attn_interface.py` defines custom op
  wrappers for `_flash_attn_forward`, `_flash_attn_varlen_forward`, and
  `_flash_attn_backward`, with fake registrations for torch compile shape
  propagation.
- Kernel extension: `csrc/flash_attn/flash_api.cpp` is the compiled binding
  layer that translates tensor layouts, sequence lengths, dropout, causal/local
  windowing, softcap, and ALiBi data into kernel parameter structs.
- Integration helpers: `flash_attn/modules/mha.py`, `flash_attn/bert_padding.py`,
  `flash_attn/layers/rotary.py`, and `flash_attn/ops/*` show how the kernel
  functions are embedded into transformer blocks and adjacent fused ops.
