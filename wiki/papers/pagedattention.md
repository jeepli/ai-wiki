# PagedAttention

**Summary**: This paper introduces PagedAttention and vLLM, using OS-style paging ideas to manage dynamic KV-cache memory for high-throughput LLM serving. (source: raw/paper/pagedattention.pdf, pp. 1-2)

**Sources**: `raw/paper/pagedattention.pdf`

**Last updated**: 2026-07-03

---

## Why it matters

LLM serving throughput depends heavily on batching, but the paper argues that dynamic KV-cache memory limits batch size because each request's cache is large, grows over time, and has unknown lifetime and final length. (source: raw/paper/pagedattention.pdf, pp. 1-3)

The paper frames KV-cache memory management as a systems bottleneck: contiguous preallocation causes reserved memory waste, internal fragmentation, external fragmentation, and missed sharing opportunities across parallel sampling, beam search, and shared-prefix workloads. (source: raw/paper/pagedattention.pdf, pp. 2-3)

## Key ideas

- PagedAttention splits each sequence's KV cache into fixed-size KV blocks and allows logically contiguous KV cache to live in non-contiguous physical GPU memory. (source: raw/paper/pagedattention.pdf, pp. 2, 5)
- vLLM maintains block tables that map logical KV blocks to physical KV blocks, similar to virtual-memory page tables. (source: raw/paper/pagedattention.pdf, pp. 5-6)
- Blocks are allocated on demand as decoding progresses, so a request's unused reserved memory is bounded by one block. (source: raw/paper/pagedattention.pdf, p. 6)
- The system supports memory sharing through operations such as fork, append, and free, enabling efficient parallel sampling, beam search, and prefix sharing. (source: raw/paper/pagedattention.pdf, p. 9)

## Method or mechanism

The PagedAttention kernel reads key/value blocks through block-table metadata, computes attention over separately fetched KV blocks, and writes newly generated KV cache into allocated physical blocks. (source: raw/paper/pagedattention.pdf, pp. 5-6)

vLLM combines a centralized scheduler, a KV-cache manager, CPU/GPU block allocators, distributed GPU workers, and custom kernels for PagedAttention and block copy. (source: raw/paper/pagedattention.pdf, pp. 5, 9)

The paper's memory-manager abstraction separates logical blocks from physical blocks, records how many positions are filled in each logical block, and can free blocks when a request completes. (source: raw/paper/pagedattention.pdf, pp. 5-6)

## Results and limitations

The paper reports that vLLM improves throughput by 2-4x at similar latency compared with FasterTransformer and Orca, with larger gains for longer sequences, larger models, and more complex decoding algorithms. (source: raw/paper/pagedattention.pdf, pp. 1-2)

The paper reports that prior systems use only 20.4%-38.2% of KV-cache memory for actual token states in one profiling setup, while vLLM reduces waste through block-level allocation and sharing. (source: raw/paper/pagedattention.pdf, p. 2)

The paper's discussion says the paging idea is most useful when dynamic memory allocation and memory capacity limit throughput; for workloads with static tensor shapes or compute-bound serving, paging overhead can outweigh the benefit. (source: raw/paper/pagedattention.pdf, pp. 15-16)

## Open questions

- How should block size be tuned across models, prompt/output length distributions, and decoding algorithms? (source: raw/paper/pagedattention.pdf, pp. 6, 14)
- How should serving systems combine paged KV cache with newer offload, prefix caching, disaggregation, and distributed transfer mechanisms? (source: raw/paper/pagedattention.pdf, pp. 13-16)

## Related pages

- [[systems/pagedattention]]
- [[systems/vllm]]
- [[concepts/kv-cache]]
- [[concepts/attention]]
- [[models/transformer]]
