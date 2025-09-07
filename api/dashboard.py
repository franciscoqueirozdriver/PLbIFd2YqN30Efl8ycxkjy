from flask import Flask, jsonify
from ._sheets import ws
from ._utils import ok, err
import traceback

app = Flask(__name__)

def _to_bool(value):
    return str(value).strip().upper() == 'TRUE'

def _to_float(value):
    try:
        # Remove R$, spaces, and use . as decimal separator
        s = str(value).replace("R$", "").strip().replace(".", "").replace(",", ".")
        return float(s)
    except (ValueError, TypeError):
        return 0.0

@app.get("/")
def get_dashboard_stats():
    try:
        indicacoes_records = ws("Indicacoes").get_all_records()
        indicadores_records = ws("Indicadores").get_all_records()

        total_indicacoes = len(indicacoes_records)
        total_indicadores = len(indicadores_records)

        total_vendas = 0
        faturamento_total = 0.0

        for indicacao in indicacoes_records:
            if _to_bool(indicacao.get("gerou_venda")):
                total_vendas += 1
                faturamento_total += _to_float(indicacao.get("faturamento_gerado", 0))

        taxa_conversao = (total_vendas / total_indicacoes * 100) if total_indicacoes > 0 else 0

        stats = {
            'total_indicacoes': total_indicacoes,
            'total_indicadores': total_indicadores,
            'total_vendas': total_vendas,
            'taxa_conversao': round(taxa_conversao, 1),
            'faturamento_total': faturamento_total
        }

        return jsonify(stats)

    except Exception as e:
        return jsonify(ok=False, error="DASHBOARD_ERROR", message=str(e), trace=traceback.format_exc()), 500
            "error": str(e),
            "trace": traceback.format_exc()
        })
