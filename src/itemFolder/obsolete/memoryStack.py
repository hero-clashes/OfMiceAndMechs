import src

'''
'''
class MemoryStack(src.items.Item):
    type = "MemoryStack"

    '''
    call superclass constructor with modified parameters
    '''
    def __init__(self,xPosition=None,yPosition=None, name="MemoryStack",creator=None,noId=False):

        self.macros = []

        super().__init__(src.canvas.displayChars.memoryStack,xPosition,yPosition,name=name,creator=creator)

        self.attributesToStore.extend([
                "macros"])

    '''
    trigger production of a player selected item
    '''
    def apply(self,character):
        super().apply(character,silent=True)

        if not self.room:
            character.addMessage("this machine can only be used within rooms")
            return

        options = []

        options.append(("p","push macro on stack"))
        options.append(("l","load/pop macro from stack"))

        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = self.doAction

        self.character = character

    '''
    '''
    def doAction(self):

        import copy
        if self.submenue.getSelection() == "p":
            self.character.addMessage("push your macro onto the memory stack")
            self.macros.append(copy.deepcopy(self.character.macroState["macros"]))
            self.character.addMessage(self.macros)
        elif self.submenue.getSelection() == "l":
            self.character.addMessage("you load a macro from the memory stack")
            self.character.macroState["macros"] = copy.deepcopy(self.macros.pop())
            self.character.addMessage(self.character.macroState["macros"])
        else:
            self.character.addMessage("invalid option")

src.items.addType(MemoryStack)