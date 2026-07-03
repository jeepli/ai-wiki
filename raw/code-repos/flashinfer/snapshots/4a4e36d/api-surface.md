---
repo: flashinfer
commit: 4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5
source_version: 4a4e36d
document: api-surface.md
status: source-backed
---

# Api Surface

Source snapshot: `flashinfer` commit
`4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5`.

## Public Package Surface

`flashinfer/__init__.py` is the primary curated API surface. It re-exports
version metadata, JIT helpers, activation ops, attention wrappers, cascade
wrappers, decode/prefill functions, page/KV helpers, quantization functions,
fused MoE APIs, GEMM/grouped-MM APIs, MLA wrappers, norm ops, RoPE helpers,
sampling/logits processors, and profiler/testing utilities
(`flashinfer@4a4e36d:flashinfer/__init__.py`).

## Attention APIs

- Single decode: `single_decode_with_kv_cache`.
- Batch decode: `BatchDecodeWithPagedKVCacheWrapper`,
  `BatchDecodeMlaWithPagedKVCacheWrapper`, and CUDA-graph decode wrapper.
- Single prefill: `single_prefill_with_kv_cache` and
  `single_prefill_with_kv_cache_return_lse`.
- Batch prefill: `BatchPrefillWithPagedKVCacheWrapper` and
  `BatchPrefillWithRaggedKVCacheWrapper`.
- Cascade/prefix APIs: `BatchDecodeWithSharedPrefixPagedKVCacheWrapper`,
  `BatchPrefillWithSharedPrefixPagedKVCacheWrapper`,
  `MultiLevelCascadeAttentionWrapper`, `merge_state`, `merge_state_in_place`,
  and `merge_states`.

Citation: `flashinfer@4a4e36d:flashinfer/__init__.py`,
`flashinfer@4a4e36d:flashinfer/decode.py`,
`flashinfer@4a4e36d:flashinfer/prefill.py`,
`flashinfer@4a4e36d:flashinfer/cascade.py`.

## Serving Primitive APIs

- KV cache pages: `append_paged_kv_cache`, `append_paged_mla_kv_cache`,
  `get_batch_indices_positions`, `get_seq_lens`.
- GEMM: `SegmentGEMMWrapper`, `mm_bf16`, `mm_fp4`, `mm_fp8`, `mm_mxfp8`,
  `bmm_bf16`, `bmm_fp8`, `bmm_mxfp8`, and grouped MM variants.
- MoE: `cutlass_fused_moe`, TensorRT-LLM MoE wrappers, CuteDSL MoE wrappers, and
  Blackwell B12x MoE wrappers.
- Quantization: FP4/NVFP4/MXFP4 and FP8 quantize/dequantize functions exported
  from `flashinfer/quantization/`.
- Norm/RoPE: RMSNorm/layernorm variants, fused QK RMSNorm+RoPE, and LLaMA 3.1
  RoPE helpers.

## CLI and Extension Points

The package script `flashinfer` maps to `flashinfer.__main__:cli`
(`flashinfer@4a4e36d:pyproject.toml`). JIT extension points are represented by
`JitSpec`, `JitSpecRegistry`, and the shared registry in
`flashinfer/jit/core.py`.
