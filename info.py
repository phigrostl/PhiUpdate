import json
import os
import sys
from UnityPy import Environment
import zipfile

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
    for obj in env.objects:
        if obj.type.name != "MonoBehaviour":
            continue
        data = obj.read()
        if data.m_Script.get_obj().read().name == "GameInformation":
            GameInformation = obj.read_typetree(typetree["GameInformation"])
        elif data.m_Script.get_obj().read().name == "GetCollectionControl":
            Collections = obj.read_typetree(typetree["GetCollectionControl"], True)
        elif data.m_Script.get_obj().read().name == "TipsProvider":
            Tips = obj.read_typetree(typetree["TipsProvider"], True)

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

    D = {}
    for item in Collections.collectionItems:
        if item.key in D:
            D[item.key][1] = item.subIndex
        else:
            D[item.key] = [item.multiLanguageTitle.chinese, item.subIndex]

    with open("info/collection.tsv", "w", encoding="utf8") as f:
        for key, value in D.items():
            f.write("%s\t%s\t%s\n" % (key, value[0], value[1]))

    with open("info/avatar.txt", "w", encoding="utf8") as avatar:
        with open("info/tmp.tsv", "w", encoding="utf8") as tmp:
            for item in Collections.avatars:
                avatar.write(item.name)
                avatar.write("\n")
                tmp.write("%s\t%s\n" % (item.name, item.addressableKey[7:]))

    with open("info/tips.txt", "w", encoding="utf8") as f:
        for tip in Tips.tips[0].tips:
            f.write(tip)
            f.write("\n")
            
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

if __name__ == "__main__":
    if len(sys.argv) == 1:
        path = input("\n输入apk路径：")
    else:
        path = sys.argv[1]
    if not os.path.isdir("info"):
        os.mkdir("info")
    run(path)
