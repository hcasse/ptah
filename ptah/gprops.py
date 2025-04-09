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

from ptah.props import type_union, type_penum, type_length, type_float, \
	type_font, implies_set, type_color, type_percent, \
	Property, ColorProperty, ImageProperty, StringProperty
from ptah.graph import Mode, Align, BorderStyle, BorderWidth, Shadow, FontSize
from ptah.util import enum_list


border_width_type = type_union([
	type_penum(BorderWidth),
	type_length
])
border_style_type = type_penum(BorderStyle)
shadow_type = type_penum(Shadow)


# background properties
BACKGROUND_COLOR_PROP = ColorProperty(
	"background-color", "Color for background.")
BACKGROUND_IMAGE_PROP = ImageProperty(
	"background-image", "background image")
BACKGROUND_MODE_PROP = Property("background-mode",
	"Background image mode.", type_penum(Mode))

# image properties
MODE_PROP = Property(
	"mode",
	f"image mode, one of {enum_list(Mode)}.",
	type_penum(Mode),
	default = Mode.FIT)
ALIGN_PROP = Property(
	"align",
	f"image alignment, one of {enum_list(Align)}",
	type_penum(Align),
	default = Align.CENTER)
IMAGE_PROP = ImageProperty("image", "image")
SCALE_PROP = Property(
	"scale",
	"image scale.",
	type_float,
	default = 1.)
HORIZONTAL_SHIFT_PROP = Property(
	"horizontal-shift",
	"shift in % of the image width.",
	type_length)
VERTICAL_SHIFT_PROP = Property(
	"vertical-shift",
	"shift in % of the image height.",
	type_length)

# text properties
TEXT_ALIGN_PROP = Property("text-align", f"Text alignment among {enum_list(Align)}.", type_penum(Align))
TEXT_PROP = StringProperty("text", "Page text.")
FONT_SIZE_PROP = Property("font-size", "font size.", type_penum(FontSize))
FONT_PROP = Property("font", "font name", type_font)

# border properties
BORDER_STYLE = Property(
	"border-style",
	"Style for the border.",
	border_style_type,
	default = BorderStyle.NONE
)
BORDER_COLOR = Property(
	"border-color",
	"Color for border of an image.",
	type_color,
	default = "#000000",
	implies = implies_set(BORDER_STYLE, BorderStyle.NONE, BorderStyle.SOLID))
BORDER_WIDTH = Property(
	"border-width",
	f"width of border lines: length or one of {enum_list(BorderWidth)}.",
	border_width_type,
	default = BorderWidth.MEDIUM,
	implies = implies_set(BORDER_STYLE, BorderStyle.NONE, BorderStyle.SOLID))

# shadow properties
SHADOW_STYLE = Property(
	"shadow",
	f"select the shadow type among {enum_list(Shadow)}.",
	shadow_type,
	default = Shadow.NONE)
SHADOW_XOFFSET = Property(
	"shadow-xoffset",
	"shadow horizontal offset.",
	type_length,
	default = 1.5)
SHADOW_YOFFSET = Property(
	"shadow-yoffset",
	"shadow vertical offset.",
	type_length,
	default = 1.5)
SHADOW_COLOR = Property(
	"shadow-color",
	"shadow color.",
	type_color,
	default = "#000000")
SHADOW_OPACITY = Property(
	"shadow-opacity",
	"shadow opacity as percent value (100% opaque, 0% transparent).",
	type_percent)


