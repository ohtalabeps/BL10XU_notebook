"""
段階的なレーザー加熱をするときの，レーザーエネルギー変化をプロットするmodule
"""

import matplotlib.pyplot as plt
import numpy as np


class LaserProfile():
    def __init__(self):
        """
        (Laser linear controlの画面を参照している)
        """
        self.linear = False
        self.delay_ms = 1_000
        self.time_adjust_ms = 100
        self.power_W = None
        self.base_width_ms = None
        self.whole_time_ms = None # plotの終わり時間を決める
        self.laser_diameter_um = None
        if self.linear: # 線形加熱の場合
            self.start_power_W = None
            self.goal_power_W = None
            self.step_width_ms = None
            self.linear_width_ms = None

    def set_from_json(self, json):
        # TODO
        pass

    def get_laser_profile_arr(self):
        if self.linear: # 線形加熱の場合
            print(" -- linear 加熱 --")
        else: # 定常加熱の場合
            print(" -- burst 加熱 --")
        self._compute_time_arr()
        self._compute_power_arr()


    def _compute_time_arr(self):
        # 線形加熱の場合
        if self.linear:
            if self.linear_width_ms == self.base_width_ms:
                step_num = round(self.linear_width_ms / self.step_width_ms)
                time_list = [
                    0,
                    self.delay_ms + self.time_adjust_ms,
                    self.delay_ms + self.time_adjust_ms
                ]
                for i in range(step_num):
                    ele = time_list[-1] + self.step_width_ms # 時間を進める
                    time_list.append(ele) # 追加
                    time_list.append(ele) # レーザー出力のみ上がる
                time_list.append(time_list[-1]) # クエンチ
                time_list.append(self.whole_time_ms) # 最後
            elif self.linear_width_ms < self.base_width_ms:
                step_num = round(self.linear_width_ms / self.step_width_ms)
                time_list = [
                    0,
                    self.delay_ms + self.time_adjust_ms,
                    self.delay_ms + self.time_adjust_ms
                ]
                for i in range(step_num):
                    ele = time_list[-1] + self.step_width_ms # 時間を進める
                    time_list.append(ele) # 追加
                    time_list.append(ele) # レーザー出力のみ上がる
                time_list.append(self.delay_ms + self.time_adjust_ms + self.base_width_ms) # ここまで保つ
                time_list.append(time_list[-1]) # クエンチ
                time_list.append(self.whole_time_ms) # 最後
            else:
                raise Exception("線形加熱のwidthが長い場合は実装されていません。実装してください。")
        # 定常加熱の場合
        else:
            time_list = [
                0, # 1点目
                self.delay_ms + self.time_adjust_ms,
                self.delay_ms + self.time_adjust_ms,
                self.delay_ms + self.time_adjust_ms + self.base_width_ms,
                self.delay_ms + self.time_adjust_ms + self.base_width_ms,
                self.whole_time_ms # 最後
            ]
        time_arr = np.array(time_list)
        self.time_arr = time_arr / 1_000 # ms -> s
        print("\t時間計算終わり")

    def _compute_power_arr(self):
        # 線形加熱の場合
        if self.linear:
            if self.linear_width_ms == self.base_width_ms:
                step_num = round(self.linear_width_ms / self.step_width_ms)
                power_step = (self.goal_power_W - self.start_power_W) / step_num
                power_list = [
                    0,
                    0,
                    self.start_power_W
                ]
                for i in range(step_num):
                    ele = power_list[-1]
                    power_list.append(ele) # 時間のみ進む
                    power_list.append(ele + power_step) # エネルギー上がる
                power_list.append(0) # クエンチ
                power_list.append(0) # 最後
            elif self.linear_width_ms < self.base_width_ms:
                step_num = round(self.linear_width_ms / self.step_width_ms)
                power_step = (self.goal_power_W - self.start_power_W) / step_num
                power_list = [
                    0,
                    0,
                    self.start_power_W
                ]
                for i in range(step_num):
                    ele = power_list[-1]
                    power_list.append(ele) # 時間のみ進む
                    power_list.append(ele + power_step) # エネルギー上がる
                power_list.append(power_list[-1]) # 最後のエネルギーを保つ
                power_list.append(0) # クエンチ
                power_list.append(0) # 最後
            else:
                raise Exception("線形加熱のwidthが長い場合は実装されていません。実装してください。")
        # 定常加熱の場合
        else:
            power_list = [
                0, # 1点目
                0,
                self.power_W,
                self.power_W,
                0,
                0 # 最後
            ]
        power_arr = np.array(power_list)
        self.power_arr = power_arr
        print("\tエネルギー計算終わり")


if __name__ == "__main__":
    print(" --------------------------------")
    print("|    Develop: Laser profile Plot   |")
    print(" --------------------------------\n")

    laser_profile = LaserProfile()
    breakpoint()
else:
    print(f"{__name__: <30} is imported")

