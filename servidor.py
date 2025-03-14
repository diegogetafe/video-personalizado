import os
from flask import Flask, request, jsonify
import dropbox
import time
import subprocess

# 🔹 CONFIGURA TU ACCESS TOKEN DE DROPBOX
ACCESS_TOKEN = "sl.u.AFnFe2XsdeG7QheIRPuy65-F35LgsXnQPDUU1fBpEho_qPSeTwJ1IZ_I8Tlsi7T7pr9YtmARhh9KhtggDmoJYG91-TiFNaLFJZy2fMFvOiW2id5XYz7FJcYaM8T-eO4ecCq6Tsw2fxYNWKlAWJ25oE5YRSvxoOrzZHV_Np4OIsQv-3WRmFW_FmBsN40YCb7i3xCbN9a9XH1DqY-coXchwR3JBi2VrR0p1EpDEQ3X8FYOEqjUtkB2sYhfOSKIKrZJ2pB_5eSuWAMTmwZkwB5pUvKZV36UXc0u_2oY-mByKP_ciSv3DDhReT8PYIF7iM5s48fb3V3A6omwuRZKiWSfNma7tWk8teDgTH89YMb6WmYIP3vLsTAXC2nRu6zDmNxjC_CtwrFwL8lnIc5HdX3kybN5YsxpImWDGqRS6PgomqpamWnqzCYltYQqVutVnjz_qp7KGmLtYmeSbuTETRWf4LwdNzGp3qy3MY42_THlC8WIzv_G5ERlIio3Fvx2HqPSf_IAWNW_Uf7NR0kxBkzjybI3g8fIjjBNSZKlw5VzsfH5i7RkQRw3Dh4OJ8UtwcBxbSu5Gd0wbuEEAjM1JAYHMvZdLD0G9yUp2i1v-l-z3N2TO1RZhBUApH-zYadraKgVJnIEiLobu-9Sh6OIhPTaUNjC6bRFyNSwoykimfhOVz5a6VZN6XdEEbrjfdwrCBmzBI_hZeTIV_Up4emMpsqj2nf5M6IJw8GfvtKlqQrOBzIjmMgLYFTMtFOvSqCQ7pSl0ojUvg13mImuTzSraEhvSCCBRwSocNCZ6NJfIcidNFoRT0RJe3OEK5Ejni0OPfT-xthoChFrTgDK7SYkXPmgWr97dEurEr326bvzL3ncjigqHbHFH-ESSejihgCJo7YrrTvc2kSz1Wb4bmEqdr8VROeoLHCmzzpx5u4VSNK-CTVO0LRQ-99FNSNZueTFf0o2iPqV53jw7cz41N3hU6yQq0qurUNWq6w7eO_5b_Sx3zOBiwk3qleVN5uqAOTOpuml_uuy0UW_62hStqzwznzc11mGz9OwsCSIo7O7NydbtV2DfoM4Ld4csbl0004hfuYQgblUqhUibD83LStZJAROMm3cmVgAiAjLC-Y66j4B6KWYrVs1Uba7WiJyTxW9gxlMT-IWWrKejIu4M2deGFomyZDPzPURPHOU_Xc5IthpHcAoTPXWvhV8Da01oRt_6ix-yvgtMrUZBIwNaCK9iNk_2QTZY7H1XuRsGt-x_36lbCuxLKMlMFpfqtvg5_Z23xFQwX2LkywUIiy0jJIes0647tVyv3EoZ3NFCxFkD-WZm4TGrTVtz7a005TV1gI48hU3wNyI1kbbeZvzSlS86UEPUZMKJFDg44lG5nBTGl66J0X7wg"

# 🔹 OBTENER RUTA DEL PROYECTO EN RAILWAY
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# 🔹 UBICACIÓN DE ARCHIVOS DENTRO DEL PROYECTO
video_base = os.path.join(BASE_DIR, "video_base.mp4")  # Asegura que Railway encuentra el video
fuente = os.path.join(BASE_DIR, "Bebas-Regular.ttf")  # Asegura que Railway encuentra la fuente

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

if __name__ == "__main__":
    app.run(debug=True)