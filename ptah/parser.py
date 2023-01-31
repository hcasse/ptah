"""Generic parser for wiki-like syntax."""

import re
import sys

LEVEL_DOC = 0
LEVEL_H1 = 1
LEVEL_H2 = 2
LEVEL_H3 = 3
LEVEL_H4 = 4
LEVEL_H5 = 5
LEVEL_PAR = 6
LEVEL_WORD = 7

TYPE_DOC = 0
TYPE_HEADER = 1
TYPE_PAR = 2

TYPE_STYLE = 100
TYPE_BOLD = 100
TYPE_ITALIC = 101
TYPE_EMPH = 102
TYPE_CODE = 103
TYPE_ULINE = 104
TYPE_SUB = 105
TYPE_SUP = 106


class Handler:
	"""Handler of parsing actions."""

	def on_text(self, text):
		"""Called when simple text is found."""
		pass


class Token:
	"""A token, i.e. a family of words scanned by an RE."""

	def __init__(self, name, re):
		self.name = name
		self.re = re

	def on_found(self, word, parser):
		"""Action called when the token is found."""
		pass


class Syntax:
	"""A collection of tokens."""

	def __init__(self, name, handler, tokens):
		self.name = name
		self.handler = handler
		self.tokens = tokens
		self.map = {}
		self.re = None
		for token in tokens:
			token.syntax = self

	def add_token(self, token):
		self.tokens.append(token)
		token.syntax = self
		self.re = None

	def remove_token(self, token):
		self.tokens.remove(token)
		token.syntax = None
		self.re = None

	def get_re(self):
		if self.re == None:
			self.re = ""
			if self.tokens != []:
				t = self.tokens[0]
				self.re = "(?P<%s>%s)" % (t.name, t.re)
				self.map[t.name] = t
				for t in self.tokens[1:]:
					self.re = "%s|(?P<%s>%s)" % (self.re, t.name, t.re)
					self.map[t.name] = t
			print("DEBUG:", self.re)
			self.re = re.compile(self.re)
		return self.re
			
	def on_token(self, match, parser):
		self.map[match.lastgroup].on_found(match[0], parser)

	def on_text(self, text, parser):
		"""Called when simple text is found."""
		self.handler.on_text(text)


class Context:
	"""A parsing context corresponding to sub-languages or grammar level."""

	def __init__(self, syntax, level, type):
		self.syntax = syntax
		self.level = level
		self.type = type

	def on_pop(self, parser):
		"""Called when the context is popped."""
		pass

	def on_push(self, parser):
		"""Calle when the context is pushed."""
		pass


class Parser:
	"""Parser of wiki-like text."""

	def __init__(self, syntax):
		self.stack = [Context(syntax, LEVEL_DOC, TYPE_DOC)]

	def parse_text(self, text):
		p = 0

		# parse the text
		while p < len(text):
			m = self.stack[-1].syntax.get_re().search(text, p)
			print("DEBUG:", m)
			if m ==  None:
				self.stack[-1].syntax.on_text(text[p:], self)
				break
			else:
				if p < m.start():
					self.stack[-1].syntax.on_text(text[p:m.start()], self)
					self.stack[-1].syntax.on_token(m, self)
					p = m.end()

		# pop the content of the stack
		while len(self.stack) != 1:
			self.stack[-1].on_pop(self)
			self.stack.pop()

	def push_exclusive(self, context):
		"""Push a context excluding context of higher or same level."""
		while context.level <= self.stack[-1].level:
			self.stack[-1].on_pop(self)
			self.stack.pop()
		self.stack.append(context)
		context.on_push(self)

	def push_inclusive(self, context):
		"""Push a context excluding context of higher level but keeping
		conext of the same level."""
		while context.level < self.stack[-1].level:
			self.stack[-1].on_pop(self)
			self.stack.pop()
		self.stack.append(context)
		context.on_push(self)

	def pushpop_style(self, context):
		"""Push the context inclusively unless the context is already
		pushed i.e. mixed with other context of same level."""
		if not self.pop_style(context.level, context.type):
			self.stack.append(context)
			context.on_push(self)

	def pop_style(self, level, type):
		"""Perform the pop of a style-like context.
		Return True if pop is successful, False else."""

		# pop higher contexts
		while level < self.stack[-1].level:
			self.stack[-1].on_pop(self)
			self.stack.pop()

		# look for same context
		i = len(self.stack) - 1
		while i > 0 and level == self.stack[i].level:
			if self.stack[i].type == type:
				for j in range(len(self.stack)-1, i-1, -1):
					self.stack[i].on_pop(self)
				del self.stack[i]
				for j in range(i, len(self.stack)):
					self.stack[i].on_push(self)
				return True
			i = i - 1
		return False


class SimpleToken(Token):
	"""A token that call a function when it is found."""

	def __init__(self, name, re, fun):
		Token.__init__(self, re)

	def on_found(self, word, parser):
		self.fun(word, parser)


class StyleContext(Context):

	def __init__(self, token):
		Context.__init__(self, token.syntax, LEVEL_WORD, token.type)
		self.token = token

	def on_push(self, parser):
		self.token.begin(self.token.type)

	def on_pop(self, parser):
		self.token.end(self.token.type)


class StyleToken(Token):

	def __init__(self, name, re, type, begin, end):
		Token.__init__(self, name, re)
		self.type = type
		self.begin = begin
		self.end = end

	def on_found(self, word, parser):
		parser.pushpop_style(StyleContext(self))


class ReplaceToken(Token):
	"""A token that allows to perform simple replacements."""

	def __init__(self, name, map, fun):
		r = "|".join([re.escape(x) for x in map.keys()])
		Token.__init__(self, name, r)
		self.map = map
		self.fun = fun

	def on_found(self, word, parser):
		self.fun(self.map[word], parser)


class StyleBeginToken(Token):
	"""A token begining a style."""

	def __init__(self, name, re, type, begin, end):
		Token.__init__(self, name, re)
		self.type = type
		self.begin = begin
		self.end = end

	def on_found(self, word, parser):
		parser.push_inclusive(StyleContext(self))


class StyleEndToken(Token):
	"""Token ending a style."""

	def __init__(self, name, re, type):
		Token.__init__(self, name, re)
		self.type = type

	def on_found(self, word, parser):
		if not parser.pop_style(LEVEL_WORD, self.type):
			self.syntax.handler.on_text(word)


# Testing
class LatexHandler(Handler):
	STYLES = {
		TYPE_BOLD: "\\textbf{",
		TYPE_ITALIC: "\\textit{",
		TYPE_CODE: "\\texttt{"
	}

	def __init__(self):
		self.res = ""

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
		])

		

HANDLER = LatexHandler()
SYNTAX = MarkdownSyntax(HANDLER)
SYNTAX.add_token(ReplaceToken("latex_escape", {
	"%": "\\%",
	"{": "\\{",
	"}": "\\}"
}, SYNTAX.on_text))

PARSER = Parser(SYNTAX)

def test(text):
	HANDLER.res = ""
	print("BEFORE: ", text)
	PARSER.parse_text(text)
	print("DEBUG: res = ", HANDLER.res)

test("ab{c%d}efg **123** 45 *ok* ko __1__ 2 _3_ 4")
test("123`ab`45")
