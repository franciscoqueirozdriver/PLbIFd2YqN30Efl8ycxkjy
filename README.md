# Sistema de Controle de Indicações - Método Duplo A

Uma aplicação web completa para gerenciar o programa de indicações "Método Duplo A", substituindo planilhas Excel por uma solução moderna e eficiente.

## 🚀 Funcionalidades

### Dashboard
- **KPIs em tempo real**: Total de indicados, indicadores, vendas, taxa de conversão e faturamento
- **Filtros por período**: Análise de dados por data inicial e final
- **Resumo visual**: Cards informativos com métricas importantes

### Gestão de Indicações
- **Lista completa**: Visualização de todas as indicações com busca e filtros
- **Formulário de cadastro**: Interface intuitiva para nova indicação
- **Controle de vendas**: Marcar/desmarcar vendas e gerenciar faturamento
- **Status de recompensa**: Controle do fluxo de pagamento (Não, Em Processamento, Sim)

### Gestão de Indicadores
- **Rede de indicadores**: Visualização da rede com estatísticas individuais
- **Métricas por indicador**: Indicações, vendas, conversão e faturamento
- **Busca e filtros**: Localização rápida de indicadores

### Importação de Dados
- **Upload de planilhas Excel**: Importação automática de dados existentes
- **Validação de dados**: Verificação de telefones, datas e campos obrigatórios
- **Relatório de importação**: Feedback detalhado do processo

## 🛠️ Tecnologias Utilizadas

### Backend
- **Flask**: Framework web Python
- **SQLAlchemy**: ORM para banco de dados
- **Marshmallow**: Serialização e validação de dados
- **SQLite**: Banco de dados (facilmente migrável para PostgreSQL/MySQL)
- **phonenumbers**: Validação e normalização de telefones brasileiros

### Frontend
- **React**: Biblioteca JavaScript para interface
- **Tailwind CSS**: Framework CSS para estilização
- **Axios**: Cliente HTTP para comunicação com API
- **React Router**: Navegação entre páginas
- **Lucide Icons**: Ícones modernos

## 📋 Requisitos do Sistema

- Python 3.11+
- Node.js 20+
- Navegador web moderno

## 🔧 Instalação e Configuração

### 1. Backend (Flask)

```bash
cd controle-indicacoes
source venv/bin/activate
pip install -r requirements.txt
```

### 2. Executar a Aplicação

```bash
python src/main.py
```

A aplicação estará disponível em: `http://localhost:5000`

## 📊 Estrutura do Banco de Dados

### Tabela: indicadores
- `id` (UUID): Identificador único
- `nome` (String): Nome completo
- `telefone` (String): Telefone normalizado E.164
- `email` (String): Email (opcional)
- `created_at`, `updated_at`: Timestamps

### Tabela: indicacoes
- `id` (UUID): Identificador único
- `data_indicacao` (Date): Data da indicação
- `nome_indicado` (String): Nome do indicado
- `telefone_indicado` (String): Telefone normalizado E.164
- `gerou_venda` (Boolean): Se gerou venda
- `faturamento_gerado` (Integer): Valor em centavos
- `status_recompensa` (Enum): Nao, Sim, EmProcessamento
- `observacoes` (Text): Observações opcionais
- `indicador_id` (UUID): Referência ao indicador
- `created_at`, `updated_at`: Timestamps

## 🔗 API Endpoints

### Indicadores
- `GET /api/indicadores` - Listar indicadores
- `POST /api/indicadores` - Criar indicador
- `GET /api/indicadores/{id}` - Obter indicador
- `PATCH /api/indicadores/{id}` - Atualizar indicador
- `DELETE /api/indicadores/{id}` - Excluir indicador

### Indicações
- `GET /api/indicacoes` - Listar indicações
- `POST /api/indicacoes` - Criar indicação
- `GET /api/indicacoes/{id}` - Obter indicação
- `PATCH /api/indicacoes/{id}` - Atualizar indicação
- `DELETE /api/indicacoes/{id}` - Excluir indicação
- `GET /api/dashboard` - Obter KPIs

### Importação
- `POST /api/import/excel` - Importar planilha Excel

## 📱 Interface do Usuário

### Design System
- **Cores principais**: Tons de roxo (#7C3AED, #6D28D9)
- **Tipografia**: Fontes legíveis e hierarquia clara
- **Componentes**: Cards com cantos arredondados, botões modernos
- **Responsividade**: Funciona em desktop, tablet e mobile

### Navegação
- **Sidebar**: Menu lateral com navegação principal
- **Breadcrumbs**: Navegação contextual
- **Estados visuais**: Hover, loading, erro e sucesso

## 🔒 Regras de Negócio

### Validações
- **Telefones**: Formato brasileiro E.164 obrigatório
- **Datas**: Não podem ser futuras
- **Vendas**: Faturamento obrigatório quando gerou venda
- **Status**: Fluxo controlado de recompensas

### Automações
- **Status automático**: Em Processamento quando marca venda
- **Faturamento zero**: Quando desmarca venda
- **Normalização**: Telefones automaticamente formatados

## 📈 Métricas e KPIs

### Dashboard Principal
- **Total de Indicados**: Contagem total de indicações
- **Total de Indicadores**: Contagem única de indicadores
- **Total de Vendas**: Indicações que geraram venda
- **Taxa de Conversão**: Percentual de vendas/indicações
- **Faturamento Total**: Soma dos valores de venda

### Filtros Disponíveis
- **Período**: Data inicial e final
- **Status de recompensa**: Filtro por status
- **Indicador específico**: Filtro por indicador
- **Busca textual**: Nome, telefone, observações

## 🚀 Próximos Passos

### Funcionalidades Futuras
- [ ] Sistema de autenticação e autorização (RBAC)
- [ ] Exportação para CSV/Excel
- [ ] Página de configurações
- [ ] Relatórios avançados
- [ ] Notificações automáticas
- [ ] API para integrações externas

### Melhorias Técnicas
- [ ] Testes automatizados
- [ ] Deploy em produção
- [ ] Monitoramento e logs
- [ ] Backup automático
- [ ] Performance optimization

## 📞 Suporte

Para dúvidas ou suporte técnico, consulte a documentação da API ou entre em contato com a equipe de desenvolvimento.

## 📄 Licença

Este projeto foi desenvolvido especificamente para o programa "Método Duplo A" e está sujeito aos termos de uso estabelecidos.

---

**Desenvolvido com ❤️ para otimizar o programa de indicações Método Duplo A**

