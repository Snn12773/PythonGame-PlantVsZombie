from collections import defaultdict

import pygame

"""
事件总线
代替pygame内置的event
采用订阅-推送方法
在更复杂的游戏情景应该会更高效吧
"""
class EventBus:
    def __init__(self):
        #所有事件
        self.events:list[pygame.event.Event] = []
        #订阅者
        #结构：subscribers["事件"]={订阅者:{过滤器}}
        self.subscribers = defaultdict(dict)

    def update(self, dt:float):
        #接收新的事件
        self.events = pygame.event.get()
        #每帧开始清除事件
        for event in self.subscribers:
            for sub in self.subscribers[event]:
                if hasattr(sub, "clearEvent"):
                    sub.clearEvent()
        #对每个订阅者推送事件
        for event in self.events:
            if self.subscribers[event.type]:
                for sub in self.subscribers[event.type]:
                    if not hasattr(sub, "getEvent"):
                        return
                    if self.filter(event,self.subscribers[event.type][sub]):
                        sub.getEvent(event)

    #过滤器方法
    #过滤器:{"名称":"参数"}
    def filter(self,event:pygame.event.Event,e_filter:dict):
        temp = True
        if e_filter is None:
            return True
        for f in e_filter:
            if hasattr(event, f):
                if getattr(event,f,None) != e_filter[f]:
                    temp = False
        return temp

    #订阅
    def subscribe(self,source,event_type,e_filter:dict = None):
        self.subscribers[event_type][source] = e_filter

    #取消订阅
    def unsubscribe(self,source,event:pygame.event.Event):
        self.subscribers[event.type].remove(source)
#单例
eventBus = EventBus()