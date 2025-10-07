#
#	Ptah -- Photo album generator
#	Copyright (C) 2022 Hugues Cassé <hug.casse@gmail.com>
#
#	This program is free software: you can redistribute it and/or modify
#	it under the terms of the GNU General Public License as published by
# 	the Free Software Foundation, either version 3 of the License, or
#	(at your option) any later version.
#
#	This program is distributed in the hope that it will be useful,
#	but WITHOUT ANY WARRANTY; without even the implied warranty of
#	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#	GNU General Public License for more details.
#
#	You should have received a copy of the GNU General Public License
#	along with this program.  If not, see <https://www.gnu.org/licenses/>.
#

"""Ptah command."""

import argparse
from importlib.metadata import version, PackageNotFoundError
import re
import subprocess
import sys
import yaml

from ptah import io
from ptah import format
from ptah import util
from ptah import latex
from ptah import props
from ptah.album import Album
import ptah.pages


# get version
try:
	__version__ = version("ptah")
except PackageNotFoundError:
	__version__ = "0.0.0"


# formats
# https://en.wikipedia.org/wiki/ISO_216
FORMATS = {
	"a3": (297, 420),
	"a4": (210, 297),
	"a5": (148, 210),
	"folio": (305, 483),
	"quarto": (214, 305),
	"imperial-octavo": (210, 292),
	"super-octavo": (178, 279),
	"royal-octavo": (159, 254),
	"medium-octavo": (165, 235),
	"octavo": (153, 229),
	"crown-octavo": (137, 203),
	"duodecimo": (127, 187),
	"sextodecimo": (102, 171),
	"octodecimo": (102, 165)
}


# entry point
def main(mon = io.DEF):

	# parse arguments
	parser = argparse.ArgumentParser(
		prog = "ptah",
		description = "Photo album generator"
	)
	parser.add_argument('albums', nargs="*", help="Album to generate.")
	parser.add_argument("--doc", action="store_true",
		help="Generate the documentation.")
	parser.add_argument("--debug", action="store_true",
		help="Generate the documentation.")
	parser.add_argument("--version", action="store_true",
		help="Display the version.")

	args = parser.parse_args()
	albums = args.albums
	if albums == None:
		albums = "album.ptah"

	# generic options
	if args.debug:
		util.DEBUG = True

	# version case
	if args.version:
		print(f"ptah V{__version__}, copyright (c) 2025 H. Cassé <hug.casse@gmail.com>")
		sys.exit(0)

	# generate the documentation
	if args.doc:
		latex.gen_doc()

	# process the albums
	else:
		for path in args.albums:
			try:
				album = Album(path)
				album.read(mon)
				latex.Drawer(album).gen()
			except util.CheckError as e:
				mon.print_error(str(e))


if __name__ == "__main__":
	main()

