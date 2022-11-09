from typing import Dict, Any

from Constant import *


class SymbolTable:
    def __init__(self) -> None:
        self.class_table = {}
        self.sub_table = {}

        self.index = {IDT_STATIC: 0, IDT_FIELD: 0, IDT_VAR: 0, IDT_ARG: 0}

    def getTableByKind(self, kind):
        if kind == IDT_STATIC or kind == IDT_FIELD:
            return self.class_table

        return self.sub_table

    def startSubroutine(self) -> None:
        self.sub_table = {}
        self.index[IDT_VAR] = 0
        self.index[IDT_ARG] = 0

    def define(self, name, type, kind) -> None:
        table = self.getTableByKind(kind)
        table[name] = {'type': type, 'index': self.index[kind], 'kind': kind}
        self.index[kind] += 1

    def varCount(self, kind) -> int:
        table = self.getTableByKind(kind)
        return len([1 for k, v in table.items() if v['kind'] == kind])

    def kindOf(self, name) -> str:
        return self._getTableByName(name, 'kind')

    def typeOf(self, name) -> str:
        return self._getTableByName(name, 'type')

    def indexOf(self, name) -> int:
        return self._getTableByName(name, 'index')

    def _getTableByName(self, name, key):
        """以name查屬性, 子域優先"""
        if name in self.sub_table:
            return self.sub_table[key]
        elif name in self.class_table:
            return self.class_table[key]
        return None
