# Ptah generator

## To test

Set the `PYTHONPATH` to the top source directory:

	export PYTHONPATH=$PYTHONPATH:$PWD


## To Do

[ ] add option to generate one or several pages

[x] Set up hierarchycal model for properties.
[x] "default" entry properties.
[x] "styles" entry.
[x] 'style" support in pages and so on.

[ ] Separate common options from page relative options.
[ ] Add more page models.
[ ] Add more format models.
[x] Add shadow/glow style.
[ ] Add glow style.
[x] Add font selection.
[ ] Improve title page with bigger page.

[x] Add more Markdown syntax to text.


## Latex

### \includegrahics

[https://latexref.xyz/_005cincludegraphics.html]

* scale=VALUE
* width=SIZE
* height= SIZE
* keepaspectratio
* viewport=X1 Y1 X2 Y2
* trim=XL1 YL1 XL2 YL2
* bb= X1 Y1 X2 Y2

### Fonts

[Using fonts](https://tex.stackexchange.com/questions/25249/how-do-i-use-a-particular-font-for-a-small-section-of-text-in-my-document)

[Font Catalog](https://tug.org/FontCatalogue/)

[Which fonts are installed?](https://tex.stackexchange.com/questions/2305/what-fonts-are-installed-on-my-box/2308#2308)

Commands:
* \usefont{encoding}{family}{series}{shape}
* \usepackage{FONT}
* \fontfamily{...}\selectfont
