# Calculadora de Redes

Este projeto consiste em uma Calculadora de Redes com interface de linha de comando (CLI) e interface gráfica (GUI), desenvolvida em Python. A ferramenta permite calcular e gerenciar informações de sub-redes IPv4, além de gerar tabelas de roteamento.

## Funcionalidades

O projeto é dividido em dois arquivos principais:

- `exe.py`: A lógica principal da calculadora e a interface de linha de comando (CLI).
- `exe_gui.py`: A interface gráfica (GUI) construída com Tkinter.

### Interface de Linha de Comando (`exe.py`)

- **Cálculo de Redes**: Insira o nome do host, endereço IP, máscara de sub-rede e, opcionalmente, o IP da rede para calcular:
    - Endereço de Rede
    - Gateway (primeiro IP utilizável)
    - Endereço de Broadcast
    - Representações binárias do IP, máscara e rede
    - Número de sub-redes
    - Intervalo de IPs da sub-rede
    - Número total de IPs e de hosts utilizáveis
- **Modo Interativo**: Permite adicionar múltiplas redes em uma única sessão.
- **Tabela Final**: Exibe uma tabela formatada com todas as redes inseridas.
- **Salvar em Arquivo**: Salva a tabela final em um arquivo de texto (`.txt`).

### Interface Gráfica (`exe_gui.py`)

A interface gráfica oferece todas as funcionalidades da versão CLI em um ambiente visual e mais amigável, com recursos adicionais:

- **Interface com Abas**:
    - **Calculadora de Redes**: Para adicionar e gerenciar redes em uma tabela estilo planilha.
    - **Tabela de Roteamento**: Para visualizar as tabelas de roteamento geradas.
- **Gerenciamento de Redes**:
    - Adicionar, editar e remover redes diretamente na tabela.
    - Adicionar dados de exemplo para testes rápidos.
    - Classificar a tabela por qualquer coluna.
    - Ocultar/mostrar colunas com informações binárias.
- **Geração de Tabela de Roteamento**:
    - Gera automaticamente links WAN para múltiplos roteadores.
    - Cria tabelas de roteamento internas (dentro do mesmo roteador).
    - Mostra rotas de entrada (WAN -> LAN) e de saída (LAN -> WAN) entre diferentes roteadores.
- **Importação e Exportação**:
    - **Exportar**: Salve os dados da tabela nos formatos `.csv` ou `.txt`.
    - **Importar**: Carregue redes a partir de um arquivo `.csv`.
- **Gerenciamento de Projetos**:
    - **Salvar Projeto**: Salve o estado atual da calculadora (todas as redes) em um arquivo `.json`.
    - **Carregar Projeto**: Carregue um projeto salvo anteriormente a partir de um arquivo `.json`.

## Como Usar

### Pré-requisitos

- Python 3.x

Não são necessárias bibliotecas externas, pois o projeto utiliza apenas módulos padrão do Python (`ipaddress`, `tkinter`, `csv`, `json`, `math`).

### Executando a Aplicação

1.  **Interface de Linha de Comando (CLI)**:

    Abra um terminal ou prompt de comando no diretório do projeto e execute:

    ```bash
    python exe.py
    ```

    O programa oferecerá duas opções:
    1.  **Modo interativo**: Para inserir os dados da rede manualmente.
    2.  **Testar com exemplos**: Para ver a saída de um conjunto de exemplos pré-definidos.

2.  **Interface Gráfica (GUI)**:

    Para uma experiência mais completa, execute o arquivo da GUI:

    ```bash
    python exe_gui.py
    ```

    A janela da "Calculadora de Redes" será aberta, e você poderá utilizar todas as funcionalidades visuais.
