"""
Module for serialization and deserialization.
    - load JSON/YAML configuration files
    - load and write Pickle files

For YAML files, the following custom extensions are used:
    - "!path" - allow the inclusion of relative paths
    - "!include" - allow the inclusion of YAML sub-files

Warning:
    - Pickling data is not secure.
    - Only load pickle files that you trust.
    - Do not commit the Pickle files in the Git repository.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import json
import pickle
import yaml
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


def _load_yaml(filename):
    """
    Load a YAML file.
    """

    try:
        with open(filename, "r") as fid:
            data = yaml.load(fid, _YamlLoader)
    except yaml.YAMLError as ex:
        raise FileError("invalid YAML file: %s\n%s" % (filename, str(ex))) from ex
    except OSError as ex:
        raise FileError("cannot open the file: %s" % filename) from ex

    return data


def _load_json(filename):
    """
    Load a JSON file.
    """

    try:
        with open(filename, "r") as fid:
            data = json.load(fid)
    except json.JSONDecodeError as ex:
        raise FileError("invalid JSON file: %s\n%s" % (filename, str(ex))) from ex
    except OSError as ex:
        raise FileError("cannot open the file: %s" % filename) from ex

    return data


def load_config(filename):
    """
    Load a config file (JSON or YAML).

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

    # check extension
    (name, ext) = os.path.splitext(filename)
    if ext in [".json", ".js"]:
        data = _load_json(filename)
    elif ext in [".yaml", ".yml"]:
        data = _load_yaml(filename)
    else:
        raise FileError("invalid file extension: %s" % filename)

    return data


def load_pickle(filename):
    """
    Load a pickle file.

    Parameters
    ----------
    filename  : string
        Name and path of the file to be loaded.

    Returns
    -------
    data : data
        Python data contained in the file content
    """

    # load the Pickle file
    try:
        with open(filename, "rb") as fid:
            data = pickle.load(fid)
    except pickle.UnpicklingError as ex:
        raise FileError("invalid Pickle file: %s" % filename) from ex
    except EOFError as ex:
        raise FileError("file not found: %s" % filename) from ex
    except OSError as ex:
        raise FileError("invalid Pickle file: %s" % filename) from ex

    return data


def write_pickle(filename, data):
    """
    Write a pickle file.

    Parameters
    ----------
    filename : string
        Name and path of the file to be created.
    data : data
        Python data to be saved.
    """

    # save the Pickle file
    try:
        with open(filename, "wb") as fid:
            pickle.dump(data, fid)
    except pickle.PicklingError as ex:
        raise FileError("invalid data for Pickle: %s" % filename) from ex
    except OSError as ex:
        raise FileError("cannot write the file: %s" % filename) from ex
