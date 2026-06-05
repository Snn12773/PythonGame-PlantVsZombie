import pygame
from pygame import Vector2

from src.core.data.GameEvent import DAMAGE_EVENT
from src.core.game.entity.Entity import Creature, Armor
from src.core.tool.Timer import Timer
from src.res.JsonLoader import loadJson


class Ability:
    def __init__(self,entity):
        self.entity = entity


class Zombie(Creature):
    def __init__(self,data,scene):
        super().__init__()

        self.data = data
        self.animates = self.data["animate"]
        self.scene = scene

        self.attack_interval = 1
        self.attack_timer = Timer()
        self.attack_timer.setTime(self.attack_interval)
        self.attack_timer.start()

        self.animate.setAniamte(self.animates[0])
        self.animate.setFrameRate(2)
        self.texture = self.animate.getTexture()
        self.rect = self.texture.get_rect()
        self.size = pygame.Vector2(self.texture.get_size()[0],self.texture.get_size()[1])
        self.shadow.scale(pygame.Vector2(self.size.x,self.shadow.size.y))
        self.animate.play()

        self.attacking = False
        self.attack_target = None
        self.moving = True
        self.speed = data["speed"]
        self.hp = data["hp"]
        self.max_hp = data["hp"]

        self.armor = Armor(data["armor"])

    def setPosition(self,pos:pygame.Vector2):
        self.position = pos
        self.center = Vector2(self.position.x + self.size.x/2,
                              self.position.y + self.size.y)
        self.rect.x =int(pos.x)
        self.rect.y =int(pos.y)

    def setCenter(self,pos:pygame.Vector2):
        self.center = pos
        self.position = Vector2(pos.x - self.size.x/2,
                                pos.y - self.size.y)
        self.rect.x =int(self.position.x)
        self.rect.y =int(self.position.y)

    def damage(self,damage_info):
        if self.armor.damage(damage_info["amount"]):
            return
        else:
            self.on_damage = True
            self.hp -= damage_info["amount"]
            if self.hp <= self.max_hp/2:
                frame = self.animate.getFrame()
                self.animate.play(self.animates[1])
                self.animate.setFrame(frame)
            if self.hp <= 0:
                self.destroy()

    def move(self):
        if self.moving:
            self.setCenter(Vector2(self.center.x - self.speed,
                                   self.center.y))

    def entityUpdate(self,dt:float) ->None:
        if self.moving:
            self.move()

        if self.attacking:
            if self.attack_timer.tick(dt):
                pygame.event.post(pygame.event.Event(DAMAGE_EVENT,{"target":self.attack_target,
                                                                   "damage_info":{"source":self,
                                                                                  "amount":10,
                                                                                  "damage_type":"normal"}}))

        self.attacking = False
        for plant in self.scene.plantOnline(self.line):
            if self.collideWithEntity(plant):
                self.attack_target = plant
                self.attacking = True
        self.moving = not self.attacking
