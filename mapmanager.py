import pickle

from conf import PATH_BASE_BLOCK, PATH_BASE_TEXTURE, PATH_MAP


class Mapmanager:
    """ Управление картой """

    def __init__(self) -> None:
        self.model = PATH_BASE_BLOCK  # модель кубика
        # текстура блока
        self.texture = PATH_BASE_TEXTURE
        self.colors = [
            (0.2, 0.2, 0.35, 1),
            (0.2, 0.5, 0.2, 1),
            (0.7, 0.2, 0.2, 1),
            (0.5, 0.3, 0.0, 1)
        ]  # цвет в формате RGBA
        # создаём основу для новой карты
        self.land = render.attachNewNode("Land")  # узел, к которому привязаны все блоки карты

    def _get_color(self, z):
        if z < len(self.colors):
            return self.colors[z]
        else:
            return self.colors[len(self.colors) - 1]

    def _find_blocks(self, pos):
        return self.land.findAllMatches("=at=" + str(pos))

    def _clear(self):
        """обнуляет карту"""
        self.land.removeNode()
        self.land = render.attachNewNode("Land")

    def add_block(self, position):
        # создаём строительные блоки
        block = loader.loadModel(self.model)
        block.setTexture(loader.loadTexture(self.texture))
        block.setPos(position)
        color = self._get_color(int(position[2]))
        block.setColor(color)
        block.setTag("at", str(position))
        block.reparentTo(self.land)

    def load_land(self, filename):
        """создаёт карту земли из текстового файла, возвращает её размеры"""
        self._clear()
        with open(filename) as file:
            y = 0
            for line in file:
                x = 0
                line = line.split(' ')
                for z in line:
                    for z0 in range(int(z) + 1):
                        self.add_block((x, y, z0))
                    x += 1
                y += 1
        return x, y

    def is_empty(self, pos) -> bool:
        if self._find_blocks(pos):
            return False
        else:
            return True

    def find_highest_empty(self, pos):
        x, y, z = pos
        z = 1
        while not self.is_empty((x, y, z)):
            z += 1
        return x, y, z

    def build_block(self, pos):
        """Ставим блок с учётом гравитации: """
        x, y, z = pos
        new = self.find_highest_empty(pos)
        if new[2] <= z + 1:
            self.add_block(new)

    def del_block(self, position):
        """удаляет блоки в указанной позиции """
        blocks = self._find_blocks(position)
        for block in blocks:
            block.removeNode()

    def del_block_from(self, position):
        x, y, z = self.find_highest_empty(position)
        pos = x, y, z - 1
        for block in self._find_blocks(pos):
            block.removeNode()

    def save_map(self):
        """сохраняет все блоки, включая постройки, в бинарный файл"""

        # возвращает коллекцию NodePath для всех существующих в карте мира блоков
        blocks = self.land.getChildren()
        # открываем бинарный файл на запись
        with open(PATH_MAP, 'wb') as fout:
            # сохраняем в начало файла количество блоков
            pickle.dump(len(blocks), fout)

            # обходим все блоки
            for block in blocks:
                # сохраняем позицию
                x, y, z = block.getPos()
                pos = (int(x), int(y), int(z))
                pickle.dump(pos, fout)

    def load_map(self):
        # удаляем все блоки
        self._clear()

        # открываем бинарный файл на чтение
        with open(PATH_MAP, 'rb') as fin:
            # считываем количество блоков
            length = pickle.load(fin)

            for i in range(length):
                # считываем позицию
                pos = pickle.load(fin)

                # создаём новый блок
                self.add_block(pos)
