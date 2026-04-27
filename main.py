import cv2
import os
import logging
import threading
import queue
import time
from config import DETECTIONS_DIR
from database import DatabaseManager
from detector import ShipDetector
from stream_handler import StreamHandler
from vlm_analyzer import VLMAnalyzer
from summarizer import ReportGenerator

# Configuração de Logging
logging.basicConfig(
    level=logging.INFO, 
    format='%(asctime)s [%(threadName)s] %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)

class MaritimeIntelligenceApp:
    def __init__(self):
        logging.info("=== SISTEMA DE INTELIGÊNCIA MARÍTIMA V2.0 ===")
        
        self.db = DatabaseManager()
        
        # Recupera o estado anterior do banco de dados
        seen_ids = self.db.get_seen_track_ids()
        logging.info(f"Sincronização concluída: {len(seen_ids)} navios já conhecidos.")
        
        self.detector = ShipDetector(seen_ids=seen_ids)
        self.stream = StreamHandler()
        self.vlm = VLMAnalyzer()
        self.summarizer = ReportGenerator()
        
        # Fila de processamento para a IA (Thread Safety)
        self.analysis_queue = queue.Queue()
        self.is_running = True

    def _vlm_worker(self):
        """Thread que processa a análise VLM em segundo plano."""
        logging.info("Worker de IA iniciado.")
        while self.is_running:
            try:
                # Tenta pegar um item da fila (bloqueia por 1 segundo)
                registro = self.analysis_queue.get(timeout=1)
                
                img_id = registro['id']
                img_path = os.path.join(DETECTIONS_DIR, registro['image_path'])
                
                logging.info(f"IA processando detecção #{img_id}...")
                descricao = self.vlm.analyze_image(img_path)
                
                self.db.update_vlm_description(img_id, descricao)
                logging.info(f"IA Concluída #{img_id}: {descricao}")
                
                self.analysis_queue.task_done()
            except queue.Empty:
                continue
            except Exception as e:
                logging.error(f"Erro no Worker de IA: {e}")

    def run(self):
        """Loop principal: Detecção em tempo real + Orquestração de Threads."""
        
        # Inicia o Servidor da API para a Landing Page
        import uvicorn
        from api import app as fastapi_app
        api_thread = threading.Thread(
            target=lambda: uvicorn.run(fastapi_app, host="0.0.0.0", port=8000, log_level="error"),
            name="API-Server",
            daemon=True
        )
        api_thread.start()
        logging.info("API e Landing Page disponíveis em http://localhost:8000")

        # Inicia a Thread de IA
        worker_thread = threading.Thread(target=self._vlm_worker, name="VLM-Worker", daemon=True)
        worker_thread.start()

        # Adiciona no processamento inicial tudo que estava pendente no banco
        pendentes = self.db.get_pending_detections()
        for p in pendentes:
            self.analysis_queue.put(p)

        if not self.stream.start_capture():
            return

        logging.info("Monitoramento iniciado. Pressione 'q' para gerar o relatório e sair.")
        
        try:
            while self.is_running:
                frame = self.stream.get_frame()
                if frame is None:
                    break

                # Detecção
                new_detections, annotated_frame = self.detector.process_frame(frame)

                # Persistência e enfileiramento imediato para a IA
                for det in new_detections:
                    self.db.insert_detection(det['track_id'], det['timestamp'], det['image_path'])
                    
                    # Busca o ID gerado pelo banco para colocar na fila
                    # (Simplificação: pegamos o último inserido ou buscamos por path)
                    # Para ser robusto, ideal é que insert_detection retorne o ID.
                    # Vamos buscar os pendentes novamente para atualizar a fila de forma segura.
                    pendentes_novos = self.db.get_pending_detections()
                    for p in pendentes_novos:
                        # Só adiciona se não estiver na fila (poderíamos usar um set de controle)
                        self.analysis_queue.put(p)

                # GUI
                cv2.imshow("Santos Maritime Intelligence - LIVE", annotated_frame)
                
                if cv2.waitKey(1) & 0xFF == ord('q'):
                    break

        except KeyboardInterrupt:
            logging.warning("Interrupção manual.")
        finally:
            logging.info("Encerrando captura e aguardando análises finais...")
            self.is_running = False
            self.stream.stop_capture()
            cv2.destroyAllWindows()
            
            # Fase Final: Relatório
            descricoes = self.db.get_all_descriptions()
            if descricoes:
                relatorio = self.summarizer.generate_summary(descricoes)
                print("\n" + "="*70)
                print("          RELATÓRIO DE INTELIGÊNCIA MARÍTIMA FINAL")
                print("="*70)
                print(relatorio)
                print("="*70 + "\n")

if __name__ == "__main__":
    app = MaritimeIntelligenceApp()
    app.run()
