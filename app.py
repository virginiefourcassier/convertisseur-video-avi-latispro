from flask import Flask, render_template_string, request, send_file, url_for, redirect
import subprocess
import os
import uuid
import shutil

app = Flask(__name__)

HTML_PAGE = """
<!DOCTYPE html>
<html lang="fr">
<head>
  <meta charset="UTF-8">
  <title>Convertisseur vidéo AVI – LatisPro</title>
  <style>
    body { font-family: Arial, sans-serif; background: #f3e8ff; color: #2d0052; margin: 0; padding: 24px; }
    .container { max-width: 800px; margin: 0 auto; background: #fff; border: 4px solid #6d10b1;
                 border-radius: 18px; padding: 24px; box-shadow: 0 12px 30px rgba(0,0,0,0.15); }
    h1 { text-align: center; color: #4b0082; }
    .info { background: #f8f2ff; border-left: 6px solid #6d10b1; padding: 14px; border-radius: 10px; margin-bottom: 18px; }
    .footer { margin-top: 26px; text-align: center; font-size: 14px; color: #6d10b1; border-top: 2px solid #ead7ff; padding-top: 14px; }
    button { background: #6d10b1; color: white; border: none; border-radius: 12px; padding: 10px 20px; font-size: 16px; cursor: pointer; }
    button:disabled { opacity: .6; cursor: not-allowed; }
    input[type=file] { margin: 12px 0; }
    .error { color: #c62828; margin-top: 12px; }
    .success { color: #2e7d32; margin-top: 12px; }
    .spinner {
      display: none;
      margin-top: 16px;
      text-align: center;
      color: #4b0082;
      font-weight: bold;
    }
    .spinner::before {
      content: "";
      display: inline-block;
      width: 18px;
      height: 18px;
      border: 3px solid #d1b3ff;
      border-top-color: #6d10b1;
      border-radius: 50%;
      margin-right: 8px;
      animation: spin 0.7s linear infinite;
    }
    @keyframes spin {
      to { transform: rotate(360deg); }
    }
  </style>
  <script>
    function onSubmitForm() {
      const btn = document.getElementById('convert-btn');
      const spinner = document.getElementById('spinner');
      btn.disabled = true;
      spinner.style.display = 'block';
    }
  </script>
</head>
<body>
  <div class="container">
    <h1>🎥 Convertisseur vidéo vers AVI<br>Spécial LatisPro</h1>

    <div class="info">
      <strong>Formats acceptés :</strong> .mp4, .mov, .wmv, .avi, .mkv, .webm, etc.<br>
      <strong>Durée maximale :</strong> ~ 60 s (au-delà, la conversion peut échouer).<br>
      <strong>Profil de sortie :</strong> AVI MJPEG (MJPG) 1280×720, 25 ips, audio PCM stéréo 48 kHz.<br>
      <strong>Objectif :</strong> compatibilité maximale avec LatisPro pour le pointage.
    </div>

    <form method="post" enctype="multipart/form-data" onsubmit="onSubmitForm()">
      <label for="video">Déposez une vidéo :</label><br>
      <input type="file" name="video" id="video" accept="video/*" required><br><br>
      <button type="submit" id="convert-btn">Lancer la conversion</button>
      <div id="spinner" class="spinner">Conversion en cours… Patientez.</div>
    </form>

    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}

    {% if download_id %}
      <div class="success">
        ✅ Conversion terminée.<br>
        <a href="{{ url_for('download', file_id=download_id) }}">⬇️ Télécharger le fichier AVI</a>
      </div>
    {% endif %}

    <div class="footer">
      Virginie Fourcassier – Lycée Pierre de Fermat – Toulouse
    </div>
  </div>
</body>
</html>
"""


def convert_to_avi(input_path: str, output_path: str) -> bool:
  """
  Profil calé sur la vidéo qui fonctionne dans LatisPro :
  - Vidéo : Motion JPEG (MJPG), 1280x720, 25 fps
  - Audio : PCM (araw), stéréo, 48000 Hz, 16 bits
  """
  cmd = [
      "ffmpeg",
      "-y",
      "-i",
      input_path,
      "-t",
      "60",                # couper à 60 s max
      # Vidéo
      "-vcodec",
      "mjpeg",             # Motion JPEG (MJPG)
      "-q:v",
      "3",                 # qualité correcte (~200 kb/s comme ton exemple)
      "-r",
      "25",                # 25 ips
      "-vf",
      "scale='min(1280,iw)':-1,scale=1280:720",  # max 1280 de large, puis forcer 1280x720
      # Audio
      "-acodec",
      "pcm_s16le",         # PCM linéaire 16 bits (araw dans VLC)
      "-ac",
      "2",                 # stéréo
      "-ar",
      "48000",             # 48 kHz
      output_path,
  ]
  try:
      subprocess.run(cmd, check=True, timeout=120)
      return os.path.exists(output_path)
  except Exception as e:
      print("Erreur FFmpeg :", e)
      return False


@app.route("/", methods=["GET", "POST"])
def index():
  error = None
  download_id = None

  if request.method == "POST":
      file = request.files.get("video")
      if not file:
          error = "Aucun fichier reçu."
      else:
          # dossier temporaire par conversion
          tmp_id = str(uuid.uuid4())
          tmp_dir = os.path.join("tmp", tmp_id)
          os.makedirs(tmp_dir, exist_ok=True)

          src_path = os.path.join(tmp_dir, "video_entree")
          file.save(src_path)

          out_path = os.path.join(tmp_dir, "video_pour_latispro.avi")

          ok = convert_to_avi(src_path, out_path)
          if not ok:
              error = "La conversion a échoué. Vérifiez que la vidéo dure moins de 60 s."
              shutil.rmtree(tmp_dir, ignore_errors=True)
          else:
              # on redirige vers GET avec un identifiant de téléchargement
              return redirect(url_for("index", file_id=tmp_id))

  # cas GET : on regarde si un fichier est prêt à être téléchargé
  file_id = request.args.get("file_id")
  if file_id:
      tmp_dir = os.path.join("tmp", file_id)
      out_path = os.path.join(tmp_dir, "video_pour_latispro.avi")
      if os.path.exists(out_path):
          download_id = file_id
      else:
          # si pour une raison quelconque le fichier n'existe plus
          shutil.rmtree(tmp_dir, ignore_errors=True)

  return render_template_string(HTML_PAGE, error=error, download_id=download_id)


@app.route("/download/<file_id>")
def download(file_id: str):
  tmp_dir = os.path.join("tmp", file_id)
  out_path = os.path.join(tmp_dir, "video_pour_latispro.avi")
  if not os.path.exists(out_path):
    return "Fichier introuvable ou déjà supprimé.", 404

  # on renvoie le fichier puis on pourra nettoyer manuellement les dossiers tmp si besoin
  return send_file(out_path, as_attachment=True, download_name="video_pour_latispro.avi")


if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
