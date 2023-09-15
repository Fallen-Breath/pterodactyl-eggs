#!/usr/bin/env python3
import os
import re
import shutil
import subprocess

from ruamel.yaml import YAML

WORKING_DIR = '/home/container'
CONFIG_FILE = '/start_hook.yml'
MCDR_CONFIG_FILE = 'config.yml'
MCDR_PERMISSION_FILE = 'permission.yml'
INSTALLATION_MARK = 'INSTALLATION_MARK'
config: dict  # phase -> file -> override


def log(s: str):
	if os.getenv('DEBUG_START_HOOK') == 'true':
		print('[INIT] {}'.format(s), flush=True)


def read_yaml(file_path: str):
	with open(file_path, 'r', encoding='utf8') as f:
		return YAML().load(f)


def write_yaml(data, file_path: str):
	with open(file_path, 'w', encoding='utf8') as f:
		yaml = YAML()
		yaml.width = 1048576
		yaml.dump(data, f)


def envsubst(s: str) -> str:
	def replace_var(match: re.Match):
		if match.group('escaped'):
			return '${' + match.group('var_name') + '}'
		return os.environ.get(match.group('var_name'), '')

	return re.sub(r'(?P<escaped>\\?)\${(?P<var_name>.*?)}', replace_var, s)


def apply_modification(phase: str):
	log('Applying file modifications for phase {}'.format(phase))
	for file_path, patch in config[phase].items():
		if not os.path.isfile(file_path):
			log('Skipping file {} cuz it does not exist'.format(repr(file_path)))
			continue
		log('Modifying file {}'.format(repr(file_path)))
		data = read_yaml(file_path)

		modified = False
		for key, value in patch.items():
			if isinstance(value, str):
				expanded_value = envsubst(value)
				if value != expanded_value:
					log('  expanded value {} -> {}'.format(repr(value), repr(expanded_value)))
					value = expanded_value
			if key in data:
				log('  setting key={}, value: {} -> {}'.format(key, repr(data[key]), repr(value)))
				modified |= data[key] == value
			else:
				log('  adding key={}, value={}'.format(key, repr(value)))
				modified |= True
			data[key] = value

		if modified:
			write_yaml(data, file_path)
		else:
			log('No modification was actually made on file {}'.format(repr(file_path)))


def move_minecraft_eula():
	eula_file_name = 'eula.txt'
	if not os.path.isfile(eula_file_name):
		return

	log('eula file {} detected'.format(repr(eula_file_name)))

	with open(eula_file_name, 'r') as f:
		for line in f.read().splitlines():
			if re.fullmatch(r'eula\s*=\s*true', line):
				break
		else:
			# not a valid eula file
			log('not a valid eula file, ignoring')
			return

	# move it to the MCDR working directory dir
	working_directory = read_yaml(MCDR_CONFIG_FILE).get('working_directory', 'server')
	dest_path = os.path.join(working_directory, eula_file_name)
	if os.path.isdir(working_directory):
		shutil.move(eula_file_name, dest_path)
		log('moved {} to {}'.format(repr(eula_file_name), repr(dest_path)))
	else:
		log('MCDR working directory {} not found'.format(repr(working_directory)))


def main():
	global config
	config = read_yaml(CONFIG_FILE)

	# https://pterodactyl.io/community/config/eggs/creating_a_custom_image.html#work-directory-entrypoint
	assert os.getcwd() == WORKING_DIR, 'Unexpected working dir {}, should be {}'.format(os.getcwd(), WORKING_DIR)

	is_init = os.path.isfile(INSTALLATION_MARK)
	if is_init:
		log('First launch detected, initializing MCDR environment')
		subprocess.check_call('python3 -m mcdreforged init', shell=True)
		apply_modification('install')
		os.remove(INSTALLATION_MARK)

	apply_modification('pre_start')
	move_minecraft_eula()
	
	log('Done')


if __name__ == '__main__':
	main()
