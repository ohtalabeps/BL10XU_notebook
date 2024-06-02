"""
FPDで撮った.hisファイルの読み込み
"""

import tkinter as tk
from tkinter import filedialog as fdialog

import numpy as np
import struct # バイナリデータ解析用
import pandas as pd

import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import os

"""自作plotモジュールの取り込み"""
from Util.plot import plot_xy, plot_heatmap, save_fig
from Util.log import log_debug, log_info, logger_info

@log_info
def get_files(mult=False):
    """
    Uses tkinter to allow UI source file selection
    Adapted from: http://stackoverflow.com/a/7090747
    """
    root = tk.Tk()
    root.withdraw()
    root.overrideredirect(True)
    root.geometry('0x0+0+0')
    root.deiconify()
    root.lift()
    root.focus_force()
    filepaths = fdialog.askopenfilenames()
    if not mult:
        filepaths = filepaths[0]
    root.destroy()
    print(filepaths)
    return filepaths

def load(filepaths=None):
    """
    今の仕様だと，
    load自体は複数ファイルを一括でできる
    speだと，その場合speオブジェクトの中でリストとして保存されるみたい
    """
    if filepaths is None: #この分岐はFpdFileの__init__処理と重複してる
        filepaths = get_files()

class FpdFile(object):
    def __init__(self, filepath=None):

        #TODO
        # 他のクラスでも同じことやるので，便利モジュールにここら辺の処理まとめてもいい。
        # そうすれば今の擬似tkinterでのファイル取得から変えたい時，一括で変えられる
        if filepath is None:
            self.filepath = load()
        else:
            self.filepath = filepath
        self.filename = os.path.splitext(os.path.basename(self.filepath))[0]



def read_his_file(file_path):
    try:
        with open(file_path, 'rb') as file:
            # バイナリデータを読み込む
            data = file.read()

            # バイナリデータを解析する
            ID, headerSize, headerVersion, fileSize, imageHeaderSize, ULX, ULY, BRX, BRY, numberOfFrame, correction, frameTimeInMicroseconds, frameTimeInMilliseconds = struct.unpack('<HHHLHHHHHHHdH', data[:34])
            imageWidth = BRX - ULX + 1
            imageHeight = BRY - ULY + 1

            sequential_image_intensities = []
            sequential_image_names = []

            for j in range(numberOfFrame):
                sequential_image_intensities.append([])
                start_position = headerSize + imageHeaderSize + j * imageWidth * imageHeight * 2
                for i in range(imageHeight * imageWidth):
                    intensity = struct.unpack('<H', data[start_position + i * 2:start_position + (i+1) * 2])[0]
                    sequential_image_intensities[j].append(intensity)
                sequential_image_names.append(str(j).zfill(3))

            intensity = sequential_image_intensities[0]

            src_img_size = (imageWidth, imageHeight)
            image_type = "HIS"
            comments = f"Num. of Frame: {numberOfFrame}\r\nFrame time: {frameTimeInMilliseconds} ms."

            return intensity, src_img_size, image_type, comments
    except Exception as e:
        print(e)
        return None, None, None, None



def get_df(fpd: FpdFile) -> pd.DataFrame:
    intensity, src_img_size, image_type, comments = read_his_file(fpd.filepath)
    
    # 強度を2次元dataframeにする
    intensity_arr = np.array(intensity)
    intensity_mtx = intensity_arr.reshape(src_img_size)
    df_fpd = pd.DataFrame(intensity_mtx)

    return df_fpd


def print_df_info(df, filename):
    """
    DataFrameの情報を表示する
    """
    print(f"\n{filename}\n")
    print("    ---- info() ----\n")
    print(df.info())
    print("")
    print("    ---- describe() ----\n")
    print(df.describe())
    print("")
    print("    ---- further describe() ----\n")
    print(df.describe().T.describe())


if __name__ == "__main__":
    path_CeO2 = "test_data/CeO2_FPD_MgS400_1_0.his"
    path1 = "test_data/fpd_OIpD03__36_0.his"
    path2 = "test_data/fpd_OIpD03__37_0.his"

    option = {'cmap': 'jet'}

    """
    CeO2データ
    """
    CeO2_flag = False
    logger_info(f"CeO2_flag: {CeO2_flag}")

    if CeO2_flag:
        fpd_CeO2 = FpdFile(path_CeO2)
        df_fpd_CeO2 = get_df(fpd_CeO2)
        fig_CeO2 = plot_heatmap(df_fpd_CeO2)
        
        if False:
            logger_info("save figure")
            save_fig(fig_CeO2, filename=fpd_CeO2.filename)

    if CeO2_flag and False:
        logger_info("print info")
        print(df_display_info(df_fpd_CeO2), fpd_CeO2.filename)

    """
    自分のデータ
    強度の上限をつける
    """
    my_flag = False
    logger_info(f"my_flag: {my_flag}")

    if my_flag:
        fpd1 = FpdFile(path1)
        df_fpd1 = get_df(fpd1)

        threshold = 4000
        df_fpd1[df_fpd1 >= threshold] = 0
        start = 1300
        end = 3900
        fig1 = plot_heatmap(df_fpd1.iloc[start:end, start:end], option=option)

        if False:
            logger_info("save figure")
            save_fig(fig1, f"threshold_{threshold}_{fpd1.filename}")

        """
        2枚目
        """
        if True:
            fpd2 = FpdFile(path2)
            df_fpd2 = get_df(fpd2)

            threshold = 5000
            df_fpd2[df_fpd2 >= threshold] = 0
            fig2 = plot_heatmap(df_fpd2.iloc[start:end, start:end], option=option)

            if False:
                logger_info("save figure")
                save_fig(fig2, f"threshold_{threshold}_{fpd2.filename}")


    """
    diffデータ
    """
    diff_flag = True
    logger_info(f"diff_flag: {diff_flag}")
    
    if diff_flag:
        fpd1 = FpdFile(path1)
        fpd2 = FpdFile(path2)
        df_fpd1 = get_df(fpd1)
        df_fpd2 = get_df(fpd2)

        threshold = 5000

        df_fpd1[df_fpd1 >= threshold] = 0
        df_fpd2[df_fpd2 >= threshold] = 0

        df_diff = df_fpd2 - df_fpd1 # において，増加が暖色・減少が寒色

        start = 1300
        end = 3900
        option = {'cmap': 'seismic'}

        fig_diff = plot_heatmap(df_diff.iloc[start:end, start:end], option=option)
        if True:
            save_fig(fig_diff, f"threshold_{threshold}_diff_{fpd1.filename}_{fpd2.filename}")
else:
    from Util.log import logger
    logger.info(f"{__name__: <30} is imported.")
