https://github.com/geeksville/GraXpert/actions/runs/18449315430


Traceback (most recent call last):
  File "/workspaces/graxpert/graxpert/application/app.py", line 342, in on_load_image
    image.set_from_file(filename, StretchParameters(self.prefs.stretch_option, self.prefs.channels_linked_option), self.prefs.saturation)
  File "/workspaces/graxpert/graxpert/astroimage.py", line 32, in set_from_file
    self.img_format = os.path.splitext(directory)[1].lower()
                      ^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "/usr/lib/python3.12/posixpath.py", line 118, in splitext
    p = os.fspath(p)
        ^^^^^^^^^^^^
TypeError: expected str, bytes or os.PathLike object, not tuple