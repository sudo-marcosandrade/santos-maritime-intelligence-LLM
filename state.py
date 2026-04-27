import queue

# Fila global compartilhada entre o Detector e a API
video_frame_queue = queue.Queue(maxsize=10)
