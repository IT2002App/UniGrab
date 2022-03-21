from django.shortcuts import render, redirect
from django.db import connection
from django.http import HttpResponse

# Create your views here.
def tryy(request):
	return render(request,'Home.html',{})


def Register(request):
    """Shows the main page"""
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM users WHERE userID = %s", [request.POST['userID']])
            userID = cursor.fetchone()
            ## No customer with same id
            if userID == None:
                cursor.execute("SELECT * FROM users WHERE email = %s", [request.POST['email']])
                email = cursor.fetchone()
                if email == None:
                    cursor.execute("INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s)"
                        , [request.POST['userID'], request.POST['email'], request.POST['phoneNumber'], 
                        request.POST['dob'], request.POST['address'], request.POST['password']])
                    return redirect('Login')
                else:
                    status = 'User with email %s already exists' % (request.POST['email'])
            else:
                status = 'User with ID %s already exists' % (request.POST['userID'])


    context['status'] = status

    return render(request, "Register.html", context)


def Login(request):
    context = {}
    status = ''

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM users WHERE userID = %s AND passwords = %s", [request.POST['userID'],request.POST['password']])
            user = cursor.fetchone()
            ## No customer with same id
            if user == None:
                status = 'Wrong userID or password' 
            else: 
                resp=redirect('Home')
                resp.set_cookie('userID',user[0],3600)
                return resp    


    context['status'] = status
 
    return render(request, "Login.html", context)




def Home(request):
    """Shows the main page"""
    userID=request.COOKIES.get('userID')
    ## Delete customer
    if request.POST:
        if request.POST['action'] == 'claim':
            if userID==None:
                return redirect('Login')
            with connection.cursor() as cursor:
                cursor.execute("SELECT * FROM orders WHERE orderID = %s", [request.POST['id']])
                order=cursor.fetchone()
                cursor.execute("INSERT INTO paired VALUES (%s, %s, %s)", [order[0],order[1],userID])

        
    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM orders ORDER BY userID")
        awaitingOrders = cursor.fetchall()

    result_dict = {'records': awaitingOrders}

    return render(request,'Home.html',result_dict)


def claimedOrder(request):
    """Shows the main page"""

    ## Delete customer
    userID=request.COOKIES.get('userID')
    if userID == None:
        return redirect('Login')
    if request.POST:
        if request.POST['action'] == 'cancel':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM paired WHERE orderID = %s", [request.POST['orderID']])
                return redirect('claimedOrder')
        if request.POST['action'] == 'delivered':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM paired WHERE orderID = %s", [request.POST['orderID']])
                cursor.execute("DELETE FROM order WHERE orderID = %s", [request.POST['orderID']])
                return redirect('claimedOrder')
    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM orders as o,paired as p WHERE o.orderID = p.orderID AND p.deliverymanID=%s ORDER BY o.orderID",[userID])
        claimedOrder = cursor.fetchall()

    result_dict = {'records': claimedOrder}

    return render(request,'claimedOrder.html',result_dict)



def myOrder(request):
    """Shows the main page"""
    userID=request.COOKIES.get('userID')
    if userID == None:
        return redirect('Login')
    ## Delete customer
    if request.POST:
        if request.POST['action'] == 'cancel':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM paired WHERE orderID = %s", [request.POST['orderID']])
                cursor.execute("DELETE FROM order WHERE orderID = %s", [request.POST['orderID']])
                return redirect('myOrder')
    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM orders WHERE userID = %s ORDER BY orderID",[userID])
        myOrder = cursor.fetchall()

    result_dict = {'records': myOrder}

    return render(request,'myOrder.html',result_dict)




# Create your views here.
def View(request, id):
    """Shows the main page"""
    userID=request.COOKIES.get('userID')
    if userID == None:
        return redirect('Login')
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM user WHERE userID = %s", [userID])
        customer = cursor.fetchone()
    result_dict = {'cust': customer}

    return render(request,'View.html',result_dict)


def Profile(request):
    """Shows the main page"""
    userID=request.COOKIES.get('userID')
    if userID == None:
        return redirect('Login')
    ## Use raw query to get a customer
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE userID = %s", [userID])
        customer = cursor.fetchone()
    result_dict = {'cust': customer}

    return render(request,'Profile.html',result_dict)


# Create your views here.





def placeOrder(request):
    context = {}
    status = ''
    userID=request.COOKIES.get('userID')
    if userID == None:
        return redirect('Login')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE userID = %s", [userID])
        user=cursor.fetchone()
    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:
                cursor.execute("INSERT INTO orders (userID,phoneNumber,orderContent,shopAddress,userAdress,fee) VALUES (%s, %s, %s, %s, %s, %s)"
                    , [userID, user[2], request.POST['orderContent'], request.POST['shopAddress'], user[4], request.POST['fee']])
        return redirect('myOrder')
    return render(request, "placeOrder.html", context)

# Create your views here.
def editUser(request, id):
    context = {}
    status = ''
    userID=request.COOKIES.get('userID')
    if userID == None:
        return redirect('Login')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE userID = %s", [userID])
        user=cursor.fetchone()

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM customers WHERE customerid = %s", [request.POST['userID']])
            result = cursor.fetchone()
            ## No customer with same id
            if result == None or result == user[0]:
                cursor.execute("SELECT * FROM customers WHERE email = %s", [request.POST['email']])
                email = cursor.fetchone()
                if email == None or result == user[1]:
                    cursor.execute("INSERT INTO customers VALUES (%s, %s, %s, %s, %s, %s)"#!!!!!!!!!!!!!change to alter later, remember to allow cascade
                        , [request.POST['userID'], request.POST['email'], request.POST['phoneNumber'], 
                        request.POST['dob'], request.POST['address'], request.POST['country'] ])
                    return redirect('Login')
                else:
                    status = 'User with email %s already exists' % (request.POST['email'])
            else:
                status = 'User with ID %s already exists' % (request.POST['userID'])
    context['status'] = status
    return render(request, "editUser.html", context)

def editOrder(request,orderID ):
    context = {}
    userID=request.COOKIES.get('userID')
    if userID == None:
        return redirect('Login')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users WHERE userID = %s", [userID])
        user=cursor.fetchone()

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM orders WHERE orderID = %s", [orderID])
            result = cursor.fetchone()
            ## No customer with same id
            cursor.execute("INSERT INTO orders VALUES (%s, %s, %s, %s, %s, %s)"#!!!!!!!!!!!!!change to alter later, remember to allow cascade
                , [request.POST['content'], request.POST['shopAddress'], request.POST['fee']])
            return redirect('Profile')
    return render(request, "editOrder.html")