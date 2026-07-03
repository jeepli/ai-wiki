---
repo: flashattention
commit: 73c992c8ca746935548df620ef3c1b6238fe6e68
source_version: 73c992c
document: key-flows.md
status: source-backed
---

# Key Flows

Source snapshot: `flashattention` commit
`73c992c8ca746935548df620ef3c1b6238fe6e68`.

## Dense Forward Attention

1. User code imports `flash_attn_func` from `flash_attn` or directly from
   `flash_attn.flash_attn_interface`
   (`flashattention@73c992c:flash_attn/__init__.py`,
   `flashattention@73c992c:flash_attn/flash_attn_interface.py#flash_attn_func`).
2. `flash_attn_func` normalizes arguments such as `dropout_p`, `softmax_scale`,
   `causal`, `window_size`, `softcap`, ALiBi slopes, determinism, and
   return-attention options, then goes through the autograd/custom-op wrapper
   path (`flashattention@73c992c:flash_attn/flash_attn_interface.py#_flash_attn_forward`).
3. `_flash_attn_forward` makes `q`, `k`, `v` contiguous when needed and calls
   `flash_attn_gpu.fwd`; on the default CUDA path this is the compiled
   `flash_attn_2_cuda` module, while ROCm can switch to an AITER Triton-backed
   implementation (`flashattention@73c992c:flash_attn/flash_attn_interface.py`).
4. The compiled binding layer maps tensors and options into `Flash_fwd_params`,
   including strides, dimensions, dropout representation, causal/local-window
   mode, softmax scale, and optional sequence metadata
   (`flashattention@73c992c:csrc/flash_attn/flash_api.cpp#set_params_fprop`).

## Variable-Length Attention

Varlen calls enter through `flash_attn_varlen_func`, which adds
`cu_seqlens_q`, `cu_seqlens_k`, max sequence lengths, optional block tables,
left padding, used-K sequence lengths, and split controls before dispatching to
`flash_attn_gpu.varlen_fwd`
(`flashattention@73c992c:flash_attn/flash_attn_interface.py#flash_attn_varlen_func`,
`flashattention@73c992c:flash_attn/flash_attn_interface.py#_flash_attn_varlen_forward`).

## Backward Pass

Autograd calls `_flash_attn_backward`, which accepts `dout`, saved `q/k/v/out`,
`softmax_lse`, optional preallocated gradients, dropout/scale/window/softcap
settings, deterministic mode, and RNG state. The binding layer fills
`Flash_bwd_params` by extending forward params with output-gradient and
input-gradient pointers
(`flashattention@73c992c:flash_attn/flash_attn_interface.py#_flash_attn_backward`,
`flashattention@73c992c:csrc/flash_attn/flash_api.cpp#set_params_dgrad`).

## Decode With KV Cache

`flash_attn_with_kvcache` serves incremental decode. It accepts query tensors,
existing `k_cache` / `v_cache`, optional new `k/v`, rotary tables, cache sequence
lengths, batch indices, left padding, block tables, windowing, ALiBi, split
controls, and optional LSE return
(`flashattention@73c992c:flash_attn/flash_attn_interface.py#flash_attn_with_kvcache`).
The Hopper interface expands the same flow with `page_table`, descale tensors,
`scheduler_metadata`, `pack_gqa`, and `sm_margin`
(`flashattention@73c992c:hopper/flash_attn_interface.py#flash_attn_with_kvcache`).
