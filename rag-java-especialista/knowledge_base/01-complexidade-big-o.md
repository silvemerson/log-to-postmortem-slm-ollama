# Complexidade Big-O em Java

## Notação Big-O

Big-O descreve como o tempo (ou memória) de execução de um algoritmo cresce conforme o tamanho da entrada (`n`) aumenta. As classes mais comuns, da melhor para a pior:

- `O(1)` — constante: acesso a um elemento de array por índice, `get`/`put` em `HashMap` (caso médio).
- `O(log n)` — logarítmica: busca binária, operações em árvores balanceadas (`TreeMap`, `TreeSet`).
- `O(n)` — linear: percorrer uma `ArrayList` ou `LinkedList` uma vez.
- `O(n log n)` — quase-linear: a maioria dos algoritmos de ordenação eficientes (`Collections.sort`, `Arrays.sort` para objetos).
- `O(n²)` — quadrática: laços aninhados sobre a mesma coleção, ex: bubble sort, insertion sort ingênuo.

## Complexidade de estruturas Java comuns

| Estrutura      | Acesso   | Inserção (fim) | Inserção (meio) | Busca      |
|----------------|----------|-----------------|-------------------|------------|
| `ArrayList`    | O(1)     | O(1) amortizado | O(n)              | O(n)       |
| `LinkedList`   | O(n)     | O(1)             | O(1)*             | O(n)       |
| `HashMap`      | O(1)**   | —                | —                 | O(1)**     |
| `TreeMap`      | O(log n) | —                | —                 | O(log n)   |
| `ArrayDeque`   | O(1) nas pontas | O(1)      | O(n)              | O(n)       |

\* O(1) se você já tem o iterador posicionado; para chegar até o meio ainda é O(n).
\*\* Caso médio, assumindo boa distribuição de hashes; pior caso pode degradar para O(n) com muitas colisões.

## Dicas práticas

- Não otimize prematuramente: para coleções pequenas (dezenas de elementos), a diferença entre O(n) e O(log n) raramente importa na prática — o overhead de estruturas mais "espertas" pode até ser pior.
- Meça antes de trocar de estrutura de dados só por causa da Big-O teórica; use um profiler ou benchmark (JMH) em casos críticos.
- Complexidade de tempo e de espaço são trade-offs: um `HashMap` para memoização é rápido, mas custa memória proporcional ao número de entradas distintas.
