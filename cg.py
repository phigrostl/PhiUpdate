import json
import os
import sys
from UnityPy import Environment
import zipfile

DEBUG = False

def run(path):
    with zipfile.ZipFile(path) as apk:
        os.makedirs("APK/lib/armeabi-v7a", exist_ok=True)
        os.makedirs("APK/assets/bin/Data/Managed/Metadata", exist_ok=True)
        apk.extract("lib/armeabi-v7a/libil2cpp.so", "APK/")
        apk.extract("assets/bin/Data/Managed/Metadata/global-metadata.dat", "APK/")
        print(os.system(".\\TypeTreeGeneratorCLI\\Il2CppDumper\\Il2CppDumper.exe APK/lib/armeabi-v7a/libil2cpp.so APK/assets/bin/Data/Managed/Metadata/global-metadata.dat ./TypeTreeGeneratorCLI/Il2CppDumper/"))
        print(os.system(".\\TypeTreeGeneratorCLI\\TypeTreeGeneratorCLI.exe -p ./TypeTreeGeneratorCLI/Il2CppDumper/DummyDll -a \"Assembly-CSharp.dll\" -v \"2022\" -o ./typetree.json -d json"))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        path = input("输入apk路径：")
    else:
        path = sys.argv[1]
    run(path)
