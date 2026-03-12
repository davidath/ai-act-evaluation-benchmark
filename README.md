# AI Act Evaluation Benchmark: An Open, Transparent, and Reproducible Evaluation Dataset for NLP and RAG Systems
Open dataset for evaluating NLP/RAG systems on EU AI Act compliance. Features risk-level classification, article retrieval, obligation generation, and QA tasks.

# Data Overview

### Scenarios

The `scenarios.json` file contains structured data for EU AI Act compliance scenarios. 

Each scenario includes:
- Role: The entity responsible for the AI system (Provider/Deployer).
- Intended Use: The purpose of the AI system.
- System Type: The type of AI system.
- Input Data: The data used by the AI system.
- Domain: The domain in which the AI system operates.
- Related Articles: Articles related to the scenario.
- Obligations: Compliance obligations for the scenario.

### QA Pairs
The `qa_pairs.json` file contains question-answer pairs related to EU AI Act.

# Usage
To use this repository, follow the steps outlined in the [tutorial file](./documentation/tutorial.md). Ensure that all configurations are correctly set up before running the scripts.

# License
The JSON files are licensed under Creative Commons Attribution 4.0 International (CC-BY-4.0). The script code is provided under the Apache License 2.0.

# Citation
If you use this dataset, cite the [paper](https://arxiv.org/abs/2603.09435):
```
@article{Davvetas2026,
  title   = {AI Act Evaluation Benchmark: An Open, Transparent, and Reproducible Evaluation Dataset for NLP and RAG Systems},
  author  = {Athanasios Davvetas and Michael Papademas and Xenia Ziouvelou and Vangelis Karkaletsis},
  journal = {arXiv preprint arXiv:2603.09435},
  year    = {2026}
}
```
