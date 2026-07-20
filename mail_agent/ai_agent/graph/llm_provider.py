"""
Thin wrapper so nodes don't call the Qwen client directly — swapping
models/providers later is a one-file change.
"""
from ai_agent.logics.qwen_llm_call import generate as _qwen_generate
 

def call_llm(prompt: str, system_prompt: str | None = None) -> str:
    return _qwen_generate(prompt, system_prompt=system_prompt)