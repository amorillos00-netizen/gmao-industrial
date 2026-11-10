# -*- coding: utf-8 -*-
with open('index.html', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'// Ocultar modal de login de forma infalible', text)
if m:
    pos = m.start()
    print(text[pos:pos+2500])
