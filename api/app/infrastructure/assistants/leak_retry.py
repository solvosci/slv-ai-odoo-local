import logging
import re

logger = logging.getLogger(__name__)

THINK = re.compile(r"<think>.*?</think>", re.DOTALL)
LEAK_MARKERS = ("minimax[>[", "<tool_call>", "</tool_call>", "<invoke")
MAX_ATTEMPTS = 3


def has_leak(result) -> bool:
    message = result.generations[0].message
    if message.tool_calls:
        return False
    return any(marker in message.text for marker in LEAK_MARKERS)


def log_if_empty(result):
    message = result.generations[0].message
    if not message.tool_calls and not THINK.sub("", message.text).strip():
        logger.warning("MiniMax empty reply: content=%r metadata=%r",
                       message.content, message.response_metadata)


def generate_without_leak(generate, *args, **kwargs):
    for _ in range(MAX_ATTEMPTS):
        result = generate(*args, **kwargs)
        if not has_leak(result):
            break
    log_if_empty(result)
    return result


async def agenerate_without_leak(generate, *args, **kwargs):
    for _ in range(MAX_ATTEMPTS):
        result = await generate(*args, **kwargs)
        if not has_leak(result):
            break
    log_if_empty(result)
    return result
