from backend.core.game_map import Vec2

# кардинальные направления как (dx, dy) в пикселях
DIR_RIGHT = Vec2(1, 0)
DIR_LEFT  = Vec2(-1, 0)
DIR_UP    = Vec2(0, -1)
DIR_DOWN  = Vec2(0, 1)
STOPPED   = Vec2(0, 0)


class PacMan:

    MOUTH_OPEN_ANGLE   = 45   # степени
    MOUTH_ANIM_SPEED   = 8    # полных циклов открытия-закрытия в секунду
    COLLISION_RADIUS   = 10






