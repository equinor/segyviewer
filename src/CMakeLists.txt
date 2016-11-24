python_module(numpy REQUIRED 1.6)
if (NOT DEFINED PY_numpy)
    message(FATAL_ERROR "numpy module not found!")
endif()

python_module(segyio REQUIRED 1.0.3)
if (NOT DEFINED PY_segyio)
    message(FATAL_ERROR "segyio module not found!")
endif()

python_module(matplotlib REQUIRED 1.5)
if (NOT DEFINED PY_matplotlib)
    message(FATAL_ERROR "matplotlib module not found!")
endif()

python_module(PyQt4 REQUIRED 4.11)
if (NOT DEFINED PY_PyQt4)
    message(FATAL_ERROR "PyQt4 module not found!")
endif()

add_subdirectory(segyviewlib)
