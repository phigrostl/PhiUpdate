import os
import sys

filter = []

if len(sys.argv) == 1:
    path = input("输入apk路径：")
else:
    path = sys.argv[1]
    if len(sys.argv) > 2:
        filter = sys.argv[2:]

print(os.system(f"py cg.py {path}"))
print(os.system(f"py info.py {path}"))
print(os.system(f"py parse.py {path} {' '.join(filter)}"))
