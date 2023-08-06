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


def get_env(name: str, default: Optional[str] = None) -> str:
	if name in os.environ:
		return os.environ[name]
	elif default is not None:
		log('[WARN] Environment variable {} unset, using default value {}'.format(repr(name), repr(default)))
		return default
	else:
		log("[ERROR] Environment variable {} unset, and it's required".format(repr(name)))
		sys.exit(1)


def request_get(*args, **kwargs) -> requests.Response:
	http_proxy = get_env('INSTALLER_HTTP_PROXY', '')
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
	http_proxy = get_env('INSTALLER_HTTP_PROXY', '')
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

	log('Downloading mc server jar from {} to {}'.format(server_url, repr(server_jar_path)))
	server_jar_bytes, downloaded_mb, cost = download(server_url)
	log(f'Download complete, time cost {cost:.2f}s, {downloaded_mb / cost:.2f}MB/s')
	with open(server_jar_path, 'wb') as f:
		f.write(server_jar_bytes)
	log('Saved server jar to {}'.format(repr(server_jar_path)))


def install_fabric(mc_version: str):
	vanilla_server_jar = 'minecraft_server.jar'
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


class ServerType(enum.Enum):
	NONE = enum.auto()
	VANILLA = enum.auto()
	FABRIC = enum.auto()


def main():
	parser = ArgumentParser()
	parser.add_argument('server_type', help='Supported server types: none, vanilla, fabric')
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
		log('Doing nothing server_type none')

	elif server_type == ServerType.VANILLA:
		install_vanilla(get_mc_version(), get_env('SERVER_JARFILE'))

	elif server_type == ServerType.FABRIC:
		# Renames:
		# fabric-server-launcher.jar -> ${SERVER_JARFILE}
		# vanilla_server.jar -> 'minecraft_server.jar' (hardcoded)
		install_fabric(get_mc_version())

	else:
		raise RuntimeError('Unhandled server type {}'.format(server_type))

	# ================================================================
	title('Installation End')


if __name__ == '__main__':
	main()
