# Inject timing.json into the template -> index.html
import json, sys
T = json.load(open(sys.argv[1]))
s = open("templates/index.html.tmpl").read().replace("/*TIMING*/", json.dumps(T)).replace("__END__", str(T["end"]))
open("index.html", "w").write(s)
print("index.html built, duration", T["end"])
