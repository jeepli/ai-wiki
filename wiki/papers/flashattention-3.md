# FlashAttention-3

**Summary**: FlashAttention-3 specializes exact attention for Hopper GPUs by using asynchronous Tensor Core and TMA execution, warp specialization, GEMM-softmax overlap, and FP8-aware quantization techniques. (source: raw/paper/flashattention-3.pdf, pp. 1-2, 4-7)

**Sources**: `raw/paper/flashattention-3.pdf`

**Last updated**: 2026-07-03

---

## Why it matters

FlashAttention-2 improved work partitioning on A100-class GPUs, but the FlashAttention-3 paper argues that it still underuses Hopper H100 relative to optimized GEMM because it does not explicitly exploit asynchrony or low-precision hardware features. (source: raw/paper/flashattention-3.pdf, pp. 1-2)

The paper is a good example of hardware-aware algorithm design: after HBM traffic and basic occupancy are improved, the next bottleneck is coordinating Tensor Cores, TMA memory movement, softmax, register pressure, and FP8 layout constraints. (source: raw/paper/flashattention-3.pdf, pp. 2, 4-7)

## Key ideas

- Use producer-consumer warp specialization so some warps issue data movement while others consume loaded tiles for matrix operations. (source: raw/paper/flashattention-3.pdf, pp. 2, 4-5)
- Use ping-pong scheduling to overlap softmax from one warpgroup with asynchronous WGMMA operations from another warpgroup. (source: raw/paper/flashattention-3.pdf, pp. 5-6)
- Pipeline block-wise GEMMs and softmax across loop iterations so `QK^T` and `PV` work can overlap with softmax-related operations. (source: raw/paper/flashattention-3.pdf, pp. 6-7)
- Add FP8 support with layout transformations, block quantization, and incoherent processing to reduce quantization error from outlier features. (source: raw/paper/flashattention-3.pdf, pp. 7, 11)

## Method or mechanism

FlashAttention-3 uses Hopper-specific TMA loads and WGMMA operations inside a warp-specialized CTA structure: producer warps issue asynchronous loads into shared memory, while consumer warps run attention computation. (source: raw/paper/flashattention-3.pdf, pp. 4-5)

The 2-stage GEMM-softmax pipeline computes the next score block with WGMMA while using the previous block's softmax probabilities for the value matmul, breaking the fully synchronous structure of FlashAttention-2's inner loop. (source: raw/paper/flashattention-3.pdf, pp. 6-7)

For FP8, the kernel must satisfy WGMMA layout requirements and mitigate quantization error; the paper uses in-kernel transpose, register permutation, per-block scaling, and incoherent processing. (source: raw/paper/flashattention-3.pdf, pp. 7-8, 11)

## Results and limitations

The paper reports 1.5-2.0x forward speedup over FlashAttention-2 on H100 for FP16, up to 740 TFLOPs/s and 75% utilization, plus 1.5-1.75x backward speedup. (source: raw/paper/flashattention-3.pdf, pp. 1-2, 11)

For FP8 forward attention, the paper reports performance close to 1.2 PFLOPs/s and reports that block quantization plus incoherent processing makes FP8 FlashAttention-3 2.6x more accurate than a per-tensor FP8 baseline in its outlier-feature test. (source: raw/paper/flashattention-3.pdf, pp. 1-2, 11-12)

The paper lists future work around LLM inference, persistent-kernel design for FP8, and understanding low-precision attention in large-scale training. (source: raw/paper/flashattention-3.pdf, p. 12)

## Open questions

- How much of FlashAttention-3's Hopper-specific pipeline transfers to later architectures with different accumulator storage and asynchronous execution behavior? (source: raw/paper/flashattention-3.pdf, pp. 2, 12)
- What quality and stability tradeoffs appear when FP8 attention is used in full-scale training rather than kernel-level numerical tests? (source: raw/paper/flashattention-3.pdf, p. 12)

## Related pages

- [[systems/flashattention]]
- [[papers/flashattention]]
- [[papers/flashattention-2]]
- [[papers/flashattention-4]]
- [[concepts/attention]]
- [[models/transformer]]
