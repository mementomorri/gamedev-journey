from conf import *
from mapmanager import Mapmanager
from typing import NamedTuple


class Position(NamedTuple):
    x: int
    y: int
    z: int


class Player:
    def __init__(self, pos: Position, land: Mapmanager) -> None:
        """
        Representation of player controlled actor.
        :param pos: Position - coordinates representation implemented with tuple.
        :param land:
        """
        self.land = land
        self.mode = False  # режим прохождения сквозь объекты
        self.hero = loader.loadModel('smiley')
        self.hero.setColor(1, 0.5, 0)
        self.hero.setScale(0.3)
        self.hero.setH(180)
        self.hero.setPos(pos)
        self.hero.reparentTo(render)
        self._camera_bind()
        self._accept_events()

    def _camera_bind(self) -> None:
        base.disableMouse()
        base.camera.reparentTo(self.hero)
        base.camera.setPos(0, 0, 1.5)
        self.cameraOn = True

    def _camera_up(self) -> None:
        pos = self.hero.getPos()
        base.mouseInterfaceNode.setPos(-pos[0], -pos[1], -pos[2] - 3)
        base.camera.reparentTo(render)
        base.enableMouse()
        self.cameraOn = False

    def _change_view(self) -> None:
        if self.cameraOn:
            self._camera_up()
        else:
            self._camera_bind()

    def _turn_left(self) -> None:
        self.hero.setH((self.hero.getH() + 5) % 360)

    def _turn_right(self) -> None:
        self.hero.setH((self.hero.getH() - 5) % 360)

    def _look_at(self, angle: int) -> Position:
        """ возвращает координаты, в которые переместится персонаж, стоящий в точке (x, y),
        если он делает шаг в направлении angle"""

        x_from = round(self.hero.getX())
        y_from = round(self.hero.getY())
        z_from = round(self.hero.getZ())

        dx, dy = self._check_dir(angle)
        x_to = x_from + dx
        y_to = y_from + dy
        return Position(x_to, y_to, z_from)

    def _update_pos(self, angle: int) -> None:
        self.hero.setPos(self._look_at(angle))

    @staticmethod
    def _check_dir(angle: int) -> tuple[int, int]:
        """ возвращает округленные изменения координат X, Y,
        соответствующие перемещению в сторону угла angle.
        Координата Y уменьшается, если персонаж смотрит на угол 0,
        и увеличивается, если смотрит на угол 180.
        Координата X увеличивается, если персонаж смотрит на угол 90,
        и уменьшается, если смотрит на угол 270.
            угол 0 (от 0 до 20)      ->        Y - 1
            угол 45 (от 25 до 65)    -> X + 1, Y - 1
            угол 90 (от 70 до 110)   -> X + 1
            от 115 до 155            -> X + 1, Y + 1
            от 160 до 200            ->        Y + 1
            от 205 до 245            -> X - 1, Y + 1
            от 250 до 290            -> X - 1
            от 290 до 335            -> X - 1, Y - 1
            от 340                   ->        Y - 1  """
        if 0 <= angle <= 20:
            return 0, -1
        elif angle <= 65:
            return 1, -1
        elif angle <= 110:
            return 1, 0
        elif angle <= 155:
            return 1, 1
        elif angle <= 200:
            return 0, 1
        elif angle <= 245:
            return -1, 1
        elif angle <= 290:
            return -1, 0
        elif angle <= 335:
            return -1, -1
        else:
            return 0, -1

    def _forward(self) -> None:
        self.move_to((self.hero.getH() + 180) % 360)

    def _back(self) -> None:
        self.move_to((self.hero.getH()) % 360)

    def _left(self) -> None:
        self.move_to((self.hero.getH() + 270) % 360)

    def _right(self) -> None:
        self.move_to((self.hero.getH() + 90) % 360)

    def _switch_mode(self) -> None:
        self.mode = not self.mode

    def _try_move(self, angle: int) -> None:
        """перемещается, если может"""
        pos = self._look_at(angle)
        if self.land.is_empty(pos):
            # перед нами свободно. Возможно, надо упасть вниз:
            pos = self.land.find_highest_empty(pos)
            self.hero.setPos(pos)
        else:
            # перед нами занято. Если получится, заберёмся на этот блок:
            pos = pos[0], pos[1], pos[2] + 1
            if self.land.is_empty(pos):
                self.hero.setPos(pos)
                # не получится забраться - стоим на месте

    def _up(self) -> None:
        if self.mode:
            self.hero.setZ(self.hero.getZ() + 1)

    def _down(self) -> None:
        if self.mode and self.hero.getZ() > 1:
            self.hero.setZ(self.hero.getZ() - 1)

    def _build(self) -> None:
        angle = self.hero.getH() % 180
        pos = self._look_at(angle)
        if self.mode:
            self.land.add_block(pos)
        else:
            self.land.build_block(pos)

    def _destroy(self) -> None:
        angle = self.hero.getH() % 180
        pos = self._look_at(angle)
        if self.mode:
            self.land.del_block(pos)
        else:
            self.land.del_block_from(pos)

    def _accept_events(self) -> None:
        base.accept(KEY_TURN_LEFT, self._turn_left)
        base.accept(KEY_TURN_LEFT + '-repeat', self._turn_left)
        base.accept(KEY_TURN_RIGHT, self._turn_right)
        base.accept(KEY_TURN_RIGHT + '-repeat', self._turn_right)

        base.accept(KEY_MOVE_BACK, self._forward)
        base.accept(KEY_MOVE_BACK + '-repeat', self._forward)
        base.accept(KEY_MOVE_FORWARD, self._back)
        base.accept(KEY_MOVE_FORWARD + '-repeat', self._back)
        base.accept(KEY_MOVE_LEFT, self._left)
        base.accept(KEY_MOVE_LEFT + '-repeat', self._left)
        base.accept(KEY_MOVE_RIGHT, self._right)
        base.accept(KEY_MOVE_RIGHT + '-repeat', self._right)

        base.accept(KEY_SWITCH_CAMERA, self._change_view)
        base.accept(KEY_SWITCH_MODE, self._switch_mode)

        base.accept(KEY_MOVE_UP, self._up)
        base.accept(KEY_MOVE_UP + '-repeat', self._up)
        base.accept(KEY_MOVE_DOWN, self._down)
        base.accept(KEY_MOVE_DOWN + '-repeat', self._down)

        base.accept(KEY_BUILD_BLOCK, self._build)
        base.accept(KEY_DESTROY_BLOCK, self._destroy)

        base.accept(KEY_SAVE_MAP, self.land.save_map)
        base.accept(KEY_LOAD_MAP, self.land.load_map)

    def move_to(self, angle: int) -> None:
        if self.mode:
            self._update_pos(angle)
        else:
            self._try_move(angle)
