import src
import random
import copy
import json

class PersonnelArtwork(src.items.Item):
    """
    a ingame item to build and extend cities
    is a representation of a city and holds the coresponding information
    takes tasks and delegates tasks to other manager
    """


    type = "PersonnelArtwork"

    def __init__(self, name="PersonnelArtwork", noId=False):
        """
        set up the initial state
        """

        super().__init__(display="PA", name=name)

        self.applyOptions.extend(
                        [
                                                                ("viewNPCs", "view npcs"),
                                                                ("spawnBodyguard", "spawn bodyguard"),
                                                                ("spawnRank4", "spawn rank4"),
                                                                ("spawnIndependentFighter", "spawn independent fighter"),
                                                                ("spawnIndependentWorker", "spawn independent worker"),
                        ]
                        )
        self.applyMap = {
                    "viewNPCs": self.viewNPCs,
                    "spawnRank6": self.spawnRank6,
                    "spawnRank5": self.spawnRank5,
                    "spawnRank4": self.spawnRank4,
                    "spawnRank3": self.spawnRank3,
                    "spawnMilitary": self.spawnMilitary,
                    "spawnSet": self.spawnSet,
                    "spawnRankUnranked": self.spawnRankUnranked,
                    "spawnBodyguard": self.spawnBodyguard,
                    "spawnIndependentWorker": self.spawnIndependentWorker,
                    "spawnIndependentFighter": self.spawnIndependentFighter,
                        }
        self.cityLeader = None
        self.description = """
This is a one of its kind machine. It cannot be reproduced and was created by an artisan.
This item allows to manage the clones in this base."""
        self.usageInfo = """
Activate the item to use it.
Use the item so see an overview over the NPCs in this base."""
        self.charges = 3

    def changeCharges(self,delta):
        self.charges += delta

    def viewNPCs(self,character):
        submenue = src.interaction.ViewNPCsMenu(self)
        character.macroState["submenue"] = submenue

    def getPersonnelList(self):

        personel = []

        cityLeader = self.fetchCityleader()

        if not cityLeader:
            return []

        personel.append(cityLeader)

        for subleader in cityLeader.subordinates:
            if not subleader or subleader.dead:
                continue

            personel.append(subleader)

            for subsubleader in subleader.subordinates:
                if not subsubleader or subsubleader.dead:
                    continue

                personel.append(subsubleader)

                for worker in subsubleader.subordinates:
                    if not worker or worker.dead:
                        continue

                    personel.append(worker)
        return personel
        
    def fetchCityleader(self):
        if self.cityLeader and self.cityLeader.dead:
            self.cityLeader = None
        return self.cityLeader

    def setCityleader(self,character):
        self.cityLeader = character

    def spawnSet(self,character):
        cityleader = self.spawnRank(3,character)
        for i in range(0,3):
            self.spawnRank(4,character)
        for i in range(0,9):
            self.spawnRank(5,character)
        for i in range(0,9*3):
            self.spawnRank(6,character)
        return cityleader

    def spawnRank6(self,character):
        return self.spawnRank(6,character)
    def spawnRank5(self,character):
        return self.spawnRank(5,character)
    def spawnRank4(self,character):
        return self.spawnRank(4,character)
    def spawnRank3(self,character):
        return self.spawnRank(3,character)
    def spawnRankUnranked(self,character):
        return self.spawnRank(None,character)

    def spawnMilitary(self,character):
        return self.spawnRank(None,character,isMilitary=True)

    def spawnIndependentFighter(self,character):
        if not self.charges:
            character.addMessage("no charges left. Use the epoch artwork to recharge")
            return None
        self.charges -= 1

        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        char.rank = None

        char.faction = character.faction

        quest = src.quests.ActivateEpochArtwork(epochArtwork=self.container.getItemByPosition((6,6,0))[0])
        quest.assignToCharacter(char)
        quest.activate()
        char.quests.append(quest)
        char.baseDamage = 10
        char.movementSpeed = 1.5

        char.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest",
            "NaiveDropQuest",
            "NaiveMurderQuest",
            "DropQuestMeta",
            "DeliverSpecialItem",
        ] 

        self.container.addCharacter(char,5,6)
        char.runCommandString("********")

    def spawnIndependentWorker(self,character):
        if not self.charges:
            character.addMessage("no charges left. Use the epoch artwork to recharge")
            return None
        self.charges -= 1

        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        char.rank = None
        char.baseDamage = 5
        char.movementSpeed = 0.5

        char.faction = character.faction

        quest = src.quests.ActivateEpochArtwork(epochArtwork=self.container.getItemByPosition((6,6,0))[0])
        quest.assignToCharacter(char)
        quest.activate()
        char.quests.append(quest)

        char.solvers = [
            "SurviveQuest",
            "Serve",
            "NaiveMoveQuest",
            "MoveQuestMeta",
            "NaiveActivateQuest",
            "ActivateQuestMeta",
            "NaivePickupQuest",
            "PickupQuestMeta",
            "DrinkQuest",
            "ExamineQuest",
            "FireFurnaceMeta",
            "CollectQuestMeta",
            "WaitQuest",
            "NaiveDropQuest",
            "NaiveMurderQuest",
            "DropQuestMeta",
            "DeliverSpecialItem",
        ] 

        self.container.addCharacter(char,5,6)
        char.runCommandString("********")

    def spawnBodyguard(self,character):
        if character.rank == None or character.rank > 5:
            character.addMessage("you need to be rank 5 or higher to spawn a bodyguard") 
            return None

        if not self.charges:
            character.addMessage("no charges left. Use the epoch artwork to recharge")
            return None

        self.charges -= 1
        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        char.rank = 6

        character.subordinates.append(char)
        char.superior = character
        char.faction = character.faction

        quest = src.quests.ProtectSuperior()
        quest.assignToCharacter(char)
        quest.activate()
        char.quests.append(quest)

        self.container.addCharacter(char,5,6)
        char.runCommandString("********")

    def spawnRank(self,rank,actor,isMilitary=False):
        cityLeader = self.fetchCityleader()

        if rank == 3:
            if cityLeader and not cityLeader.dead:
                actor.addMessage("only one rank 3 possible")
                return

        if rank == 4:
            if not cityLeader or self.cityLeader.dead:
                actor.addMessage("no rank 3 to hook into")
                return

            for subleader in cityLeader.subordinates:
                if subleader.dead:
                    cityLeader.subordinates.remove(subleader)

            if len(cityLeader.subordinates) > 2:
                actor.addMessage("no rank 3 to hook into")
                return

        if rank == 5:
            if not cityLeader or cityLeader.dead:
                actor.addMessage("no rank 3 to hook into")
                return

            foundSubleader = None
            for subleader in cityLeader.subordinates:
                if subleader.dead:
                    continue
                for subsubleader in subleader.subordinates:
                    if subsubleader.dead:
                        subleader.subordinates.remove(subsubleader)
                if len(subleader.subordinates) > 2:
                    continue
                foundSubleader = subleader

            if not foundSubleader:
                actor.addMessage("no rank 4 to hook into")
                return

        if rank == 6:
            if not cityLeader or cityLeader.dead:
                actor.addMessage("no rank 3 to hook into")
                return

            foundSubsubleader = None
            for subleader in cityLeader.subordinates:
                if subleader.dead:
                    continue

                for subsubleader in subleader.subordinates:
                    if subsubleader.dead:
                        continue
                    for subordinate in subsubleader.subordinates[:]:
                        if subordinate.dead:
                            subsubleader.subordinates.remove(subordinate)
                    if len(subsubleader.subordinates) > 2:
                        continue
                    foundSubsubleader = subsubleader

            if not foundSubsubleader:
                actor.addMessage("no rank 5 to hook into")
                return

        char = src.characters.Character()
        char.registers["HOMEx"] = self.container.xPosition
        char.registers["HOMEy"] = self.container.yPosition
        char.personality["abortMacrosOnAttack"] = False

        if rank == 3:
            if not cityLeader or cityLeader.dead:
                self.cityLeader = char

        if rank == 4:
            cityLeader.subordinates.append(char)
            char.duties.extend(["scratch checking","clearing","painting"])

        if rank == 5:
            foundSubleader.subordinates.append(char)
            char.duties.extend(["resource fetching","trap setting","hauling","machine placing"])

        if rank == 6:
            foundSubsubleader.subordinates.append(char)
            char.duties.extend(["resource gathering"])

        quest = src.quests.BeUsefull()
        quest.assignToCharacter(char)
        quest.activate()
        char.quests.append(quest)
        char.faction = actor.faction
        char.isMilitary = False
        if rank:
            char.rank = rank
        self.container.addCharacter(char,5,6)
        char.runCommandString("********")
        char.godMode = True

        return char

src.items.addType(PersonnelArtwork)
