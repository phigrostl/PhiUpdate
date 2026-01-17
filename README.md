# PhiUpdate

> `Phigros` 解包工具，用于快速获取 `Phigros` 的更新内容 <br> 本工具仅用于学习交流，请勿用于商业用途

## 使用方法

> 可直接在本仓库的代码文件夹下下载谱面文件，若想获取音乐等其他内容，请按照以下步骤操作

## 安装依赖项

 - 下载并解压本仓库

 - [TypeTreeGeneratorCLI](https://github.com/K0lb3/TypeTreeGenerator/releases/latest)
 - [Il2CppDumper](https://github.com/Perfare/Il2CppDumper/releases/latest)
 - [libvorbis.dll](https://xiph.org/downloads/)

```shell
pip install -r requirements.txt
```

## 可选提取内容

#### 在 `config.ini` 中配置
```ini
avatar = true               # 提取头像
chart = true                # 提取谱面
illustration = true         # 提取曲绘
illustrationblur = false    # 提取模糊曲绘
illustrationlowres = false  # 提取低分辨率曲绘
music = false               # 提取音乐
```

## 脚本说明

### main.py
`main.py` 整合了 `cg.py`, `info.py`, `parse.py`, `phira.py` 四个脚本
其中
- `cg.py` : 解包安装包
- `info.py` : 获取曲目信息
- `parse.py` : 解析曲目

``` bash
py main.py <Path> [Filter...]
```

- `Path` : `Phigros` 安装包路径
- `Filter` : 指定需要提取的曲目关键词

> 可根据需要以运行以上任意脚本

### phira.py
`phira.py` 将解析后的曲目转换为 `Phira` 可导入格式

``` bash
py phira.py [Filter...]
```

- `Filter` : 指定需要提取的曲目关键词

### 目录结构
``` dir
┌───────
├── info
│   ├── songs.txt 		    // 歌曲ID列表
│   ├── chapter.txt         // 按章节分隔的歌曲列表
│   ├── difficulty.tsv 	    // 难度列表
│   ├── info.tsv 		    // 信息列表 - ID 名称 曲师 画师 谱师
│   ├── avatar.txt 		    // 头像列表
│   ├── collection.tsv 	    // 收藏品
│   ├── tips.txt		    // Tips: Tips: Tips: Tips: Tips:
│   ├── tmp.tsv		        // 歌曲与头像的对应关系
├── chart
│   ├── <ID>
│   ├── ├── <难度>.json     // 谱面数据
│   ├── ├── illustration 	// 曲绘
│   ├── ├── music.wav	    // 音乐
│   ├── ├── <难度>.txt 	    // 更改为 info.txt 且加入 Path 键后压缩为 zip 可导入至 Phira
│   ├── <ID...>
│   ├── ...
├── avatar
│   ├── <ID>.png		    // 头像
│   ├── <ID...>.png
│   ├── ...
```

## Star History

[![Star History Chart](https://api.star-history.com/svg?repos=phigrostl/PhiUpdate&type=date&legend=top-left)](https://www.star-history.com/#phigrostl/PhiUpdate&type=date&legend=top-left)
