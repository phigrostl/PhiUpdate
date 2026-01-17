import os
import sys

levels = ["EZ", "HD", "IN", "AT"]

filter = []
if sys.argv.__len__() > 2:
    filter = sys.argv[2:]
def in_filter(key):
    global filter
    if filter.__len__() == 0:
        return True
    for f in filter:
        if f in key:
            return True
    return False

infos = {}
try:
    with open("info/info.tsv", encoding="utf8") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line[:-1].split("\t")
            infos[line[0]] = {
                "Name": line[1],
                "Composer": line[2],
                "Illustrator": line[3],
                "Chater": line[4:]
            }
except FileNotFoundError:
    print("错误：未找到 info.tsv 文件。请检查 info 目录是否存在且包含该文件。")
    exit(1)
except Exception as e:
    print(f"错误：读取 info.tsv 时出错 - {e}")
    exit(1)

try:
    with open("info/difficulty.tsv", encoding="utf8") as f:
        while True:
            line = f.readline()
            if not line:
                break
            line = line[:-1].split("\t")
            if line[0] in infos:
                infos[line[0]]["difficulty"] = line[1:]
            else:
                print(f"警告：difficulty.tsv 中的 ID {line[0]} 在 info.tsv 中未找到。")
except FileNotFoundError:
    print("错误：未找到 difficulty.tsv 文件。请检查 info 目录是否存在且包含该文件。")
    exit(1)
except Exception as e:
    print(f"错误：读取 difficulty.tsv 时出错 - {e}")
    exit(1)

infos['Introduction']['difficulty'].pop()
infos['Introduction']['difficulty'].pop()

for id, info in infos.items():
    try:
        if not in_filter(f"{info['Name']}.{info['Composer']}.0"):
            continue
        str = f"正在处理：{info['Name']}:{info['Composer']}"
        print("\r\033[K", end="")
        print(str, end='\r')
        out_dir = f"chart/{id}"
            
        for level_index in range(len(info.get("difficulty", []))):
            level = levels[level_index]
            os.makedirs(out_dir, exist_ok=True)
            info_txt_content = (
                f"#\n"
                f"Name: {info['Name']}\n"
                f"Song: music.wav\n"
                f"Picture: illustration.png\n"
                f"Chart: {level}.json\n"
                f"Level: {level} Lv.{info['difficulty'][level_index]}\n"
                f"Composer: {info['Composer']}\n"
                f"Illustrator: {info['Illustrator']}\n"
                f"Charter: {info['Chater'][level_index]}\n"
            )
            with open(os.path.join(out_dir, f"{level}.txt"), "w", encoding="utf8") as f:
                f.write(info_txt_content)
                
    except KeyError as e:
        print(f"错误：ID {id} 缺少必要的键 {e}。")
    except Exception as e:
        print(f"意外错误：处理 ID {id} 时发生错误 - {e}")
print("\r\033[K", end="")
