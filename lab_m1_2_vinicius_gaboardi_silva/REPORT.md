# Mini relatorio - Laboratorio M1

## Identificacao

- Estudante: Vinicius Gaboardi Silva
- Matricula: Ciência da Computação - 9° Periodo
- Laboratorio: M1.2 - Transformações de intensidade
- Linguagem: Python

## 1. Objetivo

Implementar transformações pontuais em imagens em níveis de cinza - ajuste de brilho, ajuste de contraste, negativo e limiarização binária - e o cálculo manual do histograma de intensidades, analisando como cada operação altera os valores dos pixels e a distribuição das intensidades.

## 2. Operacoes implementadas

Todas as operações percorrem explicitamente os pixels da imagem ('for y in range(height): for x in range(width): ...') em 'src/pdi_lab/intensity.py', sem usar funções prontas do OpenCV que executem a operação diretamente.

- **brightness**: 'g(x,y) = f(x,y) + value', com saturação em '[0, 255]'.
- **contrast**: 'g(x,y) = alpha*(f(x,y)-128)+128', com arredondamento ('round') antes da saturação em '[0, 255]'.
- **negative**: 'g(x,y) = 255 - f(x,y)' (não pode saturar, pois 'f' já está em '[0, 255]').
- **threshold**: 'g(x,y) = 0' se 'f(x,y) < T', senão '255'.
- **histogram**: vetor de 256 contadores, incrementado a cada pixel visitado; serializado em CSV por 'result_io.write_histogram_csv' (256 linhas de dados + cabeçalho).

Decisão tomada: todas as cinco operações exigem imagem de entrada com um único canal (escala de cinza). Uma imagem colorida é rejeitada com erro claro antes de processar qualquer pixel, em vez de processar apenas um canal silenciosamente.

## 3. Testes realizados

| Teste | Entrada | Operacao | Parametros | Resultado esperado ou criterio de verificacao |
|---|---|---|---|---|
| Brilho negativo | 'images/input/m1_gray_5x5.png' | brightness | '--value -30' | Linha 0 (10..50) vira '[0,0,0,10,20]'; saturação em 0 |
| Brilho positivo | 'images/input/m1_gray_5x5.png' | brightness | '--value 30' | Linha 4 (210..250) vira '[240,250,255,255,255]'; saturação em 255 |
| Contraste reduzido | 'images/input/m1_gray_5x5.png' | contrast | '--alpha 0.5' | 'g = 0.5f + 64'; sem saturação nesta imagem |
| Contraste identidade | 'images/input/m1_gray_5x5.png' | contrast | '--alpha 1.0' | Saída igual à entrada |
| Contraste ampliado | 'images/input/m1_gray_5x5.png' | contrast | '--alpha 1.5' | Linha 0 vira '[0,0,0,0,11]' e linha 4 vira '[251,255,255,255,255]'; saturação nos dois extremos |
| Negativo | 'images/input/m1_gray_5x5.png' | negative | - | 'g = 255 - f'; conferido pixel a pixel |
| Limiar baixo | 'images/input/m1_gray_5x5.png' | threshold | '--threshold 100' | Linha 1 (60..100) vira '[0,0,0,0,255]' |
| Limiar alto | 'images/input/m1_gray_5x5.png' | threshold | '--threshold 200' | Linha 3 (160..200) vira '[0,0,0,0,255]'; linha 4 toda 255 |
| Histograma original | 'images/input/m1_gray_5x5.png' | histogram | - | 25 pixels, cada intensidade 10,20,...,250 com contagem 1 |
| Histograma após brilho | saída de brightness '+30' sobre a rampa 5×5 | histogram | - | Soma continua 25; posição 255 acumula 3 pixels saturados (230, 240, 250) |
| Imagem colorida rejeitada | 'images/input/m1_color_2x2.png' | negative | - | Erro tratado ('PdiError'), sem processar a imagem |
| Parâmetro fora do intervalo | 'images/input/m1_gray_scene_256.png' | threshold | '--threshold 999' | Rejeitado na validação do contrato antes de chegar ao algoritmo ('exit_code=5') |

Automatizados em 'tests/test_intensity.py' (8 testes) e nos testes públicos de infraestrutura ('test_cli.py', 'test_infrastructure.py'). Total: 16 testes, todos passando ('python -m pytest').

## 4. Resultados

| Operacao | Entrada | Parametros | Arquivo de saida | Observacao |
|---|---|---|---|---|
| brightness | 'images/input/m1_gray_steps_16levels.png' | '--value 30' | 'images/output/brightness_pos30.png' | Sem saturação visível nos degraus mais baixos |
| brightness | 'images/input/m1_gray_steps_16levels.png' | '--value -30' | 'images/output/brightness_neg30.png' | Degraus mais escuros saturam em 0 |
| contrast | 'images/input/m1_gray_scene_256.png' | '--alpha 0.5' | 'images/output/contrast_05.png' | Imagem mais "achatada", próxima de cinza médio |
| contrast | 'images/input/m1_gray_scene_256.png' | '--alpha 1.0' | 'images/output/contrast_10.png' | Idêntica à entrada (identidade) |
| contrast | 'images/input/m1_gray_scene_256.png' | '--alpha 1.5' | 'images/output/contrast_15.png' | Regiões muito claras/escuras saturam |
| negative | 'images/input/m1_gray_scene_256.png' | - | 'images/output/negative.png' | Inversão tonal completa |
| threshold | 'images/input/m1_gray_scene_256.png' | '--threshold 100' | 'images/output/threshold_100.png' | Máscara binária, mais pixels brancos |
| threshold | 'images/input/m1_gray_scene_256.png' | '--threshold 180' | 'images/output/threshold_180.png' | Máscara binária, mais pixels pretos |
| histogram | 'images/input/m1_gray_steps_16levels.png' | - | 'results/histogram_steps_original.csv' | 256 linhas, soma = 32768 (128×256 pixels) |
| histogram | 'images/output/brightness_pos30.png' | - | 'results/histogram_steps_brightness_pos30.csv' | Distribuição deslocada à direita em relação ao original |

## 5. Analise tecnica

1. **Diferença entre brilho e contraste:** o brilho desloca todos os valores de intensidade pela mesma quantidade aditiva (translação do histograma), preservando a diferença entre pixels vizinhos. O contraste reescala a distância de cada pixel em relação ao ponto médio (128); com 'alpha > 1' ele afasta os valores do centro (mais contraste, mais saturação nos extremos) e com 'alpha < 1' ele aproxima os valores do centro (imagem mais "achatada"), sem necessariamente deslocar a média.

2. **Testes com saturação:** ocorreu saturação em 'brightness --value 30' (pixels próximos de 255 na rampa 5×5, linha 4), em 'brightness --value -30' (pixels próximos de 0, linha 0) e em 'contrast --alpha 1.5' (saturação nos dois extremos, linhas 0 e 4 da rampa 5×5). O efeito é perda de informação: valores distintos na entrada (por exemplo 230, 240 e 250) colapsam para o mesmo valor de saída (255), o que fica visível no histograma da saída (posição 255 acumula 3 pixels em vez dos 3 valores distintos originais).

3. **Deslocamento do histograma após brilho:** o histograma inteiro se desloca em bloco pela quantidade somada, exceto pela extremidade que colide contra o limite '[0, 255]'. No teste com a rampa 5×5 e '--value 30', a soma total de pixels (25) se mantém, mas os três valores mais altos (230, 240, 250) passam a se acumular na mesma posição 255 em vez de ocuparem três posições distintas.

4. **Distribuição das intensidades ao alterar o contraste:** com 'alpha < 1' o histograma se comprime em torno de 128 (menos posições distintas efetivamente usadas, menor variância); com 'alpha > 1' o histograma se espalha e tende a se acumular nos extremos 0 e 255 conforme mais valores saturam, formando picos nas bordas do intervalo.

5. **Informação perdida na limiarização:** a limiarização binária descarta toda a informação de intensidade relativa dentro de cada uma das duas classes - não é mais possível saber se um pixel binarizado como 255 estava originalmente em 100 ou em 255, nem reconstruir gradientes ou texturas finas; apenas a informação "acima ou abaixo do limiar 'T'" é preservada.

## 6. Limitacoes

- As operações de M1.1 ('inspect', 'copy', canais, escala de cinza,quantização) e de M1.3 (convolução e filtros) continuam como estavam no projeto-base, fora do escopo desta implementação de M1.2.
- As cinco operações exigem explicitamente imagem de entrada com um único canal; imagens coloridas de 3 canais são rejeitadas em vez de convertidas automaticamente para escala de cinza.
- O arredondamento do ajuste de contraste usa 'round()' do Python (arredonda para o par mais próximo em empates do tipo '.5'); não foi comparado com outras convenções de arredondamento.
- Dois arquivos de imagem do projeto-base estão corrompidos (ver nota na seção de resultados); isso é uma limitação do material de entrada, não da implementação.

## 7. Referencias

- Código base adaptado para o projeto: "https://github.com/m4rc3lo/pdi_template.git"

Liste documentacao, livros, paginas, exemplos ou outras fontes consultadas. O uso de IA generativa deve ser declarado separadamente em `AI_USAGE.md`.