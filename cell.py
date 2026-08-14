import math

class Cell:
    def __init__(self, x, y, environment, maxSugar=0, maxSpice=0, growbackRate=0, waterCapacity = 0.0):
        self.x = x
        self.y = y
        self.environment = environment
        self.maxSugar = maxSugar
        self.maxSpice = maxSpice

        #waterrr
        self.waterCapacity = float(waterCapacity)

        self.agent = None
        self.hemisphere = "north" if self.x >= self.environment.equator else "south"
        self.neighbors = {}
        self.pollution = 0
        self.pollutionFlux = 0
        self.ranges = {}
        self.season = None
        self.spice = maxSpice
        self.spiceLastProduced = 0
        self.sugar = maxSugar
        self.sugarLastProduced = 0
        self.timestep = 0

    def doPollutionDiffusion(self):
        self.pollution = self.pollutionFlux

    def doSpiceConsumptionPollution(self, spiceConsumed):
        if self.isPollutionEnabled() == True:
            consumptionPollutionFactor = self.environment.spiceConsumptionPollutionFactor
            self.pollution += consumptionPollutionFactor * spiceConsumed

    def doSpiceProductionPollution(self, spiceProduced):
        if self.isPollutionEnabled() == True:
            productionPollutionFactor = self.environment.spiceProductionPollutionFactor
            self.pollution += productionPollutionFactor * spiceProduced

    def doSugarConsumptionPollution(self, sugarConsumed):
        if self.isPollutionEnabled() == True:
            consumptionPollutionFactor = self.environment.sugarConsumptionPollutionFactor
            self.pollution += consumptionPollutionFactor * sugarConsumed

    def doSugarProductionPollution(self, sugarProduced):
        if self.isPollutionEnabled() == True:
            productionPollutionFactor = self.environment.sugarProductionPollutionFactor
            self.pollution += productionPollutionFactor * sugarProduced

    def findDistToRiver(self):
        config = self.environment.sugarscape.configuration
        orientation = config.get("environmentRiverOrientation", "vertical")
        location = config.get("environmentRiverLocation", 30)

        riverCenter = location - 0.5

        if orientation == "horizontal":
            return abs(self.y - riverCenter)
        elif orientation == "diagonal":
            return abs(self.x-self.y) / math.sqrt(2)
        else:
            return abs(self.x - riverCenter)

    def findEastNeighbor(self):
        if self.environment.wraparound == False and self.x + 1 > self.environment.width - 1:
            return None
        eastNeighbor = self.environment.findCell((self.x + 1 + self.environment.width) % self.environment.width, self.y)
        return eastNeighbor

    def findNeighborAgents(self):
        agents = []
        for neighbor in self.neighbors.values():
            agent = neighbor.agent
            if agent != None:
                agents.append(agent)
        return agents

    def findNeighbors(self, mode):
        self.neighbors = {}

        north = self.findNorthNeighbor()
        south = self.findSouthNeighbor()
        east = self.findEastNeighbor()
        west = self.findWestNeighbor()
        if north is not None:
            self.neighbors["north"] = north
        if south is not None:
            self.neighbors["south"] = south
        if east is not None:
            self.neighbors["east"] = east
        if west is not None:
            self.neighbors["west"] = west

        if mode == "moore":
            northeast = north.findEastNeighbor() if north is not None else None
            northwest = north.findWestNeighbor() if north is not None else None
            southeast = south.findEastNeighbor() if south is not None else None
            southwest = south.findWestNeighbor() if south is not None else None
            if northeast is not None:
                self.neighbors["northeast"] = northeast
            if northwest is not None:
                self.neighbors["northwest"] = northwest
            if southeast is not None:
                self.neighbors["southeast"] = southeast
            if southwest is not None:
                self.neighbors["southwest"] = southwest

    def findNeighborWealth(self):
        neighborWealth = 0
        for neighbor in self.neighbors.values():
            if neighbor != None:
                neighborWealth += neighbor.sugar + neighbor.spice
        return neighborWealth

    def findNorthNeighbor(self):
        if self.environment.wraparound == False and self.y - 1 < 0:
            return None
        northNeighbor = self.environment.findCell(self.x, (self.y - 1 + self.environment.height) % self.environment.height)
        return northNeighbor

    def findPollutionFlux(self):

        config = self.environment.sugarscape.configuration
        waterPolFlow = config.get("environmentWaterPollutionFlow", True)

        if waterPolFlow and getattr(self, 'waterCapacity', 0.0) == 1.0:
            orientation = config.get("environmentRiverOrientation", "horizontal")
            flowRate = config.get("environmentWaterPollutionFlowRate", 0.5)

            if orientation == "vertical":
                upstreamKey = "north"
            else:
                upstreamKey = "west"

            upstreamCell = self.neighbors.get(upstreamKey) 

            if upstreamCell is not None:

                ambientDiffusion = sum(n.pollution for n in self.neighbors.values()) / len(self.neighbors) if self.neighbors else 0.0      

                self.pollutionFlux = (flowRate * upstreamCell.pollution) + ((1.0 - flowRate) * ambientDiffusion)
                return

        meanPollution = 0
        for neighbor in self.neighbors.values():
            meanPollution += neighbor.pollution
        if len(self.neighbors) > 0:
            meanPollution = meanPollution / (len(self.neighbors))
        self.pollutionFlux = meanPollution

    def findSouthNeighbor(self):
        if self.environment.wraparound == False and self.y + 1 < self.environment.height - 1:
            return None
        southNeighbor = self.environment.findCell(self.x, (self.y + 1 + self.environment.height) % self.environment.height)
        return southNeighbor

    def findWestNeighbor(self):
        if self.environment.wraparound == False and self.x - 1 < 0:
            return None
        westNeighbor = self.environment.findCell((self.x - 1 + self.environment.width) % self.environment.width, self.y)
        return westNeighbor

    def isOccupied(self):
        return self.agent != None

    def isPollutionEnabled(self):
        return self.environment.pollutionStart <= self.timestep <= self.environment.pollutionEnd

    def resetAgent(self):
        self.agent = None

    def resetSpice(self):
        self.spice = 0

    def resetSugar(self):
        self.sugar = 0

    def updateSeason(self):
        if self.season == "wet":
            self.season = "dry"
        else:
            self.season = "wet"

        self.updateWaterCap()

    def updateWaterCap(self):
        config = self.environment.sugarscape.configuration

        currSeason = getattr(self.environment, 'season', None)

        if currSeason == "dry":
            riverWidth = config.get("environmentRiverWidthDry", 2)
        else:
            riverWidth = config.get("environmentRiverWidthWet", 4)

        floodPlainWidth = riverWidth * 0.5
        halfWidth = riverWidth * 0.5

        dist = self.findDistToRiver()

        if dist < halfWidth:
            self.waterCapacity = 1.0
        elif dist < (halfWidth + floodPlainWidth):
            self.waterCapacity = 0.5
        else:
            self.waterCapacity = 0.0

    def __str__(self):
        string = ""
        if self.agent != None:
            string = "-A-"
        else:
            string = f"{str(self.sugar)}/{str(self.spice)}"
        return string
