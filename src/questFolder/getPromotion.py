import src


class GetPromotion(src.quests.MetaQuestSequence):
    type = "GetPromotion"

    def __init__(self, targetRank, description="get promotion", reason=None):
        super().__init__()
        self.metaDescription = description
        self.targetRank = targetRank
        self.reason = reason

    def generateTextDescription(self):
        reasonString = ""
        if self.reason:
            reasonString = ", to "+self.reason

        text = f"""
Rise in the hierarchy and get a Promotion{reasonString}.
Use the Promotor to do this.
"""

        return text

    def handleGotPromotion(self, extraInfo):
        self.postHandler()

    def assignToCharacter(self, character):
        if self.character:
            return

        self.startWatching(character,self.handleGotPromotion, "got promotion")

        super().assignToCharacter(character)

    def triggerCompletionCheck(self,character=None):
        if not character:
            return None

        if character.rank <= self.targetRank:
            self.postHandler()
            return True
        return False

    def getSolvingCommandString(self,character,dryRun=True):
        if self.subQuests:
            return None

        submenue = character.macroState.get("submenue")
        if submenue:
            if isinstance(submenue,src.interaction.SelectionMenu):
                return ["enter"]
            return ["esc"]

        room = character.container
        if not isinstance(character.container, src.rooms.Room):
            return None

        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if item.type != "Promoter":
                continue

            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                return "Ja"
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return "Jd"
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return "Jw"
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return "Js"
        return super().getSolvingCommandString(character,dryRun=dryRun)

    def generateSubquests(self,character):
        if not self.active:
            return

        if self.subQuests:
            return

        room = character.container

        if not isinstance(character.container, src.rooms.Room):
            quest = src.quests.questMap["GoHome"](description="go to command centre")
            self.addQuest(quest)
            quest.assignToCharacter(character)
            quest.activate()
            return

        for item in room.itemsOnFloor:
            if not item.bolted:
                continue
            if item.type != "Promoter":
                continue

            if item.getPosition() == (character.xPosition-1,character.yPosition,0):
                return
            if item.getPosition() == (character.xPosition+1,character.yPosition,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition-1,0):
                return
            if item.getPosition() == (character.xPosition,character.yPosition+1,0):
                return
            quest = src.quests.questMap["GoToPosition"](targetPosition=item.getPosition(),ignoreEndBlocked=True,description="go to promoter ")
            quest.active = True
            quest.assignToCharacter(character)
            self.addQuest(quest)
            return
        quest = src.quests.questMap["GoToTile"](targetPosition=(7,7,0),description="go to command centre")
        self.addQuest(quest)
        quest.assignToCharacter(character)
        quest.activate()
        return

    def solver(self,character):
        self.triggerCompletionCheck(character)
        if not self.subQuests:
            self.generateSubquests(character)

            if self.subQuests:
                return

            command = self.getSolvingCommandString(character,dryRun=False)
            if command:
                character.runCommandString(command)
                return

        super().solver(character)

src.quests.addType(GetPromotion)
