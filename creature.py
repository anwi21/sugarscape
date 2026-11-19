class Creature:
    def __init__(self, creatureID, cell, configuration):
        self.ID = creatureID
        self.cell = cell
        self.debug = cell.environment.sugarscape.debug

    def findCreatureNeighbors(self):
        cell = self.cell

        north = cell.findNorthNeighbor()
        south = cell.findSouthNeighbor()
        east = cell.findEastNeighbor()
        west = cell.findWestNeighbor()

        neighborCells = [north,south,east,west,
                         north.findEastNeighbor() if north is not None else None,
                         north.findWestNeighbor() if north is not None else None,
                         south.findEastNeighbor() if south is not None else None,
                         south.findWestNeighbor() if south is not None else None
                        ]

        creatureNeighbors = []

        for neighborCell in neighborCells:
            if neighborCell is not None and neighborCell is not cell:
                if neighborCell.creature is not None and neighborCell not in creatureNeighbors:
                    creatureNeighbors.append(neighborCell)


        return len(creatureNeighbors)

    def shouldSurvive(self):
        neighborCount = self.findCreatureNeighbors()
        # Creatures only survive if the neighbor count is 2-3
        return neighborCount == 2 or neighborCount == 3