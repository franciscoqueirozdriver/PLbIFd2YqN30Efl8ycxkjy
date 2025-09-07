import gspread
import os
import json
from dotenv import load_dotenv

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

class GoogleSheetsClient:
    def __init__(self):
        self.spreadsheet_id = os.getenv('SPREADSHEET_ID')
        if not self.spreadsheet_id:
            raise ValueError("A variável de ambiente SPREADSHEET_ID não está definida.")

        # Montar o dicionário de credenciais a partir das variáveis de ambiente
        try:
            private_key = os.getenv('GOOGLE_PRIVATE_KEY').replace('\\n', '\n')
            creds_json = {
                "type": "service_account",
                "project_id": os.getenv('GOOGLE_PROJECT_ID', ''), # Opcional, mas bom ter
                "private_key_id": os.getenv('GOOGLE_PRIVATE_KEY_ID', ''), # Opcional
                "private_key": private_key,
                "client_email": os.getenv('GOOGLE_CLIENT_EMAIL'),
                "client_id": os.getenv('GOOGLE_CLIENT_ID', ''), # Opcional
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": f"https://www.googleapis.com/robot/v1/metadata/x509/{os.getenv('GOOGLE_CLIENT_EMAIL')}"
            }

            # Autenticar
            self.gc = gspread.service_account_from_dict(creds_json)
            self.spreadsheet = self.gc.open_by_key(self.spreadsheet_id)
        except Exception as e:
            raise ConnectionError(f"Falha ao conectar com o Google Sheets: {e}")

    def get_worksheet(self, tab_name):
        """Abre uma aba (worksheet) pelo nome."""
        try:
            return self.spreadsheet.worksheet(tab_name)
        except gspread.WorksheetNotFound:
            raise ValueError(f"A aba '{tab_name}' não foi encontrada na planilha.")

    def clear_and_insert(self, tab_name, data):
        """
        Limpa todos os dados de uma aba (exceto o cabeçalho) e insere novos dados.

        Args:
            tab_name (str): O nome da aba a ser atualizada.
            data (list of dict): Uma lista de dicionários onde cada dicionário representa uma linha.
                                 As chaves do dicionário devem corresponder aos cabeçalhos da planilha.
        """
        if not isinstance(data, list):
            raise TypeError("Os dados devem ser uma lista de dicionários.")

        worksheet = self.get_worksheet(tab_name)

        # Limpar dados antigos (da segunda linha em diante)
        worksheet.clear_basic() # Limpa toda a formatação e conteúdo, temos que reescrever o header

        if not data:
            # Se não há dados, apenas loga e sai (cabeçalho será escrito se houver)
            print(f"Nenhum dado para inserir na aba '{tab_name}'. A aba foi limpa.")
            return

        # Pega os cabeçalhos do primeiro item de dados
        headers = list(data[0].keys())

        # Converte a lista de dicionários para uma lista de listas
        rows_to_insert = [headers] + [[item.get(header, '') for header in headers] for item in data]

        # Insere os dados em lote
        worksheet.update(rows_to_insert, 'A1')

        print(f"Aba '{tab_name}' limpa e {len(data)} registros inseridos com sucesso.")

    def append_row(self, tab_name, row_data):
        """
        Adiciona uma única linha ao final da aba.

        Args:
            tab_name (str): O nome da aba.
            row_data (dict): Um dicionário com os dados da linha.
        """
        worksheet = self.get_worksheet(tab_name)
        headers = worksheet.row_values(1)

        # Garante que a ordem dos valores corresponda à ordem dos cabeçalhos
        values = [row_data.get(header, '') for header in headers]
        worksheet.append_row(values)
        print(f"1 linha adicionada à aba '{tab_name}'.")

    def get_rows(self, tab_name):
        """Retorna todos os registros de uma aba como uma lista de dicionários."""
        worksheet = self.get_worksheet(tab_name)
        return worksheet.get_all_records()

# Exemplo de uso (para teste)
if __name__ == '__main__':
    try:
        client = GoogleSheetsClient()

        # Teste de clear_and_insert
        test_data = [
            {'col1': 'a', 'col2': 1},
            {'col1': 'b', 'col2': 2}
        ]
        # client.clear_and_insert('Test', test_data) # Use uma aba de teste

        # Teste de append_row
        # client.append_row('Test', {'col1': 'c', 'col2': 3})

        # Teste de get_rows
        # rows = client.get_rows('Test')
        # print(rows)

        print("GoogleSheetsClient inicializado com sucesso.")

    except (ValueError, ConnectionError) as e:
        print(e)
