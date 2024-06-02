"""
データの読み出しや保存を管理するクラス
セーブした図を表示とかもやってほしい
"""

import os

class Read:
    def __init__(self, *, data_root_path: str):
        self.data_root_path = data_root_path

    def select_data_folder(self, *,
                           sample_num: int,
                           experiment_num: int,
                           run_num: int) -> None:
        # FIXME フォルダの深さを指定して再帰的にした方が柔軟に使える
        # root直下の試料フォルダを選ぶ
        sample_folders: list = self._search_folder(self.data_root_path)
        sample_folders = self._exclude_specific_files(items=sample_folders,
                                                      targets=['_', '.']) # FIXME targetsじゃなくてexclusions
        sample_name = self._display_folders_and_get_target(sample_folders,
                                                           sample_num,
                                                           target='1. 試料選択')
        # 試料直下の実験名フォルダを選ぶ
        sample_path = self.data_root_path + '/' + sample_name
        experiment_folders: list = self._search_folder(sample_path)
        experiment_folders = self._exclude_specific_files(items=experiment_folders,
                                                          targets=['_', '.']) # FIXME targetsじゃなくてexclusions
        experiment_name = self._display_folders_and_get_target(experiment_folders,
                                                               experiment_num,
                                                               target='2. セル選択')
        # 実験名直下のrun名フォルダを選ぶ
        run_path = sample_path + '/' + experiment_name
        run_folders: list = self._search_folder(run_path)
        run_folders = self._exclude_specific_files(items=run_folders,
                                                   targets=['_', '.']) # FIXME targetsじゃなくてexclusions
        run_name = self._display_folders_and_get_target(run_folders,
                                                        run_num,
                                                        target='3. run選択')
        # 取得したものを設定しておく
        self.sample_name = sample_name
        self.run_name = experiment_name + '_' + run_name
        print("\n解析run: " + self.run_name)
        self.data_path = run_path + '/' + run_name

    def _search_folder(self, path: str) -> list:
        folders = os.listdir(path)
        folders.sort() # 必要ではないが順番を固定した方がバグ出にくいと感じる
        return folders

    def _exclude_specific_files(self, items: list, targets: list) -> list:
        folders = [] # returnするリスト
        for item in items: # ファイルごとに
            should_exclude = False
            for target in targets: # 除外するものごとに
                if target in item:
                    should_exclude = True
                else:
                    continue
            # print(f"{item = } | {should_exclude = }") # debug用
            if not should_exclude:
                folders.append(item)
        # print(f"{targets}を含むファイルを除外しました")
        return folders

    def _display_folders_and_get_target(self,
                                        target_list: list,
                                        target_index: int,
                                        target: str) -> str:
        print(f"--- {target} --- ")
        for i, item in enumerate(target_list):
            if i == target_index:
                print(f"|>{i: >2}: {item} <====")
                target_name: str = item
            else:
                print(f"  {i: >2}: {item}")
        return target_name

    def set_filepaths(self):
        # それぞれのfile名を取得する
        files = os.listdir(self.data_path)
        files.sort()

        # それぞれのpathをセットする
        print("使用するそれぞれのデータファイル名\n")
        for file in files:
            if '.spe' in file:
                print(f"spe  : {file}\n")
                self.spe_path = self.data_path + '/' + file
            if '.nxs' in file:
                print(f"nxs  : {file}\n")
                self.nxs_path = self.data_path + '/' + file
            if '.poni' in file:
                print(f"poni : {file}\n")
                self.poni_path = self.data_path + '/' + file
            if '.csv' in file:
                if 'dist' in file:
                    print(f"dist : {file}\n")
                    self.dist_path = self.data_path + '/' + file
                if 'calib' in file:
                    print(f"calib: {file}\n")
                    self.calib_path = self.data_path + '/' + file

    # これは渡されたオブジェクトのメソッドや属性を返す
    def enumerate_methods_and_attrs(self, object, excludions: list):
        items = dir(object)
        attrs = self._exclude_internal_methods(items=items,
                                               targets=excludions)
        for i, item in enumerate(attrs):
            print(f"{i: >2}: {item: <30} | {type(getattr(object, item))}")

    def _exclude_internal_methods(self, items: list, targets: list) -> list:
        attrs = [] # returnするリスト
        for item in items: # ファイルごとに
            should_exclude = False
            for target in targets: # 除外するものごとに
                if item[0] == target:
                    should_exclude = True
                else:
                    continue
            # print(f"{item = } | {should_exclude = }") # debug用
            if not should_exclude:
                attrs.append(item)
        # print(f"{targets}から始まるファイルを除外しました")
        return attrs