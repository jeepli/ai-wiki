# FlashAttention-4

**Summary**: FlashAttention-4 redesigns exact attention for Blackwell GPUs, where tensor-core throughput scales faster than shared memory and exponential units, making non-matmul bottlenecks central to kernel design. (source: raw/paper/flashattention-4.pdf, pp. 1-2)

**Sources**: `raw/paper/flashattention-4.pdf`

**Last updated**: 2026-07-03

---

## Why it matters

The paper argues that Blackwell B200 changes the attention optimization problem: tensor-core throughput doubles relative to Hopper, while shared-memory bandwidth and exponential throughput scale more slowly or stay flat. (source: raw/paper/flashattention-4.pdf, pp. 1-2)

This makes FlashAttention-4 a case study in algorithm and kernel co-design for asymmetric hardware scaling: the attention algorithm must reduce or hide shared-memory traffic and softmax/exponential work, not only maximize matrix multiply occupancy. (source: raw/paper/flashattention-4.pdf, pp. 1-2, 10-12)

## Key ideas

- Redesign forward and backward pipelines around Blackwell's fully asynchronous MMA operations and larger tiles. (source: raw/paper/flashattention-4.pdf, pp. 1-2)
- Use software-emulated exponential and conditional softmax rescaling to reduce pressure on the exponential unit. (source: raw/paper/flashattention-4.pdf, pp. 1-2)
- Use tensor memory and 2-CTA MMA mode to reduce shared-memory traffic and reduce atomic additions in the backward pass. (source: raw/paper/flashattention-4.pdf, pp. 10-12)
- Implement the kernel in CuTe-DSL embedded in Python to retain low-level expressivity while reducing compile-time overhead. (source: raw/paper/flashattention-4.pdf, pp. 1-2, 16)

## Method or mechanism

Blackwell introduces tensor memory, larger 128x128 MMA tiles, and fully asynchronous tensor-core operations that write to tensor memory instead of registers; FlashAttention-4 builds schedules around those differences. (source: raw/paper/flashattention-4.pdf, pp. 2-4)

For backward attention, the paper's roofline analysis identifies shared-memory traffic as the bottleneck for typical tiles; the 2-CTA mode reduces operand-B shared-memory traffic and halves global atomic reductions for `dQ`. (source: raw/paper/flashattention-4.pdf, pp. 10-12)

The paper also provides a deterministic backward mode using ordered semaphore-protected reductions, trading some performance for reproducible training behavior. (source: raw/paper/flashattention-4.pdf, p. 12)

## Results and limitations

The paper reports up to 1.3x speedup over cuDNN 9.13 and 2.7x over Triton on B200 with BF16, reaching up to 1613 TFLOPs/s and 71% theoretical utilization. (source: raw/paper/flashattention-4.pdf, pp. 1-2)

The paper reports that FlashAttention-4 is implemented entirely in CuTe-DSL and achieves 20-30x faster compile times than C++ template-based kernels while preserving low-level control. (source: raw/paper/flashattention-4.pdf, pp. 1-2, 16)

The paper is optimized for Blackwell datacenter GPUs, but it argues that some ideas should transfer as compute continues to outpace non-matmul units on future accelerators. (source: raw/paper/flashattention-4.pdf, p. 16)

## Open questions

- Which FlashAttention-4 pipeline ideas will remain useful on future GPUs where exponential units, shared memory, or tensor memory scale differently? (source: raw/paper/flashattention-4.pdf, pp. 2, 16)
- How should production libraries select among FlashAttention-2, FlashAttention-3, FlashAttention-4, cuDNN, and Triton paths across GPU generations and precision modes? (source: raw/paper/flashattention-4.pdf, pp. 1-2)

## Related pages

- [[systems/flashattention]]
- [[papers/flashattention]]
- [[papers/flashattention-2]]
- [[papers/flashattention-3]]
- [[concepts/attention]]
- [[models/transformer]]
