from random import random

from io import StringIO
from gym import Env
from gym import spaces

import sys


class Actions:
    DRIVE_SLOW = 0
    DRIVE_FAST = 1
    DRIVE_LEFT = 2
    DRIVE_RIGHT = 3


class HighwayEnv(Env):
    metadata = {'render.modes': ['human', 'ansi']}

    reward_range = (-100, 10)

    def __init__(self,
                 drunk_column=None,
                 other_column=None,
                 rows=10,
                 cols=6,
                 reward_crash=-100,
                 reward_missed=1,
                 reward_success=10,
                 reward_safe=0,
                 pb_slow_left=0.1,
                 pb_slow_right=0.1,
                 pb_fast_left=0.2,
                 pb_fast_right=0.2):
        self.reward_crash = reward_crash
        self.reward_missed = reward_missed
        self.reward_success = reward_success
        self.reward_safe = reward_safe
        self.action_space = spaces.Discrete(4)
        self.observation_space = spaces.Discrete(rows*cols)

        self.pb_slow_left = pb_slow_left
        self.pb_slow_right = pb_slow_right
        self.pb_fast_left = pb_fast_left
        self.pb_fast_right = pb_fast_right

        self.rows = rows
        self.cols = cols
        self.drunk_column = drunk_column if drunk_column is not None else cols - 3
        self.other_column = other_column if other_column is not None else cols - 2
        self.drunk_position = [self.rows - 1, self.drunk_column]
        self.other_position = [self.rows - 1, self.other_column]

    def _step(self, action):
        self.__update_positions(action)
        return self.__get_reward()

    def _reset(self):
        self.drunk_position = [self.rows - 1, self.drunk_column]
        self.other_position = [self.rows - 1, self.other_column]
        return tuple(self.drunk_position)

    def _render(self, mode='human', close=False):
        if close:
            return

        outfile = StringIO() if mode == 'ansi' else sys.stdout

        for i in range(self.rows):
            outfile.write("|")
            for j in range(self.cols):
                if self.drunk_position == [i,j] and self.other_position == [i,j]:
                    outfile.write("C")
                elif self.other_position == [i,j]:
                    outfile.write("x")
                elif self.drunk_position == [i,j]:
                    outfile.write("X")
                else:
                    outfile.write(".")
            outfile.write("|")
            outfile.write("\n")

        return outfile

    def _seed(self, seed=None):
        pass

    def __update_positions(self, action):
        self.other_position[0] -= 1
        self.drunk_position[0] -= 1

        if action == Actions.DRIVE_LEFT:
            self.drunk_position[1] -= 1

        elif action == Actions.DRIVE_RIGHT:
            self.drunk_position[1] += 1

        elif action == Actions.DRIVE_SLOW:
            rnd = random()
            if rnd < self.pb_slow_left:
                self.drunk_position[1] -= 1
            elif rnd < self.pb_slow_left+self.pb_slow_right:
                self.drunk_position[1] += 1

        elif action == Actions.DRIVE_FAST:
            rnd = random()
            if rnd < self.pb_fast_left:
                self.drunk_position[1] -= 1
            elif rnd < self.pb_fast_left+self.pb_fast_right:
                self.drunk_position[1] += 1
            else:
                self.drunk_position[0] -= 1

    STATE_DEAD = -1
    STATE_MISSED = -2
    STATE_SUCCESS = -3

    def __get_reward(self):
        if self.other_position == self.drunk_position or \
                        self.drunk_position[1] < 0 or \
                        self.drunk_position[1] >= self.cols:
            return self.STATE_DEAD, self.reward_crash, True, None  # dead

        if self.drunk_position[0] < 0:
            return self.STATE_MISSED, self.reward_missed, True, None  # missed

        if self.drunk_position == [0, self.cols-1]:
            return self.STATE_SUCCESS, self.reward_success, True, None  # success!

        safe_reward = 0
        if abs(self.other_position[0]-self.drunk_position[0]) >= 1 and \
                        abs(self.other_position[0]-self.drunk_position[0]) >= 1:
            safe_reward = self.reward_safe

        return tuple(self.drunk_position), safe_reward, False, None  # just driving

