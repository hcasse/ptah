"""Module providing draw for Latex output."""

import os
import os.path
import ptah
from ptah import format
from ptah.graph import FontSize, Align, BorderStyle
from ptah.album import Album, Image, Text, Page
import ptah.font
import ptah.format
import ptah.props
from ptah import util
import subprocess
import sys
from ptah import graph
import ptah.text
from ptah import util
from PIL import Image

MINIATURE_WIDTH = 30
MINIATURE_HEIGHT = 40
MINIATURE_BACK = "yellow!50!white"


ALIGN = {
	Align.CENTER: 		lambda w, h: ("", 0, 0),
	Align.TOP: 			lambda w, h: ("anchor = north", 0, h/2),
	Align.TOP_RIGHT:	lambda w, h: ("anchor = north east", w/2, h/2),
	Align.RIGHT: 		lambda w, h: ("anchor = east", w/2, 0),
	Align.BOTTOM_RIGHT:	lambda w, h: ("anchor = south east", w/2, -h/2),
	Align.BOTTOM: 		lambda w, h: ("anchor = south", 0, -h/2),
	Align.BOTTOM_LEFT: 	lambda w, h: ("anchor = south west", -w/2, -h/2),
	Align.LEFT: 		lambda w, h: ("anchor = west", -w/2, 0),
	Align.TOP_LEFT: 	lambda w, h: ("anchor = north west", -w/2, h/2)
}


TEXT_ALIGN = {
	Align.CENTER: 		"center",
	Align.TOP:			"center",
	Align.TOP_RIGHT:	"right",
	Align.RIGHT:		"right",
	Align.BOTTOM_RIGHT:	"right",
	Align.BOTTOM:		"center",
	Align.BOTTOM_LEFT:	"left",
	Align.LEFT:			"left",
	Align.TOP_LEFT:		"left"
}


FONT_SIZES = {
	FontSize.XX_SMALL: 	"\\tiny",
	FontSize.X_SMALL: 	"\\footnotesize",
	FontSize.SMALL: 	"\\small",
	FontSize.MEDIUM: 	"",
	FontSize.LARGE: 	"\\Large",
	FontSize.X_LARGE: 	"\\LARGE",
	FontSize.XX_LARGE:	"\\HUGE"
}



BORDER_STYLES = {
	BorderStyle.NONE:	"",
	BorderStyle.SOLID:	"",
	BorderStyle.DOTTED:	"dotted",
	BorderStyle.DASHED:	"dashed",
	BorderStyle.DOUBLE:	"double"
}


PROLOG = \
"""
\\usepackage[utf8]{inputenc}
"""

class Drawer(graph.Drawer):

	def __init__(self, album = None):
		graph.Drawer.__init__(self, album)
		self.dx = self.width / 2.
		self.dy = self.height / 2.
		self.colors = {}
		self.packages = [
			"adjustbox",
			"geometry",
			"graphicx",
			"layout",
			"tikz",
			"xcolor",
			"moresize",
			"tcolorbox",
			"hyperref"
		]
		self.tikz_packages = {
			"patterns",
			"patterns.meta",
			"shapes.geometric",
			"shadows",
			"shadows.blur"
		}
		self.tcb_packages = {
			"skins"
		}
		self.doctype = "book"
		self.lmargin = album.format.oddside_margin
		self.rmargin = album.format.evenside_margin
		self.bmargin = album.format.bottom_margin
		self.tmargin = album.format.top_margin

		# text support
		self.text_syntax = ptah.text.Syntax()
		self.text_gen = None

	# Drawer functions
	def gen(self):
		self.gen_latex()
		self.gen_pdf()

	def gen_pdf(self):
		dir = self.album.get_base()
		if dir != "":
			cwd = os.path.abspath(os.getcwd())
			os.chdir(dir)
		rc = subprocess.run(
			"pdflatex %s" % os.path.basename(self.out_path),
			shell=True,
			stdin = subprocess.DEVNULL,
			stdout = sys.stdout if util.DEBUG else subprocess.DEVNULL,
			stderr = sys.stderr if util.DEBUG else subprocess.DEVNULL)
		if False:	#rc.returncode == 0:
			rc = subprocess.run(
				"pdflatex %s" % os.path.basename(self.out_path),
				shell=True,
				stdout = subprocess.DEVNULL,
				stderr = subprocess.DEVNULL)
		if dir != "":
			os.chdir(cwd)

	def gen_latex(self):
		"""Called to generate the output file."""

		# collect declaration
		background_color = self.album.background_color
		if background_color == None:
			self.declare_color("#FFFFFF")
		else:
			self.declare_color(background_color)
		for page in self.album.pages:
			page.declare(self)

		# generate the latex
		root, ext = os.path.splitext(self.album.path)
		self.out_path = root + ".tex"
		self.out = open(self.out_path, "w")
		write = self.out.write
		self.gen_declaration()
		write("\\begin{document}\n")
		self.gen_body()
		write("\\end{document}\n")
		self.out.close()

	def gen_body(self):
		write = self.out.write
		first = True
		for page in self.album.pages:
			if first:
				first = False
			else:
				write("\\newpage\n")

			# background color
			bg = page.background_color
			if bg == None:
				bg = "#FFFFFF"
			write("\\pagecolor{%s}\n" % self.get_color(bg))

			# begin tikz
			write("\\noindent\\begin{tikzpicture}\n")

			# background image
			if page.background_image != None:
				self.gen_background_image(page)

			# generate the content
			write("\\node[%sminimum width=%smm, minimum height=%smm, anchor=south west] at(%smm, %smm) {};\n"
				% (	"draw, fill=pink, " if util.DEBUG else "",
					self.page_width, self.page_height-0.2,
					-self.width/2 -self.lmargin, -self.height/2 -self.bmargin))
			if util.DEBUG:
				write("\\node[draw, minimum width=%smm, minimum height=%smm, fill=yellow] {};" % (self.width, self.height))
			page.gen(self)
			if util.DEBUG:
				write("\\draw[<->, thick, blue, overlay] (%smm, 0) -- ++(%smm,0);\n"
					% (-self.width/2, self.width))
				write("\\draw[<->, thick, blue, overlay] (%smm, 0) -- ++(%smm,0);\n"
					% (-self.width/2-self.lmargin, self.lmargin))
				write("\\draw[<->, thick, blue, overlay] (%smm, 0) -- ++(%smm,0);\n"
					% (self.width/2, self.lmargin))
				write("\\draw[<->, thick, blue, overlay] (0, %smm) -- ++(0,%smm);\n"
					% (-self.height/2, self.height))
				write("\\draw[<->, thick, blue, overlay] (0,%smm) -- ++(0,%smm);\n"
					% (-self.height/2, -self.bmargin))
				write("\\draw[<->, thick, blue, overlay] (0,%smm) -- ++(0,%smm);\n"
					% (self.height/2, self.tmargin))
			write("""\\end{tikzpicture}\n\n""")

			# even/odd page management
			self.lmargin, self.rmargin = self.rmargin, self.lmargin

	def gen_declaration(self):
		write = self.out.write

		# write prolog
		write("\\documentclass[a4paper]{%s}\n" % self.doctype)
		write(PROLOG)
		for pack in self.packages:
			write("\\usepackage{%s}\n" % pack)
		for pack in self.tikz_packages:
			write("\\usetikzlibrary{%s}\n" % pack)
		for pack in self.tcb_packages:
			write("\\tcbuselibrary{%s}\n" % pack)
		write("\\title{%s}\n" % self.album.title)
		write("\\author{%s}\n" % self.album.author)
		write("\\date{%s}\n" % self.album.date)

		# write geometry
		self.gen_geometry()

		# write colors
		for (col, name) in self.colors.items():
			write("\\definecolor{%s}{HTML}{%s}\n" % (name, col[1:]))

	def gen_geometry(self):
		write = self.out.write
		write("\\geometry{\n")
		write("paperwidth = %smm,\n" % self.format.width)
		write("paperheight = %smm,\n" % self.format.height)
		write("top = 0mm,\n")
		write("bottom = 0mm,\n")
		write("left = 0mm,\n")
		write("right = 0mm\n")
		write("}\n")

	def get_size(self, path):
		i = Image.open(path)
		return i.size

	def get_page_center(self):
		return (
			(-self.lmargin-self.width/2 + self.rmargin+self.width/2)/2,
			(-self.bmargin-self.height/2 + self.tmargin+self.height/2)/2
		)

	def get_bottom_left(self):
		return (
			-self.lmargin-self.width/2,
			-self.bmargin-self.height/2
		)

	def gen_background_image(self, page):
		write = self.out.write
		path = page.background_image

		if page.background_mode == ptah.Mode.FIT:
			cx, cy = self.get_page_center()
			write("\\node[overlay, inner sep=0] at(%smm, %smm) {"
				% (cx, cy))
			write("\\includegraphics[width=%smm, height=%smm, keepaspectratio]{%s}};"
				% (self.format.width, self.format.height, path))

		elif page.background_mode == ptah.Mode.STRETCH:
			write("\\node[overlay, inner sep=0, anchor=north west] at(%smm, %smm) {"
				% (-self.width/2-self.lmargin, self.height/2+self.tmargin))
			write("\\resizebox{%smm}{%smm}{\\includegraphics{%s}}};\n"
				% (self.format.width, self.format.height, path))

		elif page.background_mode == ptah.Mode.FILL:
			w, h = self.get_size(path)
			W, H = self.format.width, self.format.height
			# TODO manage align, scale, xshift, yshift
			if w/h < W/H:
				param = "width=\\paperwidth"
			else:
				param = "height=\\paperheight"
			cx, cy = self.get_page_center()
			write("\\node[overlay] at(%smm, %smm) {" % (cx, cy))
			write("\\includegraphics[%s, keepaspectratio]{%s}};"
				% (param, path));

		elif page.background_mode == ptah.Mode.TILE:
			x, y = self.get_bottom_left()
			write("\path[overlay, fill tile image=%s] (%smm, %smm) rectangle ++(%smm, %smm);\n"
				% (path, x, y, self.format.width, self.format.height));

	def border_props(self, style):
		if style.border_style == ptah.BorderStyle.NONE:
			return ""
		else:
			props = "draw=%s, inner sep = 0" \
				% self.get_color(style.border_color)
			if style.border_width == ptah.BorderWidth.MEDIUM:
				props += ", thick"
			elif style.border_width == ptah.BorderWidth.THICK:
				props += ", ultra thick"
			elif isinstance(style.border_width, graph.Length):
				props += ",line width=%smm" % style.border_width.get(1.)
			if style.border_style != ptah.BorderStyle.SOLID:
				props += ",%s" % BORDER_STYLES[style.border_style]
			return props

	def shadow_props(self, style):
		if style.shadow == ptah.Shadow.SIMPLE:
			print("simple")
			opacity = style.shadow_opacity
			if opacity == None:
				opacity = .25
			return ",drop shadow={" + \
				"fill=%s" % self.get_color(style.shadow_color) + \
				",opacity=%s" % opacity + \
				",shadow xshift=%smm" % style.shadow_xoffset + \
				",shadow yshift=%smm" % (-style.shadow_yoffset) + \
				"}"
		elif style.shadow == ptah.Shadow.FUZZY:
			print("fuzzy")
			opacity = style.shadow_opacity
			if opacity == None:
				opacity = 1.
			radius = (style.shadow_xoffset + style.shadow_xoffset) / 3.
			return ",blur shadow={" + \
				"fill=%s" % self.get_color(style.shadow_color) + \
				",opacity=%s" % opacity + \
				",shadow xshift=%smm" % style.shadow_xoffset + \
				",shadow yshift=%smm" % (-style.shadow_yoffset) + \
				", shadow blur radius=%smm" % radius + \
				",shadow blur steps=10" + \
				", shadow blur extra rounding=%smm" % radius + \
				"}"
		else:
			return ""

	def draw_border(self, x, y, W, H, style):
		if style.border_style != ptah.BorderStyle.NONE:
			self.out.write(
				"\\draw[%s] (%smm,%smm) rectangle ++(%smm,%smm);\n" %
				(self.border_props(style), x-W/2, y-H/2, W, H))

	def draw_border_around(self, name, style):
		if style.border_style != ptah.BorderStyle.NONE:
			self.out.write(
				"\\draw[%s] (%s.north west) rectangle (%s.south east);\n" %
				(self.border_props(style), name, name))

	def draw_image(self, path, box, style):
		write = self.out.write
		x, y = self.remap(box.centerx(), box.centery())
		W, H = box.w, box.h
		shadow = self.shadow_props(style)

		# draw the image
		if style.mode == ptah.Mode.FIT:
			anchor,dx, dy = ALIGN[style.align](W, H)
			write("\\node[%s%s,inner sep=0] at(%smm, %smm) (A) {" \
				% (anchor, shadow, x + dx, y + dy))
			write("\\includegraphics[width=%smm, height=%smm, keepaspectratio]{%s}"
				% (box.w, box.h, path));
			write("};\n")
			self.draw_border_around("A", style)

		elif style.mode == ptah.Mode.STRETCH:
			write("\\node at(%smm, %smm) {" % (x, y))
			write("\\resizebox{%smm}{%smm}{\\includegraphics{%s}}"
				% (box.w, box.h, path));
			write("};\n")
			self.draw_border(x, y, W, H, style)

		elif style.mode == ptah.Mode.FILL:

			# compute configuration
			w, h = self.get_size(path)
			anchor,dx, dy = ALIGN[style.align](W, H)
			if w/h < W/H:
				sw = W * style.scale
				param = "width=%smm" % sw
				if style.xshift != None:
					dx += style.xshift.get(sw)
				if style.yshift != None:
					sh = h * W / w * style.scale
					dy -= style.yshift.get(sh)
			else:
				sh = H * style.scale
				param = "height=%smm" % sh
				if style.horizontal_shift != None:
					sw = w * H / h * style.scale
					dx += style.horizontal_shift.get(sw)
				if style.vertical_shift != None:
					dy -= style.vertical_shift.get(sh)

			# generate the code
			write("\\begin{scope}\n")
			write("\\clip (%smm, %smm) rectangle(%smm, %smm);\n"
				% (x - W/2, y - H/2, x + W/2, y + H/2))
			write("\\node[%s] at(%smm, %smm) {"
				% (anchor, x + dx, y + dy))
			write("\\includegraphics[%s, keepaspectratio]{%s}"
				% (param, path));
			write("};\n")
			write("\\end{scope}\n")
			self.draw_border(x, y, W, H, style)

		else:
			print("ERROR: unknown mode", style.mode)
			exit(1)

	def remap(self, x, y):
		return (x - self.dx, self.dy - y)

	def draw_text(self, text, box, style):
		write = self.out.write
		x, y = self.remap(box.centerx(), box.centery())
		anc, dx, dy = ALIGN[style.text_align](box.w, box.h)
		align = TEXT_ALIGN[style.text_align]
		if util.DEBUG:
			write("\\node[minimum width=%smm, minimum height=%smm, draw] at(%smm, %smm) {};\n"
				% (box.w, box.h, x, y))
		write("\\node[")
		write("text width=%smm, " % box.w)
		font_size = FONT_SIZES[style.font_size]
		if font_size != "":
			write("font=%s, " % font_size)
		if util.DEBUG:
			write("draw, ")
		write(f"align={align}, {anc}, inner sep=0] at({x + dx}mm, {y + dy}mm) {{")
		if style.font is not None:
			style.font.use(self.out)
		parsed_text = self.text_syntax.parse(text)
		if self.text_gen is None:
			self.text_gen = ptah.text.Output(self.out)
		self.text_gen.output(parsed_text)
		write("};\n")

	def declare_color(self, color):
		"""Declare a new used color."""
		if color not in self.colors:
			self.colors[color] = "PTAHcolor%d" % len(self.colors)

	def get_color(self, color):
		"""Get the latex name for a color. Raise KeyError if the color
		has not been declared."""
		return self.colors[color]

	def use_package(self, package):
		"""Add a package."""
		if package not in self.packages:
			self.packages.append(package)

	def draw_miniature_image(self, label, box):
		x, y = self.remap(box.centerx(), box.centery())
		write = self.out.write
		write("\\node[")
		write("minimum width=%smm, " % box.w)
		write("minimum height=%smm, " % box.h)
		write("draw, fill=%s" % MINIATURE_BACK)
		write("] at(%smm, %smm) {};\n" % (x, y))
		write("\\node[opacity=.5, fill=lightgray, ellipse, minimum width=%smm, minimum height=%smm]"
			% (box.h * 0.8 / 1.5, box.h * 0.8));
		write(" at(%smm, %smm) {};\n" % (x, y))
		write("\\node at(%smm, %smm) {%s};\n" % (x, y, label))

	def draw_miniature_text(self, label, box):
		x, y = self.remap(box.centerx(), box.centery())
		write = self.out.write
		write("\\node[")
		write("minimum width=%smm, " % box.w)
		write("minimum height=%smm, " % box.h)
		write("pattern={Lines[line width=1mm, distance=1.5mm]},pattern color=lightgray")
		write("] at(%smm, %smm) {%s};\n" % (x, y, label))



DOC_SYNTAX = """
\\maketitle

\\tableofcontents

\\section{Syntax}
Album can be named \\texttt{album.ptah} or any \\textit{XXX}\\texttt{.ptah}
and must follows the scheme here:
\\begin{lstlisting}[showspaces=true]
title: TITLE
author: AUTHOR
date: DATE
format: FORMAT
pages:
  - name: PAGE1
    type: TYPE
    ...
  - name: PAGE2
    type: TYPE
    ...
...
\\end{lstlisting}


\\paragraph{Structured Properties}~

\\begin{lstlisting}[showspaces=true]
paths:
  - PATH1
  - PATH2
  ...
\\end{lstlisting}
Defines paths to retrive images.

\\begin{lstlisting}[showspaces=true]
styles:
  - name: NAME
    PROP1: VAL1
    PROP2: VAL2
    ...
  - name: NAME
  ...
\\end{lstlisting}
Defines named styles.

\\paragraph{Simple Properties:}~

"""


class DocDrawer(Drawer):

	def __init__(self):
		Drawer.__init__(self, Album("ptah.ptah"))
		self.album.pages = []

		for col in graph.HTML_COLORS.values():
			self.declare_color(col)
		self.use_package("listings")
		self.album.title = "Ptah Documentation"
		self.album.author = "H. Cassé $<$hug.casse@gmail.com$>$"
		self.album.date = "\\today"
		self.doctype = "article"

		self.mini = Album("mini")
		self.mini.format = format.Format(
			"mini",
			MINIATURE_WIDTH,
			MINIATURE_HEIGHT,
			2)
		self.mini_drawer = Drawer(self.mini)

		# text support
		self.text_syntax = ptah.text.Syntax()
		self.text_gen = None

	def gen(self):
		self.gen_latex()
		self.gen_pdf()
		self.gen_pdf()

	def gen_geometry(self):
		pass

	def write_text(self, text):
		parsed_text = self.text_syntax.parse(text)
		if self.text_gen is None:
			self.text_gen = ptah.text.Output(self.out)
		self.text_gen.output(parsed_text)

	def gen_body(self):
		write = self.out.write
		self.mini_drawer.out = self.out

		# album doc
		write(DOC_SYNTAX)
		write("\\begin{description}\n")
		write("\\setlength\\itemsep{-1mm}\n")
		for prop in Album.PROPS.values():
			write("\\item[\\texttt{%s}:]" % prop.id)
			self.write_text(prop.get_description())
			write("\n")
		write("\\end{description}\n")

		# generate format list
		write("\\section{Formats}\n")
		write("\\begin{tabular}{|c|c|c|c|c|c|c|}\n")
		write("\\hline\n")
		write("& Size & & Margins & & & \\\\")
		write("\\hline\n")
		write("Name & Width & Height & Top & Bottom & Left & Right \\\\")
		write("\\hline\hline\n")
		for fmt in ptah.format.FORMATS.values():
			write("%s & %s & %s & %s & %s & %s & %s \\\\"
				% (
					fmt.name, fmt.width, fmt.height,
					fmt.top_margin, fmt.bottom_margin,
					fmt.oddside_margin, fmt.evenside_margin
				))
		write("\\hline\n")
		write("\\end{tabular}\n\n")
		write("Size in mm.\n")

		# generate pages
		write("\\section{Page types}\n")
		for page in util.PAGE_MAP.values():
			inst = page(self.mini)

			# dump miniature
			write("\\noindent\\begin{minipage}{.3\\textwidth}\n")
			write("\\begin{tikzpicture}\n")
			write("\\node[minimum width=%smm, minimum height=%smm, draw] {};\n"
				% (MINIATURE_WIDTH, MINIATURE_HEIGHT))
			page.gen_miniature(self.mini_drawer)
			write("\\end{tikzpicture}\n")
			write("\\end{minipage}\n")

			# dump properties
			write("\\begin{minipage}{.6\\textwidth}\n")
			write("\\paragraph{Type:} %s\n" % page.NAME)
			write("\\begin{description}\n")
			write("\\setlength\\itemsep{-1mm}\n")
			counts = {}
			for frame in inst.get_content():
				cls = frame.__class__
				try:
					counts[cls] += 1
				except KeyError:
					counts[cls] = 1
			for prop in page.PROPS:
				write(f"\\item[{prop.id}:] {prop.get_description()}\n")
			for (cls, cnt) in counts.items():
				if cnt > 1:
					for prop in cls.PROPS:
						write(f"\\item[{prop.id}\\#i:] {prop.get_description()}\n")
			write("\\end{description}\n")
			write("\\end{minipage}\n\n\\bigskip")

		# dump text
		write("\\section{Text format}\n")
		write("Subset of \\href{https://www.markdownguide.org/}{MarkDown} format:\n")
		write("\\begin{description}\n")
		write("\\item[**text**, \_\_text\_\_] Bold.")
		write("\\item[*text*, \_text\_] Italic.")
		write("\\item[blank line] New paragraph.")
		write("\\end{description}\n")
		write("More to come.")

		# dump fonts
		write("\\section{Fonts}\n")
		for font in ptah.font.get_fonts():
			if font.avail:
				write(f"\paragraph{{{font.name}}}:~\n\n{{")
				font.use(self.out)
				write("ABCDEFGHIJKLMNOPQRSTUVWXYZ\n\n")
				write("abcdefghijklmnopqrstuvwxyz}\n\n")

		# dump colors
		write("\\section{Colors}\n")
		write("Colors follows HTML notation: \\texttt{\\#RRGGBB} with R, G, B hexadecimal.\n")
		write("\\paragraph{Named colors}~~~\n\n")
		write("\\bigskip\\small\\begin{tabular}{clclclcl}\n")
		n = 0
		for (name, col) in graph.HTML_COLORS.items():
			write("{\\color{%s}\\rule{8mm}{4mm}} & %s" %
				(self.get_color(col), name))
			n = n + 1
			if n == 4:
				write("\\\\\n")
				n = 0
			else:
				write(" & ")
		write("\\end{tabular}\n")


def gen_doc():
	"""Generate the documentation."""
	ptah.font.check()
	drawer = DocDrawer()
	drawer.gen()
