"""Module providing draw for Latex output."""

import os
import os.path
import ptah
import subprocess

class Drawer(ptah.Drawer):

	def __init__(self, album):

		# initialize
		ptah.Drawer.__init__(self, album)
		self.dx = -self.width / 2
		self.dy = -self.height / 2

		# generate the output
		root, ext = os.path.splitext(album.path)
		self.out_path = root + ".tex"
		self.out = open(self.out_path, "w")

		# write prolog
		self.out.write(
"""\\documentclass[a4paper]{book}
\\usepackage[utf8]{inputenc}
\\usepackage{graphicx}
\\usepackage{geometry}
\\usepackage{layout}
\\usepackage{tikz}
\\usepackage{adjustbox}
\\title{}
\\author{}
\\date{\\today}

\\geometry{
""")

		self.out.write("paperwidth = %smm,\n" % self.format.width)
		self.out.write("paperheight = %smm,\n" % self.format.height)
		self.out.write("top = %smm,\n" % self.format.top_margin)
		self.out.write("bottom = %smm,\n" % self.format.bottom_margin)
		self.out.write("left = %smm,\n" % self.format.oddside_margin)
		self.out.write("right = %smm" % self.format.evenside_margin)

		self.out.write(
"""}

\\begin{document}
""")

		# write pages
		for page in self.album.pages:
			self.out.write(
"""\\noindent\\adjustbox{max width=\\textwidth, max height=\\textheight}{\\begin{tikzpicture}
	\\node[draw, minimum width=\\textwidth, minimum height=\\textheight] {};
""")
			page.gen(self)
			self.out.write("""\\end{tikzpicture}}\n\n""")

		# write epilog
		self.out.write("""
\\end{document}
""")

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
		self.out.write(
"""
	\\node at(%smm, %smm) {\\includegraphics[
			width=%smm,
			height=%smm,
			keepaspectratio
		]{%s}};

""" % (
	x + w/2 + self.dx, x + h/2 + self.dy,
	w, h, path
))
