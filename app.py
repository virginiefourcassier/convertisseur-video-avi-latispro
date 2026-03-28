def convert_to_avi(input_path: str, output_path: str) -> bool:
  # AVI "old school" pour LatisPro : MJPEG, 25 ips, 1280x720 max, sans son
  cmd = [
      "ffmpeg",
      "-y",
      "-i", input_path,
      "-t", "60",                 # sécurité : coupe à 60 s max
      "-an",                      # pas de piste audio
      "-vcodec", "mjpeg",         # codec vidéo MJPEG
      "-q:v", "3",                # qualité bonne (3)
      "-pix_fmt", "yuvj422p",     # format de pixels classique
      "-r", "25",                 # 25 images par seconde
      "-vf", "scale='min(1280,iw)':-1,scale=trunc(iw/2)*2:trunc(ih/2)*2",
      output_path,
  ]
  try:
      subprocess.run(cmd, check=True, timeout=120)
      return os.path.exists(output_path)
  except Exception as e:
      print("Erreur FFmpeg :", e)
      return False
