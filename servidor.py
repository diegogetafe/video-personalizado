import os
from flask import Flask, request, jsonify
import dropbox
import time
import subprocess
from waitress import serve  # Servidor de producción para Railway

# 🔹 CONFIGURA TU ACCESS TOKEN DE DROPBOX
ACCESS_TOKEN = "TU_ACCESS_TOKEN_AQUI"  # Reemplaza con tu token real

# 🔹 OBTENER RUTA DEL PROYECTO EN RAILWAY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔹 UBICACIÓN DE ARCHIVOS DENTRO DEL PROYECTO
video_base = os.path.join(BASE_DIR, "video_base.mp4")  # Archivo de vídeo base
fuente = os.path.join(BASE_DIR, "Bebas-Regular.ttf")  # Fuente personalizada

app = Flask(__name__)

def generar_video(nombre_padre):
    """Genera un vídeo con el nombre del padre sobre la taquilla"""
    video_salida = os.path.join(BASE_DIR, f"video_{nombre_padre}.mp4")

    # 🔹 Ajusta x, y para colocar el texto sobre la taquilla en el vídeo
    comando = [
        "ffmpeg", "-i", video_base,
        "-vf", f"drawtext=text='{nombre_padre}':fontfile={fuente}:fontcolor=white:fontsize=50:x=100:y=200",
        "-codec:a", "copy", video_salida
    ]

    subprocess.run(comando)
    return video_salida

def subir_a_dropbox(archivo_local, nombre_padre):
    """Sube el vídeo generado a Dropbox y obtiene un enlace de descarga directa"""
    dbx = dropbox.Dropbox(ACCESS_TOKEN)
    timestamp = int(time.time())
    ruta_dropbox = f"/videos_dia_padre/{nombre_padre}_{timestamp}.mp4"

    with open(archivo_local, "rb") as f:
        dbx.files_upload(f.read(), ruta_dropbox, mode=dropbox.files.WriteMode("overwrite"))

    enlace = dbx.sharing_create_shared_link_with_settings(ruta_dropbox).url
    return enlace.replace("?dl=0", "?dl=1")  # Descarga directa

@app.route("/generar_video", methods=["POST"])
def generar_y_subir():
    data = request.json
    nombre_padre = data.get("nombre")

    if not nombre_padre:
        return jsonify({"error": "Nombre no proporcionado"}), 400

    archivo_generado = generar_video(nombre_padre)
    enlace_descarga = subir_a_dropbox(archivo_generado, nombre_padre)

    return jsonify({"link": enlace_descarga})

# 🔹 SERVIDOR PARA PRODUCCIÓN EN RAILWAY
if __name__ == "__main__":
    serve(app, host="0.0.0.0", port=5000)
