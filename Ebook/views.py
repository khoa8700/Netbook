from traceback import format_exception
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
import re
# Create your views here.
TRENDING_NOVELS_PER_PAGE=8
NOVELS_PER_PAGE=12
COMMENTS_PER_PAGE=5
NOVELS_IN_TOP_RATES=3
USERS_PER_PAGE=5
LOCK_OUT_TIME = 7 # (days)
TOP_FOLLOWED_NOVELS = 5
CHAPTERS_PER_ROW=6
NUMBER_ROW_LATEST_CHAPTERS=3
LATEST_CHAPTERS_PER_PAGE=CHAPTERS_PER_ROW*NUMBER_ROW_LATEST_CHAPTERS
LATEST_FINISHED_NOVELS= 10
LATEST_COMMENTS=6

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
    trending_novels=list(Novel.objects.filter().order_by('-views')[:TRENDING_NOVELS_PER_PAGE])
    top_followed_novels = list(Novel.objects.annotate(follow=Count("following",filter=(Q(following__is_followed=True)))).order_by('-follow'))[:TOP_FOLLOWED_NOVELS]
    # top_followed_novels_with_count = []
    # for novel in top_followed_novels:
    #     top_followed_novels_with_count.append([novel,novel.following_set.filter(is_followed=True).count()])
    latest_chapters_novels = list(Novel.objects.all().annotate(update_date=Max("chapter__update_date")).order_by('-update_date'))
    latest_chapters_novels_chapter = []
    for novel in latest_chapters_novels:
        if novel.chapter_set.count() > 0:
            latest_chapters_novels_chapter.append(list(Chapter.objects.filter(novel=novel).order_by("-update_date"))[0])
    latest_chapters_novels_chapter = latest_chapters_novels_chapter[:LATEST_CHAPTERS_PER_PAGE]
    # print("# latest_novels_full : ",latest_chapters_novels_chapter)
    
    latest_finished_novels=list(Novel.objects.filter(status=True).annotate(update_date=Max("chapter__update_date")).order_by("-update_date"))
    latest_finished_novels_chapter=[]
    for novel in latest_finished_novels:
        if novel.chapter_set.count() > 0:
            latest_finished_novels_chapter.append(list(Chapter.objects.filter(novel=novel).order_by("-update_date"))[0])
    latest_finished_novels_chapter = latest_finished_novels_chapter[:LATEST_FINISHED_NOVELS]
    
    recently_comments=list(Comment.objects.all().order_by('-publication_date')[:LATEST_COMMENTS])
    # print("recently_comments : ",recently_comments)
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
    # print(type(trending_novels))
    # print("trending_novels : ",trending_novels)
    # print("top_followed_novels : ",top_followed_novels)
    return render(request,"Ebook/index.html",{
        "trending_novels":trending_novels,
        "top_followed_novels":top_followed_novels,
        # "tags":tags,
        "latest_chapters":latest_chapters_novels_chapter,
        "latest_finished_novels":latest_finished_novels_chapter,
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
        
        user = authenticate(request, username=username, password=password)
        if not user:
            try:
                userinfo = UserInfo.objects.get(email=username)
                user = authenticate(request, username=userinfo.user, password=password)
            except:
                pass
        if user is not None:
            if not user.userinfo.is_locked_out():
                user.is_active = True
                user.save()
                login(request,user)
                return redirect('index')
            else:
                messages.info(request, 'Tài khoản của bạn đã bị khoá')
        else:
            messages.info(request, 'Tên đăng nhập hoặc mật khẩu không đúng')
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
            user = form1.save(commit=False)
            info = form2.save(commit=False)
            regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            try:
                userinfo = UserInfo.objects.get(email=info.email)
            except:
                userinfo = None
            havemessage = False
            mess = '<ul class="errorlist"><li>email<ul class="errorlist">'
            if userinfo:
                # print('2')
                havemessage = True
                mess += '<li>A user with that email already exists.</li>'
            if not re.fullmatch(regex, info.email):
                # print('3')
                havemessage = True
                mess += '<li>Wrong email format.</li>'
            mess += '</ul></ul>'
            if havemessage:
                messages.info(request, mess)
            if re.fullmatch(regex, info.email) and not userinfo:
                info.user = user # relationship one to one 
                user.save()
                info.save()
            # username = form1.cleaned_data.get('username')
                login(request,user)
                return redirect('index')
        else:
            # print("form1 valid : ",form1.is_valid())
            # print("form2 valid : ",form2.is_valid())
            print("form1 error : ",type(form1.errors)) 
            # print("form2 error : ",form2.errors) 
            messages.info(request, form1.errors)

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

@authenticated_user
def bookmark(request):
    if request.method == "POST" and request.accepts('ajax'):
        print("hello bookmark")
        slug = request.POST.get("slug")
        chapter_number = request.POST.get("chapter_number")
        # print("slug : ",slug)
        # print("chapter_number : ",chapter_number)
        novel = Novel.objects.get(slug=slug)
        user = request.user
        try:
            bookmark = Bookmark.objects.get(novel=novel,user=user,number=chapter_number)
        except:
            bookmark = None
        if not bookmark:
            print('k co bookmark')
            bookmark=Bookmark(user=user,novel=novel,number=chapter_number)
            bookmark.save()
        return JsonResponse({"ok": True}, status=200)
    return JsonResponse({"error": "invalid"}, status=400)

@authenticated_user
def usermarkread(request):
    if request.method == "POST":
        novels_id = request.POST.get('series_id').split(',')
        user = request.user
        for id in novels_id:
            novel = Novel.objects.get(id=id)
            for chapter_number in range(1,novel.chapter_set.count()+1):
                try:
                    bookmark = Bookmark.objects.get(novel=novel,user=user,number=chapter_number)
                except:
                    bookmark = None
                if not bookmark:
                    # print('k co bookmark')
                    bookmark=Bookmark(user=user,novel=novel,number=chapter_number)
                    bookmark.save()
        return JsonResponse({"status": 'success'}, status=200)
        # print(novels_id)
    return JsonResponse({"error": "invalid"}, status=400)

def read(request,slug=None,chapter_number=None):
    if slug is not None and chapter_number is not None:
        novel = get_object_or_404(Novel,slug=slug)
        # chapter_list = list(novel.chapter_set.all())
        cnt = novel.chapter_set.count()
        print("count : ",cnt)
        chapter = get_object_or_404(Chapter,novel=novel,number=chapter_number)
        # if request.user.is_authenticated:
        #     user = User.objects.get(pk=request.user.pk)
        #     print("#user : ",user)
        #     print("#novel : ",novel)
        #     try:
        #         bookmark = Bookmark.objects.get(user=user,novel=novel)
        #     except Bookmark.DoesNotExist:
        #         bookmark = None
        #     if bookmark is None:
        #         bookmark=Bookmark()
        #         bookmark.user=user
        #         bookmark.novel=novel
        #     bookmark.number=chapter_number
        #     bookmark.save()
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
        novel = get_object_or_404(Novel,slug=slug)
        novel = Novel.objects.annotate(update_date=Max('chapter__update_date')).get(slug=slug)
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
        chapters_mark = []
        if request.user.is_authenticated:
            user = User.objects.get(pk=request.user.pk)
            for chapter in chapters:
                try:
                    bookmark = Bookmark.objects.get(user=user,novel=novel,number=chapter.number)
                except Bookmark.DoesNotExist:
                    bookmark = None
                mark = False
                if bookmark is not None:
                    mark = True
                chapters_mark.append([chapter,mark])

        else:
            chapters_mark = [[chapter,False] for chapter in chapters]
        # if len(chapters)>0:
        #     first_chapter = chapters[0]
        #     if request.user.is_authenticated:
        #         user = User.objects.get(pk=request.user.pk)
        #         try:
        #             bookmark = Bookmark.objects.get(user=user,novel=novel)
        #         except Bookmark.DoesNotExist:
        #             bookmark = None
        #         if bookmark is not None:
        #             first_chapter = chapters[bookmark.number-1]
        # else:
        #     first_chapter = None
        comments = Comment.objects.filter(novel=novel).order_by("-publication_date")
        paginator = Paginator(comments, COMMENTS_PER_PAGE)
        page_number = request.GET.get('page')
        if not page_number:
            page_number = 1
        try:
            page = paginator.page(page_number)
        except:
            # page = paginator.page(paginator.num_pages)
            raise Http404

        comments = page.object_list
        print(page, comments)
        page_obj = paginator.get_page(page_number)
        
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
            # "userinfo" : userinfo,
            "novel" : novel,
            "tags" : tags,
            "chapters_mark" : chapters_mark,
            "form": form,
            "is_followed" : is_followed,
            "comments" : comments,
            # "first_chapter" : first_chapter,
            "rating" : rating,
            "follow_number" : follow_number,
            "page_obj":page_obj,
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
        print(form.data)
        print(form.errors)
        if form.is_valid():
            # user= request.user._wrapped if hasattr(request.user,'_wrapped') else request.user
            u=User.objects.get(pk=request.user.pk)
            userInfo=u.userinfo
            novel=form.save()
            novel.publication_date=datetime.now()
            novel.userinfo=userInfo
            novel.save()
            print("after tags : ",novel.tags.all())
        return redirect('manage_list')
    context={
        "form":form,
    }
    print(format_exception)
    return render(request, "Ebook/create_novel.html",context)


@authenticated_user
@author_or_admin
@author_check
def editNovel(request,id_novel=None):
    navCheck=request.GET.get("navbar")
    # if navCheck is not None and int(navCheck)==0:
    #     navCheck=False
    # else:
    #     navCheck=True
    novel = get_object_or_404(Novel,id=id_novel)
    if request.method=="POST":
        form = CreateNovelForm(data=request.POST, files=request.FILES,instance=novel)
        if form.is_valid():
            form.save()
    form = CreateNovelForm(instance=novel)
    return render(request, "Ebook/edit_novel.html",{
        "form":form,
        "navCheck":navCheck,
    })


@authenticated_user
@author_or_admin
@cache_control(no_cache=True, must_revalidate=True)
def createChapter(request, id_novel):
    novel = get_object_or_404(Novel,id=id_novel)
    form = CreateChapterForm()
    if request.method == "POST":
        form = CreateChapterForm(request.POST)
        if form.is_valid():
            chapter = form.save(commit=False)
            chapter.novel = novel
            chapter.update_date=datetime.now()
            chapter.save()
            # return redirect('my_work_detail',slug=slug)
    context={
        "form":form
    }
    return render(request,"Ebook/create_chapter.html",context)

@cache_control(no_cache=True, must_revalidate=True)
@authenticated_user
@author_or_admin
@author_check
def editChapter(request, id_novel=None, id_chapter=None):
    novel = get_object_or_404(Novel, id=id_novel)
    # novel = Novel.objects.get(slug=slug)
    chapter = get_object_or_404(Chapter,novel=novel,id=id_chapter)
    # chapter = Chapter.objects.get(novel=novel,number=chapter_number)
    # form = CreateChapterForm()
    if request.method == "POST": 
        # is_delete = request.POST.get("delete")
        # if is_delete is not None: 
        #     chapter.delete()
        #     return redirect('my_work_detail',slug=slug)
        # else:
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
        form = CreateUserInfoForm(data=request.POST, files=request.FILES,instance=info)
        print(form.data)
        print(form.errors)
        if form.is_valid():
            print('ok')
            form.save()
            return redirect('profile_details')
        else:
            print('error')
    
    form = CreateUserInfoForm(instance=info)
    # print("hello profile")
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
def profile(request,id):
    user = User.objects.get(id=id)
    userinfo = UserInfo.objects.get(user=user)
    follow = Following.objects.filter(user=user,is_followed=True).count()
    novels = userinfo.novel_set.all().annotate(update_date=Max('chapter__update_date'))
    nchapter = 0
    for novel in novels:
        nchapter += novel.chapter_set.count()
    print(follow)
    return render(request,"Ebook/profile.html",{
        "userinfo":userinfo,
        "nfollow":follow,
        "novels":novels,
        "nchapter":nchapter
        }
    )


@authenticated_user
@csrf_exempt
def follow(request):
    if request.method == "POST" and request.accepts('ajax'):
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
            n_bookmark = Bookmark.objects.filter(user=user,novel=following.novel).count()
            print(bookmark)
        except Bookmark.DoesNotExist:
            n_bookmark = 0
        n_unread = following.novel.chapter_set.count()-n_bookmark
        latest_chapter = Chapter.objects.get(novel=following.novel,number=following.novel.chapter_set.count())
        bookmark_novel.append(n_unread)
        bookmark_novel.append(latest_chapter)
        bookmark_novels.append(bookmark_novel)
    # print("#### bookmark_novels : ",bookmark_novels)
    return render(request,"Ebook/favourite.html",{"bookmark_novels":bookmark_novels})
    # return render(request,"Ebook/profile_follow.html")

def introduce(request):
    return render(request,"Ebook/introduce.html")
@authenticated_user
def updatePassword(request):
    user = User.objects.get(pk=request.user.pk)
    print("current password : ",user.password)
    if request.method == "POST":
        oldpassword = request.POST.get("oldpassword")
        newpassword = request.POST.get("newpassword")
        newpassword_confirmation = request.POST.get("newpassword_confirmation")
        checkoldpass = user.check_password(oldpassword)
        messages = []
        if not checkoldpass:
            return render(request,"Ebook/update_password.html",context={'message':"Mật khẩu cũ không đúng"})
        if newpassword != newpassword_confirmation:
            return render(request,"Ebook/update_password.html",context={'message':"Xác nhận mật khẩu không đúng"})
        if len(newpassword) < 8:
            return render(request,"Ebook/update_password.html",context={'message':"Độ dài mật khẩu mới nhỏ hơn 8 ký tự"})
        user.set_password(newpassword)
        user.save()
        update_session_auth_hash(request,user)
        # messages.success(request, ('Your password was successfully updated!'))
        logout(request)
        return redirect('login')
        # return redirect('update_password')
    return render(request,"Ebook/update_password.html")

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
        if novel.chapter_set.count() > 0:
            novel_chapter.append([novel, list(Chapter.objects.filter(novel=novel).order_by("-number"))[0]])
            # chapter = list(Chapter.objects.filter(novel=novel).order_by("-number"))
        # if len(chapter) > 0:
    
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
    if request.method == "POST" and request.accepts('ajax'):
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
    if request.method == "POST" and request.accepts('ajax'):
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
    if request.method == "POST" and request.accepts('ajax'):
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
    print(title)
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
    if request.method=="POST" and request.accepts('ajax'):
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

@authenticated_user
@author_or_admin
def deleteChapter(request, id_novel=None, id_chapter=None):
    print("in delete chapter")
    try:
        print(id_novel,id_chapter)
        novel = Novel.objects.get(id=id_novel)
        print(novel)
        user = User.objects.get(pk=request.user.pk)
        if user.userinfo==novel.userinfo:
            chapter = Chapter.objects.get(novel=novel,id=id_chapter)
            bookmark = Bookmark.objects.filter(novel=novel,number=chapter.number)
            bookmark.delete()
            chapter.delete()
    except:
        return JsonResponse({"error":"something wrong"})
    print('delete')
    return redirect('edit_novel', id_novel=id_novel)

# @authenticated_user
# @author_or_admin
# def deleteChapter(request,slug=None,chapter_number=None):
#     if slug is not None and chapter_number is not None:
#         try:
#             novel = Novel.objects.get(slug=slug)
#         except Novel.DoesNotExist:
#             novel = None
#         if novel is not None:
#             try:
#                 chapter = Chapter.objects.get(novel=novel,number=chapter_number)
#             except Chapter.DoesNotExist:
#                 chapter = None
#             if chapter is not None:
#                 user = User.objects.get(pk=request.user.pk)
#                 if user.userinfo==novel.userinfo:
#                     chapter.delete()
#     return redirect('edit_novel',slug=slug)
    
def manageNovel(request,id_novel):
    # if slug is not None:
    novel=get_object_or_404(Novel,id=id_novel)
    return render(request,"Ebook/manage.html",{
        "novel" : novel,
    })
    # return HttpResponseNotFound('<h1>Page not found</h1>')

def navbarNovel(request, id_novel):
    # if slug is not None:
        novel=get_object_or_404(Novel,id=id_novel)
        chapters = Chapter.objects.filter(novel=novel).order_by("number")
        return render(request,"Ebook/nav_novel.html",{
            "novel" : novel,
            "chapters" : chapters,
        })
    # return HttpResponseNotFound('<h1>Page not found</h1>')


def noti(request):
    noti = 0
    print('hello')
    if request.user.is_authenticated:
        print('ok')
        user = User.objects.get(pk=request.user.pk)
        followings = list(Following.objects.filter(user=user,is_followed=True))
        for following in followings:
            try:
                n_bookmark = Bookmark.objects.filter(user=user,novel=following.novel).count()
            except Bookmark.DoesNotExist:
                n_bookmark = 0

            noti += following.novel.chapter_set.count() - n_bookmark
        print('noti',noti)
        return { 
            "noti" : noti,
        }
    return { 
        "noti" : noti,
    }


@authenticated_user
@admin_only
def unBanComment(request):
    print("welcome unban")
    if request.method == "POST" and request.accepts('ajax'):
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
    if request.method == "POST" and request.accepts('ajax'):
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
    if request.method == "POST" and request.accepts('ajax'):
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
