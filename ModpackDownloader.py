#!/usr/bin/env python
# -*- coding: utf-8 -*-

'''
@Date: 2018-04-04 15:58:00
@Author: c_ben
@Version: 1.0
'''

import os
import re
import sys
import json
import shutil
import pickle
import requests
from zipfile import ZipFile
from bs4 import BeautifulSoup

CACHE_PATH = 'cache'

class CacheManager(dict):
	def __init__(self):
		if not os.path.isdir(CACHE_PATH):
			os.makedirs(CACHE_PATH)
		self.data_path = os.path.join(CACHE_PATH, 'cache_data.pkl')
		if os.path.isfile(self.data_path):
			with open(self.data_path, 'rb') as f:
				self.update(pickle.load(f))

	def __setitem__(self, key, value):
		dict.__setitem__(self, key, value)
		with open(self.data_path, 'wb') as f:
			pickle.dump(dict(self), f)

	def save_file(self, res):
		filename = re.match('^.*\/([^\/]+)$', res.url).group(1)
		path = os.path.join(CACHE_PATH, filename)
		with open(path, 'wb') as f:
			for chunk in res.iter_content(4096):
				f.write(chunk)
		return filename, path

class ModpackDownloader:
	URLS = [
		'https://minecraft.curseforge.com/projects/%s/files',
		'https://minecraft.curseforge.com/projects/%s/files/%s/download'
	]

	def __init__(self, project_id, file_id=None):
		self.cache = CacheManager()
		self.session = requests.Session()
		self.session.headers.update({
				'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleW' + \
					'ebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
			})
		self.session.proxies = {
			'http': '127.0.0.1:1080',
			'https': '127.0.0.1:1080'
		}

		project_id = str(project_id)
		print('整合包ID：' + project_id)

		if file_id is None:
			file_id = self.get_file_id(project_id)
		file_id = str(file_id)
		print('版本ID：' + file_id)

		modpack, modpack_path = self.get_modpack_file(project_id, file_id)

		manifest_path = os.path.join(modpack_path, 'manifest.json')
		with open(manifest_path) as f:
			manifest = json.load(f)

		self.get_mods_file(manifest['files'], modpack_path)

		print('发现异常模组链接，请检查并补充到mods文件夹中')
		for i in self.cache['exception']:
			print(i)

		self.cache['exception'] = []
		print('模组已全部下载完成')

	def get_mods_file(self, mods, modpack_path):
		length = len(mods)
		print('补全模组进度：0/%d' % length, end='', flush=True)
		mods_path = os.path.join(modpack_path, 'overrides/mods')
		for i, mod in enumerate(mods):
			key = (mod['projectID'], mod['fileID'])
			if key in self.cache:
				filename, path = self.cache[key]
				print('\r已存在模组：' + self.get_name(filename))
			else:
				try:
					res = self.session.get(self.URLS[1] % key, stream=True)
					filename, path = self.cache.save_file(res)
					print('\r已下载模组：' + self.get_name(filename))
					self.cache[key] = (filename, path)
				except Exception as e:
					self.cache['exception'] = self.cache.get('exception', [])
					self.cache['exception'].append(self.URLS[1] % key)
			shutil.copyfile(path, os.path.join(mods_path, filename))
			print('补全模组进度：%d/%d' % (i + 1, length), end='', flush=True)
		print('\r已补全全部模组，共%d个模组' % length)

	def get_modpack_file(self, project_id, file_id):
		if (project_id, file_id) in self.cache:
			filename, path = self.cache[(project_id, file_id)]
			print('已存在整合包文件：' + filename)
			modpack = self.get_name(filename)
			modpack_path = os.path.join(CACHE_PATH, modpack)
		else:
			res = self.session.get(self.URLS[1] % (project_id, file_id), stream=True)
			filename, path = self.cache.save_file(res)
			print('已下载整合包文件：' + filename)
			modpack, modpack_path = self.unzip_file(filename, path)
			print('已解压整合包：' + modpack)
			self.cache[(project_id, file_id)] = (filename, path)
		return modpack, modpack_path

	def get_file_id(self, project_id):
		response = self.session.get(self.URLS[0] % project_id)
		soup = BeautifulSoup(response.text, 'lxml')
		file = soup.find('div', 'project-file-name-container')
		return re.search('\/([^\/]+)$', file.find('a')['href']).group(1)

	def get_name(self, filename):
		name = re.match('^(.+)\.[^\.]+$', filename)
		return name.group(1).replace('+', ' ')

	def unzip_file(self, filename, path):
		dir_name = self.get_name(filename)
		dir_path = os.path.join(CACHE_PATH, dir_name)
		if not os.path.isdir(dir_path):
			os.makedirs(dir_path)
		with ZipFile(path, 'r') as f:
			f.extractall(dir_path)
		return dir_name, dir_path

if __name__ == '__main__':
	project_id = sys.argv[1]
	try:
		file_id = sys.argv[2]
	except:
		file_id = None
	ModpackDownloader(project_id, file_id)