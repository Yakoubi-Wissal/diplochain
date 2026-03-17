from database import get_db
from sqlalchemy import text
import asyncio

async def test():
    async with get_db().__anext__() as db:
        try:
            res = await db.execute(text("SELECT fn_refresh_dashboard_metrics(CURRENT_DATE)"))
            print("executed", res)
        except Exception as e:
            print("error", e)

asyncio.run(test())
