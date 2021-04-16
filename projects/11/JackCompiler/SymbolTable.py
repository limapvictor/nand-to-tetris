from Constants import *

class SymbolTable:
    SEGMENT_BY_VAR_KIND = {
        VAR_STATIC: SEGMENT_STATIC, 
        VAR_FIELD: SEGMENT_THIS, 
        VAR_ARG: SEGMENT_ARG, 
        VAR_LOCAL: SEGMENT_LOCAL
    }
    
    def startSubroutine(self):
        self._table = []
        self._varCountByKind = {VAR_STATIC: 0, VAR_FIELD: 0, VAR_ARG: 0, VAR_LOCAL: 0}

    def getByName(self, name):
        entry = [var for var in self._table if var['name'] == name]
        return entry[0] if len(entry) > 0 else None

    def insert(self, name, varType, kind):
        newEntry = {
            'name': name,
            'type': varType,
            'kind': kind,
            'segment': self.SEGMENT_BY_VAR_KIND[kind],
            'index': self._varCountByKind[kind]
        } 
        self._table.append(newEntry)
        self._varCountByKind[kind] = self._varCountByKind[kind] + 1

    def getVarCountByKind(self, kind):
        return self._varCountByKind[kind]
