"""
nxsとponiを読み込んで，cakingされたデータを読み出す
"""
import matplotlib.pyplot as plt
import seaborn as sns

import numpy as np
import pandas as pd
from tqdm import tqdm
import time

import h5py
from pyFAI.azimuthalIntegrator import AzimuthalIntegrator


class NxsFile:
    def __init__(self, filepath=None):
        if filepath is None:
            print("hoge")
            # self.filepath_dist = get_files(root)
            # logger.info(f"ファイル: {self.filepath_dist}")
        else:
            self.filepath = filepath
            print(f"Load: {self.filepath}")

    """poniファイルの設定"""
    def set_poni(self, *, poni_path=None):
        if poni_path is None:
            raise ValueError("poni_path must be set.")
        else:
            self.poni_path = poni_path
            print(f"Set: {self.poni_path}")
            ai = AzimuthalIntegrator()
            ai.load(self.poni_path)
            print(f"\n{ai}\n")
            self.ai = ai

    def rotate_poni_m90(self):
        # PONI1とPONI2を交換
        self.ai.poni1, self.ai.poni2 = self.ai.poni2, self.ai.poni1
        # rot1とrot2を交換し、符号を調整
        self.ai.rot1, self.ai.rot2 = self.ai.rot2, -self.ai.rot1

    def adjust_poni(self, *, scale: dict): # 本当はこれは使わないでやりたい
        if "poni1_scale" in scale:
            self.ai.poni1 *= scale["poni1_scale"]
        if "poni2_scale" in scale:
            self.ai.poni2 *= scale["poni2_scale"]
        if "rot1_scale" in scale:
            self.ai.rot1 *= scale["rot1_scale"]
        if "rot2_scale" in scale:
            self.ai.rot2 *= scale["rot2_scale"]
        if "rot3_scale" in scale:
            self.ai.rot3 *= scale["rot3_scale"]
        print(f"\n{scale}\n{self.ai}")


    """nxsファイル"""
    def read_file(self):
        self.data_file = h5py.File(self.filepath, "r")

    def show_data_path(self):
        print('hoge')

    def get_data(self, rotation=False):
        print("データを読み込み中...")
        t1 = time.time()

        self.dataset = self.data_file.get('/entry/instrument/detector/data')
        tmp_data = self.dataset[:] # NOTE dioptasのLambdaLoaderの読み込みと反転になっていたので、反転してる
        self.data = tmp_data[:, ::-1, :] # ここで反転。https://github.com/Dioptas/Dioptas/blob/5dff77dd0c4d3987f24c967a930b46166b069613/dioptas/model/loader/LambdaLoader.py
        self.exposure_ms = self.data_file.get('/entry/instrument/detector/count_time')[0] # NOTE 多分msの露光時間だと思うが，他の露光時間のファイルを見てないから断定できてない
        self.framerate_sec = 1000.0 / self.exposure_ms
        self.filename = self.data_file.get('/entry/instrument/detector/collection/save_file_name')[0].__str__()[2:-7]
        del self.data_file
        del self.dataset

        self.frame_num = self.data.shape[0]
        self.x_pixel = self.data.shape[1]
        self.y_pixel = self.data.shape[2]
        # 1frame目が飛んでいる時用の処理
        # 他で適用しても問題ないのでいつもやる
        if self.frame_num > 1:
            self.data[0,:,:] = self.data[1,:,:] * 1
        # 回転させる必要があるデータで-90degする
        # NOTE poniを回転させることにしたので使わない
        if rotation:
            print("    rotation = True")
            self.data = np.rot90(self.data, k=-1, axes=(1,2))

        t2 = time.time()
        print(f"完了 --- かかった時間{round(t2-t1)} s")

    def set_cake_data(self, npt_rad=1000, npt_azim=360):
        cake = []

        for i in tqdm(range(self.frame_num)):
            I, tth, azi = self.ai.integrate2d(self.data[i,:,:],
                                              npt_rad=npt_rad, # NOTE これはintegrate_1dと揃える
                                              npt_azim=npt_azim,
                                              unit="2th_deg")
            cake.append(I)

        self.cake = np.array(cake)
        self.tth = tth
        self.azi = azi
        del cake

    def set_1d_pattern_data(self, npt_rad=1000):
        I = []
        for i in tqdm(range(self.frame_num)):
            tth, I_1d = self.ai.integrate1d(self.data[i,:,:],
                                            npt=npt_rad,
                                            unit="2th_deg")
            I.append(I_1d)
        self.tth = np.array(tth)
        self.I = np.array(I)
        del I

    def plot_cake(self):
        fig = plot_heatmap(self.cake[0])
        plt.show(block=False)
        plt.pause(.01)
        

    def plot_frame(self, *, frame_num: int):
        option = {
            # tuple
            # 'figsize': tuple,
            # int
            # 'dpi': int,
            # str
            # 'fig_title': str,
            # 'ax_title': str,
            # 'facecolor': str or tuple(R, G, B, Alpha),
            'cmap': "jet",
            # 'xlabel': str,
            # 'ylabel': str,
            # boolean
            'show'  : True
        }
        fig = plot_heatmap(self.data[frame_num,:,:], option=option)
        return fig


# 注意: クラスメソッドじゃない
def print_hdf5_hierarchy(g, indent=0):
    for key in g.keys():
        print(" " * indent + "/" + key)  # グループ名を出力
        if isinstance(g[key], h5py.Group): # もしkey先がgroupの場合
            print_hdf5_hierarchy(g[key], indent + 4)  # グループ内のさらに深い階層を出力

def plot_heatmap(data, *,
                 option: dict = {}): # NOTE これは単体試験用に置いてるだけ。本体では使わない

    # option.get(キー，無い場合の初期値)
    figsize = option.get('figsize', (5,5))
    facecolor = option.get('facecolor', 'white')
    dpi = option.get('dpi', 150)
    cmap = option.get('cmap', 'viridis')
    xlabel = option.get('xlabel', 'x')
    ylabel = option.get('ylabel', 'y')
    show = option.get('show', True)

    # Figureを作る
    fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=facecolor)
    ax = fig.add_subplot(1, 1, 1)

    if 'fig_title' in option:
        title = option.get('fig_title', 'hoge') # 初期値hogeを使うようなユースケースは考えづらいのでhogeにしてる
        fig.suptitle(title)
    # TODO
    # ax_titleは複数になる場合がある。現在はsubplotが111のみなので不要だが，subplotが増えたら拡張する。
    # ex) axオブジェクトの種類数に対応する。ax1 ~ ax3なら，ax_titleは3つまでつけられる。
    if 'ax_title' in option:
        title = option.get('ax_title', 'hoge') # 初期値hogeを使うようなユースケースは考えづらいのでhogeにしてる
        ax.set_title(title)

    sns.heatmap(data, cmap=cmap)
    
    ax.set_xlabel(xlabel)
    ax.set_ylabel(ylabel)

    if show: plt.show(block=False)
    plt.pause(.01)

    return fig, ax


def get_files(root, mult=False):
    """
    Uses tkinter to allow UI source file selection
    Adapted from: http://stackoverflow.com/a/7090747
    """
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    filepaths = fdialog.askopenfilenames()
    if not mult:
        filepaths = filepaths[0]
    return filepaths

def main():
    filepath1 = "/Users/ishizawaosamu/work/python/module/test_data/nxs_test_data/OIpD03__5_00000.nxs"
    poni_path1 = "/Users/ishizawaosamu/work/python/module/test_data/nxs_test_data/Dioptas_lambda_MgS400_CeO2_240208.poni"

    filepath2 = "/Users/ishizawaosamu/work/python/module/test_data/nxs_test_data/OIbDia06_3_00000.nxs"
    poni_path2 = "/Users/ishizawaosamu/work/python/module/test_data/nxs_test_data/Dioptas_lambda_MgS400_CeO2_231102.poni"

    filepath3 = "/Users/ishizawaosamu/work/python/module/test_data/nxs_test_data/OIMgO05_5_00000.nxs"
    poni_path3 = "/Users/ishizawaosamu/work/python/module/test_data/nxs_test_data/Dioptas_lambda_MgS235_CeO2_221105.poni"

    filepath4 = "/Users/ishizawaosamu/work/python/module/test_data/nxs_test_data/CeO2_lambda_MgS235_1_00000.nxs"
    poni_path4 = "/Users/ishizawaosamu/work/python/module/test_data/nxs_test_data/lambda_MgS235_Dioptas_CeO2.poni"

    nxs = NxsFile(filepath2)
    nxs.read_file()
    nxs.get_poni(poni_path2)
    nxs.set_poni()
    # print_hdf5_hierarchy(nxs.data_file)
    nxs.get_data()
    nxs.plot_frame(frame_num=0)
    nxs.cake_data()
    nxs.plot_cake()
    nxs.plot_integrate1d_data()
    breakpoint()

if __name__ == "__main__":
    import trace
    import sys
    # トレース用の設定を作成
    # tracer = trace.Trace(
    #     ignoredirs=[sys.prefix, sys.exec_prefix],
    #     trace=1,
    #     count=1
    #     # outfile="trace.txt"
    # )
    # 
    # # トレースを開始
    # tracer.run('main()')
    # 
    # # トレースの結果をレポート
    # r = tracer.results()
    # r.write_results(summary=True, coverdir="trace")

    main()
else:
    # from Util.log import logger
    # from Util.log import log_info

    print(f"{__name__: <30} is imported")
