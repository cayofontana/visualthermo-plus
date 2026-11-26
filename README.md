# visualthermo-plus
## Análise exploratória das sequências Y16

Instale as dependências com `pip install -e .` e execute na raiz do projeto:

```bash
python -m visualthermo.analysis data/captures/sequencia_1.npz data/captures/sequencia_2.npz
```

Os resultados são criados em `data/analysis/`, em pastas separadas por sequência:
`summary.json`, `timeline.csv`, mapas PNG e matrizes `.npy`.
Para múltiplas sequências, também é criado `comparison.csv`.

O desvio-padrão temporal é amostral (`ddof=1`). A análise residual subtrai
apenas a média espacial de cada quadro e **não modifica os arquivos originais**.
As descontinuidades sinalizadas são **candidatas**, não eventos NUC confirmados.
A escala Y16 não é uma temperatura calibrada em °C.

Testes: `python -m unittest discover -s tests -v`.
