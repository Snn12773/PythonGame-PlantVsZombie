from pygame import Vector2

def lerpPosition(start: Vector2, end: Vector2,t:float) -> Vector2:
    x = (end.x - start.x) / t
    y = (end.y - start.y) / t
    return Vector2(x,y)