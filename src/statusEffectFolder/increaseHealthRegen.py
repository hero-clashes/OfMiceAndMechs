import src


class IncreaseHealthRegen(src.statusEffects.HealthRegenBuff):
    type = "IncreaseHealthRegen"

    def __init__(self, healthBonus=2, duration=500, inventoryItem=None):
        self.healthBonus = healthBonus
        super().__init__(duration=duration, inventoryItem=inventoryItem)

    def modHealthRegen(self, health):
        return health + self.healthBonus

    def getShortCode(self):
        return "regeneration"

src.statusEffects.addType(IncreaseHealthRegen)