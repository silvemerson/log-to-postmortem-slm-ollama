# Convenções de Algoritmos — Squad Orders

> Este documento descreve convenções **internas** da squad Orders para escolha, implementação e revisão de algoritmos em Java. Não é conhecimento público de mercado — é específico deste time e não está em nenhum livro ou documentação oficial do Java.

## Escolha de algoritmo de busca

- Para coleções com **menos de 50 elementos**, usar o utilitário interno `LinearSearchUtil.find()` (pacote `com.acme.orders.util`), mesmo que a coleção esteja ordenada. O overhead de busca binária não compensa nesse volume, e o utilitário já vem com logging padronizado.
- Para coleções com **50 elementos ou mais**, desde que ordenadas, usar `BinarySearchUtil.find()` (mesmo pacote).
- É proibido chamar `Arrays.binarySearch` ou `Collections.binarySearch` diretamente em código de produção da squad — sempre passar pelo utilitário interno, que adiciona métricas de observabilidade.

## Ordenação

- Nunca usar `Collections.sort(list)` ou `list.sort(comparator)` diretamente em código de produção. Usar `OrderSortingPolicy.applyDefault(list)`, que aplica um `Comparator` padronizado pela squad (prioridade desc, depois data de criação asc) e emite uma métrica de tempo de ordenação.

## Nomenclatura obrigatória

- Métodos de busca devem começar com o prefixo `findBy` (ex: `findByOrderId`, `findByCustomerEmail`).
- Métodos de ordenação devem começar com o prefixo `sortBy` (ex: `sortByPriority`).
- Qualquer método que implemente um algoritmo com complexidade acima de O(n log n) deve ser anotado com `@ComplexityReviewed(bigO = "...")`, indicando a complexidade e obrigando revisão do tech lead antes do merge.

## Estrutura de dados padrão para filas de processamento

- Toda fila de processamento de pedidos deve usar `PriorityBlockingQueue<Order>` com um `Comparator` baseado em `OrderPriority`. É proibido implementar fila de prioridade manualmente com `LinkedList` — já tivemos incidentes de starvation de pedidos de baixa prioridade com implementações manuais.

## Revisão obrigatória

- Qualquer algoritmo com complexidade acima de O(n log n) (ex: O(n²)) precisa de aprovação explícita do tech lead da squad Orders antes do merge, documentada no PR.
- PRs que alterem lógica de ordenação ou busca de pedidos devem incluir um teste de performance com pelo menos 10.000 registros sintéticos.
