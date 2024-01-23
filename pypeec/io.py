"""
Module for serialization and deserialization.
    - load JSON/YAML input files
    - load and write JSON/Pickle data files

For YAML files, the following custom extensions are used:
    - "!path" - allows the inclusion of relative paths
    - "!include" - allows the inclusion of YAML sub-files

For JSON files, the following custom extensions are used:
    - "__complex__" - allows the serialization of complex numbers
    - "__numpy__" - allows the serialization of NumPy arrays

The JSON/YAML files with the custom extensions are still valid JSON/YAML files.

The JSON files can be serialized/deserialized as/from:
    - text files
    - gzip files

Warning:
    - Pickling data is not secure.
    - Only load pickle files that you trust.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import json
import pickle
import gzip
import yaml
import numpy as np
from pypeec.error import FileError


class _YamlLoader(yaml.Loader):
    """
    This Python class offers extension to the YAML format.
        - include YAML file in YAML file
        - include relative filesystem paths
    """

    def __init__(self, stream):
        """
        Constructor of the Loader class.
        """

        # get the path of the YAML file for relative paths
        self.path_root = os.path.abspath(stream.name)
        self.path_root = os.path.dirname(self.path_root)

        # call the constructor of the parent
        super().__init__(stream)

        # handling of inclusion inside YAML files
        def fct_handle_include(self, node):
            res = _YamlLoader.__yaml_handling(self, node, self.__extract_yaml)
            return res

        # handling of path inside YAML files
        def fct_handle_path(self, node):
            res = _YamlLoader.__yaml_handling(self, node, self.__extract_path)
            return res

        # add the extension to the YAML format
        _YamlLoader.add_constructor("!include", fct_handle_include)
        _YamlLoader.add_constructor("!path", fct_handle_path)

    def __yaml_handling(self, node, fct):
        """
        Apply a function to a YAML for list, dict, scalar.
        """

        if isinstance(node, yaml.ScalarNode):
            return fct(self.construct_scalar(node))
        elif isinstance(node, yaml.SequenceNode):
            result = []
            for filename in self.construct_sequence(node):
                result.append(fct(filename))
            return result
        elif isinstance(node, yaml.MappingNode):
            result = {}
            for k, v in self.construct_mapping(node).iteritems():
                result[k] = fct(v)
            return result
        else:
            raise yaml.YAMLError("invalid node")

    def __extract_path(self, filename):
        """
        Find the path with respect to the YAML file path.
        """

        return os.path.join(self.path_root, filename)

    def __extract_yaml(self, filename):
        """
        Load an included YAML file.
        """

        filepath = self.__extract_path(filename)
        with open(filepath, "r") as f:
            content = yaml.load(f, _YamlLoader)
            return content


class _JsonNumPyEncoder(json.JSONEncoder):
    """
    This Python class offers extension to the JSON format (encoder).
        - encode NumPy scalar types
        - encode NumPy array types
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """

        super().__init__(**kwargs)

    def default(self, obj):
        """
        Function encoding NumPy types as dictionaries.
        """

        # encode complex number
        if np.isscalar(obj) and np.iscomplexobj(obj):
            return {
                "__complex__": None,
                "real": obj.real,
                "imag": obj.imag,
            }

        # encode numpy array
        if isinstance(obj, np.ndarray):
            # handle numpy array
            if np.issubdtype(obj.dtype, np.complex_):
                return {
                    "__numpy__": None,
                    "dtype": "complex",
                    "shape": obj.shape,
                    "data": {
                        "real": obj.real.flatten().tolist(),
                        "imag": obj.imag.flatten().tolist(),
                    },
                }
            elif np.issubdtype(obj.dtype, np.floating):
                return {
                    "__numpy__": None,
                    "dtype": "float",
                    "shape": obj.shape,
                    "data": obj.flatten().tolist(),
                }
            elif np.issubdtype(obj.dtype, np.integer):
                return {
                    "__numpy__": None,
                    "dtype": "int",
                    "shape": obj.shape,
                    "data": obj.flatten().tolist(),
                }
            elif np.issubdtype(obj.dtype, bool):
                return {
                    "__numpy__": None,
                    "dtype": "bool",
                    "shape": obj.shape,
                    "data": obj.flatten().tolist(),
                }
            else:
                FileError("invalid numpy array for serialization")
        else:
            # if not numpy, default to the base encoder
            return json.JSONEncoder.default(self, obj)


class _JsonNumPyDecoder(json.JSONDecoder):
    """
    This Python class offers extension to the JSON format (decoder).
        - decode NumPy scalar types
        - decode NumPy array types
    """

    def __init__(self, **kwargs):
        """
        Constructor
        """

        kwargs.setdefault("object_hook", self.parse)
        super().__init__(**kwargs)

    def parse(self, obj):
        """
        Function decoding NumPy types from dictionaries.
        """

        # if not dict, do nothing
        if not isinstance(obj, dict):
            return obj

        # parse the extensions
        elif "__complex__" in obj:
            # handling complex scalar
            real = obj["real"]
            imag = obj["imag"]
            return complex(real, imag)
        elif "__numpy__" in obj:
            # handle numpy array
            dtype = obj["dtype"]
            shape = obj["shape"]
            data = obj["data"]

            # parse the type
            if dtype == "complex":
                real = np.array(data["real"], dtype=np.complex_).reshape(shape)
                imag = np.array(data["imag"], dtype=np.complex_).reshape(shape)
                return real+1j*imag
            elif dtype == "float":
                return np.array(data, dtype=np.float_).reshape(shape)
            elif dtype == "int":
                return np.array(data, dtype=np.int_).reshape(shape)
            elif dtype == "bool":
                return np.array(data, dtype=bool).reshape(shape)
        else:
            return obj


def _load_yaml(filename):
    """
    Load a YAML file (with extensions).
    """

    try:
        with open(filename, "r") as fid:
            data = yaml.load(fid, _YamlLoader)
    except yaml.YAMLError as ex:
        raise FileError("invalid YAML file: %s\n%s" % (filename, str(ex)))
    except OSError:
        raise FileError("cannot open the file: %s" % filename)

    return data


def _load_json(filename, is_gzip):
    """
    Load a JSON file (with extensions).
    """

    try:
        if is_gzip:
            with gzip.open(filename, "rt", encoding="utf-8") as fid:
                data = json.load(fid, cls=_JsonNumPyDecoder)
        else:
            with open(filename, "r") as fid:
                data = json.load(fid, cls=_JsonNumPyDecoder)
    except (json.JSONDecodeError, TypeError, ValueError) as ex:
        raise FileError("invalid JSON file: %s\n%s" % (filename, str(ex)))
    except OSError:
        raise FileError("cannot open the file: %s" % filename)

    return data


def _write_json(filename, data, is_gzip):
    """
    Write a JSON file (with extensions).
    """

    try:
        if is_gzip:
            with gzip.open(filename, "wt", encoding="utf-8") as fid:
                json.dump(data, fid, cls=_JsonNumPyEncoder)
        else:
            with open(filename, "w") as fid:
                json.dump(data, fid, indent=4, cls=_JsonNumPyEncoder)
    except (json.JSONDecodeError, TypeError, ValueError) as ex:
        raise FileError("invalid JSON file: %s\n%s" % (filename, str(ex)))
    except OSError:
        raise FileError("cannot write the file: %s" % filename)

    return data


def _load_pickle(filename):
    """
    Load a pickle file.
    """

    # load the Pickle file
    try:
        with open(filename, "rb") as fid:
            data = pickle.load(fid)
    except pickle.UnpicklingError:
        raise FileError("invalid Pickle file: %s" % filename)
    except EOFError:
        raise FileError("file not found: %s" % filename)
    except OSError:
        raise FileError("invalid Pickle file: %s" % filename)

    return data


def _write_pickle(filename, data):
    """
    Write a pickle file.
    """

    # save the Pickle file
    try:
        with open(filename, "wb") as fid:
            pickle.dump(data, fid)
    except pickle.PicklingError:
        raise FileError("invalid data for Pickle: %s" % filename)
    except OSError:
        raise FileError("cannot write the file: %s" % filename)


def load_input(filename):
    """
    Load an input file (JSON or YAML).

    Parameters
    ----------
    filename : string)
        Name and path of the file to be loaded.
        The file type is determined by the extension.
        For YAML files, the extension should be "yaml" or "yml".
        For JSON files, the extension should be "json" or "js".

    Returns
    -------
    data : data
        Python data contained in the file content
    """

    (name, ext) = os.path.splitext(filename)
    if ext in [".json", ".js"]:
        data = _load_json(filename, False)
    elif ext in [".gz", ".gzip"]:
        data = _load_json(filename, True)
    elif ext in [".yaml", ".yml"]:
        data = _load_yaml(filename)
    else:
        raise FileError("invalid file extension: %s" % filename)

    return data


def load_data(filename):
    """
    Load a data file (JSON or Pickle).

    Parameters
    ----------
    filename : string)
        Name and path of the file to be loaded.
        The file type is determined by the extension.
        For JSON files, the extension should be "json" or "js".
        For Pickle files, the extension should be "pck".

    Returns
    -------
    data : data
        Python data contained in the file content
    """

    (name, ext) = os.path.splitext(filename)
    if ext in [".json", ".js"]:
        data = _load_json(filename, False)
    elif ext in [".gz", ".gzip"]:
        data = _load_json(filename, True)
    elif ext in [".pck", ".pkl"]:
        data = _load_pickle(filename)
    else:
        raise FileError("invalid file extension: %s" % filename)

    return data


def write_data(filename, data):
    """
    Write a data file (JSON or Pickle).

    Parameters
    ----------
    filename : string)
        Name and path of the file to be created.
        The file type is determined by the extension.
        For JSON files, the extension should be "json" or "js".
        For Pickle files, the extension should be "pck".
    data : data
        Python data to be saved.
    """

    (name, ext) = os.path.splitext(filename)
    if ext in [".json", ".js"]:
        _write_json(filename, data, False)
    elif ext in [".gz", ".gzip"]:
        _write_json(filename, data, True)
    elif ext in [".pck", ".pkl"]:
        _write_pickle(filename, data)
    else:
        raise FileError("invalid file extension: %s" % filename)
