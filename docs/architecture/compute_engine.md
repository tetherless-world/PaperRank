# `Compute` Engine Architecture

## Overview

### Description

This computation of a PaperRank score involves finding a [stable solution](https://en.wikipedia.org/wiki/Stable_process) to the [Markov process](http://mathworld.wolfram.com/MarkovProcess.html) of a random web surfer.

For more information on how the original PageRank is computed, see:
- http://meyer.math.ncsu.edu/Meyer/PS_Files/DeeperInsidePR.pdf
- http://ilpubs.stanford.edu:8090/422/1/1999-66.pdf

For insight into the implmenentation of the orthodox PaperRank algorithm, the following lectures from the [CS 246 (*Mining of Massive Datasets*)](http://ilpubs.stanford.edu:8090/422/1/1999-66.pdf) course at Stanford University provides an excellent overview:
- [Lecture 5 - Link Analysis and PageRank](https://www.youtube.com/watch?v=fL41WSVDunM&list=PLLssT5z_DsK9JDLcT8T62VtzwyW9LNepV&index=5)
- [Lecture 6 - PageRank: The "Flow" Formulation](https://www.youtube.com/watch?v=1nLV8FEaZD0&index=6&list=PLLssT5z_DsK9JDLcT8T62VtzwyW9LNepV)
- [Lecture 7 - PageRank: The Matrix Formulation](https://www.youtube.com/watch?v=3_1h13PJkUs&list=PLLssT5z_DsK9JDLcT8T62VtzwyW9LNepV&index=7)
- [Lecture 8 - PageRank: Power Iteration](https://www.youtube.com/watch?v=VpiyOxiVmCg&list=PLLssT5z_DsK9JDLcT8T62VtzwyW9LNepV&index=8)
- [Lecture 9 - PageRank: The Google Formulation](https://www.youtube.com/watch?v=ytjf6zYDd4s&list=PLLssT5z_DsK9JDLcT8T62VtzwyW9LNepV&index=9)
- [Lecture 10 - PageRank: Why Teleports Solve the Problem](https://www.youtube.com/watch?v=UZePPh340sU&index=10&list=PLLssT5z_DsK9JDLcT8T62VtzwyW9LNepV)
- [Lecture 11 - How we Really Compute PageRank](https://www.youtube.com/watch?v=E9aoTVmQvok&list=PLLssT5z_DsK9JDLcT8T62VtzwyW9LNepV&index=11)

The computation of PaperRank is a recursive process. We can capitalize on our knowledge of the structure of the citation graph to optimize this process.

### Algorithm Optimization

The bare citation graph can be considered to be a mapping of some paper, to a list of other papers. In addition to this mapping, the `Update` Engine also creates a map of inbound citations. That is, it compiles a list of papers that cite the current paper. The existence of this list simplifies the computation of PaperRank significantly.

**Citation Graph Immutability**

It is also reasonable to assume that the outbound citation graph does not change. That is, the citations used in a publication do not change after the time of publication, and can be considered immuatable.

**Reverse Time-Ordered Optimization**

To leverage the benefit of computing PaperRank on an immutable citation graph, we must build a list of paper pointers, weakly sorted by reverse time of publication. That is, from newset to oldest. This will allow us to compute the final PaperRank scores for all of the elements in the database with a minimum amount of recursive computations. This section describes this optimization in detail.

The immutability of the outbound citation graph guarantees a paper published at some time `t` cannot have been cited by some paper published at time `t-1`. Considering the inverse of this, we can assert that papers published at time `t` can only have been cited by papers published at some time >= `t`. Thus, if computed from newest to oldest, any inbound PageRank lookups will be guaranteed to exist in the existing database.

Typically, this would include a recursive lookup. We can minimize this recursion by iterating through the IDs in reverse, from newest to oldest and computing PaperRank for an increasingly large set of IDs.

If the list `ids_sorted` contains the list of IDs sorted by reverse-time of publication, PaperRank will be computed for increasingly large subsets of `ids_sorted` in the following progression: `ids_sorted[0:1]`, `ids_sorted[0:2]`, `ids_sorted[0:3]`, ..., `ids_sorted[0:len(ids_sorted)]`.

This iteration strategy will ensure minimal recursive calls. These calls will only occur in the cases where an inbound citation's PaperRank does not yet exist, or if the (weakly) sorted list provides IDs out of order.

These recursive cals will only occur if the weakly sorted list provides papers in incorrect order, or papers published at the same time that cite each other. However, as we do not care about the intermediary scores, we can simply ignore a score if it is not found in the lookup step; our strategy guarantees it will be added to the citation graph eventually.


***PubMed Implementation Specific Information***

The PubMed system indexes papers with a system of Pubmed IDs (hereafter pmids). We exploit the face that PubMed IDs are sequencial on assignment to create a weakly sort by time of publication. This is done by simply ordering the list of (integer-cast) IDs from highest to lowest.

---

Taking into account the optimizations described above, we designed the following workflow:

1. Build a list of Paper IDs to iterate (include weak sorting)
2. Build out-degree table
3. Iterate through ID list, call computation function with increasingly large subsets of complete ID list

To enable this computation, we designed an architecture with three, distinct layers of abstraction and an additional `util` submodule. The `util` submodule will encapsulate the functionality of building the list of weakly sorted IDs, and other related tasks (i.e. step 1 and 2).

The highest layer of abstraction, the `Manager` submodule will handle iterating through a progressively increasing subset of IDs, and handling additional functionality such as input preprocessing. The second layer of abstraction will be the `Score` submodule, which will compute the PaperRank for the given list of IDs, and store it in the database.


## `Score` Sub-Module

This module will handle the computation of the actual PaperRank score. It's workflow can be divided into two layers of abstraction: a layer which computes the PaperRank for a given iteration, and a layer that continuously calls this function to compute PaperRank until the solution is stable (i.e. when the sum of the change of each of the PaperRank scores falls below a certain threshhold).

### PaperRank Iteration Compute

The following pseudocode describes the function computing the PaperRank for an iteration. It will take a list of IDs, `id_list` as its parameter and will return a vector of PaperRank scores, with the position of the score corresponding to the position of the ID in `id_list`. In addition to the returned list, it will save the computed PaperRank values to the database directly, in a HashMap.

```python
N = len(id_list)
beta = config.get_beta()  # Probably 0.85

scores = []

for id in id_list:
    pr_id = 0
    inbound_list = db.get_inbound(id)

    for inbound in inbound_list:
        # Skip if not iterated yet, used in place of recursive call
        if inbound in db.pr_list:
            pr_id += beta * (db.get_pr(inbound) / db.get_outdegree(inbound))

    db.set_pr(id, pr_id)  # Save to db

    scores.append(pr_id)  # Append to list

# Redistributing leaked PaperRank (from dangling papers):

leaked_pr = 1 - sum(scores)

if leaked_pr > 0:
    for id in id_list:
        scores[id] += leaked_pr / N

return scores
```

### PaperRank Stable Compute

The following pseudocode describes the function that will be used to compute stable PaperRank scores for a given list of IDs, `id_list`.

```python
N = len(id_list)
episilon = config.get_epsilon()  # Probably 10^(-4)

scores_old = list(value=(1/N), length=N)

stable = False

while not stable:
    scores_new = PaperRankIterationCompute(id_list)

    stable = sum(absolute(scores_new - scores_old)) < epsilon

    scores_old = copy(scores_new)
```


## `Manager` Sub-Module

The following pseudocode describes the logic of the `Manager` sub-module:

```python
full_id_list = util.getSortedIDList()
N = len(full_id_list)

for idx in range(N):
    current_subset = full_id_list[0:idx]
    PaperRankStableCompute(current_subset)
```

***PubMed Implementation Specific Information***

We can capitalize on the ordered nature of the IDs to simply iterate backwards from a sufficiently high number, to capture all of the IDs. This will reduce the amount of pre-processing required.
