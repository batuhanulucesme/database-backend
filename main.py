from fastapi import FastAPI, Request, Form, status, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from pymongo import MongoClient
from .auth import authenticate_user

app = FastAPI()
templates = Jinja2Templates(directory="frontend")

# Connect to MongoDB
client = MongoClient("mongodb://localhost:27017")
db = client['inventory']
equipments_collection = db['equipments']
users_collection = db["users"]

# Correctly mount the static files directory
app.mount("/frontend", StaticFiles(directory="frontend"), name="frontend")

@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    return RedirectResponse(url="/login")

@app.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    return templates.TemplateResponse("login.html", {"request": request})

@app.post("/login")
async def login(request: Request, username: str = Form(...), password: str = Form(...)):
    try:
        user = authenticate_user(username, password)
        if not user:
            return templates.TemplateResponse("login.html", {"request": request, "error": "Invalid credentials"})
        response = RedirectResponse(url="/index", status_code=status.HTTP_302_FOUND)
        response.set_cookie(key="user_id", value=str(user["_id"]))
        response.set_cookie(key="user_email", value=user["email"])  # Assuming user object has an email attribute
        response.set_cookie(key="user_name", value=user["name"])  # Assuming user object has a name attribute
        return response
    except Exception as e:
        print(f"Login error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

# @app.get("/index", response_class=HTMLResponse)
# async def index(request: Request):
#     user_email = request.cookies.get("user_email")
    
#     query = {"owner": user_email}
#     # Fetch the documents
#     equipments = equipments_collection.find(query)

#     # Print the fetched documents
#     for equipment in equipments:
#         print(equipment)
    
#     if not user_email:
#         return RedirectResponse(url="/login")
#     return templates.TemplateResponse("index.html", {"request": request, "user_email": user_email})

@app.get("/index", response_class=HTMLResponse)
async def index(request: Request):
    user_email = request.cookies.get("user_email")
    
    if not user_email:
        return RedirectResponse(url="/login")

    query = {"owner": user_email}
    equipments = list(equipments_collection.find(query))

    return templates.TemplateResponse("index.html", {"request": request, "user_email": user_email, "equipments": equipments})






@app.get("/api/equipment")
async def get_user_equipment(request: Request, page: int = 1, per_page: int = 10, sort_field: str = '_id', sort_order: int = 1):
    try:
        user_email = request.cookies.get("user_email")
        if not user_email:
            raise HTTPException(status_code=401, detail="Unauthorized")

        total_count = equipments_collection.count_documents({"owner": user_email})
        equipments = equipments_collection.find({"owner": user_email}) \
                                         .sort(sort_field, sort_order) \
                                         .skip((page - 1) * per_page) \
                                         .limit(per_page)

        equipment_list = list(equipments)
        return {"data": equipment_list, "total_count": total_count, "per_page": per_page}
    except Exception as e:
        print(f"Error fetching equipment: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

@app.get("/logout", response_class=HTMLResponse)
async def logout(request: Request):
    response = RedirectResponse(url="/login")
    response.delete_cookie("user_id")
    response.delete_cookie("user_email")
    response.delete_cookie("user_name")
    return response

@app.get("/add_equipment", response_class=HTMLResponse)
async def add_equipment(request: Request):
    return templates.TemplateResponse("add_equipment.html", {"request": request})

@app.post("/submit_equipment")
async def submit_equipment(request: Request, 
                           name: str = Form(...), 
                           serial_num: str = Form(...), 
                           description: str = Form(...),
                           type: str = Form(...), 
                           department_num: str = Form(...), 
                           usage_location: str = Form(...), 
                           current_location: str = Form(...),
                           due_date: str = Form(...), 
                           purpose: str = Form(...)):
    try:
        user_email = request.cookies.get("user_email")
        user_name = request.cookies.get("user_name")
        if not user_email or not user_name:
            return RedirectResponse(url="/login")
        
        equipment = {
            "name": name,
            "serial_num": serial_num,
            "description": description,
            "type": type,
            "department_num": department_num,
            "usage_location": usage_location,
            "current_location": current_location,
            "due_date": due_date,
            "purpose": purpose,
            "owner": user_email,
            "owner_name": user_name
        }
        
        equipment.insert_one(equipment)
        return RedirectResponse(url="/index", status_code=status.HTTP_302_FOUND)
    except Exception as e:
        print(f"Submit equipment error: {e}")
        raise HTTPException(status_code=500, detail="Internal Server Error")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8001, reload=True)
