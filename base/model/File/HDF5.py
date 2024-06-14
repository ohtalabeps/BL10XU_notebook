
import h5py
import numpy as np

class HDF5:
    def __init__(self, *, hdf: h5py.File):
        self.f = hdf
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