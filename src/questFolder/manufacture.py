import src


class Manufacture(src.quests.MetaQuestSequence):
    type = "Manufacture"

    def __init__(self, description="manufacture", creator=None, targetPosition=None, targetPositionBig=None,reason=None):
        questList = []
        super().__init__(questList, creator=creator)
        self.metaDescription = description
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.reason = reason

    def handleManufactured(self, extraInfo):
        if self.completed:
            1/0
        if not self.active:
            return

        if extraInfo["table"].getPosition() == self.targetPosition:
            self.postHandler()
            return

    def handleManufacturingFailed(self, extraInfo):
        self.fail("manufacturing table unavailable")

    def assignToCharacter(self, character):
        if self.character:
            return None

        self.startWatching(character,self.handleManufactured, "manufactured")
        self.startWatching(character,self.handleManufacturingFailed, "failed manufacturing")

        return super().assignToCharacter(character)

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = f", to {self.reason}"
        return f"""
use the manufacturing table on {self.targetPosition}{reason}.
"""

    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            return False

        if not character.container.isRoom:
            self.fail()
            return True

        items = character.container.getItemByPosition(self.targetPosition)
        if not items or items[0].type not in ("ManufacturingTable",):
            self.fail()
            return True

        return False

    def getNextStep(self,character,ignoreCommands=False):
        if self.subQuests:
            return (None,None)

        if self.targetPositionBig and character.getBigPosition() != self.targetPositionBig:
            quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,reason="get to the tile the machine is on")
            return ([quest],None)

        pos = character.getPosition()
        if self.targetPosition not in (pos,(pos[0],pos[1]+1,pos[2]),(pos[0]-1,pos[1],pos[2]),(pos[0]+1,pos[1],pos[2]),(pos[0],pos[1]-1,pos[2])):
            quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,ignoreEndBlocked=True,reason="get near the machine")
            return ([quest],None)

        if (pos[0],pos[1],pos[2]) == self.targetPosition:
            return (None,("jj","manufacture item"))
        if (pos[0]-1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Jaj","manufacture item"))
        if (pos[0]+1,pos[1],pos[2]) == self.targetPosition:
            return (None,("Jdj","manufacture item"))
        if (pos[0],pos[1]-1,pos[2]) == self.targetPosition:
            return (None,("Jwj","manufacture item"))
        if (pos[0],pos[1]+1,pos[2]) == self.targetPosition:
            return (None,("Jsj","manufacture item"))
        return None

    def getSolvingCommandString(self, character, dryRun=True):
        nextStep = self.getNextStep(character)
        if nextStep == (None,None):
            return super().getSolvingCommandString(character)
        return self.getNextStep(character)[1]

    def generateSubquests(self, character=None):
        (nextQuests,nextCommand) = self.getNextStep(character,ignoreCommands=True)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

    def solver(self, character):
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
        if self.targetPositionBig:
            result.append(((self.targetPositionBig[0],self.targetPositionBig[1]),"target"))
        return result

    def getQuestMarkersSmall(self,character,renderForTile=False):
        if isinstance(character.container,src.rooms.Room):
            if renderForTile:
                return []
        else:
            if not renderForTile:
                return []

        result = super().getQuestMarkersSmall(character,renderForTile=renderForTile)
        if renderForTile:
            if self.targetPosition and self.targetPositionBig:
                result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result


src.quests.addType(Manufacture)
