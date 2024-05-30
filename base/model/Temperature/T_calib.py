import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import h5py
from time import time



class T_calib:
    def __init__(self, *, filepath: str):
        self.filepath_calib = filepath
        print(f"ファイル: {self.filepath_calib}")

    def _load_calib_data(self) -> pd.DataFrame:
        # クラス内で呼ばれることを想定している。
        # calibデータはでかいので保持しない。

        print("~~ calib.csvを読み込み中...これには時間がかかります")
        t1 = time()
        df = pd.read_csv(self.filepath_calib)
        t2 = time()
        print(f"読み込みました。かかった時間: {round(t2 - t1)} sec ~~\n")

        df.drop(['ROI', 'Column'], axis=1, inplace=True)
        return df

    def get_pixel_integrated_array(self):
        df = self._load_calib_data()
        self.calib_intensity_arr = df.groupby('Row')['Intensity'].sum() #type: pd.Series

        print("\n~~ frameごとの積算データの概要を表示")
        print(self.calib_intensity_arr.describe())
        del df

    def get_max_pixel(self) -> tuple[int]:
        pixel1 = self.calib_intensity_arr[100:150].idxmax() # 100-150 pixelで最大値pixelを探す
        pixel2 = self.calib_intensity_arr[360:410].idxmax() # 360-410 pixelで~
        self.up_max_pixel = pixel1
        self.down_max_pixel = pixel2
        return pixel1, pixel2

    def plot_integrated_array(self, draw_max_pixel=True):
        x_array = np.arange(len(self.calib_intensity_arr))
        y_array = self.calib_intensity_arr

        figsize = (4, 4)
        dpi = 200
        facecolor = 'white'
        fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=facecolor)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x_array, y_array)
        ax.set_title('Integrated Spectrum Intensity')
        ax.set_xlabel('Pixel')
        ax.set_ylabel('Intensity(a.u.)')
        if draw_max_pixel:
            ax.axvline(self.up_max_pixel, color='r',
                       linestyle='--',
                       label='Up',
                       markersize=2)
            ax.axvline(self.down_max_pixel, color='orange',
                       linestyle='--',
                       label='Down',
                       markersize=2)
            ax.legend()
        ax.grid()

    def plot_integrated_array_partial(self,
                                      draw_max_pixel=True,
                                      lower_um = 100,
                                      upper_um = 500,
                                      pixel_to_um = 1.28):
        x_array = np.arange(len(self.calib_intensity_arr)) * pixel_to_um
        y_array = self.calib_intensity_arr

        figsize = (4, 4)
        dpi = 200
        facecolor = 'white'
        fig = plt.figure(figsize=figsize, dpi=dpi, facecolor=facecolor)
        ax = fig.add_subplot(1, 1, 1)
        ax.plot(x_array, y_array)
        ax.set_title('Integrated Spectrum Intensity')
        ax.set_xlabel('sample length(μm)')
        ax.set_ylabel('Intensity(a.u.)')
        if draw_max_pixel:
            ax.axvline(self.up_max_pixel * pixel_to_um, color='r',
                       linestyle='--',
                       label='Up',
                       markersize=2)
            ax.axvline(self.down_max_pixel * pixel_to_um, color='orange',
                       linestyle='--',
                       label='Down',
                       markersize=2)
            ax.legend()
        ax.set_xlim(lower_um, upper_um)
        lower_pixel = round(lower_um / 1.28)
        upper_pixel = round(upper_um / 1.28)
        ax.set_ylim(self.calib_intensity_arr[lower_pixel:upper_pixel].min() * 0.9,
                    self.calib_intensity_arr[lower_pixel:upper_pixel].max() * 1.1)
        print(f"{lower_um} μmから {upper_um} μmまで表示中")
        ax.grid()

    def plot_single_spectrum(self, *,
                             ax, frame, pixel,
                             color) -> plt.Axes:
        calib_df = self._load_calib_data()
        spectrum = calib_df[(calib_df['Frame'] == frame) & (calib_df['Row'] == pixel)]
        ax.plot(spectrum['Wavelength'], spectrum['Intensity'],
                label=f"{frame =} / {pixel =}", color=color, alpha=0.5)
        del calib_df
        return ax

    """
    hdf5ファイルにしてみる。calibに限らずでかデータに使えそうなのでやる。
    目的) メモリで保持せずに、スペクトルを自由に読みだす
    色々メリット: https://qiita.com/simonritchie/items/23db8b4cb5c590924d95
    今嬉しい -> 1. データの部分アクセスが可能 / 2. Numpy的に使える
    実装すればさらに嬉しい -> 1. 圧縮できる / 2. 階層的にデータを入れられるので1runで1つのファイルにまとめられる(部分的に読めるので容量気にならないはず)
    """
    def dump_to_hdf5(self, *,
                     frame_num: int,
                     pixel = 512, # ROI対応する可能性があるので引数にしてる
                     wave_length_pixel = 512,
                     filename = 'CalibData.hdf5',
                     hierarchy = 'temperature/'):
        df = self._load_calib_data()
        calib_arr = df['Intensity'].values.reshape((frame_num, pixel, wave_length_pixel)) # 3次元のnp配列になる
        with h5py.File(filename, 'w') as f:
            f.create_dataset(hierarchy + 'calib_data', data=calib_arr)

if __name__ != "__main__":
    print(f"{__name__: <30} is imported")