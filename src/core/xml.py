import sys
import os
import io
import xmltodict
from xml.parsers.expat import ExpatError
#from xmltodict import InvalidSignatureException
#import ExpatError
import json
from collections import OrderedDict
from jsonConverter import ToHtml as JsonToHtml

class ToHtml(JsonToHtml):

    def __init__(self) -> None:
        super().__init__()

    def loadFile(self, xmlFile):
        try:
            if not self._isValidPathname(xmlFile) or not os.path.exists(xmlFile):
                raise ValueError('Input file [' + str(xmlFile) + '] does not exists')
            self.__sourceFile = xmlFile
            xmlDatas = None
            with io.open(self.__sourceFile, 'r', encoding='utf-8') as stream:
                try:
                    xmlDatas = xmltodict.parse(stream.read(), process_namespaces=True)
                except (xmltodict.ParsingInterrupted, ExpatError):
                    raise ValueError("invalid xml")
                if not xmlDatas or 'xml' not in xmlDatas:
                    raise ValueError("invalid xml")
                xmlDatas = xmlDatas['xml']
        except ValueError as e:
            sys.exit(e)
        if xmlDatas is not None and len(xmlDatas) > 0:
            self.__FileContent = json.loads(json.dumps(xmlDatas), object_pairs_hook=OrderedDict)
            if self._extractedNode:
                self._extractedNode = self.__FileContent
                return self._extractedNode
        return self.__FileContent

if __name__ == '__main__':
    sys.exit('Direct access not allowed')
