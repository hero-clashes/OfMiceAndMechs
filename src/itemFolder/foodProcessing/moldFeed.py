import src


class MoldFeed(src.items.Item):
    """
    ingame item acting as a fertilizer for mold.
    """

    type = "MoldFeed"

    def __init__(self):
        """
        configure super class
        """

        super().__init__(display=src.canvas.displayChars.moldFeed)
        self.name = "mold feed"
        self.description = "This is a good base for mold growth. If mold grows onto it, it will grow into a bloom."
        self.usageInfo = """
place mold feed next to a mold and when the mold grows onto it, it will grow into a bloom.

Activate it to eat
"""

        self.walkable = True
        self.bolted = False

    def destroy(self, generateScrap=True):
        """
        destroy this item without leaving residue
        """

        super().destroy(generateScrap=False)

    def apply(self, character):
        """
        handle a character eating the item

        Parameters:
            character: the character eating this item
        """

        character.addSatiation(1000,reason="ate mold feed")
        self.destroy()

    def pickUp(self, character):
        self.startWatching(character,self.OnDrop,"dropped")
        character.addMessage("it's heavy and slows you down")
        self.debuff = src.statusEffects.statusEffectMap["Slowed"](slowDown=0.1, duration = None, reason="You carry a MoldFeed", inventoryItem=self)
        character.statusEffects.append(self.debuff)
        super().pickUp(character)

    def OnDrop(self,params):
        (character,item) = params
        if item == self:
            character.statusEffects.remove(self.debuff)
            self.stopWatching(character,self.OnDrop,"dropped")


src.items.addType(MoldFeed)
