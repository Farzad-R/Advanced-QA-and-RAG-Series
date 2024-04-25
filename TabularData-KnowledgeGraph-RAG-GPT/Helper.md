Pipeline workflow #1:
1. Load the csv file
2. Add `taglines` column
3. Prepare Neo4j GraphDB for Q&A:
    - Start the graph
    - Create the knowledge graph schema query
    - Create vector index in the graph
    - Embed the tagline column and store the embedding values (List) in the vector index 