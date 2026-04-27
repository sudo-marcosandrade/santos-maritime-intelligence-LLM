import cv2
import yt_dlp
import time
from config import DEFAULT_STREAM_URL

class StreamHandler:
    def __init__(self, url=DEFAULT_STREAM_URL):
        self.url = url
        self.cap = None

    def _get_stream_url(self):
        """Usa yt-dlp para extrair a URL real do vídeo do YouTube."""
        ydl_opts = {
            'format': 'best[height<=720]', # Qualidade balanceada para processamento
            'quiet': True,
            'no_warnings': True
        }
        try:
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(self.url, download=False)
                return info['url']
        except Exception as e:
            print(f"Erro ao extrair URL do stream: {e}")
            return None

    def start_capture(self):
        """Inicializa a captura do vídeo."""
        real_url = self._get_stream_url()
        if real_url:
            self.cap = cv2.VideoCapture(real_url)
            if not self.cap.isOpened():
                print("Erro: Não foi possível abrir o stream de vídeo.")
                return False
            return True
        return False

    def get_frame(self):
        """Lê o próximo frame. Se houver erro de TLS ou Socket, tenta re-extrair a URL do YouTube."""
        if self.cap and self.cap.isOpened():
            try:
                ret, frame = self.cap.read()
                if ret:
                    return frame
                else:
                    raise Exception("Frame vazio ou erro de leitura")
            except Exception as e:
                print(f"Aviso: Conexão interrompida ({e}). Reconectando...")
                self.stop_capture()
                time.sleep(2) # Pequena pausa antes de tentar novamente
                if self.start_capture():
                    ret, frame = self.cap.read()
                    return frame if ret else None
        return None

    def stop_capture(self):
        """Libera os recursos de vídeo."""
        if self.cap:
            self.cap.release()
            cv2.destroyAllWindows()

if __name__ == "__main__":
    # Teste rápido de visualização
    handler = StreamHandler()
    if handler.start_capture():
        print("Stream iniciado com sucesso. Pressione 'q' para fechar a janela de teste.")
        while True:
            frame = handler.get_frame()
            if frame is None:
                print("Fim do stream ou erro na captura.")
                break
            
            cv2.imshow("Teste Stream - Santos Maritime", frame)
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
        handler.stop_capture()
    else:
        print("Falha ao iniciar o stream. Verifique sua conexão ou a URL do YouTube.")
