from enum import Enum


class ModelRoute(str, Enum):
  """
  Represents the type of AI capability Alfred needs.

  These routes describe capabilities, not specific providers
  or model names.
  """

  CHAT = "chat"
  REASONING = "reasoning"
  VISION = "vision"
  WEB = "web"
  EMBEDDING = "embedding"
  VIDEO = "video"
  STT = "stt"
  TTS = "tts"