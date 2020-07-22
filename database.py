class Database:
    def __init__(self, filename):
        self.filename = filename

    def _read(self):
        with open(self.filename,'r') as source:
            database = source.readlines()
        return database

    def _write(self, context):
        with open(self.filename,'w') as source:
            source.write(context)

    def getPlayers(self):
        players = {}
        for line in self._read():
            values = line.split(";")
            if len(values) == 0:
                continue
            playerID = values[0]
            if len(values) == 1:
                continue
            attributes = dict([pair.split(":") for pair in values[1:]])
            players[playerID] = attributes
        return players

    def savePlayers(self, players):
        lines = []
        for playerID, attributes in players.items():
            line = playerID
            for key, value in attributes.items():
                line += f";{key}:{value}"
            lines.append(line)
        self._write('\n'.join(lines))

