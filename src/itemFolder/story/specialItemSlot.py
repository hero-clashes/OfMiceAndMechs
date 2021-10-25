import src


class SpecialItemSlot(src.items.Item):
    """
    ingame item transforming into a rip in reality when using a key
    """

    type = "SpecialItemSlot"

    def __init__(self):
        """
        configure the superclass
        """

        super().__init__(display=src.canvas.displayChars.sparkPlug)
        self.name = "special item slot"

        self.walkable = True
        self.bolted = True
        self.strength = 1
        self.itemID = None
        self.hasItem = False

    def apply(self, character):
        """
        handle a chracter trying to unlock the item

        Parameters:
            character: the character trying to unlock the item
        """

        if self.hasItem == False:
            foundItem = None
            for item in character.inventory:
                if not item.type == "SpecialItem":
                    continue
                if item.itemID == self.itemID:
                    foundItem = item
                    break

            if foundItem:
                character.inventory.remove(foundItem)

                self.hasItem = True
                character.addMessage("you add the special item")
            else:
                character.addMessage("you need to have special item #%s in your inventory"%(self.itemID,))
        else:
            newItem = src.items.itemMap["SpecialItem"]()
            newItem.itemID = self.itemID
            if self.yPosition == 1:
                self.container.addItem(newItem,(self.xPosition,self.yPosition+1,self.zPosition))
            else:
                self.container.addItem(newItem,(self.xPosition+1,self.yPosition,self.zPosition))

            self.hasItem = False

    def render(self):
        if self.hasItem:
            return ":)"
        else:
            return src.canvas.displayChars.sparkPlug

src.items.addType(SpecialItemSlot)