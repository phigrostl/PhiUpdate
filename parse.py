import base64
from concurrent.futures import ThreadPoolExecutor, wait
from configparser import ConfigParser
from io import BytesIO
import json
import os
from queue import Queue
import sys
import threading
import time
from UnityPy import Environment
from UnityPy.classes import AudioClip
from UnityPy.enums import ClassIDType
from zipfile import ZipFile
from tqdm import tqdm

class ByteReader:
    def __init__(self, data):
        self.data = data
        self.position = 0

    def readInt(self):
        self.position += 4
        return self.data[self.position - 4] ^ self.data[self.position - 3] << 8 ^ self.data[self.position - 2] << 16

queue_out = Queue()
queue_in = Queue()
progress_bar = None
write_num = 0

filter = []
def in_filter(key):
    global filter
    if filter.__len__() == 0:
        return True
    for f in filter:
        if f in key:
            return True
    return False

def io():
    global progress_bar
    while True:
        item = queue_in.get()
        if item is None:
            break
        else:
            path, resource = item
            if isinstance(resource, BytesIO):
                with resource:
                    with open(path, "wb") as f:
                        f.write(resource.getbuffer())
            else:
                with open(path, "wb") as f:
                    if isinstance(resource, bytes):
                        f.write(resource)
                    else:
                        f.write(str(resource).encode('utf-8'))
            if progress_bar:
                progress_bar.update(1)

def save_image(path, image):
    bytesIO = BytesIO()
    image.save(bytesIO, "png")
    queue_in.put((path, bytesIO))

def save_music(path, music: AudioClip):
    sample_data = next(iter(music.samples.values()))
    queue_in.put((path, sample_data))

def save_chart(path, obj):
    content = obj.text if isinstance(obj.text, bytes) else obj.text.encode("utf-8")
    queue_in.put((path, content))

classes = ClassIDType.TextAsset, ClassIDType.Sprite, ClassIDType.AudioClip

def save(key, entry, futures):
    global write_num, pool, config
    obj = entry.get_filtered_objects(classes)
    obj = next(obj).read()
    folder_name = key.rsplit("/", 1)[0]

    base_folder = "chart"
    out_folder = os.path.join(base_folder, folder_name)
    if not key[:7] == "avatar.":
        os.makedirs(out_folder, exist_ok=True)

    if config["avatar"] and key[:7] == "avatar." and in_filter(key):
        futures.append(pool.submit(save_image, os.path.join("avatar", f"{key[7:]}.png"), obj.image))
        write_num += 1
    elif config["chart"] and key[-14:-7] == "/Chart_" and key[-5:] == ".json" and in_filter(key):
        futures.append(pool.submit(save_chart, os.path.join(out_folder, f"{key[-7:-5]}.json"), obj))
        write_num += 1
    elif config["illustrationBlur"] and key[-21:-3] == "/IllustrationBlur." and in_filter(key):
        futures.append(pool.submit(save_image, os.path.join(out_folder, "illustrationBlur.png"), obj.image))
        write_num += 1
    elif config["illustrationLowRes"] and key[-23:-3] == "/IllustrationLowRes." and in_filter(key):
        futures.append(pool.submit(save_image, os.path.join(out_folder, "illustrationLowres.png"), obj.image))
        write_num += 1
    elif config["illustration"] and key[-17:-3] == "/Illustration." and in_filter(key):
        futures.append(pool.submit(save_image, os.path.join(out_folder, "illustration.png"), obj.image))
        write_num += 1
    elif config["music"] and key[-10:] == "/music.wav" and in_filter(key):
        futures.append(pool.submit(save_music, os.path.join(out_folder, "music.wav"), obj))
        write_num += 1

def run(path):
    global progress_bar
    with ZipFile(path) as apk:
        with apk.open("assets/aa/catalog.json") as f:
            data = json.load(f)

    key = base64.b64decode(data["m_KeyDataString"])
    bucket = base64.b64decode(data["m_BucketDataString"])
    entry = base64.b64decode(data["m_EntryDataString"])

    table = []
    reader = ByteReader(bucket)
    for x in range(reader.readInt()):
        key_position = reader.readInt()
        key_type = key[key_position]
        key_position += 1
        if key_type == 0:
            length = key[key_position]
            key_position += 4
            key_value = key[key_position:key_position + length].decode()
        elif key_type == 1:
            length = key[key_position]
            key_position += 4
            key_value = key[key_position:key_position + length].decode("utf16")
        elif key_type == 4:
            key_value = key[key_position]
        else:
            raise BaseException(key_position, key_type)
        for i in range(reader.readInt()):
            entry_position = reader.readInt()
            entry_value = entry[4 + 28 * entry_position:4 + 28 * entry_position + 28]
            entry_value = entry_value[8] ^ entry_value[9] << 8
        table.append([key_value, entry_value])
    for i in range(len(table)):
        if table[i][1] != 65535:
            table[i][1] = table[table[i][1]][0]
    for i in range(len(table) - 1, -1, -1):
        if type(table[i][0]) == int or table[i][0][:15] == "Assets/Tracks/#" or table[i][0][:14] != "Assets/Tracks/" and \
                table[i][0][:7] != "avatar.":
            del table[i]
        elif table[i][0][:14] == "Assets/Tracks/":
            table[i][0] = table[i][0][14:]

    global avatar
    if config["avatar"]:
        avatar = {}
        if os.path.exists("info/tmp.tsv"):
            with open("info/tmp.tsv",encoding="utf8") as f:
                line = f.readline()[:-1]
                while line:
                    l = line.split("\t")
                    avatar[l[1]] = l[0]
                    line = f.readline()[:-1]

    file_count = table.__len__()
    progress_bar = tqdm(total=file_count, desc="写入文件", ncols=100)

    thread = threading.Thread(target=io)
    thread.start()
    ti = time.time()
    global pool
    with ThreadPoolExecutor(6) as pool:
        futures = []
        i = 0
        with ZipFile(path) as apk:
            for key, entry in tqdm(table, desc="处理资源", ncols=100):
                env = Environment()
                env.load_file(apk.read("assets/aa/Android/%s" % entry), name=key)
                files_iter = env.files.items()
                i += 1
                for ikey, ientry in files_iter:
                    save(ikey, ientry, futures)
                    progress_bar.total = int(write_num / (i / file_count))
                    progress_bar.refresh()
        wait(futures)

    queue_in.put(None)
    thread.join()
    progress_bar.close()
    tqdm.write("%f秒" % round(time.time() - ti, 4))

if __name__ == "__main__":
    if len(sys.argv) == 1:
        path = input("输入apk路径：")
    else:
        path = sys.argv[1]
        if len(sys.argv) > 2:
            filter = sys.argv[2:]
    c = ConfigParser()
    c.read("config.ini", "utf8")
    types = c["TYPES"]
    config = {
        "avatar": types.getboolean("avatar"),
        "chart": types.getboolean("Chart"),
        "illustrationBlur": types.getboolean("IllustrationBlur"),
        "illustrationLowRes": types.getboolean("IllustrationLowRes"),
        "illustration": types.getboolean("Illustration"),
        "music": types.getboolean("music")
    }
    type_list = ("avatar", "chart", "illustrationBlur", "illustrationLowRes", "illustration", "music")
    os.makedirs("chart", exist_ok=True)
    os.makedirs("avatar", exist_ok=True)
    for directory in type_list:
        if not config[directory]:
            continue
        if os.path.isdir("/system/") and not os.getcwd().startswith("/data/"):
            with open(directory + "/.nomedia", "wb"):
                pass
    run(path)
