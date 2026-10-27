# main.py
from fastapi import FastAPI, Depends
from db import getDB,lifespan
#from routes import router as all_routes
#from routes.upload import router as upload_router
#from routes import users
app = FastAPI(lifespan=lifespan)

# Include the router
#app.include_router(upload_router, prefix="/file")

#app.include_router(all_routes)
#app.include_router(users.router)
@app.get("/users")
async def read_users(db=Depends(getDB)):
    cur=await db.execute("SELECT * FROM users")
    return await cur.fetchall()
