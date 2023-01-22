"""Basic collection of pages."""

import os
import ptah

def not_none(x, msg):
	if x == None:
		raise util.CheckError("msg")

def one_of(val, vals, id):
	val = val.lower()
	for i in range(0, len(vals)):
		if val == vals[i]:
			return i
	raise util.CheckError("%s must be one of %s" % (id, vals))

def check_image(path, page):
	if not os.path.exists(os.path.join(page.album.get_base(), path)):
		raise util.CheckError("no image on path '%s'" % path)

def get_image(path, page):
	check_image(path, page)
	page.image = path

def get_image1(path, page):
	check_image(path, page)
	page.image1 = path

def get_image2(path, page):
	check_image(path, page)
	page.image2 = path

def get_orientation(val, page):
	page.orientation = one_of(
		val,
		["vertical", "horizontal"],
		"orientation")


# Center page
class CenterPage(ptah.Page):

	PROPS = {
		"image": get_image
	}

	def __init__(self):
		ptah.Page.__init__(self)
		self.image = None

	def check(self):
		not_none(self.image, "no image provided")

	def get_props(self):
		return CenterPage.PROPS

	def gen(self, drawer):
		drawer.draw_image(
			self.image,
			0, 0,
			drawer.width, drawer.height
		)


# Duo page
class DuoPage(ptah.Page):

	PROPS = {
		"image1": get_image1,
		"image2": get_image2,
		"orientation": get_orientation
	}

	def __init__(self):
		ptah.Page.__init__(self)
		self.image1 = None
		self.image2 = None
		self.orientation = 0

	def check(self):
		not_none(self.image1, "no image1 provided")
		not_none(self.image2, "no image2 provided")

	def get_props(self):
		return DuoPage.PROPS

	def gen(self, drawer):
		if self.orientation == 0:
			h = (drawer.height - drawer.sep) / 2
			x1 = 0
			y1 = h + drawer.sep
			x2 = 0
			y2 = 0
			w = drawer.width
		else:
			w = (drawer.width - drawer.sep) / 2
			x1 = w + drawer.sep
			y1 = 0
			x2 = 0
			y2 = 0
			h = drawer.height
		drawer.draw_image(self.image1, x1, y1, w, h)
		drawer.draw_image(self.image2, x2, y2, w, h)
	

# Page initialization
ptah.PAGE_MAP["center"] = CenterPage
ptah.PAGE_MAP["duo"] = DuoPage
