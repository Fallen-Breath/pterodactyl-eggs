#!/usr/bin/env python3
import argparse
import os
import subprocess
import sys
from typing import Iterator, NamedTuple


class Context(NamedTuple):
	image_base: str
	system: str
	java: str
	mcdr: str
	tag: str


def iterate_all() -> Iterator[Context]:
	for image_base, systems in {
		'eclipse-temurin': ['jammy'],
		'openjdk': ['bullseye', 'slim-bullseye'],
	}.items():
		for system in systems:
			for java in [8, 11, 17, 21]:
				for mcdr in ['latest', '2.13', '2.12']:
					tag = f'fallenbreath/pterodactyl-yolks:minecraft-runtime-{system}-{java}-{mcdr}'
					yield Context(image_base, system, str(java), mcdr, tag)


def cmd_build(args: argparse.Namespace):
	for ctx in iterate_all():
		if ctx.mcdr == 'latest':
			mcdr_req = 'mcdreforged'
		else:
			mcdr_req = f'mcdreforged~={ctx.mcdr}'

		print(f'======== System: {ctx.system}, Java: {ctx.java}, MCDR: {ctx.mcdr}, Tag: {ctx.tag!r} ========')

		cmd = [
			'docker', 'build', os.getcwd(),
			'-t', ctx.tag,
			'--build-arg', f'IMAGE_BASE={ctx.image_base}',
			'--build-arg', f'SYSTEM={ctx.system}',
			'--build-arg', f'JAVA_VERSION={ctx.java}',
			'--build-arg', f'MCDR_REQUIREMENT={mcdr_req}',
		]
		if args.http_proxy is not None:
			cmd.extend([
				'--build-arg', f'http_proxy={args.http_proxy}',
				'--build-arg', f'https_proxy={args.http_proxy}',
			])
		subprocess.check_call(cmd)

		if args.push:
			subprocess.check_call(['docker', 'push', ctx.tag])


def cmd_push(args: argparse.Namespace):
	for ctx in iterate_all():
		subprocess.check_call(['docker', 'push', ctx.tag])


def cmd_delete(args: argparse.Namespace):
	for ctx in iterate_all():
		subprocess.check_call(['docker', 'image', 'rm', ctx.tag])


def main():
	parser = argparse.ArgumentParser()
	subparsers = parser.add_subparsers(title='Command', help='Available commands', dest='command', required=True)

	parser_build = subparsers.add_parser('build', help='Build all images')
	parser_build.add_argument('-p', '--push', action='store_true', help='Push after build')
	parser_build.add_argument('--http-proxy', help='Set the url of http proxy to be used in build')

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
