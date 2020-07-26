from django.contrib import messages
from django.shortcuts import redirect, render
from .forms import SignUpForm

def signup(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            signed_user = form.save()
            messages.success(request, '회원가입 환영합니다.')
            signed_user.send_welcome_email()    # 비동기, Celery로 처리할 것 추천.
            next_url = request.GET.get('next', '/')
            return redirect(next_url)
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup_form.html', {
        'form': form
    })
    