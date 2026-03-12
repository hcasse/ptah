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

from colorama import Fore, Back, Style
import subprocess

TESTS = [
	"back.ptah",
	"border.ptah"
]

cnt = 0
failed = 0
for test in TESTS:
	cnt += 1
	print(f"Testing {test}")
	rc = subprocess.run(["python3", "-m", "ptah", test])
	if rc.returncode:
		print(f"{Fore.RED}Error: {rc.returncode}{Style.RESET_ALL}")
		failed += 1
	else:
		print(f"{Fore.GREEN}Success!{Style.RESET_ALL}")
print(f"{cnt} tests, {failed} failed")
