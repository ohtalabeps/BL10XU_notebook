"""
保存する時に使う
一時データとか図とか動画とか
"""

import os
import matplotlib.pyplot as plt


class Save:
    def __init__(self, *, save_root_path: str):
        self.save_root_path = save_root_path
        if not os.path.exists(self.save_root_path): os.mkdir(self.save_root_path)

    def set_run_save_dir(self, *, run_name: str):
        self.run_dir = os.path.join("run", run_name) # 命名が汚い
        self.save_run_path = os.path.join(self.save_root_path, self.run_dir)
        if not os.path.exists(self.save_run_path):
            os.mkdir(self.save_run_path)
            print(f"{self.save_run_path}にフォルダを作成しました。")
        print(f"{self.save_run_path}を保存フォルダとして設定しました。")

    """
    Figure
    """
    def save_fig(self, *,
                 fig_name: str,
                 fig: plt.figure,
                 dpi = 300):
        fname = os.path.join(self.save_run_path, fig_name)
        fig.savefig(fname, dpi=dpi)

    """
    Movie
    """
    # 1. speの動画
    def save_spe_movie(self, data):
        print("speデータの動画を作成")
        # データをもらって、movieディレクトリにanimation movieを作成する
    # 2. T_distの動画

    # 3. nxsの動画
    # 4. nxs cakingの動画