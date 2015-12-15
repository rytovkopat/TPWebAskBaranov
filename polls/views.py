from django.http import HttpResponse, HttpResponseRedirect, JsonResponse, Http404
from django.shortcuts import render
from django.core.paginator import Paginator, EmptyPage
from polls.models import Question, Logic, CustomUser, Tag, Answer, Like
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth import authenticate, login as djangoLogin, logout as djangoLogout
from polls.forms import RegisterForm, MainSettingsForm, PswSettingsForm, AvatarSettingsForm, LoginForm, QuestionForm, AnswerForm
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.decorators import login_required


def paginate(request, qs):
    try:
        limit = int(request.GET.get('limit', 5))
    except ValueError:
        limit = 10
    if limit > 100:
        limit = 10
    try:
        page = int(request.GET.get('page', 1))
    except ValueError:
        raise Http404
    paginator = Paginator(qs, limit)
    #paginator.page_range = 5
    
    try:
        page = paginator.page(page)
    except EmptyPage:
        page = paginator.page(paginator.num_pages)
    return page


def index(request, order=None):
    context = {}
    context.update({'user': get_authenticate_user(request)})
    if not order or order == 'newest':
        questions = Question.manager.get_new_queryset()
    elif order == 'hot':
        questions = Question.manager.get_best_queryset()
    else:
        raise Http404

    page = paginate(request, questions)
    context.update({'question_list': page, 'order': order})
    response = render(request, 'index.html', context)
    return response


def tag(request, tag):
    context = {}
    context.update({'user': get_authenticate_user(request)})
    questions = Logic.get_tag(tag=tag)
    page = paginate(request, questions)
    context.update({'question_list': page, 'tag': tag})
    response = render(request, 'index.html', context)
    return response


def question(request, question_id):
    context = {}
    try:
        question_ = Question.objects.get(pk=question_id)
    except ObjectDoesNotExist:
        raise Http404
    form = AnswerForm()
    user = get_authenticate_user(request)
    if user:
        if request.method == 'POST':
            form = AnswerForm(request.POST)
        if form.is_valid():
            answer = Answer.objects.create(
                                author=user,
                                content=form.cleaned_data.get('content'),
                                created=datetime.now(),
                                question=question_)
            answer.save()

    answers = Logic.get_order(question=question_)
    page = paginate(request, answers)
    context.update({'question': question_, 'answer_list': page, 'user': user})
    response = render(request, 'questions.html', context)
    return response


@login_required(login_url='/login/')
def ask(request):
    user = get_authenticate_user(request)
    context = {'user': user}
    form = QuestionForm()
    if request.method == 'POST':
        form = QuestionForm(request.POST)
        if form.is_valid():
            question = Question.objects.create(
            author=user,
            title=form.cleaned_data.get('title'),
            content=form.cleaned_data.get('content'),
            created=datetime.now()
            )
            tags = form.cleaned_data.get('tags').split(',')
            for tag in tags:
                try:
                    if ' ' in tag:
                        tag = tag.replace(' ', '_')
                    t = Tag.objects.get(title=tag)
                except Tag.DoesNotExist:
                    t = Tag.objects.create(title=tag)
                    t.save()
                question.tags.add(t)
            question.save()
            return HttpResponseRedirect('/question/' + str(question.id))
    context.update({'form': form})
    return render(request, 'ask.html', context)


def login(request):
    redirect_to = request.GET.get('next', '/')
    context = {'user': get_authenticate_user(request)}
    form = LoginForm()
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.login_user(request):
            return HttpResponseRedirect(redirect_to)
    context.update({'form': form})
    return render(request, 'login.html', context)


def register(request):
    if request.user.is_authenticated():
        return HttpResponseRedirect('/')
    context = ({'user': get_authenticate_user(request)})
    form = RegisterForm()

    try:
        path = request.GET['continue']
    except KeyError:
        path='/'

    if request.method == 'POST':
        form = RegisterForm(request.POST, request.FILES)
        if form.save_user():
            return HttpResponseRedirect(path)
        else:
            HttpResponseRedirect('/')

    user = get_authenticate_user(request)
    context.update({'user': user, 'form': form})
    return render(request, 'signup.html', context)


def get_authenticate_user(request):
    if request.user.is_authenticated():
        user = CustomUser.objects.get(user_ptr_id=request.user.id)
    else:
        user = None
    return user


def logout(request):
    djangoLogout(request)
    return HttpResponseRedirect('/')


@login_required(login_url='/login/')
def settings(request):
    User = get_authenticate_user(request)

    if request.method == 'POST':
        if 'login' in request.POST:
            mainForm = MainSettingsForm(request.POST)

            if mainForm.is_valid_(User):
                User.username = mainForm.cleaned_data.get('login')
                User.email = mainForm.cleaned_data.get('email')
                User.first_name = mainForm.cleaned_data.get('nickName')
                User.save()

            login = request.POST.get('login')
            email = request.POST.get('email')
            nickName = request.POST.get('nickName')
        else:
            login = User.username
            email = User.email
            nickName = User.first_name
            mainForm = MainSettingsForm()

        if 'password1' in request.POST:
            pswForm = PswSettingsForm(request.POST)
            if pswForm.is_valid_():
                User.set_password(pswForm.cleaned_data.get('password1'))
                User.save()
        else:
            pswForm = PswSettingsForm()

        if 'avatar' in request.FILES:
            avatarForm = AvatarSettingsForm(request.POST, request.FILES)
            if avatarForm.is_valid():
                User.avatar = avatarForm.cleaned_data.get('avatar')
                User.save()
        else:
            avatarForm = AvatarSettingsForm()

    else:
        login = User.username
        email = User.email
        nickName = User.first_name
        mainForm = MainSettingsForm()
        pswForm = PswSettingsForm()
        avatarForm = AvatarSettingsForm()

    context = {'user':User, 'mainForm':mainForm, 'pswForm': pswForm, 'avatarForm':avatarForm, 'login':login, 'email':email, 'nickName':nickName}
    return render(request, 'settings.html', context)


def like(request):
    if request.method == 'POST':
        response_data = {}
        user = get_authenticate_user(request)

        object_id = int(request.POST.get('object_id',''))
        like_type = int(request.POST.get('like_type',''))
        object_type = request.POST.get('object_type','')

        if user:
            new_rating = None
            error = None

            if object_type == 'answer':
                answ = Answer.objects.get(id=object_id)

                if user != answ.author:
                    try:
                        like = Like.objects.filter(answer__id=object_id).get(author=user)
                        var = setRatingVar(like_type, int(like.value))
                        like.value = like_type
                        like.save()
                    except:
                        like = Like.objects.create(author=user, value=like_type)
                        like.save()
                        answ.likes.add(like)
                        var = like_type

                    answ.rating = str(var + answ.rating)
                    answ.save()
                    new_rating = answ.rating
                    result = 'Create like successful!'
                else:
                    result = 'Like wasn\'t created!'
                    error = 'It is your answer!'

            elif object_type == 'question':
                quest = Question.objects.get(id=object_id)

                if user != quest.author:
                    try:
                        like = Like.objects.filter(question__id=object_id).get(author=user)
                        var = setRatingVar(like_type, int(like.value))
                        like.value = like_type
                        like.save()
                    except:
                        like = Like.objects.create(author=user, value=like_type)
                        like.save()
                        quest.likes.add(like)
                        var = like_type

                    quest.rating = str(var + quest.rating)
                    quest.save()
                    new_rating = quest.rating
                    result = 'Create like successful!'
                else:
                    result = 'Like wasn\'t created!'
                    error = 'It is your question!'

            else:
                result = 'Like wasn\'t created!'
                error = 'Object not found!'

            response_data['result'] = result
            if new_rating:
                response_data['new_rating'] = new_rating
            if error:
                response_data['error'] = error

        else:
            response_data['result'] = 'Like wasn\'t created!'
            response_data['error'] = 'User is not authenticated!'

        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "No POST data!"})


def setRatingVar(like_type, last_type):
    if last_type == -1:
        if like_type == -1:
            var = 0
        else:
            var = like_type + 1
    elif last_type == 1:
        if like_type == 1:
            var = 0
        else:
            var = like_type - 1
    else:
        var = like_type
    return var


def set_correct(request):
    if request.method == 'POST':
        response_data = {}

        user = get_authenticate_user(request)

        answer_id = int(request.POST.get('answer_id',''))

        if user:
            answ = Answer.objects.get(id=answer_id)

            if user == answ.question.author:
                answ.correct =  not answ.correct
                answ.save()
                result = 'Set correct successful!'
            else:
                result = 'Set correct wasn\'t checked!'
                response_data['error'] = 'This question isn\'t your!'

            response_data['result'] = result
            response_data['new_state'] = answ.correct
        else:
            response_data['result'] = 'Set correct wasn\'t checked!'
            response_data['error'] = 'User is not authenticated!'

        return JsonResponse(response_data)
    else:
        return JsonResponse({"error": "No POST data!"})


