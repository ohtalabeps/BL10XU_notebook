"""
段階的なレーザー加熱をするときの，レーザーエネルギー変化をプロットするmodule
"""

import matplotlib.pyplot as plt
import numpy as np


# TODO
# 1. このモジュールを実行した時 -> 単体のfigureを返す
# 2. このモジュールが他で呼ばれた時(温度のところでなど) -> figが作ってる前提でaxを生成し，axオブジェクトを返す
#    fig or axを引数に渡して，それを返して貰えばいいのか。
# 2では温度にレーザーエネルギー変化を重ねてplotするイメージ
# となると2ではy軸を２つ作る必要があり，x軸を共有する必要がある
# TODO
# linearでなくバースト加熱の時にも対応できるようにしたい
# stepでそのままできるか。多分できなくて，フラグによる分岐が必要。

class LaserProfile():
    def __init__(self):
        """
        Linear加熱の時のinputパラメータ
        (Laser linear controlの画面を参照している)
        """
        # self.input_option = {
        #         "start_power-W"    : 10,
        #         "goal_power-W"     : 50,
        #         "delay-ms"         : 1000,
        #         "time_adjust-ms"   : 100,
        #         "width-ms"         : 8000,
        #         "step_width-ms"    : 100,
        #         "residue-ms"       : 1000,
        #         "laser_diameter-um": 17.5
        # }
        self.start_power = 10
        self.goal_power = 50
        self.delay = 1_000
        self.time_adjust = 100
        self.width = 8_000
        self.step_width = 100
        self.residue = 1_000
        self.laser_diameter = 17.5

    def get_plot_values(self):
        self.step_num = self.width / self.step_width # 何回エネルギーが変化するか
        # 最後は変化した瞬間に止まる(はず)なので，-1している
        self.energy_step = (self.goal_power - self.start_power) / self.step_num #(W), 一回あたりのエネルギー変化幅

        self.time_series = np.arange(
                self.delay, # start
                self.delay + self.width + 1, #end, endは含まないため+1している。ms単位なので最後が含まれるようになるだけ
                self.step_width # step
                )
        self.energy_series = np.arange(
                self.start_power,
                self.goal_power,
                self.energy_step
                )

        self.step_x = (self.time_series + self.time_adjust) / 1000 #time(s), ユニバーサル演算
        self.step_y = np.r_[np.zeros(1), self.energy_series] #Total Energy(W), 先頭に0を追加している。np.r_は1次元配列の結合

    def show_profile_plot(self) -> None:
        figsize = (4, 4)
        dpi = 200
        facecolor = 'white'
        
        fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=facecolor)
        ax = fig.add_subplot(1, 1, 1)
        
        color = 'red'
        # TODO delay + timeadjustをx1みたいな変数にする。説明で図示を使えるし，ax.plotの可読性も上がる
        # 1. line1
        ax.plot(
                [0, (self.delay + self.time_adjust) / 1000],
                [0, 0],
                color = color
                )
        # 2. step
        ax.step(
                self.step_x,
                self.step_y,
                where = 'pre',
                color = color
                # color = 'blue' # どこがstepで書かれているか知りたい時はこっちをコメントアウト
                )
        # 3. line2
        ax.plot(
                [(self.delay + self.time_adjust + self.width) / 1000, (self.delay + self.time_adjust + self.width) / 1000],
                [self.goal_power - self.energy_step, 0],
                color = color
                )
        # 4. line3
        ax.plot(
                [(self.delay + self.time_adjust + self.width) / 1000, (self.delay + self.width + self.residue) / 1000],
                [0, 0],
                color = color
                )
        ax.set_title('Laser Profile')
        ax.set_xlabel('Time (s)')
        ax.set_ylabel('Total Power (W)')
        ax.grid()# TODO ここのgridをoptionにする


    def overlap_laser_profile(self, ax) -> plt.axes:
        # 別のy軸で重ねる
        # TODO speの方かこっちのx軸を変更して重なるようにする
        twin = ax.twinx()
        color = 'red' # TODO これもoptionとして切り出す。plotオプション
        # TODO delay + timeadjustをx1みたいな変数にする。説明で図示を使えるし，ax.plotの可読性も上がる
        # TODO ax.plotの部分をDRYにする。クラス内に切り出して，showとoverlapからはaxを渡す。

        # 1. line1
        twin.plot(
                [0, (self.delay + self.time_adjust) / 1000],
                [0, 0],
                color = color
                )
        # 2. step
        twin.step(
                self.step_x,
                self.step_y,
                where = 'pre',
                color = color,
                label = 'Laser Power'
                # color = 'blue' # どこがstepで書かれているか知りたい時はこっちをコメントアウト
                )
        # 3. line2
        twin.plot(
                [(self.delay + self.time_adjust + self.width) / 1000, (self.delay + self.time_adjust + self.width) / 1000],
                [self.goal_power - self.energy_step, 0],
                color = color
                )
        # 4. line3
        twin.plot(
                [(self.delay + self.time_adjust + self.width) / 1000, (self.delay + self.width + self.residue) / 1000],
                [0, 0],
                color = color
                )
        #twin.grid()# TODO ここのgridをoptionにする
        twin.legend()

        twin.set_ylabel('Total Power (W)')
        return ax



if __name__ == "__main__":
    """
    想定: 
        このモジュールを実行したとき
    """
    print(" --------------------------------")
    print("|    Develop: Laser profile Plot   |")
    print(" --------------------------------\n")

    laser_profile = LaserProfile()
    breakpoint()
else:
    print(f"{__name__: <30} is imported")

