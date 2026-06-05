from typing import List

import pygame


class GameObject:
    def __init__(self):
        self.events:List[pygame.event.Event] = []

        self.position: pygame.Vector2 = pygame.Vector2(0,0)
        self.center: pygame.Vector2 = pygame.Vector2(0,0)
        self.size: pygame.Vector2 = pygame.Vector2(0,0)

        self.texture:pygame.Surface = None
        self.rect:pygame.Rect = None
        self.collide:bool = False

    def getEvent(self,event):
        self.events.append(event)

    def clearEvent(self):
        self.events = []

    def update(self,dt:float):
        pass

    #默认的设置坐标方法
    def setPosition(self,pos:pygame.Vector2):
        self.position = pos
        self.center = pygame.Vector2(pos.x+self.size.x/2,
                                     pos.y+self.size.y/2)

    #默认的设置中心方法
    def setCenter(self,center:pygame.Vector2):
        self.center = center
        self.position = pygame.Vector2(center.x-self.size.x/2,
                                       center.y-self.size.y/2)

    def loadTexture(self,path:str):
        self.texture = pygame.image.load(path)
        self.rect = self.texture.get_rect()
        self.size = pygame.Vector2(self.texture.get_size()[0], self.texture.get_size()[1])