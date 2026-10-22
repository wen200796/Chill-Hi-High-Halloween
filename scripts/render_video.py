"""Render every frame of scene.py into a near-lossless silent master.

Output: output/_build/master_video.mp4 (1080x1920, 30 fps, x264 crf 10).
"""
import subprocess
import sys
import time
from multiprocessing import Pool

import scene

OUT = scene.ROOT / "output/_build/master_video.mp4"


def frame(i):
    return scene.render_frame(i / scene.FPS).tobytes()


def main():
    n = round(scene.DURATION * scene.FPS)
    ff = subprocess.Popen([
        "ffmpeg", "-v", "error", "-y", "-f", "rawvideo", "-pix_fmt", "rgb24",
        "-s", f"{scene.W}x{scene.H}", "-r", str(scene.FPS), "-i", "-",
        "-c:v", "libx264", "-preset", "medium", "-crf", "10", "-pix_fmt", "yuv420p", str(OUT),
    ], stdin=subprocess.PIPE)
    t0 = time.time()
    with Pool(4) as pool:
        for i, buf in enumerate(pool.imap(frame, range(n), chunksize=4)):
            ff.stdin.write(buf)
            if i % 60 == 0:
                print(f"frame {i}/{n}  {time.time() - t0:.0f}s", flush=True)
    ff.stdin.close()
    sys.exit(ff.wait())


if __name__ == "__main__":
    main()
