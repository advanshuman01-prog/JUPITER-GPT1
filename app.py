import os, re, uuid, subprocess, shutil
from pathlib import Path
from flask import Flask, render_template, request, send_file, flash, redirect, url_for
from werkzeug.utils import secure_filename

BASE = Path(__file__).resolve().parent
UPLOADS = BASE / "uploads"
OUTPUTS = BASE / "outputs"
UPLOADS.mkdir(exist_ok=True); OUTPUTS.mkdir(exist_ok=True)
app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "change-this-before-deploying")
app.config["MAX_CONTENT_LENGTH"] = 1500 * 1024 * 1024
ALLOWED = {".mp4", ".mov", ".mkv", ".webm"}

def run(cmd):
    p = subprocess.run(cmd, capture_output=True, text=True)
    if p.returncode:
        raise RuntimeError((p.stderr or p.stdout)[-1800:])
    return p.stdout

def duration(path):
    out = run(["ffprobe", "-v", "error", "-show_entries", "format=duration",
               "-of", "default=noprint_wrappers=1:nokey=1", str(path)])
    return float(out.strip())

def safe_name(s):
    s = re.sub(r"[^a-zA-Z0-9_-]+", "-", s).strip("-")
    return s[:48] or "jupiter-short"

def make_clips(src, count, seconds, job):
    total = duration(src)
    if total < seconds:
        seconds = max(10, int(total))
    # Starter selection: spaced segments across the source. This is not semantic/viral AI ranking.
    max_start = max(0, total - seconds)
    if count == 1:
        starts = [max_start / 2]
    else:
        starts = [max_start * i / (count - 1) for i in range(count)]
    made = []
    for i, start in enumerate(starts, 1):
        out = OUTPUTS / f"{job}_short_{i:02d}.mp4"
        vf = "scale=1080:1920:force_original_aspect_ratio=increase,crop=1080:1920"
        run(["ffmpeg", "-y", "-ss", str(start), "-i", str(src), "-t", str(seconds),
             "-vf", vf, "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
             "-c:a", "aac", "-b:a", "128k", "-movflags", "+faststart", str(out)])
        made.append({"name": out.name, "start": round(start,1), "end": round(start+seconds,1)})
    return made

@app.get("/")
def index():
    return render_template("index.html")

@app.post("/create")
def create():
    f = request.files.get("video")
    if not f or not f.filename:
        flash("कृपया अपनी वीडियो फाइल चुनें।")
        return redirect(url_for("index"))
    ext = Path(secure_filename(f.filename)).suffix.lower()
    if ext not in ALLOWED:
        flash("MP4, MOV, MKV या WEBM वीडियो अपलोड करें।")
        return redirect(url_for("index"))
    job = uuid.uuid4().hex[:10]
    src = UPLOADS / f"{job}{ext}"
    f.save(src)
    try:
        count = max(1, min(10, int(request.form.get("count", 5))))
        seconds = max(15, min(90, int(request.form.get("seconds", 45))))
        clips = make_clips(src, count, seconds, job)
        # Package generated clips for one-click retrieval.
        import zipfile
        bundle = OUTPUTS / f"{job}_JUPITER_SHORTS.zip"
        with zipfile.ZipFile(bundle, "w", zipfile.ZIP_DEFLATED) as z:
            for c in clips:
                z.write(OUTPUTS / c["name"], c["name"])
        return render_template("result.html", clips=clips, bundle=bundle.name,
                               seo=seo_for(f.filename, len(clips)))
    except Exception as e:
        flash(f"वीडियो प्रोसेस नहीं हो सकी: {e}")
        return redirect(url_for("index"))
    finally:
        try: src.unlink(missing_ok=True)
        except: pass

def seo_for(filename, n):
    base = Path(filename).stem.replace("_", " ").replace("-", " ")
    return [{"title": f"{base[:65]} | Best Moment #{i+1} #shorts",
             "description": f"Watch this short highlight from {base}. Subscribe for more. #shorts",
             "hashtags": "#shorts #youtubeShorts #viral #trending"}
            for i in range(n)]

@app.get("/download/<path:name>")
def download(name):
    p = OUTPUTS / Path(name).name
    if not p.exists(): return "File expired or not found.", 404
    return send_file(p, as_attachment=True)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
