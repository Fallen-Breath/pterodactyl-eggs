#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from typing import Iterator, Tuple


def iterate_all() -> Iterator[Tuple[str, str, str, str]]:
	for system in ["bullseye", "slim-bullseye"]:
		for java in [8, 17, 21]:
			for mcdr in ["latest", "2.12", "2.11", "2.10"]:
				tag = f"fallenbreath/pterodactyl-yolks:minecraft-runtime-{system}-{java}-{mcdr}"
				yield system, str(java), mcdr, tag


def cmd_build(args: argparse.Namespace):
	for system, java, mcdr, tag in iterate_all():
		if mcdr == 'latest':
			mcdr_req = 'mcdreforged'
		else:
			mcdr_req = f"mcdreforged~={mcdr}"

		print(f"======== System: {system}, Java: {java}, MCDR: {mcdr}, Tag: {tag!r} ========")

		subprocess.check_call([
			'docker', 'build', os.getcwd(),
			'--build-arg', f'SYSTEM={system}',
			'--build-arg', f'JAVA_VERSION={java}',
			'--build-arg', f'MCDR_REQUIREMENT={mcdr_req}',
			'-t', tag,
		])

		if args.push:
			subprocess.check_call(['docker', 'push', tag])


def cmd_push(args: argparse.Namespace):
	for _, _, _, tag in iterate_all():
		subprocess.check_call(['docker', 'push', tag])


def cmd_delete(args: argparse.Namespace):
	for _, _, _, tag in iterate_all():
		subprocess.check_call(['docker', 'image', 'rm', tag])


def main():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(title='Command', help='Available commands', dest='command', required=True)

	parser_build = subparsers.add_parser('build', help='Build all images')
	parser_build.add_argument('-p', '--push', action='store_true', help='Push after build')

	subparsers.add_parser('push', help='Push all images')
	subparsers.add_parser('delete', help='Delete all images')

	args = parser.parse_args()

	if args.command == 'build':
		cmd_build(args)
	elif args.command == 'push':
		cmd_push(args)
	elif args.command == 'delete':
		cmd_delete(args)
	else:
		print('Unknown command {!r}'.format(args.command))
		sys.exit(1)


if __name__ == '__main__':
	try:
		main()
	except subprocess.CalledProcessError as e:
		print(type(e).__name__, e.returncode, file=sys.stderr)
	except KeyboardInterrupt:
		pass
