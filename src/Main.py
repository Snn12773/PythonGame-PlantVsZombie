import pygame

from src.core.data.Save import save
from src.core.game.EventBus import eventBus
from src.core.game.Scene import *
from src.core.data import Animate


class Main:
    def __init__(self):
        self.running = False

        #窗体
        self.WINDOW_WIDTH = 800
        self.WINDOW_HEIGHT = 600
        self.WINDOW_TITLE = "Plant Vs Zombie Rebuild.v3 by Snn12772"

        #实例化窗体
        pygame.init()
        self.clock = pygame.time.Clock()
        self.screen = pygame.display.set_mode((self.WINDOW_WIDTH, self.WINDOW_HEIGHT))
        pygame.display.set_caption(self.WINDOW_TITLE)

        self.dt: float = 0

        #加载存档
        save.load("test")

        #场景
        self.scene:Scene = None
        self.level_data = loadJson("data\map\level.json")

        self.start()

    def setup(self):
        animate_data = loadJson("data/animate.json")
        for anim in animate_data:
            print(anim)
            Animate.loadAnimate(anim, "src/res/animate/" + animate_data[anim] +"/")
        self.scene = Level()
        self.scene.load(self.level_data.get("adventure").get("day")[0])

        self.scene.start()

    def draw(self):
        self.screen.fill("white")

        draw_list = self.scene.draw(self.screen)
        for l in draw_list:
            for texture, position in l:
                self.screen.blit(texture, position)

        self.scene.main_camera.drawHitBox(self.screen)

        pygame.display.flip()

    def update(self,dt:float):
        eventBus.update(dt)

        self.scene.update(dt)

    def start(self):
        self.setup()
        self.running = True

    def stop(self):
        self.save()
        self.running = False

    def save(self):
        pass

    def load(self):
        pass

    #运行时调用
    def run(self)->bool:
        if self.running:
            #退出
            for event in eventBus.events:
                if event.type == pygame.QUIT:
                    self.stop()

            self.update(self.dt)
            self.draw()

            self.dt = self.clock.tick(60) / 1000


            return True
        else:
            return False



if __name__ == "__main__":
    main = Main()
    while main.run():
        pass