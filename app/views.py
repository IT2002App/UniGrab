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

            cursor.execute("SELECT * FROM Users WHERE user_name = %s", [request.POST['userName']])
            userName = cursor.fetchone()
            ## No customer with same id
            if userName == None:
                cursor.execute("SELECT * FROM Users WHERE email = %s", [request.POST['email']])
                email = cursor.fetchone()
                if email == None:
                    cursor.execute("INSERT INTO Users(user_name,email,phone_number,address,birthday,passwords) VALUES (%s, %s, %s, %s, %s, %s)"
                        , [request.POST['userName'], request.POST['email'], request.POST['phoneNumber'], 
                         request.POST['address'],request.POST['dob'], request.POST['password']])
                    return redirect('Login')
                else:
                    status = 'User with email %s already exists' % (request.POST['email'])
            else:
                status = 'User with name %s already exists' % (request.POST['userName'])


    context['status'] = status

    return render(request, "Register.html", context)


def Login(request):
    context = {}
    status = ''

    if request.POST:
        if request.POST['userName'] == 'admin':
            return redirect('Admin')
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:

            cursor.execute("SELECT * FROM users WHERE user_name = %s AND passwords = %s", [request.POST['userName'],request.POST['password']])
            user = cursor.fetchone()
            ## No customer with same id
            if user == None:
                status = 'Wrong userName or password' 
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
                cursor.execute("SELECT user_id FROM Orders WHERE order_id = %s", [request.POST['id']])
                order=cursor.fetchone()
                if order!=userID:
                    cursor.execute("INSERT INTO claim VALUES (%s, %s, %s)", [request.POST['id'],order,userID])
                    cursor.execute("UPDATE Orders SET status = 'claimed' WHERE order_id = %s", [request.POST['id']])#!!!!!!!!!!!!!!!!!!!!!!!!!
                    return redirect('Home')
    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT o.*, u.user_name FROM Orders o, Users u WHERE status = 'waiting' AND o.user_id=u.user_id ORDER BY u.user_id")
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
                cursor.execute("DELETE FROM claim WHERE order_id = %s", [request.POST['orderId']])
                cursor.execute("UPDATE Orders SET status = 'waiting' WHERE order_id = %s", [request.POST['orderId']])#!!!!!!!!!!!!!!!alter
                return redirect('claimedOrder')
        if request.POST['action'] == 'delivered':
            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM claim WHERE order_id = %s", [request.POST['orderId']])
                cursor.execute("UPDATE Orders SET status = 'completed' WHERE order_id = %s", [request.POST['orderId']])#！！！！！！！！！！！！！！！！alter
                return redirect('claimedOrder')
    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT o.*,u.user_name FROM Orders o, Users u, Claim c WHERE c.deliveryman_id = %s AND o.order_id=c.order_id AND u.user_id=o.user_id ", [userID])
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
                cursor.execute("DELETE FROM claim WHERE order_id = %s", [request.POST['orderId']])
                cursor.execute("DELETE FROM Orders WHERE order_id = %s", [request.POST['orderId']])
                return redirect('myOrder')
    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM orders WHERE user_id = %s ORDER BY order_id",[userID])
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
        cursor.execute("SELECT * FROM Orders WHERE order_id = %s", [id])
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
        cursor.execute("SELECT * FROM users WHERE user_id = %s", [userID])
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
        cursor.execute("SELECT * FROM users WHERE user_id = %s", [userID])
        user=cursor.fetchone()
    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:
                cursor.execute("INSERT INTO Orders (user_id,phone_number  ,order_content,shop_address,user_address,fee,status) VALUES (%s,%s, %s, %s, %s, %s, %s)"
                    , [userID, user[3], request.POST['orderContent'], request.POST['shopAddress'], user[5], request.POST['fee'],'waiting'])
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
        cursor.execute("SELECT * FROM Users WHERE user_id = %s", [userID])
        user=cursor.fetchone()

    if request.POST:
        ## Check if customerid is already in the table
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM Users WHERE user_name = %s", [request.POST['userName']])
            result = cursor.fetchone()
            ## No customer with same id
            if result == None or result == user[1]:
                cursor.execute("SELECT * FROM Users WHERE email = %s", [request.POST['email']])
                email = cursor.fetchone()
                if email == None or email == user[2]:
                    cursor.execute("UPDATE Users SET user_name = %s,email = %s,phone_number = %s,birthday = %s,address = %s,passwords = %s WHERE user_id = %s", 
				   [request.POST['userName'],equest.POST['email'],[request.POST['phoneNumber'],
                                   request.POST['dob'],request.POST['address'],request.POST['password'],userID])
                    return redirect('Login')
                else:
                    status = 'User with email %s already exists' % (request.POST['email'])
            else:
                status = 'User with name %s already exists' % (request.POST['userName'])
    context['status'] = status
    context['user'] = user
    return render(request, "editUser.html", context)

def editOrder(request,id ):
    context = {}
    status = ''
    userID=request.COOKIES.get('userID')
    if userID == None:
        return redirect('Login')
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM Orders WHERE order_id = %s", [id])
        order=cursor.fetchone()
    if request.POST:
        with connection.cursor() as cursor:
            cursor.execute("UPDATE Orders SET order_content = %s,shop_address = %s,fee = %s WHERE order_id = %s", 
			   [request.POST['orderContent'],
			   request.POST['shopAddress'],request.POST['fee'],id])
        return redirect('myOrder')
    context['order'] = order
    return render(request, "editOrder.html", context)



def Admin(request):
    status='order'
    if request.POST:
        if 'act' in request.POST and request.POST['act'] == 'Home':
            return redirect('Home')
        if 'act' in request.POST and request.POST['act'] == 'orders':
                status='order'
        if 'act' in request.POST and request.POST['act'] == 'users':
            status='user'
        if 'action' in request.POST and request.POST['action'] == 'Delete':
            if status=='order' and 'orderId' in request.POST:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM claim WHERE order_id = %s",[request.POST['orderId']])
                    cursor.execute("DELETE FROM orders WHERE order_id = %s",[request.POST['orderId']])
                    return redirect('Admin')
            else:
                with connection.cursor() as cursor:
                    cursor.execute("DELETE FROM users WHERE user_id = %s",[request.POST['userId']])
        
    ## Use raw query to get all objects
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM orders ORDER BY order_id")
        Orders = cursor.fetchall()
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM users ORDER BY user_id")
        Users = cursor.fetchall()
    result_dict = {'orders': Orders,'users': Users,'status':status}

    return render(request,'Admin.html',result_dict)
