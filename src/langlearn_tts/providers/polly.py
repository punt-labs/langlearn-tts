"""AWS Polly TTS provider."""

from __future__ import annotations

import logging
from dataclasses import dataclass
from pathlib import Path
from typing import TYPE_CHECKING, Any, cast

import boto3

from langlearn_tts.types import HealthCheck, SynthesisRequest, SynthesisResult

if TYPE_CHECKING:
    from mypy_boto3_polly.client import PollyClient as PollyClientType
    from mypy_boto3_polly.literals import (
        EngineType,
        LanguageCodeType,
        VoiceIdType,
    )

logger = logging.getLogger(__name__)

__all__ = ["PollyProvider"]

# Engine preference order: best quality first.
_ENGINE_PREFERENCE: list[str] = ["neural", "generative", "long-form", "standard"]


@dataclass(frozen=True)
class VoiceConfig:
    """Maps a Polly voice to its API parameters.

    Each VoiceConfig bundles a Polly voice ID with its required language
    code and engine type, eliminating the need for callers to know these
    implementation details.
    """

    voice_id: VoiceIdType
    language_code: LanguageCodeType
    engine: EngineType


# Cache of resolved voices, keyed by lowercase name.
# Pre-populated entries act as aliases and are never overwritten.
VOICES: dict[str, VoiceConfig] = {}

# Whether the full voice list has been fetched from the API.
_voices_loaded: bool = False


def _best_engine(supported: list[str]) -> EngineType:
    """Pick the best engine from a list of supported engines."""
    if not supported:
        msg = "Voice has no supported engines"
        raise ValueError(msg)
    for engine in _ENGINE_PREFERENCE:
        if engine in supported:
            return engine  # type: ignore[return-value]
    return supported[0]  # type: ignore[return-value]


def _load_voices_from_api(client: Any) -> None:  # pyright: ignore[reportExplicitAny]
    """Fetch all voices from the Polly API and populate the cache.

    Paginates through all pages of the describe_voices response.
    """
    global _voices_loaded
    if _voices_loaded:
        return

    next_token: str | None = None

    while True:
        kwargs: dict[str, str] = {}
        if next_token is not None:
            kwargs["NextToken"] = next_token

        resp: dict[str, Any] = client.describe_voices(**kwargs)

        for voice in resp["Voices"]:
            key = voice["Id"].lower()
            if key not in VOICES:
                VOICES[key] = VoiceConfig(
                    voice_id=voice["Id"],
                    language_code=voice["LanguageCode"],
                    engine=_best_engine(voice["SupportedEngines"]),
                )

        next_token = resp.get("NextToken")
        if not next_token:
            break

    _voices_loaded = True
    logger.debug("Loaded %d voices from Polly API", len(VOICES))


class PollyProvider:
    """AWS Polly TTS provider.

    Implements the TTSProvider protocol by wrapping boto3 Polly calls.
    Accepts an optional pre-configured boto3 Polly client for
    dependency injection in tests.
    """

    def __init__(self, boto_client: PollyClientType | None = None) -> None:
        if TYPE_CHECKING:
            self._client: PollyClientType
        if boto_client is not None:
            self._client = boto_client
        else:
            self._client = cast("PollyClientType", boto3.client("polly"))  # type: ignore[redundant-cast]  # pyright: ignore[reportUnknownMemberType]

    @property
    def name(self) -> str:
        return "polly"

    @property
    def default_voice(self) -> str:
        return "joanna"

    def synthesize(
        self, request: SynthesisRequest, output_path: Path
    ) -> SynthesisResult:
        """Synthesize text to an MP3 file using AWS Polly.

        Resolves the voice name to Polly parameters internally, wraps
        the text in SSML with prosody rate, and writes the MP3 output.
        """
        voice_cfg = self._resolve_voice_config(request.voice)
        ssml_text = (
            f'<speak><prosody rate="{request.rate}%">{request.text}</prosody></speak>'
        )
        logger.debug(
            "Synthesizing: voice=%s, text=%r",
            voice_cfg.voice_id,
            request.text,
        )

        response = self._client.synthesize_speech(
            Text=ssml_text,
            TextType="ssml",
            VoiceId=voice_cfg.voice_id,
            LanguageCode=voice_cfg.language_code,
            OutputFormat="mp3",
            Engine=voice_cfg.engine,
            SampleRate="22050",
        )

        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, "wb") as f:
            f.write(response["AudioStream"].read())

        logger.info("Wrote %s", output_path)
        return SynthesisResult(
            file_path=output_path,
            text=request.text,
            voice_name=voice_cfg.voice_id,
        )

    def resolve_voice(self, name: str) -> str:
        """Validate and resolve a voice name to its canonical form.

        Returns the Polly voice ID (e.g. "Joanna") if the name is valid.
        """
        cfg = self._resolve_voice_config(name)
        return cfg.voice_id

    def check_health(self) -> list[HealthCheck]:
        """Check AWS credentials and Polly API access."""
        from botocore.exceptions import (
            ClientError,
            EndpointConnectionError,
            NoCredentialsError,
            NoRegionError,
        )

        checks: list[HealthCheck] = []

        def _ok(msg: str) -> HealthCheck:
            return HealthCheck(passed=True, message=msg)

        def _fail(msg: str) -> HealthCheck:
            return HealthCheck(passed=False, message=msg)

        # AWS credentials (STS)
        try:
            sts: Any = boto3.client("sts")  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            identity: Any = sts.get_caller_identity()  # pyright: ignore[reportUnknownMemberType, reportUnknownVariableType]
            account: str = identity["Account"]  # pyright: ignore[reportUnknownVariableType]
            checks.append(_ok(f"AWS credentials (account: {account})"))
        except NoCredentialsError:
            checks.append(
                _fail("AWS credentials: not configured (run `aws configure`)")
            )
        except NoRegionError:
            checks.append(_fail("AWS credentials: no region set (run `aws configure`)"))
        except EndpointConnectionError:
            checks.append(_fail("AWS credentials: cannot reach AWS (check network)"))
        except ClientError as e:
            checks.append(_fail(f"AWS credentials: {e}"))

        # AWS Polly access
        try:
            polly: Any = boto3.client("polly")  # pyright: ignore[reportUnknownMemberType]
            polly.describe_voices()
            checks.append(_ok("AWS Polly access"))
        except (NoCredentialsError, NoRegionError):
            checks.append(_fail("AWS Polly access: skipped (no credentials)"))
        except EndpointConnectionError:
            checks.append(_fail("AWS Polly access: cannot reach AWS (check network)"))
        except ClientError as e:
            checks.append(_fail(f"AWS Polly access: {e}"))

        return checks

    def _resolve_voice_config(self, name: str) -> VoiceConfig:
        """Resolve a voice name to its full VoiceConfig.

        Checks the local cache first, then queries the Polly API.
        """
        key = name.lower()
        if key in VOICES:
            return VOICES[key]

        _load_voices_from_api(self._client)

        if key in VOICES:
            return VOICES[key]

        available = ", ".join(sorted(VOICES))
        raise ValueError(f"Unknown voice '{name}'. Available: {available}")
