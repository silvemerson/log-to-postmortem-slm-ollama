# Estruturas de Dados em Java

## Listas

- `ArrayList<T>`: array dinâmico. Ótima para acesso aleatório (`get(i)` em O(1)) e para percorrer sequencialmente. Inserção/remoção no meio é O(n) porque precisa deslocar elementos.
- `LinkedList<T>`: lista duplamente encadeada. Boa para inserção/remoção nas pontas ou quando você já tem um `ListIterator` posicionado. Implementa também `Deque<T>`.

## Mapas

- `HashMap<K,V>`: sem ordem garantida, O(1) médio para `get`/`put`. Use quando a ordem não importa e você quer a busca mais rápida possível.
- `LinkedHashMap<K,V>`: mantém a ordem de inserção, com custo ligeiramente maior que `HashMap`.
- `TreeMap<K,V>`: mantém as chaves ordenadas (via `Comparable` ou `Comparator`), operações em O(log n). Use quando precisar iterar em ordem ou buscar por faixas (`ceilingKey`, `floorKey`).

## Filas e Pilhas

- `ArrayDeque<T>`: implementação recomendada para pilha (`push`/`pop`) e fila (`offer`/`poll`) — mais eficiente que `Stack` e `LinkedList` para esses usos.
- `PriorityQueue<T>`: fila de prioridade baseada em heap binário. `poll()` sempre retorna o menor elemento (ou o definido pelo `Comparator`), em O(log n). Não garante ordem entre elementos de mesma prioridade.
- `PriorityBlockingQueue<T>`: variante thread-safe de `PriorityQueue`, útil em cenários concorrentes de processamento (ex: filas de jobs/pedidos).

## Sets

- `HashSet<T>`: conjunto sem duplicatas, sem ordem garantida, O(1) médio para `contains`/`add`.
- `TreeSet<T>`: conjunto ordenado, O(log n) para as mesmas operações.
- `LinkedHashSet<T>`: mantém ordem de inserção.

## Quando escolher o quê

- Precisa de acesso por índice frequente? `ArrayList`.
- Precisa de busca por chave rápida, sem se importar com ordem? `HashMap`.
- Precisa sempre processar o "próximo mais importante"? `PriorityQueue` (ou `PriorityBlockingQueue` se for concorrente).
- Precisa de unicidade e ordenação? `TreeSet`.
