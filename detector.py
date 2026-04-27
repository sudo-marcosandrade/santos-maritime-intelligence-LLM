import cv2
import os
from datetime import datetime
from ultralytics import YOLO
from config import MODEL_PATH, DETECTIONS_DIR, YOLO_CONFIDENCE, TARGET_CLASSES

class ShipDetector:
    def __init__(self, model_path=MODEL_PATH, seen_ids=None):
        """
        Inicializa o modelo YOLOv12.
        seen_ids pode ser passado (ex: do banco de dados) para evitar duplicidade.
        """
        self.model = YOLO(model_path)
        self.seen_ids = seen_ids if seen_ids is not None else set()

    def process_frame(self, frame):
        """
        Processa um frame, realiza o tracking e salva crops de novos navios.
        Retorna uma lista de dados das novas detecções e o frame anotado para visualização.
        """
        new_detections = []
        
        # Executa o tracking no frame
        results = self.model.track(
            frame, 
            conf=YOLO_CONFIDENCE, 
            persist=True, 
            verbose=False
        )

        annotated_frame = frame.copy()

        for result in results:
            # Plota as detecções no frame de visualização
            annotated_frame = result.plot()

            if result.boxes.id is not None:
                for box in result.boxes:
                    track_id = int(box.id.item())
                    cls_idx = int(box.cls.item())
                    label = result.names[cls_idx]

                    # Filtra apenas as classes de interesse (ex: 'boat')
                    if label in TARGET_CLASSES and track_id not in self.seen_ids:
                        self.seen_ids.add(track_id)
                        
                        # Extrai coordenadas e realiza o crop
                        x1, y1, x2, y2 = map(int, box.xyxy[0])
                        
                        # Garante que o crop está dentro dos limites da imagem
                        y1, y2 = max(0, y1), min(frame.shape[0], y2)
                        x1, x2 = max(0, x1), min(frame.shape[1], x2)
                        
                        crop_img = frame[y1:y2, x1:x2]
                        
                        if crop_img.size > 0:
                            # Gera nome do arquivo e timestamp
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            file_timestamp = timestamp.replace(":", "").replace(" ", "_")
                            filename = f"ship_{track_id}_{file_timestamp}.jpg"
                            filepath = os.path.join(DETECTIONS_DIR, filename)
                            
                            # Salva a imagem
                            cv2.imwrite(filepath, crop_img)
                            
                            # Adiciona aos resultados para o banco de dados
                            new_detections.append({
                                'track_id': track_id,
                                'timestamp': timestamp,
                                'image_path': filename
                            })
        
        # Adicionado para o Stream na Landing Page
        try:
            from state import video_frame_queue
            if not video_frame_queue.full():
                video_frame_queue.put(annotated_frame)
        except ImportError:
            pass

        return new_detections, annotated_frame

if __name__ == "__main__":
    # Teste rápido de inicialização
    try:
        detector = ShipDetector()
        print(f"Detector YOLOv12 carregado com sucesso a partir de: {MODEL_PATH}")
    except Exception as e:
        print(f"Erro ao carregar o modelo: {e}")
