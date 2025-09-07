from flask import Flask, request

from ._utils import ok, json_error, parse_bool, parse_float
from ._sheets import get_rows
from ._rbac import tem_permissao

app = Flask(__name__)


def _user_type() -> str:
    return request.headers.get("X-User-Type", "admin")


@app.route("/", methods=["OPTIONS"])
def options_root():
    return ok()


@app.get("/")
def dashboard():
    if not tem_permissao(_user_type(), "dashboard", "visualizar"):
        return json_error(403, "FORBIDDEN", "Sem permissão")
    indicadores = get_rows("Indicadores", limit=1000000)["rows"]
    indicacoes = get_rows("Indicacoes", limit=1000000)["rows"]
    indicadores = [r for r in indicadores if r.get("status") == "active"]
    indicacoes = [r for r in indicacoes if r.get("status") == "active"]
    data_ini = request.args.get("data_ini")
    data_fim = request.args.get("data_fim")
    if data_ini:
        indicacoes = [r for r in indicacoes if r.get("data_indicacao") >= data_ini]
    if data_fim:
        indicacoes = [r for r in indicacoes if r.get("data_indicacao") <= data_fim]
    total_vendas = sum(1 for r in indicacoes if parse_bool(r.get("gerou_venda")))
    faturamento = sum(parse_float(r.get("faturamento_gerado")) for r in indicacoes)
    data = {
        "total_indicadores": len(indicadores),
        "total_indicacoes": len(indicacoes),
        "total_indicacoes_com_venda": total_vendas,
        "faturamento_total": faturamento,
    }
    return ok(data=data)
