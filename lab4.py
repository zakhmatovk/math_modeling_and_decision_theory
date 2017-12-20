import numpy as np
import math
from itertools import product
from functools import reduce
from operator import mul

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
   new_strategies = {}
   for source_strategy, vector in zip(source_strategies.items(), vectors):
      key, value = source_strategy
      new_strategies[key] = value + vector

   return new_strategies


def get_target_strategies(buyer_result, seller_result, strategies, strategy_tree):
   traget_strategies = {}
   buyer = {}
   seller = {}
   for key, value in buyer_result.items():
      buyer.setdefault(key[0], {}).setdefault(key[2], []).append(value)

   buyer = dict((strategy_idx, max(data.items(), key=lambda x: sum(x[1]))[0])
                for strategy_idx, data in buyer.items())

   for key, value in seller_result.items():
      seller.setdefault(key[1], {}).setdefault(key[0], []).append(value)

   seller = dict((strategy_idx, max(data.items(), key=lambda x: sum(x[1]))[0])
                 for strategy_idx, data in seller.items())

   for idx, next_idx in seller.items():
      curr = strategy_tree[0][idx]
      strategy = np.zeros(len(strategies[curr]))
      strategy[strategy_tree[curr].index(next_idx)] = 1.0
      traget_strategies[curr] = strategy

   for key, strategy_idx in buyer.items():
      strategy = np.zeros(len(strategies[key]))
      strategy[strategy_idx] = 1.0
      traget_strategies[key] = strategy
   return traget_strategies

def play_game(payments, route, strategy_tree, strategies, step=0.01):
   result = {}
   for key, steps in route.items():
      result[key] = reduce(mul, (strategies[step][strategy_idx] for step, strategy_idx in steps))
   # print(result)
   total = []
   total_sum = []

   for payment in payments:
      total_temp = {}
      temp_sum = []
      for key, chance in result.items():
         for idx, strategy_chance in enumerate(strategies[key[0]]):
            _sum = payment[key][idx] * chance * strategy_chance
            total_temp[key + (idx,)] = _sum
            temp_sum.append(_sum)

      total.append(total_temp)
      total_sum.append(sum(temp_sum))
   target_strategies = get_target_strategies(total[1], total[0], strategies, strategy_tree)
   target_strategies[0] = strategies[0]
   return get_next_step(strategies, target_strategies, step, log=False), total_sum

def process(payments, route, strategy_tree, strategies, step=0.01):
   results = []
   strategy_history = []
   # for _ in range(1000):
   while check_end(results):
      strategies, result = play_game(payments, route, strategy_tree, strategies, step)
      print(result)
      results.append(result)
      strategy_history.append(strategies)
   print(strategy_history[-2])
   print(results[-2])


def check_end(results, delta=0.01):
   if len(results) < 3:
      return True
   curr = results[-1]
   prev = results[-2]
   for player_idx in range(len(curr)):
      if curr[player_idx] - prev[player_idx] > delta:
         return True
   return False

# strategies = gen_strategies([2, 2])

def __main__():
   chance_of_good_car = 0.5
   strategies = {
       # ([хорошая, плохая])
      0: np.array([chance_of_good_car, 1 - chance_of_good_car]),
      # ход продавца
      1: np.array([0.8, 0.2]), # хорошая машина у продавца; [высокая цена, низкая цена]
      2: np.array([0.75, 0.25]), # плохая машина у продавца; [высокая цена, низкая цена]
      # ход покупателя
      3: np.array([0.20, 0.8]),  # высокая цена [куплю, не куплю]
      4: np.array([0.25, 0.75])  # низкая цена [куплю, не куплю]
   }

   strategy_tree = {
      0: [1, 2],
      1: [3, 4],
      2: [3, 4]
   }
   route = {
      (3, 0): [(1, 0), (0, 0)],
      (3, 1): [(2, 0), (0, 1)],
      (4, 0): [(1, 1), (0, 0)],
      (4, 1): [(2, 1), (0, 1)]
   }


   good_car_price = 100
   bad_car_price = 50
   hight_price = 80
   low_price = 60

   buyer_payments = {
      (3, 0): [good_car_price - hight_price, 0], # 20
      (4, 0): [good_car_price - low_price, 0], # 40
      (3, 1): [bad_car_price - hight_price, 0], # -30
      (4, 1): [bad_car_price - low_price, 0] # -10
   }

   good_car_price = 50
   bad_car_price = 25
   hight_price = 100
   low_price = 50

   seller_payments = {
      (3, 0): [hight_price - good_car_price, -good_car_price], # 50; -50
      (4, 0): [low_price - good_car_price, -good_car_price], # 0, -50
      (3, 1): [hight_price - bad_car_price, -bad_car_price], # 75, -25
      (4, 1): [low_price - bad_car_price, -bad_car_price] # 25, -25
   }

   process([seller_payments, buyer_payments], route, strategy_tree, strategies, step=0.01)


__main__()
