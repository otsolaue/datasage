from enum import Enum
from typing import Any

from pydantic import BaseModel


class StageType(str, Enum):
    INGEST = "ingest"
    CLEAN = "clean"
    EXTRACT = "extract"
    ANALYZE = "analyze"
    EXPORT = "export"


STAGE_LABELS = {
    StageType.INGEST:  "1. Ingest",
    StageType.CLEAN:   "2. Clean",
    StageType.EXTRACT: "3. Extract",
    StageType.ANALYZE: "4. Analyze",
    StageType.EXPORT:  "5. Export",
}

STAGE_DESCRIPTIONS = {
    StageType.INGEST:  "Load raw text from files, URLs, or paste directly.",
    StageType.CLEAN:   "Remove noise, normalize formatting, filter irrelevant content.",
    StageType.EXTRACT: "Pull structured information from unstructured text using LLM prompts.",
    StageType.ANALYZE: "Summarize, classify, or compare extracted content.",
    StageType.EXPORT:  "Save results as CSV, JSON, or plain text.",
}


class StageResult(BaseModel):
    stage: StageType
    input_text: str
    output_text: str
    metadata: dict[str, Any] = {}
