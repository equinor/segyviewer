set(PYTHON_SOURCES
    __init__.py
    layoutcombo.py
    layoutcanvas.py
    layoutfigure.py
    colormapcombo.py
    )

add_python_package(segyview segyview "${PYTHON_SOURCES}")
