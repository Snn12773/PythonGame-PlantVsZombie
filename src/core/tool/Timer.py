class Timer:
    def __init__(self):
        self.timer: float = 0
        self.time: float = 0
        self.oneshot: bool = False
        self.ticking: bool = False

    def tick(self,dt: float)-> bool:
        if not self.ticking:
            return False
        self.timer += dt
        if self.timer > self.time:
            if self.oneshot:
                self.ticking = False
            self.timer = 0
            return True
        else:
            self.timer += dt
            return False

    #开始计时
    def start(self):
        self.ticking = True

    #停止计时
    def stop(self):
        self.ticking = False

    #设置是否只触发一次
    def setOneshot(self,is_oneshot:bool):
        self.oneshot = is_oneshot
        return self

    #获取计时器时间
    def getTime(self)->float:
        return self.timer

    #设置时间
    def setTime(self,time:float):
        self.time = time
        return self

    #重置计时
    def reset(self,time:float):
        self.timer = 0
        return self