from flask import Flask, render_template_string, request, send_file
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
    input[type=file] { margin: 12px 0; }
    .error { color: #c62828; margin-top: 12px; }
    .success { color: #2e7d32; margin-top: 12px; }
  </style>
</head>
<body>
  <div class="container">
    <h1>🎥 Convertisseur vidéo vers AVI<br>Spécial LatisPro</h1>

    <div class="info">
      <strong>Formats acceptés :</strong> .mp4, .mov, .wmv, .avi, .mkv, .webm, etc.<br>
      <strong>Durée maximale :</strong> ~ 60 s (au-delà, la conversion peut échouer).<br>
      <strong>Son :</strong> supprimé.<br>
      <strong>Objectif :</strong> produire un AVI MJPEG 25 ips compatible LatisPro.
    </div>

    <form method="post" enctype="multipart/form-data">
      <label for="video">Déposez une vidéo :</label><br>
      <input type="file" name="video" id="video" accept="video/*" required><br><br>
      <button type="submit">Lancer la conversion</button>
    </form>

    {% if error %}
      <div class="error">{{ error }}</div>
    {% endif %}

    {% if download_url %}
      <div class="success">
        ✅ Conversion terminée.<br>
        <a href="{{ download_url }}">⬇️ Télécharger le fichier AVI</a>
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
  cmd = [
      "ffmpeg",
      "-y",
      "-i", input_path,
      "-t", "60",
      "-an",
      "-vcodec", "mjpeg",
      "-q:v", "3",
      "-pix_fmt", "yuvj422p",
      "-r", "25",
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
  download_url = None

  if request.method == "POST":
      file = request.files.get("video")
      if not file:
          error = "Aucun fichier reçu."
      else:
          tmp_dir = os.path.join("tmp", str(uuid.uuid4()))
          os.makedirs(tmp_dir, exist_ok=True)
          src_path = os.path.join(tmp_dir, "video_entree")
          file.save(src_path)

          out_path = os.path.join(tmp_dir, "video_pour_latispro.avi")

          ok = convert_to_avi(src_path, out_path)
          if not ok:
              error = "La conversion a échoué. Vérifiez que la vidéo dure moins de 60 s."
              shutil.rmtree(tmp_dir, ignore_errors=True)
          else:
              # On sert directement le fichier, puis on nettoie le dossier après envoi
              return send_file(out_path, as_attachment=True, download_name="video_pour_latispro.avi")

  return render_template_string(HTML_PAGE, error=error, download_url=download_url)

if __name__ == "__main__":
  app.run(host="0.0.0.0", port=8000)
