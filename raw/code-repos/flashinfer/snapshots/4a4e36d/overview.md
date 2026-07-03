---
repo: flashinfer
commit: 4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5
source_version: 4a4e36d
document: overview.md
status: source-backed
---

# Overview

FlashInfer is tracked here as an inference-kernel source snapshot for LLM
serving primitives: paged KV-cache attention, prefill/decode wrappers, MLA,
GEMM, fused MoE, normalization, RoPE, sampling, quantization, JIT kernels, and
packaged cubins. Source: `flashinfer` commit
`4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5`; declared role in `code-repos.yml`;
package metadata in `external-repos/flashinfer/pyproject.toml`.

## Directory Map

- `flashinfer/` is the Python package. Top-level modules include
  `decode.py`, `prefill.py`, `page.py`, `cascade.py`, `mla/`, `gemm/`,
  `norm/`, `rope.py`, `sampling.py`, `fused_moe/`, `quantization/`, `jit/`,
  `trace/`, and `profiler/`
  (`flashinfer@4a4e36d:flashinfer/__init__.py`).
- `include/flashinfer/` holds public C++/CUDA headers, including attention,
  GEMM, TensorRT-LLM related headers, allocator/logging/exception utilities,
  and cubin loader support
  (`flashinfer@4a4e36d:include/flashinfer/attention/blackwell/device/fmha.hpp`,
  `flashinfer@4a4e36d:include/flashinfer/cubin_loader.h`).
- `csrc/` contains generated and handwritten CUDA/C++ sources for attention,
  fused MoE, MHC, XQA, Blackwell NVFP4 attention, grouped GEMM, and related
  kernels (`flashinfer@4a4e36d:csrc/`).
- `flashinfer-cubin/` and `flashinfer-jit-cache/` are packaging companions for
  binary cubins and prebuilt JIT cache artifacts
  (`flashinfer@4a4e36d:flashinfer-jit-cache/flashinfer_jit_cache/__init__.py`).
- `tests/`, `benchmarks/`, `examples/`, and `docs/` provide correctness,
  performance, usage, and API documentation coverage
  (`flashinfer@4a4e36d:tests/attention/`, `flashinfer@4a4e36d:docs/api/`).

## Main Subsystems

- Attention wrappers: `flashinfer/decode.py`, `flashinfer/prefill.py`,
  `flashinfer/cascade.py`, and `flashinfer/mla/` expose batch/single decode and
  prefill APIs over paged or ragged KV caches.
- KV-cache utilities: `flashinfer/page.py` exports append and indexing helpers
  for paged KV and MLA KV cache workflows.
- Kernel specialization: `flashinfer/jit/core.py` defines `JitSpec`,
  `JitSpecRegistry`, and JIT cache locations, while `csrc/` and `include/`
  provide the native implementation surface.
- Serving-adjacent ops: fused MoE, GEMM, grouped MM, FP4/FP8 quantization,
  norm, RoPE, logits processing, and sampling are exported through
  `flashinfer/__init__.py`.
