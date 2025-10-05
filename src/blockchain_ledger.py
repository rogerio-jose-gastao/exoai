import json
import hashlib
import os
from datetime import datetime
from typing import List, Dict, Any

LEDGER_FILE = "ledger.json"


def _calculate_hash(block: Dict[str, Any]) -> str:
    """Calcula o hash SHA-256 de um bloco."""
    block_string = json.dumps(block, sort_keys=True).encode()
    return hashlib.sha256(block_string).hexdigest()


def _load_ledger() -> List[Dict[str, Any]]:
    """Carrega o ledger existente ou cria um novo."""
    if not os.path.exists(LEDGER_FILE):
        with open(LEDGER_FILE, "w") as f:
            json.dump([], f)
    with open(LEDGER_FILE, "r") as f:
        return json.load(f)


def _save_ledger(ledger: List[Dict[str, Any]]):
    """Salva o ledger atualizado."""
    with open(LEDGER_FILE, "w") as f:
        json.dump(ledger, f, indent=2)


def add_entry(candidate_id: str, probability: float, detection_hash: str) -> Dict[str, Any]:
    """Adiciona uma nova entrada ao ledger."""
    ledger = _load_ledger()

    previous_hash = ledger[-1]["hash"] if ledger else "GENESIS"
    new_block = {
        "index": len(ledger) + 1,
        "timestamp": datetime.utcnow().isoformat(),
        "candidate_id": candidate_id,
        "probability": probability,
        "detection_hash": detection_hash,
        "previous_hash": previous_hash
    }

    new_block["hash"] = _calculate_hash(new_block)
    ledger.append(new_block)
    _save_ledger(ledger)

    print(f"✅ Ledger updated: block #{new_block['index']} with hash {new_block['hash'][:12]}...")
    return new_block


def list_entries(limit: int = 10) -> List[Dict[str, Any]]:
    """Lista as últimas entradas do ledger."""
    ledger = _load_ledger()
    return ledger[-limit:]


def verify_integrity() -> bool:
    """Verifica se o ledger é íntegro."""
    ledger = _load_ledger()
    for i in range(1, len(ledger)):
        if ledger[i]["previous_hash"] != ledger[i - 1]["hash"]:
            print(f"⚠️ Ledger corrupted at block {i + 1}")
            return False
        recalculated = _calculate_hash({k: v for k, v in ledger[i].items() if k != "hash"})
        if recalculated != ledger[i]["hash"]:
            print(f"⚠️ Hash mismatch at block {i + 1}")
            return False
    print("✅ Ledger integrity verified.")
    return True


if __name__ == "__main__":
    print("📘 Blockchain ledger utility")
    print("Last 5 entries:", list_entries(5))
    verify_integrity()
