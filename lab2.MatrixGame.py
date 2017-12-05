import numpy as np
import math
from itertools import product
from functools import reduce

def gen_mixed_strategy(size):
  _sum = 1.0
  avaliable_value = _sum
  strategy = [0.0] * size;
  for index in range(size - 1):
    current_value = np.random.random() * avaliable_value
    avaliable_value -= current_value
    strategy[index] = current_value
  strategy[-1] = _sum - sum(strategy)
  return strategy

def gen_row(size, max_value, ):
  _sum = 1.0
  avaliable_value = _sum
  strategy = [0.0] * size;
  for index in range(size - 1):
    current_value = np.random.random() * avaliable_value
    avaliable_value -= current_value
    strategy[index] = current_value
  strategy[-1] = _sum - sum(strategy)
  return strategy

def gen_strategies(sizes):
  return [np.array(gen_mixed_strategy(size)) for size in sizes]

def create_data(players_srategy_count):
   data = np.zeros(players_srategy_count)
   return data

def get_player_result(payment_matrix, selected_strategies, player_number=None):
   """
      Посчитаем выйгрыйш игрока player_number

      :param payment_matrix: матрица выплат
      :type payment_matrix: A x B x C ....
         A - стратегия, которую выбрал игрок 1
         B - стратегия, которую выбрал игрок 2
         ...

      :param selected_strategies: какую стратегию выбрал какой игрок
      :type selected_strategies: {tuple of int} or {list of int}. Размер = количество игроков
   """
   if isinstance(selected_strategies, tuple):
      selected_strategies = list(selected_strategies)
   selected_strategies = tuple(selected_strategies[::-1])
   if player_number is not None:

      index = tuple([player_number]) + selected_strategies
      return payment_matrix[index]
   return sum(payment_player[selected_strategies] for payment_player in payment_matrix)

def reform_paleyr_strategy(strategies):
   """
      Преобразуем массив шансов стратегий в их перебор

      :param strategies:
      :type strategies: [
         [0.5, 0.5],
         [0.33, 0.33, 0.34]
      ]
      :return: dict {
            (strategY_indexes) : (strategy_chances)
            (0, 0) : (0.5, 0.33)
            (0, 1) : (0.5, 0.33)
            (0, 2) : (0.5, 0.34)
            ...
         }
      :rtype:
   """
   strategy_indexes = list(product(*[[strategy_index for strategy_index in range(len(chances_player))]
         for chances_player in strategies]))
   strategy_chances = list(product(*strategies))
   return dict(zip(strategy_indexes, strategy_chances))


def count_mixed_result(payment_matrix, strategies, player_number=None):
   """
      Рассчитаем результат игры в смешанных стратегиях
   """
   result = []
   for strategy_indexes, chances in reform_paleyr_strategy(strategies).items():
      total_chance = reduce(lambda res, x: res*x, chances, 1)
      if player_number is not None:
         result.append(get_player_result(payment_matrix, strategy_indexes, player_number) * total_chance)
         continue
      for player in range(len(chances)):
         result.append(get_player_result(payment_matrix, strategy_indexes, player) * total_chance)
   return sum(result)

def get_best_strategy_for_player(payment_matrix, strategies, player_number):
   """
      Рассчитаем лучшую стратегию для игрока {player_number} при фиксированных вероятностях выбора стретегий
   """
   result = {}
   temp_strategies = strategies[:player_number] + [np.zeros(len(strategies[player_number])) + 1] + strategies[player_number + 1:]
   for strategy_indexes, chances in reform_paleyr_strategy(temp_strategies).items():
      total_chance = reduce(lambda res, x: res*x, chances, 1)
      result.setdefault(strategy_indexes[player_number], []).append(
         get_player_result(payment_matrix, strategy_indexes, player_number) * total_chance
      )
   best_strategy = max(result.items(), key=lambda item: sum(item[1]))[0]
   return best_strategy

def get_best_strategies(payment_matrix, strategies):
   """
      Получим набор стратегий к которому стремятся игроки
   """
   new_strategies = []
   for player_number in range(len(payment_matrix)):
      best_strategy_index = get_best_strategy_for_player(payment_matrix, strategies, player_number)
      chances = np.zeros(len(strategies[player_number]))
      chances[best_strategy_index] = 1.0
      new_strategies.append(chances)
   return new_strategies

def get_next_step(source_strategies, target_strategies, step=0.01, log=False):
   vectors = []
   max_value = 1.0
   for player_number in range(len(source_strategies)):
      source_strategy = source_strategies[player_number]
      target_strategy = target_strategies[player_number]
      vector = target_strategy - source_strategy
      _max = max(vector)
      _min = min(vector)
      for idx, value in enumerate(vector):
         if value != _min and value != _max:
            vector[idx] = 0.0
         elif value == _min:
            vector[idx] = -_max
      avaliable_step = max_value - sum(source_strategy[target_strategy > 0])
      current_step = avaliable_step if avaliable_step < step else step
      vector[vector < 0] /= -sum(vector[vector < 0])
      vector[vector > 0] /= sum(vector[vector > 0])
      vector = vector * current_step
      vectors.append(vector)
      if log:
         print("==========")
         print("player: {}".format(player_number))
         print("source: {} -> target: {}".format(source_strategy, target_strategy))
         print("vector: {}".format(vector))
         print("sum positive: {}".format(sum(source_strategy[target_strategy > 0])))
         print("avaliable_step: {}".format(avaliable_step))
         print("current_step: {}".format(current_step))
   new_strategies = []
   for source_strategy, vector in zip(source_strategies, vectors):
      new_strategies.append(source_strategy + vector)
   return new_strategies

def process(payment_matrix, start_strategies, log=False, step=0.01, search_max=True):
  strategies = start_strategies
  history = []
  i = 0
  if log:
    print(strategies)
  while check_end(payment_matrix, strategies, history, False) and i < 10000:
    i += 1
    if log:
      print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
      print("step: {}; sum: {}".format(i, count_mixed_result(payment_matrix, strategies)))
      for player_number in range(len(strategies)):
        print("player: {}; sum: {}".format(player_number, count_mixed_result(payment_matrix, strategies, player_number)))
    target_strategies = get_best_strategies(payment_matrix, strategies)
    strategies = get_next_step(strategies, target_strategies, step=step, log=log)
    # print((count_mixed_result(payment_matrix, strategies, 1), strategies[0]))
    if log:
      print("++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
  return get_best_result(history)



def check_end(payment_matrix, strategies, history, search_max=True):
  current_value = {}
  better_result = False
  last_values = []
  last_values_count = 200
  if len(history) > last_values_count:
    last_values = history[-last_values_count:]
  else:
    better_result = True
  for player_number in range(len(strategies)):
    player_result = count_mixed_result(payment_matrix, strategies, player_number);
    current_value[player_number] = player_result
    if search_max:
      if last_values and math.fabs(player_result) > min(math.fabs(value.get(player_number)) for value in last_values):
        better_result = True
      if last_values and math.fabs(player_result) > math.fabs(last_values[-1].get(player_number)):
        current_value['best'] = True
    else:
      if last_values and math.fabs(player_result) < max(math.fabs(value.get(player_number)) for value in last_values):
        better_result = True
      if last_values and math.fabs(player_result) < math.fabs(last_values[-1].get(player_number)):
        current_value['best'] = True
  current_value['total'] = count_mixed_result(payment_matrix, strategies)
  current_value['strategies'] = strategies
  current_value['index'] = len(history)
  history.append(current_value)
  #print(current_value['total'])
  return better_result

def get_best_result(history):
  for value in reversed(history):
    if 'best' in value:
      return value
  return history[-1]

# print(create_data((3, 2)))
# Допустим у первого игрока 2 стратегии
# У второго 3 стратегии
(3, 1) # второй игрок выбирает 1-ю стратегию
(2, 3) # второй игрок выбирает 2-ю стратегию
(2, 1) # второй игрок выбирает 3-ю стратегию

(3, 1, 2) # первый игрок выбирает 1-ю стратегию
(1, 2, 2) # первый игрок выбирает 2-ю стратегию

# payment_matrix = np.array([
# [[3, 1], [2, 3], [2, 1]],
# [[3, 1], [1, 2], [2, 2]]
# ])
# strategies = [
#   np.array([0.3, 0.7]), # веротности выбора стратегий первым игроком
#   np.array([0.1, 0.56, 0.34]) # вероятности выбора стратегий вторым игроком
# ]
# strategies = gen_strategies([2, 3])

# крестики-нолики
payment_matrix = np.array([
  [[0, -1, 1], [1, 0, -1], [-1, 1, 0]],
  [[0, 1, -1], [-1, 0, 1], [1, -1, 0]]
])
strategies = [
  np.array([0.3, 0.3, 0.4]), # веротности выбора стратегий первым игроком
  np.array([0.1, 0.56, 0.34]) # вероятности выбора стратегий вторым игроком
]
strategies = gen_strategies([3, 3])

# Дилема заключённых
# payment_matrix = np.array([
#   [[-1,-4], [-4,-10]],
#   [[-1,-4], [-4,-10]],
# ])

# strategies = [
#   np.array([0.5, 0.5]), # веротности выбора стратегий первым игроком
#   np.array([0.5, 0.5]) # вероятности выбора стратегий вторым игроком
# ]
# strategies = gen_strategies([2, 2])

# print(count_mixed_result(payment, strategies))
#steps = [0.1, 0.01, 0.001, 0.0001]
steps = [0.01]
search_max_values = [True]
for step, search_max in product(steps, search_max_values):
  print("+++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++")
  print(strategies)
  print("step: {}; search_max: {}".format(step, search_max))
  print(process(payment_matrix, strategies, log=False, step=step, search_max=search_max))
#print(get_player_result(payment_matrix, [0, 1], 0))