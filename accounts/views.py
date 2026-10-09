from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import RegisterForm


def index(request):
    """首页（落地页）。"""
    return render(request, 'accounts/index.html')


def register(request):
    """用户注册。"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  # 注册成功后自动登录
            messages.success(request, f'注册成功，欢迎 {user.username}！')
            return redirect('home')
    else:
        form = RegisterForm()

    return render(request, 'accounts/register.html', {'form': form})


def login_view(request):
    """用户登录。"""
    if request.user.is_authenticated:
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username', '').strip()
        password = request.POST.get('password', '')
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, f'登录成功，欢迎回来 {user.username}！')
            return redirect('home')
        else:
            messages.error(request, '用户名或密码错误')

    return render(request, 'accounts/login.html')


def logout_view(request):
    """退出登录。"""
    logout(request)
    messages.info(request, '你已安全退出')
    return redirect('login')


@login_required
def home(request):
    """个人中心。"""
    return render(request, 'accounts/home.html')


@login_required
def update_score(request):
    """更新最高分（供贪吃蛇游戏提交分数）。"""
    if request.method == 'POST':
        try:
            score = int(request.POST.get('score', 0))
        except (ValueError, TypeError):
            score = 0

        profile = request.user.profile
        if score > profile.high_score:
            profile.high_score = score
            profile.save()
            messages.success(request, f'新纪录！最高分已更新为 {score}')
        else:
            messages.info(request, f'本次得分 {score}，未超过历史最高分 {profile.high_score}')

    return redirect('home')
