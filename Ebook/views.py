from django.core.checks import messages
from django.http.response import Http404
from django.shortcuts import redirect, render, get_object_or_404
from django.http import HttpResponse
from django.template.defaultfilters import slugify
from django.views.decorators.cache import never_cache
from django.core.exceptions import ObjectDoesNotExist
from django.views.decorators.csrf import csrf_exempt
from django.db.models import Q, Count, Max, OuterRef, Subquery

from .models import Bookmark, Comment, Following, Novel, Chapter, Rating, Tag, UserInfo
from .decorator import *
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from .forms import CreateUserForm, CreateUserInfoForm, CreateNovelForm, CreateChapterForm, CreateRatingForm
from django.contrib.auth.models import User
import urllib
from django.core.files import File
from django.views.decorators.cache import cache_control
from django.http import HttpResponseRedirect, HttpResponseNotFound
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from datetime import datetime
from datetime import timedelta
from django.utils import timezone
import datetime as dt
from django.utils import timezone
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
import pytz
from django.db.models.fields import BooleanField, DateField, FloatField, IntegerField, TextField
import string
# Create your views here.
TRENDING_NOVELS_PER_PAGE=8
NOVELS_PER_PAGE=2
NOVELS_IN_TOP_RATES=3
USERS_PER_PAGE=2
LOCK_OUT_TIME = 7 # (days)
TOP_FOLLOWED_NOVELS = 5
CHAPTERS_PER_ROW=6
NUMBER_ROW_LATEST_CHAPTERS=3
LATEST_CHAPTERS_PER_PAGE=CHAPTERS_PER_ROW*NUMBER_ROW_LATEST_CHAPTERS-1
LATEST_NOVELS_FULL=16
LATEST_COMMENTS_PER_PAGE=6

JSON_OK=JsonResponse({"ok":True})
JSON_ERROR=JsonResponse({"error":"error"})

ADMIN=1
AUTHOR=2
CUSTOMER=3

ROLE_CHOICES=[
    [AUTHOR,'author'],
    [CUSTOMER,'customer'],
]


def index(request):
    trending_novels=list(Novel.objects.filter().order_by('-publication_date')[:TRENDING_NOVELS_PER_PAGE])
    top_followed_novels = list(Novel.objects.annotate(count=Count("following",filter=(Q(following__is_followed=True)))).order_by('-count'))[:TOP_FOLLOWED_NOVELS]
    top_followed_novels_with_count = []
    for novel in top_followed_novels:
        top_followed_novels_with_count.append([novel,novel.following_set.filter(is_followed=True).count()])
    latest_chapters = list(Chapter.objects.all().order_by('-update_date')[:LATEST_CHAPTERS_PER_PAGE])
    latest_novels_full=list(Novel.objects.annotate(latest_update_date=Max("chapter__update_date")).filter(status=True).order_by("-latest_update_date"))
    print("# latest_novels_full : ",latest_novels_full)
    latest_novels_full_and_last_chapters=[]
    for novel in latest_novels_full:
        if novel.chapter_set.count()==0:
            continue
        latest_novels_full_and_last_chapters.append([novel,list(Chapter.objects.filter(novel=novel).order_by("-update_date"))[0]])
    recently_comments=list(Comment.objects.all().order_by('-publication_date')[:LATEST_COMMENTS_PER_PAGE])
    print("recently_comments : ",recently_comments)
    # print("# lastest chapter : ",latest_chapters)
    # page_number = request.GET.get('page')
    # if page_number is None:
    #     page_number=1
    # # print("page : ",page_number)
    # paginator = Paginator(novels, NOVELS_PER_PAGE)

    # try:
    #     page = paginator.page(page_number)
    # except PageNotAnInteger:
    #     # page = paginator.page(1)
    #     raise Http404
    # except EmptyPage:
    #     # page = paginator.page(paginator.num_pages)
    #     raise Http404

    # novels = page.object_list
    # page_obj = paginator.get_page(page_number)

    tags = list(Tag.objects.all())
    print(type(trending_novels))
    print("trending_novels : ",trending_novels)
    print("top_followed_novels : ",top_followed_novels)
    return render(request,"Ebook/index.html",{
        "trending_novels":trending_novels,
        "top_followed_novels_with_count":top_followed_novels_with_count,
        "tags":tags,
        "latest_chapters":latest_chapters,
        "latest_novels_full_and_last_chapters":latest_novels_full_and_last_chapters,
        "recently_comments":recently_comments,
        # "page_obj":page_obj,
    })

@authenticated_user
def home(request):
    return render(request,"Ebook/main.html",{"name":"home"})

@authenticated_user
@admin_only
def admin(request):
    return render(request,"Ebook/main.html",{"name":"admin"})

@unauthenticated_user
def loginPage(request):
    if request.method=="POST":
        username=request.POST.get("username")
        password=request.POST.get("password")
        user = User.objects.get(username=username)
        if not user.userinfo.is_locked_out():
            user.is_active = True
            user.save()
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request,user)
                return redirect('index')
            else:
                messages.info(request, 'Username OR password is incorrect')
        else:
            messages.info(request, 'Account is locked')
    context = {}
    return render(request, 'Ebook/login.html', context)

@unauthenticated_user
def registerPage(request):

    form1 = CreateUserForm()
    form2 = CreateUserInfoForm()
	
    if request.method == 'POST':
        form1 = CreateUserForm(request.POST)
        form2 = CreateUserInfoForm(request.POST)
        if form1.is_valid() and form2.is_valid():
            user = form1.save()
            info = form2.save()
            info.user = user # relationship one to one 
            info.save()
            username = form1.cleaned_data.get('username')
            messages.success(request, 'Account was created for ' + username)
            return redirect('login')
        else:
            print("form1 valid : ",form1.is_valid())
            print("form2 valid : ",form2.is_valid())
            print("form1 error : ",form1.errors) 
            print("form2 error : ",form2.errors) 

    context = {
        'formUser':form1,
        'formInfo':form2,
    }
    return render(request, 'Ebook/register.html', context)

def logoutUser(request):
	logout(request)
	return redirect('login')

def search(request):
    novels=[]
    keyword=request.GET.get("keyword")
    print("keyword : ",keyword)
    novels=list(Novel.objects.filter(title__contains=keyword))
    print(novels)
    page_number = request.GET.get('page')
    if page_number is None:
        page_number=1
    # print("page : ",page_number)
    paginator = Paginator(novels, NOVELS_PER_PAGE)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # page = paginator.page(1)
        raise Http404
    except EmptyPage:
        # page = paginator.page(paginator.num_pages)
        raise Http404

    novels = page.object_list
    page_obj = paginator.get_page(page_number)
    return render(request,"Ebook/search.html",{
        "novels":novels,
        "page_obj":page_obj,
    })

@authenticated_user
@author_or_admin
@author_check
def myWorkDetail(request,slug=None):
    novel = get_object_or_404(Novel,slug=slug)
    chapters = list(Chapter.objects.filter(novel=novel))
    return render(request,"Ebook/my_work_detail.html",{"chapters":chapters})

def read(request,slug=None,chapter_number=None):
    if slug is not None and chapter_number is not None:
        novel = get_object_or_404(Novel,slug=slug)
        # chapter_list = list(novel.chapter_set.all())
        cnt = novel.chapter_set.count()
        print("count : ",cnt)
        chapter = get_object_or_404(Chapter,novel=novel,number=chapter_number)
        if request.user.is_authenticated:
            user = User.objects.get(pk=request.user.pk)
            print("#user : ",user)
            print("#novel : ",novel)
            try:
                bookmark = Bookmark.objects.get(user=user,novel=novel)
            except Bookmark.DoesNotExist:
                bookmark = None
            if bookmark is None:
                bookmark=Bookmark()
                bookmark.user=user
                bookmark.novel=novel
            bookmark.number=chapter_number
            bookmark.save()
        return render(request,'Ebook/read.html',{
            "novel" : novel,
            "chapter" : chapter,
            "range" : range(1,cnt+1),
            "max_range" : cnt,
            "slug" : slug,
            "chapter_number" : chapter_number,
        })
    return redirect('index')

@never_cache
def detail(request,slug=None):
    if slug is not None:
        userinfo = None
        if request.user.is_authenticated:
            user = User.objects.get(pk=request.user.pk)
            userinfo = UserInfo.objects.get(user=user)
        novel = get_object_or_404(Novel,slug=slug)
        form = CreateRatingForm()
        tags = list(novel.tags.all())
        follow_number = Following.objects.filter(novel=novel,is_followed=True).count()
        ############ test
        # local_tz = pytz.timezone('Asia/Bangkok')
        # current = timezone.now().replace(tzinfo=pytz.utc).astimezone(local_tz)
        # userinfo_ban = userinfo.ban_time.replace(tzinfo=pytz.utc).astimezone(local_tz)
        # print("current day : ",current)
        # print("ban day : ",userinfo_ban)

        # is_banned = (current <= userinfo_ban)

        # print("is banned : ",is_banned)

        ############ endtest

        chapters = list(Chapter.objects.filter(novel=novel))
        if len(chapters)>0:
            first_chapter = chapters[0]
            if request.user.is_authenticated:
                user = User.objects.get(pk=request.user.pk)
                try:
                    bookmark = Bookmark.objects.get(user=user,novel=novel)
                except Bookmark.DoesNotExist:
                    bookmark = None
                if bookmark is not None:
                    first_chapter = chapters[bookmark.number-1]

        else:
            first_chapter = None
        comments = Comment.objects.filter(novel=novel).order_by("-publication_date")

        is_followed = False
        rating = None
        if request.user.is_authenticated:
            user = User.objects.get(pk=request.user.pk)
            try:
                following = Following.objects.get(user=user,novel=novel)
            except ObjectDoesNotExist:
                following = None
            if following is not None:
                is_followed = following.is_followed
            
            try:
                rating = Rating.objects.get(user=user,novel=novel)
            except ObjectDoesNotExist:
                rating = None
            if request.method == "POST" and not userinfo.is_banned():
                is_comment = request.POST.get("comment")
                if is_comment is not None:
                    content = request.POST.get("content")
                    comment = Comment()
                    comment.user = user
                    comment.novel = novel
                    comment.content = content
                    comment.save()
                    return redirect('detail',slug=slug)
        
        print("tags : ",tags)
        return render(request,'Ebook/detail.html',{
            "slug" : slug,
            "userinfo" : userinfo,
            "novel" : novel,
            "tags" : tags,
            "chapters" : chapters,
            "form": form,
            "is_followed" : is_followed,
            "comments" : comments,
            "first_chapter" : first_chapter,
            "rating" : rating,
            "follow_number" : follow_number,
        })
    return redirect('index')

@authenticated_user
@author_or_admin
def myWork(request, slug=None):
    user = User.objects.get(pk=request.user.pk)
    novels = list(Novel.objects.filter(userinfo=user.userinfo))
    print("novels : ",novels)
    return render(request,'Ebook/my_work.html',{"novels":novels})

@authenticated_user
@author_or_admin
def createNovel(request):
    form = CreateNovelForm()
    if request.method == "POST":
        print("inPOST_create_novel")
        form = CreateNovelForm(request.POST, request.FILES)
        if form.is_valid():
            # user= request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
            u=User.objects.get(pk=request.user.pk)
            userInfo=u.userinfo
            novel=form.save(commit=False)
            novel.publication_date=datetime.now()
            novel.save()
            novel.userinfo=userInfo
            novel.save()
            print(novel.tags.all())
        return redirect('login')
    context={
        "form":form,
    }
    print(form)
    return render(request, "Ebook/create_novel.html",context)


@authenticated_user
@author_or_admin
@author_check
def editNovel(request,slug=None):
    navCheck=request.GET.get("nav")
    if navCheck is not None and int(navCheck)==0:
        navCheck=False
    else:
        navCheck=True
    novel = get_object_or_404(Novel,slug=slug)
    if request.method=="POST":
        form = CreateNovelForm(data=request.POST, files=request.FILES,instance=novel)
        if form.is_valid():
            form.save()
    form = CreateNovelForm(instance=novel)
    return render(request, "Ebook/edit_novel.html",{
        "form":form,
        "slug":slug,
        "navCheck":navCheck,
    })


@authenticated_user
@author_or_admin
@cache_control(no_cache=True, must_revalidate=True)
def createChapter(request, slug=None):
    novel = get_object_or_404(Novel,slug=slug)
    form = CreateChapterForm()
    if request.method == "POST":
        form = CreateChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.novel = novel
            chapter.update_date=datetime.now()
            chapter.save()
            return redirect('my_work_detail',slug=slug)
    context={
        "form":form
    }
    return render(request,"Ebook/create_chapter.html",context)

@cache_control(no_cache=True, must_revalidate=True)
@authenticated_user
@author_or_admin
@author_check
def editChapter(request, slug=None, chapter_number=None):
    novel = get_object_or_404(Novel,slug=slug)
    # novel = Novel.objects.get(slug=slug)
    chapter = get_object_or_404(Chapter,novel=novel,number=chapter_number)
    # chapter = Chapter.objects.get(novel=novel,number=chapter_number)
    # form = CreateChapterForm()
    if request.method == "POST": 
        is_delete = request.POST.get("delete")
        if is_delete is not None: 
            chapter.delete()
            return redirect('my_work_detail',slug=slug)
        else:
            form = CreateChapterForm(request.POST,instance=chapter)
            if form.is_valid():
                chapter = form.save(commit=False)
                chapter.update_date=datetime.now()
                chapter.save()
                # return redirect('my_work_detail',slug=slug)
    
    # if slug is not None and chapter_number is not None:
        # novel = Novel.objects.get(slug=slug)
    form = CreateChapterForm(instance=chapter)
    context={
        "form":form
    }
    return render(request,"Ebook/edit_chapter.html",context)

@authenticated_user
@self_authenticate
def profile_details(request):
    # print('view profile')
    username = request.user.username
    user = User.objects.get(username=username)
    info = UserInfo.objects.get(user=user)
    if request.method == "POST": 
        form = CreateUserInfoForm(request.POST,instance=info)
        print(form.data)
        if form.is_valid():
            print('ok')
            form.save()
            return redirect('profile_details')
    
    form = CreateUserInfoForm(instance=info)
    print("hello profile")
    # print(form)
    context={
        "form":form
    }
    # print('view form')
    return render(request,"Ebook/profile_details.html",context)

@never_cache
@authenticated_user
def rate(request):
    if request.method == "POST":
        slug = request.POST.get("novel")
        novel = Novel.objects.get(slug=slug)
        if novel is not None:
            user = User.objects.get(pk=request.user.pk)
            print("#type : ",type(user))
            print("#name : ",user.userinfo.name)
            ratingForm = CreateRatingForm(request.POST)
            rating = ratingForm.save(commit=False)
            rating.novel = novel
            rating.user = user
            rating.save()

            prev_number=novel.number_rating
            sum_rate=prev_number*novel.avg_rate
            sum_rate+=1.0*rating.rate
            novel.number_rating+=1

            novel.avg_rate=sum_rate/novel.number_rating
            novel.save()

            return redirect('detail',slug=novel.slug)
    return redirect('index')

@authenticated_user
def profile_general(request):
    user = User.objects.get(pk=request.user.pk)
    userinfo = UserInfo.objects.get(user=user)
    return render(request,"Ebook/profile_general.html",{"userinfo":userinfo})


@authenticated_user
@csrf_exempt
def follow(request):
    if request.method == "POST" and request.is_ajax():
        print("in POST")
        slug = request.POST.get("slug")
        if slug is not None:
            novel = get_object_or_404(Novel,slug=slug)
            user = User.objects.get(pk=request.user.pk)
            try:
                following = Following.objects.get(user=user,novel=novel)
            except ObjectDoesNotExist:
                following = None
            
            if following is None:
                following = Following()
                following.user = user
                following.novel = novel
            following.is_followed = not following.is_followed
            following.save()
            return JsonResponse({"ok": True}, status=200)
            # return redirect('detail',slug=slug)
    return JsonResponse({"error": "invalid"}, status=400)

@authenticated_user
def profile_follow(request):
    user = User.objects.get(pk=request.user.pk)
    followings = list(Following.objects.filter(user=user,is_followed=True))
    bookmark_novels = []
    for following in followings:
        bookmark_novel=[]
        
        try:
            bookmark = Bookmark.objects.get(user=user,novel=following.novel)
        except Bookmark.DoesNotExist:
            bookmark = None

        bookmark_novel.append(bookmark)
        bookmark_novel.append(following.novel)
        bookmark_novels.append(bookmark_novel)
    print("#### bookmark_novels : ",bookmark_novels)
    return render(request,"Ebook/profile_follow.html",{"bookmark_novels":bookmark_novels})
    # return render(request,"Ebook/profile_follow.html")

@authenticated_user
def profile_change_pass(request):
    user = User.objects.get(pk=request.user.pk)
    print("current password : ",user.password)
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password1 = request.POST.get("new_password1")
        new_password2 = request.POST.get("new_password2")
        flag = user.check_password(old_password)
        print("flag : ",flag)
        if flag and new_password1==new_password2:
            user.set_password(new_password1)
            user.save()
            update_session_auth_hash(request,user)
            messages.success(request, ('Your password was successfully updated!'))
            return redirect('profile_change_pass')
        else:
            messages.error(request, ('Please correct the error below.'))
    return render(request,"Ebook/profile_change_pass.html")

def tag_list(request):
    tag_list = list(Tag.objects.all())
    context={"tag_list" : tag_list}
    return context

def top_rates_novel_list(request):
    novel_list = list(Novel.objects.order_by('-avg_rate'))[:NOVELS_IN_TOP_RATES]
    print(novel_list)
    context={"novel_list" : novel_list}
    return context

@authenticated_user
@admin_only
def manage(request):
    
    name = request.GET.get('name')
    if name is not None:
        userinfos=list(UserInfo.objects.filter(name__icontains=name).exclude(role=UserInfo.ADMIN))
    else:
        userinfos=list(UserInfo.objects.all().exclude(role=UserInfo.ADMIN))
    page_number = request.GET.get('page')
    if page_number is None:
        page_number=1
    # print("page : ",page_number)
    paginator = Paginator(userinfos, USERS_PER_PAGE)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # page = paginator.page(1)
        raise Http404
    except EmptyPage:
        # page = paginator.page(paginator.num_pages)
        raise Http404

    userinfos = page.object_list
    page_obj = paginator.get_page(page_number)
    return render(request,"Ebook/user_manage.html",{
        "userinfos" : userinfos,
        "page_obj" : page_obj,
        "ROLE_CHOICES" : ROLE_CHOICES,
    })

@authenticated_user
@admin_only
def ban(request):
    # print("date : ",datetime.now())
    # date_after = datetime.now() + timedelta(days=5)
    # print("date after : ",date_after)
    print("in ban")
    if request.method == "POST":
        print("in ban POST method")
        username = request.POST.get("username")
        if username is not None:
            user = User.objects.get(username = username)
            userinfo = UserInfo.objects.get(user = user)
            print("# name : ",userinfo.name)
            prev_ban_level = userinfo.prev_ban_level
            print("# prev_level : ",prev_ban_level)
            if prev_ban_level==0:
                userinfo.prev_ban_level=1
                current_date = datetime.now()
                ban_to = current_date + timedelta(days=userinfo.prev_ban_level)

                userinfo.ban_time = ban_to
                userinfo.save()
                print("save userinfo")
            else:
                if userinfo.ban_time is not None:
                    delta = datetime.now().date() - userinfo.ban_time.date()
                    print("# delta : ",delta.total_seconds())
                    if not userinfo.is_banned():
                        if delta.days <= userinfo.prev_ban_level*2:
                            userinfo.prev_ban_level*=2
                            userinfo.ban_time = datetime.now() + timedelta(days=userinfo.prev_ban_level)
                            userinfo.save()
                        else:
                            userinfo.prev_ban_level=1
                            current_date = datetime.now()
                            ban_to = current_date + timedelta(days=userinfo.prev_ban_level)
                            userinfo.ban_time = ban_to
                            userinfo.save()
    return redirect('user_manage')

@authenticated_user
@admin_only
def lock_out(request):
    print("in lock out")
    if request.method == "POST":
        username = request.POST.get("username")
        if username is not None:
            user = User.objects.get(username = username)
            userinfo = UserInfo.objects.get(user = user)
            lock_out_time = userinfo.lock_out_time
            userinfo.lock_out_time = datetime.now()
            userinfo.lock_out_time += timedelta(days=LOCK_OUT_TIME)
            userinfo.save()
            user.is_active = False
            user.save()
    return redirect('user_manage')

def about_us(request):
    return render(request,"Ebook/about_us.html")

def novelList(request, first_letter = None):
    
    order = request.GET.get("sapxep")
    ongoing = request.GET.get("dangtienhanh")
    complete = request.GET.get("hoanthanh")
    
    # print(order)
    if not (order or ongoing or complete):
        order = 'tentruyen'
        ongoing = 1
        complete = 1
        
    tag_list = [tag['slug'] for tag in Tag.objects.all().values('slug')]
    if first_letter == None:
        novels = Novel.objects.all()
    elif first_letter in tag_list:
        tag = Tag.objects.get(slug=first_letter)
        novels = tag.novel_set.all()
    elif first_letter == 'khac':
        novels = Novel.objects.filter(title__regex='^[^a-zA-Z]')
    elif first_letter in string.ascii_uppercase:
        novels = Novel.objects.filter(title__startswith=first_letter)
    else:
        novels = Novel.objects.all()
        
    if ongoing == '1' and complete == None:
        novels = novels.filter(status=0)
    elif ongoing == None and complete == '1':
        novels = novels.filter(status=1)
        
    novels = novels.annotate(follow=Count("following",filter=Q(following__is_followed=True)))
    novels = novels.annotate(update_date=Max("chapter__update_date"))
    # latest_chapter = Chapter.objects.filter(novel__id=OuterRef('id')).order_by('-update_date')[:1]
    # novels = novels.annotate(latest_chapter = Subquery(latest_chapter.values('chapter')))
    
    if order == 'tentruyen':
        novels = novels.order_by("title")
    elif order == 'tentruyenza':
        novels = novels.order_by("-title")
    elif order == 'capnhat':
        novels = novels.order_by("-update_date")
    elif order == 'truyenmoi':
        novels = novels.order_by("-publication_date")
    elif order == 'theodoi':
        novels = novels.order_by('-follow')
    elif order == 'top':
        novels = novels.order_by("-views")
        
    novel_chapter = []
    for novel in novels:
        novel_chapter.append([novel, list(Chapter.objects.filter(novel=novel).order_by("-number"))[0]])
    
    page_number = request.GET.get('page')
    if page_number is None:
        page_number=1
    paginator = Paginator(novel_chapter, NOVELS_PER_PAGE)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # page = paginator.page(1)
        raise Http404
    except EmptyPage:
        # page = paginator.page(paginator.num_pages)
        raise Http404
    # print(novel_chapter)
    
    novels = page.object_list
    page_obj = paginator.get_page(page_number)
    
    return render(request,"Ebook/novel_list.html",{
        'novels':novels,
        'first_letter':first_letter,
        'ongoing':ongoing,
        'complete':complete,
        'order':order,
        'page_obj':page_obj,
        })
    
def search_tag(request, slug=None):
    novels=[]
    tag = Tag.objects.get(slug=slug)
    print("tag : ",tag)
    novels = list(tag.novel_set.all())
    print("novels : ",novels)
    page_number = request.GET.get('page')
    if page_number is None:
        page_number=1
    # print("page : ",page_number)
    paginator = Paginator(novels, NOVELS_PER_PAGE)

    try:
        page = paginator.page(page_number)
    except PageNotAnInteger:
        # page = paginator.page(1)
        raise Http404
    except EmptyPage:
        # page = paginator.page(paginator.num_pages)
        raise Http404

    novels = page.object_list
    page_obj = paginator.get_page(page_number)
    return render(request,"Ebook/search.html",{
        "novels":novels,
        "page_obj":page_obj,
        "tag" : tag,
    })
    
@csrf_exempt
def increase_views(request):
    print("welcome")
    if request.method == "POST" and request.is_ajax():
        print("hello increase views")
        slug = request.POST.get("slug")
        chapter_number = request.POST.get("chapter_number")
        print("slug : ",slug)
        print("chapter_number : ",chapter_number)
        if slug is not None and chapter_number is not None:
            try:
                novel = Novel.objects.get(slug=slug)
            except Novel.DoesNotExist:
                novel = None
            if novel is not None:
                try:
                    chapter = Chapter.objects.get(novel=novel,number=chapter_number)
                except Chapter.DoesNotExist:
                    chapter = None
                if chapter is not None:
                    novel.views+=1
                    chapter.views+=1
                    novel.save()
                    chapter.save()
                    print("### increase view : done")
                    return JsonResponse({"ok": True}, status=200)
    return JsonResponse({"error": "invalid"}, status=400)
        
        
def base(request):
    return render(request,'Ebook/base.html')

@csrf_exempt
def postComment(request):
    if request.method == "POST" and request.is_ajax():
        print("## in post comment")
        slug = request.POST.get("slug")
        print("## slug in comment : ",slug)
        if slug is not None:
            try:
                novel = Novel.objects.get(slug=slug)
            except Novel.DoesNotExist:
                novel = None
            if novel is not None:
                user = User.objects.get(pk=request.user.pk)
                content = request.POST.get("content")
                print("## content : ",content)
                comment = Comment()
                comment.publication_date=datetime.now()
                comment.user=user
                comment.novel=novel
                comment.content=content
                comment.save()
                return JsonResponse({"ok": True}, status=200)
    return JsonResponse({"error": "invalid"}, status=400)

@never_cache
@authenticated_user
def nRate(request):
    if request.method == "POST" and request.is_ajax():
        slug = request.POST.get("slug")
        novel = Novel.objects.get(slug=slug)
        if novel is not None:
            user = User.objects.get(pk=request.user.pk)
            print("#type : ",type(user))
            print("#name : ",user.userinfo.name)
            rate = int(request.POST.get("rate"))
            print("rate : ",rate)
            rating = Rating()
            rating.rate=rate
            rating.novel = novel
            rating.user = user
            rating.save()

            prev_number=novel.number_rating
            sum_rate=prev_number*novel.avg_rate
            sum_rate+=1.0*rating.rate
            novel.number_rating+=1

            novel.avg_rate=sum_rate/novel.number_rating
            novel.save()

            return JsonResponse({"ok": True}, status=200)
    return JsonResponse({"error": "invalid"}, status=400)

def advancedSearch(request):

    tags=list(Tag.objects.all())

    ret=Novel.objects

    found=False

    title=request.GET.get("title")
    if title is not None:
        ret=ret.filter(title__icontains=title)
        found=True

    # print("after search : ",list(ret))

    status=request.GET.get("status")
    if status is not None:
        status=int(status)
        if status!=0:
            if status==1:
                status=False
            if status==2:
                status=True

            ret=ret.filter(status=status)
        found=True

    author=request.GET.get("author")
    if author is not None:
        ret=ret.filter(userinfo__name__icontains=author)
        found=True

    filter_tags_slug=request.GET.get("tags")

    if filter_tags_slug is not None:
        if filter_tags_slug != "":
            filter_tags_slug=filter_tags_slug.split(",")
            # print("all tags : ",filter_tags_slug)
            if len(filter_tags_slug)!=0:
                for tag_slug in filter_tags_slug:
                    ret=ret.filter(tags=Tag.objects.get(slug=tag_slug))
        found=True
    
    reject_tags_slug=request.GET.get("rejecttags")
    print("#reject_tags_slug : ",reject_tags_slug)
    if reject_tags_slug is not None:
        if reject_tags_slug != "":
            reject_tags_slug=reject_tags_slug.split(",")
            if len(filter_tags_slug)!=0:
                for tag_slug in reject_tags_slug:
                    ret=ret.exclude(tags=Tag.objects.get(slug=tag_slug))
        found=True

    # print("advanced search : ",list(ret))
    dict={}
    cnt=0
    if not found:
        ret=[]

    novels_and_last_chapters=[]
    for novel in ret:
        if novel.chapter_set.count()==0:
            continue
        novels_and_last_chapters.append([novel,list(Chapter.objects.filter(novel=novel).order_by("-number"))[0]])

    for novel in ret:
        dict[cnt]=novel.slug
        cnt+=1
    return render(request,"Ebook/advanced_search.html",{
        "novels_and_last_chapters" : novels_and_last_chapters,
        "tags" : tags,
    })

def action(request):
    novels_number=Novel.objects.all().count()
    chapters_number=Chapter.objects.all().count()
    return render(request,'Ebook/action.html',{
        "novels_number" : novels_number,
        "chapters_number" : chapters_number,
    })
def tagsList(request):
    tags = list(Tag.objects.all())
    return render(request,'Ebook/tags_list.html',{
        "tags" : tags,
    })

@authenticated_user
@author_or_admin
def manageList(request):
    user = User.objects.get(pk=request.user.pk)
    userinfo = UserInfo.objects.get(user=user)
    novels = Novel.objects.filter(userinfo=userinfo)
    keywords=request.GET.get("keywords")
    if keywords is not None:
        print("have keywords : ",keywords)
        novels=novels.filter(title__icontains=keywords)
    return render(request,'Ebook/manage_list.html',{
        "novels" : novels,
        "userinfo" : userinfo,
    })

@authenticated_user
@author_or_admin
def deleteNovel(request):
    print("in delete novel 1")
    if request.method=="POST" and request.is_ajax():
        print("in delete novel 2")
        slug = request.POST.get("slug")
        print("# delete novel ",slug)
        if slug is not None:
            try:
                novel = Novel.objects.get(slug=slug)
            except Novel.DoesNotExist:
                novel = None
            if novel is not None:
                user = User.objects.get(pk=request.user.pk)
                if user.userinfo==novel.userinfo:
                    novel.delete()
                    return JsonResponse({"ok":True})
    return JsonResponse({"error":"something wrong"})
        
def manageNovel(request,slug=None):
    if slug is not None:
        novel=get_object_or_404(Novel,slug=slug)
        return render(request,"Ebook/manage.html",{
            "novel" : novel,
        })
    return HttpResponseNotFound('<h1>Page not found</h1>')

def navbarNovel(request,slug):
    if slug is not None:
        novel=get_object_or_404(Novel,slug=slug)
        chapters = Chapter.objects.filter(novel=novel).order_by("number")
        return render(request,"Ebook/nav_novel.html",{
            "novel" : novel,
            "chapters" : chapters,
            "slug" : slug,
        })
    return HttpResponseNotFound('<h1>Page not found</h1>')

@authenticated_user
@author_or_admin
def deleteChapter(request,slug=None,chapter_number=None):
    if slug is not None and chapter_number is not None:
        try:
            novel = Novel.objects.get(slug=slug)
        except Novel.DoesNotExist:
            novel = None
        if novel is not None:
            try:
                chapter = Chapter.objects.get(novel=novel,number=chapter_number)
            except Chapter.DoesNotExist:
                chapter = None
            if chapter is not None:
                user = User.objects.get(pk=request.user.pk)
                if user.userinfo==novel.userinfo:
                    chapter.delete()
    return redirect('edit_novel',slug=slug)

@authenticated_user
@admin_only
def unBanComment(request):
    print("welcome unban")
    if request.method == "POST" and request.is_ajax():
        username = request.POST.get("username")
        print("username : ",username)
        if username is not None:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None
            if user is not None:
                try:
                    userinfo = UserInfo.objects.get(user=user)
                except UserInfo.DoesNotExist:
                    userinfo = None
                if userinfo is not None:
                    userinfo.ban_time = None
                    userinfo.prev_ban_level = 0
                    userinfo.save()
                    return JSON_OK
    return JSON_ERROR

@authenticated_user
@admin_only
def unLockout(request):
    if request.method == "POST" and request.is_ajax():
        username = request.POST.get("username")
        print("username : ",username)
        if username is not None:
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None
            if user is not None:
                try:
                    userinfo = UserInfo.objects.get(user=user)
                except UserInfo.DoesNotExist:
                    userinfo = None
                if userinfo is not None:
                    userinfo.lock_out_time = None
                    userinfo.save()
                    return JSON_OK
    return JSON_ERROR

@authenticated_user
@admin_only
def modifyRole(request):
    if request.method == "POST" and request.is_ajax():
        username = request.POST.get("username")
        role = request.POST.get("role")
        if username is not None and role is not None:
            print("username : ",username)
            print("role : ",role)
            try:
                user = User.objects.get(username=username)
            except User.DoesNotExist:
                user = None
            if user is not None:
                userinfo = UserInfo.objects.get(user=user)
                userinfo.role = role
                userinfo.save()
                return JSON_OK
    return JSON_ERROR