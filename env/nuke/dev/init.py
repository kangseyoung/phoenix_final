"""
이 스크립트에는 뉴크 실행시 사전에 설정해야하는
스크립트나 플러그인, 기즈모들을 참조하는 스크립트가 작성되면 좋아요.
"""

print("*" *30)
print("init.py")
print("이니셜라이즈 스크립트가 실행됨")
print("*" *30)

import nuke
import sys
sys.path.append("/home/rapa/_phoenix_/env/nuke/dev/python")

nuke.pluginAddPath("./gizmo")
nuke.pluginAddPath("./icons")
nuke.pluginAddPath("./lib/python3.9/site-packages")
nuke.pluginAddPath("/home/rapa/_phoenix_/env/nuke/dev/lib/python3.9/site-packages")

nuke.pluginAddPath("./lut")
nuke.pluginAddPath("./plugins")
nuke.pluginAddPath("./python")




nuke.pluginAddPath("./lib/python3.9")
