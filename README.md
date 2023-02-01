#  PTAH

PTAH stands for PhoTo Album Handler and aims to generate photo album in PDF ready for printing. Ptah is the egyptian god of craftsmen and architects and it is perfect name to generate your photo album as a work of art. In addition, it is a perfect for ashort and unused sheel command.


## How to use it?

The first step is to generate the documentation :

	$ ptah --doc

The generate PDF file, `ptah.pdf`, sum up the syntax of **Ptah** and
the list of options that may be used in the album file.

The album file is expressed in [YAML](https://yaml.org/spec/history/2001-12-10.html).

It may be declared in a file named  `album.ptah` and in this case, the
album can be built by moving to the album directory and typing:

	$ ptah

And the result can be found in `album.pdf`.

The album can be declared in any file `XXX.ptah` and can be built with:

	$ ptah XXX.ptah

The result is in `XXX.pdf`.

One important component of **Ptah** are path to photo files. If they
are expressed as relative path, these are relative to the directory
containing the album file.


## How to install?


## Test photos

Many thanks to:
* [PH](https://pxhere.com/)
* [Unsplash](https://unsplash.com)

## License

Freely available under [GPL v3][file:LICENCE].

