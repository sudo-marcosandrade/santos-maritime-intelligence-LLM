from google import genai
from config import GEMINI_API_KEY, VLM_MODEL_NAME

class ReportGenerator:
    def __init__(self, api_key=GEMINI_API_KEY, model_name=VLM_MODEL_NAME):
        """Configura o novo SDK do Google GenAI para sumarização."""
        if not api_key:
            print("AVISO: GOOGLE_API_KEY não configurada.")
            self.client = None
        else:
            self.client = genai.Client(api_key=api_key)
            self.model_id = model_name

    def generate_summary(self, descriptions):
        """Gera resumo executivo usando o novo SDK."""
        if self.client is None:
            return "Erro: API Key não configurada."

        if not descriptions:
            return "Nenhuma detecção registrada."

        text_notes = "\n".join([f"- {desc}" for desc in descriptions])
        prompt = f"""
        Abaixo estão as notas técnicas de todos os navios detectados hoje:
        {text_notes}
        Escreva um parágrafo de resumo executivo formal e focado em inteligência logística.
        """

        try:
            response = self.client.models.generate_content(
                model=self.model_id,
                contents=prompt
            )
            return response.text.strip()
        except Exception as e:
            return f"Erro ao gerar relatório: {str(e)}"
