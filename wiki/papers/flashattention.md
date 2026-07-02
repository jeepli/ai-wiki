# FlashAttention

**Summary**: This paper introduces FlashAttention, an IO-aware exact attention algorithm that uses tiling and recomputation to reduce GPU HBM reads/writes while preserving the mathematical result of attention. (source: raw/flashattention.pdf, p. 1)

**Sources**: `raw/flashattention.pdf`

**Last updated**: 2026-07-02

---

## Why it matters

The paper argues that many attention methods focus on reducing FLOPs, but wall-clock speed on GPUs is often dominated by memory access, especially reads and writes between HBM and on-chip SRAM. (source: raw/flashattention.pdf, pp. 1-3)

FlashAttention matters for long-context [[models/transformer]] training because it avoids materializing the large `N x N` attention matrix in HBM while still computing exact [[concepts/attention]]. (source: raw/flashattention.pdf, pp. 1, 4-5)

## Key ideas

- Standard attention computes `S = QK^T`, `P = softmax(S)`, and `O = PV`, and writes the `N x N` matrices `S` and `P` to HBM. (source: raw/flashattention.pdf, p. 4)
- FlashAttention tiles `Q`, `K`, and `V`, loads blocks into SRAM, computes block-local attention, and incrementally combines block results with numerically stable softmax statistics. (source: raw/flashattention.pdf, pp. 4-5)
- The algorithm stores output and softmax normalization statistics, then recomputes attention blocks during backward pass instead of storing `O(N^2)` intermediates. (source: raw/flashattention.pdf, pp. 5, 20-21)
- The paper extends the same IO-aware idea to block-sparse FlashAttention, whose IO complexity improves with the nonzero-block sparsity ratio. (source: raw/flashattention.pdf, pp. 6, 24-25)

## Method or mechanism

The forward pass loops over `K` and `V` blocks, then over `Q` blocks, computing local scores and softmax statistics in SRAM before writing the merged output back to HBM. (source: raw/flashattention.pdf, pp. 4-5)

The paper proves that dense FlashAttention returns `softmax(QK^T)V`, uses `O(N)` extra memory, and keeps the dominant FLOPs at `O(N^2 d)`. (source: raw/flashattention.pdf, p. 5)

The IO analysis states that standard attention requires `Theta(Nd + N^2)` HBM accesses, while FlashAttention requires `Theta(N^2 d^2 M^-1)` HBM accesses where `M` is SRAM size. (source: raw/flashattention.pdf, p. 6)

## Results and limitations

The paper reports that FlashAttention trains BERT-large 15% faster than the MLPerf 1.1 training speed record, speeds up GPT-2 training up to about 3x over HuggingFace and Megatron-LM baselines, and speeds up Long Range Arena training by about 2.4x. (source: raw/flashattention.pdf, pp. 1, 7-8)

The paper reports that GPT-2 with FlashAttention and 4K context is still 30% faster than Megatron-LM with 1K context while achieving 0.7 better perplexity. (source: raw/flashattention.pdf, p. 8)

The paper reports that FlashAttention memory footprint grows linearly with sequence length and is up to 20x more memory-efficient than exact attention baselines in its benchmark. (source: raw/flashattention.pdf, pp. 9-10)

The main limitation is engineering cost: the implementation requires writing low-level CUDA kernels, and implementations may not transfer directly across GPU architectures or new attention variants. (source: raw/flashattention.pdf, p. 10)

## Open questions

- Which parts of deep learning beyond attention should be redesigned around IO-aware algorithms? (source: raw/flashattention.pdf, p. 10)
- How should IO-aware attention be analyzed and implemented across multiple GPUs, where inter-GPU communication adds another memory hierarchy? (source: raw/flashattention.pdf, p. 10)

## Related pages

- [[systems/flashattention]]
- [[concepts/attention]]
- [[models/transformer]]
- [[papers/attention-is-all-you-need]]
