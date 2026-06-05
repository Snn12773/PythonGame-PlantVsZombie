from collections import defaultdict
from typing import List

import pygame

from src.core.game.GameObject import GameObject
from src.core.game.UI.UI import UI


class Camera(GameObject):
    def __init__(self):
        super().__init__()
        #开启碰撞箱显示的图层
        self.show_hitbox = []
        #开启中心点显示的图层
        self.show_centre = []

        #该摄像机渲染的对象
        #层名称:{层:[对象]}
        self.obj_in_sight:dict[str,List[List[GameObject]]] = defaultdict(list)

        self.obj_in_sight["background"] = []
        self.obj_in_sight["shadow"] = []
        self.obj_in_sight["other_up"] = []
        self.obj_in_sight["other_down"] = []
        self.obj_in_sight["projectile"] = []
        self.obj_in_sight["plant"] = []
        self.obj_in_sight["zombie"] = []
        self.obj_in_sight["armor"] = []

        for obj_type in self.obj_in_sight:
            for i in range(20):
                self.obj_in_sight[obj_type].append([])


        self.origin = pygame.Vector2(0,0)

        self.line = 5

    def draw(self, screen:pygame.Surface)->list[list[tuple[pygame.Surface,pygame.Vector2]]]:
        draw:list[list[tuple[pygame.Surface,pygame.Vector2]]] = []
        #最下层的先渲染
        #背景层
        bg = self.drawAllFromType("background",screen)
        draw.append(bg)
        #影子层
        shadow = self.drawAllFromType("shadow",screen)
        draw.append(shadow)

        down = self.drawAllFromType("other_down",screen)
        draw.append(down)

        #实体需要按行渲染
        for line in range(self.line):
            entity = self.drawByLayers(["projectile","plant","zombie","armor",],line,screen)
            draw.append(entity)

        up = self.drawAllFromType("other_up",screen)
        draw.append(up)
        return draw

    def drawHitBox(self,screen):
        if len(self.show_hitbox) == 0:
            return

        for obj_type in self.show_hitbox:
            for layer in self.obj_in_sight[obj_type]:
                for obj in layer:
                    pygame.draw.rect(screen,"red",obj.rect)

    def drawAllFromType(self,obj_type:str,screen:pygame.Surface)->list[tuple[pygame.Surface,pygame.Vector2]]:
        draw: list[tuple[pygame.Surface,pygame.Vector2]] = []
        for layer in self.obj_in_sight[obj_type]:
            for obj in layer:
                draw.append((obj.texture,obj.position))
        return draw

    def drawByLayers(self,obj_types:List[str],layer:int,screen:pygame.Surface)->list[tuple[pygame.Surface,pygame.Vector2]]:
        draw: list[tuple[pygame.Surface,pygame.Vector2]] = []
        for obj_type in obj_types:
            for obj in self.obj_in_sight[obj_type][layer]:
                draw.append((obj.texture,obj.position))
        return draw


    def bind(self,obj:GameObject,obj_type:str,layer:int):
        if layer > len(self.obj_in_sight[obj_type])-1:
            layer = len(self.obj_in_sight[obj_type])-1
        elif layer < 0:
            layer = 0
        self.obj_in_sight[obj_type][layer].append(obj)

    def unbind(self,obj:GameObject,obj_type:str,layer:int):
        if obj in self.obj_in_sight[obj_type][layer]:
            self.obj_in_sight[obj_type][layer].remove(obj)

    #更改摄像机位置
    def setPosition(self,position:pygame.Vector2):
        for type in self.obj_in_sight:
            for layer in self.obj_in_sight[type]:
                for obj in layer:
                    obj.setPosition(pygame.Vector2(obj.position.x - self.position.x + self.origin.x,
                                                   obj.position.y - self.position.y + self.origin.y))

class UICamera(Camera):
    def __init__(self):
        super().__init__()
        self.obj_in_sight["UI"] = []
        for i in range(20):
            self.obj_in_sight["UI"].append([])

    def draw(self,screen:pygame.Surface)->list[list[tuple[pygame.Surface,pygame.Vector2]]]:
        draw = []
        draw.append(self.drawAllFromType("UI",screen))
        return draw

    def drawAllFromType(self,obj_type:str,screen:pygame.Surface):
        draw: list[tuple[pygame.Surface,pygame.Vector2]] = []
        for layer in self.obj_in_sight[obj_type]:
            for obj in layer:
                draw = obj.draw(screen)
        return draw