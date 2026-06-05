from collections import defaultdict
from typing import List

import pygame
from pygame import Vector2

from src.core.tool import MoveFunc
from src.core.tool import Timer

from src.core.data import GameEvent
from src.core.data.Animate import getPreview, loadAnimate
from src.core.data.Animate import Animate
from src.core.data.GameEvent import *
from src.core.game.GameObject import GameObject

from src.core.game.EventBus import eventBus


class UI(GameObject):
    def __init__(self):
        super().__init__()
        self.scene = None

        self.layer = 0

        self.child: List[UI] = []
        self.parent: UI = None

        self.layout_position: Vector2 = Vector2(0, 0)

        self.lock: bool = False
        self.visible: bool = True

        self.layout_animate = False
        self.mark_layout: bool = False
        self.root: bool = False

        self.has_texture = True
        self.texture: pygame.Surface = None
        self.rect: pygame.Rect = None

        self.input_getter = False

        self.mouse_in = False

    def setLayer(self, layer: int):
        self.layer = layer
        for child in self.child:
            child.setLayer(layer+1)

    def addChild(self, child):
        self.child.append(child)
        child.parent = self
        child.setLayer(self.layer+1)
        return self

    def addChildWithIndex(self, child,index):
        self.child.insert(index, child)
        child.parent = self
        child.setLayer(self.layer+1)
        return self

    def removeChild(self, child):
        self.child.remove(child)
        if child.parent == self:
            child.parent = None
        return self

        # 将当前节点设置为根

    def setRoot(self):
        if self.parent is None:
            self.root = True
        return self

    def loadScene(self, scene):
        self.scene = scene
        for child in self.child:
            child.loadScene(scene)

    def defaultPosition(self):
        self.gotoLayout(force=True)
        for child in self.child:
            child.defaultPosition()

    #是否显示
    def setVisible(self, visible: bool):
        self.visible = visible
        return self

    #加载贴图
    def loadTexture(self, path: str):
        self.texture = pygame.image.load(path)
        self.rect = self.texture.get_rect()
        self.size = pygame.Vector2(self.rect.width, self.rect.height)
        return self

    def loadFromSurface(self, surface: pygame.Surface):
        self.texture = surface
        self.rect = self.texture.get_rect()
        self.size = pygame.Vector2(self.rect.width, self.rect.height)

    #设置位置
    def setPosition(self,position: Vector2):
        if self.rect is not None:
            self.rect.x = int(position.x)
            self.rect.y = int(position.y)
        if self.parent is not None:
            super().setPosition(position)
        for child in self.child:
            child.setPosition(Vector2(self.position.x+child.layout_position.x,
                                      self.position.y+child.layout_position.y))

    #相对于父层级的位置
    def setLayoutPosition(self, position: Vector2):
        if not self.mark_layout:
            self.mark_layout = True
        self.layout_position = position

    #获取尺寸
    def getSize(self):
        return self.size

    def gotoLayout(self,force:bool=False):
        if force or (self.mark_layout and not self.layout_animate):
            if self.root or self.parent is None:
                self.setPosition(self.layout_position)
            else:
                self.setPosition(Vector2(self.parent.position.x + self.layout_position.x,
                            self.parent.position.y + self.layout_position.y))

    #排列
    def layout(self):
        if self.mark_layout:
            self.gotoLayout()
        for c in self.child:
            c.layout()

    #绘制方法,先绘制低层再绘制高层
    def draw(self,screen:pygame.Surface, draw_list: dict[int,List[tuple[pygame.Surface,pygame.Vector2]]] = None):
        if not self.visible:
            return
        if draw_list is None:
            draw_list = defaultdict(list)
        if self.has_texture:
            draw_list[self.layer].append((self.texture, self.position))
        for child in self.child:
            child.draw(screen, draw_list)

        if self.root:
            draw:list[tuple[pygame.Surface,pygame.Vector2]] = []
            for layer in sorted(draw_list):
                for ui in draw_list[layer]:
                    draw.append(ui)

            return draw
        return []

    #鼠标进入时
    def guiInput(self,position:Vector2):
        pass

    def mouseIn(self):
        pass

    def mouseExit(self):
        pass

    def update(self,dt:float)->None:
        if self.scene is None:
            return
        if self.input_getter:
            if self.visible and self.rect is not None:
                if self.rect.collidepoint(pygame.mouse.get_pos()):
                    if not self.mouse_in:
                        self.mouseIn()
                        self.mouse_in = True
                    self.guiInput(pygame.Vector2(pygame.mouse.get_pos()[0],pygame.mouse.get_pos()[1]))
                else:
                    if self.mouse_in:
                        self.mouseExit()
                        self.mouse_in = False

        self.uiUpdate(dt)

        for child in self.child:
            child.update(dt)

    #专门处理ui更新
    def uiUpdate(self,dt: float):
        pass

#按钮
class UIButton(UI):
    def __init__(self):
        super().__init__()
        self.action_name: str = ""

        self.input_getter = True
        self.pressed: bool = False
        self.texture_unpress:pygame.Surface = None
        self.texture_press:pygame.Surface = None
        self.mask: pygame.Surface = None

        eventBus.subscribe(self,pygame.MOUSEBUTTONDOWN,{})

    def canPress(self)->bool:
        return True

    def loadButtonTexture(self,unpress_path: str,press_path:str):
        self.texture_unpress = pygame.image.load(unpress_path)
        self.texture_press = pygame.image.load(press_path)
        self.loadTexture(unpress_path)

    def guiInput(self,position:Vector2):
        can_press = self.canPress()
        for event in self.events:
            #左键-按下
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if can_press:
                    self.press()


    def press(self):
        pass

    def release(self):
        pass

    #传入事件的名字,作为BUTTON_PRESS的参数
    def setActionName(self, name: str):
        self.action_name = name
        return self

#切换按钮
#支持多种形态
class UISwitchButton(UI):
    def __init__(self):
        super().__init__()
        self.action_name: str = ""
        self.args: dict = {}
        self.options: List[str] = []
        self.index:int = 0

    def addOption(self, option: str):
        self.options.append(option)
        return self

    def removeOption(self, option: str):
        self.options.remove(option)
        return self

    def press(self):
        if self.index >= len(self.options):
            self.index = 0
        else:
            self.index = self.index + 1

    #默认在true和false间切换
    def default(self):
        self.options = ["True", "False"]
        return self

#图像
class UIImage(UI):
    def __init__(self):
        super().__init__()

    def scale(self,size:Vector2):
        self.texture = pygame.transform.scale(self.texture,size)
        self.rect = self.texture.get_rect()

#动图
class UIAnimateTexture(UI):
    def __init__(self):
        super().__init__()
        self.animate: Animate = None

#文本
class UIText(UI):
    def __init__(self):
        super().__init__()
        self.text: str = ""
        self.text_size = 14
        self.color: str = "white"

    def setText(self, text: str):
        self.text = text

    def setTextSize(self,size:int):
        self.text_size = size

    #默认没有子元件了
    def draw(self,screen:pygame.Surface, draw_list: dict[int,List[tuple[pygame.Surface,pygame.Vector2]]] = None):
        font = pygame.font.SysFont("simhei", self.text_size)
        self.texture = font.render(self.text, True, self.color)
        super().draw(screen, draw_list)

#容器
class UIContainer(UI):
    LAYOUT_MODE = {"vertical":0,
                   "horizontal":1,
                   "none":2}
    def __init__(self):
        super().__init__()

        self.layout_mode = self.LAYOUT_MODE["none"]
        #上边界
        self.border_up = 0
        #左边界
        self.border_left = 0
        #间隔
        self.interval = 0

        self.has_texture = False

    def addChild(self, child):
        super().addChild(child)
        self.layout()

    def layout(self):
        #垂直排列
        if self.layout_mode == self.LAYOUT_MODE["vertical"]:
            temp_x = self.position.x + self.border_left
            temp_y = self.position.y + self.border_up
            for c in self.child:
                c.setLayoutPosition(pygame.Vector2(temp_x,temp_y))
                temp_y += c.size.y + self.interval
        #水平排列
        elif self.layout_mode == self.LAYOUT_MODE["horizontal"]:
            temp_x = self.position.x + self.border_left
            temp_y = self.position.y + self.border_up
            for c in self.child:
                c.setLayoutPosition(pygame.Vector2(temp_x,temp_y))
                temp_x += c.size.x + self.interval
        #无序
        else:
            for c in self.child:
                c.setLayoutPosition(pygame.Vector2(self.position.x - c.position.x,
                                    self.position.y - c.position.y))
        for c in self.child:
            c.layout()

    def setLayoutMode(self, mode:int):
        self.layout_mode = mode

    #按子层次的大小计算尺寸
    def getSize(self):
        x_min = self.position.x
        y_min = self.position.y
        x_max = self.position.x + self.size[0]
        y_max = self.position.y + self.size[1]
        for c in self.child:
            x_min = min(x_min, c.position.x)
            y_min = min(y_min, c.position.y)
            x_max = max(x_max, c.position.x + c.getSize().x)
            y_max = max(y_max, c.position.y + c.getSize().y)
        self.size = pygame.Vector2(x_max - x_min, y_max - y_min)
        return self.size


#容器(带背景)
class UIPanel(UIContainer):
    def __init__(self):
        super().__init__()
        self.has_texture = True

    def getSize(self):
        return self.size

#网格容器
class UIGridContainer(UI):
    def __init__(self):
        super().__init__()
        #行与列
        self.row: int = 0
        self.col: int = 0
        #边界
        self.border_up = 0
        self.border_left = 0
        #间隔
        self.interval_x = 0
        self.interval_y = 0

        self.has_texture = False

    def addChild(self, child):
        super().addChild(child)
        self.layout()

    def layout(self):
        temp_x = self.position.x + self.border_left
        temp_y = self.position.y + self.border_up
        r,c = 0,0
        count = 0
        for ch in self.child:
            count += 1
            if count > self.row*self.col:
                break
            temp_x = self.position.x + self.border_left + c * (ch.size.x + self.interval_x)
            temp_y = self.position.y + self.border_up + r * (ch.size.y + self.interval_y)
            ch.setLayoutPosition(pygame.Vector2(temp_x, temp_y))
            if c < self.col-1:
                c += 1
            else:
                c = 0
                r += 1
        for c in self.child:
            c.layout()

    def setCol(self, col:int):
        self.col = col
        return self

    def setRow(self, row:int):
        self.row = row
        return self

    #按子层次的大小计算尺寸
    def getSize(self):
        x_min = self.position.x
        y_min = self.position.y
        x_max = self.position.x + self.size[0]
        y_max = self.position.y + self.size[1]
        for c in self.child:
            x_min = min(x_min, c.position.x)
            y_min = min(y_min, c.position.y)
            x_max = max(x_max, c.position.x + c.getSize().x)
            y_max = max(y_max, c.position.y + c.getSize().y)
        self.size = pygame.Vector2(x_max - x_min, y_max - y_min)
        return self.size

#网格容器(带背景)
class UIGridBox(UIGridContainer):
    def __init__(self):
        super().__init__()
        self.has_texture = True

    def getSize(self):
        return self.size

class UIProgressBar(UI):
    DIRECT = {"up": 0,
              "down": 1,
              "left": 2,
              "right": 3}
    def __init__(self):
        super().__init__()
        self.max = 100
        self.min = 0
        self.value = 0

        self.origin_progress_texture: pygame.Surface = None
        self.clip_progress_texture: pygame.Surface = None
        #是否有框架，决定是否要渲染框架
        self.has_frame = False

        self.border_up = 0
        self.border_left = 0
        self.progress_pos: Vector2 = Vector2(self.position.x + self.border_left,
                                             self.position.y + self.border_up)

        #延伸方向
        self.direct: int = self.DIRECT["right"]

    def loadProgressTexture(self,path:str):
        self.origin_progress_texture = pygame.image.load(path).convert_alpha()
        self.clip_progress_texture = pygame.image.load(path).convert_alpha()
        self.rect = self.origin_progress_texture.get_rect()
        self.size = Vector2(self.rect.width, self.rect.height)

    def setPosition(self,position:Vector2):
        offset = Vector2(position.x - self.position.x,
                        position.y - self.position.y)
        super().setPosition(position)
        self.progress_pos = Vector2(self.progress_pos.x + offset.x,
                                    self.progress_pos.y + offset.y)


    def clip(self):
        size = self.origin_progress_texture.get_size()
        precent = self.value/(self.max - self.min)
        if self.value == self.max:
            self.clip_progress_texture = self.origin_progress_texture.copy()
            self.progress_pos = Vector2(self.position.x + self.border_left,
                                        self.position.y + self.border_up)
            return
        if self.value == self.min:
            self.visible = False
            self.progress_pos = Vector2(self.position.x + self.border_left,
                                        self.position.y + self.border_up)
            return
        else:
            self.visible = True

        if self.direct == self.DIRECT["left"]:
            progress_pos = Vector2(self.position.x + self.border_left + size[0]*(1-precent),
                                   self.position.y + self.border_up)
            self.clip_progress_texture = self.origin_progress_texture.subsurface((progress_pos.x,
                                                                                 progress_pos.y,
                                                                                  self.size[0]*precent,
                                                                                  self.size[1]))
        elif self.direct == self.DIRECT["up"]:
            progress_pos = Vector2(self.position.x + self.border_left,
                                   self.position.y + self.border_up + size[1]*(1-precent))
            self.clip_progress_texture = self.origin_progress_texture.subsurface((0,
                                                                                  0,
                                                                                  self.size[0],
                                                                                  self.size[1]*precent))
        elif self.direct == self.DIRECT["down"]:
            progress_pos = Vector2(self.position.x + self.border_left,
                                   self.position.y + self.border_up)
            self.clip_progress_texture = self.origin_progress_texture.subsurface((0,
                                                                                  0,
                                                                                  self.size[0] * precent,
                                                                                  self.size[1]))
        elif self.direct == self.DIRECT["right"]:
            progress_pos = Vector2(self.position.x + self.border_left,
                                   self.position.y + self.border_up)
            self.clip_progress_texture = self.origin_progress_texture.subsurface((0,
                                                                                  0,
                                                                                  self.size[0],
                                                                                  self.size[1] * precent))


    def setValue(self, value):
        self.value = value
        self.clip()

    def getValue(self):
        return self.value

    def setMax(self, value):
        self.max = value
        if self.value > self.max:
            self.value = self.max
        self.clip()

    def getMax(self):
        return self.max

    def setMin(self, value):
        self.min = value
        if self.value < self.min:
            self.value = self.min
        self.clip()

    def getMin(self):
        return self.min

    def update(self,dt:float):
        pass

    def draw(self,screen:pygame.Surface, draw_list: dict[int,List[tuple[pygame.Surface,pygame.Vector2]]] = None):
        if draw_list is None:
            draw_list = {}
        if self.has_texture and self.visible:
            draw_list[self.layer].append((self.clip_progress_texture,self.progress_pos))
        for child in self.child:
            child.draw(screen, draw_list)

        for layer in draw_list:
            for ui in draw_list[layer]:
                screen.blit(ui[0], ui[1])

class UISeedCard(UIImage):
    GAME_STAGE = {"choose":0,
                  "playing":1}
    def __init__(self,plant:str,plant_data):
        super().__init__()

        self.plant : str = plant
        self.plant_data: dict = plant_data

        self.layout_animate = True

        self.texture_dark = pygame.image.load("src/res/texture/UI/UI_Seed_Card_bg_dark.png")
        self.texture_light = pygame.image.load("src/res/texture/UI/UI_Seed_Card_bg.png")
        self.loadTexture("src/res/texture/UI/UI_Seed_Card_bg.png")

        self.preview: UIImage = UIImage()
        self.preview.loadFromSurface(getPreview(plant_data["animate"][0]))
        self.preview.scale(pygame.Vector2(self.preview.size.x * 45/self.size.x,
                                        self.preview.size.y * 45/self.size.y))
        self.addChild(self.preview)

        #花费文本
        self.cost_text = UIText()
        self.cost = plant_data["cost"]

        self.cost_text.color = "black"
        self.cost_text.setText(str(self.cost))
        self.addChild(self.cost_text)
        self.text_post_fix_x = 4
        self.cost_text.setLayoutPosition((pygame.Vector2(self.position.x + self.size.x/2 - self.cost_text.text.__len__()*self.text_post_fix_x,
                                             self.position.y + self.size.y - 20)))

        #cd显示
        self.cd_progress = UIProgressBar()
        self.cd_progress.loadProgressTexture("src/res/texture/UI/UI_Seed_Card_mask.png")
        self.cd_progress.direct = UIProgressBar.DIRECT["up"]
        self.addChild(self.cd_progress)
        self.cd_progress.setLayoutPosition(self.position.copy())
        self.cd_progress.setPosition(self.position.copy())
        self.cd_progress.setValue(0)

        self.cd = plant_data["cd"]
        self.cd_timer = 0
        self.in_cd = False
        self.timer_cd = Timer.Timer()
        self.timer_cd.setOneshot(True)
        self.timer_cd.setTime(self.cd)

        self.input_getter = True
        self.choose : bool = False
        self.selectable = True
        self.select: bool = False
        self.moving: bool = False

        eventBus.subscribe(self,pygame.MOUSEBUTTONDOWN)

    def makeCopy(self):
        copy = UISeedCard(self.plant,self.plant_data)
        return copy

    def guiInput(self,position:Vector2):
        if self.lock or self.moving:
            return
        if not self.selectable:
            return
        if self.scene.stage == self.GAME_STAGE["choose"]:
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.choose:
                            pygame.event.post(pygame.event.Event(CHOOSE_CARD,{"source":self}))
                        else:
                            pygame.event.post(pygame.event.Event(UNCHOOSE_CARD,{"source":self}))
                        self.choose = not self.choose

    def uiUpdate(self,dt:float):
        if self.in_cd:
            if self.timer_cd.tick(dt):
                self.in_cd = False
                self.setSelectAble(self.canSelect())
                self.cd_progress.setValue(0)
            self.cd_progress.setValue(100 - int(100 * (self.timer_cd.getTime() / self.cd)))

        if self.moving:
            self.setLayer(3)
            for c in self.child:
                c.layer = self.layer + 1
            velocity = MoveFunc.lerpPosition(self.position,self.layout_position,5)
            self.setPosition(pygame.Vector2(velocity.x + self.position.x,
                                            velocity.y + self.position.y))
            if self.position.distance_to(self.layout_position) < 1:
                self.moving = False
                self.setPosition(self.layout_position.copy())
                self.setLayer(self.parent.layer + 1)
            for c in self.child:
                c.setLayer(self.layer + 1)

        if self.scene.stage == self.GAME_STAGE["playing"]:
            self.setSelectAble(self.canSelect())
            for event in self.events:
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:
                        if not self.selectable:
                            return
                        if self.select:
                            g = self.scene.plantablePosition(event.pos, self.plant_data)
                            if g is not None:
                                pygame.event.post(pygame.event.Event(PLANT, {"plant_data": self.plant_data,
                                                                             "grid": g,}))
                                pygame.event.post(pygame.event.Event(SUN_LOST, {"amount":self.cost}))
                                self.select = False
                                self.preview.visible = True
                                #进入cd
                                self.in_cd = True
                                self.timer_cd.start()
                                self.setSelectAble(self.canSelect())
                            else:
                                pygame.event.post(pygame.event.Event(UNSELECT_CARD, {"source": self}))
                                self.select = False
                                self.preview.visible = True
                        else:
                            if self.scene.any_card_selected or not self.rect.collidepoint(event.pos):
                                return
                            pygame.event.post(pygame.event.Event(SELECT_CARD, {"source": self,
                                                                               "preview": getPreview(
                                                                                   self.plant_data["animate"][0]),
                                                                               "plant_data": self.plant_data}))
                            self.select = True
                            self.preview.visible = False

    def canSelect(self)->bool:
        if self.in_cd:
            return False
        if self.scene.sun < self.cost:
            return False
        return True

    def setSelectAble(self,selectable:bool):
        if self.selectable == selectable:
            return
        self.selectable = selectable
        if selectable:
            self.texture = self.texture_light
        else:
            self.texture = self.texture_dark


class UISeedPanel(UIPanel):
    def __init__(self):
        super().__init__()
        self.max_container = 7

        self.border_left = 4
        self.border_up = 4
        self.interval = 4

        self.loadTexture("src/res/texture/UI/UI_Seed_Panel.png")

        self.setLayoutMode(self.LAYOUT_MODE["horizontal"])

        eventBus.subscribe(self,CHOOSE_CARD)
        eventBus.subscribe(self,UNCHOOSE_CARD)
        eventBus.subscribe(self,SELECT_CARD)
        eventBus.subscribe(self,UNSELECT_CARD)

    def uiUpdate(self,dt:float):
        for event in self.events:
            if event.type == CHOOSE_CARD:
                self.addChild(event.source)
                self.layout()
                event.source.moving = True
            if event.type == UNCHOOSE_CARD:
                self.removeChild(event.source)
                self.layout()
                event.source.moving = True


class UISelectGrid(UIGridBox):
    def __init__(self):
        super().__init__()
        self.col = 8
        self.row = 6
        self.border_up = 56
        self.border_left = 6
        #依据已解锁植物填充
        self.unlock_list: dict[str,bool]
        #空槽位
        self.temp_card = {}

        self.loadTexture("src/res/texture/UI/UI_Select_Grids.png")

        eventBus.subscribe(self,CHOOSE_CARD)
        eventBus.subscribe(self,UNCHOOSE_CARD)
        eventBus.subscribe(self,BUTTON_PRESSED,{"action":"card_choose_done"})

    def uiUpdate(self,dt:float):
        for event in self.events:
            if event.type == CHOOSE_CARD:
                index = self.child.index(event.source)

                #将空卡牌作为占位符
                temp = event.source.makeCopy()
                temp.lock = True
                temp.visible = False
                self.temp_card[event.source.plant] = index
                self.removeChild(event.source)
                self.addChildWithIndex(temp,index)
                self.layout()
                temp.gotoLayout(force=True)
                event.source.moving = True

            if event.type == UNCHOOSE_CARD:
                index = self.temp_card[event.source.plant]
                temp = self.child[index]
                self.removeChild(temp)
                del temp
                self.addChildWithIndex(event.source, index)
                self.layout()
                event.source.moving = True

            if event.type == BUTTON_PRESSED and event.action == "card_choose_done":
                self.visible = False
                self.lock = True


class UISunResources(UIImage):
    def __init__(self):
        super().__init__()
        self.loadTexture("src/res/texture/UI/UI_SUN.png")

        self.amount:int = 0

        self.text_pos_fix_x = 5
        self.text_ui = UIText()
        self.text_ui.setTextSize(20)
        self.addChild(self.text_ui)
        self.text_ui.setLayoutPosition(Vector2(self.size.x/2 - self.text_ui.size.x/2 - self.text_pos_fix_x,
                                               self.size.y - self.text_ui.size.y - 25))

        eventBus.subscribe(self, SUN_LOST)
        eventBus.subscribe(self, SUN_GAIN)

    def setAmount(self,amount:int):
        self.amount = amount
        self.text_ui.setText(str(amount))
        self.text_ui.setLayoutPosition(Vector2(self.size.x/2 - self.text_ui.size.x/2 - self.text_pos_fix_x*len(self.text_ui.text),
                                               self.size.y - self.text_ui.size.y - 25))

    def uiUpdate(self,dt:float):
        for event in self.events:
            if event.type == SUN_GAIN:
                self.setAmount(event.amount + self.amount)
            if event.type == SUN_LOST:
                self.setAmount(self.amount - event.amount)


class UISeedSelectButton(UIButton):
    def __init__(self):
        super().__init__()
        self.loadButtonTexture("src/res/texture/UI/UI_Choose_Button/select_button0000.png",
                                "src/res/texture/UI/UI_Choose_Button/select_button0001.png")
        self.action_name = "card_choose_done"

    def mouseIn(self):
        if self.canPress():
            self.texture = self.texture.copy()
            self.texture.fill((50, 50, 50), special_flags=pygame.BLEND_RGB_ADD)

    def mouseExit(self):
        if self.pressed:
            self.texture = self.texture_press
        else:
            self.texture = self.texture_unpress

    def canPress(self) ->bool:
        if self.scene.plant_choose == self.scene.max_slot or self.scene.plant_choose == self.scene.unlock_plant:
            return True
        else:
            return False

    def press(self):
        pygame.event.post(pygame.event.Event(BUTTON_PRESSED,{"source":self,"action":self.action_name}))
        #需要更改
        self.visible = False
        self.lock = True
