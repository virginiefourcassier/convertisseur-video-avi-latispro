def convert_to_avi(input_path: str, output_path: str) -> bool:
  # Conversion stricte pour LatisPro : AVI MJPEG, 25 ips, sans son
  cmd = [
      "ffmpeg",
      "-y",
      "-i", input_path,
      "-t", "60",           # coupe proprement au cas où (ta vidéo fait 2 s, donc ok)
      "-an",                # supprime totalement la piste audio
      "-vcodec", "mjpeg",   # vidéo en MJPEG
      "-q:v", "2",          # qualité élevée (2 = très bon)
      "-pix_fmt", "yuvj422p",  # format de pixels classique pour MJPEG
      "-r", "25",           # 25 images/s
      "-vf", "scale=iw:ih", # conserve la taille, pas de redimensionnement compliqué
      output_path,
  ]
  try:
      subprocess.run(cmd, check=True, timeout=120)
      return os.path.exists(output_path)
  except Exception as e:
      print("Erreur FFmpeg :", e)
      return False
