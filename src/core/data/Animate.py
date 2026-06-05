import os
from typing import List

import pygame

from src.core.tool.Timer import Timer

#加载动画
#从文件加载后以名字为键存储在动画中
def loadAnimate(name:str,path:str)->None:
    ani = []
    for file in os.listdir(path):
        if file.endswith(".png"):
            ani.append(pygame.image.load(path + file))

    Animate.animates[name] = ani

def getPreview(name:str)->pygame.Surface:
    return Animate.animates[name][0].copy()

#这回动画不再把帧加载进自己的类中，节省内存
class Animate:
    animates = {}
    def __init__(self):
        self.frame_rate: int = 8
        self.frame: int = 0
        self.animate_name: str = ""
        self.playing: bool = False
        self.timer: Timer = Timer()
        self.timer.setTime(1/float(self.frame_rate))

    #设置当前动画
    def setAniamte(self,name:str):
        self.animate_name = name
        return self

    #设置帧率
    def setFrameRate(self,frame_rate:float):
        self.frame_rate = frame_rate
        return self

    #设置当前帧
    def setFrame(self,frame:int):
        self.frame = frame
        return self

    #获取当前帧
    def getFrame(self):
        return self.frame

    #获取当前帧
    def getTexture(self)-> pygame.Surface:
        return self.animates[self.animate_name][self.frame]

    #开始播放
    def play(self,animate:str = None,frame:int = 0):
        self.playing = True
        self.timer.start()
        if animate is not None:
            self.animate_name = animate
        self.frame = frame

    #停止播放
    def stop(self):
        self.playing = False
        self.timer.stop()

    #下一帧
    def nextFrame(self):
        if self.frame >= len(self.animates[self.animate_name]) -1:
            self.frame = 0
        else:
            self.frame = self.frame + 1

    #上一帧
    def prevFrame(self):
        if self.frame <= 0:
            self.frame = len(self.animates[self.animate_name])-1
        else:
            self.frame = self.frame - 1

    def update(self,dt:float):
        if self.playing:
            if self.timer.tick(dt):
                self.nextFrame()

