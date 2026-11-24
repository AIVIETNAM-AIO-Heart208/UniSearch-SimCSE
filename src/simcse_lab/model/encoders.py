"""Frozen PhoBERT SimCSE encoder used for D1."""

from functools import lru_cache
from hashlib import sha256

from simcse_lab.retrieval.preprocess import segment

MODEL_ID = "VoVanPhuc/sup-SimCSE-VietNamese-phobert-base"
REVISION = "608779b86741a8acd8c8d38132974ff04086b138"
MAX_LENGTH = 256
SNAPSHOT_HASHES = {
    "model.safetensors": "2559811f500b42fa23b8fe313d94a9503299aff1f0e0f58fdd4824571cb4423c",
    "config.json": "4bc82a39c36f328f3fbcbfd83c26d00621b396ac7e9ff1a38cfa7c70d88fa608",
    "vocab.txt": "dffd7543c401fb6567253ae7c3313004532c33d062525250049c616544bad777",
    "bpe.codes": "9dfe53fb8abbddd3387da99641c36e00bee757a3679aad9cf0a7cdc4b30f6ef8",
    "tokenizer_config.json": "f80601760ebdd7737e988a60bb3c14bca12a6786c06e84c99bd2f3329ad80fa0",
    "special_tokens_map.json": "7638f5bbbe86ef6d604ef28ad3647dc690d6d117c81c0d63e885416be8da1150",
    "added_tokens.json": "895678a80ea84920b4240c0616a1b0b086368c7ca3cbacb80996a2b30b4f2b67",
}


def verify_snapshot(model_path):
    for name, expected in SNAPSHOT_HASHES.items():
        digest = sha256()
        with (model_path / name).open("rb") as stream:
            for block in iter(lambda: stream.read(1024 * 1024), b""):
                digest.update(block)
        if digest.hexdigest() != expected:
            raise ValueError(f"{name} does not match {MODEL_ID} revision {REVISION}")
    return dict(SNAPSHOT_HASHES)


class SimCSEEncoder:
    def __init__(self, model_path, device):
        import torch
        from transformers import AutoModel, AutoTokenizer

        self.torch = torch
        self.device = torch.device(device)
        self.tokenizer = AutoTokenizer.from_pretrained(model_path, local_files_only=True)
        self.model = AutoModel.from_pretrained(
            model_path, local_files_only=True, use_safetensors=True
        ).to(self.device).eval()
        self.token_ids = lru_cache(maxsize=256)(self._token_ids)

    def _token_ids(self, text):
        return self.tokenizer.encode(segment(text), add_special_tokens=True, verbose=False)

    def count_tokens(self, text):
        return len(self.token_ids(text))

    def encode(self, texts, batch_size):
        torch = self.torch
        vectors = []
        with torch.inference_mode():
            for start in range(0, len(texts), batch_size):
                token_ids = [self.token_ids(text) for text in texts[start:start + batch_size]]
                if max(map(len, token_ids)) > MAX_LENGTH:
                    raise ValueError(f"Encoder input exceeds {MAX_LENGTH} tokens in batch at {start}")
                inputs = self.tokenizer.pad({"input_ids": token_ids}, padding=True, return_tensors="pt")
                pooled = self.model(**inputs.to(self.device)).pooler_output.float()
                norms = torch.linalg.vector_norm(pooled, dim=-1, keepdim=True)
                if not torch.isfinite(norms).all() or (norms == 0).any():
                    raise ValueError("Encoder produced an invalid embedding")
                vectors.append((pooled / norms).cpu().numpy())
        import numpy as np

        return np.concatenate(vectors)
