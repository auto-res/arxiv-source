import os
import requests
import tarfile
import shutil


def obtain_resource(directory_, url_):
    arxiv_number = url_.replace('https://arxiv.org/abs/', '')

    os.makedirs(directory_ + '/tmp', exist_ok=True)

    # ディレクトリ名を論文タイトルに変える
    dir_name = arxiv_number.replace('.','-')
    arxiv_dir = directory_ + f'/{dir_name}'

    if os.path.exists(arxiv_dir):
        shutil.rmtree(arxiv_dir)

    os.rename(directory_ + '/tmp', arxiv_dir)

    # ディレクトリに移動
    os.makedirs(arxiv_dir + '/source', exist_ok=True)
    os.chdir(arxiv_dir + '/source')

    # ファイルをダウンロード
    soruce_url = f'https://arxiv.org/e-print/{arxiv_number}'
    response = requests.get(soruce_url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/51.0.2704.103 Safari/537.36'})

    with open(f'{arxiv_number}.tar.gz', 'wb') as f:
        f.write(response.content)

    # ファイルを解凍
    with tarfile.open(f'{arxiv_number}.tar.gz', 'r:gz') as tar:
        tar.extractall()

    os.remove(f'{arxiv_number}.tar.gz')

    # 論文の情報を保存するディレクトリを作成
    os.makedirs(arxiv_dir, exist_ok=True)

    # titleのデータを取得
    title_extract(arxiv_dir)

    # related workのデータを取得
    related_work_extract(arxiv_dir)

    # abstractのデータを取得
    abstract_extract(arxiv_dir)

    return



def search_files(directory, keywords):
    """
    ファイル名に指定の文字を含むか判定
    """
    # 指定されたディレクトリ内のすべてのファイルをリストアップ
    for root, dirs, files in os.walk(directory):
        for file in files:
            # ファイル名に指定された文字列が含まれているかどうかを確認
            for keyword in keywords:
                if keyword in file:
                    return os.path.join(root, file)
    return None



def list_tex_files(directory):
    tex_files = []
    # 指定されたディレクトリ内のすべてのファイルをリストアップ
    for root, dirs, files in os.walk(directory):
        for file in files:
            # ファイルの拡張子が .tex であるかどうかを確認
            if file.endswith('.tex'):
                tex_files.append(os.path.join(root, file))
    return tex_files



def extract_text_between(file_path, start_string, end_string):
    with open(file_path, 'r', encoding='utf-8') as f:
        data = f.read()
    start_index = data.find(start_string)
    if start_index != -1:
        # start_stringの後で、end_stringが初めて出現するインデックスを取得
        end_index = data.find(end_string, start_index + len(start_string))
        if end_index != -1:
            # スタート文字列とエンド文字列を含めない場合
            return data[start_index + len(start_string):end_index]
    return None





def title_extract(arxiv_dir_):
    tex_files = list_tex_files(arxiv_dir_)
    for i in tex_files:
            text = extract_text_between(i, '\\title{', '}')
            if text != None:
                text = text.replace('\\','')
                text = text.replace('\n','')
                with open(arxiv_dir_ + '/title.txt', 'w', encoding='utf-8') as file:
                    file.write(text)
    return





def related_work_extract(arxiv_dir_):
    keywords = ["related", "Related"]
    result = search_files(arxiv_dir_, keywords)

    if result != None:
        with open(result, 'r', encoding='utf-8') as file:
            text = file.read()

        # テキストを別のファイルに書き込む
        with open(arxiv_dir_ + '/related_work.txt', 'w', encoding='utf-8') as file:
            file.write(text)
    else:
        tex_files = list_tex_files(arxiv_dir_)
        for i in tex_files:
            text = extract_text_between(i, '\\section{Related Work}', '\\section')
            if text != None:
                with open(arxiv_dir_ + '/related_work.txt', 'w', encoding='utf-8') as file:
                    file.write(text)
    return




def abstract_extract(arxiv_dir_):
    keywords = ["abst", "Abst"]
    result = search_files(arxiv_dir_, keywords)

    if result != None:
        with open(result, 'r', encoding='utf-8') as file:
            text = file.read()

        # テキストを別のファイルに書き込む
        with open(arxiv_dir_ + '/abstract.txt', 'w', encoding='utf-8') as file:
            file.write(text)
    else:
        tex_files = list_tex_files(arxiv_dir_)
        for i in tex_files:
            text = extract_text_between(i, '\\begin{abstract}', '\\end{abstract}')
            if text != None:
                with open(arxiv_dir_ + '/abstract.txt', 'w', encoding='utf-8') as file:
                    file.write(text)
    return