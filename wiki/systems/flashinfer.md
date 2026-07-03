# FlashInfer

**Summary**: FlashInfer is a serving-kernel library for paged KV-cache attention, prefill/decode wrappers, MLA, GEMM, fused MoE, quantization, JIT kernels, and packaged cubins. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/overview.md)

**Sources**: `raw/code-repos/flashinfer/latest.yml`; `raw/code-repos/flashinfer/snapshots/4a4e36d/overview.md`; `raw/code-repos/flashinfer/snapshots/4a4e36d/architecture.md`; `raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md`; `raw/code-repos/flashinfer/snapshots/4a4e36d/api-surface.md`; `raw/code-repos/flashinfer/snapshots/4a4e36d/build-and-entrypoints.md`

**Last updated**: 2026-07-03

---

## Why it matters

FlashInfer sits below full serving engines such as [[systems/vllm]] and [[systems/sglang]]: it packages high-performance inference primitives that an engine can call directly, especially paged KV-cache prefill and decode kernels. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/overview.md; raw/code-repos/flashinfer/snapshots/4a4e36d/architecture.md)

It is useful to study separately from [[systems/flashattention]] because the code snapshot emphasizes serving-time wrappers, paged KV metadata, JIT/cubin packaging, MLA, GEMM, MoE, quantization, norm, RoPE, sampling, and logits processing rather than only dense exact attention. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/overview.md)

## Key ideas

The core attention pattern is a two-phase wrapper: `plan(...)` prepares metadata such as page tables, sequence lengths, split behavior, data types, RoPE/logits metadata, and optional CUDA graph buffers; `run(...)` or `forward(...)` then launches the kernel on that planned layout. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/architecture.md; raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md)

`BatchDecodeWithPagedKVCacheWrapper` and `BatchPrefillWithPagedKVCacheWrapper` are the main paged-KV wrapper families for decode and prefill. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md)

FlashInfer also exposes single-request decode with `single_decode_with_kv_cache`, page update helpers such as `append_paged_kv_cache`, and JIT registry objects such as `JitSpec` and `JitSpecRegistry`. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md; raw/code-repos/flashinfer/snapshots/4a4e36d/api-surface.md)

## Method or mechanism

The Python package exports a curated surface from `flashinfer/__init__.py`, while native implementations are split across `include/flashinfer/`, `csrc/`, `flashinfer-cubin/`, and `flashinfer-jit-cache/`. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/overview.md; raw/code-repos/flashinfer/snapshots/4a4e36d/architecture.md)

The native layer includes Blackwell FMHA and MLA headers, CUDA/C++ kernel families for attention, fused MoE, grouped GEMM, MHC, XQA, and NVFP4 attention, plus JIT cache logic under `flashinfer/jit/`. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/architecture.md)

The package build uses `flashinfer-python`, a custom `build_backend`, optional `cu12` / `cu13` CUTLASS DSL dependency groups, and an `nvep` extra for MoE expert-parallel transport dependencies. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/build-and-entrypoints.md; raw/code-repos/flashinfer/snapshots/4a4e36d/architecture.md)

## Results and limitations

This wiki source records architecture and code-entry facts for commit `4a4e36d`, but it does not provide benchmark results or stability guarantees for each kernel family. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/manifest.yml; raw/code-repos/flashinfer/snapshots/4a4e36d/build-and-entrypoints.md)

The most important limitation for learning is boundary confusion: FlashInfer is a kernel and wrapper library, not a complete request scheduler or OpenAI-compatible serving stack by itself. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/overview.md; raw/code-repos/flashinfer/snapshots/4a4e36d/api-surface.md)

## Open questions

The current source snapshot does not explain how each downstream serving engine chooses between FlashInfer, FlashAttention, Triton, or other attention backends at runtime; answer that by exploring the specific engine code when needed. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/overview.md; raw/code-repos/vllm/snapshots/8357226/architecture.md)

## Related pages

- [[concepts/kv-cache]]
- [[systems/flashattention]]
- [[systems/vllm]]
- [[systems/sglang]]
