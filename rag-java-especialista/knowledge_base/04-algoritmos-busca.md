# Algoritmos de Busca em Java

## Busca linear

Percorre a coleção elemento por elemento até encontrar o valor ou chegar ao fim. Complexidade O(n). Não exige que a coleção esteja ordenada. É a opção mais simples e, para coleções pequenas, costuma ser mais rápida na prática que alternativas "mais espertas" — o overhead de estruturas auxiliares só se paga a partir de um certo volume de dados.

```java
for (Order order : orders) {
    if (order.getId().equals(targetId)) {
        return order;
    }
}
```

## Busca binária

Exige a coleção **ordenada**. Divide o espaço de busca pela metade a cada passo, O(log n).

```java
int index = Arrays.binarySearch(sortedArray, target);
// ou, para listas:
int index = Collections.binarySearch(sortedList, target);
```

Se a coleção não estiver ordenada, `binarySearch` tem comportamento indefinido (não lança erro, mas o resultado pode ser incorreto) — sempre garanta a ordenação antes de usar.

## Busca por chave (hash-based)

`HashMap.get(key)` e `HashSet.contains(elem)` são O(1) em média porque usam a função hash do objeto para localizar diretamente o "bucket" onde o elemento estaria, evitando percorrer a coleção. É a opção mais rápida quando você pode indexar por uma chave única.

## Guia rápido de decisão

- Coleção pequena (algumas dezenas de elementos) e sem necessidade de reordenar: busca linear é suficiente e mais simples de manter.
- Coleção grande, já ordenada, e você não pode/quer usar mapa: busca binária.
- Você pode montar um índice por chave (ex: ID) antes de fazer múltiplas buscas: `HashMap`, para amortizar o custo de construção do índice.
