=======
SEGYVIEWER
=======

Segyviewer is a small LGPL licensed python library for easy viewing of SEG-Y
files. It uses the segyio library for reading files.

## Getting started ##

Segyviewer is available through pip and installed with

```bash
pip install segyviewer
```

to open segyviewer with your chosen <file.segy>
```bash
segyviewer <file.segy>
```

## Build Segyviewer

To build segyviewer you need:

 * [Python](https://www.python.org/) 2.7 or 3.x.
 * [numpy](http://www.numpy.org/) version 1.10 or greater
 * [setuptools](https://pypi.python.org/pypi/setuptools) version 28 or greater
 * [setuptools-scm](https://pypi.python.org/pypi/setuptools_scm)
 * [PyQt4](https://www.riverbankcomputing.com/software/pyqt/download)
 * [segyio](https://github.com/Statoil/segyio)
 * [matplotlib](https://matplotlib.org/)

To build and install segyviewer, perform the following actions in your console:

```bash
git clone https://github.com/Statoil/segyviewer
cd segyviewer
python setup.py build
python setup.py install
```

Please note that the required library pyqt4 is not listed in requirements.txt. QT not longer
supports PyQt4 and as such it is not possible to pip install PyQt4.
Setup.py, which uses pip, would fail if PyQt4 was listed in requirements.txt.
