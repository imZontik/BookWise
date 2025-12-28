from prometheus_client import Histogram

REDIS_OPERATION_SECONDS = Histogram(
    "redis_operation_seconds",
    "Время, потраченнное на операции в Redis",
    ["op", "status"],
    buckets=(
        0.0005, 0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5
    )
)


DATABASE_QUERY_SECONDS = Histogram(
    "db_query_duration_seconds",
    "Время выполнения SQL-запросов",
    buckets=(0.001, 0.0025, 0.005, 0.01, 0.025, 0.05, 0.1, 0.25, 0.5, 1, 2, 5, 10),
)