#!/usr/bin/env python3
#
#	ptah -- generator of photo album
#	Copyright (C) 2026  Hugues Cassé <hug.casse@gmail.com>
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
#	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.

"""Module for testing the content of this directory."""

import argparse
from colorama import Fore, Back, Style
import subprocess

TESTS = [
	"back.ptah",
	"border.ptah",
	"colors.ptah",
	"default.ptah",
	"font-test.ptah",
	"paths.ptah",
	"shadow.ptah",
	"styles.ptah",
	"test.ptah",
	"text.ptah"
]
FAILING = [
]

parser = argparse.ArgumentParser()
parser.add_argument("files", nargs="*", help="file to test with.")
parser.add_argument("--failed", action="store_true", help="files must be failing.")
args = parser.parse_args()

files = args.files
failing = []
if not files:
	files = TESTS
	failing = FAILING
elif args.failed:
	failing = files

cnt = 0
failed = 0
for test in files:
	cnt += 1
	print(f"Testing {test}")
	rc = subprocess.run(["python3", "-m", "ptah", test])
	if test not in failing:
		if rc.returncode:
			print(f"{Fore.RED}Error: {rc.returncode}{Style.RESET_ALL}")
			failed += 1
		else:
			print(f"{Fore.GREEN}Success!{Style.RESET_ALL}")
	else:
		print(f"DEBUG: {rc.returncode}")
		if rc.returncode:
			print(f"{Fore.GREEN}Failed as expected!{Style.RESET_ALL}")
		else:
			print(f"{Fore.RED}Error: should have failed!{Style.RESET_ALL}")
			failed += 1
print(f"{cnt} tests, {failed} failed")
