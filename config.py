import os
from pathlib import Path
from dotenv import load_dotenv

# Carrega as variáveis de ambiente do arquivo .env
load_dotenv()

# Caminhos Base
BASE_DIR = Path(__file__).resolve().parent
ASSETS_DIR = BASE_DIR / "assets"
DETECTIONS_DIR = ASSETS_DIR / "detections"

# Configurações de Arquivos e Banco de Dados
DB_PATH = str(BASE_DIR / "maritime_intelligence.db")
MODEL_PATH = str(ASSETS_DIR / "yolo12m.pt")

# Configurações do Modelo YOLO
YOLO_CONFIDENCE = 0.5
YOLO_TRACK_PERSIST = True
TARGET_CLASSES = ['boat']

# Configurações do Google Gemini (VLM)
GEMINI_API_KEY = os.getenv("GOOGLE_API_KEY")
VLM_MODEL_NAME = 'gemini-2.0-flash'

# Configurações de Stream (YouTube)
DEFAULT_STREAM_URL = 'https://www.youtube.com/watch?v=tMYtrEBNVAU'

# Garante que as pastas necessárias existam
DETECTIONS_DIR.mkdir(parents=True, exist_ok=True)

if __name__ == "__main__":
    print(f"Configurações carregadas com sucesso!")
    print(f"Banco de Dados: {DB_PATH}")
    print(f"Diretório de Capturas: {DETECTIONS_DIR}")
    if not GEMINI_API_KEY:
        print("AVISO: GOOGLE_API_KEY não encontrada no arquivo .env")
