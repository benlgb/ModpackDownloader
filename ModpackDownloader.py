#!/usr/bin/env python
# -*- coding: utf-8 -*-

# version: 2.0

import os
import sys
import json
import shutil
import aiohttp
import asyncio
import zipfile
import requests
from tqdm import tqdm
from zipfile import ZipFile

class ModpackDownloader:
	BASE_URL = 'https://minecraft.curseforge.com/projects/%d/files/%d/download'

	def __init__(self, path):
		modpack, dirname = self.extract(path)
		print('[+] start to download modpack:', modpack)

		mods = self.getModslist(dirname)

		loop = asyncio.get_event_loop()
		task = self.downloadMods(mods)
		mod_files = loop.run_until_complete(task)
		print('[+] successfully downloaded all the mods(total: %d)' % len(mods))

		self.concatFile(modpack, mod_files)

	# 整合文件
	def concatFile(self, modpack, mod_files):
		if os.path.exists(modpack):
			shutil.rmtree(modpack)
		dirname = os.path.join('cache', modpack, 'overrides')
		shutil.copytree(dirname, modpack)
		dirname = os.path.join(modpack, 'mods')
		for mod_file in mod_files:
			filename = os.path.basename(mod_file)
			path = os.path.join(dirname, filename)
			shutil.copyfile(mod_file, path)

	# 下载模组
	async def downloadMods(self, mods):
		with tqdm(total=len(mods), leave=False) as pbar:
			async with aiohttp.ClientSession() as session:
				tasks = [self.downloadMod(i, session, pbar) for i in mods]
				tasks = [asyncio.ensure_future(i) for i in tasks]
				return await asyncio.gather(*tasks, return_exceptions=True)

	async def downloadMod(self, mod_info, session, pbar):
		try:
			if not os.path.isdir('cache/mods'):
				os.makedirs('cache/mods')
			project_id = mod_info['projectID']
			file_id = mod_info['fileID']
			url = self.BASE_URL % (project_id, file_id)
			async with session.get(url, timeout=60) as res:
				filename = os.path.basename(str(res.url))
				path = os.path.join('cache/mods', filename)
				with open(path, 'wb') as f:
					f.write(await res.read())
			saying = '\r[+] successfully downloaded mod: %s' % filename
			print(saying + ' ' * (os.get_terminal_size().columns - len(saying) + 1))
			pbar.update()
			return path
		except Exception as e:
			return await self.downloadMod(mod_info)

	# 模组列表
	def getModslist(self, dirname):
		path = os.path.join(dirname, 'manifest.json')
		with open(path) as f:
			data = json.load(f)
		return data['files']

	# 解压整合包文件
	def extract(self, path):
		modpack = os.path.basename(path)[:-4]
		modpack = modpack.replace('+', ' ')
		dirname = os.path.join('cache', modpack)
		if not os.path.isdir(dirname):
			os.makedirs(dirname)
		with ZipFile(path, 'r') as f:
			f.extractall(dirname)
		return modpack, dirname

if __name__ == '__main__':
	modpack = sys.argv[1]
	ModpackDownloader(modpack)
