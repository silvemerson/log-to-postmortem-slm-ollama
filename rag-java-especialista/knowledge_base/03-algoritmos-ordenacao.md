# Algoritmos de Ordenação em Java

## Ordenação nativa

- `Arrays.sort(int[] arr)` — para tipos primitivos, usa uma variante de **Dual-Pivot Quicksort**, O(n log n) em média, O(n²) no pior caso (raro na prática).
- `Arrays.sort(Object[] arr)` / `Collections.sort(List<T> list)` — para objetos, usa **TimSort** (híbrido de merge sort e insertion sort), O(n log n) garantido, e é **estável** (mantém a ordem relativa de elementos iguais). TimSort é preferido para objetos porque merge sort é estável e Dual-Pivot Quicksort não é.

## Comparator customizado

```java
List<Order> orders = ...;
orders.sort(Comparator.comparing(Order::getPriority).reversed()
        .thenComparing(Order::getCreatedAt));
```

Combine múltiplos critérios com `thenComparing`. Prefira `Comparator.comparing` a implementar `compareTo` manualmente quando o critério de ordenação pode variar por contexto.

## Quando implementar seu próprio algoritmo

Raramente é necessário. Casos legítimos:

- **Bucket sort**: quando os dados têm distribuição conhecida e limitada (ex: notas de 0 a 10) — pode chegar a O(n).
- **Radix sort**: para chaves inteiras com número fixo de dígitos, útil em volumes muito grandes.
- **Ordenação parcial (`top-k`)**: se você só precisa dos k maiores/menores elementos, use um `PriorityQueue` de tamanho k em vez de ordenar tudo — O(n log k) em vez de O(n log n).

## Armadilhas comuns

- `Collections.sort` com uma lista imutável (`List.of(...)`) lança `UnsupportedOperationException`.
- Comparators que não são consistentes com `equals` podem causar comportamento inesperado em `TreeSet`/`TreeMap`.
- Ordenar dentro de um laço (ordenar a cada iteração) é um anti-padrão comum que transforma O(n log n) em O(n² log n).
