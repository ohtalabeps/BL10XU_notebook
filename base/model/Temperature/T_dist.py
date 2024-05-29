import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class T_dist:
    def __init__(self, *, filepath: str):
        """
        作成時にはfilepathのみ設定する
        """
        self.filepath_dist = filepath
        print(f"ファイル: {self.filepath_dist}")

    def _load_dist_data(self) -> pd.DataFrame:
        """
        ファイルを読み込む。内部だけで使用されることを想定している。
        """
        print("dist.csvを読み込み中...")
        df = pd.read_csv(self.filepath_dist)
        print("読み込みました")
        return df

    def set_T_data(self):
        """
        frame * pixelの2次元データに整形してセットする。
        """
        df = self._load_dist_data()
        df.drop(['ROI','Frame','Wavelength'], axis=1, inplace=True)
        df = df.pivot(index='Row', columns='Column', values='Intensity')
        """
        colormapを適切な範囲にするための処置
        1. 強度が12,000以上のところを300に置き換える
        2. 強度がマイナスのところを0に置き換える
        """
        df[df >= 12000] = 300
        df[df < 0] = 0
        self.temp_df = df

    def return_T_profile(self, *, frame: int):
        """
        指定されたframeの温度分布を返す。
        """
        return self.temp_df.iloc[frame, :]

    def return_T_variation(self, *, pixel: int):
        """
        指定されたpixelの時系列温度を返す
        あまり使わなそうだが一応作ってる。
        """
        return self.temp_df.iloc[:, pixel]

    def return_stats_arr(self, *,
                         start_frame, # frame
                         end_frame,   # frame
                         center,      # pixel
                         half_width): # pixel
        """
        設定されたframe, pixelの間での最大値、平均値、最小値の配列をそれぞれ返す。
        T_calibなどで設定されていると想定している。
        """
        lower_pixel = center - half_width
        upper_pixel = center + half_width
        adopted_df = self.temp_df.iloc[start_frame:end_frame, lower_pixel:upper_pixel].replace(0, np.nan).T
        min_arr = adopted_df.min()
        mean_arr = adopted_df.mean()
        max_arr = adopted_df.max()
        return min_arr, mean_arr, max_arr

if __name__ != "__main__":
    print(f"{__name__: <30} is imported.")
