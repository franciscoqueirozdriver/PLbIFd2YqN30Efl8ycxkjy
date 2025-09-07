from typing import Any, Dict

from ._sheets import get_rows
from ._utils import (
    ensure_required,
    normalize_phone_e164,
    parse_bool,
    parse_float,
)

VALID_STATUS = {"Nao", "EmProcessamento", "Sim"}


def validate_indicador_create(data: Dict[str, Any]) -> Dict[str, Any]:
    ensure_required(data, ["nome", "telefone"])
    data["telefone"] = normalize_phone_e164(data["telefone"])
    existing = get_rows("Indicadores", filters={"telefone": data["telefone"]}, limit=1)["rows"]
    if existing:
        raise ValueError("Telefone já cadastrado")
    return data


def validate_indicador_update(indicador_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
    if "telefone" in data:
        phone = normalize_phone_e164(data["telefone"])
        existing = get_rows("Indicadores", filters={"telefone": phone}, limit=1)["rows"]
        if existing and existing[0].get("indicador_id") != indicador_id:
            raise ValueError("Telefone já cadastrado")
        data["telefone"] = phone
    return data


def validate_indicacao_create(data: Dict[str, Any]) -> Dict[str, Any]:
    ensure_required(data, ["indicador_id", "data_indicacao", "nome_indicado", "telefone_indicado"])
    data["telefone_indicado"] = normalize_phone_e164(data["telefone_indicado"])
    data["gerou_venda"] = parse_bool(data.get("gerou_venda", False))
    data["faturamento_gerado"] = parse_float(data.get("faturamento_gerado", 0))
    status = data.get("status_recompensa", "Nao")
    if status not in VALID_STATUS:
        raise ValueError("status_recompensa inválido")
    if data["gerou_venda"] and data["faturamento_gerado"] <= 0:
        raise ValueError("faturamento_gerado inválido")
    if data["gerou_venda"] and status == "Nao":
        status = "EmProcessamento"
    data["status_recompensa"] = status
    return data


def validate_indicacao_update(existing: Dict[str, Any], data: Dict[str, Any]) -> Dict[str, Any]:
    if "telefone_indicado" in data:
        data["telefone_indicado"] = normalize_phone_e164(data["telefone_indicado"])
    gerou_venda = parse_bool(data.get("gerou_venda", existing.get("gerou_venda")))
    data["gerou_venda"] = gerou_venda
    if "faturamento_gerado" in data:
        data["faturamento_gerado"] = parse_float(data["faturamento_gerado"], existing.get("faturamento_gerado", 0))
    status = data.get("status_recompensa", existing.get("status_recompensa", "Nao"))
    if status not in VALID_STATUS:
        raise ValueError("status_recompensa inválido")
    if existing.get("status_recompensa") == "Sim" and status != "Sim":
        raise ValueError("status_recompensa não pode regredir")
    if gerou_venda and data.get("faturamento_gerado", existing.get("faturamento_gerado", 0)) <= 0:
        raise ValueError("faturamento_gerado inválido")
    if gerou_venda and status == "Nao":
        status = "EmProcessamento"
    data["status_recompensa"] = status
    return data
