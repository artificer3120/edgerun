#!/usr/bin/env python3
"""
Restructure neonforge home to:
- move edgerun (now docs) out of tools, into docs section
- add edgerun-app (the live viewer) into tools where edgerun used to be
- bump counts: docs 5->6, tools 8->8 (still 8: edgerun replaced by edgerun-app), total 46->47
"""
import time, shutil

p = "/home/ubuntu/neonforge/pages/home.html"
shutil.copy(p, p + ".bak." + str(int(time.time())))
src = open(p).read()

# 1) Replace the existing edgerun-in-tools entry with edgerun-app
old_tools_entry = '''<a class="pg" href="?p=edgerun">
  <div class="pg-t">edgerun mesh</div>
  <div class="pg-d">physical sensor map — drag to grab, release to float</div>
</a>'''
new_tools_entry = '''<a class="pg" href="?p=edgerun-app">
  <div class="pg-t">edgerun — viewer</div>
  <div class="pg-d">the live d3-force viewer · drag, release, layer-toggle</div>
</a>'''
assert old_tools_entry in src, "old tools entry not found"
src = src.replace(old_tools_entry, new_tools_entry)

# 2) Insert edgerun (the doc) into docs section, before tunneltime
docs_anchor = '''<a class="pg" href="?p=tunneltime-2026-05-07">
  <div class="pg-t">tunneltime hub — 2026-05-07</div>
  <div class="pg-d">documentation hub for the radix widget series</div>
</a>'''
docs_insert = '''<a class="pg" href="?p=edgerun">
  <div class="pg-t">edgerun mesh</div>
  <div class="pg-d">physical sensor recon · spec + live embed</div>
</a>
''' + docs_anchor
assert docs_anchor in src, "docs anchor not found"
src = src.replace(docs_anchor, docs_insert)

# 3) bump docs count 5 -> 6
src = src.replace(
    '<h2 class="cat-h">docs <span class="cat-n">5</span></h2>',
    '<h2 class="cat-h">docs <span class="cat-n">6</span></h2>',
)

# 4) bump total counter 46 -> 47
src = src.replace(
    '<span id="visible-count">46</span> / 46 pages',
    '<span id="visible-count">47</span> / 47 pages',
)

open(p, "w").write(src)
print("home.html restructured: edgerun(docs)+edgerun-app(tools)")
