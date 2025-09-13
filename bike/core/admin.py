from django.contrib import admin
from .models import SiteBrand, NavItem

@admin.register(SiteBrand)
class SiteBrandAdmin(admin.ModelAdmin):
    list_display = ('left_text', 'right_text', 'left_color', 'right_color', 'shadow')

@admin.register(NavItem)
class NavItemAdmin(admin.ModelAdmin):
    list_display = ('title', 'url', 'order', 'is_external')
    list_editable = ('order', 'is_external')

# about page
from django.contrib import admin
from .models import AboutPage, ApproachImage

class ApproachImageInline(admin.TabularInline):
    model = ApproachImage
    extra = 1
    fields = ('image', 'caption', 'order', 'grid_position', 'image_tag',)
    readonly_fields = ('image_tag',)

@admin.register(AboutPage)
class AboutPageAdmin(admin.ModelAdmin):
    inlines = [ApproachImageInline]
    list_display = ('__str__',)
    fieldsets = (
        (None, {
            'fields': ('title','intro_heading','highlight_text','intro_paragraph','hero_image')
        }),
        ('Mission / success banner', {
            'fields': ('success_image','mission_title','mission_text','mission_overlay_opacity')
        }),
        ('Approach', {
            'fields': ('approach_heading','approach_paragraph')
        }),
    )

@admin.register(ApproachImage)
class ApproachImageAdmin(admin.ModelAdmin):
    list_display = ('__str__','order','grid_position','image_tag')
    readonly_fields = ('image_tag',)
    ordering = ('order',)

# buybike 
from django.contrib import admin
from django.utils.html import format_html
from .models import Bike

@admin.register(Bike)
class BikeAdmin(admin.ModelAdmin):
    list_display = ('id','category','brand','model','variant','make_year','price','owner','is_booked','is_published')
    list_filter = ('category','brand','make_year','is_booked','is_published','fuel_type')
    search_fields = ('brand','model','variant','location','owner__username')
    readonly_fields = ('created_at','updated_at','booked_at')

    fieldsets = (
        (None, {'fields': ('owner','category','brand','model','variant','price','is_published','is_booked','booked_by','booked_at')}),
        ('Specs', {'fields': ('make_year','kilometers','fuel_type','previous_owner','transmission','odometer_type','wheel_type','bike_color')}),
        ('Brakes & Ignition', {'fields': ('front_brake_type','rear_brake_type','abs_available','ignition_type')}),
        ('RTO & Registration', {'fields': ('rto_state','rto_city','registration_year','registration_certificate')}),
        ('Images', {'fields': ('main_image','thumb1','thumb2','thumb3','thumb4','thumb5','thumb6')}),
        ('Other', {'fields': ('refurbished','finance_available','insurance_available','warranty','location')}),
        ('Timestamps', {'fields': ('created_at','updated_at')}),
    )

    def image_thumb(self,obj):
        if obj.main_image:
            return format_html('<img src="{}" style="height:60px;border-radius:6px;"/>', obj.main_image.url)
        return '-'
    image_thumb.short_description = "Main"

# home page
from django.contrib import admin
from .models import HomePage, HeroImage

class HeroImageInline(admin.TabularInline):
    model = HeroImage
    extra = 1
    fields = ("image", "order",)
    readonly_fields = ()

@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    inlines = [HeroImageInline]
    list_display = ("__str__", "hero_button_text")
    fieldsets = (
        (None, {"fields": ("hero_heading", "hero_highlight", "hero_paragraph")}),
        ("CTA", {"fields": ("hero_button_text", "hero_button_url")}),
        ("Carousel", {"fields": ("carousel_interval",)}),
    )

@admin.register(HeroImage)
class HeroImageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order")
    ordering = ("order",)

# home 2nd section
from django.contrib import admin
from .models import HomeFeature

@admin.register(HomeFeature)
class HomeFeatureAdmin(admin.ModelAdmin):
    list_display = ("__str__", "order", "is_active")
    list_editable = ("order", "is_active")
    fields = ("title", "paragraph", "image", "button_text", "button_url", "order", "is_active")

# support section homepage
from django.contrib import admin
from .models import SupportSection, SupportItem

class SupportItemInline(admin.TabularInline):
    model = SupportItem
    extra = 1
    fields = ("image","title","text","order","direction","is_active")
    readonly_fields = ()

@admin.register(SupportSection)
class SupportSectionAdmin(admin.ModelAdmin):
    inlines = [SupportItemInline]
    list_display = ("heading","is_active")


# sellbike page
# core/admin.py
from django.contrib import admin
from .models import Banner, SellRequest

@admin.register(Banner)
class BannerAdmin(admin.ModelAdmin):
    list_display = ('id', 'title_line_1', 'title_line_2', 'title_line_3')
    readonly_fields = ()
    search_fields = ('title_line_1', 'title_line_2')

@admin.register(SellRequest)
class SellRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'brand', 'model', 'variant', 'year', 'kms_range', 'owner', 'estimated_price', 'user', 'created_at')
    list_filter = ('brand','owner','kms_range','created_at')
    search_fields = ('brand','model','variant','phone','name')
    readonly_fields = ('estimated_price', 'created_at')

from django.contrib import admin
from .models import SatisfiedCustomerSection, HappyCustomer, TrustedRidersSection, FAQ

admin.site.register(SatisfiedCustomerSection)
admin.site.register(HappyCustomer)
admin.site.register(TrustedRidersSection)
admin.site.register(FAQ)
