from urllib.request import urlopen
from io import BytesIO
from zipfile import ZipFile
import os
import shutil
from ruamel.yaml import YAML
from ruamel.yaml import CommentedMap

ZIP_REPOSITORY_MAIN_URL = 'https://github.com/PlayerGhost/bombcrypto-multibot/archive/refs/heads/main.zip'

EXTRACT_TO = 'download/'


def downloadfromurl(url):
    print(f'Baixando a versão atualizada de:\n{url}')
    http_response = urlopen(url)
    return BytesIO(http_response.read())


def unzipto(extract_to, file_bytes=None):
    print(f'Extraindo arquivos para: {extract_to}')
    zipFile = ZipFile(file_bytes)
    zipFile.extractall(path=extract_to)


if __name__ == '__main__':
    try:
        os.mkdir("download")

        zip_content_bytes = downloadfromurl(ZIP_REPOSITORY_MAIN_URL)
        unzipto(extract_to=EXTRACT_TO, file_bytes=zip_content_bytes)

        print('Fazendo backup das configurações...')

        yaml = YAML()
        yaml.preserve_quotes = True
        yaml.boolean_representation = ['False', 'True']

        with open('./config.yaml', encoding='utf-8') as open_ymlBackup, \
                open('./download/bombcrypto-multibot-main/config.yaml', encoding='utf-8') as open_ymlCurrent:
            yamlBackup = yaml.load(open_ymlBackup)
            yamlCurrent = yaml.load(open_ymlCurrent)

        with open('./download/bombcrypto-multibot-main/config.yaml', 'w', encoding='utf-8') as open_yml:


            for i in yamlBackup:
                if type(yamlBackup[i]) is CommentedMap:
                    for j in yamlBackup[i]:
                        yamlCurrent[i][j] = yamlBackup[i][j]
                else:
                    if i in yamlCurrent:
                        yamlCurrent[i] = yamlBackup[i]

            yaml.dump(yamlCurrent, open_yml)

        print('Atualizando arquivos...')

        root_src_dir = './download/bombcrypto-multibot-main/'
        root_dst_dir = './'

        for src_dir, dirs, files in os.walk(root_src_dir):
            dst_dir = src_dir.replace(root_src_dir, root_dst_dir, 1)

            if not os.path.exists(dst_dir):
                os.makedirs(dst_dir)

            for file_ in files:
                src_file = os.path.join(src_dir, file_)
                dst_file = os.path.join(dst_dir, file_)

                if os.path.exists(dst_file):
                    if os.path.samefile(src_file, dst_file):
                        continue

                    os.remove(dst_file)

                shutil.move(src_file, dst_dir)

        shutil.rmtree('./download')

        print('Atualização conluída.')
    except Exception as e:
        print('A atualização do bot apresentou problemas...')
        print('Erro: %s' % (str(e)))
    input('Pressione Enter para continuar...')