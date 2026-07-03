---
repo: vllm
commit: 8357226f4f1b92aa2139ebc482ca71012f02016b
source_version: 8357226
document: key-flows.md
status: source-backed
---

# Key Flows

Source snapshot: `vllm` commit
`8357226f4f1b92aa2139ebc482ca71012f02016b`.

## OpenAI-Compatible Serving Startup

1. CLI/server args are parsed by the entrypoint stack declared in
   `pyproject.toml` (`vllm = vllm.entrypoints.cli.main:main`) and handled by
   OpenAI server utilities (`vllm@8357226:pyproject.toml`,
   `vllm@8357226:vllm/entrypoints/openai/api_server.py`).
2. `build_app(...)` creates the FastAPI app, stores args on app state, registers
   vLLM serve routers, OpenAI model routers, SageMaker routers, generate routes,
   scale-out routes, and middleware/exception handling
   (`vllm@8357226:vllm/entrypoints/openai/api_server.py#build_app`).
3. `build_async_engine_client(...)` creates `AsyncEngineArgs` from CLI args and
   delegates to `build_async_engine_client_from_engine_args(...)`
   (`vllm@8357226:vllm/entrypoints/openai/api_server.py#build_async_engine_client`).
4. The engine args create `VllmConfig`, and `AsyncLLM.from_vllm_config(...)`
   creates the V1 async engine client
   (`vllm@8357226:vllm/entrypoints/openai/api_server.py#build_async_engine_client_from_engine_args`,
   `vllm@8357226:vllm/v1/engine/async_llm.py#AsyncLLM.from_vllm_config`).

## Request Execution Through V1 Engine

`AsyncLLM` converts incoming `EngineInput` into `EngineCoreRequest` using
`InputProcessor`, converts `EngineCoreOutputs` into `RequestOutput` with
`OutputProcessor`, and talks to the background engine through
`EngineCoreClient.make_async_mp_client`
(`vllm@8357226:vllm/v1/engine/async_llm.py#AsyncLLM`). Engine core classes are
defined in `vllm/v1/engine/core.py`, with `EngineCore`, `EngineCoreProc`, and
`EngineCoreActor` as the primary inspection points.

## Scheduling and KV Cache

`Scheduler` initializes request maps, waiting/skipped/running queues, max running
request constraints, max scheduled token constraints, KV connector hooks,
encoder/multimodal cache managers, and finished request tracking
(`vllm@8357226:vllm/v1/core/sched/scheduler.py#Scheduler`). During scheduling,
KV-cache decisions flow through `KVCacheManager`, which exposes `KVCacheBlocks`
to hide block-group internals from scheduler code and performs prefix-cache
lookups in `get_computed_blocks`
(`vllm@8357226:vllm/v1/core/kv_cache_manager.py#KVCacheManager.get_computed_blocks`).

## Offline Inference

Offline Python users instantiate `vllm.LLM`, which is exported from
`vllm/__init__.py` and implemented in `vllm/entrypoints/llm.py#LLM`. The class
documents model/tokenizer selection, tensor parallel size, dtype, quantization,
GPU memory utilization, KV cache memory sizing, offload options, eager/CUDA graph
behavior, multimodal options, compilation config, attention config, and
speculative decoding aliases
(`vllm@8357226:vllm/entrypoints/llm.py#LLM`).

## Attention Backend Execution

Worker/model-runner code selects and invokes attention backends under
`vllm/v1/attention/`. Backends include FlashAttention, FlashInfer, Triton,
ROCm/AITER, CPU, FlexAttention, Mamba, and linear-attention variants
(`vllm@8357226:vllm/v1/attention/backends/flash_attn.py`,
`vllm@8357226:vllm/v1/attention/backends/flashinfer.py`,
`vllm@8357226:vllm/v1/attention/ops/paged_attn.py`).
