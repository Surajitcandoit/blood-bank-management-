import requests
from django.shortcuts import render, redirect
from django.http import HttpResponse
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
import requests
from django.contrib import messages
import os
# If API_URL isn't set, it defaults to your local server for testing
API_BASE_URL = os.getenv("API_URL", "http://127.0.0.1:8000").rstrip('/')

def landing_page(request):
    # If the user is already logged in, skip the landing page
    if request.session.get("token"):
        return redirect("dashboard")
        
    return render(request, "landing_page.html")


def dashboard(request):
    token = request.session.get("token")
    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        # Request the admin dashboard
        response = requests.get(
            f"{API_BASE_URL}/admin/dashboard",
            headers=headers,
            timeout=5 # Prevents hanging if backend is slow
        )

        # If the user is NOT an admin (403), or token expired (401)
        if response.status_code in [401, 403]:
            # Fallback to the general stats endpoint that doesn't require admin
            fallback_response = requests.get(f"{API_BASE_URL}/dashboard/stats")
            if fallback_response.status_code == 200:
                return render(request, "dashboard.html", {"data": fallback_response.json(), "role": "user"})

        # If completely broken
        if response.status_code != 200:
            return render(request, "dashboard.html", {"error": f"API Error: {response.text}"})

        # Success for admin
        data = response.json()
        return render(request, "dashboard.html", {"data": data, "role": "admin"})

    except requests.exceptions.RequestException as e:
        return render(request, "dashboard.html", {"error": "Could not connect to the backend server. Is FastAPI running?"})
    
def register_view(request):
    if request.method == "POST":
        data = {
            "name": request.POST.get("name"),
            "email": request.POST.get("email"),
            "password": request.POST.get("password"),
            "role": request.POST.get("role")  # Let them choose "donor" or "hospital"
        }
        
        try:
            response = requests.post(
                f"{API_BASE_URL}/register",
                json=data
            )
            response_data = response.json()
            
            # FastAPI returns {"message": ...} on success, {"error": ...} on failure
            if "error" in response_data:
                return render(request, "register.html", {"error": response_data["error"]})
            
            # If successful, send them to login
            return redirect("login")
            
        except requests.exceptions.ConnectionError:
            return render(request, "register.html", {"error": "Backend server is down."})

    return render(request, "register.html")

def login_view(request):
    if request.method == "POST":
        email = request.POST.get("email")
        password = request.POST.get("password")

        try:
            # FIX: Send as 'data' (Form Data) and use the 'username' key
            response = requests.post(
                f"{API_BASE_URL}/login",
                data={"username": email, "password": password} 
            )
            
            if response.status_code == 200:
                data = response.json()
                
                if "access_token" in data:
                    request.session["token"] = data["access_token"]
                    # NEW: Save the role into the Django session
                    request.session["role"] = data.get("role", "donor") 
                    
                    return redirect("dashboard")
                else:
                    error_msg = data.get("error", "Invalid Credentials")
                    return render(request, "login.html", {"error": error_msg})
            else:
                # This will catch 422 errors or other backend crashes
                return render(request, "login.html", {"error": f"Backend Error: {response.status_code}"})
                    
        except requests.exceptions.ConnectionError:
            return render(request, "login.html", {"error": "Backend server is not running."})

    return render(request, "login.html")

def manage_staff(request):
    token = request.session.get("token")
    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}
    
    # Fetch the list of admins from FastAPI
    response = requests.get(
        f"{API_BASE_URL}/admin/staff",
        headers=headers
    )
    
    staff_data = []
    if response.status_code == 200:
        staff_data = response.json()

    return render(request, "manage_staff.html", {"staff": staff_data})

def delete_staff(request, user_id):
    token = request.session.get("token")
    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}

    # Tell FastAPI to delete the admin
    response = requests.delete(
        f"{API_BASE_URL}/admin/staff/{user_id}",
        headers=headers
    )
    
    data = response.json()
    if "error" in data:
        messages.error(request, data["error"])
    else:
        messages.success(request, "Staff member removed.")

    return redirect("manage_staff")


def logout_view(request):

    request.session.flush()

    return redirect("login")

def add_donation(request, donor_id):
    token = request.session.get("token")
    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        units = request.POST.get("units")
        blood_group = request.POST.get("blood_group")

        # Send to FastAPI backend
        requests.post(
            f"{API_BASE_URL}/donation/add",
            json={
                "donor_id": int(donor_id),
                "blood_group": blood_group,
                "units": int(units)
            },
            headers=headers
        )
        # Redirect to inventory to see the updated stock!
        return redirect("inventory")

    # If it's a GET request, grab the blood group from the URL to pre-fill the form
    blood_group = request.GET.get("bg", "")
    return render(
        request, 
        "add_donation.html", 
        {"donor_id": donor_id, "blood_group": blood_group}
    )

def inventory(request):

    token = request.session.get("token")

    if not token:
        return redirect("login")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    blood_group = request.GET.get("blood_group")

    response = requests.get(
        f"{API_BASE_URL}/inventory",
        headers=headers
    )

    inventory_data = response.json()

    # Search filter
    if blood_group:

        inventory_data = [
            item for item in inventory_data
            if item["blood_group"].lower()
            == blood_group.lower()
        ]

    return render(
        request,
        "inventory.html",
        {
            "inventory": inventory_data
        }
    )


def hospitals(request):

    token = request.session.get("token")

    if not token:
        return redirect("login")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    # Create Hospital
    if request.method == "POST":

        requests.post(
            f"{API_BASE_URL}/hospital/create",
            json={
                "hospital_name": request.POST["hospital_name"],
                "address": request.POST["address"],
                "phone": request.POST["phone"],
                "license_no": request.POST["license_no"]
            },
            headers=headers
        )

        return redirect("hospitals")

    # Get Hospitals
    response = requests.get(
        f"{API_BASE_URL}/hospitals",
        headers=headers
    )

    hospital_data = response.json()

    return render(
        request,
        "hospitals.html",
        {
            "hospitals": hospital_data
        }
    )

def create_blood_request(request):
    token = request.session.get("token")
    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}

    if request.method == "POST":
        # Extract data from the HTML form
        hospital_id = request.POST.get("hospital_id")
        blood_group = request.POST.get("blood_group")
        units = request.POST.get("units")

        requests.post(
            f"{API_BASE_URL}/request-blood",
            json={
                "hospital_id": int(hospital_id),
                "blood_group": blood_group,
                "units": int(units)
            },
            headers=headers
        )
        
        # Send them back to the requests page to see their pending request
        return redirect("requests")

    return render(request, "request_blood.html")

def requests_page(request):

    token = request.session.get("token")

    if not token:
        return redirect("login")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{API_BASE_URL}/requests",
        headers=headers
    )

    request_data = response.json()

    return render(
        request,
        "requests.html",
        {
            "requests": request_data
        }
    )

def approve_request(request, request_id):
    token = request.session.get("token")
    if not token:
        return redirect("login")

    headers = {"Authorization": f"Bearer {token}"}

    try:
        response = requests.post(
            f"{API_BASE_URL}/request/{request_id}/approve",
            headers=headers
        )
        
        # Parse the JSON response from FastAPI
        data = response.json()

        # If FastAPI returns an error (like "Insufficient stock" or "Blood group not available")
        if "error" in data:
            # Create a red error message
            messages.error(request, data["error"])
        else:
            # Create a green success message
            messages.success(request, "Blood request approved successfully!")

    except requests.exceptions.RequestException:
        messages.error(request, "Backend server is down.")

    return redirect("requests")

def reject_request(request, request_id):

    token = request.session.get("token")

    if not token:
        return redirect("login")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    requests.post(
        f"{API_BASE_URL}/request/{request_id}/reject",
        headers=headers
    )

    return redirect("requests")

def distributions(request):

    token = request.session.get("token")

    if not token:
        return redirect("login")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    response = requests.get(
        f"{API_BASE_URL}/distributions",
        headers=headers
    )

    distribution_data = response.json()

    return render(
        request,
        "distributions.html",
        {
            "distributions": distribution_data
        }
    )

def reports(request):

    token = request.session.get("token")

    if not token:
        return redirect("login")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    dashboard = requests.get(
        f"{API_BASE_URL}/admin/dashboard",
        headers=headers
    ).json()

    low_stock = requests.get(
        f"{API_BASE_URL}/inventory/low-stock",
        headers=headers
    ).json()

    expired = requests.get(
        f"{API_BASE_URL}/inventory/expired",
        headers=headers
    ).json()

    return render(
        request,
        "reports.html",
        {
            "dashboard": dashboard,
            "low_stock": low_stock,
            "expired": expired
        }
    )

def donors(request):

    token = request.session.get("token")

    if not token:
        return redirect("login")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    if request.method == "POST":

        requests.post(
            f"{API_BASE_URL}/donors",
            json={
                "name": request.POST["name"],
                "blood_group": request.POST["blood_group"],
                "age": int(request.POST["age"]),
                "phone": request.POST["phone"],
                "address": request.POST["address"]
            },
            headers=headers
        )

        return redirect("donors")

    response = requests.get(
        f"{API_BASE_URL}/donors",
        headers=headers
    )
    blood_group = request.GET.get("blood_group")
    donor_data = response.json()
    if blood_group:
        donor_data = [

        donor

        for donor in donor_data

        if donor["blood_group"].lower()
        == blood_group.lower()

    ]
    return render(
        request,
        "donors.html",
        {
            "donors": donor_data
        }
    )

def delete_donor(request, donor_id):

    token = request.session.get("token")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    requests.delete(
        f"{API_BASE_URL}/donor/{donor_id}",
        headers=headers
    )

    return redirect("donors")

def delete_hospital(
    request,
    hospital_id
):

    token = request.session.get("token")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    requests.delete(
        f"{API_BASE_URL}/hospital/{hospital_id}",
        headers=headers
    )

    return redirect("hospitals")

def export_report(request):

    token = request.session.get("token")

    headers = {
        "Authorization": f"Bearer {token}"
    }

    dashboard = requests.get(
        f"{API_BASE_URL}/admin/dashboard",
        headers=headers
    ).json()

    response = HttpResponse(
        content_type="application/pdf"
    )

    response[
        "Content-Disposition"
    ] = 'attachment; filename="blood_bank_report.pdf"'

    doc = SimpleDocTemplate(response)

    styles = getSampleStyleSheet()

    content = []

    content.append(
        Paragraph(
            "Blood Bank Management Report",
            styles["Title"]
        )
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(
            f"Total Donors: {dashboard['total_donors']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Total Hospitals: {dashboard['total_hospitals']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Total Requests: {dashboard['total_requests']}",
            styles["Normal"]
        )
    )

    content.append(
        Paragraph(
            f"Total Distributions: {dashboard['total_distributions']}",
            styles["Normal"]
        )
    )

    doc.build(content)

    return response



