from fastapi import FastAPI, HTTPException, Response
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, StreamingResponse
import uvicorn
from analytics import MaritimeAnalytics
from database import DatabaseManager
from summarizer import ReportGenerator
import logging
import pandas as pd
import os
import cv2
from state import video_frame_queue

# Configuração de Log

app = FastAPI(title="Santos Maritime Intelligence API")

# ... (CORS e StaticFiles mantidos)
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])
if not os.path.exists("assets"): os.makedirs("assets")
app.mount("/assets", StaticFiles(directory="assets"), name="assets")

analytics = MaritimeAnalytics()
db = DatabaseManager()
summarizer = ReportGenerator()

def gen_frames():
    while True:
        if not video_frame_queue.empty():
            frame = video_frame_queue.get()
            ret, buffer = cv2.imencode('.jpg', frame)
            if not ret: continue
            yield (b'--frame\r\n'
                   b'Content-Type: image/jpeg\r\n\r\n' + buffer.tobytes() + b'\r\n')

@app.get("/api/video_feed")
async def video_feed():
    """Endpoint que fornece o stream de vídeo para o HTML."""
    return StreamingResponse(gen_frames(), media_type="multipart/x-mixed-replace; boundary=frame")

@app.get("/")
def read_root():
    return FileResponse("index.html")

# Adicione esta função para outros scripts enviarem frames para a API
@app.post("/api/update_frame")
async def update_frame(frame_data: dict):
    # Logica para receber frame via POST (opcional, simplificaremos via global no mesmo processo se rodar junto)
    pass

@app.get("/api/kpis")
def get_kpis(): return analytics.get_kpis()

@app.get("/api/traffic")
def get_traffic(): return analytics.get_traffic_by_hour()

@app.get("/api/distribution")
def get_distribution(): return analytics.get_ship_types_distribution()

@app.get("/api/detections/latest")
def get_latest_detections(limit: int = 10):
    try:
        conn = db._get_connection()
        query = f"SELECT * FROM detections ORDER BY id DESC LIMIT {limit}"
        df = pd.read_sql_query(query, conn)
        conn.close()
        return df.to_dict(orient="records")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/report/summary", tags=["AI"])
def get_ai_summary():
    """Gera dinamicamente o relatório executivo baseado nos dados atuais."""
    descriptions = db.get_all_descriptions()
    if not descriptions:
        return {"summary": "Aguardando análises da IA para gerar o resumo executivo."}
    
    report = summarizer.generate_summary(descriptions)
    return {"summary": report}

if __name__ == "__main__":
    # Comando para rodar: python api.py
    uvicorn.run(app, host="0.0.0.0", port=8000)
