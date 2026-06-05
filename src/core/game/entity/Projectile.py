import pygame

from pygame import Vector2

from src.core.data.GameEvent import DAMAGE_EVENT
from src.core.game.entity.Entity import Entity


class Projectile(Entity):
    def __init__(self, data):
        super().__init__()
        self.animate.setAniamte(data["animate"])
        self.texture = self.animate.getTexture()
        self.rect = self.texture.get_rect()
        self.size = Vector2(self.texture.get_size()[0], self.texture.get_size()[1])
        self.height = data["height"]

        self.shadow.scale(self.size)

        self.source:Entity = None

        self.damage = data["damage"]
        self.gravity = data["gravity"]
        self.G = 9.8
        if data["move"] == "throw":
            self.throw = True
        else:
            self.throw = False
        self.target = "zombie"

        self.velocity = Vector2(0,0)
        if data["move"] == "forward":
            self.velocity.x = data["speed"]

    #抛射物，由起点、终点、时间计算初速度
    def getOrbit(self,start:Vector2,end:Vector2,time:float)->Vector2:
        velocity = Vector2(0,0)
        velocity.x = (start.x - end.x)/time
        velocity.y = (self.G*time)/2
        return velocity

    #专门的move方法
    def move(self,dt:float):
        if self.gravity:
            self.height = self.height - self.velocity.y
            self.velocity.y -= self.gravity*dt
        if self.height <= 0:
            self.destroy()
        self.setCenter(Vector2(self.center.x + self.velocity.x,
                                self.center.y))
        gird_pos = self.scene.getGridPosition(self.center)

        if self.position.x > 800:
            self.destroy()

    def entityUpdate(self,dt:float) ->None:
        self.move(dt)
        if self.line < 0:
            return
        for zombie in self.scene.zombieOnline(self.line):
            if self.collideWithEntity(zombie):
                pygame.event.post(pygame.event.Event(DAMAGE_EVENT,{"target": zombie,
                                                                   "damage_info":{"source": self,
                                                                    "amount": self.damage,
                                                                    "damage_type": "normal"}}))
                self.destroy()
                break

    def setCenter(self, center: pygame.Vector2):
        self.center = center
        self.position = pygame.Vector2(center.x - self.size.x / 2,
                                       self.center.y - self.size.y / 2 - self.height)
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)

    def setPosition(self, pos: pygame.Vector2):
        self.position = pos
        self.center = pygame.Vector2(pos.x + self.size.x / 2,
                                     pos.y + self.size.y / 2 + self.height)
