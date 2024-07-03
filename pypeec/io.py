"""
Module for serialization and deserialization.
    - load JSON/YAML input files
    - load and write JSON/Pickle data files

For YAML files, the following custom extensions are used:
    - "!path" - parse relative paths (with respect to the YAML file)
    - "!include" - include other YAML files (recursion possible)
    - "!env" - include YAML string from environment variables
    - "!merge_dict" - merge a list of dicts
    - "!merge_list" - merge a list of lists

For JSON files, the following custom extensions are used:
    - "__complex__" - allows the serialization of complex numbers
    - "__numpy__" - allows the serialization of NumPy arrays

The JSON/YAML files with the custom extensions are still valid JSON/YAML files.

The JSON files can be serialized/deserialized as/from:
    - text files
    - gzip files

Warning
-------
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


class _YamlLoader(yaml.Loader):
    """
    This Python class offers extension to the YAML format.
        - include YAML file in YAML file
        - include relative filesystem paths
        - merge list of dicts
        - merge list of lists
    """

    def __init__(self, stream):
        """
        Constructor.
        Custom YAML loader subclassing the default loader.
        """

        # get the path of the YAML file for relative paths
        self.path_root = os.path.abspath(stream.name)
        self.path_root = os.path.dirname(self.path_root)

        # flag indicating if any merge commands are used
        self.has_merge = False

        # call the constructor of the parent
        super().__init__(stream)

        # handling of YAML files inclusion
        def fct_handle_include(self, node):
            res = _YamlLoader._yaml_handling(self, node, self._extract_yaml)
            return res

        # handling of relative paths
        def fct_handle_path(self, node):
            res = _YamlLoader._yaml_handling(self, node, self._extract_path)
            return res

        # handling of environment variables inclusion
        def fct_handle_env(self, node):
            res = _YamlLoader._yaml_handling(self, node, self._extract_env)
            return res

        # handling merge of a list of dicts
        def fct_handle_merge_dict(self, node):
            self.has_merge = True
            res = _MergeObj(self.construct_sequence(node), "dict")
            return res

        # handling merge of a list of lists
        def fct_handle_merge_list(self, node):
            self.has_merge = True
            res = _MergeObj(self.construct_sequence(node), "list")
            return res

        # add the extension to the YAML format
        _YamlLoader.add_constructor("!include", fct_handle_include)
        _YamlLoader.add_constructor("!path", fct_handle_path)
        _YamlLoader.add_constructor("!env", fct_handle_env)
        _YamlLoader.add_constructor("!merge_dict", fct_handle_merge_dict)
        _YamlLoader.add_constructor("!merge_list", fct_handle_merge_list)

    def _yaml_handling(self, node, fct):
        """
        Apply a function to a YAML node for list, dict, scalar.
        """

        if isinstance(node, yaml.ScalarNode):
            return fct(self.construct_scalar(node))
        elif isinstance(node, yaml.SequenceNode):
            result = []
            for arg in self.construct_sequence(node):
                result.append(fct(arg))
            return result
        elif isinstance(node, yaml.MappingNode):
            result = {}
            for tag, arg in self.construct_mapping(node).items():
                result[tag] = fct(arg)
            return result
        else:
            raise yaml.YAMLError("invalid YAML node type")

    def _extract_path(self, filename):
        """
        Find the path with respect to the YAML file path.
        """

        # check type
        if type(filename) is not str:
            raise yaml.YAMLError("path command arguments should be strings")

        # construct relative path
        filepath = os.path.join(self.path_root, filename)

        return filepath

    def _extract_yaml(self, filename):
        """
        Load an included YAML file.
        """

        # check type
        if type(filename) is not str:
            raise yaml.YAMLError("include command arguments should be strings")

        # construct relative path
        filepath = os.path.join(self.path_root, filename)

        # load YAML file
        with open(filepath, "r") as fid:
            data = _parse_yaml(fid)

        return data

    def _extract_env(self, name):
        """
        Load a YAML file from an environment variable.
        """

        # check type
        if type(name) is not str:
            raise yaml.YAMLError("env command arguments should be strings")

        # get and check the variable
        value = os.getenv(name)
        if value is None:
            raise yaml.YAMLError("env variable is not existing: %s" % name)

        # load YAML string
        data = yaml.safe_load(value)

        return data


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

        # encode complex number and numpy array
        if np.isscalar(obj) and np.iscomplexobj(obj):
            return {
                "__complex__": None,
                "real": obj.real,
                "imag": obj.imag,
            }
        elif isinstance(obj, np.ndarray):
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
                TypeError("invalid numpy array for serialization")
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
        if "__complex__" in obj:
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


class _MergeObj:
    """
    This Python class is used to merge YAML data.
        - a custom merge command is used with a list of arguments
        - the arguments (lists or dicts) are merged together
        - the merge is performed recursively

    The merge objects are created during the YAML parsing.
    The merge objects are replaced by the merged data after the parsing.
    """

    def __init__(self, data_list, data_type):
        """
        Constructor.
        Assign the list of data to be merged and the data type.
        """

        if type(data_list) is not list:
            raise yaml.YAMLError("arguments of the merge_dict / merge_list should be a list")

        self.data_list = data_list
        self.data_type = data_type

    def extract(self):
        """
        Merge a list of dicts or a list of lists.
        The merge is performed recursively.
        """

        if self.data_type == "dict":
            res = {}
            for data in self.data_list:
                data = _merge_data(data)
                if type(data) is not dict:
                    raise yaml.YAMLError("merge_dict cannot only merge dictionaries")
                res.update(data)
        elif self.data_type == "list":
            res = []
            for data in self.data_list:
                data = _merge_data(data)
                if type(data) is not list:
                    raise yaml.YAMLError("merge_list cannot only merge lists")
                res += data
        else:
            raise yaml.YAMLError("invalid merge type")

        return res


def _merge_data(data):
    """
    Walk through the data recursively and merge it.
    Find the merge objects and replace them with merged data.
    This function is used for the YAML merge extensions.
    """

    if type(data) is dict:
        for tag, val in data.items():
            data[tag] = _merge_data(val)
    elif type(data) is list:
        for idx, val in enumerate(data):
            data[idx] = _merge_data(val)
    elif type(data) is _MergeObj:
        data = data.extract()
    else:
        pass

    return data


def _parse_yaml(stream):
    """
    Load a YAML stream (with custom extensions).
    If required, merge the data (custom merge commands).
    """

    # create loader
    loader = _YamlLoader(stream)

    # parse, merge, and clean
    try:
        data = loader.get_single_data()
        if loader.has_merge:
            data = _merge_data(data)
    finally:
        loader.dispose()

    return data


def _load_yaml(filename):
    """
    Load a YAML file (with custom extensions).
    """

    try:
        with open(filename, "r") as fid:
            data = _parse_yaml(fid)
    except yaml.YAMLError as ex:
        raise RuntimeError("invalid YAML file: %s\n%s" % (filename, str(ex))) from None
    except OSError:
        raise OSError("cannot open the file: %s" % filename) from None

    return data


def _load_json(filename, is_gzip):
    """
    Load a JSON file (with extensions).
    The JSON file can be a text file or a gzip file.
    """

    try:
        if is_gzip:
            with gzip.open(filename, "rt", encoding="utf-8") as fid:
                data = json.load(fid, cls=_JsonNumPyDecoder)
        else:
            with open(filename, "r") as fid:
                data = json.load(fid, cls=_JsonNumPyDecoder)
    except (json.JSONDecodeError, TypeError, ValueError) as ex:
        raise RuntimeError("invalid JSON file: %s\n%s" % (filename, str(ex))) from None
    except OSError:
        raise OSError("cannot open the file: %s" % filename) from None

    return data


def _write_json(filename, data, is_gzip):
    """
    Write a JSON file (with extensions).
    The JSON file can be a text file or a gzip file.
    """

    try:
        if is_gzip:
            with gzip.open(filename, "wt", encoding="utf-8") as fid:
                json.dump(data, fid, cls=_JsonNumPyEncoder)
        else:
            with open(filename, "w") as fid:
                json.dump(data, fid, indent=4, cls=_JsonNumPyEncoder)
    except (json.JSONDecodeError, TypeError, ValueError) as ex:
        raise RuntimeError("invalid JSON file: %s\n%s" % (filename, str(ex))) from None
    except OSError:
        raise OSError("cannot write the file: %s" % filename) from None

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
        raise RuntimeError("invalid Pickle file: %s" % filename) from None
    except EOFError:
        raise EOFError("file not found: %s" % filename) from None
    except OSError:
        raise OSError("invalid Pickle file: %s" % filename) from None

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
        raise RuntimeError("invalid data for Pickle: %s" % filename) from None
    except OSError:
        raise OSError("cannot write the file: %s" % filename) from None


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
        For GZIP/JSON files, the extension should be "gzip" or "gz".

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
        raise ValueError("invalid file extension: %s" % filename)

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
        For GZIP/JSON files, the extension should be "gzip" or "gz".
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
        raise ValueError("invalid file extension: %s" % filename)

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
        For GZIP/JSON files, the extension should be "gzip" or "gz".
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
        raise ValueError("invalid file extension: %s" % filename)
