# Transformer

**Summary**: Transformer is an attention-based encoder-decoder model architecture that replaces recurrent and convolutional sequence modeling layers with stacked self-attention and feed-forward blocks. (source: raw/paper/attention-is-all-you-need.pdf, pp. 1-3)

**Sources**: `raw/paper/attention-is-all-you-need.pdf`; `raw/paper/flashattention.pdf`

**Last updated**: 2026-07-02

---

## Why it matters

Transformer made sequence modeling more parallelizable by removing recurrence from the main architecture and using [[concepts/attention]] to connect sequence positions. (source: raw/paper/attention-is-all-you-need.pdf, pp. 1-2)

Its long-sequence bottleneck is full attention's quadratic matrix, which later systems work such as [[systems/flashattention]] optimizes without changing the model's attention result. (source: raw/paper/attention-is-all-you-need.pdf, p. 6; raw/paper/flashattention.pdf, pp. 1, 4-5)

## Key ideas

- The encoder produces continuous representations for the input sequence. (source: raw/paper/attention-is-all-you-need.pdf, pp. 2-3)
- The decoder autoregressively generates output tokens and uses masked self-attention to preserve causal ordering. (source: raw/paper/attention-is-all-you-need.pdf, p. 3)
- Each encoder layer combines multi-head self-attention with a position-wise feed-forward network. (source: raw/paper/attention-is-all-you-need.pdf, p. 3)
- Each decoder layer adds encoder-decoder attention so decoder states can attend to encoder outputs. (source: raw/paper/attention-is-all-you-need.pdf, p. 3)

## Method or mechanism

The original model uses residual connections and layer normalization around each sub-layer, with `d_model = 512` in the base setup. (source: raw/paper/attention-is-all-you-need.pdf, p. 3)

The position-wise feed-forward network is two linear transformations with a ReLU in between, applied independently to each sequence position; the paper uses `d_ff = 2048`. (source: raw/paper/attention-is-all-you-need.pdf, p. 5)

The architecture injects order by adding positional encodings to token embeddings because it has no recurrence or convolution. (source: raw/paper/attention-is-all-you-need.pdf, p. 6)

## Results and limitations

The original paper reports state-of-the-art machine translation results for its time with lower training cost than several recurrent and convolutional baselines. (source: raw/paper/attention-is-all-you-need.pdf, pp. 7-8)

The architecture's full self-attention has `O(n^2 d)` per-layer complexity, so long contexts require either restricted attention, more efficient systems, or other architectural changes. (source: raw/paper/attention-is-all-you-need.pdf, p. 6)

## Common pitfalls

- Transformer is not "only attention"; feed-forward layers, residual connections, normalization, embeddings, positional encodings, and training schedule are all part of the original system. (source: raw/paper/attention-is-all-you-need.pdf, pp. 3-7)
- [[systems/flashattention]] is not a different model architecture; it is an implementation method for exact attention. (source: raw/paper/flashattention.pdf, pp. 4-5)

## Related pages

- [[papers/attention-is-all-you-need]]
- [[concepts/attention]]
- [[systems/flashattention]]
- [[papers/flashattention]]
