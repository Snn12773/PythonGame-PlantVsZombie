import random
from collections import defaultdict
from typing import List

import pygame
from pygame import Vector2
from pygame.examples import grid

from src.core.game.UI.UI import UIImage
from src.core.game.entity.Collect import Sun
from src.core.game.entity.Entity import Entity
from src.core.game.entity.Plant import Plant
from src.core.game.entity.Projectile import Projectile
from src.core.game.entity.Zombie import Zombie
from src.core.game.scene.Grid import Grid


class EntityManager:
    def __init__(self):
        #场景
        self.scene = None
        #所有实体
        self.entities: dict[str,List[Entity]] = {"zombie":[],
                                                 "plant":[],
                                                 "projectile":[],
                                                 "armor":[],
                                                 "other_up":[],
                                                 "ohter_down":[]}
        #所有行
        self.by_line: dict[str,List[List[Entity]]] = {"zombie":[],
                                                       "plant":[],
                                                       "projectile":[],
                                                       "armor":[]}
        #
        self.by_col: dict[str,List[List[Entity]]] = {"zombie":[],
                                                       "plant":[],
                                                       "projectile":[],
                                                       "armor":[]}

        self.destroy_list: dict[str,List[Entity]] ={"zombie":[],
                                                    "plant":[],
                                                    "projectile":[],
                                                    "armor":[],
                                                    "other_up":[],
                                                    "ohter_down":[]}

    def initEntityList(self,line:int,col:int):
        for entity_type in self.by_line:
            for i in range(line):
                self.by_line[entity_type].append([])
        for entity_type in self.by_col:
            for i in range(col):
                self.by_col[entity_type].append([])

    def creatPlant(self,data,grid:Grid):
        plant = Plant(data,self.scene)
        plant.setCenter(grid.center.copy())
        plant.setGridPosition(grid.row,grid.col)
        grid.setPlant(plant)
        self.addToEntity("plant",plant,grid.row,grid.col)

    def createZombie(self,data,line:int,col:int=-1):
        zombie = Zombie(data,self.scene)
        zombie.setCenter(self.scene.getGridLineCenter(line).copy())
        zombie.line = line

        self.addToEntity("zombie",zombie,line,col)


    def createSun(self,amount:int,position:Vector2,is_throw=False):
        sun = Sun(amount)
        sun.line = -1
        sun.col = -1
        rand_height = random.randrange(10 - int(sun.size.y/2),30)
        sun.height += rand_height
        sun.setCenter(Vector2(position.x,
                              position.y - rand_height))
        velocity = Vector2(0,-1)
        if is_throw:
            velocity = Vector2(random.uniform(-1,1),
                               random.uniform(1,2))
        else:
            sun.height = 600 - position.y
        sun.setThrow(is_throw,velocity)
        self.addToEntity("other_up",sun,-1,-1)


    def createProjectile(self,source:Entity,data,position:pygame.Vector2,grid:Grid):
        p = Projectile(data)
        p.source = source
        p.setCenter(position)
        p.row = grid.row
        p.col = grid.col
        p.line = grid.row
        p.scene = self.scene
        self.addToEntity("projectile",p,grid.row,grid.col)

    def addToEntity(self,entity_type,entity,line:int,col:int):
        if line == -1:
            self.scene.main_camera.bind(entity,entity_type,0)
        else:
            self.scene.main_camera.bind(entity,entity_type,line)
        if entity.has_shadow:
            self.scene.main_camera.bind(entity.shadow,"shadow",line)

        self.entities[entity_type].append(entity)

        if not line == -1:
            self.by_line[entity_type][line].append(entity)
        if not col == -1:
            self.by_col[entity_type][col].append(entity)

    def update(self,dt:float):
        self.destroy_list = {"zombie":[],
                             "plant":[],
                             "projectile":[],
                             "armor":[],
                             "other_up":[],
                             "ohter_down":[]}


        for entity_type in self.entities:
            for entity in self.entities[entity_type]:
                entity.update(dt)

        for entity_type in self.entities:
            for entity in self.entities[entity_type]:
                if entity.mark_destroy:
                    self.destroy_list[entity_type].append(entity)

        #处理标记销毁的实体
        for entity_type in self.destroy_list:
            for entity in self.destroy_list[entity_type]:
                self.removeFromLine(entity_type,entity,entity.line)
                self.removeFromCol(entity_type,entity,entity.col)
                self.removeFromEntity(entity_type,entity)
                if entity.line == -1:
                    self.scene.main_camera.unbind(entity, entity_type,0)
                else:
                    self.scene.main_camera.unbind(entity, entity_type, entity.line)

                del entity


    def removeFromLine(self,entity_type,entity,line:int):
        if entity_type not in self.by_line:
            return
        if entity in self.by_line[entity_type][line]:
            self.by_line[entity_type][line].remove(entity)


    def removeFromCol(self,entity_type,entity,col:int):
        if entity_type not in self.by_col:
            return
        if entity in self.by_col[entity_type][col]:
            self.by_col[entity_type][col].remove(entity)

    def removeFromEntity(self,entity_type,entity):
        if entity in self.entities[entity_type]:
            self.entities[entity_type].remove(entity)
            if entity.has_shadow:
                self.scene.main_camera.unbind(entity.shadow,"shadow",entity.line)

            del entity

    def getZombies(self,line:int):
        if line <0 or line > len(self.by_line["zombie"])-1:
            return []
        else:
            return self.by_line["zombie"][line]

    def getPlant(self,line:int):
        if line <0 or line > len(self.by_line["projectile"])-1:
            return []
        else:
            return self.by_line["plant"][line]


class GridManager:
    def __init__(self):
        #场景
        self.scene = None

        self.grids:List[List[Grid]] = []
        self.size:tuple = ()
        self.gird_size:pygame.Vector2 = pygame.Vector2(64,64)

        self.start:pygame.Vector2 = pygame.Vector2((0,0))
        self.end:pygame.Vector2 = pygame.Vector2((0,0))

    def create(self,data,start:pygame.Vector2,end:pygame.Vector2):
        self.start = start
        self.end = end

        self.size = (data.get("size")[0],data.get("size")[1])
        scale_x = (end.x - start.x) / self.size[1]
        scale_y = (end.y - start.y) / self.size[0]
        grid_size = pygame.Vector2(scale_x, scale_y)
        self.gird_size = grid_size
        if data.get("type") == "full":
            for row in range(self.size[0]):
                l = []
                for col in range(self.size[1]):
                    grid = Grid().create(data.get("fill"),
                                            row,
                                            col,
                                            pygame.Vector2(start.x + col*scale_x,
                                                           start.y + row*scale_y),
                                            grid_size)
                    self.scene.main_camera.bind(grid,"background",1)
                    l.append(grid)
                self.grids.append(l)

        elif data.get("type") == "full_line":
            for row in range(self.size[0]):
                l = []
                if data.get("fill")[int(row)] == "dirt":
                    self.grids.append(l)
                    continue
                for col in range(self.size[1]):
                    grid = Grid().create(data.get("fill")[int(row)],
                                                         row,
                                                         col,
                                                         pygame.Vector2(start.x + col*scale_x,
                                                                        start.y + row*scale_y),
                                                         grid_size)
                    self.scene.main_camera.bind(grid, "background",1)
                    l.append(grid)
                self.grids.append(l)

        return self

    #快速定位(但是我其实信不过这个)
    #-1就是不在地图范围内的意思
    def getGridPosition(self,pos:pygame.Vector2)->pygame.Vector2:
        col = int((pos.x - self.start.x)/self.gird_size.x)
        row = int((pos.y - self.start.y)/self.gird_size.y)
        if col < 0 or col > self.size[1]:
            col = -1
        if row < 0 or row > self.size[0]:
            row = -1
        return pygame.Vector2(row,col)

    #检测碰撞总是没错的……
    #目前只会在放置植物的时候使用
    #性能影响不大？
    def positonInGrid(self,pos:pygame.Vector2)->Grid:
        for line in self.grids:
            for grid in line:
                if grid.rect.collidepoint(pos):
                    return grid
        return None

    def getGridLineCenter(self,line:int)->pygame.Vector2:
        return Vector2(800,self.grids[line][0].center.y)

    def update(self,dt:float):
        for line in self.grids:
            for g in line:
                g.update(dt)

class MouseManager:
    def __init__(self):
        self.scene = None
        self.position:Vector2 = Vector2(0,0)
        self.prev_position:Vector2 = Vector2(0,0)

        self.picking = False
        self.preview:pygame.Surface = None

    def update(self,dt:float):
        mouse = pygame.mouse.get_pos()
        self.position = Vector2(mouse[0],mouse[1])

        if self.picking:
            self.prev_position = Vector2(self.position.x - self.preview.get_size()[0]/2,
                                            self.position.y - self.preview.get_size()[1]/2)

    def drawPreview(self,screen:pygame.Surface) -> tuple[pygame.Surface,pygame.Vector2]:
        if self.picking:
            return (self.preview,self.prev_position)
        else:
            return None


    def onSelect(self,preview:pygame.Surface):
        self.preview = preview
        self.preview.set_alpha(125)
        self.prev_position = Vector2(self.position.x - self.preview.get_size()[0]/2,
                                            self.position.y - self.preview.get_size()[1]/2)
        self.picking = True

    def onDeselect(self):
        self.preview = None
        self.picking = False
