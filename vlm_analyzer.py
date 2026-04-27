from google import genai
import os
from config import GEMINI_API_KEY, VLM_MODEL_NAME

class VLMAnalyzer:
    def __init__(self, api_key=GEMINI_API_KEY, model_name=VLM_MODEL_NAME):
        """Configura o novo SDK do Google GenAI."""
        if not api_key:
            print("AVISO: GOOGLE_API_KEY não configurada.")
            self.client = None
        else:
            # Novo padrão de inicialização do SDK google-genai
            self.client = genai.Client(api_key=api_key)
            self.model_id = model_name

    def analyze_image(self, image_path):
        """Envia uma imagem para o Gemini usando o novo SDK."""
        if self.client is None:
            return "Erro: Cliente API não configurado."

        if not os.path.exists(image_path):
            return f"Erro: Arquivo {image_path} não encontrado."

        try:
            # No novo SDK, o upload e a geração são integrados ou mais simplificados
            with open(image_path, "rb") as f:
                image_bytes = f.read()

            prompt = (
                "Descreva este navio em uma frase técnica e curta. "
                "Foque no tipo (cargueiro, petroleiro, porta-contêiner, etc), "
                "nas cores predominantes e em qualquer identificação visível."
            )

            # Chamada direta usando bytes da imagem (mais rápido que upload_file para imagens pequenas)
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=[
                    prompt,
                    genai.types.Part.from_bytes(data=image_bytes, mime_type="image/jpeg")
                ]
            )
            
            return response.text.strip()
            
        except Exception as e:
            return f"Erro na análise VLM: {str(e)}"

if __name__ == "__main__":
    analyzer = VLMAnalyzer()
    if analyzer.client:
        print(f"VLM Analyzer (Novo SDK) inicializado com {VLM_MODEL_NAME}.")
