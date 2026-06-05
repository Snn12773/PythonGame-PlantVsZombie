import random

from pygame.examples import grid

from src.core.data.Save import save
from src.core.game.Camera import Camera, UICamera
from src.core.game.EventBus import eventBus
from src.core.game.GameObject import GameObject
from src.core.game.UI.UI import *
from src.core.game.entity.Zombie import Zombie
from src.core.game.manager.Manager import *

from src.core.data.GameEvent import *

from src.res.JsonLoader import loadJson


class Scene(GameObject):
    def __init__(self):
        super().__init__()
        """
        场景层级顺序：
            背景
            影子
            实体：
                行(低-高):
                    弹射物
                    植物
                    僵尸
            UI(单独摄像机)
        """

        #管理器类
        self.gridManager = GridManager()
        self.entityManager = EntityManager()
        self.mouseManager = MouseManager()

        self.gridManager.scene = self
        self.entityManager.scene = self

        #摄像机
        self.main_camera = Camera()
        self.ui_camera = UICamera()

        self.running = False

    def loadUI(self) -> UI:
        return UIContainer()

    def load(self,data):
        pass

    def save(self):
        pass

    def draw(self,screen:pygame.Surface)->list[list[tuple[pygame.Surface,pygame.Vector2]]]:
        pass


    def update(self,dt:float):
        pass

    def start(self):
        self.running = True

    def stop(self):
        self.running = False

    def onRunning(self,dt:float):
        pass

#关卡
#由主菜单加载
class Level(Scene):
    def __init__(self):
        super().__init__()
        #背景
        self.background:GameObject = GameObject()
        self.background.loadTexture("src/res/texture/background/day.png")

        #数据
        self.data = {}
        self.map_data = {}
        self.map_size: tuple[int, int] = (0,0)
        #僵尸生成缓冲
        self.zombie_buffer = []
        #僵尸预览
        self.preview = []
        #旗帜
        self.flag = 0
        self.total_flag = 0
        self.wave = 0
        self.waves = []

        """
        ---------------------------计时器---//
        这里是各种计时器
        也许不需要那么多？
        不知道
        """
        #关卡内计时器
        self.timer = Timer.Timer()
        #开始前的准备时间
        self.preparing = True
        self.prepare_time = 20
        #出怪计时器
        self.spawn_time = 20
        self.spawn_timer = Timer.Timer()
        self.spawn_timer.setTime(self.spawn_time)
        self.spawn_timer.setOneshot(True)
        #单次出怪间隔
        self.spawn_interval = 5
        self.spawn_interval_timer = Timer.Timer()
        self.spawn_interval_timer.setTime(self.spawn_interval)
        #出怪计数器
        self.spawn_total = 0
        self.spawned = 0

        self.timer.setTime(self.prepare_time)
        """
        -----------------------------------//
        """

        #植物
        self.unlock_plant:int = 0
        self.plant_choose:int = 0
        self.max_slot:int = 7

        #游戏状态
        self.stage = UISeedCard.GAME_STAGE["choose"]

        #加载ui
        self.ui_global_container = self.loadUI()
        self.ui_global_container.loadScene(self)

        #是否有卡牌被选择
        self.any_card_selected:bool = False

        #拥有阳光
        self.sun:int = 50



        #事件订阅
        eventBus.subscribe(self,CHOOSE_CARD)
        eventBus.subscribe(self,UNCHOOSE_CARD)
        eventBus.subscribe(self,SELECT_CARD)
        eventBus.subscribe(self,UNSELECT_CARD)
        eventBus.subscribe(self,PLANT)
        eventBus.subscribe(self,BUTTON_PRESSED,{"action":"card_choose_done"})
        eventBus.subscribe(self,pygame.MOUSEBUTTONDOWN)
        eventBus.subscribe(self,SPAWN_PROJECTILE)
        eventBus.subscribe(self,SUN_LOST)
        eventBus.subscribe(self,SUN_GAIN)
        eventBus.subscribe(self,SPAWN_SUN)
        eventBus.subscribe(self,SPAWN_ZOMBIE)

    def loadUI(self) -> UI:
        #所有ui
        ui_global_container: UIContainer = UIContainer()
        ui_top_container: UIContainer = UIContainer()
        ui_bottom_container: UIContainer = UIContainer()
        ui_sun_resources:UISunResources = UISunResources()
        ui_seed_bar:UIPanel = UISeedPanel()
        ui_seed_select_grid:UIGridBox = UISelectGrid()
        ui_seed_select_button:UIButton = UISeedSelectButton()
        ui_menu:UIPanel = UIPanel()
        ui_menu_button:UISwitchButton = UISwitchButton()
        ui_level_progress:UIProgressBar = UIProgressBar()

        #ui设置
        ui_global_container.setLayoutMode(UIContainer.LAYOUT_MODE["none"])
        ui_top_container.setLayoutMode(UIContainer.LAYOUT_MODE["horizontal"])
        ui_sun_resources.setAmount(50)

        #ui层级
        ui_global_container.setRoot()
        ui_global_container.addChild(ui_top_container)
        ui_global_container.addChild(ui_bottom_container)
        #ui_global_container.addChild(self.ui_menu)
        #ui_global_container.addChild(self.ui_menu_button)

        ui_global_container.addChild(ui_seed_select_grid)
        ui_global_container.addChild(ui_seed_select_button)

        ui_top_container.addChild(ui_sun_resources)
        ui_top_container.addChild(ui_seed_bar)

        #加载植物卡
        plant_data = loadJson("data/entity/plant.json")
        for plant in save.plant_unlock_list:
            if save.plant_unlock_list[plant] == True:
                self.unlock_plant += 1
                p = UISeedCard(plant,plant_data[plant])
                ui_seed_select_grid.addChild(p)

        #标记
        ui_sun_resources.gotoLayout()
        ui_seed_bar.gotoLayout()

        #把根节点加入摄像机
        self.ui_camera.bind(ui_global_container,"UI",0)
        ui_global_container.layout()
        #ui位置
        ui_seed_select_button.layer = ui_seed_select_grid.layer + 1
        ui_seed_select_grid.setLayoutPosition(pygame.Vector2(80,74))
        ui_seed_select_button.setLayoutPosition(pygame.Vector2(ui_seed_select_grid.layout_position.x + ui_seed_select_grid.size.x/2 - ui_seed_select_button.size.x/2,
                                                              ui_seed_select_grid.layout_position.y + ui_seed_select_grid.size.y - 60))
        ui_global_container.defaultPosition()

        return ui_global_container


    def load(self,data):
        self.main_camera.bind(self.background,"background",0)

        #从存档加载
        self.max_slot = save.card_slot

        self.data = data

        self.map_data = loadJson("data/map/map.json").get(data.get("map"))
        self.map_size = self.map_data.get("size")
        self.gridManager.create(self.map_data,pygame.Vector2(50,110),pygame.Vector2(755,550))

        self.entityManager.initEntityList(self.map_data.get("size")[0],self.map_data.get("size")[1])
        self.main_camera.line = self.map_data.get("size")[0]

        self.preview = data.get("preview")
        self.total_flag = data.get("flag").get("total")
        self.waves = data.get("flag").get("waves")

    #开始生成僵尸
    def startWave(self):
        zombies = []
        z = self.waves[self.wave]
        for i in range(z.times):
            for j in range(z.frequency):
                zombies.append(random.choice(z.zombies))
        self.zombie_buffer.append(zombies)

    #加载下一波
    def nextWave(self):
        self.spawned = 0
        self.spawn_total = self.waves[self.wave]["times"]

    def nextSpawn(self):
        if self.spawned == self.spawn_total:
            return
        n = self.waves[self.wave]["frequency"]
        for i in range(n):
            self.zombie_buffer.append(random.choices(self.waves[self.wave]["zombies"]))
        self.spawned += 1



    def draw(self,screen:pygame.Surface) ->list[list[tuple[pygame.Surface,pygame.Vector2]]]:
        draw:list[list[tuple[pygame.Surface,pygame.Vector2]]] = []
        draw_main = self.main_camera.draw(screen)
        draw_ui = self.ui_camera.draw(screen)
        draw.extend(draw_main)
        draw.extend(draw_ui)
        if self.mouseManager.picking:
            preview = [[self.mouseManager.drawPreview(screen)]]
            draw.extend(preview)

        return draw

    def update(self,dt:float):
        if not self.running:
            return

        self.onRunning(dt)

        self.main_camera.update(dt)
        self.ui_camera.update(dt)
        self.entityManager.update(dt)
        self.mouseManager.update(dt)
        self.ui_global_container.update(dt)

        for event in self.events:
            if event.type == CHOOSE_CARD:
                self.plant_choose += 1
            if event.type == UNCHOOSE_CARD:
                self.plant_choose -= 1
            if event.type == SELECT_CARD:
                self.any_card_selected = True
                self.mouseManager.onSelect(event.preview)
            if event.type == UNSELECT_CARD:
                self.any_card_selected = False
                self.mouseManager.onDeselect()

            if event.type == PLANT:
                self.any_card_selected = False
                self.mouseManager.onDeselect()
                self.entityManager.creatPlant(event.plant_data,event.grid)
            if event.type == SPAWN_SUN:
                self.entityManager.createSun(event.amount,
                                             event.position,
                                             event.is_throw)
            if event.type == SPAWN_PROJECTILE:
                self.entityManager.createProjectile(event.source,
                                                    event.data,
                                                    event.position,
                                                    event.grid)
            if event.type == SPAWN_ZOMBIE:
                self.entityManager.createZombie(event.data,
                                                event.line)

            if event.type == SUN_LOST:
                self.sun -= event.amount

            if event.type == SUN_GAIN:
                self.sun += event.amount


            if event.type == BUTTON_PRESSED and event.action == "card_choose_done":
                self.stage = UISeedCard.GAME_STAGE["playing"]

            if event.type == pygame.MOUSEBUTTONDOWN:
                if event.button == 1:
                    pass

    def getGridPosition(self,pos:pygame.Vector2)->pygame.Vector2:
        return self.gridManager.getGridPosition(pos)

    def plantablePosition(self,pos:pygame.Vector2,plant_data:dict)->Grid|None:
        g = self.gridManager.positonInGrid(pos)
        if g is None or not g.canPlant(plant_data):
            return None
        return g

    def getGridLineCenter(self,line:int)->Vector2:
        return self.gridManager.getGridLineCenter(line)

    def getGrid(self,pos:pygame.Vector2)->Grid|None:
        return self.gridManager.positonInGrid(pos)

    def anyZombieOnline(self,line:int)->bool:
        if len(self.entityManager.getZombies(line)) > 0:
            return True
        else:
            return False

    def plantOnline(self,line:int)->List[Plant]:
        return self.entityManager.getPlant(line)

    def zombieOnline(self,line:int)->List[Zombie]:
        return self.entityManager.getZombies(line)

    def outOfMapSize(self,row:int,col:int)->bool:
        if row < 0 or row >= self.map_size[0] or col < 0 or col >= self.map_size[1]:
            return True
        else:
            return False

    def getMapSize(self)->tuple[int,int]:
        return self.map_size

    def start(self):
        self.running = True
        self.timer.start()

    def stop(self):
        self.running = False

    def onRunning(self,dt:float):
        if self.stage == UISeedCard.GAME_STAGE["choose"]:
            return
        if self.preparing:
            if self.timer.tick(dt):
                self.preparing = False
                self.timer.setTime(25)
        else:
            if self.timer.tick(dt):
                zombie_data = loadJson("data/entity/zombie.json")["normal_zombie"]
                line = random.randrange(0,self.map_size[0]-1)
                pygame.event.post(pygame.event.Event(SPAWN_ZOMBIE,{"data":zombie_data,
                                                                   "line":line}))


#主界面
class MainMenu(Scene):
    def __init__(self,data):
        super().__init__()

#加载界面
class LoadingScreen(Scene):
    def __init__(self,data):
        super().__init__()
