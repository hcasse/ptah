"""Markdown syntax support."""

from ptah.wiki import *

class MarkdownSyntax(Syntax):

	def __init__(self, handler):
		Syntax.__init__(self, "markdown", handler, [

			StyleEndToken("bold_end", "(?<=\S)(\\*\\*|__)", TYPE_BOLD),
			StyleBeginToken("bold", "(\\*\\*|__)(?=\S)", TYPE_BOLD,
				handler.begin_style, handler.end_style),

			StyleEndToken("italic_end", "(?<=\S)[*_]", TYPE_ITALIC),
			StyleBeginToken("italic", "[*_](?=\S)", TYPE_ITALIC,
				handler.begin_style, handler.end_style),

			StyleToken("code", "`", TYPE_CODE,
				handler.begin_style, handler.end_style)
		],
		[
			FunToken("line_end", "^$", self.on_par_end)
		])

	def on_par_end(self, word, parser):
		parser.pop_to(LEVEL_PAR)
		return ""

def make(handler):
	return MarkdownSyntax(handler)
