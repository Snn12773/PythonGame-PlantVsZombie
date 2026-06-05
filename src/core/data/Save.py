
"""
我该怎么写这个呢
"""
from src.res.JsonLoader import loadJson


class Save:
    def __init__(self):
        #植物解锁目录
        #{"植物名":是否解锁}
        self.plant_unlock_list ={}

        #关卡数据
        #我不想做关卡内保存，简单记录打到哪里即可
        #{"某个模式":["关卡":进度]}}
        self.level_data = {}

        #资源
            #金币
        self.coin = 0
            #卡槽数
        self.card_slot = 7

        #道具解锁
        #{"工具名":是否解锁}
        self.tool_unlock_list = {}

        self.create("1")

    def create(self,name):
        data = loadJson("data/default_save.json")
        self.plant_unlock_list = data["plant_unlock_list"]
        self.level_data = data["level_data"]
        self.coin = data["coin"]
        self.card_slot = data["card_slot"]
        self.tool_unlock_list = data["tool_unlock_list"]

    #加载
    def load(self,name:str) -> dict:
        pass

    #保存
    def save(self,name:str):
        save_data = {
            "plant_unlock_list":self.plant_unlock_list,
            "level_data":self.level_data,
            "coin":self.coin,
            "card_slot":self.card_slot,
            "tool_unlock_list":self.tool_unlock_list
        }

    #解锁植物
    def unlockPlant(self,plant:str):
        if plant in self.plant_unlock_list:
            self.plant_unlock_list[plant]=True

    #
    def setLevelProgress(self,mode:str,level:str,progress:int):
        if mode in self.level_data:
            if level in self.level_data[mode]:
                self.level_data[mode][level] = progress


#这是一个单例，所有类都能访问
#但是不太确定是否要这么做
save = Save()