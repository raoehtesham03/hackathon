
import elasticsearch

es_client= elasticsearch.Elasticsearch(
    hosts=["http://localhost:9200"],
    max_retries=2,
)