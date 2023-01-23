"""Module providing draw for Latex output."""

import os
import os.path
import ptah
import ptah.format
import subprocess

DEBUG = False
MINIATURE_WIDTH = 30
MINIATURE_HEIGHT = 40

PROLOG = \
"""
\\usepackage[utf8]{inputenc}
\\usepackage{graphicx}
\\usepackage{geometry}
\\usepackage{layout}
\\usepackage{tikz}
\\usepackage{adjustbox}
"""

class Drawer(ptah.Drawer):

	def __init__(self, album = None):

		# initialize
		ptah.Drawer.__init__(self, album)
		self.dx = self.width / 2.
		self.dy = self.height / 2.

		# generate the output
		root, ext = os.path.splitext(album.path)
		self.out_path = root + ".tex"
		self.out = open(self.out_path, "w")

		# write prolog
		self.out.write("\\documentclass[a4paper]{book}\n")
		self.out.write(PROLOG)
		self.out.write("\\title{}\n")
		self.out.write("\\author{}\n")
		self.out.write("\\date{\\today}\n")

		# write geometry
		self.out.write("\\geometry{\n")
		self.out.write("paperwidth = %smm,\n" % self.format.width)
		self.out.write("paperheight = %smm,\n" % self.format.height)
		self.out.write("top = %smm,\n" % self.format.top_margin)
		self.out.write("bottom = %smm,\n" % self.format.bottom_margin)
		self.out.write("left = %smm,\n" % self.format.oddside_margin)
		self.out.write("right = %smm\n" % self.format.evenside_margin)
		self.out.write("}\n")

		# write the body
		self.out.write("\\begin{document}\n")
		for page in self.album.pages:
			self.out.write(
"""\\noindent\\adjustbox{max width=\\textwidth, max height=\\textheight}{\\begin{tikzpicture}
\\node[%sminimum width=\\textwidth, minimum height=\\textheight] {};"""
			% ("draw, " if DEBUG else ""))
			page.gen(self)
			self.out.write("""\\end{tikzpicture}}\n\n""")

		# write epilog
		self.out.write("\\end{document}\n")

		# close all
		self.out.close()

		# generate the PDF
		dir = album.get_base()
		if dir != "":
			cwd = os.path.abspath(os.getcwd())
			os.chdir(dir)
		subprocess.run(
			"pdflatex %s" % os.path.basename(self.out_path),
			shell=True)
		if dir != "":
			os.chdir(cwd)



	def draw_image(self, path, x, y, w, h):
		x, y = self.remap(x, y)
		self.out.write("\\node at(%smm, %smm) {" % (x+w/2., y-h/2))
		self.out.write("\\includegraphics[width=%smm, height=%smm, keepaspectratio]{%s}"
			% (w, h, path));
		self.out.write("};\n")

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


def gen_doc(props):
	"""Generate the documentation."""
	album = ptah.Album("ptah.ptah")
	album.format = ptah.format.Format("doc",
		MINIATURE_WIDTH,
		MINIATURE_HEIGHT,
		2)
	drawer = Drawer(album)
	
	with open("ptah.tex", "w") as out:
		drawer.out = out

		# generate prolog
		out.write("\\documentclass[a4paper]{article}\n")
		out.write(PROLOG)
		out.write("\\usepackage{listings}\n")
		out.write("\\title{Ptah Documentation}\n")
		out.write("\\author{H. Cassé $<$hug.casse@gmail.com$>$}\n")
		out.write("\\date{\\today}\n")
		out.write("\\begin{document}\n")

		# generate syntax
		out.write(
"""

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
""")

		out.write("\\begin{description}\n")
		for prop in props.values():
			out.write("\\item[%s] %s\n" % (prop.id, prop.get_description()))
		out.write("\\end{description}\n")

		# generate format list
		out.write("\\section{Formats}\n")
		out.write("\\begin{tabular}{|c|c|c|c|c|c|c|}\n")
		out.write("\\hline\n")
		out.write("& Size & & Margins & & & \\\\")
		out.write("\\hline\n")
		out.write("Name & Width & Height & Top & Bottom & Left & Right \\\\")
		out.write("\\hline\hline\n")
		for fmt in ptah.format.FORMATS.values():
			out.write("%s & %s & %s & %s & %s & %s & %s \\\\"
				% (
					fmt.name, fmt.width, fmt.height,
					fmt.top_margin, fmt.bottom_margin,
					fmt.oddside_margin, fmt.evenside_margin
				))
		out.write("\\hline\n")
		out.write("\\end{tabular}\n\n")
		out.write("Size in mm.\n")

		# generate pages
		out.write("\\section{Page types}\n")
		for page in ptah.PAGE_MAP.values():

			# dump miniature
			out.write("\\noindent\\begin{minipage}{.3\\textwidth}\n")
			out.write("\\begin{tikzpicture}\n")
			out.write("\\node[minimum width=%smm, minimum height=%smm, draw] {};\n"
				% (MINIATURE_WIDTH, MINIATURE_HEIGHT))
			page.gen_miniature(drawer)
			out.write("\\end{tikzpicture}\n")
			out.write("\\end{minipage}\n")

			# dump properties
			out.write("\\begin{minipage}{.6\\textwidth}\n")
			out.write("\\paragraph{Type:} %s\n" % page.NAME)
			out.write("\\begin{description}\n")
			for prop in page.PROPS.values():
				print(prop)
				out.write("\\item[%s] %s\n" % (prop.id, prop.get_description()))
			out.write("\\end{description}\n")
			out.write("\\end{minipage}\n\n\\bigskip")

		# generate epilog
		out.write("\\end{document}\n")

	# run the generation
	subprocess.run("pdflatex ptah.tex", shell=True)

	# open the file at the end
