import pygame

from src.core.data.GameEvent import *
from src.core.game.EventBus import eventBus
from src.core.game.GameObject import GameObject


class Grid(GameObject):
    def __init__(self):
        super().__init__()

        #在其上的植物
        self.plant = None
        self.plantable = True

        self.collide = True

        self.grass_type = 0

        self.type = ""
        self.col = -1
        self.row = -1

        eventBus.subscribe(self,PLANT,{"grid":self})

    def create(self,type:str,row,col,pos:pygame.Vector2,size:pygame.Vector2):
        self.loadTexture("src/res/texture/grid/Grassland1.png")
        self.type = type
        self.col = col
        self.row = row

        self.setPosition(pos)
        if type == "grassland":
            if (col+row) %2 == 0:
                self.grass_type = 0
                self.loadTexture("src/res/texture/grid/Grassland1.png")
            else:
                self.grass_type = 1
                self.loadTexture("src/res/texture/grid/Grassland2.png")
        else:
            print(type)
        self.scale(size)
        return self

    def setPosition(self,pos:pygame.Vector2):
        super().setPosition(pos)
        self.rect.x = int(pos.x)
        self.rect.y = int(pos.y)


    def scale(self,size:pygame.Vector2):
        self.size = size
        self.texture = pygame.transform.scale(self.texture,size)
        self.rect = self.texture.get_rect()
        self.rect.x = int(self.position.x)
        self.rect.y = int(self.position.y)
        self.center = pygame.Vector2(self.position.x+ self.size.x/2,self.position.y + self.size.y/2)

    def canPlant(self,plant_data):
       return self.plantable

    def setPlant(self,plant):
        self.plant = plant
        self.plantable = False

    def removePlant(self):
        self.plant = None
        self.plantable = True

    def update(self,dt:float):
        for event in self.events:
            if event.type == PLANT:
                self.plantable = False
