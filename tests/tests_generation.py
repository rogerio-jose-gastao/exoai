import sys
from pathlib import Path

# Garante que a pasta src/ está no caminho de importação
sys.path.append(str(Path(__file__).resolve().parent.parent / "src"))

from src.generate_code import generate_code

def test_generate_creates_files():
    # Executa a geração de código
    spec_file = Path(__file__).resolve().parent.parent / "exoai_specs.yaml"
    generate_code(spec_file.name)

    # Verifica se os arquivos dos componentes foram criados
    for name in ["data_collector", "ml_detector", "blockchain_ledger", "agent_orchestrator"]:
        path = Path(__file__).resolve().parent.parent / "src" / f"{name}.py"
        assert path.exists(), f"{path} não foi criado"
