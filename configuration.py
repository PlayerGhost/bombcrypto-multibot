import yaml


class Configuration:
    with open('./config.yaml', 'r', encoding='utf-8') as open_yml:
        c = yaml.safe_load(open_yml)

    language = c['language']
    gameMode = c['gameMode']
    accountLabels = c['accountLabels']
    telegram = c['telegram']
    threshold = c['threshold']
    home = c['home']
