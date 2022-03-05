class Strings:
    def __init__(self, language):
        self.language = language

    def getRegionalizedString(self, index):
            stringPT = ['Heróis que devem ser mandados para casa carregados.',
                      'Colocando os heróis para dormir (seus vagabundos)',
                      'Barras verdes detectadas',
                      'Botoes detectados',
                      'Botoes com barra verde detectados',
                      'Clicando em',
                      'heróis',
                      'Houve muitos cliques em heróis, tente aumentar o go_to_work_btn threshold',
                      'Nenhum herói que deveria ser enviado para casa encontrado.',
                      'Heróis que devem ser enviados para casa encontrados.',
                      'Herói não está trabalhando, enviando para casa.',
                      'Herói está trabalhando, não será enviado para casa.',
                      'Herói já está na casa, ou a casa está cheia.',
                      'O bot irá colocar os bonecos para trabalhar!',
                      'Enviando heróis com a energia cheia para o trabalho',
                      'Enviando heróis com a energia verde para o trabalho',
                      'Enviando todos heróis para o trabalho',
                      '💪 Todo os heróis enviados para o trabalho',
                      'Heróis enviados para o trabalho',
                      'O bot irá atualizar a posição dos heróis aguarde!',
                      'Atualizando posição dos heróis',
                      'O bot irá logar, aguarde!',
                      'Checando se o jogo se desconectou',
                      'Muitas tentativas de login, atualizando',
                      'Botão de conexão da carteira encontrado, logando!',
                      'Preenchendo campo de usuário!',
                      'Preenchendo campo de senha!',
                      'Clicando no botão login!',
                      'Botão de conexão pela metamask, clicado!',
                      'O bot irá consultar seu baú, aguarde!',
                      'Consultando seu baú',
                      'Saldo não encontrado.',
                      '🚨 Seu baú 🚀🚀🚀 na conta',
                      'O bot irá tirar screenshot das suas telas, aguarde!',
                      'Aqui vai como está sua tela na conta',
                      'O bot irá atualizar a página e tentará logar novamente, aguarde!',
                      'janelas com o nome Bombcrypto encontradas!',
                      'Bot inicializado em',
                      'Contas.',
                      'É hora de faturar alguns BCoins!!!',
                      'Janela atual:',
                      'Completamos mais um mapa na conta',
                      'Parabéns temos',
                      'nova(s) jaula(s) no novo mapa 🎉🎉🎉, na conta',
                      '\n\n>>---> Nenhuma janela com o nome Bombcrypto encontrada!']

            stringEN = []

            if self.language == "pt":
                return stringPT[index]
            elif self.language == "en":
                if len(stringEN) >= index:
                    return stringEN[index]
                else:
                    return stringPT[index]
