
def set_value(field, row, col, value):
   return field | value << 2 * size * size - 2 - 2 * row * size - 2 * col

def get_value(field, row, col):
   return (field >> 2 * size * size - 2 - 2 * row * size - 2 * col) & 3

def print_binary(value):
   """
      Выводи поле в двоичном представлении
   """
   str_value = '{:b}'.format(value)[1:]
   print(' '.join(str_value[index : index + 2 * size] for index in range(0, 2 * size * size, 2 * size)))

def gen_win_results(value):
   """
      Сгенерируем выйгрышные матрицы.
      1. Крест
      2. Каждый ряд
      3. Каждую колонку
   """
   results = [gen_empty_field()] * (2 + size * 2)

   for index in range(size):
      # Зададим крест
      results[0] = set_value(results[0], index, index, value)
      results[1] = set_value(results[1], size - 1 - index, index, value)
      # Зададим ряд
      for shift in range(size):
         results[2 + shift] = set_value(results[2 + shift], shift, index, value)
         results[2 + size + shift] = set_value(results[2 + size + shift], index, shift, value)
   return results

def check_result(field):
   """
      Проверка поля на конец игры
   """
   for win_cross_field in win_crosses:
   # Проверка, что выйграли крестики
      if field & win_cross_field == win_cross_field:
         return cross

   # Проверка, что выйграли нолики
   for win_zero_field in win_zeros:
      if field & win_zero_field == win_zero_field:
         return zero
   # Проверка, что ничья
   temp_field = field
   for _ in range(size * size):
      if (temp_field & 3) == 0:
         # Игра не окончена
         return None
      else:
         temp_field = temp_field >> 2
   # Ничья
   return 0

def gen_empty_field():
   return empty_field

def field_to_string(field):
   """
      Строкове представление поля. В Виде матрицы
   """
   crosses = "{:b}".format(field)[2::2]
   zeros = "{:b}".format(field)[1::2]
   str_value = ['_'] * (size * size)
   for index in range(size * size):
      if crosses[index] == '1':
         str_value[index] = 'X'
      elif zeros[index] == '1':
         str_value[index] = 'O'
   return '\n'.join(' '.join(str_value[index : index + size]) for index in range(0, size * size, size))

def print_field(field):
   """
      Печать поля в виде матрицы
   """
   print(field_to_string(field))

def get_reflection(field, length, double_reflection=False):
   """
      Получим отражения
   """
   part_mask = (1 << 2 * length) - 1
   part_shift = 2 * length
   new_field = 1
   temp_field = field
   for index in range(size):
      new_field = new_field << part_shift
      if double_reflection:
         new_field = new_field | (get_reflection(temp_field & part_mask, 1) & part_mask)
      else:
         new_field = new_field | (temp_field & part_mask)
      temp_field = (temp_field >> part_shift)
   return new_field

def get_similars(field, with_current=False):
   """
      Получим список похожих полей.
      Всевозмодные отражения и повороты.
   """
   reflections = [gen_empty_field()] * (8 if with_current else 7)

   if with_current:
      reflections[7] = field

   reflections[0] = get_reflection(field, size)
   reflections[1] = get_reflection(field, size, True)
   reflections[2] = get_reflection(reflections[0], size, True)

   # Сделаем поворот и зеркально отразим его 3 раза
   for row in range(size):
      for col in range(size):
         value = get_value(field, row, col)
         reflections[3] = set_value(reflections[3], col, row, value)

   reflections[4] = get_reflection(reflections[3], size, True)
   reflections[5] = get_reflection(reflections[3], size)
   reflections[6] = get_reflection(reflections[4], size)
   return reflections

def process(field, value=1):
   """
      Рекурсивно соберем дерево и получим рещультаты для листьев
   """
   avaliable_steps = 0
   # Если поле уже встречалось, то дальше идти не нужно
   if field in recents:
      return field

   # Если похожее поле уже встречалось, вернём его и дальше идти не нужно
   for similar_field in get_similars(field):
      if similar_field in recents:
         return similar_field

   # Если такого или похожего поля не было. То отметим, что было
   recents.add(field)

   # Проверка выйгрыша в листьях
   who_wins = check_result(field)
   if who_wins == cross:
      tree[field] = (0., 1., 0.)
      return field
   elif who_wins == zero:
      tree[field] = (0., 0., 1.)
      return field
   # Тут ничья
   elif who_wins == 0:
      tree[field] = (1., 0., 0.)
      return field

   for row in range(size):
      for col in range(size):
         if get_value(field, row, col) != 0:
            continue
         avaliable_steps += 1
         # Сделаем ход
         new_field = set_value(field, row, col, value)
         # Обработаем поле после хода
         new_field = process(new_field, 3 - value)
         # Добавим поле или похожее полее в детей
         children.setdefault(field, []).append(new_field)
   return field

def count_results(field):
   """
      Иерархически рассчитаем вероятности выйгрыша для всех состояний
   """
   child_list = children.get(field, [])
   children_total = len(child_list)

   draw_chance_list = []
   cross_chance_list = []
   zero_chance_list = []

   for child in child_list:
      if child in tree:
         draw_chance, cross_chance, zero_chance = tree[child]
      else:
         draw_chance, cross_chance, zero_chance = count_results(child)
         tree[child] = draw_chance, cross_chance, zero_chance
      draw_chance_list.append(draw_chance)
      cross_chance_list.append(cross_chance)
      zero_chance_list.append(zero_chance)
   return sum(draw_chance_list) / children_total, sum(cross_chance_list) / children_total, sum(zero_chance_list) / children_total

def get_best_move(field, player, log=False):
   """
      Определим лучший ход.
      1. Выберем все возможные следующие ходы (на 1 вперёд)
      2. Из всех выберем ход с максимальным шаносом выйгрыша для {player}
      3. Из всех выберем ход с минимальным шансом проигрыша для {player}
      4. Из всех выберем ход с максимальным шансом ничьи для {player}
      5. Выберем ход с максимальным шансом из п.2-4
   """
   child_list = []
   for similar_field in get_similars(field, True):
      if similar_field in children:
         child_list = children[similar_field]
         break;
   children_win_chance = []
   children_loss_chance = []
   children_draw_chance = []
   for child in child_list:
      for similar_child in get_similars(child, True):
         if similar_child in tree:
            children_win_chance.append((child, tree[similar_child][player]))
            children_loss_chance.append((child, tree[similar_child][3 - player]))
            children_draw_chance.append((child, tree[similar_child][0]))
            break;
   if log:
      for child, chance in children_win_chance:
         print(tree[child])
         print_field(child)
   if not children_win_chance:
      return None

   best_child, chance = max([
      max(children_win_chance, key=lambda t: t[1]),
      min(children_loss_chance, key=lambda t: t[1]),
      max(children_draw_chance, key=lambda t: t[1])
   ], key=lambda t: t[1])
   return best_child

def game(field, computer):
   print_field(field)
   result = None
   current_sign = cross
   while check_result(field) is None:
      if computer == current_sign:
         print("Мой ход:")
         field = get_best_move(field, computer)
         if field is None:
            print("Жизнь к такому меня не готовила...")
            break
         print_field(field)
      else:
         print("Ваш ход:")
         row = input('Введите строку: ')
         col = input('Введите колонку: ')
         if get_value(field, int(row), int(col)) == 0:
            field = set_value(field, int(row), int(col), 3 - computer)
         else:
            print("В клетке ({}, {}) у же есть значение".format(row, col))
            continue
         print(field)
         print_field(field)
      current_sign = 3 - current_sign
   else:
      result = check_result(field)
   if result == computer:
      print("Я победил!!!")
   elif result == (3 - computer):
      print("Вы победили(")
   else:
      print("К сожалению, у нас ничья.")

# 1 - 01 - cross
# 2 - 10 - zero
cross = 1
zero = 2

size = 3
empty_field = 1 << 2 * size * size
win_crosses = gen_win_results(cross)
win_zeros = gen_win_results(zero)


empty_field = gen_empty_field()
field_result = {}

recents = set()
tree = {}
children = {}

process(empty_field, cross)
tree[empty_field] = count_results(empty_field)

continue_game = True
computer_value = cross
while continue_game:
   computer_value = cross if int(input("Чем мне играть? (1 - Крестики / Другое - Нолики): ")) == 1 else zero
   game(gen_empty_field(), computer_value)
   continue_game = int(input("\nСыграем ещё? (1 - Да / Другое - Нет): ")) == 1

print("Спасибо за игру.")
