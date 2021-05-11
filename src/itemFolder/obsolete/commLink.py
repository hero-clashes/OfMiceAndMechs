import src

'''
a dummy for an interface with the mech communication network
bad code: this class is dummy only and basically is to be implemented
'''
class Commlink(src.items.Item):
    type = "CommLink"

    '''
    call superclass constructor with modified paramters
    '''
    def __init__(self,xPosition=0,yPosition=0,name="Commlink",creator=None,noId=False):
        super().__init__(src.canvas.displayChars.commLink,xPosition,yPosition,name=name,creator=creator)

        self.scrapToDeliver = 100
        self.attributesToStore.extend([
               "scrapToDeliver"])

    '''
    get tributes and trades
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        if self.scrapToDeliver > 0:
            toRemove = []
            for item in character.inventory:
                if isinstance(item,itemMap["Scrap"]):
                    toRemove.append(item)
                    self.scrapToDeliver -= 1

            character.addMessage("you need to delivered %s scraps"%(len(toRemove)))
            for item in toRemove:
                character.inventory.remove(item)

        if self.scrapToDeliver > 0:
            character.addMessage("you need to deliver %s more scraps to have payed tribute"%(self.scrapToDeliver))
            return

        character.addMessage("you have payed tribute yay")

    def getLongInfo(self):
        text = """
item: CommLink

description:
A comlink. 

"""

src.items.addType(Commlink)