import elasticsearch

def create_es_client(host):
    es_client = elasticsearch.Elasticsearch(
        hosts=[host],
        max_retries=2,
    )
    return es_client