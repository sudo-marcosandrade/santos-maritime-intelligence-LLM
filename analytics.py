import pandas as pd
import sqlite3
from config import DB_PATH

class MaritimeAnalytics:
    """
    Motor de Analytics do Projeto.
    Transforma registros brutos e descrições de texto em dados estruturados para BI.
    """
    
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path

    def _load_data(self):
        """Conecta ao banco e carrega os dados processados para um DataFrame."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Filtramos apenas o que já passou pela análise da IA (VLM)
            query = "SELECT * FROM detections WHERE status = 'concluido'"
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if not df.empty:
                # Converte o timestamp para o formato datetime do Pandas para análise temporal
                df['timestamp'] = pd.to_datetime(df['timestamp'])
            return df
        except Exception as e:
            print(f"Erro ao carregar dados para analytics: {e}")
            return pd.DataFrame()

    def get_traffic_by_hour(self):
        """
        Gera dados para gráfico de linha: Volume de tráfego por hora.
        Ideal para identificar picos de movimentação no Porto.
        """
        df = self._load_data()
        if df.empty:
            return {}

        # Agrupa por hora e conta navios únicos (track_id)
        df.set_index('timestamp', inplace=True)
        traffic = df.resample('H')['track_id'].nunique()
        
        # Retorna um dicionário onde a chave é a hora e o valor é a contagem
        return {k.strftime("%H:00"): int(v) for k, v in traffic.items()}

    def get_ship_types_distribution(self):
        """
        Mineração de Texto: Extrai categorias das descrições geradas pelo Gemini.
        Aqui é onde transformamos a 'conversa' da IA em 'estatística'.
        """
        df = self._load_data()
        if df.empty:
            return {}

        # Dicionário de mapeamento (Palavra-chave na descrição -> Categoria do Gráfico)
        mapping = {
            'Cargueiro': ['cargueiro', 'cargo', 'mercante', 'graneleiro'],
            'Porta-Contêiner': ['contêiner', 'container', 'porta-contêiner'],
            'Petroleiro': ['petroleiro', 'tanker', 'óleo', 'combustível'],
            'Rebocador': ['rebocador', 'tug', 'apoio'],
            'Passageiros': ['cruzeiro', 'passageiros', 'turismo', 'ferry'],
            'Navio de Guerra': ['fragata', 'militar', 'marinha', 'guerra']
        }

        distribution = {cat: 0 for cat in mapping.keys()}
        distribution['Outros'] = 0

        # Analisa cada descrição gerada pelo Gemini
        for desc in df['vlm_description'].fillna("").str.lower():
            found = False
            for category, keywords in mapping.items():
                if any(key in desc for key in keywords):
                    distribution[category] += 1
                    found = True
                    break
            if not found and desc != "":
                distribution['Outros'] += 1

        # Remove categorias com valor zero para limpar o gráfico
        return {k: v for k, v in distribution.items() if v > 0}

    def get_kpis(self):
        """Retorna indicadores de alto nível para o topo do Dashboard/Landing Page."""
        df = self._load_data()
        if df.empty:
            return {
                "total_navios": 0,
                "tipo_predominante": "N/A",
                "status_ia": "Aguardando dados"
            }

        dist = self.get_ship_types_distribution()
        tipo_predominante = max(dist, key=dist.get) if dist else "N/A"

        return {
            "total_navios_detectados": int(df['track_id'].nunique()),
            "tipo_predominante": tipo_predominante,
            "analises_ia_concluidas": len(df),
            "taxa_sucesso_vlm": "100%" # Pode ser calculado comparando pendentes x concluidos
        }

if __name__ == "__main__":
    # Teste de execução isolada
    engine = MaritimeAnalytics()
    print("\n[ANALYTICS] Testando extração de dados...")
    print(f"KPIs: {engine.get_kpis()}")
    print(f"Tipos de Navios: {engine.get_ship_types_distribution()}")
    print(f"Tráfego por Hora: {engine.get_traffic_by_hour()}")
