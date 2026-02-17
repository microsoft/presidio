"""Custom recognizers for GLiNER edge parity profile."""

from __future__ import annotations

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from presidio_analyzer.analysis_explanation import AnalysisExplanation
from presidio_analyzer.local_recognizer import LocalRecognizer
from presidio_analyzer.nlp_engine import NlpArtifacts
from presidio_analyzer.predefined_recognizers.country_specific.us.us_ssn_recognizer import (
    UsSsnRecognizer,
)
from presidio_analyzer.predefined_recognizers.ner.gliner_recognizer import GLiNERRecognizer
from presidio_analyzer.recognizer_result import RecognizerResult

try:
    from gliner import GLiNER
except ImportError:
    GLiNER = None


class EdgeONNXGLiNERRecognizer(GLiNERRecognizer):
    """GLiNER recognizer loading ONNX artifacts from Hugging Face snapshots."""

    REQUIRED_MODEL_FILES = [
        "gliner_config.json",
        "tokenizer.json",
        "tokenizer_config.json",
        "special_tokens_map.json",
    ]

    _MODEL_CACHE: Dict[Tuple[str, str, str], object] = {}

    def __init__(
        self,
        *args,
        onnx_model_file: str = "onnx/model.onnx",
        target_entities: Optional[List[str]] = None,
        **kwargs,
    ):
        self.onnx_model_file = onnx_model_file
        self.target_entities = target_entities or []
        super().__init__(*args, **kwargs)

    @staticmethod
    def _materialize_file(src: Path, dest: Path) -> None:
        dest.parent.mkdir(parents=True, exist_ok=True)
        try:
            if dest.exists() or dest.is_symlink():
                dest.unlink()
            os.symlink(src, dest)
        except OSError:
            shutil.copy2(src, dest)

    @classmethod
    def _cache_key(
        cls,
        model_name: str,
        onnx_model_file: str,
        map_location: Optional[str],
    ) -> Tuple[str, str, str]:
        return (model_name, onnx_model_file, str(map_location or "auto"))

    def load(self) -> None:
        if not GLiNER:
            raise ImportError("GLiNER is not installed. Please install it.")

        key = self._cache_key(self.model_name, self.onnx_model_file, self.map_location)
        cached = self._MODEL_CACHE.get(key)
        if cached is not None:
            self.gliner = cached
            return

        from huggingface_hub import snapshot_download

        allow_patterns = list(self.REQUIRED_MODEL_FILES)
        allow_patterns.append(self.onnx_model_file)

        snapshot_dir = Path(
            snapshot_download(
                repo_id=self.model_name,
                allow_patterns=allow_patterns,
            )
        )

        runtime_dir = Path(tempfile.mkdtemp(prefix="gliner_edge_runtime_"))

        for rel_file in self.REQUIRED_MODEL_FILES + [self.onnx_model_file]:
            src = snapshot_dir / rel_file
            if not src.exists():
                raise FileNotFoundError(f"Required model file missing: {src}")
            self._materialize_file(src, runtime_dir / rel_file)

        # Keep workaround isolated to runtime dir rather than mutating HF cache.
        (runtime_dir / "model.safetensors").touch(exist_ok=True)

        self.gliner = GLiNER.from_pretrained(
            str(runtime_dir),
            load_onnx_model=True,
            load_tokenizer=True,
            onnx_model_file=self.onnx_model_file,
            map_location=self.map_location,
        )

        self._MODEL_CACHE[key] = self.gliner

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: Optional[NlpArtifacts] = None,
    ) -> List[RecognizerResult]:
        """Analyze text with fixed configured labels to avoid ad-hoc label expansion."""

        predictions = self.gliner.predict_entities(
            text=text,
            labels=list(self.gliner_labels),
            flat_ner=self.flat_ner,
            threshold=self.threshold,
            multi_label=self.multi_label,
        )

        requested = set(entities or [])
        target = set(self.target_entities or [])

        results = []
        for pred in predictions:
            presidio_entity = self.model_to_presidio_entity_mapping.get(
                pred["label"], pred["label"]
            )

            if requested and presidio_entity not in requested:
                continue
            if target and presidio_entity not in target:
                continue

            results.append(
                RecognizerResult(
                    entity_type=presidio_entity,
                    start=pred["start"],
                    end=pred["end"],
                    score=pred["score"],
                    analysis_explanation=AnalysisExplanation(
                        recognizer=self.name,
                        original_score=pred["score"],
                        textual_explanation=f"Identified as {presidio_entity} by GLiNER",
                    ),
                )
            )

        return results


class ContextAwareUsSsnRecognizer(UsSsnRecognizer):
    """US SSN recognizer with optional low-score context gating."""

    def __init__(
        self,
        *args,
        min_score: float = 0.5,
        low_score_require_context: bool = True,
        context_terms: Optional[List[str]] = None,
        context_window_chars: int = 80,
        target_entities: Optional[List[str]] = None,
        **kwargs,
    ):
        super().__init__(*args, **kwargs)
        self.min_score = min_score
        self.low_score_require_context = low_score_require_context
        self.context_terms = [term.lower() for term in (context_terms or ["ssn", "social security"])]
        self.context_window_chars = context_window_chars
        self.target_entities = target_entities or []

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: Optional[NlpArtifacts] = None,
    ) -> List[RecognizerResult]:
        results = super().analyze(text, entities, nlp_artifacts)
        if not results:
            return []

        requested = set(entities or [])
        target = set(self.target_entities or [])

        filtered = []
        for result in results:
            if requested and result.entity_type not in requested:
                continue
            if target and result.entity_type not in target:
                continue

            if result.score >= self.min_score:
                filtered.append(result)
                continue

            left = max(0, result.start - self.context_window_chars)
            right = min(len(text), result.end + self.context_window_chars)
            context = text[left:right].lower()
            has_context = any(term in context for term in self.context_terms)

            if self.low_score_require_context and has_context:
                filtered.append(result)
            elif not self.low_score_require_context:
                filtered.append(result)

        return filtered


class GLiNERPartialCardRecognizer(LocalRecognizer):
    """Heuristic detector for partial card mentions using GLiNER ad-hoc labels."""

    def __init__(
        self,
        supported_language: str = "en",
        version: str = "0.0.1",
        context: Optional[List[str]] = None,
        model_name: str = "knowledgator/gliner-pii-edge-v1.0",
        onnx_model_file: str = "onnx/model.onnx",
        threshold: float = 0.25,
        flat_ner: bool = True,
        multi_label: bool = False,
        map_location: Optional[str] = "cpu",
        labels: Optional[List[str]] = None,
        required_context_terms: Optional[List[str]] = None,
        strong_context_terms: Optional[List[str]] = None,
        blocklist_terms: Optional[List[str]] = None,
        target_entities: Optional[List[str]] = None,
        name: str = "GLiNERPartialCardRecognizer",
        enabled: bool = True,
        **kwargs,
    ):
        self.model_name = model_name
        self.onnx_model_file = onnx_model_file
        self.threshold = threshold
        self.flat_ner = flat_ner
        self.multi_label = multi_label
        self.map_location = map_location
        self.target_entities = target_entities or []
        self.enabled = enabled
        self.gliner = None

        super().__init__(
            name=name,
            supported_language=supported_language,
            version=version,
            context=context,
            supported_entities=["CREDIT_CARD"],
        )
        self.labels = labels or [
            "partial credit card",
            "credit card ending digits",
            "last 4 digits",
        ]
        self.required_context_terms = [
            t.lower()
            for t in (
                required_context_terms
                or [
                    "credit",
                    "debit",
                    "payment",
                    "charge",
                    "charged",
                    "transaction",
                    "billing",
                    "statement",
                    "fraud",
                    "mastercard",
                    "amex",
                ]
            )
        ]
        self.strong_context_terms = [
            t.lower() for t in (strong_context_terms or self.required_context_terms)
        ]
        self.blocklist_terms = [
            t.lower()
            for t in (
                blocklist_terms
                or [
                    "invoice",
                    "order",
                    "ticket",
                    "reservation",
                    "account",
                    "pin",
                    "otp",
                    "year",
                    "code",
                    "passport",
                    "green card",
                    "travel visa",
                ]
            )
        ]

    @staticmethod
    def _extract_partial_credit_card_value(predicted_text: str) -> Optional[str]:
        normalized = " ".join(predicted_text.split())
        match = re.search(r"(\d{4})$", normalized)
        if match:
            return match.group(1)
        if re.fullmatch(r"(?:\*+\s*)?\d{4}", normalized):
            return re.sub(r"^\*+\s*", "", normalized)
        return None

    def load(self) -> None:
        if not self.enabled:
            return

        self.gliner = EdgeONNXGLiNERRecognizer._MODEL_CACHE.get(
            EdgeONNXGLiNERRecognizer._cache_key(
                self.model_name, self.onnx_model_file, self.map_location
            )
        )

        if self.gliner is not None:
            return

        # Warm-load via shared edge recognizer to reuse one code path/cache.
        loader = EdgeONNXGLiNERRecognizer(
            supported_language=self.supported_language,
            model_name=self.model_name,
            onnx_model_file=self.onnx_model_file,
            map_location=self.map_location,
            entity_mapping={"partial credit card": "CREDIT_CARD"},
            threshold=self.threshold,
            flat_ner=self.flat_ner,
            multi_label=self.multi_label,
            name=f"{self.name}Loader",
        )
        loader.load()
        self.gliner = loader.gliner

    def analyze(
        self,
        text: str,
        entities: List[str],
        nlp_artifacts: Optional[NlpArtifacts] = None,
    ) -> List[RecognizerResult]:
        if not self.enabled:
            return []
        if entities and "CREDIT_CARD" not in entities:
            return []
        if self.target_entities and "CREDIT_CARD" not in self.target_entities:
            return []

        text_lower = text.lower()
        has_last4_phrase = bool(
            re.search(
                r"(card\s+ending|ending\s+(?:in|with)\s+\d{4}|last\s+(?:4|four)\s+digits?.*card)",
                text_lower,
            )
        )
        has_required_context = any(term in text_lower for term in self.required_context_terms)
        if not has_required_context and not has_last4_phrase:
            return []

        has_blocked_context = any(term in text_lower for term in self.blocklist_terms)
        has_strong_context = any(term in text_lower for term in self.strong_context_terms)
        if has_blocked_context and not has_strong_context:
            return []

        predictions = self.gliner.predict_entities(
            text=text,
            labels=list(self.labels),
            threshold=self.threshold,
            flat_ner=self.flat_ner,
            multi_label=self.multi_label,
        )

        best = None
        for pred in predictions:
            value = self._extract_partial_credit_card_value(pred.get("text", ""))
            if value is None:
                continue
            if best is None or pred["score"] > best["score"]:
                best = {
                    "value": value,
                    "score": pred["score"],
                }

        if best is None:
            return []

        start = text.rfind(best["value"])
        end = start + len(best["value"])
        if start < 0:
            return []

        return [
            RecognizerResult(
                entity_type="CREDIT_CARD",
                start=start,
                end=end,
                score=best["score"],
                analysis_explanation=AnalysisExplanation(
                    recognizer=self.name,
                    original_score=best["score"],
                    textual_explanation="Identified as partial card number by GLiNER fallback",
                ),
            )
        ]
