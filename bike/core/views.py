from django.shortcuts import render
from .models import SiteBrand, NavItem,HomePage,HomeFeature,SupportSection,SatisfiedCustomerSection, HappyCustomer, TrustedRidersSection, FAQ

def get_brand_and_nav():
    brand = SiteBrand.objects.first()
    navitems = NavItem.objects.all()
    return brand, navitems

def home(request):
    page = HomePage.objects.first()
    images = page.images.all() if page else []
    brand, navitems = get_brand_and_nav()
    features = HomeFeature.objects.filter(is_active=True).order_by("order")
    section = SupportSection.objects.filter(is_active=True).first()
    items = section.items.filter(is_active=True) if section else []
    satisfied = SatisfiedCustomerSection.objects.first()
    happy_customers = HappyCustomer.objects.all()
    trusted = TrustedRidersSection.objects.first()
    faqs = FAQ.objects.all()
    return render(request, 'core/home.html', {'brand': brand, 'navitems': navitems,"page": page,
        "hero_images": images,"features": features,"support_section": section,
        "support_items": items,"satisfied": satisfied,
        "happy_customers": happy_customers,
        "trusted": trusted,
        "faqs": faqs,})

def buy_bike(request):
    brand, navitems = get_brand_and_nav()
    # You can load real products later; for now just demo content
    return render(request, 'core/buy_bike.html', {'brand': brand, 'navitems': navitems})

def sell_bike(request):
    brand, navitems = get_brand_and_nav()
    return render(request, 'core/sell_bike.html', {'brand': brand, 'navitems': navitems})

def about(request):
    brand, navitems = get_brand_and_nav()
    return render(request, 'core/about.html', {'brand': brand, 'navitems': navitems})

import json
import logging
import re

from django.conf import settings
from django.core.mail import send_mail, BadHeaderError
from django.http import JsonResponse, HttpResponseBadRequest
from django.views.decorators.http import require_POST
from django.shortcuts import render

from .models import SiteBrand, NavItem

logger = logging.getLogger(__name__)

def get_brand_and_nav():
    brand = SiteBrand.objects.first()
    navitems = NavItem.objects.all()
    return brand, navitems

def contact(request):
    """
    Renders the contact page template (GET).
    The template should include the form and client JS that posts to contact_submit.
    """
    brand, navitems = get_brand_and_nav()
    return render(request, 'core/contact.html', {'brand': brand, 'navitems': navitems})


# --- Validation regexes ---
NAME_RE = re.compile(r"^[A-Za-z\s\.\-']{2,100}$")
EMAIL_RE = re.compile(r'^[^\s@]+@[^\s@]+\.[^\s@]{2,}$')
PHONE_RE = re.compile(r'^[0-9]{7,15}$')
MESSAGE_RE = re.compile(r"^[A-Za-z\s\.\,\?\!\-'\(\)]{5,1000}$")

ALLOWED_REASONS = {
    "General Enquiry", "Buy a Bike", "Sell a Bike",
    "Exchange a Bike", "RTO Service", "Others",
}
ALLOWED_CHANNELS = {"OLX", "Instagram", "Youtube", "Google", "Website", "Facebook", "Walk - in"}

@require_POST
def contact_submit(request):
    # Expect JSON POST
    try:
        data = json.loads(request.body.decode("utf-8"))
    except json.JSONDecodeError:
        return JsonResponse({"success": False, "error": "Invalid JSON"}, status=400)

    name = (data.get("name") or "").strip()
    email = (data.get("email") or "").strip()
    phone = (data.get("phone") or "").strip()
    reason = (data.get("reason") or "").strip()
    channel = (data.get("channel") or "").strip()
    message = (data.get("message") or "").strip()

    # Server-side validation
    if not NAME_RE.match(name):
        return JsonResponse({"success": False, "error": "Invalid name"}, status=400)
    if not EMAIL_RE.match(email):
        return JsonResponse({"success": False, "error": "Invalid email"}, status=400)
    if not PHONE_RE.match(phone):
        return JsonResponse({"success": False, "error": "Invalid phone"}, status=400)
    if reason not in ALLOWED_REASONS or channel not in ALLOWED_CHANNELS:
        return JsonResponse({"success": False, "error": "Invalid selection"}, status=400)
    if not MESSAGE_RE.match(message):
        return JsonResponse({"success": False, "error": "Invalid message content"}, status=400)

    subject = f"Contact form: {reason} - {name}"
    body = (
        "You have received a new contact form submission.\n\n"
        f"Name: {name}\nEmail: {email}\nPhone: {phone}\nReason: {reason}\nChannel: {channel}\n\n"
        "Message:\n" f"{message}\n"
    )
    recipient_list = ["youremail@example.com"]  # change to your receiving address

    try:
        send_mail(subject, body, settings.DEFAULT_FROM_EMAIL, recipient_list, fail_silently=False)
    except BadHeaderError:
        logger.exception("BadHeaderError while sending contact email")
        return JsonResponse({"success": False, "error": "Invalid header in email"}, status=500)
    except Exception:
        logger.exception("Error sending contact email")
        return JsonResponse({"success": False, "error": "Failed to send email"}, status=500)

    return JsonResponse({"success": True})


# about view
from django.shortcuts import render, get_object_or_404
from .models import AboutPage

def about(request):
    # Get the first AboutPage instance; if none exists, show a basic default
    about = AboutPage.objects.first()
    brand, navitems = get_brand_and_nav()
    if not about:
        # You can render a sensible fallback, or create a default in admin.
        return render(request, 'core/about.html', {'about': None})

    # get approach images (ordered)
    images = about.approach_images.all()
    return render(request, 'core/about.html', {'about': about, 'approach_images': images,'brand': brand, 'navitems': navitems})


# buybike page
# core/views.py
from django.shortcuts import render, get_object_or_404
from django.db.models import Q
from .models import Bike

def buy_bike(request):
    qs = Bike.objects.filter(is_published=True)

    # read raw GET params
    selected_categories = request.GET.getlist('category')        # list
    selected_brands = request.GET.getlist('brand')              # list
    selected_fuel = request.GET.getlist('fuel')                 # list
    selected_cc = request.GET.get('cc')                         # single value
    selected_sort = request.GET.get('sort','newest')

    # apply filters
    if selected_categories:
        qs = qs.filter(category__in=selected_categories)
    if selected_brands:
        qs = qs.filter(brand__in=selected_brands)

    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    if min_price:
        try: qs = qs.filter(price__gte=float(min_price))
        except: pass
    if max_price:
        try: qs = qs.filter(price__lte=float(max_price))
        except: pass

    min_year = request.GET.get('min_year')
    max_year = request.GET.get('max_year')
    if min_year:
        try: qs = qs.filter(make_year__gte=int(min_year))
        except: pass
    if max_year:
        try: qs = qs.filter(make_year__lte=int(max_year))
        except: pass

    max_km = request.GET.get('max_km')
    if max_km:
        try: qs = qs.filter(kilometers__lte=int(max_km))
        except: pass

    # CC filtering (keep your existing approach or replace with numeric field)
    if selected_cc:
        # example: basic contains checks for 'cc' values; adjust as needed
        if selected_cc == 'below100':
            qs = qs.filter(variant__icontains='cc', )
            # you can refine with a numeric field (recommended)
        elif selected_cc == 'below200':
            qs = qs.filter(variant__icontains='cc')
        elif selected_cc == 'below300':
            qs = qs.filter(variant__icontains='cc')
        elif selected_cc == 'below400':
            qs = qs.filter(variant__icontains='cc')

    if selected_fuel:
        qs = qs.filter(fuel_type__in=selected_fuel)

    location = request.GET.get('location')
    if location:
        qs = qs.filter(location__icontains=location)

    q = request.GET.get('q')
    if q:
        qs = qs.filter(Q(brand__icontains=q) | Q(model__icontains=q) | Q(variant__icontains=q) | Q(location__icontains=q))

    # sorting
    if selected_sort == 'newest':
        qs = qs.order_by('-created_at')
    elif selected_sort == 'price_asc':
        qs = qs.order_by('price')
    elif selected_sort == 'price_desc':
        qs = qs.order_by('-price')
    elif selected_sort == 'alpha':
        qs = qs.order_by('brand','model')

    bikes = qs
    total_count = bikes.count()
    available_brands = Bike.objects.values_list('brand', flat=True).distinct()
    brand, navitems = get_brand_and_nav()

    context = {
        'bikes': bikes,
        'total_count': total_count,
        'available_brands': available_brands,
        'query': request.GET,               # keep if you used other query.get() in template
        # pass the computed selected lists/values for use in template
        'selected_categories': selected_categories,
        'selected_brands': selected_brands,
        'selected_fuel': selected_fuel,
        'selected_cc': selected_cc,
        'selected_sort': selected_sort,
        'brand': brand, 'navitems': navitems
    }
    return render(request, 'core/buy_bike.html', context)


# core/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Bike, TestRide

def bike_detail(request, pk):
    """
    Renders the bike detail page.
    """
    bike = get_object_or_404(Bike, pk=pk)
    brand, navitems = get_brand_and_nav()
    # gather thumbnails if you store them as thumb1..thumb6 fields OR a related model.
    # If you used separate fields (thumb1..thumb6), build a list here:
    thumbs = []
    for f in ("thumb1","thumb2","thumb3","thumb4","thumb5","thumb6"):
        img = getattr(bike, f, None)
        if img:
            thumbs.append(img)
    # If you use a related model for images, adjust accordingly.
    context = {
        "bike": bike,
        "thumbs": thumbs,
        'brand': brand, 'navitems': navitems
    }
    return render(request, "core/bike_detail.html", context)


@login_required
@require_POST
def book_test_ride(request, pk):
    """
    Creates a TestRide entry for authenticated users.
    Accepts normal POST or AJAX POST. Returns JSON for AJAX.
    """
    bike = get_object_or_404(Bike, pk=pk)

    # prevent owner from booking their own listing
    try:
        owner = getattr(bike, "owner")
        if owner and owner == request.user:
            msg = "You cannot book a test ride for your own listing."
            if request.headers.get("x-requested-with") == "XMLHttpRequest":
                return JsonResponse({"success": False, "message": msg}, status=400)
            return redirect(bike.get_absolute_url())
    except Exception:
        pass

    # check existing pending test ride by same user for same bike
    existing = TestRide.objects.filter(bike=bike, user=request.user, status=TestRide.STATUS_PENDING)
    if existing.exists():
        msg = "You already have a pending test ride for this bike."
        if request.headers.get("x-requested-with") == "XMLHttpRequest":
            return JsonResponse({"success": False, "message": msg})
        return redirect(bike.get_absolute_url())

    phone = request.POST.get("phone", "").strip() or None
    scheduled_for = request.POST.get("scheduled_for") or None
    notes = request.POST.get("notes", "").strip() or None

    tr = TestRide.objects.create(
        bike=bike,
        user=request.user,
        phone=phone,
        scheduled_for=scheduled_for if scheduled_for else None,
        notes=notes,
        refundable_amount=1000.00,
        status=TestRide.STATUS_PENDING,
    )

    # Optionally: send a notification/email here

    if request.headers.get("x-requested-with") == "XMLHttpRequest":
        return JsonResponse({
            "success": True,
            "message": "Test ride booked successfully. We will contact you to confirm the slot.",
            "test_ride_id": tr.pk
        })
    # normal POST redirect
    return redirect(bike.get_absolute_url() + "#test-ride-booked")



@login_required
def bike_payment(request, pk):
    bike = get_object_or_404(Bike, pk=pk)
    brand, navitems = get_brand_and_nav()
    return render(request, "core/bike_payment.html", {"bike": bike,'brand': brand, 'navitems': navitems})

# loginview
# core/views.py
from django.contrib.auth import authenticate, login, logout, get_user_model
from django.contrib import messages
from django.shortcuts import render, redirect
from django.urls import reverse

User = get_user_model()

def login_view(request):
    """
    Custom login view:
    - Accepts username OR email in the 'username' field.
    - Redirects to ?next=... or homepage after login.
    """
    next_url = request.GET.get('next') or request.POST.get('next') or reverse('home')
    print('coming')
    if request.method == 'POST':
        print('coming2')

        identifier = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')

        if not identifier or not password:
            brand, navitems = get_brand_and_nav()
            return render(request, 'core/auth/login.html', {
                'error': "Please enter both username/email and password.",
                'next': next_url, 'brand': brand, 'navitems': navitems
            })

        # Try direct authentication with given identifier
        user = authenticate(request, username=identifier, password=password)

        # If that fails, try email -> username fallback
        if user is None:
            try:
                user_obj = User.objects.filter(email__iexact=identifier).first()
                if user_obj:
                    user = authenticate(request, username=user_obj.username, password=password)
            except Exception:
                pass

        if user is not None:
            login(request, user)
            return redirect(next_url)
        else:
            brand, navitems = get_brand_and_nav()
            return render(request, 'core/auth/login.html', {
                'error': "Invalid credentials. Please try again.",
                'next': next_url, 'brand': brand, 'navitems': navitems,
                'username': identifier
            })

    # GET request
    brand, navitems = get_brand_and_nav()
    return render(request, 'core/auth/login.html', {
        'next': next_url, 'brand': brand, 'navitems': navitems
    })


def logout_view(request):
    logout(request)
    return redirect('home')


# sellbike page view
# core/views.py (append)
from django.shortcuts import render, get_object_or_404
from django.http import JsonResponse, HttpResponseForbidden
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from .models import Banner, SellRequest
from django.utils import timezone




def _get_banner():
    # return the first banner if exists else None
    try:
        return Banner.objects.first()
    except Exception:
        return None

def sell_bike_view(request):
    """
    GET: render sell page (banner loaded from admin)
    POST handled by AJAX endpoint sell_get_price
    """
    brand, navitems = get_brand_and_nav()
    banner = _get_banner()
    context = {
        'banner': banner,
        'brand': brand, 'navitems': navitems,
    }
    return render(request, 'core/sell_bike.html', context)


@require_POST
def sell_get_price(request):
    """
    AJAX endpoint: validates payload, computes estimate, saves SellRequest.
    If user is authenticated, it ties the SellRequest to user; else saves anonymous.
    Returns JSON: {ok:True, price: <int>, id: <sellrequest id>}
    """
    data = request.POST
    # basic required fields
    brand = data.get('brand','').strip()
    model = data.get('model','').strip()
    variant = data.get('variant','').strip()
    year = data.get('year','').strip()
    kms = data.get('kms','').strip()
    owner = data.get('owner','').strip()
    name = data.get('name','').strip()
    phone = data.get('phone','').strip()
    notes = data.get('notes','').strip()

    # simple validation
    if not all([brand, model, variant, year, kms, owner]):
        return JsonResponse({'ok': False, 'error': 'Missing required fields'}, status=400)

    try:
        year_int = int(year)
    except ValueError:
        return JsonResponse({'ok': False, 'error': 'Invalid year'}, status=400)

    # server-side pricing logic (simple realistic heuristic)
    brand_base = {
        'TVS': 60000, 'Honda': 75000, 'Bajaj': 50000, 'Hero': 40000, 'Royal Enfield': 220000,
        'Yamaha': 80000, 'Vespa': 95000, 'KTM': 240000, 'Suzuki': 85000
    }
    base = brand_base.get(brand, 50000)

    vf = 1.0
    if '350' in variant or '410' in variant or '400' in variant:
        vf = 1.6
    elif '150' in variant:
        vf = 1.25
    elif '125' in variant:
        vf = 1.05
    elif '110' in variant:
        vf = 0.92

    age = max(0, (timezone.now().year - year_int))
    age_factor = max(0.35, 1 - (age * 0.06))

    kms_factor = 1.0
    if 'Under' in kms:
        kms_factor = 0.96
    elif '5,000' in kms and '20,000' in kms:
        kms_factor = 0.9
    elif '20,000' in kms:
        kms_factor = 0.8
    elif '+' in kms or '50,000' in kms:
        kms_factor = 0.72

    owner_factor = 1.0
    if owner.startswith('2nd'):
        owner_factor = 0.88
    elif owner.startswith('3rd'):
        owner_factor = 0.75

    price = int(round(base * vf * age_factor * kms_factor * owner_factor))
    # round to nearest 100
    price = (price // 100) * 100

    # Save SellRequest
    sr = SellRequest.objects.create(
        user = request.user if request.user.is_authenticated else None,
        brand = brand,
        model = model,
        variant = variant,
        year = year_int,
        kms_range = kms,
        owner = owner,
        estimated_price = price,
        name = name,
        phone = phone,
        notes = notes
    )
    return JsonResponse({'ok': True, 'price': price, 'id': sr.id})
