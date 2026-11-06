import json, sys
T = json.load(open(sys.argv[1]))
b0 = T["segs"][0]["t"]; bd = round(T["segs"][-1]["t"] + T["segs"][-1]["dur"] - b0, 4)
s = (open("templates/index.html.tmpl").read().replace("/*TIMING*/", json.dumps(T)).replace("__END__", str(T["end"]))
     .replace("__B0__", str(b0)).replace("__BDUR__", str(bd)))
open("index.html", "w").write(s)
