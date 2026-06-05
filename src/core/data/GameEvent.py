import pygame.event

#生物受伤事件
    #参数{伤害目标,damage_info{伤害来源，伤害量，伤害类型}}
DAMAGE_EVENT = pygame.USEREVENT + 1

#按钮按下
    #参数{原按钮，事件名称}
BUTTON_PRESSED = pygame.USEREVENT + 2

#切换按钮按下
    #参数{原按钮，事件名称，按钮选项参数}
SWITCH_BUTTON_PRESSED = pygame.USEREVENT + 3

#获取阳光
    #参数{阳光实体,阳光数}
SUN_GAIN = pygame.USEREVENT + 4

#僵尸在场上
    #参数{行}
ZOMBIE_ON_LAWN = pygame.USEREVENT + 5

#产生弹射物
    #参数{来源,弹射物数据,位置,起点格}
SPAWN_PROJECTILE = pygame.USEREVENT + 6

#(选卡)选择植物卡
    #参数{卡牌,预览，植物数据}
CHOOSE_CARD = pygame.USEREVENT + 7

#(选卡)取消选择
    #参数{卡牌}
UNCHOOSE_CARD = pygame.USEREVENT + 8

#(关卡内)选择
    #参数{卡牌}
SELECT_CARD = pygame.USEREVENT + 9

#(关卡内)取消选择
    #参数{卡牌}
UNSELECT_CARD = pygame.USEREVENT + 10

#种植植物
    #参数{植物数据,位置(格子)}
PLANT = pygame.USEREVENT + 11

#失去阳光
    #参数:{数量}
SUN_LOST = pygame.USEREVENT + 12

#生产阳光
    #参数:{数量,位置,是否抛出}
SPAWN_SUN = pygame.USEREVENT + 13

#生成僵尸
    #参数{僵尸数据,行,列(可选)}
SPAWN_ZOMBIE = pygame.USEREVENT + 14