"""Module providing draw for Latex output."""

import os
import os.path
import ptah
import ptah.format
import ptah.props
import subprocess
from PIL import Image

DEBUG = False
MINIATURE_WIDTH = 30
MINIATURE_HEIGHT = 40

ALIGN = [
	lambda w, h: ("", 0, 0),
	lambda w, h: ("anchor = north", 0, h/2),
	lambda w, h: ("anchor = north east", w/2, h/2),
	lambda w, h: ("anchor = east", w/2, 0),
	lambda w, h: ("anchor = south east", w/2, -h/2),
	lambda w, h: ("anchor = south", 0, -h/2),
	lambda w, h: ("anchor = south west", -w/2, -h/2),
	lambda w, h: ("anchor = west", -w/2, 0),
	lambda w, h: ("anchor = north west", -w/2, h/2)
]

PROLOG = \
"""
\\usepackage[utf8]{inputenc}
"""

class Drawer(ptah.Drawer):

	def __init__(self, album = None):
		ptah.Drawer.__init__(self, album)
		self.dx = self.width / 2.
		self.dy = self.height / 2.
		self.colors = {}
		self.packages = [
			"adjustbox",
			"geometry",
			"graphicx",
			"layout",
			"tikz",
			"xcolor"
		]
		self.doctype = "book"

	def gen(self):

		# generate Latex file
		self.gen_latex()

		# generate PDF file
		dir = self.album.get_base()
		if dir != "":
			cwd = os.path.abspath(os.getcwd())
			os.chdir(dir)
		subprocess.run(
			"pdflatex %s" % os.path.basename(self.out_path),
			shell=True,
			capture_output = True)
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

			# set background
			bg = page.background_color
			if bg == None:
				bg = self.album.background_color
				if bg == None:
					bg = "#FFFFFF"
			write("\\pagecolor{%s}\n" % self.get_color(bg))

			# generate the content
			write(
"""\\noindent\\adjustbox{max width=\\textwidth, max height=\\textheight}{\\begin{tikzpicture}
\\node[%sminimum width=\\textwidth, minimum height=\\textheight] {};
"""
			% ("draw, " if DEBUG else ""))
			page.gen(self)
			write("""\\end{tikzpicture}}\n\n""")

	def gen_declaration(self):
		write = self.out.write
		
		# write prolog
		write("\\documentclass[a4paper]{%s}\n" % self.doctype)
		write(PROLOG)
		for pack in self.packages:
			write("\\usepackage{%s}\n" % pack)
		write("\\title{%s}\n" % self.album.title)
		write("\\author{%s}\n" % self.album.author)
		write("\\date{%s}\n" % self.album.date)

		# write geometry
		write("\\geometry{\n")
		write("paperwidth = %smm,\n" % self.format.width)
		write("paperheight = %smm,\n" % self.format.height)
		write("top = %smm,\n" % self.format.top_margin)
		write("bottom = %smm,\n" % self.format.bottom_margin)
		write("left = %smm,\n" % self.format.oddside_margin)
		write("right = %smm\n" % self.format.evenside_margin)
		write("}\n")

		# write colors
		for (col, name) in self.colors.items():
			write("\\definecolor{%s}{HTML}{%s}\n" % (name, col[1:]))

	def get_size(self, path):
		i = Image.open(path)
		return i.size

	def draw_image(self, path, box, style):
		write = self.out.write
		x, y = self.remap(box.centerx(), box.centery())
		W, H = box.w, box.h

		if style.mode == ptah.MODE_FIT:
			anchor,dx, dy = ALIGN[style.align](W, H)
			write("\\node[%s] at(%smm, %smm) {"
				% (anchor, x + dx, y + dy))
			write("\\includegraphics[width=%smm, height=%smm, keepaspectratio]{%s}"
				% (box.w, box.h, path));
			write("};\n")

		elif style.mode == ptah.MODE_STRETCH:
			write("\\node at(%smm, %smm) {" % (x, y))
			write("\\resizebox{%smm}{%smm}{\\includegraphics{%s}}"
				% (box.w, box.h, path));
			write("};\n")

		elif style.mode == ptah.MODE_FILL:

			# compute configuration
			w, h = self.get_size(path)
			anchor,dx, dy = ALIGN[style.align](W, H)
			if w/h < W/H:
				sw = W * style.scale
				param = "width=%smm" % sw
				if style.xshift != None:
					dx += sw * style.xshift / 100.
				if style.yshift != None:
					sh = h * W / w * style.scale
					dy -= sh * style.yshift / 100.
			else:
				sh = H * style.scale
				param = "height=%smm" % sh
				if style.xshift != None:
					sw = w * H / h * style.scale
					dx += sw * style.xshift / 100.
				if style.yshift != None:
					dy -= sh * style.yshift / 100.

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
			
		else:
			print("ERROR: unknown mode", style.mode)
			exit(1)
			
	def remap(self, x, y):
		return (x - self.dx, self.dy - y)

	def draw_box(self, x, y, w, h, draw = "black", fill = None):
		x, y = self.remap(x, y)
		self.out.write("\\node[")
		self.out.write("minimum width=%smm, " % w)
		self.out.write("minimum height=%smm, " % h)
		if draw != None:
			self.out.write("draw=%s, " % draw)
		if fill != None:
			self.out.write("fill=%s, " % fill)
		self.out.write("] at(%smm, %smm) {};\n" % (x+w/2., y-h/2.))

	def draw_text(self, x, y, w, h, text):
		x, y = self.remap(x, y)
		self.out.write("\\node[")
		self.out.write("minimum width=%smm, " % w)
		self.out.write("minimum height=%smm, " % h)
		self.out.write("] at(%smm, %smm) {%s};\n"
			% (x+w/2., y-h/2., text))

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

DOC_SYNTAX = """
\\maketitle

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
"""


class DocDrawer(Drawer):

	def __init__(self):
		Drawer.__init__(self, ptah.Album("ptah.ptah"))
		self.album.pages = []

		for col in ptah.props.HTML_COLORS.values():
			self.declare_color(col)
		self.use_package("listings")
		self.title = "Ptah Documentation"
		self.author = "H. Cassé $<$hug.casse@gmail.com$>$"
		self.date = "\\today"
		self.doctype = "article"

		self.mini = ptah.Album("mini")
		self.mini.format = ptah.format.Format(
			"mini",
			MINIATURE_WIDTH,
			MINIATURE_HEIGHT,
			2)
		self.mini_drawer = Drawer(self.mini)
		
	def gen_body(self):
		write = self.out.write
		self.mini_drawer.out = self.out

		# album doc
		write(DOC_SYNTAX)
		write("\\paragraph{Properties}\n")
		write("\\begin{description}\n")
		write("\\setlength\\itemsep{-1mm}\n")
		for prop in ptah.ALBUM_PROPS.values():
			write("\\item[%s] %s\n" % (prop.id, prop.get_description()))
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
		for page in ptah.PAGE_MAP.values():

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
			for prop in page.PROPS.values():
				write("\\item[%s] %s\n" % (prop.id, prop.get_description()))
			write("\\end{description}\n")
			write("\\end{minipage}\n\n\\bigskip")

		# dump colors
		write("\\section{Colors}\n")
		write("Colors follows HTML notation: \\texttt{\\#RRGGBB} with R, G, B hexadecimal.\n")
		write("\\paragraph{Named colors}~~~\n\n")
		write("\\bigskip\\small\\begin{tabular}{clclclcl}\n")
		n = 0
		for (name, col) in ptah.props.HTML_COLORS.items():
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
	drawer = DocDrawer()
	drawer.gen()
