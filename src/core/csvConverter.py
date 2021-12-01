import sys
import os
import io
import csv
import json
from collections import OrderedDict
from jsonConverter import ToHtml as JsonToHtml

class ToHtml(JsonToHtml):

    def __init__(self) -> None:
        super().__init__()
        self.__quoting=csv.QUOTE_NONE
        self.__dialect='readingdialect'
        self.__delimiter=','

    def loadFile(self, csvFile):
        try:
            if not self._isValidPathname(csvFile) or not os.path.exists(csvFile):
                raise ValueError('Input file [' + str(csvFile) + '] does not exists')
            self.__sourceFile = csvFile
            csvDatas = None
            csv.register_dialect(self.__dialect, delimiter=self.__delimiter, quoting=self.__quoting)
            with io.open(self.__sourceFile, 'r', encoding='utf-8') as stream:
                try:
                    csvDatas = csv.DictReader(stream, dialect=self.__dialect)
                except csv.Error as a:
                    sys.exit(a)
        except ValueError as e:
            sys.exit(e)
        if csvDatas is not None and len(csvDatas) > 0:
            self.__FileContent = json.loads(json.dumps(csvDatas), object_pairs_hook=OrderedDict)
            if self._extractedNode:
                self._extractedNode = self.__FileContent
                return self._extractedNode
        return self.__FileContent

if __name__ == '__main__':
    sys.exit('Direct access not allowed')
