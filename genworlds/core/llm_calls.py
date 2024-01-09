from typing import Optional
import os
import re
import asyncio

import aiohttp
import json

from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI()


async def process_streaming_buffer(buffer: str, chunk: str, regex: str) -> str:
    updated_buffer = buffer + chunk
    if regex:
        match = re.search(regex, updated_buffer)
        if match:
            full_match = match.group(0)
            return {'stop': True, 'match': full_match}
    return {'stop': False, 'match': None}

async def call_openai(model_name:str, prompt:str, regex: Optional[str], return_streaming_channel:Optional[asyncio.Queue]) -> str:
    stream = client.chat.completions.create(
        model=model_name,
        messages=[{"role": "user", "content": prompt}],
        stream=True,
    )

    buffer = ""
    for chunk in stream:
        chunk_str = chunk.choices[0].delta.content
        if chunk_str is not None:
            if return_streaming_channel is not None:
                await return_streaming_channel.put(chunk_str)
                continue
            result = await process_streaming_buffer(buffer, chunk_str, regex)
            buffer += chunk_str
            if result['stop']:
                return result['match']
            else:
                if return_streaming_channel is not None:
                    await return_streaming_channel.put({'done': True})
                if 'done' in chunk_str:
                    return buffer
        else:
            return buffer
