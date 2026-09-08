# Mini relatorio - Laboratorio M1

## Identificacao

- Estudante: Vinícius Gaboardi Silva
- Matricula: Ciência da Computação - 9° Periodo
- Laboratorio: M1.1 - Representação, canais e níveis de cinza
- Linguagem: Python

## 1. Objetivo

Implementar as operações fundamentais de uma imagem digital: inspeção de dimensões/canais/tipo, cópia, separação dos canais, conversão para níveis de cinza (média simples e média ponderada) e quantização radiométrica em 16, 8, 4 e 2 níveis. Nenhuma dessas operações usa uma função pronta equivalente do OpenCV, todas percorrem a matriz de pixels com laços explícitos em src/pdi_lab/m1_1.py.

## 2. Operacoes implementadas

- 'inspect': percorre todos os pixels acumulando mínimo, máximo, soma e contagem - geral e por canal - sem usar 'numpy.min'/'max'/'mean'. Largura, altura, número de canais e 'dtype' são consultados via 'image.shape' e 'image.dtype', permitidos pelo contrato como infraestrutura. A saída é impressa em 'chave=valor' no stdout e, se 'output' for informado, também é serializada em JSON via 'result_io.write_json_object'.
- 'copy': cria uma matriz de zeros com 'numpy.zeros_like' (apenas para alocar memória) e copia cada pixel individualmente em um laço duplo (ou triplo, quando há canais).
- 'channel_b' / channel_g' / 'channel_r': mantêm a imagem de saída com 3 canais, zerando os outros dois e copiando apenas o canal solicitado,pixel a pixel. Os índices seguem a ordem BGR usada pelo OpenCV ('b=0, g=1, r=2').
- 'grayscale_average': para cada pixel, calcula '(R+G+B)/3' em ponto flutuante e arredonda com 'round()', sem conversão prematura para inteiro.
- 'grayscale_weighted': aplica '0,299R + 0,587G + 0,114B' por pixel, com o mesmo cuidado de arredondar apenas no final.
- 'quantize': usa o mapeamento 'saida = (entrada // (256/levels)) *(256/levels)', ou seja, cada pixel é levado ao início da faixa (bin) em que ele se encontra. Como '256/levels' é sempre inteiro para 'levels ∈ {2,4,8,16}', o resultado permanece garantidamente em '[0, 255]'. A operação foi implementada de forma genérica para 1 ou 3 canais, embora o roteiro só peça a aplicação sobre uma imagem já em níveis de cinza.

Decisão importante: operações que exigem uma imagem BGR de 3 canais('channel_*', 'grayscale_average', 'grayscale_weighted') validam o número de canais da entrada e retornam erro ('exit_code.GENERAL_ERROR') caso a imagem não seja colorida, em vez de assumir um formato incorreto silenciosamente.

## 3. Testes realizados

| Teste | Entrada | Operacao | Parametros | Resultado esperado ou criterio de verificacao |
|---|---|---|---|---|
| 'test_copy_is_pixel_exact' | 'm1_color_2x2.png', 'm1_gray_5x5.png' | copy | - | Saída numericamente idêntica à entrada |
| 'test_extract_channel_preserves_only_the_requested_channel' | 'm1_color_2x2.png' | channel_b/g/r | - | Apenas o canal solicitado é não-nulo |
| 'test_extract_channel_rejects_non_bgr_input' | matriz 5x5 (1 canal) | channel_b | - | Levanta 'PdiError' (canal inesperado) |
| 'test_grayscale_average_matches_manual_formula' | 'm1_color_2x2.png' | grayscale_average | - | Resultado '[[85,85],[85,255]]', conferido à mão |
| 'test_grayscale_weighted_matches_manual_formula' | 'm1_color_2x2.png' | grayscale_weighted | - | Resultado '[[76,150],[29,255]]', conferido à mão |
| 'test_grayscale_average_and_weighted_differ_on_saturated_channels' | 'm1_color_2x2.png' | ambas | - | As duas versões produzem valores diferentes |
| 'test_quantize_produces_at_most_the_requested_levels' | 'm1_gray_5x5.png' | quantize | 2, 4, 8, 16 | Conjunto de valores de saída é subconjunto dos níveis esperados |
| 'test_quantize_two_levels_matches_manual_calculation' | 'm1_gray_5x5.png' | quantize | levels=2 | Comparado com 'images/reference/m1_gray_5x5.csv' calculado à mão |
| 'test_quantize_keeps_boundary_values_in_range' | valores sintéticos '0' e '255' | quantize | 2, 4, 8, 16 | Saída sempre em '[0, 255]' |
| 'test_quantize_rejects_invalid_levels' | 'm1_gray_5x5.png' | quantize | levels=3 | Levanta 'PdiError' |
| 'test_inspect_reports_dimensions_and_overall_stats' | 'm1_gray_5x5.png' | inspect | - | width/height/pixels/min/max/mean corretos |
| 'test_inspect_reports_per_channel_stats_for_color_images' | 'm1_color_2x2.png' | inspect | - | Estatísticas por canal presentes e corretas |
| 'test_cli_inspect_prints_expected_keys' | 'm1_gray_5x5.png' | inspect (CLI) | - | Saída padrão contém as chaves esperadas |
| 'test_cli_quantize_writes_output_file' | 'm1_gray_5x5.png' | quantize (CLI) | levels=4 | Arquivo gerado e valores dentro dos níveis esperados |
| 'test_cli_channel_r_writes_three_channel_image' | 'm1_color_2x2.png' | channel_r (CLI) | - | Arquivo de saída com 3 canais e canal R preservado |

Os testes usam 'm1_color_2x2.png' e 'm1_gray_5x5.png' porque seus valores de pixel são conhecidos ('images/reference/small_images_reference.json' e 'images/reference/m1_gray_5x5.csv'), permitindo conferência manual completa.

## 4. Resultados

| Operacao | Entrada | Parametros | Arquivo de saida | Observacao |
|---|---|---|---|---|
| inspect | 'm1_gray_scene_256.png' | - | 'results/inspect_gray_scene_256.json' | width=256, height=256, channels=1 |
| inspect | 'm1_color_2x2.png' | - | 'results/inspect_color_2x2.json' | estatísticas por canal B, G, R |
| copy | 'm1_gray_scene_256.png' | - | 'images/output/copy.png' | idêntica à entrada, pixel a pixel |
| channel_b | 'm1_color_2x2.png' | - | 'images/output/channel_b.png' | apenas canal azul preservado |
| channel_g | 'm1_color_2x2.png' | - | 'images/output/channel_g.png' | apenas canal verde preservado |
| channel_r | 'm1_color_2x2.png' | - | 'images/output/channel_r.png' | apenas canal vermelho preservado |
| grayscale_average | 'm1_color_2x2.png' | - | 'images/output/gray_average.png' | '[[85,85],[85,255]]' |
| grayscale_weighted | 'm1_color_2x2.png' | - | 'images/output/gray_weighted.png' | '[[76,150],[29,255]]' |
| quantize | 'm1_gray_scene_256.png' | levels=16 | 'images/output/quant_16.png' | banding quase imperceptível |
| quantize | 'm1_gray_scene_256.png' | levels=8 | 'images/output/quant_8.png' | leve banding em regiões suaves |
| quantize | 'm1_gray_scene_256.png' | levels=4 | 'images/output/quant_4.png' | banding evidente |
| quantize | 'm1_gray_scene_256.png' | levels=2 | 'images/output/quant_2.png' | imagem reduzida a preto/branco |

## 5. Analise tecnica

**1. Diferença entre resolução espacial e resolução radiométrica.**
Resolução espacial é a quantidade de amostras (pixels) por unidade de área - está associada a 'width'/'height' (mais pixels, mais detalhe de forma e posição). Resolução radiométrica é a quantidade de níveis distintos de intensidade que cada pixel pode assumir - está associada à profundidade de bits e é exatamente o que a operação 'quantize' reduz, mantendo 'width' e 'height' inalterados.

**2. Por que a média ponderada difere da média simples.**
A média simples trata R, G e B como igualmente importantes para a luminância percebida. A média ponderada usa os coeficientes '0,299/0,587/0,114', que refletem a sensibilidade do olho humano - muito maior ao verde, intermediária ao vermelho e menor ao azul. Isso fica evidente nos resultados de teste: um pixel verde puro produz '85' na média simples, mas '150' na ponderada; um pixel azul puro produz '85' na média simples e apenas '29' na ponderada.

**3. O que ocorre visualmente quando a quantidade de níveis é reduzida.**
Transições suaves de intensidade são substituídas por platôs constantes ("bandas"), pois vários valores de entrada são mapeados para o mesmo valor de saída. Em 'levels=2', a imagem se aproxima de uma máscara binária preto/branco (visível em 'quant_2.png').

**4. Em quais regiões a perda de informação fica mais evidente.**
Em regiões de gradiente suave (poucas variações de intensidade por pixel), como fundos ou sombreados - porque a quantização "achata" pequenas diferenças em um mesmo nível, criando contornos artificiais (banding). Em regiões já uniformes (fundo constante) ou já com alto contraste (bordas nítidas), a perda visual é pouco perceptível, pois esses valores já tendiam a cair no mesmo nível ou permanecer em extremos distintos. 

**5. Como o tipo e o número de canais interferem no acesso a um pixel.**
Uma imagem de 1 canal ('uint8', 2D) é acessada como 'image[y, x]' e retorna um escalar. Uma imagem de 3 canais (BGR) é acessada como 'image[y, x, c]', onde 'c' seleciona o canal, e a ordem de armazenamento do OpenCV é B, G, R - não R, G, B. Ignorar essa ordem foi a causa mais comum de erro durante o desenvolvimento (por exemplo, trocar 'image[y, x, 2]' por 'image[y, x, 0]' ao buscar o vermelho), por isso os testes usam 'm1_color_2x2.png' com valores de referência conhecidos para pegar esse tipo de engano.

## 6. Limitacoes

- 'quantize' foi implementado de forma genérica para imagens de 1 ou 3 canais, mas o roteiro só exige a aplicação sobre uma imagem já convertida para níveis de cinza; o comportamento em imagens coloridas não foi detalhado no enunciado.
- As operações de M1.1 não tratam imagens com canal alfa (4 canais); nesse caso, 'channel_b/g/r', 'grayscale_average' e 'grayscale_weighted' retornam erro por número inesperado de canais. Duas imagens-base do repositório ('m1_color_scene_256.png' e 'm1_gray_ramp_256.png') estão corrompidas (ver seção 3) e não puderam ser usadas nas demonstrações; isso é uma limitação do ambiente de dados, não do algoritmo.

## 7. Referencias

- Código base adaptado para o projeto: "https://github.com/m4rc3lo/pdi_template.git"

Liste documentacao, livros, paginas, exemplos ou outras fontes consultadas. O uso de IA generativa deve ser declarado separadamente em `AI_USAGE.md`.