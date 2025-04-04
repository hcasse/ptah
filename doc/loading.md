# Loading of objects

Objects composing the album (Page, Frame, etc) are loaded from a YAML file and
are composed of properties.

They follow the cyclce below:

1. They are created and they provides a list of supported properties.
2. Their properties are then loaded and stored in an `AttrList`.
3. Their `check` method is called to complete and check the consistency of properties (and the actual value of some properties are obtained at this time).

Then they will be used to generate by the back-end to generate the code (currently **Latex**):

1. The requires styles are built (`Style`, `TextStyle`, etc) by resolving properties along the container tree.
2. They are drawn.
