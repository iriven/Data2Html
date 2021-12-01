import sys
import os
import io
import yaml
import json
from collections import OrderedDict
from jsonConverter import ToHtml as JsonToHtml
if sys.version_info[:2] < (3, 0):
    from cgi import escape as html_escape
    text = unicode
    text_types = (unicode, str)
else:
    from html import escape as html_escape
    text = str
    text_types = (str,)
class ToHtml(JsonToHtml):

    def __init__(self) -> None:
        super().__init__()

    def loadFile(self, yamlFile):
        try:
            if not self._isValidPathname(yamlFile) or not os.path.exists(yamlFile):
                raise ValueError('Input file [' + str(yamlFile) + '] does not exists')
            self.__sourceFile = yamlFile
            yamlDatas = None
            with io.open(self.__sourceFile, 'r', encoding='utf-8') as stream:
                try:
                    yamlDatas = yaml.safe_load(stream)
                except yaml.YAMLError as exc:
                    print(exc)
        except ValueError as e:
            sys.exit(e)
        if yamlDatas is not None and len(yamlDatas) > 0:
            self.__FileContent = json.loads(json.dumps(yamlDatas), object_pairs_hook=OrderedDict)
            if self._extractedNode:
                self._extractedNode = self.__FileContent
                return self._extractedNode
        return self.__FileContent

    def load(self, yamlInput):
        try:
            yamlDatas = None
            if not yamlInput:
                yamlDatas = {}
            elif type(yamlInput) in text_types:
                try:
                    yamlDatas = yaml.safe_load(yamlInput)
                except yaml.YAMLError as exc:
                    print(exc)
        except ValueError as e:
            sys.exit(e)
        if yamlDatas is not None and len(yamlDatas) > 0:
            self.__FileContent = json.loads(json.dumps(yamlDatas), object_pairs_hook=OrderedDict)
            if self._extractedNode:
                self._extractedNode = self.__FileContent
                return self._extractedNode
        return self.__FileContent

def _Representer(data):
        """see: yaml.representer.represent_mapping"""
        return yaml.representer.represent_mapping('tag:yaml.org,2002:map', data.items())
class ToYAML(object):
    """
    Keep yaml human readable/editable.  Disable yaml references.
    """
    def __init__(self, **kwargs) -> None:
        if kwargs is None:
            kwargs = {}
        kwargs.setdefault('Dumper', yaml.SafeDumper)
        kwargs.setdefault('flowstyle', False)
        kwargs.setdefault('allow_unicode', True)
        kwargs.setdefault('sort_keys', False)
        kwargs.setdefault('indent', 4)
        kwargs.setdefault('eol', os.linesep)
        yaml.representer.SafeRepresenter.add_representer(OrderedDict, _Representer)
        self.sortKeys =  kwargs.get('sort_keys')
        self.acceptUnicode =  kwargs.get('allow_unicode')
        self.Dumper = kwargs.get('Dumper')
        self.Dumper.ignore_aliases = lambda self, data: True
        self.flowstyle =  kwargs.get('flowstyle')
        self.overwrite = kwargs.get('overwrite', False)
        self.encoding = kwargs.get('encoding', 'utf-8')
        self.indent = kwargs.get('indent')
        self.eol = kwargs.get('eol')
        if kwargs.get('filePath', None):
            self.setDestinationPath(self, kwargs.get('filePath'))
        self.data = {}

    def setDestinationPath(self, yamlFile: str)-> bool:
        try:
            filePath = yamlFile if yamlFile.endswith('.yml') else yamlFile + '.yml'
            if not self._isValidPathname(filePath):
                raise ValueError('Invalid file path: [' + str(yamlFile) + ']')
            if os.path.exists(filePath) and not self.overwrite:
                raise Exception("Yaml file '%s' exists as '%s" % (yamlFile, filePath))
            self.filePath = filePath
            return True
        except Exception as e:
            raise e

    def save(self, data, filePath: str = None):
        try:
            if filePath:
                self.setDestinationPath(filePath)
            if not isinstance(data, dict):
                if type(data).__name__ not in ('list', 'tuple'):
                    data = dict([data])
            with open(self.filePath, 'w', encoding=self.encoding) as streaming:
                yaml.dump(data,
                        stream=streaming,
                        default_flow_style=self.flowstyle,
                        allow_unicode=self.acceptUnicode,
                        indent=self.indent,
                        encoding=self.encoding,
                        sort_keys=False,
                        line_break=self.eol,
                        Dumper=self.Dumper)
                streaming.close()
        except IOError  as e:
            sys.exit('I/O error(%s): %s' % (e.errno, e.strerror))


if __name__ == '__main__':
    sys.exit('Direct access not allowed')
