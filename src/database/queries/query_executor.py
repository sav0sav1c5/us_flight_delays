import time

def execute_query(collection, pipeline, query_name, verbose = True):
    """
    Executes an aggregation pipeline on a MongoDB collection and measures execution time.

    Returns tuple of query results and execution time in seconds.
    """

    start_time = time.time()
    results = collection.aggregate(pipeline)
    end_time = time.time()

    execution_time = end_time - start_time
    query_results = list(results)

    if verbose:
        print(f"Query '{query_name}' executed in {execution_time:.4f} seconds")
        
    return query_results, execution_time 