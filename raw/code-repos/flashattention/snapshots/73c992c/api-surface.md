---
repo: flashattention
commit: 73c992c8ca746935548df620ef3c1b6238fe6e68
source_version: 73c992c
document: api-surface.md
status: source-backed
---

# Api Surface

Source snapshot: `flashattention` commit
`73c992c8ca746935548df620ef3c1b6238fe6e68`.

## Public Imports

`flash_attn/__init__.py` exposes the package-level attention API:

- `flash_attn_func`
- `flash_attn_kvpacked_func`
- `flash_attn_qkvpacked_func`
- `flash_attn_varlen_func`
- `flash_attn_varlen_kvpacked_func`
- `flash_attn_varlen_qkvpacked_func`
- `flash_attn_with_kvcache`

Citation: `flashattention@73c992c:flash_attn/__init__.py`.

## Core Function Families

- Dense attention: `flash_attn_func(q, k, v, dropout_p=0.0, softmax_scale=None,
  causal=False, window_size=(-1, -1), softcap=0.0, alibi_slopes=None,
  deterministic=False, return_attn_probs=False)`
  (`flashattention@73c992c:flash_attn/flash_attn_interface.py#flash_attn_func`).
- Variable-length attention: `flash_attn_varlen_func(q, k, v, cu_seqlens_q,
  cu_seqlens_k, max_seqlen_q, max_seqlen_k, ...)`
  (`flashattention@73c992c:flash_attn/flash_attn_interface.py#flash_attn_varlen_func`).
- Decode/KV cache: `flash_attn_with_kvcache(q, k_cache, v_cache, k=None,
  v=None, rotary_cos=None, rotary_sin=None, cache_seqlens=None, block_table=None,
  ...)`
  (`flashattention@73c992c:flash_attn/flash_attn_interface.py#flash_attn_with_kvcache`).
- Experimental/newer GPU path: `hopper/flash_attn_interface.py` provides
  similarly named functions with extra parameters for paged metadata, descale,
  scheduler hints, packed GQA, and SM margin
  (`flashattention@73c992c:hopper/flash_attn_interface.py#flash_attn_func`).

## Extension and Integration APIs

- `flash_attn/modules/mha.py` integrates package functions into MHA-style modules.
- `flash_attn/bert_padding.py` supports unpadding/repadding flows used by varlen
  attention.
- `flash_attn/layers/rotary.py` and `flash_attn/layers/patch_embed.py` provide
  model-layer helpers.
- `flash_attn/ops/` exposes related fused operations such as fused dense,
  layer norm, RMSNorm, and activations.

## Non-Stable Internal APIs

Symbols prefixed with `_flash_attn_*` are the lower-level torch custom-op /
autograd boundary and should be treated as internal unless investigating
dispatch, tracing, or kernel integration
(`flashattention@73c992c:flash_attn/flash_attn_interface.py#_flash_attn_forward`,
`flashattention@73c992c:flash_attn/flash_attn_interface.py#_flash_attn_backward`).
