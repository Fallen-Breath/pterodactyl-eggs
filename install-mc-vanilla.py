#!/usr/bin/env python3
import os
import sys
import time
from io import BytesIO
from pathlib import Path
from typing import Tuple

import requests


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


def download(url: str) -> Tuple[bytes, float, float]:
	buf = BytesIO()
	response = requests.get(url, stream=True)
	total_mb = int(response.headers.get('content-length')) / 1048576
	downloaded_mb = 0
	start_time = time.time()
	last_report = start_time

	for chunk in response.iter_content(chunk_size=1024):
		now = time.time()
		downloaded_mb += len(chunk) / 1048576
		buf.write(chunk)

		if now - last_report >= 1:
			percent = (downloaded_mb / max(total_mb, 1)) * 100
			log(f'  {downloaded_mb:.2f}MB / {total_mb:.2f}MB, {percent:.2f}%')
			last_report = now

	return buf.getvalue(), downloaded_mb, time.time() - start_time


def main():
	# ================================================================
	title('Preparing')
	# Server Files: /mnt/server
	working_dir = Path('/mnt/server')
	switch_cwd(working_dir)

	log('touching INSTALLATION_MARK')
	Path('INSTALLATION_MARK').touch(exist_ok=True)

	# ================================================================
	title('Initialize Vanilla Minecraft')

	switch_cwd(working_dir / 'server')

	log('Downloading Minecraft version manifests')
	version_manifests = requests.get('https://launchermeta.mojang.com/mc/game/version_manifest.json').json()
	latest_release = version_manifests['latest']['release']
	latest_snapshot = version_manifests['latest']['snapshot']
	log('latest release is {}'.format(latest_release))
	log('latest snapshot is {}'.format(latest_snapshot))

	input_version = os.getenv('VANILLA_VERSION') or 'latest'
	version_id = {
		'latest': latest_release,
		'snapshot': latest_snapshot,
	}.get(input_version, input_version)
	for version in version_manifests['versions']:
		if version.get('id') == version_id:
			manifest_url = version['url']
			break
	else:
		log('Cannot find version {}'.format(version_id))
		sys.exit(1)

	log('Downloading manifest data of {} from {}'.format(version_id, manifest_url))
	manifest = requests.get(manifest_url).json()
	server_url = manifest['downloads']['server']['url']

	server_jar_path = os.environ['SERVER_JARFILE']
	log('Downloading server jar from {} to {}'.format(server_url, repr(server_jar_path)))
	server_jar_bytes, downloaded_mb, cost = download(server_url)
	log(f'Download complete, time cost {cost:.2f}s, {downloaded_mb / cost:.2f}MB/s')
	with open(server_jar_path, 'wb') as f:
		f.write(server_jar_bytes)
	log('Saved server jar to {}'.format(repr(server_jar_path)))

	# ================================================================
	title('Done')


if __name__ == '__main__':
	main()
