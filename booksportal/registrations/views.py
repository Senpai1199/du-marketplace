from django.shortcuts import render, redirect, reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger

from registrations.permissions import has_profile_completed

import re

from itertools import chain

from registrations.models import Book, Course, UserProfile, BookSet, College

@login_required(login_url='login')
@has_profile_completed
def index(request):
    """
        Redirect '/' to 'home/'
    """
    return redirect('home')

@login_required(login_url='login')
def base_view(request):
    return render(request,'registrations/base.html', context={})

@login_required(login_url='login')
@has_profile_completed
def home(request):
    """
        The HOME page of the portal where all the book listings would be displayed according to the year of the logged in user
    """
    try:
        profile = UserProfile.objects.get(auth_user=request.user)
    except UserProfile.DoesNotExist:
        messages.error(request, "Please complete your profile first.")
        return redirect('complete_profile')
    books1 = Book.objects.filter(semester=request.user.profile.semester, sold=False,
        bookset=None).exclude(seller=request.user.profile)
    books2 = Book.objects.filter(bookset=None, sold=False).exclude(semester=request.user.profile.semester).exclude(seller=request.user.profile) #This needs to be changed
    books = list(chain(books1, books2))
    context = {
        "books": books[:10]
    }
    return render(request, 'registrations/home.html', context=context)

@csrf_exempt
def sign_up(request):
    """
        Allows users to register on DUBS
    """
    if request.user.is_authenticated:
        try:
            profile = UserProfile.objects.get(auth_user=request.user)
            return redirect('home')
        except UserProfile.DoesNotExist:
            messages.warning(request, "Please complete your profile first!")
            return redirect('complete_profile')

    context = {
        "courses": Course.objects.all(),
        "colleges": College.objects.all()
    }

    if request.method == "GET":
        return render(request, 'registrations/sign_up.html', context)

    elif request.method == "POST":
        data = request.POST
        try:
            first_name = str(data["first_name"])
            email = str(data["email"])
            password = str(data["password"])
            confirm_pass = str(data["confirm_pass"])
            gender = str(data["gender"])
            college_name = str(data["college_name"])
            course_name = str(data["course_name"])
            semester = data["semester"]

            try:
                email = email.strip()
                existing_user = User.objects.get(email=email)
                messages.warning(request, "This email is already registered")
                try:
                    return redirect(request.META.get('HTTP_REFERER'))
                except:
                    return render(request, 'registrations/sign_up.html', context)
            except User.DoesNotExist:
                pass

            if not re.match(r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)", email):
                messages.warning(request, "Invalid email")
                return render(request, 'registrations/sign_up.html', context)

            password = password.strip()
            confirm_pass = confirm_pass.strip()
            if password != confirm_pass:
                messages.error(request, "Passwords don't match")
                return render(request, 'registrations/sign_up.html', context)

            try:
                course = Course.objects.get(name=course_name)
            except Course.DoesNotExist:
                messages.error(request, "Course selected must be from the list only.")
                return render(request, 'registrations/sign_up.html', context)

            try:
                college = College.objects.get(name=college_name)
            except College.DoesNotExist:
                messages.error(request, "College selected must be from the list only.")
                return render(request, 'registrations/sign_up.html', context)
            
            if semester == "Masters":
                semester = 7

            first_name = first_name.strip()
            last_name = str(data["last_name"].strip()) # received here because lname is optional
            user = User.objects.create(username=email)
            user.set_password(password)
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.save()

            user_prof = UserProfile.objects.create(
                    auth_user = user,
                    gender = gender,
                    course = course,
                    college = college,
                    semester = semester
                )

            try:
                profile_pic = request.FILES["file"]
                user_prof.image = profile_pic
                user_prof.save()
            except KeyError: # setting default dp
                print("*** PIC NOT FOUND ****")
                img_path = '../media/default_male_dp.png'
                if gender == "F":
                    img_path = '../media/default_female_dp.png'
                elif gender == "O":
                    img_path = "../media/default_neutral_dp.jpg"
                user_prof.image = img_path
                user_prof.save()

            messages.success(request, "Registered Successfully!")
            login(request, user, backend='django.contrib.auth.backends.ModelBackend')
            return redirect('home')

        except KeyError as missing_key:
            print(missing_key)
            messages.warning(request, "Please complete the form.")
            try:
                return redirect(request.META.get('HTTP_REFERER'))
            except:
                return render(request, 'registrations/sign_up.html', context)
        except ValueError as value_error:
            print(value_error)
            messages.warning(request, "Invalid values entered in the form. Please fill again!")
            try:
                return redirect(request.META.get('HTTP_REFERER'))
            except:
                return render(request, 'registrations/sign_up.html', context)

@csrf_exempt
def login_view(request):
    """
        Handles user's login
    """

    if request.method == 'GET':
        if request.user.is_authenticated:
            if request.user.is_active:
                try:
                    profile = UserProfile.objects.get(auth_user=request.user)
                    return redirect('home')
                except UserProfile.DoesNotExist:
                    messages.warning(request, 'Please complete your profile details.')
                    return redirect('complete_profile')
            else:
                messages.warning(request, 'Invalid username/password. Please try again.')
                try:
                    return redirect(request.META.get('HTTP_REFERER'))
                except:
                    return redirect('login')
        else:
            return render(request, 'registrations/login.html')

    elif request.method == 'POST':
        username = request.POST['username'] # usernane or email
        password = request.POST['password']
        user = authenticate(username=username, password=password)
        if user is None: # if username authentication fails, try email
            user = authenticate(email=username, password=password)

        if user is not None:
            if user.is_active:
                try:
                    login(request, user)
                    try:
                        profile = UserProfile.objects.get(auth_user=user)
                        return redirect('home')
                    except UserProfile.DoesNotExist:
                        messages.warning(request, 'Please complete your profile details.')
                        return redirect('complete_profile')
                except Exception as e:
                    message = "User does not Exist."
                    context = {'error_heading':'No User','message' : message,'url':request.build_absolute_uri(reverse('login'))}
                    return render(request, 'registrations/message.html', context)
        else:
            messages.warning(request, 'Invalid username/password. Please try again.')
            try:
                return redirect(request.META.get('HTTP_REFERER'))
            except:
                return redirect('login')

@csrf_exempt
@login_required(login_url='login')
def complete_profile(request):
    """
        Complete user's profile details
    """
    if request.method == "GET":
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(auth_user=request.user)
                return redirect('home')
            except UserProfile.DoesNotExist:
                context = {
                        "courses": Course.objects.all(),
                        "colleges": College.objects.all()
                    }
                return render(request, 'registrations/complete_profile.html', context)
        else:
            messages.warning(request, "Please login first.")
            return redirect('login')

    elif request.method == "POST":
        if request.user.is_authenticated:
            try:
                profile = UserProfile.objects.get(auth_user=request.user)
                return redirect('home')
            except:
                pass
        else:
            messages.warning(request, "Please login first.")
            return redirect('login')

        data = request.POST

        try: # for required values
            college_name = str(data["college_name"])
            course_name = str(data["course_name"])
            semester = data["semester"] #1 to 6 or Masters
            gender = str(data["gender"])
        except KeyError as e:
            context = {
                    "courses": Course.objects.all(),
                    "colleges": College.objects.all()
                }
            messages.error(request, "Please complete the form.".format(e))
            return render(request, 'registrations/complete_profile.html', context)
        except ValueError as value_error:
            context = {
                    "courses": Course.objects.all(),
                    "colleges": College.objects.all()
                }
            messages.error(request, "Invalid Value: {}".format(value_error))
            return render(request, 'registrations/complete_profile.html', context)

        try:
            college = College.objects.get(name=college_name)
        except College.DoesNotExist:
            context = {
                    "courses": Course.objects.all(),
                    "colleges": College.objects.all()
            }
            messages.error(request, "Please choose college from the list only.")
            return render(request, 'registrations/complete_profile.html', context)

        try:
            course = Course.objects.get(name=course_name)
        except Course.DoesNotExist:
            context = {
                    "courses": Course.objects.all(),
                    "colleges": College.objects.all()
            }
            messages.error(request, "Please choose course from the list only.")
            return render(request, 'registrations/complete_profile.html', context)

        if semester == "Masters":
            semester = 7

        try:
            profile_pic = request.FILES["file"]
            user_prof = UserProfile.objects.create(
                auth_user = request.user,
                gender = gender,
                course = course,
                college = college,
                image = profile_pic,
                semester = semester
            )
        except KeyError:
            img_path = '../media/default_male_dp.png'
            if gender == "F":
                img_path = '../media/default_female_dp.png'
            elif gender == "O":
                img_path = "../media/default_neutral_dp.jpg"

            user_prof = UserProfile.objects.create(
                auth_user = request.user,
                gender = gender,
                course = course,
                college = college,
                semester = semester,
                image = img_path
            )
        messages.success(request, "Profile Complete!")
        return redirect('home')

@login_required(login_url='login')
@has_profile_completed
@csrf_exempt
def profile(request):
    """
        Allows user to view his/her profile page
    """
    context = {
        "books_count": Book.objects.filter(seller__auth_user=request.user, sold=False).count(),
        "bookset_count": BookSet.objects.filter(seller__auth_user=request.user, sold=False).count(),
        "books_sold": Book.objects.filter(seller__auth_user=request.user, sold=True).count(),
        "first_name": request.user.first_name,
        "last_name": request.user.last_name,
        "email": request.user.email,
        "college_name": request.user.profile.college.name,
        "college_category": request.user.profile.college.category,
        "course_name": request.user.profile.course.name,
    }
    semester = request.user.profile.semester
    if semester == 7:
        semester = "Masters"
    context["semester"] = semester

    if request.method == "GET":
        return render(request, 'registrations/profile.html', context)

    elif request.method == "POST": # edit profile
        data = request.POST

        try:
            first_name = str(data["first_name"])
            last_name = str(data["last_name"])
            semester = data["semester"]
            semester = semester.strip()
            valid_sems = ["1", "2", "3", "4", "5", "6", "masters", "Masters"]
            if semester not in valid_sems:
                messages.warning(request, "Invalid value for semester.")
                return redirect(request.META.get('HTTP_REFERER'))
            if semester == "Masters" or semester == "masters":
                semester = 7
            else:
                semester = int(semester)

            profile = request.user.profile
            profile.semester = semester
            profile.save()
            first_name = first_name.strip()
            last_name = last_name.strip()
            request.user.first_name = first_name
            request.user.last_name = last_name
            request.user.save()
            messages.warning(request, "Profile updated successfully!")
            return redirect('profile')
        except KeyError as missing_key:
            messages.warning(request, "Missing value: !".format(missing_key))
            return redirect(request.META.get('HTTP_REFERER'))

@login_required(login_url='login')
@has_profile_completed
def change_pic(request):
    """
        Allows users to change their profile pic
    """
    if request.method == "POST":
        try:
            new_dp = request.FILES["file-input"]
            try:
                prof = UserProfile.objects.get(auth_user=request.user)
                prof.image = new_dp
                prof.save()
                messages.warning(request, "Profile picture changed successfully!")
                return redirect('profile')
            except UserProfile.DoesNotExist:
                messages.warning(request, "Please complete your profile first.")
                return redirect('complete_profile')
        except KeyError:
            messages.warning(request, "No image was selected")
            return redirect(request.META.get('HTTP_REFERER'))


@login_required(login_url='login')
@has_profile_completed
def logout_view(request):
    """
        Logout user from portal
    """
    logout(request)
    return redirect('login')

@csrf_exempt
@login_required(login_url='login')
@has_profile_completed
def sell_book(request):
    """
        Handles the form for adding an individual listing of book/reading to sell
    """
    if request.method == 'GET':
        books = Book.objects.filter(seller__auth_user=request.user)
        return render(request, 'registrations/sell_book.html', {"courses": Course.objects.all()})

    elif request.method == 'POST':
        data = request.POST
        try: # for required values
            title = str(data['title'])
            condition = str(data['condition'])
            course_name = str(data['course_name'])
            semester = data['semester']
            price = float(data['price'])
            book_type = str(data["type"]) # contains exact category value 'B' or 'R'
        except KeyError as e:
            messages.error(request, "Missing Field {}".format(e))
            return render(request, 'registrations/sell_book.html', {"courses": Course.objects.all()})
        except ValueError as value_error:
            messages.error(request, "Invalid Value: {}".format(value_error))
            return render(request, 'registrations/sell_book.html', {"courses": Course.objects.all()})

        try:
            seller = UserProfile.objects.get(auth_user=request.user)
        except UserProfile.DoesNotExist:
            messages.error(request, "Please complete your profile details first.")
            return render(request, 'registrations/sell_book.html', {"courses": Course.objects.all()})

        if book_type == "B":
            try:
                edition = data["edition"] # optional for Reading
                if edition == "":
                    messages.warning(request, "You must enter an edition if you're adding a book.")
                    return redirect(request.META.get('HTTP_REFERER'))
                edition = edition.strip()
            except KeyError as e:
                messages.warning(request, "You must enter an edition if you're adding a book.")
                return redirect(request.META.get('HTTP_REFERER'))
        try:
            book_image = request.FILES["file"]
        except KeyError:
            messages.warning(request, "Please upload an image for your listing.")
            return render(request, 'registrations/sell_book.html', {"courses": Course.objects.all()})

        try:
            course_name = course_name.strip()
            course = Course.objects.get(name=course_name)
        except Course.DoesNotExist:
            messages.warning(request, "Please select a course from the list.")
            return render(request, 'registrations/sell_book.html', {"courses": Course.objects.all()})
        # end of data validation

        semester = semester.strip()
        if semester == "Masters":
            if course_name == "Masters":
                semester = 7
            else:
                messages.warning(request, "Invalid course-semester value combination.")
                return redirect(request.META.get('HTTP_REFERER'))
        semester = int(semester)

        price = int(price)
        title = title.strip()
        condition = condition.strip()
        try:
            contains_notes = data["notes"]
            contains_notes = True
        except KeyError:
            contains_notes = False

        new_book = Book.objects.create(
                                    title=title,
                                    category=book_type,
                                    contains_notes=contains_notes,
                                    condition=condition,
                                    semester=semester,
                                    image=book_image,
                                    course=course,
                                    price=price,
                                    seller=seller,
                                    additional_details=str(data["additional_details"]).strip()
                                )
        messages.success(request, "Success! Book added for the sellers to see.")
        return render(request, 'registrations/sell_book.html', {"courses": Course.objects.all()})

@login_required(login_url='login')
def about(request):
    """
        The 'About Us' page
    """
    return render(request, 'registrations/about.html')

@login_required(login_url='login')
def contact(request):
    """
        The 'Contact Us' page
    """
    return render(request, 'registrations/contact.html')

@login_required(login_url='login')
@has_profile_completed
def search_book(request):
    """
        Allows users to do a custom search for a book
    """

    if request.method == 'GET':
        context = {}
    else:
        form_data = request.POST

        try:
            search_keyword = form_data['search_keyword']
            course_id = form_data['course_id']
            category = form_data['category']
            semester = form_data['semester']
            sort_by = form_data['sort_by']

        except KeyError as missing_key_exception:
            m = re.search("'([^']*)'", str(missing_key_exception))
            key = m.group(1)
            messages.error(request, 'Missing data in form : {}. If problem persists contact administrator.'.format(key))
            context = {
                        'form_data': form_data
            }

            return render(request, 'registrations/search_book.html', context=context)

        if course_id == 'all':
            course_id = [course.id for course in Course.objects.all()]
        else:
            course_id = [int(course_id)]

        if semester == 'all':
            semester = [1,2,3,4,5,6,7]
        else:
            semester = [int(semester)]

        if category == 'all':
            category = ['B', 'R']
        else:
            category = [category]

        try:
            contains_notes = form_data["notes_req"]
            books = Book.objects.filter(course__id__in=course_id, semester__in=semester,
                title__contains=search_keyword,category__in=category, bookset=None,
                contains_notes=True, sold=False).exclude(seller=request.user.profile).order_by(sort_by)
        except KeyError:
            books = Book.objects.filter(course__id__in=course_id, semester__in=semester,
            title__contains=search_keyword,category__in=category, bookset=None,
            sold=False).exclude(seller=request.user.profile).order_by(sort_by)

        try:
            page_no = int(form_data['page_no'])
        except KeyError:
            page_no = 1

        if books.count() == 0:
            search_result = "No Matching Results Found"
            context = {
                "search_result": search_result,
                "form_data": form_data,
            }
        else:
            search_result = "Search Results"
            paginator = Paginator(books, 1)

            try:
                page_books = paginator.page(page_no)
            except PageNotAnInteger:
                page_no = 1
                page_books = paginator.page(page_no)
            except EmptyPage:
                page_no = paginator.num_pages
                page_books = paginator.page(page_no)

            page_info = "Page {} of {}".format(page_no, paginator.num_pages)

            context = {
                "search_result": search_result,
                "books": page_books,
                "form_data": form_data,
                "is_paginated": True,
                "page_info": page_info
            }
    return render(request, 'registrations/search_book.html', context=context)

@login_required(login_url='login')
@has_profile_completed
def view_listings(request):
    """
        Allows the seller to view the listings made by him/her
        Title, Course, Year, Price, Sold, Mark as sold, Edit Details
    """
    seller_books = Book.objects.filter(seller__auth_user=request.user)

    if len(seller_books) == 0:
        messages.warning(request, "You have no listing so far. You can create one by going to Sell option in the sidebar.")
        return redirect('home')

    rows = [
            {
                'data': [
                            {"value": book.title, "type": "Title"},
                            {"value": book.course.name, "type": "Course Name"},
                            {"value": book.semester, "type": "Semester"},
                            {"value": book.price, "type": "Price"},
                            {"value": book.interested_count, "type": "Interested Count"}
                        ],

                'link': [
                            {
                                'title':'Mark as Sold',
                                'url':reverse('mark_sold', kwargs={ 'b_id': book.id })
                            },

                            {
                                'title':'Edit Details',
                                'url':reverse('edit_listing_details', kwargs={ 'b_id': book.id })
                            },
                            {
                                'title':'Remove Book',
                                'url':reverse('remove_book', kwargs={ 'b_id': book.id })
                            }
                        ],
                'sold': book.sold
            }for book in seller_books # user's listings
           ]


    tables = [
                {
                    'title': 'My Book Listings',
                    'rows': rows,
                    'headings': [
                        'Title',
                        'Course',
                        'Semester',
                        'Price',
                        'Interested Buyers',
                        '',
                        'Edit Details',
                        'Remove Listing'
                        ]
                }
            ]
    # print(tables[0]["rows"][8]["data"][0]["value"], tables[0]["rows"][8]["sold"])
    return render(request, 'registrations/view_listings.html', {"tables": tables})

@login_required(login_url='login')
@has_profile_completed
def view_set_listings(request):
    """
        Allows the seller to view the listings made by him/her
        Title, Course, Year, Price, Sold, Mark as sold, Edit Details
    """
    return

@login_required(login_url='login')
@has_profile_completed
def mark_sold(request, b_id):
    try:
        book = Book.objects.get(id=b_id, seller__auth_user=request.user)
        book.sold = True
        book.save()
        return redirect('my_listings')
    except Book.DoesNotExist:
        messages.warning(request, "Book not found or You are not authorized to mark it as SOLD.")
        return redirect('my_listings')

@login_required(login_url='login')
@has_profile_completed
def remove_book(request, b_id):
    try:
        book = Book.objects.get(id=b_id, seller__auth_user=request.user)
        if book.sold == True:
            messages.warning(request, "This book is already SOLD!")
            return redirect('my_listings')
        book.delete()
        messages.success(request, "Book listing removed successfully!")
        return redirect('my_listings')
    except Book.DoesNotExist:
        messages.warning(request, "Book not found or You are not authorized remove it.")
        return redirect('my_listings')

@login_required(login_url='login')
@has_profile_completed
def edit_listing_details(request, b_id):
    """
        Allows users to edit their particular listing details
    """
    user = request.user
    try:
        book = Book.objects.get(id=b_id)
        if book.sold == True:
            messages.warning(request, "This book is already sold.")
            return redirect('my_listings')
    except Book.DoesNotExist:
        messages.warning(request, "Book listing not found.")
        return render(request, 'registrations/edit_listing_details.html', context=context)

    context = {
        "book": book,
        "courses": Course.objects.all(),
    }
    if book.semester == 7:
        context["semester"] = "Masters"
    else:
        context["semester"] = book.semester

    if request.method == "GET":
        return render(request, 'registrations/edit_listing_details.html', context=context)

    elif request.method == "POST":
        data = request.POST
        try: # for required values
            title = str(data['title'])
            condition = str(data['condition'])
            course_name = str(data['course_name'])
            semester = data['semester']
            price = float(data['price'])
            book_type = str(data["type"]) # contains exact category value 'B' or 'R'
        except KeyError as e:
            messages.error(request, "Missing Field {}".format(e))
            return render(request, 'registrations/edit_listing_details.html', context=context)
        except ValueError as value_error:
            messages.error(request, "Invalid Value: {}".format(value_error))
            return render(request, 'registrations/edit_listing_details.html', context=context)

        try:
            seller = UserProfile.objects.get(auth_user=request.user)
        except UserProfile.DoesNotExist:
            messages.error(request, "Please complete your profile details first.")
            return redirect('complete_profile')

        if book_type == "B":
            try:
                edition = data["edition"] # optional for Reading
                if edition == "":
                    messages.warning(request, "You must enter an edition if you're adding a book.")
                    return render(request, 'registrations/edit_listing_details.html', context=context)
                edition = edition.strip()
            except KeyError as e:
                messages.warning(request, "You must enter an edition if you're adding a book.")
                return render(request, 'registrations/edit_listing_details.html', context=context)

        try:
            course_name = course_name.strip()
            course = Course.objects.get(name=course_name)
        except Course.DoesNotExist:
            messages.warning(request, "Please select a course from the list.")
            return render(request, 'registrations/edit_listing_details.html', context=context)

        if semester == "Masters":
            if course_name == "Masters":
                semester = 7
            else:
                messages.warning(request, "Invalid course-semester value combination.")
                return redirect(request.META.get('HTTP_REFERER'))
        semester = int(semester)

        price = int(price)
        title = title.strip()
        condition = condition.strip()
        try:
            contains_notes = data["notes"]
            contains_notes = True
        except KeyError:
            contains_notes = False

        book.title = title
        book.category = book_type
        book.contains_notes = contains_notes
        book.condition = condition
        book.semester = semester
        book.course = course
        book.price = price
        book.seller = seller
        book.additonal_details = str(data["additional_details"]).strip()
        book.save()
        try:
            book_image = request.FILES["file"]
            book.image = book_image
            book.save()
        except KeyError:
            pass
        messages.success(request, "Success! Book listing edited successfully!")
        return redirect('my_listings')

@login_required(login_url='login')
@has_profile_completed
def search_bookset(request):
    """
        Allows users to do a custom search for a BookSet
    """

    if request.method == 'GET':
        context = {}
    else:
        form_data = request.POST

        try:
            search_keyword = form_data['search_keyword']
            course_id = form_data['course_id']
            semester = form_data['semester']
            sort_by = form_data['sort_by']
        except KeyError as missing_key_exception:
            m = re.search("'([^']*)'", str(missing_key_exception))
            key = m.group(1)
            messages.error(request, 'Missing data in form : {}. If problem persists contact administrator.'.format(key))
            context = {
                'form_data': form_data
            }
            return render(request, 'registrations/search_bookset.html', context=context)

        if course_id == 'all':
            course_id = [course.id for course in Course.objects.all()]
        else:
            course_id = [int(course_id)]

        if semester == 'all':
            semester = [1,2,3,4,5,6,7]
        else:
            semester = [int(semester)]

        try:
            contains_notes = form_data["notes_req"]
            booksets = BookSet.objects.filter(course__id__in=course_id, semester__in=semester,
                title__contains=search_keyword, contains_notes=True,
                sold=False).exclude(seller=request.user.profile).order_by(sort_by)
        except KeyError:
            booksets = BookSet.objects.filter(course__id__in=course_id, semester__in=semester,
            title__contains=search_keyword, sold=False).exclude(seller=request.user.profile).order_by(sort_by)

        try:
            page_no = int(form_data['page_no'])
        except KeyError:
            page_no = 1

        if booksets.count() == 0:
            search_result = "No Matching Results Found"
            context = {
                "search_result": search_result,
                "form_data": form_data,
            }
        else:
            search_result = "Search Results"
            paginator = Paginator(booksets, 1)

            try:
                page_booksets = paginator.page(page_no)
            except PageNotAnInteger:
                page_no = 1
                page_booksets = paginator.page(page_no)
            except EmptyPage:
                page_no = paginator.num_pages
                page_booksets = paginator.page(page_no)

            page_info = "Page {} of {}".format(page_no, paginator.num_pages)

            context = {
                "search_result": search_result,
                "booksets": page_booksets,
                "form_data": form_data,
                "is_paginated": True,
                "page_info": page_info
            }
    return render(request, 'registrations/search_bookset.html', context=context)

@login_required(login_url='login')
@has_profile_completed
def add_interested(request):
    """
        add a book/bookset to interested
    """
    try:
        type = request.GET.get('type')
        id = request.GET.get('id')

        if type == 'book':
            book_obj = Book.objects.get(id=id)
            book_obj.interested_users.add(request.user.profile)
            book_obj.interested_count = book_obj.interested_users.all().count()
            book_obj.save()
            response_message = "Success"
            seller = book_obj.seller

        elif type == 'bookset':
            bookset_obj = BookSet.objects.get(id=id)
            bookset_obj.interested_users.add(request.user.profile)
            bookset_obj.interested_count = bookset_obj.interested_users.all().count()
            bookset_obj.save()
            response_message = "Success"
            seller = bookset_obj.seller
        else:
            response_message = "Invalid entity type"

    except KeyError:
        response_message = "Invalid Request"
    except Book.DoesNotExist:
        response_message = "Invalid Book-Id"
    except BookSet.DoesNotExist:
        response_message = "Invalid BookSet-Id"

    if response_message == "Success":
        seller_name = seller.auth_user.first_name + ' ' + seller.auth_user.last_name
        seller_email = seller.auth_user.email
        seller_college = seller.college.name
        response = {
                    'message': response_message,
                    'seller_name': seller_name,
                    'seller_email': seller_email,
                    'seller_college': seller_college
                    }
    else:
        response = {'message': response_message}

    return JsonResponse(response)

@login_required(login_url='login')
@has_profile_completed
@csrf_exempt
def change_password(request):
    """
        Allows users to change their password
    """
    user = request.user
    data = request.POST
    try:
        old_pass = str(data["old_pass"])
        new_pass = str(data["new_pass"])
        new_pass_confirm = str(data["new_pass_confirm"])
        if new_pass == "":
            messages.warning(request, "New password can't be blank.")
            return redirect(request.META.get('HTTP_REFERER'))
        try:
            existing_user = authenticate(username=user.username, password=old_pass)
            if new_pass != new_pass_confirm:
                messages.warning(request, "Passwords don't match.")
                return redirect(request.META.get('HTTP_REFERER'))
            else:
                existing_user.set_password(new_pass)
                existing_user.save()
                messages.warning(request, "Password changed successfully!.")
                update_session_auth_hash(request, existing_user)
                return redirect('profile')
        except:
            messages.warning(request, "Old password doesn't match.")
            return redirect(request.META.get('HTTP_REFERER'))

    except KeyError as missing_key:
        messages.warning(request, "Password change failure! Missing field in the form.")
        try:
            return redirect(request.META.get('HTTP_REFERER'))
        except:
            return render(request, 'registrations/profile.html', context)

def sell_bookset(request):
    """
        Form to add bookset for selling.
    """
    context = {
                'courses': Course.objects.all()
    }
    return render(request, 'registrations/sell_bookset.html',context=context)
