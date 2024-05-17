import httpx
from fastapi import APIRouter, Request, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse
from pydantic import BaseModel
from datetime import date

router = APIRouter()
from .containers import getContainer

class InviteData(BaseModel):
    event: int
    title: str
    date: date
    organizer: str
    private: str
    status: str

templates = Jinja2Templates(directory="project/templates")

@router.get("")
async def home(request: Request):
    """
    Display the home page with public events.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: Renders the home page template.
    """
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/web/login", status_code=303)

    feedback = {
        'category': request.cookies.get("feedback_category"),
        'message': request.cookies.get("feedback_message")
    }

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{getContainer()}/events/public")

    if resp.status_code == 200:
        events = resp.json().get("events")
        response = templates.TemplateResponse('home.html', {
            "request": request,
            "username": username,
            "feedback": feedback,
            "events": events
        })
    else:
        response = templates.TemplateResponse('home.html', {
            "request": request,
            "username": username,
            "feedback": feedback,
            "error_message": resp.json().get("detail")
        })

    response.delete_cookie("feedback_message")
    response.delete_cookie("feedback_category")
    return response

@router.post("/event")
async def create_event(request: Request, title: str = Form(...), description: str = Form(...), date: str = Form(...), publicprivate: str = Form(...), invites: str = Form(...)):
    """
    Create an event and send out invites.

    Args:
        request (Request): The HTTP request object.
        title (str): The title of the event.
        description (str): The description of the event.
        date (str): The date of the event.
        publicprivate (str): The privacy status of the event.
        invites (str): A list of invitees.

    Returns:
        RedirectResponse: Redirects to the home page with feedback.
    """
    async with httpx.AsyncClient() as client:
        data_event = {
            "title": title,
            "organizer": request.cookies.get("username"),
            "date": date,
            "private": publicprivate,
            "text": description,
        }

        resp = await client.post(f"{getContainer()}/events", data=data_event)
        if resp.status_code == 200:
            event_id = resp.json().get("event_id")
            data_invites = {
                "event_id": event_id,
                "title": data_event.get('title'),
                "organizer": data_event.get('organizer'),
                "date": data_event.get('date'),
                "private": data_event.get('private'),
                "usernames": invites
            }
            resp = await client.post(f"{getContainer()}/invites", data=data_invites)
            response = RedirectResponse(url="/web", status_code=303)
            feedback_message = ""

            if resp.status_code == 422:
                feedback_message += resp.json().get("detail")

            data_calendar = {
                "event_id": event_id,
                "title": data_event.get('title'),
                "date": data_event.get('date'),
                "organizer": data_event.get('organizer'),
                "private": data_event.get('private'),
                "username": data_event.get('organizer'),
                "status": "Participate"
            }
            resp = await client.post(f"{getContainer()}/calendar", data=data_calendar)

            if resp.status_code == 200 and not feedback_message:
                response.set_cookie("feedback_category", "success")
                response.set_cookie("feedback_message", "Successfully created event! Everyone is invited! Event is added to your calendar!")
            else:
                feedback_message += resp.json().get("detail")
                response.set_cookie("feedback_category", "danger")
                response.set_cookie("feedback_message", feedback_message)

            return response
        else:
            response = RedirectResponse(url="/web", status_code=303)
            response.set_cookie("feedback_category", "danger")
            response.set_cookie("feedback_message", resp.json().get("detail"))
            return response

@router.get("/calendar")
@router.post('/calendar')
async def calendar(request: Request):
    """
    Retrieve and display a user's calendar.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: Renders the calendar page template.
    """
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/web/login", status_code=303)

    calendar_user = username
    success = None
    no_result = None
    calendar = None

    if request.method == 'POST':
        form = await request.form()
        calendar_user = form.get('calendar_user', username)

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{getContainer()}/calendar/{calendar_user}?asker={username}")

        if resp.status_code == 200:
            calendar = resp.json().get("events")
            success = True
        elif resp.status_code == 404:
            no_result = True
        elif resp.status_code in [401, 500]:
            success = False

    return templates.TemplateResponse('calendar.html', {
        "request": request,
        "username": username,
        "calendar_user": calendar_user,
        "calendar": calendar,
        "success": success,
        "no_result": no_result
    })

@router.get('/share')
@router.post('/share')
async def share_page(request: Request):
    """
    Share a user's calendar with another user.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: Renders the share page template.
    """
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/web/login", status_code=303)

    if request.method == 'POST':
        form = await request.form()
        share_user = form.get('username')
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{getContainer()}/calendar/share?owner={username}&shared={share_user}")
            success = resp.status_code == 200
            return templates.TemplateResponse('share.html', {
                "request": request,
                "username": username,
                "success": success
            })

    return templates.TemplateResponse('share.html', {
        "request": request,
        "username": username,
        "success": None
    })

@router.get('/event/{event_id}')
async def view_event(request: Request, event_id: int):
    """
    Retrieve and display details for a specific event.

    Args:
        request (Request): The HTTP request object.
        event_id (int): The ID of the event.

    Returns:
        TemplateResponse: Renders the event details page template.
    """
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/web/login", status_code=303)

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{getContainer()}/events/event/{event_id}?username={username}")

    if resp.status_code == 200:
        event = resp.json().get('event')
        return templates.TemplateResponse('event.html', {
            "request": request,
            "username": username,
            "event": event,
            "success": True
        })
    else:
        return templates.TemplateResponse('event.html', {
            "request": request,
            "username": username,
            "event": None,
            "success": False,
            "event_failed": True,
            "error_message": resp.json().get('detail')
        })

@router.get('/login')
@router.post('/login')
async def login(request: Request):
    """
    Handle user login.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: Renders the login page template.
    """
    if request.method == 'GET':
        return templates.TemplateResponse('login.html', {"request": request, "username": None})

    form_data = await request.form()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{getContainer()}/users/authenticate", data=form_data)

    if resp.status_code == 200:
        username = resp.json().get('username')
        response = RedirectResponse(url="/web", status_code=303)
        response.set_cookie(key="username", value=username, max_age=3600, expires=3600, httponly=True, samesite='strict')
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "login_failed": True,
            "login_error_message": resp.json().get('detail')
        })

@router.get('/register')
@router.post("/register")
async def register(request: Request):
    """
    Handle user registration.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: Renders the registration page template.
    """
    if request.method == 'GET':
        return templates.TemplateResponse('login.html', {"request": request, "username": None})

    form_data = await request.form()
    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{getContainer()}/users", data=form_data)

    if resp.status_code == 200:
        username = resp.json().get('username')
        response = RedirectResponse(url="/web", status_code=303)
        response.set_cookie(key="username", value=username, max_age=3600, expires=3600, httponly=True, samesite='strict')
        return response
    else:
        return templates.TemplateResponse("login.html", {
            "request": request,
            "registration_failed": True,
            "registration_error_message": resp.json().get('detail')
        })

@router.get('/invites')
async def invites(request: Request):
    """
    Retrieve and display user invites.

    Args:
        request (Request): The HTTP request object.

    Returns:
        TemplateResponse: Renders the invites page template.
    """
    username = request.cookies.get("username")
    if not username:
        return RedirectResponse(url="/web/login", status_code=303)

    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{getContainer()}/invites/{username}")

    if resp.status_code == 200:
        invites = resp.json().get('invites')
        return templates.TemplateResponse('invites.html', {
            "request": request,
            "username": username,
            "invites": invites
        })
    else:
        error = resp.json().get('detail')
        return templates.TemplateResponse('invites.html', {
            "request": request,
            "username": username,
            "error_message": error
        })

@router.post("/invites")
async def handle_invite(request: Request, data: InviteData):
    """
    Handle user response to invites.

    Args:
        request (Request): The HTTP request object.
        data (InviteData): The invite data.

    Returns:
        JSONResponse: JSON response with feedback message.
    """
    username = request.cookies.get("username")
    if not username:
        return JSONResponse(status_code=303, content={"message": "Redirecting to login"})

    feedback = {"category": "", "message": ""}

    if data.status == "Don't Participate":
        async with httpx.AsyncClient() as client:
            resp = await client.delete(f"{getContainer()}/invites?event_id={data.event}&username={username}")
            if resp.status_code == 200:
                feedback = {"category": "success", "message": "Your decline of the invite has been successfully registered"}
            else:
                feedback = {"category": "danger", "message": resp.json().get("detail")}
            return JSONResponse(status_code=resp.status_code, content=feedback)

    async with httpx.AsyncClient() as client:
        resp = await client.post(f"{getContainer()}/events/participant?event_id={data.event}&username={username}&status={data.status}")

    feedback_message = ""
    if resp.status_code in [200, 409]:
        async with httpx.AsyncClient() as client:
            delete_resp = await client.delete(f"{getContainer()}/invites?event_id={data.event}&username={username}")
            if delete_resp.status_code != 200:
                feedback_message += delete_resp.json().get("detail")

        data_calendar = {
            "event_id": data.event,
            "title": data.title,
            "date": data.date,
            "organizer": data.organizer,
            "private": data.private,
            "username": username,
            "status": data.status
        }
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{getContainer()}/calendar", data=data_calendar)

            if resp.status_code == 200 and not feedback_message:
                feedback = {"category": "success", "message": "Participation has been successfully registered and event is added to your calendar!"}
            else:
                feedback_message += resp.json().get("detail")

    if resp.status_code == 500:
        feedback = {"category": "danger", "message": resp.json().get("detail")}

    if not feedback:
        feedback = {"category": "danger", "message": feedback_message}

    return JSONResponse(status_code=resp.status_code, content=feedback)

@router.get("/logout")
async def logout():
    """
    Handle user logout by clearing the session.

    Returns:
        RedirectResponse: Redirects to the login page.
    """
    response = RedirectResponse(url="/web/login", status_code=303)
    response.set_cookie("username", "", expires=0)
    return response
