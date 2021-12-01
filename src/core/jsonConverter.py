import sys
import os
import io
import json
from collections import OrderedDict
if sys.version_info[:2] < (3, 0):
    from cgi import escape as html_escape
    text = unicode
    text_types = (unicode, str)
else:
    from html import escape as html_escape
    text = str
    text_types = (str,)

currentdir = os.path.dirname(os.path.realpath(__file__))
parentDirectory = os.path.dirname(currentdir)
sys.path.append(os.path.abspath(parentDirectory))

from utils.upresets import html
from utils.ujson import nodeExtractor

class ToHtml(object):
    ERROR_INVALID_NAME = 123
    def __init__(self)-> None:
        self.__sourceFile = None
        self.__FileContent = {}
        self._extractedNode = {}
        self.__destFile = None
        self.__destDirectory = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'outputs')

    def __getColumnHeaders(self, jsonDatas):
        if not jsonDatas or not hasattr(jsonDatas, '__getitem__') \
        or not hasattr(jsonDatas[0], 'keys'):
            return None
        columnHeaders = jsonDatas[0].keys()
        for entry in jsonDatas:
            if not hasattr(entry, 'keys') \
            or not hasattr(entry, '__iter__') \
            or len(entry.keys()) != len(columnHeaders):
                return None
            for header in columnHeaders:
                if header not in entry:
                    return None
        return columnHeaders

    def __processNode(self, jsonDatas):
        if type(jsonDatas) in text_types:
            if self.escape:
                return html_escape(text(jsonDatas))
            else:
                return text(jsonDatas)
        if hasattr(jsonDatas, 'items'):
            return self.__processObject(jsonDatas)
        if hasattr(jsonDatas, '__iter__') and hasattr(jsonDatas, '__getitem__'):
            return self.__processList(jsonDatas)
        return text(jsonDatas)

    def __processList(self, jsonList):
        if not jsonList:
            return ''
        output = ''
        columnHeaders = self.__getColumnHeaders(jsonList)
        if columnHeaders is not None:
            output += self.tableInitialize
            output += '<thead>'
            output += '<tr><th>' + '</th><th>'.join(columnHeaders) + '</th></tr>'
            output += '</thead>'
            output += '<tbody>'
            for entry in jsonList:
                output += '<tr><td>'
                output += '</td><td>'.join([self.__processNode(entry[columnHeader]) for columnHeader in columnHeaders])
                output += '</td></tr>'
            output += '</tbody>'
            output += '</table>'
            return output
        output = '<ul><li>'
        output += '</li><li>'.join([self.__processNode(child) for child in jsonList])
        output += '</li></ul>'
        return output

    def __processObject(self, jsonDatas):
        if not jsonDatas:
            return '' #avoid empty tables
        output = self.tableInitialize + '<tr>'
        output += '</tr><tr>'.join([
            "<th>%s</th><td>%s</td>" %(
                self.__processNode(k),
                self.__processNode(v)
            )
            for k, v in jsonDatas.items()
        ])
        output += '</tr></table>'
        return output

    def __makeDestinationFolder(self, sPath, mode=0o775):
        if self._isValidPathname(sPath):
            if not sPath or os.path.exists(sPath):
                return []
            (head, tail) = os.path.split(sPath)  # head/tail
            res = self.__makeDestinationFolder(head, mode)
            os.mkdir(sPath)
            os.chmod(sPath, mode)
            res += [sPath]
            return res

    def _isValidPathname(self, pathname: str)->bool:
        try:
            if not isinstance(pathname, str) or not pathname:
                return False
            _, pathname = os.path.splitdrive(pathname)
            root_dirname = os.environ.get('HOMEDRIVE', 'C:') \
                if sys.platform == 'win32' else os.path.sep
            assert os.path.isdir(root_dirname)
            root_dirname = root_dirname.rstrip(os.path.sep) + os.path.sep
            for pathname_part in pathname.split(os.path.sep):
                try:
                    os.lstat(root_dirname + pathname_part)
                except OSError as exc:
                    if hasattr(exc, 'winerror'):
                        if exc.winerror == self.ERROR_INVALID_NAME:
                            return False
                    elif exc.errno in {errno.ENAMETOOLONG, errno.ERANGE}:
                        return False
        except TypeError as exc:
            return False
        else:
            return True

    def execute(self, table_attributes='class="table table-bordered sortable"', encode=False, escape=True):
        if not os.path.exists(self.__destDirectory) or not os.path.isdir(self.__destDirectory):
            self.__makeDestinationFolder(self.__destDirectory)
        self.table_attributes = table_attributes if table_attributes else 'class="table-responsive-md table-bordered sortable table-striped table-hover"'
        self.tableInitialize = "<table %s>" % self.table_attributes
        self.escape = escape
        self._extractedNode = self._extractedNode if len(self._extractedNode) > 0 else self.__FileContent
        converted = html.pageHeader() + self.__processNode(self._extractedNode) + html.pageFooter()
        if encode:
            converted = converted.encode('ascii', 'xmlcharrefreplace')
        self.__destFile = os.path.join(self.__destDirectory, os.path.splitext(os.path.basename(self.__sourceFile))[0] + html.pageExtension())
        with io.open(self.__destFile, 'w', encoding='utf8') as fp:
            fp.write(converted)
            fp.close()
        print("File " + self.__destFile + " has been generated")
        return converted

    def extractNode(self, nodePath)->dict:
        extractor = nodeExtractor(self.__FileContent)
        self._extractedNode = extractor.extract(nodePath)
        return self._extractedNode

    def loadFile(self, jsonFile):
        try:
            if not self._isValidPathname(jsonFile) or not os.path.exists(jsonFile):
                raise ValueError('Input file [' + str(jsonFile) + '] does not exists')
            self.__sourceFile = jsonFile
            jsonDatas = None
            with io.open(self.__sourceFile, 'r', encoding='utf-8') as stream:
                try:
                    jsonDatas = json.loads(stream, object_pairs_hook=OrderedDict)
                except json.JSONDecodeError as exc:
                    print(exc)
        except ValueError as e:
            sys.exit(e)
        if jsonDatas is not None and len(jsonDatas) > 0:
            self.__FileContent = jsonDatas
            if self._extractedNode:
                self._extractedNode = self.__FileContent
                return self._extractedNode
        return self.__FileContent

    def load(self, jsonInput):
        try:
            jsonDatas = None
            if not jsonInput:
                jsonDatas = {}
            elif type(jsonInput) in text_types:
                try:
                    jsonDatas = json.loads(jsonInput, object_pairs_hook=OrderedDict)
                except json.JSONDecodeError as exc:
                    print(exc)
        except ValueError as e:
            sys.exit(e)
        if jsonDatas is not None and len(jsonDatas) > 0:
            self.__FileContent = jsonDatas
            if self._extractedNode:
                self._extractedNode = self.__FileContent
                return self._extractedNode
        return self.__FileContent

    def setDestinationFolder(self, FilePath):
        try:
            if self._isValidPathname(FilePath):
                self.__destDirectory = os.path.dirname(os.path.abspath(FilePath)) if os.path.isfile(os.path.abspath(FilePath)) else os.path.abspath(FilePath)
        except IOError  as e:
            sys.exit('I/O error(%s): %s' % (e.errno, e.strerror))


if __name__ == '__main__':
    sys.exit('Direct access not allowed')
