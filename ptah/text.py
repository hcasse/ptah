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

"""Classes managing text. It is currently based on Thot."""

from thot.common import Env
from thot.doc import Document, Par
from thot.tparser import Manager
from thot.back import get_output

class Text:
	"""Text ready to be displayed as a result of syntax parsing."""

	def __init__(self, syntax, range):
		self.syntax = syntax
		self.range = range

	def __str__(self):
		return " ".join([x.toText() for x in self.range])


class Syntax:
	"""Syntax to read a text."""

	def __init__(self, syntax="markdown"):
		self.syntax = syntax
		self.doc = Document(Env())
		self.manager = Manager(self.doc)
		self.manager.use(self.syntax)

	def parse(self, text):
		"""Parse the passed text and returns corresponding Text object."""
		lines = [l + '\n' for l in text.split('\n')]
		self.doc.clear()
		self.doc.append(Par())
		self.manager.close_to_top()
		self.manager.parseInternal(lines, "<ptah>")
		return Text(self, self.doc.getContent())


class Output:
	"""Provides output facilities for the text."""

	def __init__(self, out, type="latex"):
		self.out = out
		self.type = type
		self.gen = None

	def output(self, text):
		"""Output the text to the passed output.
		Raises ThotException in case of error."""
		if self.gen is None:
			self.doc = text.syntax.doc
			self.doc.env["THOT_OUT_TYPE"] = self.type
			self.gen = get_output(self.doc).Generator(self.doc, out=self.out)
		for node in text.range:
			node.gen(self.gen)
