# main.py
from fastapi import FastAPI, Depends, Request, Form
from fastapi.responses import HTMLResponse,RedirectResponse
from fastapi.templating import Jinja2Templates
from db import getDB,lifespan
from datetime import date

#from routes import router as all_routes
#from routes.upload import router as upload_router
#from routes import users


templates = Jinja2Templates(directory="templates")
app = FastAPI(lifespan=lifespan)

# Include the router
# app.include_router("routes/r", prefix="/") #mount every thing from ./routes/ to url under prefix

@app.get("/students/list")
async def read_users(db=Depends(getDB)):
	cur=await db.execute("SELECT * FROM students")
	return await cur.fetchall()


@app.get("/students/list/template")
async def stuList(request: Request, db=Depends(getDB)):
    cur = await db.execute("SELECT * FROM students ORDER BY stuid")
    data = await cur.fetchall()

    return templates.TemplateResponse(
        name="studentList.html",
        request=request,
        context={"students": data}
    )

@app.get("/student/edit/{stuid}")
async def stuEdit(stuid:int,request:Request, db=Depends(getDB)):
	cur=await db.execute("SELECT * FROM students where stuid=%s",(stuid,))
	data= await cur.fetchone()
	return templates.TemplateResponse(name="studentEdit.html", request=request,context={"data": data})


@app.post("/student/update")
async def stuUpdate(
    stuid: int = Form(...),
    name: str | None = Form(None),
    id: str | None = Form(None),
    height: int | None = Form(None),
    weight: int | None = Form(None),
    math: int | None = Form(None),
    english: int | None = Form(None),
    chinese: int | None = Form(None),
    birthday: date | None = Form(None),
    iq: int | None = Form(None),
    city: str | None = Form(None),
    mentor: str | None = Form(None),
    db=Depends(getDB)
):
    await db.execute(
        """
        UPDATE students
        SET name=%s,
            id=%s,
            height=%s,
            weight=%s,
            math=%s,
            english=%s,
            chinese=%s,
            birthday=%s,
            iq=%s,
            city=%s,
            mentor=%s
        WHERE stuid=%s
        """,
        (name, id, height, weight, math,
         english, chinese, birthday, iq,
         city, mentor, stuid)
    )

    await db.commit()

    return RedirectResponse(
        url="/students/list/template",
        status_code=303
    )

@app.post("/student/delete")
async def stuDelete(stuid: int = Form(...), db=Depends(getDB)):
    await db.execute(
        "DELETE FROM students WHERE stuid=%s",
        (stuid,)
    )
    await db.commit()

    return RedirectResponse(
        url="/students/list/template",
        status_code=303
    )
    

@app.get("/student/add")
async def stuAdd(request: Request):
    return templates.TemplateResponse(
        name="studentAdd.html",
        request=request
    )

@app.post("/student/add")
async def stuInsert(
    stuid: int = Form(...),
    name: str | None = Form(None),
    id: str | None = Form(None),
    height: int | None = Form(None),
    weight: int | None = Form(None),
    math: int | None = Form(None),
    english: int | None = Form(None),
    chinese: int | None = Form(None),
    birthday: date | None = Form(None),
    iq: int | None = Form(None),
    city: str | None = Form(None),
    mentor: str | None = Form(None),
    db=Depends(getDB)
):
    await db.execute(
        """
        INSERT INTO students
        (stuid, name, id, height, weight, math,
         english, chinese, birthday, iq, city, mentor)
        VALUES
        (%s, %s, %s, %s, %s, %s,
         %s, %s, %s, %s, %s, %s)
        """,
        (stuid, name, id, height, weight, math,
         english, chinese, birthday, iq, city, mentor)
    )

    await db.commit()

    return RedirectResponse(
        url="/students/list/template",
        status_code=303
    )