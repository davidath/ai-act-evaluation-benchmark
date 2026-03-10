from typing import Optional
import subprocess
import shlex
import os


def set_feature_if_exists(config: dict, obj, key: str,
                          default: Optional[float] = None) -> None:
    value = config.get(key, default)
    setattr(obj, key, value)


def gpt_oss_extract_final(text: str) -> str:
    start_marker = "<|message|>"
    end_marker = "<|return|>"
    last_message_start = text.rfind(start_marker) + len(start_marker)
    end_index = text.find(end_marker, last_message_start)
    extracted_text = text[last_message_start:end_index].strip()
    return extracted_text


class LlammaCppGPTOSSTextGenerator:
    def __init__(self, config: dict) -> None:
        self.lcpp_run_path: str = config.get('run_path')
        self.model_path: str = config.get('model_path')

        if not self.model_path or not self.model_path.endswith(".gguf"):
            raise ValueError(
                "Model path must end with '.gguf' and cannot be empty")

        if not self.lcpp_run_path:
            raise ValueError("Run path cannot be empty")

        self.temp: float = 0.15
        self.ctx_size: int = 8192

        set_feature_if_exists(config, self, 'temp', self.temp)
        set_feature_if_exists(config, self, 'ctx_size', self.ctx_size)

    def generate(self, prompt: str) -> str:
        # Sanitize the prompt to prevent command injection
        sanitized_prompt = shlex.quote(prompt)

        cmd = [
            os.path.join(self.lcpp_run_path, 'llama-run'),
            '--temp', str(self.temp),
            '-c', str(self.ctx_size),
            self.model_path
        ]

        try:
            result = subprocess.run(
                cmd,
                input=sanitized_prompt,
                capture_output=True,
                text=True,
                check=True
            )
        except subprocess.CalledProcessError as e:
            raise RuntimeError(f"Error running llama-run: {e.stderr}")
        except FileNotFoundError:
            raise FileNotFoundError("The specified executable was not found.")
        except PermissionError:
            raise PermissionError("Permission denied to execute the command.")
        except Exception as e:
            raise RuntimeError(f"An unexpected error occurred: {str(e)}")

        return gpt_oss_extract_final(result.stdout.strip())
