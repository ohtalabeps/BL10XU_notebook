
import h5py
import numpy as np

class HDF5:
    def __init__(self, *, f: h5py.File):
        self.f = f
        self.path_num = 0
        self.path_list = []
        self.get_hdf5_all_path(f=self.f) # 初期化した時に、datapath一覧を読み込むようにしてる

    def get_hdf5_all_path(self, f, path=""):
        for key in f.keys():
            current_path = path + "/" + key
            if isinstance(f[key], h5py.Group): # もしkey先がgroupの場合
                self.get_hdf5_all_path(f[key], path=current_path)
            else:
                print(f"{self.path_num: <2}: {current_path}")
                self.path_num += 1
                self.path_list.append(current_path)

    def show_all_hierarchy(self, f, indent=0, path="", display_length=20):
        for key in f.keys():
            print(" " * indent + "/" + key)  # グループ名を出力
            current_path = path + "/" + key
            if isinstance(f[key], h5py.Group):  # もしkey先がgroupの場合
                self.show_all_hierarchy(f[key], indent + 4, path=current_path, display_length=display_length)  # グループ内のさらに深い階層を出力
            else:
                print(" " * indent + f" --> path:  \"{current_path}\"")
                print(" " * indent + f"       L {type(f[key])}")
                dataset = f[key]

                if dataset.shape == ():  # スカラー(単一値)の場合
                    value = str(dataset[()])  # スカラーの場合の読み取り
                else:
                    value = str(f.get(key)[0])

                if len(value) > display_length:
                    print(" " * indent + f"       L {value[:display_length]}")
                else:
                    print(" " * indent + f"       L {value}")

    def search_data_path(self, query: str):
        result_list = []

        print(f"「{query}」で検索します。")
        for path in self.path_list:
            if query in path:
                result_list.append(path)
        print(f"{len(result_list)} 個のpathが見つかりました。\n")

        for i, path in enumerate(result_list):
            print(f"{i: >2}: {path}")
        print("") # 改行用

        return result_list