import src
import random

class PlaceItem(src.quests.MetaQuestSequence):
    type = "PlaceItem"

    def __init__(self, description="place item", creator=None, lifetime=None, targetPosition=None, targetPositionBig=None, itemType=None, tryHard=False, boltDown=False,reason=None):
        questList = []
        super().__init__(questList, creator=creator, lifetime=lifetime)
        self.metaDescription = "%s %s on position %s on tile %s"%(description,itemType,targetPosition,targetPositionBig,)
        self.targetPosition = targetPosition
        self.targetPositionBig = targetPositionBig
        self.itemType = itemType
        self.tryHard = tryHard
        self.boltDown = boltDown
        self.reason = reason

    def generateTextDescription(self):
        reason = ""
        if self.reason:
            reason = ", to %s"%(self.reason,)
        text = """
place item %s on position %s on tile %s%s."""%(self.itemType,self.targetPosition,self.targetPositionBig,reason,)
        if self.boltDown:
            text += """
Bolt down the item afterwards."""

        if not self.character.inventory or not self.character.inventory[-1].type == self.itemType:
            text += """

You do not have a %s in your inventory."""%(self.itemType,)
        else:
            text += """

You have a %s in your inventory."""%(self.itemType,)

        if self.character.getBigPosition() == self.targetPositionBig:
            text += """

You are on the target tile.
"""
        else:
            direction = ""
            diffXBig = self.targetPositionBig[0] - self.character.getBigPosition()[0]
            if diffXBig < 0:
                direction = "and %s tiles to the west"%(-diffXBig,)
            if diffXBig > 0:
                direction = "and %s tiles to the east"%(diffXBig,)
            diffYBig = self.targetPositionBig[1] - self.character.getBigPosition()[1]
            if diffYBig < 0:
                direction = "and %s tiles to the north"%(-diffYBig,)
            if diffYBig > 0:
                direction = "and %s tiles to the south"%(diffXBig,)
            text += """

The target tile is %s
"""%(direction[4:],)
        
        if self.tryHard:
            text += """

Try as hard as you can to achieve this.
If you don't find the items to place, produce them.
"""

        return text

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character, self.droppedItem, "dropped")
        self.startWatching(character, self.producedItem, "producedItem")
        super().assignToCharacter(character)

    def getQuestMarkersTile(self,character):
        result = super().getQuestMarkersTile(character)
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
            result.append(((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15),"target"))
        else:
            if character.getBigPosition() == self.targetPositionBig:
                result.append(((self.targetPosition[0],self.targetPosition[1]),"target"))
        return result

    def producedItem(self,extraInfo):
        item = extraInfo["item"]
        self.checkPlacedItem(item)

    def droppedItem(self,extraInfo):
        item = extraInfo[1]
        self.checkPlacedItem(item)

    def checkPlacedItem(self,item):
        if item.type == self.itemType:
            if item.container.isRoom:
                if item.container.getPosition() == self.targetPositionBig and item.getPosition() == self.targetPosition:
                    self.postHandler()
            else:
                if item.getPosition() == (self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15,0):
                    self.postHandler()

    def solver(self, character):
        if self.triggerCompletionCheck(character):
            return
        (nextQuests,nextCommand) = self.getNextStep(character)
        if nextQuests:
            for quest in nextQuests:
                self.addQuest(quest)
                self.startWatching(quest,self.unhandledSubQuestFail,"failed")
            return

        if nextCommand:
            character.runCommandString(nextCommand[0])
            return
        super().solver(character)

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

    def unhandledSubQuestFail(self,extraParam):
        self.fail(extraParam["reason"])

    def getNextStep(self,character=None,ignoreCommands=False):
        if not self.subQuests:
            if not ignoreCommands:
                submenue = character.macroState.get("submenue")
                if submenue:
                    return (None,(["esc"],"exit the menu"))

            itemFound = None
            itemIndex = 0
            for item in reversed(character.inventory):
                itemIndex += 1
                if item.type == self.itemType:
                    itemFound = item
                    break

            if not itemFound:
                quest = src.quests.questMap["FetchItems"](toCollect=self.itemType,amount=1,takeAnyUnbolted=True,tryHard=self.tryHard,reason="have an item to place")
                return ([quest],None)

            if not character.getBigPosition() == self.targetPositionBig:
                quest = src.quests.questMap["GoToTile"](targetPosition=self.targetPositionBig,description="go to buildsite",reason="be able to place the %s"%(self.itemType,))
                return ([quest],None)

            if not itemFound.walkable:
                if character.container.isRoom:
                    items = character.container.getItemByPosition((self.targetPosition[0],self.targetPosition[1],0))
                else:
                    items = character.container.getItemByPosition((self.targetPositionBig[0]*15+self.targetPosition[0],self.targetPositionBig[1]*15+self.targetPosition[1],0))
                if items:
                    quest = src.quests.questMap["CleanSpace"](targetPosition=self.targetPosition,targetPositionBig=self.targetPositionBig)
                    return ([quest],None)

            if not character.getSpacePosition() == self.targetPosition:
                quest = src.quests.questMap["GoToPosition"](targetPosition=self.targetPosition,description="go to placement spot",reason="be able to place the %s"%(self.itemType,))
                return ([quest],None)

            if itemIndex > 1:
                dropCommand = "il"+itemIndex*"w"+"j"
            else:
                dropCommand = "l"

            if self.boltDown:
                return (None,(dropCommand+"cb","drop and bolt the item"))
            else:
                return (None,(dropCommand,"drop the item"))
        return (None,None)
    
    def triggerCompletionCheck(self,character=None):
        if not character:
            return False

        rooms = character.getTerrain().getRoomByPosition(self.targetPositionBig)
        if not rooms:
            items = character.getTerrain().getItemByPosition((self.targetPosition[0]+self.targetPositionBig[0]*15,self.targetPosition[1]+self.targetPositionBig[1]*15,0))
        else:
            items = rooms[0].getItemByPosition(self.targetPosition)

        if not items:
            return False

        if items[-1].type == self.itemType:
            self.postHandler()
            return True
        return False

src.quests.addType(PlaceItem)
