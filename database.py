import sqlite3
from config import DB_PATH

class DatabaseManager:
    def __init__(self, db_path=DB_PATH):
        self.db_path = db_path
        self.init_db()

    def _get_connection(self):
        """Retorna uma nova conexão com o banco de dados."""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Cria a tabela de detecções se ela não existir."""
        query = '''
            CREATE TABLE IF NOT EXISTS detections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                track_id INTEGER,
                timestamp TEXT,
                image_path TEXT,
                vlm_description TEXT,
                status TEXT DEFAULT 'pendente'
            )
        '''
        with self._get_connection() as conn:
            conn.execute(query)
            conn.commit()

    def insert_detection(self, track_id, timestamp, image_path):
        """Insere uma nova detecção capturada pelo YOLO."""
        query = "INSERT INTO detections (track_id, timestamp, image_path) VALUES (?, ?, ?)"
        with self._get_connection() as conn:
            conn.execute(query, (track_id, timestamp, image_path))
            conn.commit()

    def get_pending_detections(self):
        """Busca todos os registros que ainda não foram analisados pela VLM."""
        query = "SELECT id, image_path FROM detections WHERE status = 'pendente'"
        with self._get_connection() as conn:
            conn.row_factory = sqlite3.Row  # Permite acessar colunas pelo nome
            cursor = conn.cursor()
            cursor.execute(query)
            return cursor.fetchall()

    def update_vlm_description(self, detection_id, description):
        """Atualiza o registro com a descrição da IA e muda o status para 'concluido'."""
        query = "UPDATE detections SET vlm_description = ?, status = 'concluido' WHERE id = ?"
        with self._get_connection() as conn:
            conn.execute(query, (description, detection_id))
            conn.commit()

    def get_all_descriptions(self):
        """Retorna todas as descrições concluídas para geração de relatório."""
        query = "SELECT vlm_description FROM detections WHERE status = 'concluido'"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return [row[0] for row in cursor.fetchall()]

    def get_seen_track_ids(self):
        """Retorna um conjunto de todos os track_ids já registrados para evitar duplicidade."""
        query = "SELECT DISTINCT track_id FROM detections"
        with self._get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute(query)
            return {row[0] for row in cursor.fetchall()}

if __name__ == "__main__":
    db = DatabaseManager()
    print(f"Banco de dados inicializado em: {DB_PATH}")
