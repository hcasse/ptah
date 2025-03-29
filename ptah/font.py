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

"""Management of Latex fonts."""

import os
import os.path
import re
import shutil
import subprocess
import tempfile

def normalize(s):
	return s.lower().replace(' ', '')

class FontTester:
	"""Tester for a font in the current installation."""

	def declare(self, out):
		"""Called to declare the use of the tested fonts."""
		pass

	def gen(self, out):
		"""Called to generate the test. Return True if the line matches."""
		pass

	def check(self, line):
		"""Check a line of the result."""
		pass

class Font:
	"""Representation of a font."""

	def __init__(self, name):
		self.name = name
		self.avail = None

	def declare(self, out):
		"""Called to generate code in the header of the document."""
		pass

	def use(self, out):
		"""Called to generate code for using this font."""
		pass


class DefaultFontTester(FontTester):
	"""Tester for default Latex fonts."""

	RE = re.compile("LaTeX Font Warning: Font shape `OT1/([a-zA-Z0-9]+)/m/n' undefined")

	def __init__(self):
		self.map = {}

	def declare(self, out):
		for font in self.map.values():
			font.avail = True
			font.declare(out)

	def gen(self, out):
		for font in self.map.values():
			font.use(out)

	def check(self, line):
		m = self.RE.match(line)
		if m is not None:
			key = m.group(1)
			try:
				self.map[key].avail = False
				#print("DEBUG:", key, " not found!")
				return True
			except KeyError:
				pass
		return False

	def add(self, key, font):
		"""Add a font."""
		self.map[key] = font

DEFAULT_TESTER = DefaultFontTester()

class DefaultFont(Font):

	def __init__(self, key, name):
		Font.__init__(self, name)
		self.key = key
		DEFAULT_TESTER.add(key, self)

	def use(self, out):
		out.write(f"\\fontfamily{{{self.key}}}\\selectfont\n")

TESTERS = [DEFAULT_TESTER]

FONT_LIST = [
	DefaultFont("pag", "Avant Garde"),
	DefaultFont("fvs", "Bitstream Vera Sans"),
	DefaultFont("pbk", "Bookman"),
	DefaultFont("bch", "Charter"),
	DefaultFont("ccr", "Computer Concrete"),
	DefaultFont("cmr", "Computer Modern"),
	DefaultFont("pcr", "Courier"),
	DefaultFont("ugm", "Garamond"),
	DefaultFont("phv", "Helvetica"),
	DefaultFont("zi4", "Inconsolata"),
	DefaultFont("lmr", "Latin Modern"),
	DefaultFont("lmss", "Latin Modern Sans"),
	DefaultFont("lmtt", "Latin Modern Typewriter"),
	DefaultFont("LinuxBiolinumT-OsF", "Linux Biolinum"),
	DefaultFont("LinuxLibertineT-OsF", "Linux Libertine"),
	DefaultFont("pnc", "New Century Schoolbook"),
	DefaultFont("ppl", "Palatino"),
	DefaultFont("qag", "TeX Gyre Adventor"),
	DefaultFont("qbk", "TeX Gyre Bonum"),
	DefaultFont("qzc", "TeX Gyre Chorus"),
	DefaultFont("qcr", "TeX Gyre Cursor"),
	DefaultFont("qhv", "TeX Gyre Heros"),
	DefaultFont("qpl", "TeX Gyre Pagella"),
	DefaultFont("qcs", "TeX Gyre Schola"),
	DefaultFont("qtm", "TeX Gyre Termes"),
	DefaultFont("ptm", "Times"),
	DefaultFont("uncl", "Uncial"),
	DefaultFont("put", "Utopia"),
	DefaultFont("pzc", "Zapf Chancery")
]

FONT_MAP = { normalize(f.name): f for f in FONT_LIST }

def find(name):
	"""Look for a font. Return found font or None."""
	try:
		font = FONT_MAP[normalize(name)]
		if font.avail != False:
			return font
	except KeyError:
		pass
	return None


def check():
	"""Check for the fonts."""

	# generate the file
	dir = tempfile.mkdtemp("-font", "ptah-")
	with open(os.path.join(dir, "test.tex"), "w") as out:
		out.write("""
\\documentclass[a4paper]{book}
\\usepackage[utf8]{inputenc}
""")
		for tester in TESTERS:
			tester.declare(out)
		out.write("\\begin{document}\n")
		for tester in TESTERS:
			tester.gen(out)
		out.write("\\end{document}\n")
		out.flush()

	# run the command
	cwd = os.path.abspath(os.getcwd())
	os.chdir(dir)
	cp = subprocess.run(
		"pdflatex test.tex",
		shell=True,
		capture_output=True,
		encoding = "utf8")
	os.chdir(cwd)
	for line in (cp.stdout + "\n" + cp.stderr).split('\n'):
		#print(f"DEBUG: testing [{line}]")
		for tester in TESTERS:
			if tester.check(line):
				break

	# clean all
	shutil.rmtree(dir, ignore_errors=True)


def get_fonts():
	"""Get the available fonts."""
	return FONT_LIST
