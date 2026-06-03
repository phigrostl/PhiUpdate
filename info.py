import json
import os
import sys
from UnityPy import Environment
import zipfile
import xml.etree.ElementTree as ET

DEBUG = False

Songs = []
Chapters = []

def get_song_name(song_id):
    for songs in Songs:
        for song in songs:
            if song["songsId"] == song_id:
                return song["songsName"]
    return "UK"

def get_song_chapter_name(song_id):
    for chapter in Chapters:
        for song in chapter["songInfo"]["songs"]:
            if song["songsId"] == song_id:
                return chapter["songInfo"]["title"]
    return "UK"


def run(path):
    with open("typetree.json") as f:
        typetree = json.load(f)
    env = Environment()
    with zipfile.ZipFile(path) as apk:
        with apk.open("assets/bin/Data/globalgamemanagers.assets") as f:
            env.load_file(f.read(), name="assets/bin/Data/globalgamemanagers.assets")
        with apk.open("assets/bin/Data/level0") as f:
            env.load_file(f.read())

    # 初始化为 None，防止变量未定义
    GameInformation = None
    Collections = None
    Tips = None

    # 由于 obj.read() 默认 typetree 不匹配部分 MonoBehaviour，
    # 改为直接尝试每个自定义 typetree，用特有字段判断脚本类型
    # 注意：不传 as_dict=True，read_typetree 返回的就是 dict
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        for tree_name in ("GameInformation", "GetCollectionControl", "TipsProvider"):
            try:
                result = obj.read_typetree(typetree[tree_name])
                if tree_name == "GameInformation" and GameInformation is None and "song" in result:
                    GameInformation = result
                elif tree_name == "GetCollectionControl" and Collections is None and "collectionItems" in result:
                    Collections = result
                elif tree_name == "TipsProvider" and Tips is None and "tips" in result:
                    Tips = result
            except Exception as e:
                if DEBUG:
                    print(f"  {tree_name}: {type(e).__name__}: {e}")
                continue

    if GameInformation is None:
        print("错误：未找到 GameInformation！")
        return

    difficulty = []
    table = []
    for key, songs in GameInformation["song"].items():
        for song in songs:
            if len(song["difficulty"]) == 5:
                song["difficulty"].pop()
            if song["difficulty"][-1] == 0.0:
                song["difficulty"].pop()
                song["charter"].pop()
            for i in range(len(song["difficulty"])):
                song["difficulty"][i] = str(round(song["difficulty"][i], 1))
            difficulty.append([song["songsId"]]+song["difficulty"])
            table.append((song["songsId"], song["songsName"], song["composer"], song["illustrator"], *song["charter"]))
        Songs.append(songs)

    with open("info/difficulty.tsv", "w", encoding="utf8") as f:
        for item in difficulty:
            f.write("\t".join(map(str, item)))
            f.write("\n")

    with open("info/info.tsv", "w", encoding="utf8") as f:
        for item in table:
            f.write("\t".join(map(str, item)))
            f.write("\n")

    single = []
    illustration = []
    for key in GameInformation["keyStore"]:
        if key["kindOfKey"] == 0:
            single.append(key["keyName"])
        elif key["kindOfKey"] == 2 and key["keyName"] != "Introduction" and key["keyName"] not in single:
            illustration.append(key["keyName"])

    with open("info/songs.txt", "w", encoding="utf8") as f:
        for item in table:
            f.write("%s" % item[0])
            f.write("\n")

    # 处理 Collections 数据
    if Collections is not None:
        D = {}
        for item in Collections["collectionItems"]:
            try:
                key = item["key"]
                title = item["multiLanguageTitle"]["chinese"]
                if key in D:
                    D[key][1] = item["subIndex"]
                else:
                    D[key] = [title, item["subIndex"]]
            except Exception as e:
                if DEBUG:
                    print(f"跳过无法处理的 collection item: {e}")
                continue

        with open("info/collection.tsv", "w", encoding="utf8") as f:
            for key, value in D.items():
                f.write("%s\t%s\t%s\n" % (key, value[0], value[1]))

        with open("info/avatar.txt", "w", encoding="utf8") as avatar:
            with open("info/tmp.tsv", "w", encoding="utf8") as tmp:
                for item in Collections["avatars"]:
                    try:
                        avatar.write(item["name"])
                        avatar.write("\n")
                        tmp.write("%s\t%s\n" % (item["name"], item["addressableKey"][7:]))
                    except Exception as e:
                        if DEBUG:
                            print(f"跳过无法处理的 avatar: {e}")
                        continue
    else:
        print("警告：未找到 GetCollectionControl，collection.tsv / avatar.txt / tmp.tsv 将为空")

    if Tips is not None:
        with open("info/tips.txt", "w", encoding="utf8") as f:
            tips_list = Tips["tips"]
            if isinstance(tips_list, list) and len(tips_list) > 0 and "tips" in tips_list[0]:
                for tip in tips_list[0]["tips"]:
                    f.write(tip)
                    f.write("\n")
    else:
        print("警告：未找到 TipsProvider，tips.txt 将为空")

    chaptersStr = ""
    for chapter in GameInformation["chapters"]:
        Chapters.append(chapter)

    for chapter in Chapters:
        chaptersStr += f"\n*{chapter['songInfo']['banner']}\n"
        for song in chapter["songInfo"]["songs"]:
            song_name = get_song_name(song["songsId"])
            chaptersStr += f"{song_name}\n"

    with open("info/chapter.txt", "w", encoding="utf8") as f:
        f.write(chaptersStr)

    # 提取 APK 版本信息
    try:
        import apkutils
        apk = apkutils.APK.from_file(path)
        manifest_xml_str = apk.get_manifest()

        if manifest_xml_str:
            root = ET.fromstring(manifest_xml_str)
            android_ns = {"android": "http://schemas.android.com/apk/res/android"}
            package_name = root.get("package", "NULL")

            version_name = root.get("android:versionName", "NULL")
            if version_name == "NULL":
                version_name = root.get("{" + android_ns["android"] + "}versionName", "NULL")

            version_code = root.get("android:versionCode", "NULL")
            if version_code == "NULL":
                version_code = root.get("{" + android_ns["android"] + "}versionCode", "NULL")

            with open("info/version.tsv", "w", encoding="utf8") as f:
                f.write(f"{package_name}\t{version_name}\t{version_code}\n")

    except ImportError:
        print("警告：apkutils 未安装，version.tsv 将为空。安装方法：pip install apkutils")
    except Exception as e:
        print(f"警告：提取版本信息失败: {e}")

if __name__ == "__main__":
    if len(sys.argv) == 1:
        path = input("\n输入apk路径：")
    else:
        path = sys.argv[1]
    if not os.path.isdir("info"):
        os.mkdir("info")
    run(path)
