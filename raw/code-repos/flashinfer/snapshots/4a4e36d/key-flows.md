---
repo: flashinfer
commit: 4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5
source_version: 4a4e36d
document: key-flows.md
status: source-backed
---

# Key Flows

Source snapshot: `flashinfer` commit
`4a4e36d7fdaccd5eac8445a0bb4840e9d742c8b5`.

## Single Decode

`single_decode_with_kv_cache(q, k, v, ...)` is the direct decode API for one
query against KV tensors. It accepts layout, positional encoding mode, tensor
core flag, optional q/k/v scales, local window, logits soft cap, softmax scale,
RoPE parameters, and optional LSE return
(`flashinfer@4a4e36d:flashinfer/decode.py#single_decode_with_kv_cache`). A JIT
variant, `single_decode_with_kv_cache_with_jit_module`, accepts a compiled JIT
module and forwards the same logical decode work
(`flashinfer@4a4e36d:flashinfer/decode.py#single_decode_with_kv_cache_with_jit_module`).

## Batch Decode With Paged KV Cache

1. Construct `BatchDecodeWithPagedKVCacheWrapper(float_workspace_buffer,
   kv_layout="NHD", use_cuda_graph=False, ...)`
   (`flashinfer@4a4e36d:flashinfer/decode.py#BatchDecodeWithPagedKVCacheWrapper.__init__`).
2. Call `plan(indptr, indices, last_page_len, num_qo_heads, num_kv_heads,
   head_dim, page_size, ...)` to prepare page tables, split behavior, layout,
   sequence lengths, data types, RoPE/logits metadata, and optional CUDA graph
   buffers (`flashinfer@4a4e36d:flashinfer/decode.py#BatchDecodeWithPagedKVCacheWrapper.plan`).
3. Call `run(q, paged_kv_cache, ...)` or `forward(...)` to execute and
   optionally return LSE (`flashinfer@4a4e36d:flashinfer/decode.py#BatchDecodeWithPagedKVCacheWrapper.run`).
4. Call `end_forward()` when the wrapper lifecycle needs explicit cleanup
   (`flashinfer@4a4e36d:flashinfer/decode.py#BatchDecodeWithPagedKVCacheWrapper.end_forward`).

## Batch Prefill With Paged KV Cache

`BatchPrefillWithPagedKVCacheWrapper` uses the same plan/run lifecycle for
prefill. Its `plan(...)` takes query/output indptr, paged KV indptr/indices,
last-page lengths, head counts, head dimensions, page size, causal/custom mask
settings, positional encoding, data types, fixed split size, and maximum
sequence metadata
(`flashinfer@4a4e36d:flashinfer/prefill.py#BatchPrefillWithPagedKVCacheWrapper.plan`).
Execution uses `run(...)`, `forward(...)`, or `forward_return_lse(...)`
(`flashinfer@4a4e36d:flashinfer/prefill.py#BatchPrefillWithPagedKVCacheWrapper.run`).

## Paged KV Cache Updates

Top-level exports include `append_paged_kv_cache`, `append_paged_mla_kv_cache`,
`get_batch_indices_positions`, and `get_seq_lens`, all imported from
`flashinfer/page.py` through `flashinfer/__init__.py`. These are the code points
to inspect when a serving engine updates page-backed KV state between prefill
and decode (`flashinfer@4a4e36d:flashinfer/__init__.py`).

## JIT Flow

`JitSpec` describes a compilable kernel artifact, `JitSpecRegistry` tracks
registered specs, and `jit_spec_registry` is the shared registry object
(`flashinfer@4a4e36d:flashinfer/jit/core.py#JitSpec`,
`flashinfer@4a4e36d:flashinfer/jit/core.py#JitSpecRegistry`). JIT cache
location logic is in `flashinfer/jit/env.py` and packaged cache discovery is in
`flashinfer-jit-cache/flashinfer_jit_cache/__init__.py`.
