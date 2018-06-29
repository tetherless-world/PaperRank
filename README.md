# PaperRank


|[Architecture Overview](https://docs.google.com/document/d/1U7CSw3BXnk3Qb4DK-jvoeL0mj4tLFNIWwyveFmQ7_y0/edit?usp=sharing)|
|---|

## Configuration Files

This system ingests configuration files in JSON from the `config/` folder in the parent directory. The configuration file ingestion engine (`PaperRank/utils/configuration.py`) builds an initial set of base configuration parametrs from `config/base.json`.

### Overriding Parameters

- Parameters in `config/base.json` can be overriden by passing an additional argument to the setup function with the name of the JSON file to be used (i.e. `PaperRank.config.setup(override='default.json')`, with the file being placed in `config/default.json`).
- The JSON file `config/default.json` must follow the same structure as `config/base.json`.

### Redis Database Mapping Configuration

|Name|Redis DB Number|Type|Description|
|:-------------------:|:--:|:--:|:----------|
|LOG|0|Pipe|Error log|
|OUT|1|Set|Outbound citation mapping|
|SEEN|2|Set|Set of PubMed IDs and nodes already seen|
|GRAPH|3|List|List of tuples that model the citation graph|
|EXPLORE|4|Set|Exploration frontier|
|INSTANCE|5|Set|Instance node set|
|NOT|6|Set|Set of non-pubmed citations|
