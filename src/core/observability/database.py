import time

from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncEngine

from src.core.observability.metrics import DATABASE_QUERY_SECONDS


def setup_db_timing(async_engine: AsyncEngine) -> None:
    eng = async_engine.sync_engine

    @event.listens_for(eng, "before_cursor_execute")
    def before_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        context._prom_start_time = time.perf_counter()

    @event.listens_for(eng, "after_cursor_execute")
    def after_cursor_execute(conn, cursor, statement, parameters, context, executemany):
        start = getattr(context, "_prom_start_time", None)
        if start is None:
            return
        DATABASE_QUERY_SECONDS.observe(time.perf_counter() - start)

    @event.listens_for(eng, "handle_error")
    def handle_error(exception_context):
        ctx = exception_context.execution_context
        start = getattr(ctx, "_prom_start_time", None) if ctx is not None else None
        if start is None:
            return
        DATABASE_QUERY_SECONDS.observe(time.perf_counter() - start)