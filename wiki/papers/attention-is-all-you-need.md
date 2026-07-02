# Attention Is All You Need

**Summary**: This paper introduces the Transformer, an encoder-decoder architecture based entirely on attention mechanisms instead of recurrence or convolution. (source: raw/attention-is-all-you-need.pdf, p. 1)

**Sources**: `raw/attention-is-all-you-need.pdf`

**Last updated**: 2026-07-02

---

## Why it matters

Transformer changed sequence modeling by making [[concepts/attention]] the central dependency mechanism, which made training more parallelizable than recurrent models and gave each token a short path to every other token. (source: raw/attention-is-all-you-need.pdf, pp. 1-2, 6)

The paper is also the source for the canonical [[models/transformer]] block: multi-head attention, position-wise feed-forward networks, residual connections, layer normalization, embeddings, and positional encodings. (source: raw/attention-is-all-you-need.pdf, pp. 3-6)

## Key ideas

- The model keeps the encoder-decoder pattern: the encoder maps input tokens to continuous representations, and the decoder autoregressively generates output tokens. (source: raw/attention-is-all-you-need.pdf, pp. 2-3)
- Encoder layers contain multi-head self-attention and a position-wise feed-forward network, each wrapped with residual connection and layer normalization. (source: raw/attention-is-all-you-need.pdf, p. 3)
- Decoder layers add encoder-decoder attention and use masking in decoder self-attention so a position cannot attend to future output tokens. (source: raw/attention-is-all-you-need.pdf, p. 3)
- Scaled dot-product attention computes `softmax(QK^T / sqrt(d_k))V`; the scale factor counteracts large dot products that push softmax into low-gradient regions. (source: raw/attention-is-all-you-need.pdf, p. 4)
- Multi-head attention projects queries, keys, and values into multiple learned subspaces so different heads can attend to different positions and representation subspaces. (source: raw/attention-is-all-you-need.pdf, pp. 4-5)

## Method or mechanism

The Transformer uses attention in three places: encoder self-attention, masked decoder self-attention, and encoder-decoder attention from decoder states to encoder outputs. (source: raw/attention-is-all-you-need.pdf, p. 5)

The base configuration uses `N = 6` encoder and decoder layers, `d_model = 512`, `d_ff = 2048`, `h = 8` attention heads, and `d_k = d_v = 64` per head. (source: raw/attention-is-all-you-need.pdf, pp. 3-5)

Because the model has no recurrence or convolution, it adds sinusoidal positional encodings to token embeddings to inject sequence order. (source: raw/attention-is-all-you-need.pdf, p. 6)

## Results and limitations

On WMT 2014 English-to-German, Transformer big reports 28.4 BLEU and improves over previously reported best results, including ensembles, by more than 2 BLEU. (source: raw/attention-is-all-you-need.pdf, pp. 1, 8)

On WMT 2014 English-to-French, Transformer big reports 41.8 BLEU after training for 3.5 days on 8 P100 GPUs. (source: raw/attention-is-all-you-need.pdf, pp. 1, 8)

The paper notes that self-attention has per-layer complexity `O(n^2 d)`, which becomes a limitation for very long sequences and motivates later efficient-attention systems such as [[systems/flashattention]]. (source: raw/attention-is-all-you-need.pdf, p. 6; raw/flashattention.pdf, pp. 1-2)

## Open questions

- How should position information be represented for contexts much longer than those seen in training? The original paper found sinusoidal and learned positional embeddings nearly identical on its translation setup. (source: raw/attention-is-all-you-need.pdf, pp. 6, 9)
- Which attention restrictions or implementations best preserve quality while reducing long-sequence cost remains a recurring research question. (source: raw/attention-is-all-you-need.pdf, pp. 6, 10)

## Related pages

- [[models/transformer]]
- [[concepts/attention]]
- [[papers/flashattention]]
- [[systems/flashattention]]
