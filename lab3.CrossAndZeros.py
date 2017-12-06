
def set_value(field, row, col, value):
   return field | value << 2 * size * size - 2 - 2 * row * size - 2 * col

def get_value(field, row, col):
   return (field >> 2 * size * size - 2 - 2 * row * size - 2 * col) & 3

def print_binary(value):
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
   for win_cross_field in win_crosses:
      if field & win_cross_field == win_cross_field:
         return cross
   for win_zero_field in win_zeros:
      if field & win_zero_field == win_zero_field:
         return zero
   return 0

def gen_empty_field():
   return empty_field

def field_to_string(field):
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

def get_rotations(field):
   new_field = gen_empty_field()
   for row in range(size):
      for col in range(size):
         new_field = set_value(new_field, size - 1 - col, row, get_value(field, row, col))
   return new_field

def get_similars(field, with_current=False):

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
   avaliable_steps = 0

   who_wins = check_result(field)
   if who_wins == cross:
      tree[field] = (0., 1., 0.)
      return
   elif who_wins == zero:
      tree[field] = (0., 0., 1.)
      return

   for row in range(size):
      for col in range(size):
         if get_value(field, row, col) != 0:
            continue
         avaliable_steps += 1
         new_field = set_value(field, row, col, value)
         process(new_field, 3 - value)
         children.setdefault(field, []).append(new_field)

   if avaliable_steps == 0:
      tree[field] = (1., 0., 0.)
      return
   return

def count_results(field):
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

tree = {}
children = {}

process(empty_field, 1)
tree[empty_field] = count_results(empty_field)


f = gen_empty_field()
f = set_value(f, 2, 0, cross)
f = set_value(f, 1, 0, zero)
f = set_value(f, 2, 1, cross)
f = set_value(f, 2, 2, zero)
f = set_value(f, 1, 1, cross)
f = set_value(f, 0, 0, zero)
print_field(f)
