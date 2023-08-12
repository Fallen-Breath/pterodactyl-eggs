#!/usr/bin/env python3
import enum
import functools
import os
import ssl
import subprocess
import sys
import time
from argparse import ArgumentParser
from io import BytesIO
from pathlib import Path
from typing import Tuple, Optional

import requests
from requests.auth import HTTPProxyAuth


def log(s: str):
	print('[INSTALL] {}'.format(s), flush=True)


def title(s: str):
	n = 100 - len(s) - 2
	m1 = n // 2
	m2 = n - m1
	log('{} {} {}'.format('=' * m1, s, '=' * m2))


def switch_cwd(path: Path):
	path.mkdir(parents=True, exist_ok=True)
	os.chdir(path)


def get_env(name: str, default: Optional[str] = None, warn_if_missing: bool = True) -> str:
	if name in os.environ:
		return os.environ[name]
	elif default is not None:
		if warn_if_missing:
			log('[WARN] Environment variable {} unset, using default value {}'.format(repr(name), repr(default)))
		return default
	else:
		log("[ERROR] Environment variable {} unset, and it's required".format(repr(name)))
		sys.exit(1)


def request_get(*args, **kwargs) -> requests.Response:
	http_proxy = get_env('INSTALLER_HTTP_PROXY', '', warn_if_missing=False)
	if http_proxy:
		kwargs['proxies'] = {
			'http': http_proxy,
			'https': http_proxy,
		}

	errors = []
	retries = 3
	for i in range(retries):
		try:
			return requests.get(*args, **kwargs)
		except (requests.exceptions.ConnectionError, ssl.SSLError) as e:
			errors.append(e)
			if i < retries - 1:
				log('[WARN] requests.get() attempt {} failed ({}), retrying'.format(i + 1, e))
	if len(errors) > 0:
		log('[ERROR] All requests.get() attempts failed')
		raise errors[0] from None


def bash_call(command: str):
	http_proxy = get_env('INSTALLER_HTTP_PROXY', '', warn_if_missing=False)
	if http_proxy:
		env = {
			**os.environ,
			'http_proxy': http_proxy,
			'https_proxy': http_proxy,
		}
	else:
		env = None
	subprocess.check_call(command, shell=True, env=env)


@functools.lru_cache
def get_json(url: str):
	return request_get(url).json()


def download(url: str) -> Tuple[bytes, float, float]:
	buf = BytesIO()
	response = request_get(url, stream=True)
	total_mb = int(response.headers.get('content-length')) / 1048576
	downloaded_mb = 0
	start_time = time.time()
	last_report = start_time

	for chunk in response.iter_content(chunk_size=1024):
		now = time.time()
		downloaded_mb += len(chunk) / 1048576
		buf.write(chunk)

		if now - last_report >= 5:
			percent = (downloaded_mb / max(total_mb, 1)) * 100
			if percent > 0:
				eta_sec = (now - start_time) / percent * (100 - percent)
				if eta_sec > 60:
					eta = f'{eta_sec / 60:.2f}min'
				else:
					eta = f'{eta_sec:.2f}s'
			else:
				eta = 'N/A'
			log(f'  {downloaded_mb:.2f}MB / {total_mb:.2f}MB, {percent:.2f}%, ETA {eta}')
			last_report = now

	return buf.getvalue(), downloaded_mb, time.time() - start_time


def download_to(name: str, url: str, file_path: str):
	log('Downloading {} from {} to {}'.format(name, url, repr(file_path)))
	buf, downloaded_mb, cost = download(url)
	log(f'Download complete, time cost {cost:.2f}s, {downloaded_mb / cost:.2f}MB/s')

	file_dir = os.path.dirname(file_path)
	if len(file_dir) > 0:
		os.makedirs(file_dir, exist_ok=True)
	with open(file_path, 'wb') as f:
		f.write(buf)
	log('Written {} to file'.format(repr(file_path)))


def prepare():
	# Server Files: /mnt/server
	working_dir = Path('/mnt/server')
	if not working_dir.is_dir():
		log('[FATAL] Working dir {} does not exist'.format(working_dir))
		sys.exit(1)
	switch_cwd(working_dir)

	log('Touching INSTALLATION_MARK for start_hook')
	Path('INSTALLATION_MARK').touch(exist_ok=True)

	switch_cwd(working_dir / 'server')


def get_mc_version() -> str:
	log('Downloading Minecraft version manifests')
	version_manifests = get_json('https://launchermeta.mojang.com/mc/game/version_manifest.json')
	latest_release = version_manifests['latest']['release']
	latest_snapshot = version_manifests['latest']['snapshot']
	log('Latest mc release: {}'.format(latest_release))
	log('Latest mc snapshot: {}'.format(latest_snapshot))

	input_version = get_env('MC_VERSION')
	mc_version = {
		'latest': latest_release,
		'snapshot': latest_snapshot,
	}.get(input_version, input_version)
	log('mc_version: $MC_VERSION={} -> {}'.format(input_version, mc_version))
	return mc_version


def install_vanilla(mc_version: str, server_jar_path: str):
	"""
	:return: mc_version
	"""
	# ================================================================
	title('Installing Vanilla Minecraft')
	log('mc_version: {}'.format(mc_version))
	log('server_jar_path: {}'.format(server_jar_path))

	version_manifests = get_json('https://launchermeta.mojang.com/mc/game/version_manifest.json')
	for version in version_manifests['versions']:
		if version.get('id') == mc_version:
			manifest_url = version['url']
			break
	else:
		log('[ERROR] Cannot find version {}'.format(mc_version))
		sys.exit(1)

	log('Downloading manifest data of mc {} from {}'.format(mc_version, manifest_url))
	manifest = get_json(manifest_url)
	server_url = manifest['downloads']['server']['url']

	download_to('mc server jar', server_url, server_jar_path)


def install_fabric():
	vanilla_server_jar = 'minecraft_server.jar'
	mc_version = get_mc_version()
	install_vanilla(mc_version, vanilla_server_jar)

	# ================================================================
	title('Installing Fabric Loader')
	loader_version = get_env('FABRIC_LOADER_VERSION', 'latest')
	server_jar_file = get_env('SERVER_JARFILE')
	log('mc_version: {}'.format(mc_version))
	log('loader_version: {}'.format(loader_version))
	log('server_jar_file: {}'.format(server_jar_file))

	installer_versions = get_json('https://meta.fabricmc.net/v2/versions/installer')
	for version in installer_versions:
		if version.get('stable', False):
			installer_url = version['url']
			break
	else:
		log('[ERROR] Cannot valid fabric installer version from {}'.format(installer_versions))
		sys.exit(1)

	installer_name = os.path.basename(installer_url)
	log('Downloading latest fabric installer {} from {}'.format(repr(installer_name), installer_url))
	installer_bytes, _, _ = download(installer_url)
	with open(installer_name, 'wb') as f:
		f.write(installer_bytes)

	command = 'java -jar {} server -mcversion {}'.format(installer_name, mc_version)
	if loader_version != 'latest':
		command += ' -loader {}'.format(loader_version)
	log('Installing fabric with command {}'.format(repr(command)))
	bash_call(command)

	fabric_server_launcher_properties = 'fabric-server-launcher.properties'
	log('Setting server jar file name in {}'.format(fabric_server_launcher_properties))
	with open(fabric_server_launcher_properties, 'w', encoding='utf8') as f:
		f.write('serverJar={}\n'.format(vanilla_server_jar))

	fabric_server_launcher_jar = 'fabric-server-launch.jar'  # hardcoded
	if server_jar_file != fabric_server_launcher_jar:
		log('Renaming {} to $SERVER_JARFILE={}'.format(repr(fabric_server_launcher_jar), repr(server_jar_file)))
		os.rename(fabric_server_launcher_jar, server_jar_file)


def install_paper():
	# ================================================================
	title('Installing Paper')
	mc_version = get_env('MC_VERSION')
	build_num = get_env('BUILD_NUMBER', 'latest')
	server_jar_path = get_env('SERVER_JARFILE')
	log('mc_version: {}'.format(mc_version))
	log('build_num: {}'.format(build_num))
	log('server_jar_path: {}'.format(server_jar_path))

	supported_mc_versions = get_json('https://api.papermc.io/v2/projects/paper').get('versions', [])
	if len(supported_mc_versions) == 0:
		log('[ERROR] supported_mc_versions is empty')
		sys.exit(1)
	if mc_version != 'latest' and mc_version not in supported_mc_versions:
		log('[WARN] given mc version {} is unsupported, use latest version'.format(repr(mc_version)))
		mc_version = 'latest'
	if mc_version == 'latest':
		mc_version = supported_mc_versions[-1]
		log('using latest supported mc version: {}'.format(repr(mc_version)))

	builds = get_json(f'https://api.papermc.io/v2/projects/paper/versions/{mc_version}').get('builds', [])
	if len(supported_mc_versions) == 0:
		log('[ERROR] builds for mc {} is empty'.format(repr(mc_version)))
		sys.exit(1)
	if build_num != 'latest' and build_num not in map(str, builds):
		log('[WARN] given paper build {} not found for mc {}, use latest build'.format(repr(build_num), repr(mc_version)))
		build_num = 'latest'
	if build_num == 'latest':
		build_num = max(builds)
		log('using latest build num: {}'.format(repr(build_num)))

	download_url = f'https://api.papermc.io/v2/projects/paper/versions/{mc_version}/builds/{build_num}/downloads/paper-{mc_version}-{build_num}.jar'
	download_to('paper server jar', download_url, server_jar_path)

	install_vanilla(mc_version, 'cache/mojang_{}.jar'.format(mc_version))


def install_bungeecord():
	# ================================================================
	title('Installing Bungeecord')
	build_num = get_env('BUILD_NUMBER', 'latest')
	server_jar_path = get_env('SERVER_JARFILE')
	log('build_num: {}'.format(build_num))
	log('server_jar_path: {}'.format(server_jar_path))

	data = get_json(f'https://ci.md-5.net/job/Bungeecord/api/json')
	builds = data['builds']
	if len(builds) == 0:
		log('[ERROR] build num list is empty')
		sys.exit(1)
	build_map = {b['number']: b for b in builds}
	build_nums = list(build_map.keys())
	if build_num != 'latest' and build_num not in map(str, build_nums):
		log('[WARN] given bungeecord build {} not found, use latest build'.format(repr(build_num)))
		build_num = 'latest'
	if build_num == 'latest':
		build_num = max(map(int, build_nums))
		log('using latest build num: {}'.format(repr(build_num)))

	data = get_json(build_map[build_num]['url'] + 'api/json')
	if len(data['artifacts']) == 0:
		log('[ERROR] empty artifact for build {}'.format(build_num))
		return

	for artifact in data['artifacts']:
		path = artifact['relativePath']
		url = f'{data["url"]}artifact/{path}'
		file_name = artifact['fileName']
		log('found artifact {} for build {}'.format(repr(file_name), build_num))
		if 'bungeecord' in file_name.lower():
			file_path = server_jar_path
		else:
			file_path = os.path.join('modules', file_name)

		download_to(file_name, url, file_path)


class ServerType(enum.Enum):
	NONE = enum.auto()
	VANILLA = enum.auto()
	FABRIC = enum.auto()
	PAPER = enum.auto()
	BUNGEECORD = enum.auto()


def main():
	parser = ArgumentParser()
	parser.add_argument('server_type', help='Supported server types: {}'.format(', '.join(map(lambda st: st.name.lower(), ServerType))))
	args = parser.parse_args()

	# ================================================================
	title('Installation Start')

	try:
		server_type = ServerType[args.server_type.upper()]
	except KeyError:
		log('[ERROR] Unknown server type {}'.format(args.server_type))
		sys.exit(1)

	prepare()

	if server_type == ServerType.NONE:
		log('Doing nothing with server_type none')
		log('You need to setup the server yourself')

	elif server_type == ServerType.VANILLA:
		install_vanilla(get_mc_version(), get_env('SERVER_JARFILE'))

	elif server_type == ServerType.FABRIC:
		# Renames:
		# fabric-server-launcher.jar -> ${SERVER_JARFILE}
		# vanilla_server.jar -> 'minecraft_server.jar' (hardcoded)
		install_fabric()

	elif server_type == ServerType.PAPER:
		install_paper()

	elif server_type == ServerType.BUNGEECORD:
		install_bungeecord()

	else:
		raise RuntimeError('Unhandled server type {}'.format(server_type))

	# ================================================================
	title('Installation End')


if __name__ == '__main__':
	main()
