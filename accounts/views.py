from django.contrib import messages
from django.contrib.auth import login as auth_login
from django.contrib.auth import authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import (
    LoginView, logout_then_login, 
    PasswordChangeView as AuthPasswordChangeView
)
from django.contrib.auth.forms import AuthenticationForm
# from django.contrib.auth.backends import authenticate
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from .forms import SignUpForm, ProfileForm, PasswordChangeForm
from .models import User

# login = LoginView.as_view(template_name="accounts/login_form.html")

def login(request):
    if request.method == "POST":
        form = AuthenticationForm(request, request.POST)
        if form.is_valid():
            user = authenticate(username=request.POST['username'], password=request.POST['password'])
            if user is not None:
                if user.is_active:
                    auth_login(request, user)
                    messages.success(request, "로그인되었습니다.")
                    return redirect('instagram:index')
                else:
                    messages.error(request, "관리자의 승인을 기다려주세요.")
        
        else:
            messages.error(request, "로그인 실패하셨습니다")
    else:
        form = AuthenticationForm()
    
    context = {
        'form': form
    }
    return render(request, "accounts/login_form.html", context)

def logout(request):
    messages.success(request, '로그아웃되었습니다.')
    return logout_then_login(request)

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            signed_user = form.save()
            signed_user.is_active = False
            signed_user.save()
            # auth_login(request, signed_user)
            # user_follow(request, "admin")
            messages.success(request, '회원가입 환영합니다.')
            # signed_user.send_welcome_email()    # 비동기, Celery로 처리할 것 추천.
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup_form.html', {
        'form': form,
    })
    
@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, '프로필을 수정/저장했습니다.')
            return redirect('accounts:profile_edit')
    else:
        form = ProfileForm(instance=request.user)
    return render(request, 'accounts/profile_edit_form.html', {
        'form': form
    })

class PasswordChangeView(LoginRequiredMixin, AuthPasswordChangeView):
    success_url = reverse_lazy("accounts:password_change")
    template_name = 'accounts/password_change_form.html'
    form_class = PasswordChangeForm

    def form_valid(self, form):
        messages.success(self.request, '암호를 변경했습니다'),
        return super().form_valid(form)

password_change = PasswordChangeView.as_view()

@login_required
def user_follow(request, username):
    follow_user = get_object_or_404(User, username=username, is_active=True)
    # request.user => follow_user를 팔로우하려고 합니다.
    request.user.following_set.add(follow_user)
    # 당하는 입장에서는
    follow_user.follower_set.add(request.user)
    messages.success(request, f"{follow_user.name}님을 팔로우했습니다.")
    redirect_url = request.META.get("HTTP_REFERER", "root") # HTTP_REFERER는 실제 url, root은 url 리버스/패턴 네임
    return redirect(redirect_url)

@login_required
def user_unfollow(request, username):
    unfollow_user = get_object_or_404(User, username=username, is_active=True)
    request.user.following_set.remove(unfollow_user)
    unfollow_user.follower_set.remove(request.user)
    messages.success(request, f"{follow_user.name}님을 언팔로우했습니다.")
    redirect_url = request.META.get("HTTP_REFERER", "root")
    return redirect(redirect_url)