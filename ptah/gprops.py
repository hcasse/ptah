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

"""Graphic properties."""

from ptah.props import parse_union, parse_penum, parse_length, parse_float, \
	parse_font, parse_color, parse_percent, \
	Property, ColorProperty, ImageProperty, StringProperty, \
	enum_prop
from ptah.graph import Mode, Align, BorderStyle, BorderWidth, Shadow, FontSize
from ptah.util import enum_list


parse_border_width = parse_union([
	parse_penum(BorderWidth),
	parse_length
])
parse_border_style = parse_penum(BorderStyle)
parse_shadow = parse_penum(Shadow)


# background properties
BACKGROUND_COLOR_PROP = ColorProperty(
	"background-color", "Color for background.")
BACKGROUND_IMAGE_PROP = ImageProperty(
	"background-image", "background image")
BACKGROUND_MODE_PROP = enum_prop("background-mode", "Background image mode: %s.", Mode)

# image properties
MODE_PROP = enum_prop("mode", "image mode, one of %s.", Mode, Mode.FIT)
ALIGN_PROP = enum_prop("align", "image alignment, one of %s.", Align, Align.CENTER)
IMAGE_PROP = ImageProperty("image", "image")
SCALE_PROP = Property(
	"scale",
	"image scale.",
	parse_float,
	default = 1.)
HORIZONTAL_SHIFT_PROP = Property(
	"horizontal-shift",
	"shift in % of the image width.",
	parse_length)
VERTICAL_SHIFT_PROP = Property(
	"vertical-shift",
	"shift in % of the image height.",
	parse_length)

# text properties
TEXT_ALIGN_PROP = enum_prop("text-align", "text alignment among %s.", Align)
TEXT_PROP = StringProperty("text", "page text.")
TEXT_COLOR_PROP = Property("text-color", "color fot the text.", parse_color)
FONT_SIZE_PROP = enum_prop("font-size", "font size: %s.", FontSize, FontSize.MEDIUM)
FONT_PROP = Property("font", "font name", parse_font)

# border properties
BORDER_STYLE = enum_prop("border-style", "style for the border: %s.", BorderStyle)
BORDER_COLOR = Property(
	"border-color",
	"Color for border of an image.",
	parse_color)
BORDER_WIDTH = enum_prop("border-width","width of border lines: length or one of %s.",
	BorderWidth, BorderWidth.MEDIUM)

# shadow properties
SHADOW_STYLE = enum_prop("shadow", "select the shadow type among %s.", Shadow, Shadow.NONE)
SHADOW_XOFFSET = Property(
	"shadow-xoffset",
	"shadow horizontal offset.",
	parse_length,
	default = 1.5)
SHADOW_YOFFSET = Property(
	"shadow-yoffset",
	"shadow vertical offset.",
	parse_length,
	default = 1.5)
SHADOW_COLOR = Property(
	"shadow-color",
	"shadow color.",
	parse_color,
	default = "#000000")
SHADOW_OPACITY = Property(
	"shadow-opacity",
	"shadow opacity as percent value (100\\% opaque, 0\\% transparent).",
	parse_percent)


