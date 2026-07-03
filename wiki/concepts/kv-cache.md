# KV Cache

**Summary**: A KV cache stores previously computed key/value tensors or blocks during autoregressive inference so later decode steps can reuse prior context instead of recomputing it. In serving engines, the practical problem is not just storing tensors, but allocating, paging, prefix-matching, sharing, moving, and scheduling cache state efficiently. (source: raw/paper/pagedattention.pdf, pp. 1-6; raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md; raw/code-repos/vllm/snapshots/8357226/key-flows.md; raw/code-repos/sglang/snapshots/b276a9a/key-flows.md)

**Sources**: `raw/paper/pagedattention.pdf`; `raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md`; `raw/code-repos/vllm/snapshots/8357226/architecture.md`; `raw/code-repos/vllm/snapshots/8357226/key-flows.md`; `raw/code-repos/sglang/snapshots/b276a9a/architecture.md`; `raw/code-repos/sglang/snapshots/b276a9a/key-flows.md`; `raw/code-repos/flashattention/snapshots/73c992c/key-flows.md`

**Last updated**: 2026-07-03

---

## Why it matters

KV cache design is central to LLM serving because decode repeatedly attends over prior tokens, and the cache determines how prior key/value state is stored, indexed, shared, evicted, paged, or transferred. The PagedAttention paper argues that inefficient KV-cache management can limit batching through fragmentation, reservation, and duplicate storage. (source: raw/paper/pagedattention.pdf, pp. 1-3; raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md; raw/code-repos/vllm/snapshots/8357226/key-flows.md)

The same high-level idea appears at different layers: [[systems/flashattention]] exposes `flash_attn_with_kvcache` as a kernel API, [[systems/flashinfer]] exposes paged KV wrapper primitives, [[systems/vllm]] manages KV blocks in a scheduler-facing manager, and [[systems/sglang]] uses radix/prefix cache structures in its runtime. (source: raw/code-repos/flashattention/snapshots/73c992c/key-flows.md; raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md; raw/code-repos/vllm/snapshots/8357226/architecture.md; raw/code-repos/sglang/snapshots/b276a9a/architecture.md)

## Intuition

During prefill, the system processes a prompt and creates cache state for the prompt tokens; during decode, each new token can attend to cached keys and values rather than rebuilding the entire context state. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md; raw/code-repos/flashattention/snapshots/73c992c/key-flows.md)

Serving systems make this harder because requests are batched, sequences have different lengths, prefixes can be reused, memory is finite, and cache state may need page tables, block IDs, prefix lookup, offload, or distributed transfer. (source: raw/code-repos/vllm/snapshots/8357226/key-flows.md; raw/code-repos/sglang/snapshots/b276a9a/key-flows.md)

## Mechanisms

PagedAttention introduced the reusable pattern of splitting KV cache into fixed-size logical blocks mapped to non-contiguous physical blocks, using block tables to let attention kernels access the right pages. (source: raw/paper/pagedattention.pdf, pp. 5-6)

Paged KV cache uses metadata such as page indices, page lengths, sequence lengths, and block tables to let kernels operate on non-contiguous or dynamically allocated cache pages. (source: raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md)

vLLM models KV state as blocks: `KVCacheManager` exposes `KVCacheBlocks` to the scheduler, tracks block-pool usage, and performs prefix-cache lookup through `get_computed_blocks`. (source: raw/code-repos/vllm/snapshots/8357226/architecture.md; raw/code-repos/vllm/snapshots/8357226/key-flows.md)

SGLang models prefix reuse through radix-style cache structures such as `RadixCache` and `RadixCacheCpp`, with related chunk, SWA, Mamba, unified, HiCache, and memory-pool implementations under its runtime cache subsystem. (source: raw/code-repos/sglang/snapshots/b276a9a/architecture.md; raw/code-repos/sglang/snapshots/b276a9a/key-flows.md)

## Common pitfalls

- KV cache is not one API: kernels, wrapper libraries, and serving engines expose it at different abstraction levels. (source: raw/code-repos/flashattention/snapshots/73c992c/key-flows.md; raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md; raw/code-repos/vllm/snapshots/8357226/architecture.md)
- PagedAttention is about KV-cache layout and memory management, not approximate attention; it preserves attention semantics while changing how prior key/value state is addressed. (source: raw/paper/pagedattention.pdf, pp. 5-6)
- Prefix cache and paged KV cache are related but not identical: prefix cache is about reusing already-computed prefixes, while paged KV cache is a memory/layout strategy for storing and addressing KV state. (source: raw/code-repos/vllm/snapshots/8357226/key-flows.md; raw/code-repos/sglang/snapshots/b276a9a/key-flows.md; raw/code-repos/flashinfer/snapshots/4a4e36d/key-flows.md)
- Implementation details are engine-specific, so answer code questions by tracing the selected repo snapshot instead of assuming one engine's cache model applies to another. (source: raw/code-repos/vllm/snapshots/8357226/architecture.md; raw/code-repos/sglang/snapshots/b276a9a/architecture.md)

## Open questions

The current wiki records architecture-level cache concepts, but it does not yet compare cache eviction policies, fragmentation behavior, distributed transfer protocols, or benchmarked latency/memory tradeoffs across engines. (source: raw/code-repos/vllm/snapshots/8357226/key-flows.md; raw/code-repos/sglang/snapshots/b276a9a/key-flows.md)

## Related pages

- [[systems/flashattention]]
- [[systems/pagedattention]]
- [[papers/pagedattention]]
- [[systems/flashinfer]]
- [[systems/vllm]]
- [[systems/sglang]]
- [[concepts/attention]]
