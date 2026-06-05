from typing import List

import pygame
from pygame import Vector2

from src.core.data.Animate import Animate
from src.core.data.GameEvent import *
from src.core.game.EventBus import eventBus
from src.core.game.GameObject import GameObject
from src.core.tool.Timer import Timer
from src.res.JsonLoader import loadJson


class Entity(GameObject):
    def __init__(self):
        super().__init__()
        self.scene = None
        #行/列为-1代表在地图外
        self.line:int = 0
        self.col:int = 0

        self.animate: Animate = Animate()
        self.shadow: Shadow = Shadow()
        self.has_shadow = True

        self.mark_destroy = False

    def update(self,dt:float)->None:
        if self.animate is not None:
            self.animate.update(dt)
            self.texture = self.animate.getTexture()

        self.shadow.setCenter(self.center.copy())

        self.entityUpdate(dt)

    def setLine(self,line:int) -> None:
        self.line = line

    def setCol(self,col:int) -> None:
        self.col = col

    def entityUpdate(self,dt:float)->None:
        pass

    def setPosition(self,pos:pygame.Vector2):
        self.position = pos
        self.rect.x = int(pos.x)
        self.rect.y = int(pos.y)
        self.center = pygame.Vector2(pos.x+self.size.x/2,
                                     pos.y+self.size.y)

    def setCenter(self,center:pygame.Vector2):
        self.center = center
        self.position = pygame.Vector2(center.x-self.size.x/2,
                                       center.y-self.size.y)
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)

    def collideWithEntity(self,entity)->bool:
        if entity.rect is None or self.rect is None:
            return False
        else:
            return self.rect.colliderect(entity.rect)

    def destroy(self)->None:
        self.mark_destroy = True

class Creature(Entity):
    def __init__(self):
        super().__init__()
        self.on_damage = False

        self.damage_timer = Timer()
        self.damage_timer.setTime(0.3)
        self.damage_timer.start()

        #接收目标为自己的伤害事件
        eventBus.subscribe(self,DAMAGE_EVENT,{"target":self})

    def onDamage(self,dt:float)->None:
        if self.on_damage:
            if self.damage_timer.tick(dt):
                self.on_damage = False
                return

            number = int(255 * (1 - self.damage_timer.getTime()/self.damage_timer.time))

            if number < 0:
                number = 0

            self.texture = self.animate.getTexture().copy()
            self.texture.fill((number, number, number), special_flags=pygame.BLEND_RGB_ADD)

    def damage(self, damage_info):
        pass

    def update(self,dt:float)->None:
        if self.animate is not None:
            self.animate.update(dt)
            self.texture = self.animate.getTexture()

        self.shadow.setCenter(self.center.copy())

        for event in self.events:
            if event.type == DAMAGE_EVENT:
                self.damage(event.damage_info)

        self.onDamage(dt)
        self.entityUpdate(dt)

class Shadow(GameObject):
    def __init__(self):
        super().__init__()
        self.loadTexture("src/res/texture/entity/Shadow.png")

    def scale(self,size:Vector2):
        self.texture = pygame.transform.scale(self.texture, (size.x, size.y))
        self.size = Vector2(self.texture.get_size()[0], self.texture.get_size()[1])

class Armor(Entity):
    def __init__(self,armor):
        super().__init__()
        if armor == "none":
            self.data = {}
        else:
            self.data = loadJson("data/entity/armor.json")["armor"]
        self.animate = Animate()
        self.hp = 0
        #是否可以被穿透
        self.through = False
        #是否可用
        self.available = False
        #该防具是否在头上
        self.on_head = True

        if armor == "none":
            pass
        else:
            self.hp = self.data["hp"]
            self.through = self.data["through"]
            self.on_head = self.data["on_head"]

    def breakArmor(self):
        self.available = False
        self.destroy()

    def damage(self,damage_info)->bool:
        if self.available:
            self.hp -= damage_info.amount
            if self.hp <= 0:
                self.breakArmor()
            return True
        else:
            return False
