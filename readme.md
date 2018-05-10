## Minecraft Curseforge 整合包补全下载 2.0

### 一、前提

- 环境： Python 3.6
- 包：requests、aiohttp、tqdm
- 整合包文件（需提前到curseforge下载好整合包文件）


### 二、使用方法

```
python3 ModpackDownloader [Modpack File Path]
```

例子：
```
python3 ModpackDownloader.py FS+Lost+Souls-1.0.3.13-B3.zip
```

完成后将整合包文件夹内的所有文件覆盖到.minecraft文件夹中


### 三、注意事项

- 本工具只做了模组的补全
- 本工具并没有做任何的输入检测，出现错误请自行检查
