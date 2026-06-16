import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(Path.cwd() / ".env")


def _env(key: str, default: str = None) -> str:
    val = os.environ.get(key, default)
    if val is None:
        raise RuntimeError(f"Missing required environment variable: {key}")
    return val


class Config:
    @property
    def AI_GATEWAY_URL(self):
        return os.environ.get("AI_FLOW_AI_GATEWAY_URL")

    @property
    def AI_GATEWAY_TOKEN(self):
        return os.environ.get("AI_FLOW_AI_GATEWAY_TOKEN")

    @property
    def ANTHROPIC_API_KEY(self):
        return os.environ.get("ANTHROPIC_API_KEY")

    @property
    def GITHUB_TOKEN(self):
        return os.environ.get("GITHUB_TOKEN")

    @property
    def GITHUB_REPOSITORY(self):
        return os.environ.get("GITHUB_REPOSITORY")

    @property
    def DB_PATH(self):
        return os.environ.get("HEAPIFY_DB_PATH", "heapify.db")


config = Config()
