# navbar

from django.db import models

class SiteBrand(models.Model):
    left_text = models.CharField(max_length=50, default="Drive")
    right_text = models.CharField(max_length=50, default="RP")
    left_color = models.CharField(max_length=7, default="#2b8ecb")
    right_color = models.CharField(max_length=7, default="#ff6b6b")
    shadow = models.BooleanField(default=True)
    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.left_text}{self.right_text}"


class NavItem(models.Model):
    title = models.CharField(max_length=50)
    url = models.CharField(max_length=200, help_text="Use URL path (eg: /, /buy-bike/ )")
    order = models.PositiveIntegerField(default=0)
    is_external = models.BooleanField(default=False)

    class Meta:
        ordering = ['order']

    def __str__(self):
        return self.title


# about page
from django.db import models
from django.utils.html import mark_safe

class AboutPage(models.Model):
    """
    Singleton-like model (create one instance via admin).
    Stores top section image, intro copy and mission overlay content.
    """
    title = models.CharField(max_length=120, default="About Us")
    # top section left image
    hero_image = models.ImageField(upload_to='about/hero/', blank=True, null=True)
    # intro (right column) text. Using a separate field to allow formatting.
    intro_heading = models.CharField(max_length=120, default="About Us")
    intro_paragraph = models.TextField(
        default="At Drive RP, we're passionate about making cycling accessible and sustainable for everyone..."
    )
    # the exact word to highlight (Drive RP) - optional override
    highlight_text = models.CharField(max_length=40, default="Drive RP")

    # success banner (background image)
    success_image = models.ImageField(upload_to='about/success/', blank=True, null=True)

    # mission card overlay
    mission_title = models.CharField(max_length=120, default="Our Mission")
    mission_text = models.TextField(default="Our mission is to make cycling more accessible, affordable, and sustainable...")
    mission_overlay_opacity = models.FloatField(default=0.95)

    # approach section left text
    approach_heading = models.CharField(max_length=120, default="Our Approach")
    approach_paragraph = models.TextField(default="We believe buying or selling a secondhand bike should be simple, safe, and stress-free...")

    def __str__(self):
        return "About Page"

    class Meta:
        verbose_name = "About Page"
        verbose_name_plural = "About Page"


class ApproachImage(models.Model):
    """
    Images used in the 'Our Approach' right-hand grid.
    'grid_position' controls layout order and spanning — we'll interpret values 1..5.
    """
    about = models.ForeignKey(AboutPage, on_delete=models.CASCADE, related_name='approach_images')
    image = models.ImageField(upload_to='about/approach/')
    caption = models.CharField(max_length=150, blank=True)
    order = models.PositiveSmallIntegerField(default=0, help_text="Sort order")
    # semantic position (1..5) - optional
    grid_position = models.PositiveSmallIntegerField(default=0, help_text="Grid slot (optional ordering)")

    def image_tag(self):
        if self.image:
            return mark_safe(f'<img src="{self.image.url}" style="max-width:120px; height:auto;" />')
        return "(no image)"
    image_tag.short_description = 'Image Preview'
    image_tag.allow_tags = True

    class Meta:
        ordering = ('order', 'id')

    def __str__(self):
        return self.caption or f"Approach Image #{self.pk}"

# buybike model
# core/models.py (only the Bike model fragment shown; merge with your existing code)
from django.db import models
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
import os

User = get_user_model()

CATEGORY_CHOICES = [
    ('scooter', 'Scooter'),
    ('motorbike', 'Motorbike'),
    ('ev', 'EV'),
]

FUEL_CHOICES = [
    ('petrol', 'Petrol'),
    ('diesel', 'Diesel'),
    ('electric', 'Electric'),
]

OWNER_CHOICES = [
    ('1st', '1st Owner'),
    ('2nd', '2nd Owner'),
    ('3rd+', '3rd+ Owner'),
]

TRANSMISSION_CHOICES = [
    ('manual', 'Manual'),
    ('automatic', 'Automatic'),
]

IGNITION_CHOICES = [
    ('kick', 'Kick'),
    ('electric', 'Electric'),
    ('both', 'Kick & Electric'),
]

BRAKE_CHOICES = [
    ('disc', 'Disc'),
    ('drum', 'Drum'),
    ('combined', 'Combined'),
]

WHEEL_TYPE_CHOICES = [
    ('alloy', 'Alloy'),
    ('spoke', 'Spoke'),
    ('steel', 'Steel'),
]
def bike_upload_path(instance, filename):
    """
    Upload path: media/bikes/<owner_id>/<brand_model>/<filename>
    Keeps filenames unique by prefixing with timestamp if collision is possible.
    """
    base, ext = os.path.splitext(filename)
    safe_brand = "".join(c for c in (instance.brand or "brand") if c.isalnum() or c in (' ', '-', '_')).replace(" ", "_")
    safe_model = "".join(c for c in (instance.model or "model") if c.isalnum() or c in (' ', '-', '_')).replace(" ", "_")
    folder = f"bikes/{instance.owner.id}/{safe_brand}_{safe_model}"
    # optional: return f"{folder}/{int(timezone.now().timestamp())}_{base}{ext}"
    return f"{folder}/{base}{ext}"

# ... other CHOICES (OWNER_CHOICES, etc.) as before ...

class Bike(models.Model):
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bikes')
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='motorbike')

    # Basic identity
    brand = models.CharField(max_length=120)
    model = models.CharField(max_length=120)
    variant = models.CharField(max_length=120, blank=True, null=True)  # you use this for CC

    # specs
    make_year = models.PositiveIntegerField(help_text="e.g. 2018")
    kilometers = models.PositiveIntegerField(help_text="Total km driven", default=0)
    fuel_type = models.CharField(max_length=10, choices=FUEL_CHOICES, default='petrol')
    previous_owner = models.CharField(max_length=10, choices=OWNER_CHOICES, default='1st')
    price = models.DecimalField(max_digits=12, decimal_places=2)
    location = models.CharField(max_length=200, help_text="City, State or local area")
    refurbished = models.BooleanField(default=False)
    rto_state = models.CharField(max_length=120, blank=True, null=True)
    rto_city = models.CharField(max_length=120, blank=True, null=True)
    registration_year = models.PositiveIntegerField(blank=True, null=True)
    transmission = models.CharField(max_length=20, choices=TRANSMISSION_CHOICES, blank=True, null=True)
    registration_certificate = models.FileField(upload_to=bike_upload_path, blank=True, null=True)
    finance_available = models.BooleanField(default=False)
    insurance_available = models.BooleanField(default=False)
    warranty = models.BooleanField(default=False, verbose_name="Warranty available")
    bike_color = models.CharField(max_length=80, blank=True, null=True)

    ignition_type = models.CharField(max_length=20, choices=IGNITION_CHOICES, blank=True, null=True)
    front_brake_type = models.CharField(max_length=20, choices=BRAKE_CHOICES, blank=True, null=True)
    rear_brake_type = models.CharField(max_length=20, choices=BRAKE_CHOICES, blank=True, null=True)
    abs_available = models.BooleanField(default=False)
    odometer_type = models.CharField(max_length=80, blank=True, null=True, help_text="Digital / Analog")
    wheel_type = models.CharField(max_length=20, choices=WHEEL_TYPE_CHOICES, blank=True, null=True)

    # Images
    main_image = models.ImageField(upload_to=bike_upload_path, blank=True, null=True)
    thumb1 = models.ImageField(upload_to=bike_upload_path, blank=True, null=True)
    thumb2 = models.ImageField(upload_to=bike_upload_path, blank=True, null=True)
    thumb3 = models.ImageField(upload_to=bike_upload_path, blank=True, null=True)
    thumb4 = models.ImageField(upload_to=bike_upload_path, blank=True, null=True)
    thumb5 = models.ImageField(upload_to=bike_upload_path, blank=True, null=True)
    thumb6 = models.ImageField(upload_to=bike_upload_path, blank=True, null=True)

    # Booking
    is_booked = models.BooleanField(default=False)
    booked_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')
    booked_at = models.DateTimeField(null=True, blank=True)

    # metadata
    is_published = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.make_year})"

    def get_absolute_url(self):
        return reverse('bike-detail', args=[self.pk])

    def book(self, user):
        self.is_booked = True
        self.booked_by = user
        self.booked_at = timezone.now()
        self.save(update_fields=['is_booked','booked_by','booked_at'])

    def unbook(self):
        self.is_booked = False
        self.booked_by = None
        self.booked_at = None
        self.save(update_fields=['is_booked','booked_by','booked_at'])


# test
# core/models.py  (append near end of file)
from django.conf import settings

class TestRide(models.Model):
    STATUS_PENDING = "pending"
    STATUS_CONFIRMED = "confirmed"
    STATUS_COMPLETED = "completed"
    STATUS_CANCELLED = "cancelled"
    STATUS_CHOICES = [
        (STATUS_PENDING, "Pending"),
        (STATUS_CONFIRMED, "Confirmed"),
        (STATUS_COMPLETED, "Completed"),
        (STATUS_CANCELLED, "Cancelled"),
    ]

    bike = models.ForeignKey('core.Bike', on_delete=models.CASCADE, related_name='test_rides')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='test_rides')
    phone = models.CharField(max_length=20, blank=True, null=True, help_text="Optional contact phone")
    refundable_amount = models.DecimalField(max_digits=10, decimal_places=2, default=1000.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default=STATUS_PENDING)
    created_at = models.DateTimeField(auto_now_add=True)
    scheduled_for = models.DateTimeField(blank=True, null=True)  # optional future schedule
    notes = models.TextField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = "Test Ride"
        verbose_name_plural = "Test Rides"

    def __str__(self):
        return f"TestRide #{self.pk} - {self.bike} by {self.user}"


# home page
from django.db import models
from django.utils.html import mark_safe

class HomePage(models.Model):
    """
    Single row model for homepage hero (create one instance in admin).
    """
    hero_heading = models.CharField(max_length=200, default="Buy or Sell Bikes the Smarter Way")
    # the exact substring to highlight in the heading (optional).
    # If present and found inside hero_heading, it will be wrapped with <span class="highlight">...</span>.
    hero_highlight = models.CharField(max_length=80, blank=True, help_text="Put the exact word/phrase to highlight, e.g. 'Buy or Sell Bikes'")

    hero_paragraph = models.TextField(
        default="Skip the hassle. Discover verified secondhand bikes at great prices or list your own in minutes. We’re here to help you ride more, spend less, and keep bikes moving — from one happy rider to the next."
    )

    hero_button_text = models.CharField(max_length=40, default="Buy Now")
    hero_button_url = models.CharField(max_length=255, blank=True, default="#")

    # small tuning (timing of carousel)
    carousel_interval = models.PositiveIntegerField(default=3500, help_text="Milliseconds between image changes")

    def heading_html(self):
        """
        Return heading HTML with the highlight span around first occurrence of hero_highlight.
        If hero_highlight not set or not found, returns escaped plain heading.
        """
        text = self.hero_heading or ""
        hl = (self.hero_highlight or "").strip()
        if hl and hl in text:
            before, after = text.split(hl, 1)
            return mark_safe(f"{before}<span class=\"highlight\">{hl}</span>{after}")
        # fallback: return plain heading
        return mark_safe(text)

    def __str__(self):
        return "Home Page Hero"

class HeroImage(models.Model):
    home = models.ForeignKey(HomePage, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="home/hero/")
    order = models.PositiveSmallIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"Hero image #{self.pk}"


# home 2nd section
from django.db import models
from django.utils.html import mark_safe

class HomeFeature(models.Model):
    """
    A feature block on the home page (left image + right content).
    Create one or multiple (use order to control display).
    """
    title = models.CharField(max_length=140, default="Buying and selling secondhand bikes isn’t just a smart financial decision")
    paragraph = models.TextField(default="— it’s a sustainable one. When you buy a pre-owned bike, you save money while gaining access to a wider variety of models, often already assembled and ready to ride. It's an eco-friendly choice that helps reduce manufacturing waste and supports a circular economy. On the other hand, selling your bike allows you to earn extra cash, declutter your space, and pass on a reliable ride to someone new.")
    button_text = models.CharField(max_length=40, default="Read More")
    button_url = models.CharField(max_length=255, blank=True, default="#")

    # the image displayed on the left
    image = models.ImageField(upload_to="home/feature/", blank=True, null=True)

    # small tuning and ordering
    order = models.PositiveSmallIntegerField(default=0, help_text="Lower numbers show first")

    # show or hide
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ("order",)
        verbose_name = "Home Feature Section"
        verbose_name_plural = "Home Feature Sections"

    def __str__(self):
        return f"Feature: {self.title[:40]}"


# support section
from django.db import models

class SupportSection(models.Model):
    """Single-row model to hold the section heading and a toggle to show/hide."""
    heading = models.CharField(max_length=160, default="Get the Support You Needs")
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return "Home Support Section"

class SupportItem(models.Model):
    """
    One of the four support items (icon image + short title + text).
    direction: 'down' => arrow flows top->around->down; 'up' => arrow flows bottom->around->up.
    """
    DIRECTION_CHOICES = (
        ('down','Down (arrow points down)'),
        ('up','Up (arrow points up)'),
    )

    section = models.ForeignKey(SupportSection, on_delete=models.CASCADE, related_name='items')
    title = models.CharField(max_length=80)
    text = models.TextField(blank=True)
    image = models.ImageField(upload_to='home/support/')
    order = models.PositiveSmallIntegerField(default=0)
    direction = models.CharField(max_length=4, choices=DIRECTION_CHOICES, default='down')
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ('order',)

    def __str__(self):
        return f"{self.title}"


# seelbike page
# core/models.py
from django.db import models
from django.conf import settings
from django.utils import timezone

class Banner(models.Model):
    """Editable homepage / sell hero content managed via admin."""
    title_line_1 = models.CharField(max_length=120, blank=True)
    title_line_2 = models.CharField(max_length=120, blank=True)
    title_line_3 = models.CharField(max_length=120, blank=True)
    subtitle = models.CharField(max_length=200, blank=True)
    image = models.ImageField(upload_to='banners/', null=True, blank=True)
    accent_color = models.CharField(max_length=7, default="#0b5fa5", help_text="Hex color (for accents)")

    def __str__(self):
        return f"Banner #{self.pk} - {self.title_line_1 or 'hero'}"

OWNER_CHOICES = [
    ('1st Owner','1st Owner'),
    ('2nd Owner','2nd Owner'),
    ('3rd+ Owner','3rd+ Owner'),
]

KMS_CHOICES = [
    ('Under 5,000','Under 5,000'),
    ('5,000 - 20,000','5,000 - 20,000'),
    ('20,000 - 50,000','20,000 - 50,000'),
    ('50,000+','50,000+'),
]

class SellRequest(models.Model):
    """A seller-submitted estimate request tied to a user (optional)."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True)
    brand = models.CharField(max_length=80)
    model = models.CharField(max_length=120)
    variant = models.CharField(max_length=120)
    year = models.PositiveIntegerField()
    kms_range = models.CharField(max_length=40, choices=KMS_CHOICES)
    owner = models.CharField(max_length=30, choices=OWNER_CHOICES)
    estimated_price = models.PositiveIntegerField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    name = models.CharField(max_length=120, blank=True, help_text="Optional seller name")
    phone = models.CharField(max_length=30, blank=True, help_text="Optional phone")
    notes = models.TextField(blank=True)

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year}) - {self.estimated_price or 'N/A'}"


from django.db import models

# Section 1: Satisfied Customers
class SatisfiedCustomerSection(models.Model):
    heading = models.CharField(max_length=255)
    logo = models.ImageField(upload_to="home/")
    # three stats
    stat1_icon = models.ImageField(upload_to="home/")
    stat1_number = models.CharField(max_length=50)
    stat1_text = models.CharField(max_length=100)

    stat2_icon = models.ImageField(upload_to="home/")
    stat2_number = models.CharField(max_length=50)
    stat2_text = models.CharField(max_length=100)

    stat3_icon = models.ImageField(upload_to="home/")
    stat3_number = models.CharField(max_length=50)
    stat3_text = models.CharField(max_length=100)

    def __str__(self):
        return self.heading


# Section 2: Happy Customers
class HappyCustomer(models.Model):
    name = models.CharField(max_length=100)
    role = models.CharField(max_length=100)
    photo = models.ImageField(upload_to="home/")
    feedback = models.TextField()

    def __str__(self):
        return self.name


# Section 3: Trusted Riders
class TrustedRidersSection(models.Model):
    heading = models.CharField(max_length=255)
    subtext = models.TextField()
    image = models.ImageField(upload_to="home/")

    def __str__(self):
        return self.heading


# Section 4: FAQ
class FAQ(models.Model):
    question = models.CharField(max_length=255)
    answer = models.TextField()

    def __str__(self):
        return self.question
