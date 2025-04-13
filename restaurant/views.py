from django.db.models import Q
from django.shortcuts import get_object_or_404, render, redirect
from django.views.generic.list import ListView
from .models import Restaurant, Menu, Feedback
from django.shortcuts import render, redirect
from django.views import View
from .forms import FeedbackForm,CustomUserCreationForm
from django.http import HttpResponseRedirect
from django.views.generic import TemplateView
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator
from django.contrib.auth import update_session_auth_hash
from .forms import ProfileUpdateForm, PasswordChangeWithOldPasswordForm
from django.core.paginator import Paginator
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


class RestaurantListView(ListView):
    model = Restaurant
    template_name = 'restaurant/restaurant_list.html'
    context_object_name = 'restaurants'
    paginate_by = 10  # This is already correct

    def get_queryset(self):
        queryset = Restaurant.objects.all().order_by('-rating')
        # Extract search and category parameters
        query = self.request.GET.get('q', '').strip()
        category = self.request.GET.get('category', '').strip()
        
        # Apply filters only if there is a valid input
        if query:
            queryset = queryset.filter(
                Q(name__icontains=query) |
                Q(description__icontains=query) |
                Q(location__icontains=query)
            )
        if category:
            queryset = queryset.filter(cuisine=category)
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        # Get the full queryset
        queryset = self.get_queryset()

        # Apply pagination manually
        paginator = Paginator(queryset, self.paginate_by)
        page = self.request.GET.get('page', 1)
        try:
            paginated_restaurants = paginator.page(page)
        except PageNotAnInteger:
            paginated_restaurants = paginator.page(1)
        except EmptyPage:
            paginated_restaurants = paginator.page(paginator.num_pages)

        # Update the context with paginated data
        context['restaurants'] = paginated_restaurants
        context['current_page'] = paginated_restaurants.number
        context['total_pages'] = paginator.num_pages
        context['has_next'] = paginated_restaurants.has_next()
        context['has_previous'] = paginated_restaurants.has_previous()
        context['search_query'] = self.request.GET.get('q', '')
        context['selected_category'] = self.request.GET.get('category', '')
        context['categories'] = Restaurant.CATEGORY_CHOICES
        return context


class MenuListView(ListView):
    """Protected view to display the menu of a specific restaurant."""
    model = Menu
    template_name = 'restaurant/menu_list.html'
    context_object_name = 'menus'

    def get_queryset(self):
        self.restaurant = get_object_or_404(Restaurant, pk=self.kwargs['restaurant_id'])
        return Menu.objects.filter(restaurant=self.restaurant)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant'] = self.restaurant
        context['feedbacks'] = self.restaurant.feedbacks.all().order_by('-created_at')
        return context


class FeedbackListView(ListView):
    """Public view to display feedback for a specific restaurant."""
    model = Feedback
    template_name = 'restaurant/feedback_list.html'
    context_object_name = 'feedbacks'

    def get_queryset(self):
        self.restaurant = get_object_or_404(Restaurant, pk=self.kwargs['restaurant_id'])
        return Feedback.objects.filter(restaurant=self.restaurant).order_by('-created_at')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['restaurant'] = self.restaurant
        return context


@method_decorator(login_required, name='dispatch')
class FeedbackCreateView(View):
    """View for customers to give feedback."""
    def get(self, request, restaurant_id):
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        form = FeedbackForm()
        return render(request, 'restaurant/feedback_form.html', {'form': form, 'restaurant': restaurant})

    def post(self, request, restaurant_id, *args, **kwargs):
        restaurant = get_object_or_404(Restaurant, pk=restaurant_id)
        form = FeedbackForm(request.POST)
        if form.is_valid():
            feedback = form.save(commit=False)
            feedback.restaurant = restaurant
            feedback.user = request.user  # Associate feedback with the logged-in user
            feedback.save()
            # Redirect back to the restaurant's menu page
            return HttpResponseRedirect(f'/restaurant/menu/{restaurant_id}/')
        return render(request, 'restaurant/feedback_form.html', {'form': form, 'restaurant': restaurant})


class AboutView(TemplateView):
    template_name = 'restaurant/about.html'


def register_view(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            username = form.cleaned_data.get('username')
            messages.success(request, f'Account created for {username}! You can now log in.')
            return redirect('restaurant_list')
    else:
        form = CustomUserCreationForm()
    return render(request, 'restaurant/register.html', {'form': form})

def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            return redirect('restaurant_list')
        else:
            messages.error(request, 'Invalid username or password.')
    return render(request, 'restaurant/login.html')

def logout_view(request):
    logout(request)
    return redirect('restaurant_list')

@login_required
def profile(request):
    if request.method == 'POST':
        # Handle Profile Update
        profile_form = ProfileUpdateForm(request.POST, instance=request.user)
        password_form = PasswordChangeWithOldPasswordForm(user=request.user, data=request.POST)

        if 'update_profile' in request.POST:
            # If user updates profile (name, email)
            if profile_form.is_valid():
                profile_form.save()
                messages.success(request, "Your profile has been updated!")
                return redirect('profile')  # Redirect to the same page to show the updated information

        elif 'change_password' in request.POST:
            # If user changes password
            if password_form.is_valid():
                password_form.save()
                update_session_auth_hash(request, password_form.user)  # Keep the user logged in after password change
                messages.success(request, "Your password has been updated!")
                return redirect('profile')  # Redirect to avoid resubmission of form

        else:
            messages.error(request, "There was an error with the form submission.")
    else:
        profile_form = ProfileUpdateForm(instance=request.user)
        password_form = PasswordChangeWithOldPasswordForm(user=request.user)

    return render(request, 'restaurant/profile.html', {'profile_form': profile_form, 'password_form': password_form})

