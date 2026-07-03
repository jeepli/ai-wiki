# LLM Wiki Index

**Summary**: Table of contents for the personal AI learning wiki.

**Last updated**: 2026-07-03

---

## Papers

- [[papers/attention-is-all-you-need]] - Source summary for the Transformer paper and its attention-based architecture.
- [[papers/flashattention]] - Source summary for the FlashAttention paper and its IO-aware exact attention algorithm.
- [[papers/flashattention-2]] - Source summary for FlashAttention-2 and its GPU work-partitioning improvements.
- [[papers/flashattention-3]] - Source summary for FlashAttention-3 and its Hopper asynchronous and FP8 attention kernels.
- [[papers/flashattention-4]] - Source summary for FlashAttention-4 and its Blackwell attention pipeline co-design.
- [[papers/pagedattention]] - Source summary for the PagedAttention paper and vLLM's KV-cache memory management.

## Concepts

- [[concepts/attention]] - Query-key-value attention, self-attention, scaled dot-product attention, and multi-head attention.
- [[concepts/kv-cache]] - KV cache, paged KV cache, prefix cache, and serving-time cache management.

## Models

- [[models/transformer]] - Transformer architecture, core components, and main limitations.

## Systems

- [[systems/flashattention]] - FlashAttention as a memory-efficient exact attention system and kernel package.
- [[systems/flashinfer]] - FlashInfer as a serving-kernel library for paged KV-cache attention and related inference primitives.
- [[systems/pagedattention]] - PagedAttention as a KV-cache paging and block-table memory management method for LLM serving.
- [[systems/vllm]] - vLLM as an inference and serving engine with scheduling, KV cache management, and attention backend selection.
- [[systems/sglang]] - SGLang as a structured generation framework and serving runtime with scheduler, radix cache, and kernel package.

## Math

- No pages yet.
