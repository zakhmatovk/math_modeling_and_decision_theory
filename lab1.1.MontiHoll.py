import numpy as np
import matplotlib.pyplot as plt

class MontiHoll:
    """
        Класс эмулирует задачу Монти-Холла
    """
    def __init__(self, door_total, car_total):
        self._door_total = door_total
        self._car_total = car_total
        self._opened_doors = set()
        self._wrong_doors = set()
        self._right_doors = set()
        self._doors = list()

    @staticmethod
    def _create_doors(door_total, car_total):
        """
            Создадим массив дверей длины {door_total}, где 0 - козёл, а 1 - машина.
            Где гарантировано будет {cat_total} машин
            :return: упорядоченный массив содержимого дверей, набор индексов неверных дверей, набор индексов верных дверей
            :rtype: (list, set, set)
        """
        doors = [0] * door_total
        wrong_door_indexes = list(range(door_total))
        right_door_indexes = []
        for _ in range(car_total):
            car_position = MontiHoll._get_random_value_from_list(wrong_door_indexes)
            wrong_door_indexes.remove(car_position)
            right_door_indexes.append(car_position)
            doors[car_position] = 1
        return doors, set(wrong_door_indexes), set(right_door_indexes)
    
    @staticmethod
    def _get_random_value_from_list(lst):
        """
            Получим рандомный элемент из массива
        """
        return lst[np.random.randint(len(lst))]

    def _open_door(self, exactly_wrong=False):
        """
           Откроем рандомную дверь. exactly_wrong == True - гарантировано неверную(без машины)
        """
        if exactly_wrong:
            # выберем все не открытие неправильные двери
            avaliable_doors = list(self._wrong_doors ^ (self._wrong_doors & self._opened_doors))
        else:
            avaliable_doors = set(range(len(self._doors)))
            avaliable_doors = list(avaliable_doors ^ (avaliable_doors & self._opened_doors))
        door_index = MontiHoll._get_random_value_from_list(avaliable_doors)
        return door_index

    def _reset_data(self):
        self._opened_doors = set()
        self._doors, self._wrong_doors, self._right_doors = MontiHoll._create_doors(self._door_total, self._car_total)

    def process(self):
        """
            Производим игру. 
            1. Сбросим данные
            2. Игрок выбирает дверь
            3. Ведущий открывает дверь
            4. Игрок выбирает новую дверь
            5. Проверяем обе двери игрока
        """
        self._reset_data()
        
        # игрок выбирает дверь
        user_door = self._open_door()
        self._opened_doors.add(user_door)
        # ведущий открывает дверь
        host_door = self._open_door(exactly_wrong=True)
        self._opened_doors.add(host_door)
        # игрок выбирает новую дверь
        new_user_door = self._open_door()
        self._opened_doors.add(new_user_door)

        is_win = self._doors[user_door]
        is_switch_win = self._doors[new_user_door]
        return is_win, is_switch_win

params = []
door_total = 10
for door_idx in range(door_total - 2):
    params.append((door_total - door_idx, 1, 10000))
result_titles = []
result_is_win = []
result_is_switch_win = []
for param in params:
    doors_total, car_total, repeats = param
    monti_holl = MontiHoll(doors_total, car_total)
    is_win_total = 0
    is_switch_win_total = 0
    for _ in range(repeats):
        is_win, is_switch_win = monti_holl.process()
        is_win_total += is_win
        is_switch_win_total += is_switch_win
    title = doors_total
    result_titles.append(title)
    result_is_win.append(is_win_total/repeats)
    result_is_switch_win.append(is_switch_win_total/repeats)

plt.plot(result_titles, result_is_win, 'ro')
plt.plot(result_titles, result_is_switch_win, 'bo')
plt.show()
