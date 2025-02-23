import random

import src

class FarmMold(src.quests.MetaQuestSequence):
    type = "FarmMold"

    def __init__(self, description="farm mold", creator=None, toCollect=None, lifetime=None, reason=None, tryHard=False):
        self.lastMoveDirection = None
        questList = []
        super().__init__(questList, creator=creator,lifetime=lifetime)
        self.metaDescription = description
        self.reason = reason
        if toCollect:
            self.metaDescription += " for "+toCollect
        self.toCollect = toCollect
        self.tryHard = tryHard

    def generateTextDescription(self):
        out = []

        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        text = """
farm mold"""

        out.append(text)
        return out

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False
        if not character.getFreeInventorySpace():
            self.postHandler()
            return True
        if character.getTerrain().alarm and not self.tryHard:
            self.postHandler()
            return True
        return False

    def getNextStep(self,character,ignoreCommands=False, dryRun = True):

        if self.subQuests:
            return (None,None)

        if not character:
            return (None,None)

        terrain = character.getTerrain()

        candidates = []
        for (coord,itemList) in terrain.itemsByBigCoordinate.items():
            if character.getTerrain().getRoomByPosition(coord):
                continue

            for item in itemList:
                if not item.type == "Bloom":
                    continue

                candidates.append(coord)

        if candidates:
            coord = random.choice(candidates)
            quest = src.quests.questMap["FarmMoldTile"](targetPosition=coord,stimulateMoldGrowth=False,tryHard=self.tryHard)
            return ([quest],None)

        candidates = []
        for (coord,itemList) in terrain.itemsByBigCoordinate.items():
            if character.getTerrain().getRoomByPosition(coord):
                continue

            numSprouts = 0
            for item in itemList:
                if not item.type == "Sprout":
                    continue
                
                if len(character.container.getItemByPosition(item.getPosition())) > 1:
                    continue

                numSprouts += 1

            if numSprouts > 4:
                candidates.append(coord)

        if candidates:
            coord = random.choice(candidates)
            quest = src.quests.questMap["FarmMoldTile"](targetPosition=coord,tryHard=self.tryHard)
            return ([quest],None)

        return (None,None)

    def pickedUpItem(self,test=None):
        pass

    @staticmethod
    def generateDutyQuest(beUsefull,character,currentRoom, dryRun):
        terrain = character.getTerrain()
        try:
            terrain.alarm
        except:
            terrain.alarm = False
        if terrain.alarm:
            return (None,None)

        quest = src.quests.questMap["FarmMold"](lifetime=1000)
        if not dryRun:
            beUsefull.idleCounter = 0
        return ([quest],None)

src.quests.addType(FarmMold)
