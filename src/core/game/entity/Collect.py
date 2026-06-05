import pygame
from pygame import Vector2

from src.core.tool.MoveFunc import lerpPosition

from src.core.data.Animate import Animate


from src.core.data.GameEvent import *
from src.core.game.EventBus import eventBus
from src.core.game.entity.Entity import Entity
from src.core.tool.Timer import Timer


class Collect(Entity):
    def __init__(self):
        super().__init__()

        self.collected = False
        self.target_pos : Vector2 = Vector2(0,0)

        self.gravity = False
        self.is_throw = False
        self.height = 0
        self.velocity = Vector2(0,0)

        self.has_resistance = False
        #阻力（率）-仅x方向
        self.resistance = 1

        self.grounded = False

        self.exist_timer = Timer()
        self.setExistTime(15)

        eventBus.subscribe(self,pygame.MOUSEBUTTONDOWN)

    def onClick(self):
        pass

    def setExistTime(self,time):
        self.exist_timer.setTime(time)
        self.exist_timer.start()

    def setThrow(self,is_throw,velocity:Vector2 = Vector2(0,0)):
        self.is_throw = is_throw
        if is_throw:
            self.gravity = True
            self.velocity = velocity

    def setVelocity(self,velocity:Vector2):
        self.velocity = velocity


    def setPosition(self,position:Vector2):
        self.position = position
        self.center = Vector2(position.x + self.size.x/2,
                              position.y + self.size.y/2 + self.height)
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)

    def setCenter(self,position:Vector2):
        self.center = position
        self.position = Vector2(self.center.x - self.size.x/2,
                                self.center.y - self.size.y/2 - self.height)
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)

    def move(self,dt:float):
        if self.collected:
            self.velocity = lerpPosition(self.position,self.target_pos,12)
            self.setPosition(Vector2(self.position.x + self.velocity.x,
                             self.position.y + self.velocity.y))
            if self.velocity.length() < 0.1:
                self.destroy()
            return

        if self.gravity:
            self. velocity.y -= 3*dt
        if self.has_resistance and abs(self.velocity.x) > 0.1:
            self.velocity.x -= self.velocity.x * self.resistance*dt

        self.setCenter(Vector2(self.center.x + self.velocity.x,
                       self.center.y))
        if not self.grounded:
            self.height += self.velocity.y

        if self.height <= 0:
            self.gravity = False
            self.grounded = True
            self.velocity = Vector2(0,0)

    def entityUpdate(self,dt:float) ->None:
        self.move(dt)
        if self.exist_timer.tick(dt):
            self.destroy()

        if self.collected:
            return

        for event in self.events:
            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1 and self.rect.collidepoint(pygame.mouse.get_pos()):
                    self.onClick()
                    self.collected = True




class Sun(Collect):
    def __init__(self,amount:int):
        super().__init__()
        self.animate.setAniamte("sun")
        self.texture = self.animate.getTexture()
        self.rect = self.texture.get_rect()
        self.size = pygame.Vector2(self.texture.get_size()[0], self.texture.get_size()[1])

        #速度与高度
        self.height = self.size.y/2

        #阻力与阻力率
        self.has_resistance = True

        self.has_shadow = False
        self.animate.play()

        self.amount = amount

    def onClick(self):
        pygame.event.post(pygame.event.Event(SUN_GAIN,{"amount":self.amount}))
