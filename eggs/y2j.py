#!/usr/bin/env python3

import json
import sys
from argparse import ArgumentParser

from ruamel.yaml import YAML, RoundTripRepresenter


def main():
	parser = ArgumentParser(description='json <-> yaml')
	parser.add_argument('-i', '--input', help='Input file', required=False)
	parser.add_argument('-o', '--output', help='Output file. If not given, use the input file name with altered extension')
	args = parser.parse_args()

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
			sys.exit(1)

	file_name = args.output or args.input.rsplit('.', 1)[0] + ('.yml' if get(args.input) == json else '.json')
	with open(file_name, 'w', encoding='utf8') as f:
		get(file_name).dump(data, f, indent=4)


if __name__ == '__main__':
	main()
