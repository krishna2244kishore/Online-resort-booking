from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from django.utils import timezone
from django.views.decorators.csrf import ensure_csrf_cookie, csrf_protect
from .models import Resort, Booking, UserProfile
from .forms import UserRegistrationForm, ResortForm, BookingForm, BookingResponseForm

@ensure_csrf_cookie
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            UserProfile.objects.create(
                user=user,
                is_resort_owner=form.cleaned_data.get('is_resort_owner', False),
                phone=form.cleaned_data.get('phone', ''),
                address=form.cleaned_data.get('address', '')
            )
            login(request, user)
            messages.success(request, 'Registration successful!')
            return redirect('resorts:home')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

@ensure_csrf_cookie
def login_view(request):
    if request.user.is_authenticated:
        return redirect('resorts:home')
        
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            login(request, user)
            next_url = request.GET.get('next', 'resorts:home')
            messages.success(request, f'Welcome back, {user.username}!')
            return redirect(next_url)
        else:
            messages.error(request, 'Invalid username or password.')
    
    return render(request, 'registration/login.html')

@login_required
def logout_view(request):
    # Clear session data
    request.session.flush()
    # Logout the user
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('resorts:login')

@login_required
def home(request):
    resorts = Resort.objects.filter(is_available=True)
    return render(request, 'resorts/home.html', {'resorts': resorts})

@login_required
@csrf_protect
def resort_create(request):
    # Check if user is a resort owner
    try:
        profile = request.user.userprofile
        if not profile.is_resort_owner:
            messages.error(request, "Only resort owners can create resorts.")
            return redirect('resorts:home')
    except UserProfile.DoesNotExist:
        messages.error(request, "Only resort owners can create resorts.")
        return redirect('resorts:home')

    if request.method == 'POST':
        form = ResortForm(request.POST, request.FILES)
        if form.is_valid():
            resort = form.save(commit=False)
            resort.owner = request.user
            resort.save()
            messages.success(request, 'Resort created successfully!')
            return redirect('resorts:resort-detail', resort_id=resort.id)
    else:
        form = ResortForm()
    
    return render(request, 'resorts/resort_form.html', {
        'form': form,
        'edit_mode': False
    })

@login_required
@csrf_protect
def resort_edit(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)
    
    # Check if user owns this resort
    if resort.owner != request.user:
        messages.error(request, "You don't have permission to edit this resort.")
        return redirect('resorts:home')
    
    if request.method == 'POST':
        form = ResortForm(request.POST, request.FILES, instance=resort)
        if form.is_valid():
            form.save()
            messages.success(request, 'Resort updated successfully!')
            return redirect('resorts:resort-detail', resort_id=resort.id)
    else:
        form = ResortForm(instance=resort)
    
    return render(request, 'resorts/resort_form.html', {
        'form': form,
        'resort': resort,
        'edit_mode': True
    })

@login_required
@csrf_protect
def resort_delete(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)
    
    # Check if user owns this resort
    if resort.owner != request.user:
        messages.error(request, "You don't have permission to delete this resort.")
        return redirect('resorts:home')
    
    if request.method == 'POST':
        resort.delete()
        messages.success(request, 'Resort deleted successfully!')
        return redirect('resorts:my-resorts')
    
    return render(request, 'resorts/resort_confirm_delete.html', {'resort': resort})

@login_required
@csrf_protect
def my_resorts(request):
    resorts = Resort.objects.filter(owner=request.user)
    return render(request, 'resorts/my_resorts.html', {'resorts': resorts})

@login_required
@csrf_protect
def resort_manage(request):
    if not request.user.userprofile.is_resort_owner:
        messages.error(request, 'Only resort owners can access this page.')
        return redirect('resorts:home')
    
    resorts = Resort.objects.filter(owner=request.user)
    return render(request, 'resorts/resort_manage.html', {'resorts': resorts})

@login_required
@csrf_protect
def resort_detail(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)
    return render(request, 'resorts/resort_detail.html', {'resort': resort})

@login_required
@csrf_protect
def create_booking(request, resort_id):
    resort = get_object_or_404(Resort, id=resort_id)
    
    # Check if resort is available
    if not resort.is_available:
        messages.error(request, "Sorry, this resort is not available for booking.")
        return redirect('resorts:home')
    
    # Check if user is not trying to book their own resort
    if resort.owner == request.user:
        messages.error(request, "You cannot book your own resort.")
        return redirect('resorts:home')

    if request.method == 'POST':
        form = BookingForm(request.POST)
        if form.is_valid():
            booking = form.save(commit=False)
            booking.user = request.user
            booking.resort = resort
            booking.total_price = resort.price_per_night * (booking.check_out_date - booking.check_in_date).days
            booking.status = 'pending'
            booking.save()
            
            messages.success(request, f'Booking request for {resort.name} has been submitted successfully!')
            return redirect('resorts:my-bookings')
    else:
        form = BookingForm()
    
    return render(request, 'resorts/booking_form.html', {
        'form': form,
        'resort': resort
    })

@login_required
@csrf_protect
def my_bookings(request):
    bookings = Booking.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'resorts/my_bookings.html', {'bookings': bookings})

@login_required
@csrf_protect
def resort_bookings(request):
    # Get all bookings for resorts owned by the current user
    bookings = Booking.objects.filter(resort__owner=request.user).order_by('-created_at')
    return render(request, 'resorts/resort_bookings.html', {'bookings': bookings})

@login_required
@csrf_protect
def booking_respond(request, booking_id):
    # Get the booking and verify ownership
    booking = get_object_or_404(Booking, id=booking_id, resort__owner=request.user)
    
    if request.method == 'POST':
        form = BookingResponseForm(request.POST, instance=booking)
        if form.is_valid():
            booking = form.save(commit=False)
            if booking.status == 'approved':
                messages.success(request, f'Booking #{booking.id} has been approved! The guest will be notified.')
            elif booking.status == 'rejected':
                messages.info(request, f'Booking #{booking.id} has been rejected.')
            booking.save()
            return redirect('resorts:resort-bookings')
    else:
        form = BookingResponseForm(instance=booking)
    
    return render(request, 'resorts/booking_respond.html', {
        'form': form,
        'booking': booking
    })

@login_required
@csrf_protect
def cancel_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    if booking.status == 'pending':
        booking.status = 'cancelled'
        booking.save()
        messages.success(request, 'Booking cancelled successfully.')
    else:
        messages.error(request, 'This booking cannot be cancelled.')
    return redirect('resorts:my-bookings')
