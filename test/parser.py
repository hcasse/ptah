#!/usr/bin/python3

from ptah.wiki import *
import ptah.wiki.markdown as markdown

class LatexHandler(Handler):
	STYLES = {
		TYPE_BOLD: "\\textbf{",
		TYPE_ITALIC: "\\textit{",
		TYPE_CODE: "\\texttt{"
	}

	def __init__(self):
		self.reset()
		
	def reset(self):
		self.res = ""
		self.one = False

	def on_text(self, text):
		self.res += text

	def begin_style(self, style):
		try:
			self.res += LatexHandler.STYLES[style]
		except KeyError:
			pass

	def end_style(self, style):
		if style in LatexHandler.STYLES:
			self.res += "}"

	def begin_par(self):
		if not self.one:
			self.one = True
		else:
			self.res += "\n"

	def on_line_end(self):
		self.res += "\n"


HANDLER = LatexHandler()
SYNTAX = markdown.make(HANDLER)
SYNTAX.add_token(ReplaceToken("latex_escape", {
	"%": "\\%",
	"{": "\\{",
	"}": "\\}"
}, SYNTAX.on_text))

PARSER = Parser(SYNTAX)

def test(text):
	HANDLER.reset()
	print("TEST: ", text)
	PARSER.parse_text(text)
	print("TEST: res = ", HANDLER.res)

test("ab{c%d}efg **123** 45 *ok* ko __1__ 2 _3_ 4")
test("123`ab`45")
test("123`5`6\n\nabcd")
test("123\n456")
