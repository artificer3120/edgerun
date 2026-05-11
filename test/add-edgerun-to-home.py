#!/usr/bin/env python3
"""Insert edgerun entry into neonforge home.html tools section."""
import time, shutil

p = "/home/ubuntu/neonforge/pages/home.html"
shutil.copy(p, p + ".bak." + str(int(time.time())))
src = open(p).read()

src = src.replace(
    '<h2 class="cat-h">tools <span class="cat-n">7</span></h2>',
    '<h2 class="cat-h">tools <span class="cat-n">8</span></h2>',
)
src = src.replace(
    '<span id="visible-count">45</span> / 45 pages',
    '<span id="visible-count">46</span> / 46 pages',
)

needle = '''<a class="pg" href="?p=terminal">
  <div class="pg-t">terminal</div>
  <div class="pg-d">terminal mockup</div>
</a>'''
insert = needle + '''
<a class="pg" href="?p=edgerun">
  <div class="pg-t">edgerun mesh</div>
  <div class="pg-d">physical sensor map — drag to grab, release to float</div>
</a>'''

if needle in src:
    src = src.replace(needle, insert)
    open(p, "w").write(src)
    print("inserted edgerun in tools section")
else:
    print("WARN: insertion needle not found")
