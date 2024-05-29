import nbformat
import os

cwd = os.getcwd()
notebook_path = cwd + '/base/notebook/'
folders = os.listdir(notebook_path)

# notebookの下にある.ipynbファイルのpathを格納する
ipynbs = []
for folder in folders:
    if folder.startswith('.'): # 隠しファイルであればskip
        continue
    else:
        folder_path = os.path.join(notebook_path, folder)
        for file in os.listdir(folder_path):
            if file.endswith('.ipynb'):
                ipynb_path = os.path.join(folder_path, file)
                ipynbs.append(ipynb_path)

# Notebookファイルを開く
for filename in ipynbs:
    with open(filename, 'r', encoding='utf-8') as f:
        print(f"以下のファイルの出力をクリアします...\n\t{filename}")
        nb = nbformat.read(f, as_version=4)

    # 各コードセルの出力・実行カウンタ・実行時間をクリアする
    for cell in nb.cells:
        if cell.cell_type == 'code':
            cell.outputs = []
            cell.execution_count = None
            if 'metadata' in cell and 'ExecuteTime' in cell.metadata:
                cell.metadata['ExecuteTime']['end_time'] = ""
                cell.metadata['ExecuteTime']['start_time'] = ""

    # 変更をファイルに保存する
    with open(filename, 'w', encoding='utf-8') as file:
        nbformat.write(nb, file)

print("\n~~ 出力・実行カウンタ・実行時間がクリアされました ~~")
