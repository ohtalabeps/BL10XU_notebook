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

    def get_data(self, rotation=False): # これあとで消す
        print("データを読み込み中...")
        t1 = time.time()

        self.dataset = self.data_file.get('/entry/instrument/detector/data')
        tmp_data = self.dataset[:] # NOTE dioptasのLambdaLoaderの読み込みと反転になっていたので、反転してる
        self.data = tmp_data[:, ::-1, :] # ここで反転。https://github.com/Dioptas/Dioptas/blob/5dff77dd0c4d3987f24c967a930b46166b069613/dioptas/model/loader/LambdaLoader.py
        self.exposure_ms = self.data_file.get('/entry/instrument/detector/count_time')[0]
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






if __name__ != "__main__":
    print(f"{__name__: <30} is imported")
