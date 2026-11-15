import glob, json, os

files = glob.glob("data/raw/meta_*.json")
groups = {}
for f in files:
    try:
        with open(f, "r", encoding="utf-8") as fp:
            m = json.load(fp)
            c = m["config"]
            tag = c.get("tag") or f"L{c['load']:g}W{c['workers']}"
            k = (c["policy"], c["scenario"], tag)
            groups.setdefault(k, []).append(c.get("run", 0))
    except Exception as e:
        print("Error reading", f, e)

print(f"{'Policy':<8} {'Scn':<5} {'Tag':<15} {'Count':<6} {'Runs'}")
print("-" * 55)
for k in sorted(groups):
    runs = sorted(groups[k])
    print(f"{k[0]:<8} {k[1]:<5} {k[2]:<15} {len(runs):<6} {runs}")
