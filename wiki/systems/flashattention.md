# FlashAttention

**Summary**: FlashAttention is an IO-aware exact attention implementation pattern and kernel package that reduces HBM traffic for dense attention while exposing PyTorch-facing APIs, CUDA/C++ bindings, Hopper kernels, and KV-cache decode paths. (source: raw/paper/flashattention.pdf, pp. 1, 4-5; raw/code-repos/flashattention/snapshots/73c992c/overview.md)

**Sources**: `raw/paper/flashattention.pdf`; `raw/paper/attention-is-all-you-need.pdf`; `raw/code-repos/flashattention/latest.yml`; `raw/code-repos/flashattention/snapshots/73c992c/overview.md`; `raw/code-repos/flashattention/snapshots/73c992c/architecture.md`; `raw/code-repos/flashattention/snapshots/73c992c/key-flows.md`; `raw/code-repos/flashattention/snapshots/73c992c/api-surface.md`; `raw/code-repos/flashattention/snapshots/73c992c/build-and-entrypoints.md`

**Last updated**: 2026-07-03

---

## Why it matters

Full [[concepts/attention]] in [[models/transformer]] needs interactions between all token positions, and the standard implementation stores large `N x N` score/probability matrices in GPU HBM. (source: raw/paper/attention-is-all-you-need.pdf, p. 6; raw/paper/flashattention.pdf, p. 4)

FlashAttention is useful as a system idea because it treats memory movement as a first-class algorithmic cost, not just an implementation detail. (source: raw/paper/flashattention.pdf, pp. 1-3)

## Method or mechanism

The stable core pattern is: tile inputs, keep blocks in SRAM, compute local score/softmax/value products, maintain online softmax statistics, and write only the merged output back to HBM. (source: raw/paper/flashattention.pdf, pp. 4-5)

For backward pass, the stable pattern is to save compact statistics and recompute attention blocks instead of saving the full attention probability matrix. (source: raw/paper/flashattention.pdf, pp. 5, 20-21)

Kernel fusion matters because it keeps intermediate operations such as masking, softmax, dropout, and matrix multiplication close to the data rather than repeatedly round-tripping through HBM. (source: raw/paper/flashattention.pdf, p. 5)

## Implementation shape

The current code-derived source snapshot presents FlashAttention as a thin Python API over compiled attention kernels: `flash_attn/__init__.py` re-exports dense, packed, varlen, and KV-cache functions, while `flash_attn/flash_attn_interface.py` owns the PyTorch custom-op and autograd-facing wrappers. (source: raw/code-repos/flashattention/snapshots/73c992c/overview.md; raw/code-repos/flashattention/snapshots/73c992c/architecture.md)

The compiled boundary is `csrc/flash_attn/flash_api.cpp`, which validates tensors and fills forward/backward parameter structs before dispatching kernels; generated kernel families are controlled by `csrc/flash_attn/src/generate_kernels.py` and `hopper/generate_kernels.py`. (source: raw/code-repos/flashattention/snapshots/73c992c/overview.md; raw/code-repos/flashattention/snapshots/73c992c/architecture.md)

The implementation has separate paths for dense forward attention, variable-length attention, backward recomputation, and incremental decode through `flash_attn_with_kvcache`; the Hopper interface adds paged-cache metadata, descale tensors, scheduler metadata, packed GQA controls, and SM margin controls. (source: raw/code-repos/flashattention/snapshots/73c992c/key-flows.md)

The package build is controlled by `setup.py` and build-time environment variables such as `BUILD_TARGET`, `FLASH_ATTENTION_TRITON_AMD_ENABLE`, `FLASH_ATTENTION_FORCE_BUILD`, `FLASH_ATTENTION_SKIP_CUDA_BUILD`, and `FLASH_ATTN_CUDA_ARCHS`. (source: raw/code-repos/flashattention/snapshots/73c992c/build-and-entrypoints.md)

## Results and limitations

As a reusable systems concept, FlashAttention preserves exact dense attention while improving memory behavior; paper-specific benchmark numbers live in [[papers/flashattention]]. (source: raw/paper/flashattention.pdf, pp. 5-10)

The system approach is constrained by implementation complexity: new variants or hardware targets may require low-level kernels, compiler support, or generated kernel specialization. (source: raw/paper/flashattention.pdf, p. 10; raw/code-repos/flashattention/snapshots/73c992c/architecture.md)

## Common pitfalls

- Dense FlashAttention is exact attention, not approximate attention. (source: raw/paper/flashattention.pdf, p. 5)
- FlashAttention changes execution and memory access, not the model's attention equation. (source: raw/paper/flashattention.pdf, pp. 4-5)
- Block-sparse FlashAttention is a separate approximate sparse variant and should not be conflated with dense exact FlashAttention. (source: raw/paper/flashattention.pdf, pp. 6, 24-25)
- The code package is not just one kernel: it includes Python API wrappers, CUDA/C++ bindings, generated kernels, Hopper paths, ROCm/Triton fallbacks, tests, and benchmarks. (source: raw/code-repos/flashattention/snapshots/73c992c/overview.md)

## Open questions

The current wiki source records architecture and key flows for commit `73c992c`, but it does not benchmark this snapshot or compare it against future FlashAttention releases. (source: raw/code-repos/flashattention/snapshots/73c992c/manifest.yml)

## Related pages

- [[papers/flashattention]]
- [[concepts/attention]]
- [[concepts/kv-cache]]
- [[models/transformer]]
- [[systems/flashinfer]]
- [[systems/vllm]]
- [[papers/attention-is-all-you-need]]
