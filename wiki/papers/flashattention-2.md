# FlashAttention-2

**Summary**: FlashAttention-2 keeps exact attention but improves the original FlashAttention kernel through better GPU work partitioning, more sequence-dimension parallelism, and fewer non-matmul operations. (source: raw/paper/flashattention-2.pdf, pp. 1, 5-8)

**Sources**: `raw/paper/flashattention-2.pdf`

**Last updated**: 2026-07-03

---

## Why it matters

FlashAttention made dense attention IO-aware and memory-efficient, but the paper argues that its A100 implementation still reached only a fraction of GEMM-like peak throughput because thread blocks and warps were not partitioning work optimally. (source: raw/paper/flashattention-2.pdf, p. 1)

The paper is useful for understanding that "memory-efficient attention" is not only about avoiding the `N x N` matrix; once HBM traffic is reduced, occupancy, shared-memory traffic, and non-matmul operations become important bottlenecks. (source: raw/paper/flashattention-2.pdf, pp. 1, 5)

## Key ideas

- Reduce non-matmul FLOPs in the online-softmax update because Tensor Core matmul throughput is much higher than FP32 non-matmul throughput on A100. (source: raw/paper/flashattention-2.pdf, p. 5)
- Parallelize over the sequence-length dimension in addition to batch and head dimensions so long-sequence, small-batch workloads can use more SMs. (source: raw/paper/flashattention-2.pdf, pp. 7-8)
- Partition work across warps within a thread block to reduce shared-memory reads and writes. (source: raw/paper/flashattention-2.pdf, p. 5)
- Preserve exact dense attention: the algorithm still returns `softmax(QK^T)V` and uses linear extra memory for logsumexp statistics. (source: raw/paper/flashattention-2.pdf, p. 6)

## Method or mechanism

FlashAttention-2 modifies the online softmax update by maintaining an unscaled output accumulator and applying the final normalization only at the end; for backward, it stores logsumexp instead of separately storing row maxima and sums. (source: raw/paper/flashattention-2.pdf, pp. 5-7)

The forward pass schedules row blocks of the attention matrix independently across thread blocks, while the backward pass also parallelizes by sequence blocks and uses atomic adds for the shared `dQ` accumulation. (source: raw/paper/flashattention-2.pdf, pp. 7-8)

The paper also discusses MQA and GQA support as indexing changes that avoid materializing duplicated key/value heads, while the backward pass must sum gradients for implicitly shared key/value heads. (source: raw/paper/flashattention-2.pdf, p. 7)

## Results and limitations

The paper reports that FlashAttention-2 is about 2x faster than FlashAttention in attention benchmarks on A100 and reaches up to 230 TFLOPs/s, or 73% of theoretical peak, in the measured settings. (source: raw/paper/flashattention-2.pdf, p. 10)

For GPT-style training on 8xA100, the paper reports up to 2.8x speedup over a baseline without FlashAttention, 1.3x speedup over FlashAttention, and up to 225 TFLOPs/s per A100 GPU. (source: raw/paper/flashattention-2.pdf, pp. 10-11)

The paper notes that simply running the implementation on H100 without using Hopper-specific features reaches higher raw throughput, but it leaves further H100-specific optimization to future work. (source: raw/paper/flashattention-2.pdf, p. 11)

## Open questions

- Which pieces of the FlashAttention-2 work-partitioning strategy remain optimal as GPU architectures add new asynchronous memory and matrix instructions? (source: raw/paper/flashattention-2.pdf, p. 11)
- How should exact attention kernels choose block sizes across sequence length, head dimension, register pressure, and shared-memory limits? (source: raw/paper/flashattention-2.pdf, pp. 5, 8)

## Related pages

- [[systems/flashattention]]
- [[papers/flashattention]]
- [[papers/flashattention-3]]
- [[papers/flashattention-4]]
- [[concepts/attention]]
- [[models/transformer]]
