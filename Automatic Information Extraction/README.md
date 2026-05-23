## Project Introduction:
This project explores an automated approach for extracting binary relational patterns from Wikipedia text by leveraging structured knowledge from DBpedia and unstructured Wikipedia content. The goal is to identify how semantic relations (e.g., birthDate, writer, language) are expressed in natural language and to build reusable linguistic patterns for downstream NLP tasks.

## Project Objective:
To automatically discover high-quality textual patterns that express structured relationships between entities, enabling improvements in:
* Information Extraction (IE)
* Question Answering (QA)
* Knowledge Base Population (KBP)

## Methodology:
The pipeline follows a three-stage process:
1. Data Preparation
* Wikipedia dump is processed to build a clean text corpus.
* Relations and entity mappings are sourced from DBpedia ontology.
2. Sentence Extraction
* Sentences containing both domain and range entities of a relation are identified.
* Uses exact, relaxed, and token-based matching to improve recall.
3. Pattern Learning
* Sentences are generalized using semantic types (e.g., PERSON, DATE).
* Suffix tree–based longest common substring extraction is used to derive relational patterns.
* Example pattern:
`[PERSON] was born on [DATE]` 

![image alt](https://github.com/KKGHOSE2021/Python-Projects/blob/612bec841b3b51c302ba001f9161cb985cec3622/Automatic%20Information%20Extraction/framework.png)

Figure: An overview of the  Wiki relation pattern extraction framework.

## Evaluation:
* Evaluated on multiple DBpedia relations (e.g., birthDate, writer, language).
* Performance measured using precision, recall, and F1-score for:
  - Sentence extraction
  - Pattern extraction
* Results show strong performance for high-frequency, well-structured relations, while sparse relations remain challenging.
  ![image alt](https://github.com/KKGHOSE2021/Python-Projects/blob/612bec841b3b51c302ba001f9161cb985cec3622/Automatic%20Information%20Extraction/result.png)
  Table: Results of sentence and pattern evaluation. 
                                  
## Key Contributions:
* A scalable, mostly language-independent pipeline for relation pattern mining.
* Integration of structured knowledge (DBpedia) with unstructured text (Wikipedia).
* Demonstration of how redundancy between infoboxes and text improves extraction quality.
* Analysis of factors affecting extraction performance (relation frequency, datatype vs entity relations).

## Potential Applications:
* Knowledge graph construction
* Open-domain question answering systems
* Automated ontology population
* Semantic search enhancement
