---
repo: sglang
commit: b276a9acee8a02159a9a8d839da8a7b4dd898b58
source_version: b276a9a
document: key-flows.md
status: source-backed
---

# Key Flows

Source snapshot: `sglang` commit
`b276a9acee8a02159a9a8d839da8a7b4dd898b58`.

## CLI to Server Startup

1. The console script `sglang` maps to `sglang.cli.main:main`
   (`sglang@b276a9a:python/pyproject.toml`).
2. `python/sglang/cli/main.py` creates subcommands `serve`, `generate`, and
   `version`; `serve` dispatches to `sglang.cli.serve.serve`
   (`sglang@b276a9a:python/sglang/cli/main.py`).
3. The SRT HTTP server is implemented in
   `python/sglang/srt/entrypoints/http_server.py`, which wires FastAPI, runtime
   `Engine`, tokenizer manager initialization, scheduler and detokenizer process
   runners, serving adapters, request schemas, and server args
   (`sglang@b276a9a:python/sglang/srt/entrypoints/http_server.py`).

## HTTP Request to Runtime Managers

The server imports request input structs such as `GenerateReqInput`,
`EmbeddingReqInput`, `TokenizeRequest`, LoRA load/unload requests, profiling
requests, weight update requests, session open/close requests, and memory
release/resume requests from `managers/io_struct.py`
(`sglang@b276a9a:python/sglang/srt/entrypoints/http_server.py`,
`sglang@b276a9a:python/sglang/srt/managers/io_struct.py`). Requests are routed
through tokenizer/template managers before scheduler/model execution.

## Scheduling and Execution

`Scheduler` receives runtime requests and coordinates batching, policy,
constrained decoding, disaggregation, LoRA, memory/cache state, metrics, and
model execution (`sglang@b276a9a:python/sglang/srt/managers/scheduler.py#Scheduler`).
`ScheduleBatch` is the batch container used for runtime execution, and
`ModelRunner` is the primary model execution class
(`sglang@b276a9a:python/sglang/srt/managers/schedule_batch.py#ScheduleBatch`,
`sglang@b276a9a:python/sglang/srt/model_executor/model_runner.py#ModelRunner`).

## Prefix/KV Cache Flow

`RadixCache` is the main Python radix prefix-cache class, while `RadixCacheCpp`
is the C++-backed variant. Related cache implementations include chunk cache,
SWA radix cache, Mamba radix cache, unified radix cache, HiCache storage, and
memory pools under `python/sglang/srt/mem_cache/`
(`sglang@b276a9a:python/sglang/srt/mem_cache/radix_cache.py#RadixCache`,
`sglang@b276a9a:python/sglang/srt/mem_cache/radix_cache_cpp.py#RadixCacheCpp`).

## Structured Generation and Tool Calling

Frontend structured generation starts at public functions exported from
`python/sglang/__init__.py`, including `function`, `gen`, `select`, role helpers,
and backend selection. Runtime constrained decoding is handled under
`python/sglang/srt/constrained/`, with grammar backends for xgrammar,
llguidance, outlines, and reasoner grammar. Function/tool call parsing is under
`python/sglang/srt/function_call/`
(`sglang@b276a9a:python/sglang/__init__.py`,
`sglang@b276a9a:python/sglang/srt/constrained/grammar_manager.py`,
`sglang@b276a9a:python/sglang/srt/function_call/function_call_parser.py`).

## Native Kernel Flow

SRT layers can call into packaged kernel ops from `sgl-kernel`. The kernel
package exposes C++/CUDA/ROCm/MUSA/Metal sources under `sgl-kernel/csrc/`,
headers under `sgl-kernel/include/`, Python bindings under
`sgl-kernel/python/sgl_kernel`, and coverage under `sgl-kernel/tests/`
(`sglang@b276a9a:sgl-kernel/csrc/`, `sglang@b276a9a:sgl-kernel/include/`).
