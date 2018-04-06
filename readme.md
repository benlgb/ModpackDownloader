## Minecraft Curseforge 整合包下载器

-   环境：Python 3.6
-   使用方法：

```cmd
python ModpackDownloader projectID [fileID]
```

-   例子：

```
python ModpackDownloader 286377 2546758

# 省略fileID，默认查找最新ID
python ModpackDownloader 286377

# 用整合包名字代替（注意格式）
python ModpackDownloader modern-skyblock-3-departed
```

-   注意事项：
    -   下载完成后整合包位置在`./cache/[modpack_name]/overrides`文件夹中，请将文件夹内所有文件都复制到`.minecraft`文件夹中（覆盖）
    -   若下载完成后出现以下提示文字，说明存在有模组缺失，请根据链接补全相关模组到`./cache/[modpack_name]/overrides/mods`文件夹中