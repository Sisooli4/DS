import httpx
from fastapi import APIRouter, Request, Depends, Form
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse, JSONResponse

from fastapi import HTTPException
import requests
import typing
from icecream import ic

from pydantic import BaseModel
from datetime import date
router = APIRouter()

from .containers import getContainer

class InviteData(BaseModel):
    event: int
    title:str
    date:date
    organizer:str
    private:str
    status: str

templates = Jinja2Templates(directory="project/templates")

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

@router.post("/event")
async def create_event(request: Request, title: str = Form(...), description: str = Form(...), date: str = Form(...), publicprivate: str = Form(...), invites: str = Form(...)):
    #==========================
    # FEATURE (create an event)
    #
    # Given some data, create an event and send out the invites.
    #==========================
    # Event creation logic would go here
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
            data_invites = {"event_id":event_id, "title": data_event.get('title'),
            "organizer": data_event.get('organizer'),
            "date": data_event.get('date'),
            "private": data_event.get('private'), "usernames":invites}
            resp = await client.post(f"{getContainer()}/invites", data=data_invites)
            response = RedirectResponse(url="/web", status_code=303)
            feedback_message = ""
            if resp.status_code == 422:
                feedback_message += resp.json().get("detail")

            data_calendar = {"event_id": event_id, "title": data_event.get('title'),
                            "date": data_event.get('date'),
                            "organizer": data_event.get('organizer'),
                            "private": data_event.get('private'), "username": data_event.get('organizer'),
                            "status": "Participate"}
            resp = await client.post(f"{getContainer()}/calendar", data=data_calendar)
            if resp.status_code == 200 and feedback_message == "":
                response.set_cookie("feedback_category", "success")
                response.set_cookie("feedback_message", "Successfully created event! Everyone is invited! Event is added to your calendar!")
            elif resp.status_code == 409 or resp.status_code == 500:
                ic(resp)
                feedback_message += resp.json().get("detail")
                response.set_cookie("feedback_category", "danger")
                response.set_cookie("feedback_message", feedback_message)

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
    calendar = None
    no_result = None
    success = None
    if username == None or username == "":
        return RedirectResponse(url="/web/login", status_code=303)
    elif request.method == 'POST':
        form = await request.form()
        calendar_user = form.get('calendar_user', username)
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{getContainer()}/calendar/{calendar_user}?asker={username}")
            ic(resp.status_code)
            if resp.status_code == 200:
                calendar = resp.json().get("events")
                success = True
            elif resp.status_code == 404:
                no_result = True
                success = None
            elif resp.status_code == 401 or resp.status_code == 500:
                success = False
    else:
        calendar_user = username
        async with httpx.AsyncClient() as client:
            resp = await client.get(f"{getContainer()}/calendar/{calendar_user}?asker={username}")
            if resp.status_code == 200:
                calendar = resp.json().get("events")
                success = True
            elif resp.status_code == 404:
                no_result = True
                success = None
            elif resp.status_code == 401 or resp.status_code == 500:
                success = False
    return templates.TemplateResponse('calendar.html', {"request": request, "username": username, "calendar_user": calendar_user, "calendar": calendar, "success": success, "no_result":no_result})

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
        async with httpx.AsyncClient() as client:
            resp = await client.post(f"{getContainer()}/calendar/share?owner={username}&shared={share_user}")
            if resp.status_code == 200:
                return templates.TemplateResponse('share.html',
                                                  {"request": request, "username": username, "success": True})
            else:
                return templates.TemplateResponse('share.html',
                                                  {"request": request, "username": username, "success": False})
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
    if request.method == 'GET':
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
    if request.method == 'GET':
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
async def invites(request: Request):
    username = request.cookies.get("username")
    if username is None or username == "":
        return RedirectResponse(url="/web/login", status_code=303)
    async with httpx.AsyncClient() as client:
        resp = await client.get(f"{getContainer()}/invites/{username}")
        if resp.status_code == 200:
            invites = resp.json().get('invites')
            response = templates.TemplateResponse('invites.html', {
                "request": request,
                "username": username,
                "invites": invites
            })
            return response
        else:
            error = resp.json().get('detail')
            response = templates.TemplateResponse('invites.html', {
                "request": request,
                "username": username,
                "error_message": error
            })
            return response

@router.post("/invites")
async def handle_invite(request: Request, data: InviteData):
    username = request.cookies.get("username")
    if username is None or username == "":
        return JSONResponse(status_code=303, content={"message": "Redirecting to login"})

    feedback = {"category": "", "message": ""}

    if data.status == "Don't Participate":
        async with httpx.AsyncClient() as client:
            resp = await client.delete(
                f"{getContainer()}/invites?event_id={data.event}&username={username}"
            )
            if resp.status_code == 200:
                feedback = {"category": "success", "message": "Your decline of the invite has been successfully registered"}
            else:
                feedback = {"category": "danger", "message": resp.json().get("detail")}
            return JSONResponse(status_code=resp.status_code, content=feedback)

    async with httpx.AsyncClient() as client:
        resp = await client.post(
            f"{getContainer()}/events/participant?event_id={data.event}&username={username}&status={data.status}"
        )
        feedback_message = ""
        feedback = ""
        if resp.status_code in [200, 409]:
            async with httpx.AsyncClient() as client:
                delete_resp = await client.delete(
                    f"{getContainer()}/invites?event_id={data.event}&username={username}"
                )
                if delete_resp.status_code != 200:
                    feedback_message += delete_resp.json().get("detail")

                data_calendar = {"event_id": data.event, "title": data.title,
                                 "date": data.date,
                                 "organizer": data.organizer,
                                 "private": data.private, "username": username,
                                 "status": data.status}
                async with httpx.AsyncClient() as client:
                    resp = await client.post(f"{getContainer()}/calendar", data=data_calendar)

                    if resp.status_code == 200:
                        if feedback_message == "":
                            feedback = {"category": "success", "message":"Participation has been successfully registered and event is added to your calendar!"}
                    else:
                        feedback_message += resp.json().get("detail")

        elif resp.status_code == 500:
            feedback = {"category": "danger", "message": resp.json().get("detail")}

        if feedback == "":
            feedback = {"category": "danger", "message": feedback_message}
        return JSONResponse(status_code=resp.status_code, content=feedback)


@router.get("/logout")
async def logout():
    #==================render_template============
    # FEATURE (logout)
    #
    # Clear the current session and redirect to the login page.
    #==============================
    response = RedirectResponse(url="/web/login", status_code=303)
    response.set_cookie("username", "", expires=0)

    return response
