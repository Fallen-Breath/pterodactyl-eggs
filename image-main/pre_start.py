#!/usr/bin/env python3
import os
import subprocess

from ruamel.yaml import YAML

WORKING_DIR = '/home/container'
CONFIG_FILE = 'config.yml'
PERMISSION_FILE = 'permission.yml'
INSTALLATION_MARK = 'INSTALLATION_MARK'


def log(s: str):
	print('[INIT] {}'.format(s), flush=True)


def read_yaml(file_path: str):
	with open(file_path, 'r', encoding='utf8') as f:
		return YAML().load(f)


def write_yaml(data, file_path: str):
	with open(file_path, 'w', encoding='utf8') as f:
		yaml = YAML()
		yaml.width = 1048576
		yaml.dump(data, f)


def modify_config():
	log('Modifying configuration file')
	data = read_yaml(CONFIG_FILE)
	data['start_command'] = 'java -Xms128M -XX:MaxRAMPercentage=95.0 -Dfile.encoding=UTF-8 -jar "$SERVER_JARFILE"'
	data['advanced_console'] = False
	write_yaml(data, CONFIG_FILE)


def modify_permission():
	log('Cleaning up permission file')
	data = read_yaml(PERMISSION_FILE)
	data['owner'] = None
	write_yaml(data, PERMISSION_FILE)


def main():
	# https://pterodactyl.io/community/config/eggs/creating_a_custom_image.html#work-directory-entrypoint
	assert os.getcwd() == WORKING_DIR, 'Unexpected working dir {}, should be {}'.format(os.getcwd(), WORKING_DIR)

	is_init = os.path.isfile(INSTALLATION_MARK)
	if is_init:
		log('First launch detected, initializing MCDR environment')
		subprocess.check_call('python3 -m mcdreforged init', shell=True)
		modify_permission()
		os.remove(INSTALLATION_MARK)

	modify_config()
	log('done')


if __name__ == '__main__':
	main()
