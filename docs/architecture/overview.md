# PaperRank Architecture Overview

The PaperRank system architecture was designed to be highly modular, and easily extensible for use with different sources. Note that it is currently configured for use with the NCBI PubMed Database, but future work to include the [Microsoft Academic Graph (MAG)](https://www.microsoft.com/en-us/research/project/microsoft-academic-graph/) and the [Open Academic Graph (OAG)](https://aminer.org/open-academic-graph) is underway.

The main functionality of PaperRank is divided into two *engines*. The first, is the **update** engine, and the second is the **compute** engine. The **update** engine is responsible for utilizing the REST API of the target source to efficiently scrape the corpus metadata, and store it in a reusable format in a database. The **compute** engine is responsible for then ingesting this information from the database, parsing it correctly, and computing the actual PaperRanks for the papers in the corpus.

For more information on each of the modules, see:

1. [**Update** module](update_engine.md)
2. [**Compute** module](compute_engine.md)
