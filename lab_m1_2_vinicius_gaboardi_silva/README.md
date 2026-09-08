# Projeto-base Python — Laboratórios M1

Esta variante usa Python 3.10+, ambiente virtual (`venv`), OpenCV sem interface gráfica e `pytest`. As operações avaliadas permanecem como **stubs**: a interface existe, mas o algoritmo ainda deve ser implementado pelo estudante.

## 1. Qual Python usar no Windows

No Windows, use uma instalação **CPython para Windows** (por exemplo, a instalação oficial do Python) e não o interpretador Python distribuído pelo MSYS2/UCRT64.

Isso é importante porque o `opencv-python-headless` é distribuído em wheels prontos para CPython/Windows. Se o ambiente virtual for criado a partir do Python do MSYS2/UCRT64, o `pip` pode não considerar esses wheels compatíveis e tentar compilar OpenCV e NumPy localmente, o que adiciona uma cadeia de compilação desnecessária para estes laboratórios.

Antes de criar o ambiente, confira qual Python será usado:

```bash
python --version
python -c "import sys; print(sys.executable)"
```

No Windows, se o comando `py` estiver disponível, esta é uma forma simples de garantir o uso do CPython para Windows:

```bash
py -3.13 -m venv .venv
```

Python 3.12 ou 3.13 são escolhas conservadoras para o ambiente da disciplina. O objetivo não é compilar OpenCV a partir do código-fonte; o objetivo é instalar o wheel pronto e trabalhar nos algoritmos do laboratório.

## 2. Arquivos de construção e dependências

### `requirements.txt`

Lista as dependências do ambiente didático e fixa suas versões para aumentar a reprodutibilidade. Neste template aparecem principalmente:

- `opencv-python-headless` — leitura, escrita e acesso às imagens sem depender de janelas gráficas;
- `pytest` — execução dos testes públicos e dos testes adicionais do estudante.

Instale com:

```bash
python -m pip install -r requirements.txt
```

### `pyproject.toml`

Descreve o pacote Python `pdi-lab`: nome, versão, versão mínima do Python, dependências de execução e localização do código dentro de `src/`.

O comando:

```bash
python -m pip install -e .
```

faz uma instalação **editável**. Assim, alterações em `src/pdi_lab/` passam a ser usadas imediatamente sem reinstalar o pacote a cada edição.

```mermaid
flowchart LR
    A[requirements.txt] --> B[dependencias do ambiente]
    C[pyproject.toml] --> D[pacote pdi_lab]
    B --> E[ambiente virtual]
    D --> E
    E --> F[python -m pdi_lab]
```

## 3. Criar e ativar o ambiente virtual

Na raiz da pasta `python/`.

### Windows — PowerShell

```powershell
py -3.13 -m venv .venv
.\.venv\Scripts\Activate.ps1
```

### Windows — Git Bash ou MSYS2 UCRT64 usando CPython para Windows

```bash
py -3.13 -m venv .venv
source .venv/Scripts/activate
```

Observe a pasta `Scripts/`. Se o ambiente criado no Windows apresentar `.venv/bin/activate`, verifique qual interpretador foi utilizado para criá-lo: provavelmente você criou o ambiente com um Python Unix-like/MSYS2 em vez do CPython para Windows.

### Linux/macOS

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Depois instale:

```bash
python -m pip install --upgrade pip
python -m pip install -r requirements.txt
python -m pip install -e .
```

Uma instalação normal deve baixar wheels binários. Se a saída indicar `Building wheel for opencv-python-headless`, interrompa e confira o interpretador e a plataforma antes de tentar compilar OpenCV localmente.

## 4. Testar o projeto-base antes de começar

```bash
python -m pytest
python -m pdi_lab --version
python -m pdi_lab --help
```

Os testes públicos verificam a infraestrutura: CLI, parâmetros, kernels, imagem de entrada e saída, CSV e JSON. Eles não implementam nem avaliam os algoritmos exigidos nos laboratórios.

## 5. Estrutura principal

```text
src/pdi_lab/
├── __main__.py      ponto de entrada
├── cli.py           leitura dos argumentos
├── contract.py      regras e validações da CLI
├── image_io.py      leitura e escrita de imagens
├── parameters.py    conversão de parâmetros
├── kernel.py        leitura e validação de kernels
├── result_io.py     escrita de CSV e JSON
└── operations.py    ponto inicial das operações avaliadas

tests/               testes públicos
images/input/        imagens-base
images/output/       resultados em imagem
kernels/             kernels textuais
results/             CSV, JSON e outros resultados
```

## 6. Onde implementar

Comece em `src/pdi_lab/operations.py` e crie módulos adicionais quando isso tornar o código mais claro.

A infraestrutura já cuida de argumentos de linha de comando, conversão e validação dos parâmetros básicos, leitura e escrita de imagens, criação dos diretórios de saída, leitura e validação estrutural de kernels, escrita de histogramas já calculados em CSV, escrita de metadados em JSON e tratamento dos principais erros de infraestrutura.

O estudante continua responsável por percorrer pixels ou vizinhanças, implementar as fórmulas solicitadas, calcular histogramas, implementar convolução e filtros, controlar saturação e tipos numéricos quando fizer parte do algoritmo, testar e analisar os resultados.

## 7. Exemplos de interface

```bash
python -m pdi_lab \
  --operation quantize \
  --input images/input/m1_gray_ramp_256.png \
  --output images/output/quant_8.png \
  --levels 8
```

```bash
python -m pdi_lab \
  --operation mean_filter \
  --input images/input/m1_gray_scene_256.png \
  --output images/output/mean_3x3.png \
  --size 3 \
  --border replicate
```

Enquanto a operação continuar como stub, o comando será reconhecido, mas informará que o algoritmo ainda não foi implementado.

## 8. Máquina restrita ou offline

Os wheels podem ser baixados previamente em outra máquina **com a mesma plataforma e versão de Python**:

```bash
python -m pip download --only-binary=:all: -r requirements.txt -d packages
```

Depois, na máquina restrita:

```bash
python -m pip install --no-index --find-links packages -r requirements.txt
python -m pip install -e .
```

O uso de `--only-binary=:all:` é intencional: se não existir wheel compatível, o download deve falhar claramente em vez de preparar silenciosamente uma compilação local do OpenCV.

## 9. OpenCV headless

A versão `opencv-python-headless` não fornece janelas de interface gráfica como `cv2.imshow`. Isso é intencional: os laboratórios usam arquivos de entrada e saída, favorecendo execução reproduzível em terminal, máquinas de laboratório e correção automatizada.
