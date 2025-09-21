import os
import json
import time
import asyncio
from typing import Any, List, Optional

from google import genai
from google.genai import types


GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY", "")


class GeminiService:
    def __init__(self) -> None:
        if not GEMINI_API_KEY:
            raise RuntimeError("GEMINI_API_KEY is not set in the environment")
        self._client = genai.Client(api_key=GEMINI_API_KEY)

    @property
    def client(self) -> genai.Client:
        return self._client


async_client = genai.Client(api_key=GEMINI_API_KEY)


async def async_gemini_generate_content(
    model: str = "gemini-2.5-flash",
    contents: Optional[List[types.Content]] = None,
    system_prompt: str = "",
    response_schema: Optional[types.Schema] = None,
    temperature: float = 0.4,
    top_p: float = 0.8,
    top_k: int = 40,
    max_output_tokens: int = 1000,
    timeout: int = 15,
    default_response: Any = None,
) -> Any:
    start_time = time.time()
    try:
        generate_content_config = types.GenerateContentConfig(
            temperature=temperature,
            top_p=top_p,
            top_k=top_k,
            max_output_tokens=max_output_tokens,
            response_mime_type="application/json" if response_schema else None,
            response_schema=response_schema,
            system_instruction=[types.Part.from_text(text=system_prompt)]
            if system_prompt
            else None,
            # thinking_config=types.ThinkingConfig(thinking_budget=0),
        )

        response_task = asyncio.create_task(
            async_client.aio.models.generate_content(
                model=model, contents=contents or [], config=generate_content_config
            )
        )

        try:
            response = await asyncio.wait_for(response_task, timeout=timeout)
        except asyncio.TimeoutError as e:
            response_task.cancel()
            print(f"Timeout error generating content: {e}")
            return default_response

        if response:
            if response_schema:
                try:
                    if response.text:
                        return json.loads(response.text)
                    else:
                        return default_response
                except json.JSONDecodeError as e:
                    print(f"JSON decode error generating content: {e}")
                    return default_response
            else:
                if response.text:
                    return response.text
                else:
                    return default_response
        else:
            print(f"No response generating content: {response}")
            return default_response

    except Exception as e:
        print(f"Error generating content: {e}")
        return default_response
    finally:
        _ = time.time() - start_time


async def async_generate_image_files(
    prompts: List[str], output_dir: str, base_file_name: str
) -> List[str]:
    os.makedirs(output_dir, exist_ok=True)

    model = "gemini-2.5-flash-image-preview"

    contents_list: List[List[types.Content]] = []
    for prompt in prompts:
        contents_list.append(
            [
                types.Content(
                    role="user",
                    parts=[types.Part.from_text(text=prompt)],
                )
            ]
        )

    async def _gen_for_index(index: int, contents: List[types.Content]) -> Optional[str]:
        generate_content_config = types.GenerateContentConfig(
            response_modalities=["IMAGE", "TEXT"],
        )

        file_name_prefix = f"{base_file_name}_{index}"
        file_path_result: Optional[str] = None

        try:
            response = await async_client.aio.models.generate_content(
                model=model, contents=contents, config=generate_content_config
            )

            if response and response.candidates:
                candidate = response.candidates[0]
                if candidate.content and candidate.content.parts:
                    for part_index, part in enumerate(candidate.content.parts):
                        if getattr(part, "inline_data", None) and getattr(part.inline_data, "data", None):
                            data_buffer = part.inline_data.data
                            mime_type = part.inline_data.mime_type
                            import mimetypes

                            file_extension = mimetypes.guess_extension(mime_type) or ".bin"
                            file_path = os.path.join(
                                output_dir, f"{file_name_prefix}_{part_index}{file_extension}"
                            )
                            with open(file_path, "wb") as f:
                                f.write(data_buffer)
                            file_path_result = file_path
                            break  # Take only the first image
        except Exception:
            return None
        return file_path_result

    tasks = [
        _gen_for_index(i, contents) for i, contents in enumerate(contents_list)
    ]
    results = await asyncio.gather(*tasks, return_exceptions=False)
    # Filter out Nones
    return [r for r in results if r]


