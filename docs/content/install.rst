Installation
============

Installing the Code
-------------------

.. code-block:: bash

    # Install Python Virtual Environment
    #    - The Python executable can be "python" or "python3"
    #    - Alternatively, Conda can be used for the environment
    python -m pip install virtualenv

    # Create a Python Virtual Environment
    #    - The Python executable can be "python" or "python3"
    #    - Alternatively, Conda can be used for the environment
    python -m venv venv

    # Activate the Python Virtual Environment
    source venv/bin/activate

    # Install PyPEEC from Pypi
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
