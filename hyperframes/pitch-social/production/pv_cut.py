import json, subprocess, sys, os
T = json.load(open(sys.argv[1])); SRC = sys.argv[2]; OUT = sys.argv[3]
os.makedirs("segs", exist_ok=True); lst = []
for i, s in enumerate(T["segs"]):
    f = f"segs/s{i:02d}.mp4"; lst.append(f"file '{f}'")
    vf = (f"setpts=(PTS-STARTPTS)/{s['speed']},fps=30,scale=660:1434:flags=lanczos,"
          f"tpad=stop_mode=clone:stop_duration=4,trim=duration={s['dur']},setpts=PTS-STARTPTS,format=yuv420p")
    subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(s["in"]), "-to", str(s["out"]), "-i", SRC, "-vf", vf, "-an",
                    "-c:v", "libx264", "-crf", "15", "-preset", "medium", "-r", "30", "-g", "15", "-threads", "2", f], check=True)
open("segs/list.txt", "w").write("\n".join(lst).replace("segs/", ""))
subprocess.run(["ffmpeg", "-v", "error", "-y", "-f", "concat", "-safe", "0", "-i", "segs/list.txt", "-c", "copy", "-movflags", "+faststart", OUT], check=True)
