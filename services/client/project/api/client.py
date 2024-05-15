import httpx
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from fastapi import HTTPException
import requests
import typing
from icecream import ic

from pydantic import BaseModel

router = APIRouter()

from .containers import getContainer

class ThingModel(BaseModel):
    id: typing.Optional[int]
    text: str

templates = Jinja2Templates(directory="project/templates")

# Username & Password of the currently logged-in user
username = None
password = None

session_data = dict()

def save_to_session(key, value):
    session_data[key] = value

def load_from_session(key):
    return session_data.pop(key) if key in session_data else None

@router.get("")
async def home(request: Request):
    username = request.cookies.get("username")
    if username is None or username == "":
        return RedirectResponse(url="/web/login", status_code=303)

    feedback = {'category': request.cookies.get("feedback_category"),
                'message': request.cookies.get("feedback_message")}

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{getContainer()}/events/public")

    if resp.status_code == 200:
        events = resp.json().get("events")
        ic(events)
        response = templates.TemplateResponse('home.html', {
            "request": request,
            "username": username,
            "feedback": feedback,
            "events": events
        })
        response.delete_cookie("feedback_message")
        response.delete_cookie("feedback_category")
        return response
    elif resp.status_code == 404 or resp.status_code == 500:
        response = templates.TemplateResponse('home.html', {
            "request": request,
            "username": username,
            "feedback": feedback,
            "error_message": resp.json().get("detail")
        })
        response.delete_cookie("feedback_message")
        response.delete_cookie("feedback_category")
        return response
    # Delete the feedback cookies

@router.post("/event")
async def create_event(request: Request, title: str = Form(...), description: str = Form(...), date: str = Form(...), publicprivate: str = Form(...), invites: str = Form(...)):
    #==========================
    # FEATURE (create an event)
    #
    # Given some data, create an event and send out the invites.
    #==========================
    # Event creation logic would go here
    async with httpx.AsyncClient() as client:
        data = {
            "title": title,
            "organizer": request.cookies.get("username"),
            "date": date,
            "private": publicprivate,
            "text": description,
        }

        resp = await client.post(f"{getContainer()}/events", data=data)
        if resp.status_code == 200:
            response = RedirectResponse(url="/web", status_code=303)
            response.set_cookie("feedback_category", "success")
            response.set_cookie("feedback_message","Successfully created event!")
            return response
        elif resp.status_code == 409:
            response = RedirectResponse(url="/web", status_code=303)
            response.set_cookie("feedback_category", "danger")
            response.set_cookie("feedback_message", resp.json().get("detail"))
            return response
        elif resp.status_code == 500:
            response = RedirectResponse(url="/web", status_code=303)
            response.set_cookie("feedback_category", "danger")
            response.set_cookie("feedback_message", resp.json().get("detail"))
            return response





@router.get("/calendar")
@router.post('/calendar')
async def calendar(request: Request):
    # ================================
    # FEATURE (calendar based on username)
    #
    # Retrieve the calendar of a certain user. The webpage expects a list of (id, title, date, organizer, status, Public/Private) tuples.
    # Try to keep in mind failure of the underlying microservice
    # =================================
    username = request.cookies.get("username")
    if username == None or username == "":
        return RedirectResponse(url="/web/login", status_code=303)
    elif request.method == 'POST':
        form = await request.form()
        calendar_user = form.get('calendar_user', username)
    else:
        calendar_user = username
    success = True  # Assume success for placeholder
    if success:
        calendar = [(1, 'Test event', 'Tomorrow', 'Benjamin', 'Going', 'Public')]  # Placeholder data
    else:
        calendar = None
    return templates.TemplateResponse('calendar.html', {"request": request, "username": username, "password": password, "calendar_user": calendar_user, "calendar": calendar, "success": success})

@router.get('/share')
@router.post('/share')
async def share_page(request: Request):
    #========================================
    # FEATURE (share a calendar with a user)
    #
    # Share your calendar with a certain user. Return success = true / false depending on whether the sharing is successful.
    #========================================
    username = request.cookies.get("username")
    if username == None or username == "":
        return RedirectResponse(url="/web/login", status_code=303)
    elif request.method == 'POST':
        form = await request.form()
        share_user = form.get('username')
        success = True  # Placeholder for sharing logic
    else:
        success = None
    return templates.TemplateResponse('share.html', {"request": request, "username": username, "success": success})

@router.get('/event/{event_id}')
async def view_event(request: Request, event_id: int):
    # ================================
    # FEATURE (event details)
    #
    # Retrieve additional information for a certain event parameterized by an id. The webpage expects a (title, date, organizer, status, (invitee, participating)) tuple.
    # Try to keep in mind failure of the underlying microservice
    # =================================
    username = request.cookies.get("username")
    if username == None or username == "":
        return RedirectResponse(url="/web/login", status_code=303)
    # success = True  # Placeholder for checking access to event details
    # if success:
    #     event = ['Test event', 'Tomorrow', 'Benjamin', 'Public',
    #              [['Benjamin', 'Participating'], ['Fabian', 'Maybe Participating']]]  # Placeholder event details
    # else:
    #     event = None
    # return templates.TemplateResponse('event.html',
    #                                   {"request": request, "username": username, "password": password, "event": event,
    #                                    "success": success})

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{getContainer()}/events/event/{event_id}?username={username}")
    if resp.status_code == 200:
        event = resp.json().get('event')
        ic(event)
        return templates.TemplateResponse('event.html', {"request": request, "username": username,
                                                         "event": event, "success": True})

    elif resp.status_code == 401:
        return templates.TemplateResponse('event.html', {"request": request, "username": username, "event": None,
                                                         "success": False, "event_failed": True, "error_message": resp.json().get('detail')})
    elif resp.status_code == 404:
        return templates.TemplateResponse('event.html', {"request": request, "username": username, "event": None,
                                                         "success": False, "event_failed": True, "error_message": resp.json().get('detail')})

    elif resp.status_code == 500:
        return templates.TemplateResponse('event.html', {"request": request, "username": username,
                                                         "success": False, "event_failed": True, "error_message": resp.json().get('detail')})

@router.get('/login')
@router.post('/login')
async def login(request: Request):
    # ================================
    # FEATURE (login)
    #
    # send the username and password to the microservice
    # microservice returns True if correct combination, False if otherwise.
    # Also pay attention to the status code returned by the microservice.
    # ================================
    if request.cookies.get("username") != None and request.cookies.get("username") != "":
        return RedirectResponse(url="/web", status_code=303)
    elif request.method == 'GET':
        return templates.TemplateResponse('login.html', {"request": request, "username": None})
    elif request.method == 'POST':
        form_data = await request.form()
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{getContainer()}/users/authenticate", data=form_data)  # Placeholder for actual authentication logic
        if resp.status_code == 200:
            username = resp.json().get('username')
            response = RedirectResponse(url="/web", status_code=303)
            response.set_cookie(
                key="username",
                value=username,
                max_age=3600,
                expires=3600,
                httponly=True,
                samesite='strict'
            )
            return response
        elif resp.status_code == 401:
            # Here we need to render login.html with an error message
            return templates.TemplateResponse("login.html", {
                "request": request,
                "login_failed": True,
                "login_error_message": resp.json().get('detail')
            })
        elif resp.status_code == 500:
            return templates.TemplateResponse("login.html", {
                "request": request,
                "login_failed": True,
                "login_error_message": resp.json().get('detail')
            })

@router.get('/register')
@router.post("/register")
async def register(request: Request):
    # ================================
    # FEATURE (register)
    #
    # send the username and password to the microservice
    # microservice returns True if registration is successful, False if otherwise.
    #
    # Registration is successful if a user with the same username doesn't exist yet.
    # ================================
    if request.cookies.get("username") != None and request.cookies.get("username") != "":
        return RedirectResponse(url="/web", status_code=303)
    elif request.method == 'GET':
        return templates.TemplateResponse('login.html', {"request": request, "username": None})
    elif request.method == 'POST':
        form_data = await request.form()
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{getContainer()}/users", data=form_data)
        if resp.status_code == 200:
            username = resp.json().get('username')
            response = RedirectResponse(url="/web", status_code=303)
            response.set_cookie(
                key="username",
                value=username,
                max_age=3600,
                expires=3600,
                httponly=True,
                samesite='strict'
            )
            return response
        elif resp.status_code == 409:  # Assuming 409 Conflict for existing username
            # Here we need to render login.html with a registration error message about existing username
            return templates.TemplateResponse("login.html", {
                "request": request,
                "registration_failed": True,
                "registration_error_message": resp.json().get('detail')
            })
        elif resp.status_code == 500:
            # General error handling
            return templates.TemplateResponse("login.html", {
                "request": request,
                "registration_failed": True,
                "registration_error_message": resp.json().get('detail')
            })

@router.get('/invites')
@router.post('/invites')
async def invites(request: Request):
    #==============================
    # FEATURE (list invites)
    #
    # retrieve a list with all events you are invited to and have not yet responded to
    #==============================
    if request.cookies.get("username") == None or request.cookies.get("username") == "":
        return RedirectResponse(url="/web/login", status_code=303)
    elif request.method == 'GET':
        my_invites = [(1, 'Test event', 'Tomorrow', 'Benjamin', 'Private')]  # Placeholder data
        return templates.TemplateResponse('invites.html', {"request": request, "username": username, "password": password, "invites": my_invites})
    else:
        # Process invite logic here
        return RedirectResponse(url="/invites", status_code=303)

@router.get("/logout")
async def logout():
    #==================render_template============
    # FEATURE (logout)
    #
    # Clear the current session and redirect to the login page.
    #==============================
    response = RedirectResponse(url="/web", status_code=303)
    response.set_cookie("username", "", expires=0)

    return response
