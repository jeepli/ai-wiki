# PagedAttention

**Summary**: PagedAttention is a serving-time KV-cache memory management technique that lets attention operate over non-contiguous fixed-size KV blocks, enabling vLLM-style block allocation and sharing. (source: raw/paper/pagedattention.pdf, pp. 1-6)

**Sources**: `raw/paper/pagedattention.pdf`; `raw/code-repos/vllm/snapshots/8357226/architecture.md`; `raw/code-repos/vllm/snapshots/8357226/key-flows.md`

**Last updated**: 2026-07-03

---

## Why it matters

Autoregressive serving repeatedly attends over prior tokens, so GPU memory used by the KV cache controls how many requests can be batched. PagedAttention targets memory fragmentation and duplication rather than changing the model's attention equation. (source: raw/paper/pagedattention.pdf, pp. 1-3)

This makes PagedAttention a reusable system idea separate from the vLLM codebase: it applies OS-style paging to KV-cache state so serving engines can allocate, share, and free cache blocks dynamically. (source: raw/paper/pagedattention.pdf, pp. 2, 5-6)

## Method or mechanism

PagedAttention partitions the KV cache into fixed-size KV blocks; logical blocks for a sequence map to physical blocks in GPU memory through block tables, and those physical blocks need not be contiguous. (source: raw/paper/pagedattention.pdf, pp. 5-6)

During decoding, the kernel uses the block table to fetch previous KV blocks, computes attention over the blocks, and stores new key/value state into the current logical block or a newly allocated physical block. (source: raw/paper/pagedattention.pdf, pp. 5-6)

The vLLM paper connects this kernel idea to scheduler-level operations: allocating blocks on demand, freeing completed-request blocks, using copy-on-write for sharing, and supporting fork/append/free operations for decoding algorithms. (source: raw/paper/pagedattention.pdf, pp. 6, 9)

## Implementation shape

In the current code-derived vLLM snapshot, the V1 runtime has a `KVCacheManager` that exposes `KVCacheBlocks` to the scheduler, tracks block-pool usage, and performs prefix-cache lookup through `get_computed_blocks`. (source: raw/code-repos/vllm/snapshots/8357226/architecture.md; raw/code-repos/vllm/snapshots/8357226/key-flows.md)

PagedAttention as a paper mechanism and vLLM as a codebase should be kept separate: the paper describes the original block-table memory model, while the current vLLM snapshot includes additional runtime layers, attention backends, and scheduler machinery. (source: raw/paper/pagedattention.pdf, pp. 5-6; raw/code-repos/vllm/snapshots/8357226/overview.md)

## Results and limitations

The paper reports that vLLM improves LLM serving throughput by 2-4x over FasterTransformer and Orca at similar latency in its evaluated workloads. (source: raw/paper/pagedattention.pdf, pp. 1-2)

The main limitation is that paging helps most when memory capacity and dynamic allocation constrain throughput; for static-shape or compute-bound workloads, the indirection and non-contiguous access overhead may not pay off. (source: raw/paper/pagedattention.pdf, pp. 15-16)

## Common pitfalls

- PagedAttention is not approximate attention; it changes KV-cache layout and memory management for serving. (source: raw/paper/pagedattention.pdf, pp. 5-6)
- Paged KV cache and prefix cache are related but different: paging is a physical memory layout strategy, while prefix caching reuses previously computed prefix states. (source: raw/paper/pagedattention.pdf, pp. 6, 13)
- The best block size is workload-dependent because small blocks increase metadata and kernel overhead, while large blocks increase internal fragmentation and reduce sharing opportunities. (source: raw/paper/pagedattention.pdf, pp. 6, 14)

## Open questions

The current wiki does not yet compare PagedAttention against later serving memory systems for eviction policy, offload, multi-GPU transfer, disaggregated prefill/decode, or prefix-cache interaction. (source: raw/paper/pagedattention.pdf, pp. 13-16; raw/code-repos/vllm/snapshots/8357226/key-flows.md)

## Related pages

- [[papers/pagedattention]]
- [[concepts/kv-cache]]
- [[systems/vllm]]
- [[systems/flashinfer]]
- [[systems/sglang]]
- [[models/transformer]]
