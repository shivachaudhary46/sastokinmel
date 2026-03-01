import torch
from ..config import settings
from elastic_transport import ObjectApiResponse
from fastapi import APIRouter
from fastapi.responses import HTMLResponse
from sentence_transformers import SentenceTransformer
from ..utilities.utils import get_es_client
from ..loggers.logger import logger 

router = APIRouter(
    prefix="/search",
    tags=["search"]
)

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model = SentenceTransformer("all-MiniLM-L6-v2").to(device)

def get_total_hits(response: ObjectApiResponse) -> int:
    logger.info(f"Total hits from response {response['hits']['total']['value']}")
    return response["hits"]["total"]["value"]

def calculate_max_pages(total_hits: int, limit: int) -> int:
    logger.info(f"Maximum pages can be sent {(total_hits + limit - 1) // limit}")
    return (total_hits + limit - 1) // limit

def extract_docs_per_year(response: ObjectApiResponse) -> dict:
    aggregations = response.get("aggregations", {})
    docs_per_year = aggregations.get("docs_per_year", {})
    buckets = docs_per_year.get("buckets", [])
    logger.info(f"Successfully extracted docs per year")
    return {bucket["key_as_string"]: bucket["doc_count"] for bucket in buckets}

def handle_error(e: Exception) -> HTMLResponse:
    error_message = f"An error occurred: {str(e)}"
    logger.error("Error occured and HTMLResponse is going to handle it {e}")
    return HTMLResponse(content=error_message, status_code=500)

@router.get("/regular_search/")
async def regular_search(
    search_query: str,
    skip: int = 0,
    limit: int = 10,
    year: str | None = None,
    tokenizer: str = "Standard",
) :
    try:
        es = get_es_client(max_retries=1, sleep_time=0)
        query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": search_query,
                            "fields": ["title", "explanation"],
                        }
                    }
                ]
            }
        }

        if year:
            query["bool"]["filter"] = [
                {
                    "range": {
                        "date": {
                            "gte": f"{year}-01-01",
                            "lte": f"{year}-12-31",
                            "format": "yyyy-MM-dd",
                        }
                    }
                }
            ]

        index_name = (
            settings.INDEX_NAME_DEFAULT if tokenizer == "Standard" else settings.INDEX_NAME_N_GRAM
        )
        response = es.search(
            index=index_name,
            body={
                "query": query,
                "from": skip,
                "size": limit,
            },
            filter_path=[
                "hits.hits._source",
                "hits.hits._score",
                "hits.total",
            ],
        )

        total_hits = get_total_hits(response)
        max_pages = calculate_max_pages(total_hits, limit)

        return {
            "hits": response["hits"].get("hits", []),
            "max_pages": max_pages,
        }
    except Exception as e:
        return handle_error(e)

@router.get("/semantic_search/")
async def semantic_search(
    search_query: str, skip: int = 0, limit: int = 10, year: str | None = None
) :
    try:
        es = get_es_client(max_retries=1, sleep_time=0)
        embedded_query = model.encode(search_query)

        query = {
            "bool": {
                "must": [
                    {
                        "knn": {
                            "field": "embedding",
                            "query_vector": embedded_query,
                            # Because we have 3333 documents, we can return them all.
                            "k": 1e4,
                        }
                    }
                ]
            }
        }

        if year:
            query["bool"]["filter"] = [
                {
                    "range": {
                        "date": {
                            "gte": f"{year}-01-01",
                            "lte": f"{year}-12-31",
                            "format": "yyyy-MM-dd",
                        }
                    }
                }
            ]

        response = es.search(
            index=settings.INDEX_NAME_EMBEDDING,
            body={
                "query": query,
                "from": skip,
                "size": limit,
            },
            filter_path=[
                "hits.hits._source",
                "hits.hits._score",
                "hits.total",
            ],
        )

        total_hits = get_total_hits(response)
        max_pages = calculate_max_pages(total_hits, limit)

        return {
            "hits": response["hits"].get("hits", []),
            "max_pages": max_pages,
        }
    except Exception as e:
        return handle_error(e)

@router.get("/get_docs_per_year_count/")
async def get_docs_per_year_count(
    search_query: str, tokenizer: str = "Standard"
) :
    try:
        es = get_es_client(max_retries=1, sleep_time=0)
        query = {
            "bool": {
                "must": [
                    {
                        "multi_match": {
                            "query": search_query,
                            "fields": ["title", "explanation"],
                        }
                    }
                ]
            }
        }

        index_name = (
            settings.INDEX_NAME_DEFAULT if tokenizer == "Standard" else settings.INDEX_NAME_N_GRAM
        )
        response = es.search(
            index=index_name,
            body={
                "query": query,
                "aggs": {
                    "docs_per_year": {
                        "date_histogram": {
                            "field": "date",
                            "calendar_interval": "year",  # Group by year
                            "format": "yyyy",  # Format the year in the response
                        }
                    }
                },
            },
            filter_path=["aggregations.docs_per_year"],
        )
        return {"docs_per_year": extract_docs_per_year(response)}
    except Exception as e:
        return handle_error(e)
