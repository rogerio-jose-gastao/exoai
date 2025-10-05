import yaml
import os
from pathlib import Path

def generate_code(spec_file: str):
    base_dir = Path(__file__).resolve().parent.parent
    spec_path = base_dir / spec_file
    with open(spec_path, "r", encoding="utf-8") as f:
        spec = yaml.safe_load(f)

    out_dir = Path(__file__).resolve().parent
    out_dir.mkdir(exist_ok=True)

    for comp in spec.get("components", []):
        name = comp["name"]
        desc = comp.get("description", "Sem descrição")
        inputs = comp.get("input", [])
        output = comp.get("output", "None")

        # --- converte qualquer estrutura YAML em string de parâmetros ---
        params = []
        if isinstance(inputs, dict):
            for k, v in inputs.items():
                params.append(f"{k}: {v}")
        elif isinstance(inputs, list):
            for inp in inputs:
                if isinstance(inp, dict):
                    for k, v in inp.items():
                        params.append(f"{k}: {v}")
                elif isinstance(inp, (list, tuple)) and len(inp) == 2:
                    params.append(f"{inp[0]}: {inp[1]}")
                elif isinstance(inp, str):
                    params.append(inp)
        elif isinstance(inputs, str) and inputs.lower() != "none":
            params.append(inputs)

        param_str = ", ".join(params)
        if param_str:
            param_str = ", " + param_str

        class_name = "".join(x.capitalize() for x in name.split("_"))
        method_name = name.replace("_", "")

        code = f'''"""
Componente gerado automaticamente via Spec-Driven Development.
Descrição: {desc}
"""

class {class_name}:
    def __init__(self):
        pass

    def {method_name}(self{param_str}):
        """
        Output esperado: {output}
        """
        # TODO: implementar lógica real
        pass
'''
        with open(out_dir / f"{name}.py", "w", encoding="utf-8") as f:
            f.write(code)

    print(f"✅ Código gerado para {len(spec['components'])} componentes.")


if __name__ == "__main__":
    generate_code("exoai_specs.yaml")
