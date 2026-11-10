# -*- coding: utf-8 -*-
with open('index.html', encoding='utf-8') as f:
    text = f.read()

import re
m = re.search(r'document\.getElementById\([\'\"]loginForm[\'\"]\)\.addEventListener', text)
if m:
    pos = m.start()
    print(text[pos:pos+2500])
