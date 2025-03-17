import os
from flask import Flask, request, jsonify
from flask_cors import CORS  # 🔹 Habilitar CORS para permitir peticiones desde Maker
import dropbox
import time
import subprocess
from waitress import serve  # 🔹 Para ejecutar correctamente en Railway

# 🔹 CONFIGURA TU ACCESS TOKEN DE DROPBOX
ACCESS_TOKEN = "sl.u.AFkYttnIjzJol2Jy5xYfdaKlP2Dy_xH9HpoTLfDFB0POMylItYtvOfzLVOeiUN1gF-f-eMFaKh0ey6BZh1i3LKV5Eo__2vUfU6cKTwnctZsuN0tu_KonNiIgznNPr6zY56iwhNA1_oFJ4W04YqACDtOvh-pti8YuDpR9AQ26eX83LxfzxyoIWkDZKtft6B78zdNiIz6gbePXSth_cdYI0CBBk8TILkPIIQt-jGtTNKy0QwSnbVSN0HAJNdcsLvYnJfEwHXI67HIjUtuC9HLeH_4hJCPIZfDL6OSJsIKnFzpe4FRx6OqscEs94RIk_ReLZzqceN_kdPioedyfQdYHyQzzD6Z71rAwWOGHbTS5qTXoczka2NEQdy1eu0O3RbSFC6zjnzDmpFHnarrrluJE5EByYAM0FEyArS_8gdH0Dqmr1DfIpQd_WWp95ocJLjkPQQwffrHz-WhTGyun99lzme4_AeZ2rhWLpL9jVttCk_0VQoZixHPZirHzk3hj89fgF46QhGkG4NPNmvKabcvsU_2jGty0NY9MudhZ_w78q2NA8fB6y9z_BtLg9Dx8ltq-v4XBpp6fvTJasQZPPVqy6iOYW3kZmu_dTQD996VVdi9J9zGNAQMtKbfCa6xXQGeqc0-6iKQr1_I-R9q8Eap3Fz4jA5xCVt9fVBJuBS2aqIyVbrSq907he5zrjJNEpitTjAC-Z7yV_sL0lbJcrLxMCyanQLCgqMNDdsBL9Ec2ihRJCZgQ80gzspb2CGuCPbywc9hmajyKhOpuFqo7OOrijN7_LyR0SAKhsRig8-viFfrVgigKpRQLAk9jBPf6icGbzKoMNxOCApU3YoF5U6xywmNpsZtdsLEFi6socFkthctiPaPG5XyoWCUrXjZaKio-_b61BhaKci5UNdQORtGVMxl_MTJlDI249aJ2SiMaY-I057zTTWOv65eZMcD2sgK78w7gHDtf_ANF2NPvtQFSprb0Ch0uF3Gzqn1dXMNo5jdnAN4OPrz3rYcNrYmUrc-eYS4CMrhBJ44dey4HbfIXUs8jpghINA0BwLItHfe8tI-3xtZWd2CmSzy8MC1JSD0BYVoRfA7a7ZCW3kkrrt8M6y4RJz6j9u4_5NxyDIAaRH4KPjKGFoU07segTDAAFeQ-jVJm5tXgTSnnPn_Y479V6QUFGGuXGG_G1o1lCr7MmXP_8gXKtPVU1hSUNBM2spLQv80c6aHrDL7rLT54f9-KlJzk8vzlZMAx1F7ns7LJXcub2-6OKE83_3Flv4TGUhx3CyF4uSq3MKMEOUWOlzrhpmUBAzoGu3XZTl9Eji30H8zHRST8uf6nzBorvYEkZqPsNYbV5IQHCuw6O0h8aPI1m9SOX-gCtPLSxindgFg1QhFSPA"  # Reemplaza con tu token real

# 🔹 OBTENER RUTA DEL PROYECTO EN RAILWAY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔹 UBICACIÓN DE ARCHIVOS DENTRO DEL PROYECTO
video_base = os.path.join(BASE_DIR, "video_base.mp4")  # Archivo de vídeo base
fuente = os.path.join(BASE_DIR, "Bebas-Regular.ttf")  # Fuente personalizada

app = Flask(__name__)
CORS(app)  # 🔹 Habilitar CORS para evitar errores de conexión con Maker

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
    serve(app, host="0.0.0.0", port=8000)  # 🔹 Cambiado a port=8000 para Railway
