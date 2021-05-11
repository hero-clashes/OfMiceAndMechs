####################################################################################
###
##     items and item related code belongs here 
#
####################################################################################

import config
import src.logger
import src.gamestate
import src.interaction

def setup():
    import src.itemFolder

# load basic libs
import json
import random
import uuid

# load basic internal libs
import src.saveing
import src.events
import config

class ItemNew(src.saveing.Saveable):
    """
    This is the base class for ingame items. It is intended to hold the common behaviour of items.
    Since i'm in the middle of refactoring things there are two base classes for items at the moment.
    This is the class stuff should be migrated to.

    Attributes:
        seed (int): rng seed intended to have predictable randomness
        container: references where the item is placed currently
    
    """
    type = "Item"

    def __init__(self,display=None,xPosition=0,yPosition=0,zPosition=0,name="unkown",seed=0,noId=False)
            """
            the constructor

            Parameters:
                display: information on how the item is shown, can be a string  
                xPosition: position information
                yPosition: position information
                zPosition: position information
                name: name shown to the user
                seed: rng seed
                noId: flag to prevent generating useless ids (obsolete?)
            """
        super().__init__()
        
        if not display:
            self.display = src.canvas.displayChars.notImplentedYet
        else:
            try:
                self.display = display
            except:
                pass

        # basic information
        self.seed = seed
        self.name = name
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.zPosition = zPosition
        self.container = None
        self.walkable = False
        self.bolted = True
        self.description = "a "+self.name
        self.tasks = []
        self.blocked = False

        # flags for traits
        self.runsJobOrders = runsJobOrders
        self.hasSettings = hasSettings
        self.runsCommands = runsCommands
        self.canReset = canReset
        self.hasMaintenance = False

        # properties for traits
        self.commands = {}
        self.applyOptions = []

        # set up metadata for saving
        self.attributesToStore.extend([
               "seed","xPosition","yPosition","zPosition","name","type",
               "walkable","bolted","description",
               "isConfigurable","hasSettings","runsCommands","canReset",
               "commands",
               ])

        if not noId:
            self.id = uuid.uuid4().hex
        else:
            self.id = None

    def useJoborderRelayToLocalRoom(self,character,tasks,itemType,information={}):
            """
            delegate a task to another item using a room manager

            Parameters:
                character: the character used for running the job order
                tasks: the tasks to delegate
                itemType: the type of item the task should be delegated to
                information: optional information block on the job order
            """

        # set up job order
        jobOrder = src.items.itemMap["JobOrder"]()
        jobOrder.taskName = "relay job Order"
        jobOrder.information = information

        # prepare the task for gooing to the roommanager
        newTasks = [
                {
                    "task":"go to room manager",
                    "command":self.commands["go to room manager"]
                },]

        # prepare the tasks for delegating the given tasks
        for task in tasks:
            newTasks.append(
                {
                    "task":"insert job order",
                    "command":"scj",
                })
            newTasks.append(
                    {
                        "task":"relay job order",
                        "command":None,
                        "type":"Item",
                        "ItemType":itemType,
                    })
            newTasks.append(task)

        # prepare the task for returning from the roommanager
        newTasks.append(
            {
                "task":"return from room manager",
                "command":self.commands["return from room manager"]
            })

        # prepare the task for gooing to the roommanager
        newTasks.append(
            {
                "task":"insert job order",
                "command":"scj",
            })
        newTasks.append(
            {
                "task":"register result",
                "command":None,
            })

        # add prepared tasks to job order
        jobOrder.tasks = list(reversed(newTasks))

        # run job order
        character.addMessage("running job order local room relay")
        character.jobOrders.append(jobOrder)
        character.runCommandString("Jj.j")

    def gatherApplyActions(self,character=None):
            """
            returns a list of actions that should be run when using this item
            this is intended to be overwritten to add actions

            Parameters:
                character: the character using the item
            Returns:
                a list of function calls to run
            """

        result = []

        # add spawning menus if applicable
        if self.applyOptions:
           result.append(self.__spawnApplyMenu) 

        return result

    def __spawnApplyMenu(self,character):
            """
            spawns a selection menu and registers a callback for when the selection is ready
            this is intended to by used by setting self.applyOptions

            Parameters:
                character: the character getting the menu
            """

        options = []
        for option in self.applyOptions:
            options.append(option)
        self.submenue = src.interaction.SelectionMenu("what do you want to do?",options)
        character.macroState["submenue"] = self.submenue
        character.macroState["submenue"].followUp = {"method":"handleApplyMenu","container":self,"params":{"character":character}}

    def handleApplyMenu(self,params):
            """
            calls a function depending on user selection
            
            Parameters:
                params: context for the selection
            """
        character = params["character"]

        selection = character.macroState["submenue"].selection

        if not selection:
            return

        # call the function set for the selection
        self.applyMap[selection](character)

    def getTerrain(self):
            """
            gets the terrain the item is placed on directly or indirectly

            Return:
                the terrain
            """
        if self.room:
            terrain = self.room.terrain
        if self.terrain:
            terrain = self.terrain
        return terrain

    def apply(self,character):
            """
            handles usage by a character
            
            Parameters:
                character: the character using the item
            """

        # gather actions
        actions = self.gatherApplyActions(character)

        # run actions
        if actions:
            for action in actions:
                action(character)
        else:
            character.addMessage("i can not do anything useful with this")

    def __vanillaPickUp(self,character):
            """
            basic behaviour for getting picked up

            Parameters:
                character: the character using the item
            """

        # prevent crashes
        if self.xPosition == None or self.yPosition == None:
            return

        # apply restrictions
        if self.bolted and not character.godMode:
            character.addMessage("you cannot pick up bolted items")
            return

        # do the pick up
        character.addMessage("you pick up a %s"%(self.type))
        self.container.removeItem(self)
        character.addItemToInventory(self)

    def gatherPickupActions(self,character=None):
            """
            returns a list of actions that should be run when picking up this item
            this is intended to be overwritten to add actions

            Parameters:
                character: the character picking up the item
            Returns:
                a list of functions
            """
        return [self.__vanillaPickUp]

    def pickUp(self,character):
            """
            handles getting picked up by a character
            
            Parameters:
                character: the character picking up the item
            """

        # gather the actions
        actions = self.gatherPickupActions()

        # run the actions
        if actions:
            for action in actions:
                action(character)
        else:
            character.addMessage("no pickup action found")

    def getLongInfo(self):
            """
            returns a long text description to show to the player
            
            Returns:
                string: the description text
            """

        text = "item: "+self.type+" \n\n"
        if hasattr(self,"descriptionText"):
            text += "description: \n"+self.description+"\n\n"
        if self.commands:
            text += "commands: \n"
            for (key,value,) in self.commands.items():
                text += "%s: %s\n"%(key,value,)
            text += "\n"
        return text

    def render(self):
            """
            returns the rendered item
            
            Returns:
                the display information
            """
        return self.display

    def getDetailedInfo(self):
            """
            returns a short text description to show to the player

            Returns:
                str: the description text
            """
        return self.description

    def fetchSpecialRegisterInformation(self):
            """
            returns some of the objects state to be stored ingame in a characters registers
            this is intended to be overwritten to add more information

            Returns:
                a dictionary containing the information
            """
        result = {}
        if hasattr(self,"type"):
            result["type"] = self.type
        if hasattr(self,"charges"):
            result["charges"] = self.charges
        if hasattr(self,"uses"):
            result["uses"] = self.uses
        if hasattr(self,"level"):
            result["level"] = self.level
        if hasattr(self,"coolDown"):
            result["coolDown"] = self.coolDown
            result["coolDownRemaining"] = self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer)
        if hasattr(self,"amount"):
            result["amount"] = self.amount
        if hasattr(self,"walkable"):
            result["walkable"] = self.walkable
        if hasattr(self,"bolted"):
            result["bolted"] = self.bolted
        if hasattr(self,"blocked"):
            result["blocked"] = self.blocked
        return result

    def getConfigurationOptions(self,character):
            """
            returns a list of configuration options for the item
            this is intended to be overwritten to add more options

            Returns:
                a dictionary containing function calls with description
            """
        options = {}
        if self.runsCommands:
            options["c"] = ("commands",None)#self.setCommands)
        if self.hasSettings:
            options["s"] = ("machine settings",None)#self.setMachineSettings)
        if self.runsJobOrders:
            options["j"] = ("run job order",self.runJobOrder)
        if self.canReset:
            options["r"] = ("reset",self.reset)
        if self.hasMaintenance:
            options["m"] = ("do maintenance",self.doMaintenance)
        return options

    def reset(self,character):
            """
            dummy for handling a character trying to reset the machine

            Parameters:
                character: the character triggering the reset request
            """
        character.addMessage("nothing to reset")

    def doMaintenance(self,character):
            """
            dummy for handling a character trying to do maintenance

            Parameters:
                character: the character triggering the maintenance offer
            """
        character.addMessage("no maintenance action set")

    def configure(self,character):
            """
            handle a character trying to configure this item by spawning a submenu

            Parameters:
                character: the character configuring this item
            """

        # store last action for debug purposes
        self.lastAction = "configure"

        # fetch the option
        options = self.getConfigurationOptions(character)

        # reformat options for menu
        text = ""
        if not options:
            text += "this machine cannot be configured, press any key to continue"
        else:
            for (key,value) in options.items():
                text += "%s: %s\n"%(key,value[0])
            
        # spawn menu
        self.submenue = src.interaction.OneKeystrokeMenu(text)
        character.macroState["submenue"] = self.submenue

        # register callback
        character.macroState["submenue"].followUp = {"container":self,"method":"configureSwitch","params":{"character":character}}

    def configureSwitch(self,params):
            """
            handle the selection of a configuration option by a character
            Parameters:
                params: context for the selection
            """

        # save last action for debug
        self.lastAction = "configureSwitch"

        # fetch configuration options
        character = params["character"]
        options = self.getConfigurationOptions(character)
        
        # call selected function
        if self.submenue.keyPressed in options:
            option = options[self.submenue.keyPressed][1](character)
        else:
            character.addMessage("no configure action found for this key")

    def addTriggerToTriggerMap(self,result,name,function):
            """
            helper function to handle annoying data structure.

            Parameters:
                result: a dict of lists containing callbacks that should be extended
                name: the name or key the callback should trigger on
                function: the callback
            """
        triggerList = result.get(name)
        if not triggerList:
           triggerList = []
           result[name] = triggerList
        triggerList.append(function)

    def getJobOrderTriggers(self):
            """
            returns a dict of lists containing callbacks to be triggered by a job order
            Returns:
                a dict of lists 
            """
        result = {}
        self.addTriggerToTriggerMap(result,"configure machine",self.jobOrderConfigure)
        self.addTriggerToTriggerMap(result,"register result",self.doRegisterResult)
        return result

    def doRegisterResult(self,task,context):
            """
            dummy callback for registering success or failure of a job order
            Parameters:
                task: the task details
                context: the context of the task
            """
        pass

    def jobOrderConfigure(self,task,context):
            """
            callback for configuring the item throug a job order
            Parameters:
                task: the task details
                context: the context of the task
            """

        # configure commands
        for (commandName,command) in task["commands"].items():
            self.commands[commandName] = command

    def runJobOrder(self,character):
            """
            handle a job order run on this item
            Parameters:
                character: the character running the job order on the item
            """

        # save last action for debug
        self.lastAction = "runJobOrder"

        if not character.jobOrders:
            character.addMessage("no job order")
            return

        # get task
        jobOrder = character.jobOrders[-1]
        task = jobOrder.popTask()

        if not task:
            character.addMessage("no tasks left")
            return

        # select callback to trigger
        triggerMap = self.getJobOrderTriggers()
        triggers = triggerMap.get(task["task"])
        if not triggers:
            character.addMessage("unknown trigger: %s %s"%(self,task,))
            return

        # trigger callbacks
        for trigger in triggers:
            trigger(task,{"character":character,"jobOrder":jobOrder})

    def runCommand(self,commandName,character):
            """
            runs a preconfigured command on a character
            Parameters:
                commandName: the kind/name of command to run
                character: the character to run the command on
            """

        # select the command from the list of preconfigured commands
        command = self.commands.get(commandName)
        if not command:
            return

        # run the selected command on the character
        character.runCommandString(command)
        character.addMessage("running command for trigger: %s - %s"%(commandName,command))

'''
the base class for all items.
'''
class Item(src.saveing.Saveable):
    '''
    state initialization and id generation
    '''
    def __init__(self,display=None,xPosition=0,yPosition=0,zPosition=0,creator=None,name="item",seed=0,noId=False):
        super().__init__()

        self.seed = seed

        # set attributes
        if not hasattr(self,"type"):
            self.type = "Item"
        if not display:
            self.display = src.canvas.displayChars.notImplentedYet
        else:
            try:
                self.display = display
            except:
                pass
        self.xPosition = xPosition
        self.yPosition = yPosition
        self.zPosition = zPosition
        self.room = None
        self.terrain = None
        self.listeners = {"default":[]}
        self.walkable = False
        self.lastMovementToken = None
        self.chainedTo = []
        self.name = name
        self.description = "a "+self.name
        self.mayContainMice = False
        self.bolted = not self.walkable
        self.container = None

        self.customDescription = None

        # set up metadata for saving
        self.attributesToStore.extend([
               "mayContainMice","name","type","walkable","xPosition","yPosition","zPosition","bolted"])

        # set id
        if not noId:
            import uuid
            self.id = uuid.uuid4().hex
        else:
            self.id = None
        self.id = json.dumps(self.id, sort_keys=True).replace("\\","")

    def render(self):
        return self.display

    def upgrade(self):
        self.level += 1

    def downgrade(self):
        self.level += 1

    '''
    generate a text with a detailed description of the items state
    bad code: casting a dict to string is not really enough
    '''
    def getDetailedInfo(self):
        return str(self.getDetailedState())

    '''
    get a short description
    bad code: name and function say different things
    '''
    def getDetailedState(self):
        return self.description

    '''
    no operation when applying a base item
    '''
    def apply(self,character,silent=False):
        character.changed("activate",self)
        self.changed("activated",character)
        if not silent:
            character.addMessage("i can not do anything useful with this")

    '''
    get picked up by the supplied character
    '''
    def pickUp(self,character):
        if self.xPosition == None or self.yPosition == None:
            return

        # apply restrictions
        if self.bolted and not character.godMode:
            character.addMessage("you cannot pick up bolted items")
            return

        character.addMessage("you pick up a %s"%(self.type))
        """
        foundBig = False
        for item in character.inventory:
            if item.walkable == False:
                foundBig = True
                break

        if foundBig and self.walkable == False:
            character.addMessage("you cannot carry more big items")
            return

        character.addMessage("you pick up a "+self.type)
        """

        # bad code: should be a simple self.container.removeItem(self)
        if self.room:
            # remove item from room
            self.container = self.room
            self.container.removeItem(self)
        else:
            # remove item from terrain
            # bad code: should be handled by the terrain
            self.container = self.terrain
            self.container.removeItem(self)

        # remove position information to place item in the void
        self.xPosition = None
        self.yPosition = None

        # add item to characters inventory
        character.inventory.append(self)
        self.changed()

    def fetchSpecialRegisterInformation(self):
        result = {}
        if hasattr(self,"type"):
            result["type"] = self.type
        if hasattr(self,"charges"):
            result["charges"] = self.charges
        if hasattr(self,"uses"):
            result["uses"] = self.uses
        if hasattr(self,"level"):
            result["level"] = self.level
        if hasattr(self,"coolDown"):
            result["coolDown"] = self.coolDown
            result["coolDownRemaining"] = self.coolDown-(src.gamestate.gamestate.tick-self.coolDownTimer)
        if hasattr(self,"amount"):
            result["amount"] = self.amount
        if hasattr(self,"walkable"):
            result["walkable"] = self.walkable
        if hasattr(self,"bolted"):
            result["bolted"] = self.bolted
        if hasattr(self,"blocked"):
            result["blocked"] = self.blocked
        return result

    '''
    registering for notifications
    bad code: should be extra class
    '''
    def addListener(self,listenFunction,tag="default"):
        # create bucket if it does not exist yet
        if not tag in self.listeners:
            self.listeners[tag] = []

        if not listenFunction in self.listeners[tag]:
            self.listeners[tag].append(listenFunction)

    '''
    deregistering for notifications
    bad code: should be extra class
    '''
    def delListener(self,listenFunction,tag="default"):
        # remove listener
        if listenFunction in self.listeners[tag]:
            self.listeners[tag].remove(listenFunction)

        # clean up empty buckets
        # bad performance: probably better to not clear and recreate buckets
        if not self.listeners[tag] and not tag == "default":
            del self.listeners[tag]

    '''
    sending notifications
    bad code: probably misnamed
    bad code: should be extra class
    '''
    def changed(self,tag="default",info=None):
        if not tag in self.listeners:
            return

        for listenFunction in self.listeners[tag]:
            if info == None:
                listenFunction()
            else:
                listenFunction(info)

    '''
    get a list of items that is affected if the item would move into some direction
    '''
    def getAffectedByMovementDirection(self,direction,force=1,movementBlock=set()):
        # add self
        movementBlock.add(self)
        
        # add things chained to the item
        for thing in self.chainedTo:
            if thing not in movementBlock and not thing == self:
                movementBlock.add(thing)
                thing.getAffectedByMovementDirection(direction,force=force,movementBlock=movementBlock)

        return movementBlock

    '''
    move the item
    '''
    def moveDirection(self,direction,force=1,initialMovement=True):
        if self.walkable:
            # destroy small items instead of moving it
            self.destroy()
        else:
            oldPosition = (self.xPosition,self.yPosition)
            if direction == "north":
                newPosition = (self.xPosition,self.yPosition-1)
            elif direction == "south":
                newPosition = (self.xPosition,self.yPosition+1)
            elif direction == "west":
                newPosition = (self.xPosition-1,self.yPosition)
            elif direction == "east":
                newPosition = (self.xPosition+1,self.yPosition)

            # remove self from current position
            if self in self.terrain.itemByCoordinates[oldPosition]:
                self.terrain.itemByCoordinates[oldPosition].remove(self)
            if len(self.terrain.itemByCoordinates) == 0:
                del self.terrain.itemByCoordinates[oldPosition]

            # destroy everything on target position
            if newPosition in self.terrain.itemByCoordinates:
                for item in self.terrain.itemByCoordinates[newPosition]:
                    item.destroy()

            # place self on new position
            self.xPosition = newPosition[0]
            self.yPosition = newPosition[1]
            if newPosition in self.terrain.itemByCoordinates:
                self.terrain.itemByCoordinates[newPosition].append(self)
            else:
                self.terrain.itemByCoordinates[newPosition] = [self]

            # destroy yourself if anything is left on target position
            # bad code: this cannot happen since everything on the target position was destroyed already
            if len(self.terrain.itemByCoordinates[(self.xPosition,self.yPosition)]) > 1:
                self.destroy()

    '''
    get the physical resistance to beeing moved
    '''
    def getResistance(self):
        if (self.walkable):
            return 1
        else:
            return 50

    '''
    do nothing
    '''
    def recalculate(self):
        pass

    '''
    destroy the item and leave scrap
    bad code: only works on terrain
    '''
    def destroy(self,generateSrcap=True):

        if not hasattr(self,"terrain"):
            self.terrain = None
        if self.room:
            container = self.room
        elif self.terrain:
            container = self.terrain
        else:
            return

        pos = (self.xPosition,self.yPosition) 

        if pos == (None,None):
            return

        # remove item from terrain
        container.removeItem(self)

        # generatate scrap
        if generateSrcap:
            newItem = src.items.itemMap["Scrap"](pos[0],pos[1],1,creator=self)
            newItem.room = self.room
            newItem.terrain = self.terrain

            if pos in container.itemByCoordinates:
                for item in container.itemByCoordinates[pos]:
                    container.removeItem(item)
                    if not item.type == "Scrap":
                        newItem.amount += 1
                    else:
                        newItem.amount += item.amount
            newItem.setWalkable()

            # place scrap
            container.addItems([newItem])

        self.xPosition = None
        self.yPosition = None
            
    def getState(self):
        state = super().getState()
        state["id"] = self.id
        state["type"] = self.type
        state["xPosition"] = self.xPosition
        state["yPosition"] = self.yPosition
        return state

    def getLongInfo(self):
        return None

    def configure(self,character):
        character.addMessage("nothing to configure")

commons = [
            "MarkerBean",
            "MetalBars",
            "Connector",
            "Bolt",
            "Stripe",
            "puller",
            "pusher",
            "Puller",
            "Pusher",
            "Stripe",
            "Rod",
            "Case",
            "Heater",
            "Mount",
            "Tank",
            "Frame",
            "Radiator",
            "Sheet",
            "GooFlask",
            "Vial",
            "Wall",
            "Door",
            "MarkerBean",
            "MemoryCell",
            "Paving",
            "GooFlask",
            "Vial",
            "ScrapCompactor",
            "PavingGenerator",
            "Machine",
            "Sheet",
        ]

semiCommons = [
        "UniformStockpileManager",
        "TypedStockpileManager",
        "GrowthTank",
        "GooDispenser",
        "MaggotFermenter",
        "BioPress",
        "GooProducer",
        "ItemUpgrader",
        "Scraper",
        "Sorter",
        "StasisTank",
        "BluePrinter",
        "BloomShredder",
        "SporeExtractor",
        "BloomContainer",
        "Container",
        "SanitaryStation",
        "AutoScribe",
        "ItemCollector",
        "HealingStation",
        ]

rare = [
        "MachineMachine",
        "ProductionArtwork",
        ]

def addType(toRegister):
    itemMap[toRegister.type] = toRegister

# maping from strings to all items
# should be extendable
itemMap = {
        "Item":Item,
        "ItemNew":ItemNew,
}

rawMaterialLookup = {
    "WaterCondenser":["Sheet","Case"],
    "Sheet":["MetalBars"],
    "Radiator":["MetalBars"],
    "Mount":["MetalBars"],
    "Stripe":["MetalBars"],
    "Bolt":["MetalBars"],
    "Rod":["MetalBars"],
    "Tank":["Sheet"],
    "Heater":["Radiator"],
    "Connector":["Mount"],
    "pusher":["Stripe"],
    "puller":["Bolt"],
    "Frame":["Rod"],
    "Case":["Frame"],
    "PocketFrame":["Frame"],
    "MemoryCell":["Connector"],
    "AutoScribe":["Case","MetalBars","MemoryCell","pusher","puller"],
    "FloorPlate":["Sheet","MetalBars"],
    "Scraper":["Case","MetalBars"],
    "GrowthTank":["Case","MetalBars"],
    "Door":["Case","MetalBars"],
    "Wall":["Case","MetalBars"],
    "Boiler":["Case","MetalBars"],
    "Drill":["Case","MetalBars"],
    "Furnace":["Case","MetalBars"],
    "ScrapCompactor":["MetalBars"],
    "GooFlask":["Tank"],
    "GooDispenser":["Case","MetalBars","Heater"],
    "MaggotFermenter":["Case","MetalBars","Heater"],
    "BloomShredder":["Case","MetalBars","Heater"],
    "SporeExtractor":["Case","MetalBars","puller"],
    "BioPress":["Case","MetalBars","Heater"],
    "GooProducer":["Case","MetalBars","Heater"],
    "CorpseShredder":["Case","MetalBars","Heater"],
    "MemoryDump":["Case","MemoryCell"],
    "MemoryStack":["Case","MemoryCell"],
    "MemoryReset":["Case","MemoryCell"],
    "MemoryBank":["Case","MemoryCell"],
    "SimpleRunner":["Case","MemoryCell"],
    "MarkerBean":["PocketFrame"],
    "PositioningDevice":["PocketFrame"],
    "Watch":["PocketFrame"],
    "BackTracker":["PocketFrame"],
    "Tumbler":["PocketFrame"],
    "RoomControls":["Case","pusher","puller"],
    "StasisTank":["Case","pusher","puller"],
    "ItemUpgrader":["Case","pusher","puller"],
    "ItemDowngrader":["Case","pusher","puller"],
    "RoomBuilder":["Case","pusher","puller"],
    "BluePrinter":["Case","pusher","puller"],
    "Container":["Case","Sheet"],
    "BloomContainer":["Case","Sheet"],
    "Mover":["Case","pusher","puller"],
    "Sorter":["Case","pusher","puller"],
    "FireCrystals":["Coal","SickBloom"],
    "Bomb":["Frame","Explosive"],
    "ProductionManager":["Case","MemoryCell","Connector"],
    "AutoFarmer":["FloorPlate","MemoryCell","Connector"],
    "UniformStockpileManager":["Case","MemoryCell","Connector"],
    "TypedStockpileManager":["Case","MemoryCell","Connector"],
}

'''
get item instances from dict state
'''
def getItemFromState(state):
    item = itemMap[state["type"]](noId=True)
    item.setState(state)
    if "id" in state:
        item.id = state["id"]
    src.saveing.loadingRegistry.register(item)
    return item

