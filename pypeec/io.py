"""
Simple module for serialization and deserialization.

WARNING: Pickling data is not secure.
         Only load pickle files that you trust.
"""

__author__ = "Thomas Guillod"
__copyright__ = "Thomas Guillod - Dartmouth College"
__license__ = "Mozilla Public License Version 2.0"

import os.path
import json
import pickle
import yaml
from pypeec.error import FileError


class YamlLoader(yaml.Loader):
    """
    This Python class offers extension to the YAML format:
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
            res = YamlLoader.__yaml_handling(self, node, self.__extract_yaml)
            return res

        # handling of path inside YAML files
        def fct_handle_path(self, node):
            res = YamlLoader.__yaml_handling(self, node, self.__extract_path)
            return res

        # add the extension to the YAML format
        YamlLoader.add_constructor("!include", fct_handle_include)
        YamlLoader.add_constructor("!path", fct_handle_path)

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
            content = yaml.load(f, YamlLoader)
            return content


def _load_yaml(filename):
    """
    Load a YAML file.
    """

    try:
        with open(filename, "r") as fid:
            data = yaml.load(fid, YamlLoader)
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


def write_config(filename, data):
    """
    Write a config file (JSON).
    """

    # check extension
    (name, ext) = os.path.splitext(filename)
    if ext != ".json":
        raise FileError("invalid file extension: %s" % filename)

    # save the Pickle file
    try:
        with open(filename, "w") as fid:
            json.dump(data, fid, indent=4)
    except (TypeError, ValueError, RecursionError) as ex:
        raise FileError("invalid data for JSON: %s" % filename) from ex
    except OSError as ex:
        raise FileError("cannot write the file: %s" % filename) from ex


def load_pickle(filename):
    """
    Load a pickle file.
    """

    # check extension
    (name, ext) = os.path.splitext(filename)
    if ext != ".pck":
        raise FileError("invalid file extension: %s" % filename)

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
    """

    # check extension
    (name, ext) = os.path.splitext(filename)
    if ext != ".pck":
        raise FileError("invalid file extension: %s" % filename)

    # save the Pickle file
    try:
        with open(filename, "wb") as fid:
            pickle.dump(data, fid)
    except pickle.PicklingError as ex:
        raise FileError("invalid data for Pickle: %s" % filename) from ex
    except OSError as ex:
        raise FileError("cannot write the file: %s" % filename) from ex
