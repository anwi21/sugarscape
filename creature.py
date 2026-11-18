class Creature:
    def __init__(self, creatureID, cell, configuration):
        self.ID = creatureID
        self.cell = cell
        self.debug = cell.environment.sugarscape.debug