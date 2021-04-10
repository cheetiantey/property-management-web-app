from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError
from django.http import JsonResponse
from django.shortcuts import HttpResponse, HttpResponseRedirect, render
from django.urls import reverse
from django.views.decorators.csrf import csrf_exempt
from django import forms

from .models import User, Email, Unit, Tenant, Maintenance, Document

# Added the line below so that files could be uploaded
from django.core.files.storage import FileSystemStorage

class addPropertyForm(forms.Form):
    lease = forms.DecimalField(label="Lease($)", decimal_places=2, widget=forms.NumberInput(
				attrs={'class': 'form-control'}))
    sqft = forms.DecimalField(label="Squarefeet", decimal_places=0, widget=forms.NumberInput(
				attrs={'class': 'form-control'}))
    bed = forms.DecimalField(label="Bed(s)", decimal_places=0, widget=forms.NumberInput(
				attrs={'class': 'form-control'}))
    bath = forms.DecimalField(label="Bath(s)", decimal_places=0, widget=forms.NumberInput(
				attrs={'class': 'form-control'}))
    photo = forms.CharField(label="Photo URL", required=False, widget=forms.TextInput(
				attrs={'class': 'form-control'}))
    location = forms.CharField(label="Location", widget=forms.Textarea(attrs={
        'style' : 'width:100%', 'class': 'form-control'}))

class addMaintenanceForm(forms.Form):
    content = forms.CharField(label="Tell us about the issue you are having. Please use as much detail as possible to help us resolve this more quickly.", 
    widget=forms.Textarea(attrs={'style' : 'width:100%', 'class': 'form-control'})) 

class addDocumentForm(forms.Form):
    title = forms.CharField(label="Title", max_length=128, widget=forms.TextInput(
				attrs={'class': 'form-control'}))
    file = forms.FileField(label='Select a file')

# Create your views here.

def index(request):
    # Authenticated users view their portal
    if request.user.is_authenticated:
        if User.objects.get(id=request.user.id).role == "manager":
            return render(request, "management/index.html", {
                "manager": True,
                "units": Unit.objects.filter(manager=request.user)
            })
        elif User.objects.get(id=request.user.id).role == "tenant":
            email = User.objects.get(id=request.user.id).email
            # This tenant lives in a unit
            try:
                unit_id = Tenant.objects.get(email=email).unit.id
                return render(request, "management/index.html", {
                    "tenant": True,
                    "units": Unit.objects.filter(id=unit_id)
                })
            # This tenant doesn't currenty live in any unit
            except Tenant.DoesNotExist:
                return render(request, "management/index.html", {
                    "tenant": True
                })
        else:
            # Not a manager/tenant
            return render(request, "management/index.html", {
                "units": Unit.objects.filter(manager=request.user)
            })

    # Everyone else is prompted to sign in
    else:
        return HttpResponseRedirect(reverse("login"))

def login_view(request):
    if request.method == "POST":

        # Attempt to sign user in
        email = request.POST["email"]
        password = request.POST["password"]
        user = authenticate(request, username=email, password=password)

        # Check if authentication successful
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("index"))
        else:
            return render(request, "management/login.html", {
                "message": "Invalid email and/or password."
            })
    else:
        return render(request, "management/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))

def register(request):
    if request.method == "POST":
        email = request.POST["email"]

        # Ensure password matches confirmation
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "management/register.html", {
                "message": "Passwords must match."
            })
        
        # Ensure phone number is 10 digits long
        number = request.POST["phone"]
        if len(number) != 10:
            return render(request, "management/register.html", {
                "message": "You phone number must be 10 digits long"
            })
        if request.POST["role"] == "manager":
            role = "manager"
        else:
            role = "tenant"

        # Attempt to create new user
        try:
            user = User.objects.create_user(email, email, password, role=role, phone_number=number)
            user.save()
        except IntegrityError as e:
            print(e)
            return render(request, "management/register.html", {
                "message": "Email address already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "management/register.html")

def maintenance(request):
    # Ensure that the user is a tenant
    if request.user.role != "tenant":
        return HttpResponseRedirect(reverse('index'))

    if request.method == "POST":
        form = addMaintenanceForm(request.POST)
        unit_id = Tenant.objects.get(email=request.user.email).unit
        
        if form.is_valid():
            content = form.cleaned_data["content"]
            m = Maintenance(unit=unit_id, content=content, resolved=False)
            m.save()
            return HttpResponseRedirect(reverse('maintenance'))
        return render(request, "management/maintenance.html", {
            "form": form,
            "resolved_requests": Maintenance.objects.filter(unit=unit_id, resolved="True"),
            "unresolved_requests": Maintenance.objects.filter(unit=unit_id, resolved="False")
        })

    else:
	try:
            unit_id = Tenant.objects.get(email=request.user.email).unit
            return render(request, "management/maintenance.html", {
                "form": addMaintenanceForm(),
                "resolved_requests": Maintenance.objects.filter(unit=unit_id, resolved="True"),
                "unresolved_requests": Maintenance.objects.filter(unit=unit_id, resolved="False")
            })
        except Tenant.DoesNotExist:
            return render(request, "management/message.html",{
		"header": "Maintenance Requests",
                "message": "You don't live in a property yet."
            })

def contact(request):
    try:
        unit_id = Tenant.objects.get(email=request.user.email).unit.id
        manager_id = Unit.objects.get(id=unit_id).manager.id
        return render(request, "management/contact.html", {
            # Contact information of the manager 
            "contact": User.objects.get(id=manager_id)
        })
    except Tenant.DoesNotExist:
        return render(request, "management/message.html",{
	    "header": "Contact Us",
            "message": "You don't live in a property yet."
        })

def add_property(request):
    # Ensure that the user accessing this page is a manger
    if request.user.role != "manager":
        return HttpResponseRedirect(reverse("index"))

    if request.method == "POST":
        form = addPropertyForm(request.POST)
        if form.is_valid():
            lease = form.cleaned_data["lease"]
            sqft = form.cleaned_data["sqft"]            
            bed = form.cleaned_data["bed"]
            bath = form.cleaned_data["bath"]
            photo = form.cleaned_data["photo"]
            location = form.cleaned_data["location"]

            u = Unit(manager=request.user, lease=lease, sqft=sqft, bed=bed, bath=bath, photo=photo, location=location)
            u.save()
            return HttpResponseRedirect(reverse('index'))

        return render(request, "management/add_property.html", {
            "form": form
        })
    return render(request, "management/add_property.html", {
        "form": addPropertyForm()
    })

def property_page(request, property_id):
    # Gives the manager a more detailed view of a property
    if request.user.role == "manager" and Unit.objects.get(id=property_id, manager=request.user):
        return render(request, "management/property_page.html", {
            "unit": Unit.objects.get(id=property_id),
            "people": Tenant.objects.filter(unit=Unit.objects.get(id=property_id))
        })
    return HttpResponseRedirect(reverse("index"))

@csrf_exempt
def add_tenant(request):
    # Add a tenant to the property
    email = request.POST.get("email")
    unit_id = Unit.objects.get(id=int(request.POST.get("unit_id")))
    t = Tenant(unit=unit_id, email=email)
    t.save()
    return HttpResponse("You've successfully added a tenant to your property")

def maintenance_requests(request):
    # Return all the properties managed by the manager 
    return render(request, "management/maintenance_requests.html", {
        "units": Unit.objects.filter(manager=request.user)
    })

def maintenance_requests_specific(request, property_id):
    # Ensure that the user is a manger and 
    # returns the specific maintenance requests for that property
    if request.user.role == "manager":
        unit_id = Unit.objects.get(manager=request.user, id=property_id)
        return render(request, "management/maintenance_requests_specific.html", {
            "requests": Maintenance.objects.filter(unit=unit_id)
        })

def resolve(request, maintenance_id):
    # Toggle 
    # Mark a maintenance request as either resolved or unresolved
    if (str(Maintenance.objects.get(id=maintenance_id).resolved) == "True"):
        Maintenance.objects.filter(id=maintenance_id).update(resolved="False")
        return HttpResponse("True to False")
    elif (str(Maintenance.objects.get(id=maintenance_id).resolved) == "False"):
        Maintenance.objects.filter(id=maintenance_id).update(resolved="True")
        return HttpResponse("False to True")
    return HttpResponse("Resolved field in Maintenance table has a value other than True/False")

def documents(request):
    if request.method == "POST":
        form = addDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            email = User.objects.get(id=request.user.id).email
            unit_id = Tenant.objects.get(email=email).unit
            title = form.cleaned_data["title"]
            D = Document(unit=unit_id, title=title, uploaded_file=request.FILES['file'])
            D.save()
            return HttpResponseRedirect(reverse('documents'))
        try:
            email = User.objects.get(id=request.user.id).email
            unit_id = Tenant.objects.get(email=email).unit
            documents = Document.objects.filter(unit=unit_id)
            return render(request, "management/documents.html", {
                "form": addDocumentForm(),
                "documents": documents
            })
        except Document.DoesNotExist:
            return render(request, "management/documents.html", {
                "form": addDocumentForm(),
                "documents": documents
            })
    else:
        # if the tenant is living in a unit
        try:
            email = User.objects.get(id=request.user.id).email
            unit_id = Tenant.objects.get(email=email).unit
            documents = Document.objects.filter(unit=unit_id)
            return render(request, "management/documents.html", {
                "form": addDocumentForm(),
                "documents": documents
            })
        # The tenant is not living in any unit
        except Tenant.DoesNotExist:
            return render(request, "management/message.html",{
		"header": "Shared Documents",
                "message": "You don't live in a property yet."
            })
        # The tenant does not have any documents
        except Document.DoesNotExist:
            email = User.objects.get(id=request.user.id).email
            unit_id = Tenant.objects.get(email=email).unit
            return render(request, "management/documents.html", {
                "form": addDocumentForm()
            })

def manager_documents(request):
    # Return a list of properties that the manager manages
    return render(request, "management/manager_documents.html", {
        "units": Unit.objects.filter(manager=request.user)
    })

def manager_documents_specific(request, property_id):
    if request.method == "POST":
        form = addDocumentForm(request.POST, request.FILES)
        if form.is_valid():
            unit_id = Unit.objects.get(id=property_id)
            title = form.cleaned_data["title"]
            D = Document(unit=unit_id, title=title, uploaded_file=request.FILES['file'])
            D.save()
            # Bring the manager back to the specific property shared document page
            return HttpResponseRedirect(reverse('manager_documents_specific', args=[property_id]))

        # Bring the manager back to the specific property shared document page
        return HttpResponseRedirect(reverse('manager_documents_specific', args=[property_id]))
    else:
        # If the person accessing this page shouldn't have access to this page
        if Unit.objects.get(id=property_id).manager != request.user:
            return HttpResponseRedirect(reverse('index'))

        # Present the manager with a form as well as the documents already uploaded(if it exists)
        unit_id = Unit.objects.get(id=property_id)
        documents = Document.objects.filter(unit=unit_id)
        return render(request, "management/documents.html", {
            "form": addDocumentForm(),
            "documents": documents
        })

