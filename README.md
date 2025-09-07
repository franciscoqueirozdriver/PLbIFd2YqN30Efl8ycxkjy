# API Serverless Flask + Google Sheets

API em Python/Flask preparada para deploy serverless na Vercel, usando abas do Google Sheets como banco de dados.

## Variáveis de ambiente

Defina as variáveis no `.env` ou no painel da Vercel:

```bash
GOOGLE_PRIVATE_KEY="<key com \\n escapado>"
GOOGLE_CLIENT_EMAIL="service-account@..."
SPREADSHEET_ID="<id da planilha>"
TZ="America/Sao_Paulo"
```

## Instalação

```bash
pip install -r requirements.txt
```

## Execução local

Os arquivos em `api/` expõem `app = Flask(__name__)`. Para testar localmente um endpoint:

```bash
flask --app api/indicadores:app run
```

## Endpoints

- `GET /api/indicadores`
- `POST /api/indicadores`
- `PUT /api/indicadores/<indicador_id>`
- `DELETE /api/indicadores/<indicador_id>`
- `GET /api/indicacoes`
- `POST /api/indicacoes`
- `PUT /api/indicacoes/<indicacao_id>`
- `DELETE /api/indicacoes/<indicacao_id>`
- `GET /api/dashboard`

## Testes manuais

Exemplos de chamadas após o deploy:

```bash
# listar indicadores
curl https://<deploy>/api/indicadores

# criar indicador
curl -X POST https://<deploy>/api/indicadores \
  -H 'Content-Type: application/json' \
  -d '{"nome":"João","telefone":"+5511999999999","email":"j@ex.com","empresa":"Tech"}'

# criar indicação
curl -X POST https://<deploy>/api/indicacoes \
  -H 'Content-Type: application/json' \
  -d '{"indicador_id":"IND_0001","data_indicacao":"2025-09-07","nome_indicado":"Maria","telefone_indicado":"+5511888888888","gerou_venda":true,"faturamento_gerado":150000,"status_recompensa":"EmProcessamento"}'
```

## Limitações / Próximos passos

- Não há garantia contra condições de corrida na geração de IDs.
- Falta camada de autenticação completa.
- Backoff simples para quotas do Sheets.
