import pygame

from src.core.data.GameEvent import *
from src.core.game.entity.Entity import Creature
from src.core.game.entity.Projectile import Projectile
from src.core.tool.Timer import Timer
from src.res.JsonLoader import loadJson


#植物技能
class Ability:
    def __init__(self, data):
        self.data = data
        self.type = data["type"]
        #挂载植物
        self.plant = None
        #挂载场景
        self.scene = None

        self.projectile_data = None

        self.cd = 0
        self.timer = Timer()
        self.is_cd = False


    def load(self,scene,plant):
        self.scene = scene
        self.plant = plant

        if "cd" in self.data:
            self.cd = self.data["cd"]
            self.is_cd = False
            self.timer.setTime(self.cd)
            self.timer.start()

        if self.type == "projectile":
            d = loadJson("data/entity/projectile.json")
            self.projectile_data = d[self.data["item"]]
            self.projectile = Projectile(self.projectile_data)


    def canActivate(self):
        temp = True
        if self.cd > 0 and not self.is_cd:
            temp = False

        return temp

    def onActivate(self):
        if self.type == "projectile":
            pygame.event.post(pygame.event.Event(SPAWN_PROJECTILE,{"source":self.plant,
                                                                   "data":self.projectile_data,
                                                                   "position":self.plant.center.copy(),
                                                                   "grid":self.scene.getGrid(self.plant.center)}))
        if self.type == "sun":
            pygame.event.post(pygame.event.Event(SPAWN_SUN,{"amount":25,
                                                            "position":self.plant.center.copy(),
                                                            "is_throw":True}))

    def update(self,dt: float):
        if self.cd > 0:
            self.is_cd = self.timer.tick(dt)

#触发条件
class Trigger:
    def __init__(self, data):
        self.data = data
        self.type = data["type"]
        #挂载植物
        self.plant = None
        #挂载场景
        self.scene = None
        self.target_line = []
        self.timer = Timer()
        self.time_triggered = False

    def load(self,scene,plant):
        self.scene = scene
        self.plant = plant

        if self.type == "time":
            self.timer.setTime(self.data["time"])
            self.timer.start()

        if self.type == "zombie":
            self.target_line = self.data["target"]



    def update(self,dt:float):
        if self.type == "none":
            return
        if self.type == "time":
           self.time_triggered = self.timer.tick(dt)
        if self.type == "contact":
            pass

    def isTriggered(self)->bool:
        if self.type == "none":
            return True
        if self.type == "zombie":
            for line in self.target_line:
                test = line + self.plant.line
                if test < 0 or test >= self.scene.getMapSize()[0]:
                    return False
                if self.scene.anyZombieOnline(test):
                    return True
        return False

#植物
class Plant(Creature):
    def __init__(self,data,scene):
        super().__init__()

        self.animate.setAniamte(data["animate"][0])
        self.texture = self.animate.getTexture()
        self.rect = self.texture.get_rect()
        self.size = pygame.Vector2(self.texture.get_size()[0],self.texture.get_size()[1])

        self.trigger: Trigger
        self.ability: Ability
        if "trigger" in data:
            self.trigger = Trigger(data["trigger"])
        else:
            self.trigger = Trigger({"type":"none"})
        if "ability" in data:
            self.ability = Ability(data["ability"])
        else:
            self.ability = Ability({"type":"none"})

        self.scene = scene
        self.setScene(scene)
        self.trigger.load(self.scene,self)
        self.ability.load(self.scene,self)

        self.row = 0
        self.col = 0

        if data["hp"] == "inf":
            self.hp = -1
        else:
            self.hp:int = int(data["hp"])

        self.animate.play()

    def entityUpdate(self,dt:float)->None:
        self.trigger.update(dt)
        self.ability.update(dt)
        if self.trigger.isTriggered() and self.ability.canActivate():
            self.ability.onActivate()

    def setGridPosition(self,row:int,col:int)->None:
        self.row = row
        self.col = col
        self.line = row

    #设置场景
    #创建时挂载场景
    def setScene(self,scene):
        self.scene = scene
        self.trigger.scene = scene
        self.ability.scene = scene

    def damage(self,damage_info)->None:
        self.on_damage = True
        if self.hp == -1:
            damage_info["amount"] = 0

        self.hp -= damage_info["amount"]

        if self.hp <= 0:
            self.destroy()

class Preview(Plant):
    def __init__(self,data):
        super().__init__(data)
        self.texture = data["texture"]