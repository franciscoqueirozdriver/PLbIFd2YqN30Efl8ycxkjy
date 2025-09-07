from typing import Literal

from ._sheets import get_rows

Acao = Literal["visualizar", "editar", "excluir", "exportar"]


def tem_permissao(tipo: str, rota: str, acao: Acao) -> bool:
    perms = get_rows("Permissoes")
    for p in perms["rows"]:
        tipo_ok = p.get("tipo") in {"*", tipo}
        rota_ok = p.get("rota") in {"*", rota}
        if tipo_ok and rota_ok:
            flag = str(p.get(acao, "")).lower()
            if flag in {"1", "true", "sim", "yes"}:
                return True
    return False
