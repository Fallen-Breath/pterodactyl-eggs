#!/usr/bin/env python3
import argparse
import json
import os
import sys

from ruamel.yaml import YAML, RoundTripRepresenter


def cmd_build(args: argparse.Namespace) -> int:
	for file_name in os.listdir(args.input):
		if file_name.endswith('.yml'):
			with open(file_name, encoding='utf8') as f:
				try:
					data = YAML().load(f)
				except ValueError as e:
					print('Failed to load {}: {}'.format(args.input, e), file=sys.stderr)
					return 1

			if args.http_proxy:
				for variable in data['variables']:
					if variable['INSTALLER_HTTP_PROXY']:
						variable['default_value'] = args.http_proxy

			file_name_base = file_name.rsplit('.', 1)[0]
			with open(file_name_base + '.json', 'w', encoding='utf8') as f:
				json.dump(data, f, indent=4)

	return 0


def cmd_y2j(args: argparse.Namespace) -> int:
	def repr_str(dumper: RoundTripRepresenter, s: str):
		if '\n' in s:
			return dumper.represent_scalar('tag:yaml.org,2002:str', s, style='|')
		return dumper.represent_scalar('tag:yaml.org,2002:str', s)

	def get(name: str):
		if name.endswith('.yml') or name.endswith('yaml'):
			yaml = YAML()
			yaml.width = 2 ** 20
			yaml.representer.add_representer(str, repr_str)
			return yaml
		else:
			return json

	with open(args.input, encoding='utf8') as f:
		try:
			data = get(args.input).load(f)
		except ValueError as e:
			print('Failed to load {}: {}'.format(args.input, e), file=sys.stderr)
			return 1

	file_name = args.output or args.input.rsplit('.', 1)[0] + ('.yml' if get(args.input) == json else '.json')
	with open(file_name, 'w', encoding='utf8') as f:
		get(file_name).dump(data, f, indent=4)

	return 0


def main():
	parser = argparse.ArgumentParser(description='egg builder tools')
	subparsers = parser.add_subparsers(title='Command', dest='command')

	parser_build = subparsers.add_parser('build', help='build the egg jsons')
	parser_build.add_argument('-i', '--input', help='Input Directory. Default: current dir', required=False, default='.')
	parser_build.add_argument('--http-proxy', help='The default value of INSTALLER_HTTP_PROXY')

	parser_y2j = subparsers.add_parser('y2j', help='tool for conversion between json and yaml')
	parser_y2j.add_argument('-i', '--input', help='Input file', required=False)
	parser_y2j.add_argument('-o', '--output', help='Output file. If not given, use the input file name with altered extension')

	args = parser.parse_args()
	if args.command == 'build':
		return cmd_build(args)
	elif args.command == 'y2j':
		return cmd_y2j(args)
	else:
		print('Unknown command {}'.format(repr(args.command)))
		return 1


if __name__ == '__main__':
	sys.exit(main())
