Installation
============

Installing the Code
-------------------

.. code-block:: bash

    # Installation of PyPEEC with pip
    #    - The Python executable can be "python" or "python3"
    #    - Alternatively, Conda can be used for the environment

    # Install Python Virtual Environment
    python -m pip install virtualenv

    # Create a Python Virtual Environment
    python -m venv venv

    # Activate the Python Virtual Environment
    source venv/bin/activate

    # Install PyPEEC from PyPi
    python -m pip install pypeec

Examples and Documentation
--------------------------

.. code-block:: bash

    # Check the PyPEEC version
    pypeec --version

    # Extract the PyPEEC examples
    pypeec examples examples

    # Extract the PyPEEC documentation
    pypeec documentation documentation
