# Attention

**Summary**: Attention maps a query and key-value pairs to an output by weighting values according to query-key compatibility; self-attention applies this mechanism within a single sequence. (source: raw/attention-is-all-you-need.pdf, pp. 3-5)

**Sources**: `raw/attention-is-all-you-need.pdf`; `raw/flashattention.pdf`

**Last updated**: 2026-07-02

---

## Intuition

Attention is a learned retrieval-and-aggregation operation: a query asks what information is needed, keys determine relevance, and values provide the information to aggregate. (source: raw/attention-is-all-you-need.pdf, p. 3)

Self-attention lets every position in a sequence directly access other positions, which shortens dependency paths compared with recurrent layers. (source: raw/attention-is-all-you-need.pdf, pp. 2, 6)

## Definition

Scaled dot-product attention computes `Attention(Q, K, V) = softmax(QK^T / sqrt(d_k))V`. (source: raw/attention-is-all-you-need.pdf, p. 4)

The `1 / sqrt(d_k)` scale helps avoid very large dot products when key/query dimensions are large, because large values can push softmax into regions with very small gradients. (source: raw/attention-is-all-you-need.pdf, p. 4)

Multi-head attention applies attention in multiple projected subspaces, concatenates the head outputs, and projects them again. (source: raw/attention-is-all-you-need.pdf, pp. 4-5)

## Why it matters

In [[models/transformer]], attention appears as encoder self-attention, decoder masked self-attention, and encoder-decoder attention. (source: raw/attention-is-all-you-need.pdf, p. 5)

The main systems cost of full attention is that standard implementations materialize `N x N` score and probability matrices, which makes long sequences expensive in memory and HBM traffic. (source: raw/flashattention.pdf, pp. 1, 4)

## Common pitfalls

- Lower FLOPs do not guarantee faster wall-clock time; memory access can dominate runtime on GPUs. (source: raw/flashattention.pdf, pp. 1-2)
- Self-attention has short dependency paths, but full attention still has `O(n^2 d)` per-layer compute in the Transformer paper's comparison. (source: raw/attention-is-all-you-need.pdf, p. 6)
- Masked decoder self-attention is not the same as encoder self-attention; masking prevents access to future output tokens. (source: raw/attention-is-all-you-need.pdf, p. 5)

## Related pages

- [[models/transformer]]
- [[systems/flashattention]]
- [[papers/attention-is-all-you-need]]
- [[papers/flashattention]]
