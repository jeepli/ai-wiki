# FlashAttention

**Summary**: FlashAttention is an IO-aware exact attention implementation pattern that computes dense attention while reducing HBM traffic and avoiding storage of the full attention matrix. (source: raw/flashattention.pdf, pp. 1, 4-5)

**Sources**: `raw/flashattention.pdf`; `raw/attention-is-all-you-need.pdf`

**Last updated**: 2026-07-02

---

## Why it matters

Full [[concepts/attention]] in [[models/transformer]] needs interactions between all token positions, and the standard implementation stores large `N x N` score/probability matrices in GPU HBM. (source: raw/attention-is-all-you-need.pdf, p. 6; raw/flashattention.pdf, p. 4)

FlashAttention is useful as a system idea because it treats memory movement as a first-class algorithmic cost, not just an implementation detail. (source: raw/flashattention.pdf, pp. 1-3)

## Method or mechanism

The stable core pattern is: tile inputs, keep blocks in SRAM, compute local score/softmax/value products, maintain online softmax statistics, and write only the merged output back to HBM. (source: raw/flashattention.pdf, pp. 4-5)

For backward pass, the stable pattern is to save compact statistics and recompute attention blocks instead of saving the full attention probability matrix. (source: raw/flashattention.pdf, pp. 5, 20-21)

Kernel fusion matters because it keeps intermediate operations such as masking, softmax, dropout, and matrix multiplication close to the data rather than repeatedly round-tripping through HBM. (source: raw/flashattention.pdf, p. 5)

## Results and limitations

As a reusable systems concept, FlashAttention preserves exact dense attention while improving memory behavior; paper-specific benchmark numbers live in [[papers/flashattention]]. (source: raw/flashattention.pdf, pp. 5-10)

The system approach is constrained by implementation complexity: new variants or hardware targets may require low-level kernels or compiler support. (source: raw/flashattention.pdf, p. 10)

## Common pitfalls

- Dense FlashAttention is exact attention, not approximate attention. (source: raw/flashattention.pdf, p. 5)
- FlashAttention changes execution and memory access, not the model's attention equation. (source: raw/flashattention.pdf, pp. 4-5)
- Block-sparse FlashAttention is a separate approximate sparse variant and should not be conflated with dense exact FlashAttention. (source: raw/flashattention.pdf, pp. 6, 24-25)

## Related pages

- [[papers/flashattention]]
- [[concepts/attention]]
- [[models/transformer]]
- [[papers/attention-is-all-you-need]]
