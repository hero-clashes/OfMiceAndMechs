import src

class ReachOutStory(src.quests.MetaQuestSequence):
    type = "ReachOutStory"

    def __init__(self, description="reach out to implant", creator=None):
        questList = []
        super().__init__(creator=creator)
        self.metaDescription = description

    def solver(self,character):
        self.triggerCompletionCheck()
        self.generateSubquests()

        if not self.subQuests:
            command = self.getSolvingCommandString(character)
            if command:
                character.runCommandString(command)
                return
            
        super().solver(character)

    def triggerCompletionCheck(self):
        return

    def handleQuestsOpened(self,extraInfo=None):
        self.postHandler()

    def assignToCharacter(self,character):
        if self.character:
            return

        self.startWatching(character,self.handleQuestsOpened,"opened quest menu")
        return super().assignToCharacter(character)

    def getSolvingCommandString(self,character,dryRun=True):
        if character.macroState.get("submenue"):
            return ["esc"]
        else:
            return "q"

src.quests.addType(ReachOutStory)