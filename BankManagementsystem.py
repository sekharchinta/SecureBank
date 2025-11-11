import mysql.connector as db

#Database Connection
con=db.connect(user='root',password='Somu#123',host='localhost',database='Bank')
cur=con.cursor()

#Class for Account Creation
class CreateAccount:
    accno='10032051'
    import re
    
    #Full Name
    def name(self):
        while True:
            x=input(f'{"Full Name: ":<13}')
            if not x.isdigit() and len(x)!=0:
                return x
            else:
                print('Enter a Valid Name!')
                pass

    #Mobile Number
    def mobile(self,k):
        while True:
            x=input(f'{"MObile Number: ":<13}')
            match=self.re.fullmatch(r'[6-9]{1}[0-9]{9}$',x)
            if match:
                if k=='user':
                    cur.execute('select phnno from user_accounts where phnno=%s',(x,))
                    personalnum=cur.fetchone()
                else:
                    cur.execute('select phnno from admin_accounts where phnno=%s',(x,))
                    personalnum=cur.fetchone()
                if personalnum is None:
                    return x
                else:
                    print('Mobile Number Alredy Existed')
                    continue
            else:
                print('Enter a valid Mobile Number!')
                pass

    #Email ID    
    def email(self,k):
        while True:
            x=input(f'{"Email ID: ":<13}')
            match = self.re.fullmatch(r'[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}$', x)
            if match:
                if k=='user':
                    cur.execute('select email from user_accounts where email=%s',(x,))
                    personalemail=cur.fetchone()
                else:
                    cur.execute('select email from admin_accounts where email=%s',(x,))
                    personalemail=cur.fetchone()
                if personalemail is None:
                    return x
                else:
                    print('Email ID alredy Existed')
                    continue
            else:
                print('Enter a Valid Email Id!')
                pass

    #Savings Or Current
    def accounttype(self):
        while True:
            x=input(f'{"Account Type(Savings/Current): ":<13}')
            if (x.lower()=='savings' or x.lower()=='current') and len(x)!=0:
                return x
            else:
                print('Enter Valid Type!')  

    #Account Number
    def accountnumber(self):
        import random
        while True:
            num=random.randint(1000,9999)
            accnum=self.accno+str(num)
            cur.execute('select accountno from user_accounts where accountno=%s',(accnum,))
            get=cur.fetchone()
            if get is None:
                return int(accnum)
                break
            else:
                pass

    #Pin Creation
    def pincreate(self):
        while True:
            pin=input('Set a 4 digit Pin: ')
            pin1=input('Re-type your pin: ')
            if pin==pin1 and (len(pin)!=0 and len(pin1)!=0):
                if (len(pin)!=4 or not pin.isdigit()):
                    print('Pin Must be 4 digits')
                    continue
                else:  
                    return int(pin)
                    break
            else:
                print('Pin doesnot match try again')
                
    #User Account Creation
    def useraccount(self):
        accounttype='user'
        data1=[]
        data1.append(self.name())
        data1.append(self.mobile(accounttype))
        data1.append(self.email(accounttype))
        data1.append(self.accounttype())
        data1.append(self.accountnumber())
        data1.append(self.pincreate())
        data1.append('Account Holder')
        #Function Call
        return self.datainsertion1(data1)


    #Admin Account Creation
    def adminaccount(self):
        accounttype='admin'
        empid=input('Enter your Employee ID: ')
        if not empid.isdigit():
            print('Enter a Valid Employee ID!')
        else:
            cur.execute('select empid from bankemployees where empid=%s',(int(empid),))
            employeeid=cur.fetchone()
            if employeeid is None:
                print('Employee ID Not Found')
                return 0
            else:
                while True:
                    data2=[]
                    data2.append(self.name())
                    data2.append(self.mobile(accounttype))
                    data2.append(self.email(accounttype))
                    cur.execute('select employeeid from admin_accounts where employeeid=%s',(empid,))
                    details=cur.fetchone()
                    if details is None:
                        data2.append(empid)
                    else:
                        print('Account Alredy Existed with this Emplpoyee ID',empid)
                        return 0
                    data2.append(self.pincreate())
                    data2.append('Admin')
                    break
        #Function call
        return self.datainsertion2(data2)
    
    #Data Insertion in to DataBase
    def datainsertion1(self,data):  
        cur.execute('insert into user_accounts(username,phnno,email,accounttype,accountno) values(%s,%s,%s,%s,%s)',data[:5])
        cur.execute('insert into logins(id,pin,usertype) values(%s,%s,%s)',data[4:])
        con.commit()
        cur.execute('select username,accountno,accounttype from user_accounts where accountno=%s',(data[4],))
        showuserdetails=cur.fetchone()
        print('Account created Successfully')
        return showuserdetails
            
    def datainsertion2(self,data):
        cur.execute('insert into admin_accounts(adminname,phnno,email,employeeid) values(%s,%s,%s,%s)',data[:4])
        cur.execute('insert into logins(id,pin,usertype) values(%s,%s,%s)',data[3:])
        con.commit()
        return 'Account created Successfully'


#Class For User Login   
class Bank:

    #Initializing Data
    def __init__(self,name,mobile,email,accounttype,accountno,balance):
        self.name=name
        self.mobile=mobile
        self.email=email
        self.accounttype=accounttype
        self.accountno=accountno
        self.__balance=balance

    #Display Information
    def displayinfo(self):
        accounttype='account viewed'
        details=['Full Name','Account Number','Account Type','Account Balance']
        data=self.name,self.accountno,self.accounttype,self.__balance
        x=iter(data)
        for i in details:
            print(f'{i} : {next(x)}')       
        return 

    #Debit Amount
    def debit(self):
        accounttype='debit'
        amount=int(input('Enter amount to debit: '))
        if amount>self.__balance:
            return 'Insufficient balance'
        else:
            self.__balance=self.__balance-amount
            cur.execute('update user_accountS set balance=%s where accountno=%s',(self.__balance,self.accountno))
            cur.execute('insert into transactions(accountno,transactiontype,amount) values(%s,%s,%s)',(self.accountno,accounttype,amount))
            con.commit()
            return 'Amount Debited succesfully'

    #Credit Amount
    def credit(self):
        accounttype='credit'
        amount=int(input('Enter amount to credit: '))
        self.__balance=self.__balance+amount
        cur.execute('update user_accounts set balance=%s where accountno=%s',(self.__balance,self.accountno))
        cur.execute('insert into transactions(accountno,transactiontype,amount) values(%s,%s,%s)',(self.accountno,accounttype,amount))
        con.commit()
        return 'Amount Succesfully added'

    #Show Balance
    def accbalance(self):
        return f'Account Balance: {self.__balance}'

    #Pin Change
    def pinchange(self):
        accounttype='pinchange'
        cur.execute('select pin from logins where id=%s and usertype="Account Holder"',(self.accountno,))
        pin=cur.fetchone()
        while True:
            existpin=int(input('Enter your Existing Pin:'))
            if pin[0]==existpin:
                while True:
                    changepin1=int(input('Set a New Pin: '))
                    changepin2=int(input('Re-enter  New Pin: '))
                    if changepin1!=changepin2:
                        print('Pin doesnot match try again')
                        continue
                    if pin[0]==changepin1:
                        print('You choose same old pin Enter a new pin')
                        continue
                    pinchange=changepin1
                    cur.execute('update logins set pin=%s where id=%s',(pinchange,self.accountno))
                    con.commit()
                    print( 'Pin changed Succesfully')
                    return
            else:
                print('Incorrect Pin')
                pass
                
    #Print Statements     
    def statements(self):
        cur.execute('select transactiontype,amount,Event_date,Event_time from transactions where accountno=%s',(self.accountno,))
        data=cur.fetchall()
        if not data:
            print('Statements Not Found')
            return
        else:
            print('*'*25)
            print(f'{self.name} : {self.accountno}')
            print(f'{"Transaction Type":<18} | {"Amount":<8} | {"Date":<10} | {"Time"}')
            for i in data:
                print(f'{i[0]:<18} | {i[1]:<8} | {i[2]} | {i[3]}')

#Class For Admin Login
class Admin:

    #Print All User Details
    def viewallusers(self):
        cur.execute('select username,accountno,accounttype,phnno,email from user_accounts')
        data=cur.fetchall()
        if data is None:
            print('No Details Found')
        else:
            print(f'{"Name":<15} | {"Account number"} | {"Account Type"} | {"Mobile Number"} | {"Email"}')
            for i in data:
                print(f'{i[0]:<15} | {i[1]:<14} | {i[2]:<12} | {i[3]:<13} | {i[4]}')
            return

    #print single User Details
    def viewoneaccount(self):
        accno=int(input('Enter Account Number: '))
        cur.execute('select username,accountno,accounttype,phnno,email from user_accounts where accountno=%s',(accno,))
        data=cur.fetchone()
        if data is None:
            print('Details Not Found')
        else:
            details=['Full Name','Account Number','Account Type','Mobile Number','Email Id']
            for i in range(len(details)):
                print(f'{details[i]:<15} : {data[i]}')
            return

    #Print all transactions
    def viewalltransactions(self):
        cur.execute('select accountno,transactiontype,amount,Event_date,Event_time from transactions')
        data=cur.fetchall()
        if data is None:
            print('No Transactions Found')
        else:
            print(f'{"Account number"} | {"Transaction Type"} | {"Amount":<8} | {"Date":<10} | {"Time"}')
            for i in data:
                print(f'{i[0]:<14} | {i[1]:<16} | {i[2]:<8} | {i[3]} | {i[4]}')
            return

    #print Single User Transacion
    def viewonetransaction(self):
        accno=int(input('Enter Account Number: '))
        cur.execute('select accountno,transactiontype,amount,Event_date,Event_time from transactions where accountno=%s',(accno,))
        data=cur.fetchall()
        if len(data) == 0:
            print('No Transactions Found')
        else:
            print(f'{"Account number"} | {"Transaction Type"} | {"Amount":<8} | {"Date":<10} | {"Time"}')
            for i in data:
                print(f'{i[0]:<14} | {i[1]:<16} | {i[2]:<8} | {i[3]} | {i[4]}')
            return

    #print particular day Statements
    def viewdaytransaction(self):
        from datetime import datetime
        date=input('Enter Date(yyyy-mm-dd): ')
        try:
            datetime.strptime(date, '%Y-%m-%d')
            cur.execute('select accountno,transactiontype,amount,Event_date,Event_time from transactions where Event_date=%s',(date,))
            data=cur.fetchall()
            if len(data) == 0:
                print('No Transactions Found')
            else:
                print(f'{"Account number"} | {"Transaction Type"} | {"Amount":<8} | {"Date":<10} | {"Time"}')
                for i in data:
                    print(f'{i[0]:<14} | {i[1]:<16} | {i[2]:<8} | {i[3]} | {i[4]}')
                return
        except ValueError:
            print("Invalid date!")
            print('Expected date in this format(YYYY-MM-DD)')


#Creation of Objects to the Classes
showout=['Create Account','User Login','Admin Login','Exit']
while True:
    print('*'*25)
    for k,v in enumerate(showout,1):
        print(f'{k} : {v}')
    print('*'*25)
    choi=input('Choose one: ')
    if choi.isdigit():
        choice=int(choi)

        #Account Creation 
        if choice==1:
            print('*'*25)
            again=['User Account','Admin Account','Exit']
            for i,j in enumerate(again,1):
                print(f'{i} : {j}')
            print('*'*25)
            createoption=input('Select One Option: ')
            if createoption.isdigit():
                createopt=int(createoption)
                if createopt==1:
                    creacc=CreateAccount()
                    getdetails=creacc.useraccount()
                    print('*'*25)
                    print('Account Details')
                    details=['Name','Account Number','Account Type']
                    for i in range(len(details)):
                        print(f'{details[i]} : {getdetails[i]} ')
                elif createopt==2:
                    createad=CreateAccount()
                    getadmin=createad.adminaccount()
                    if getadmin == 0:
                        continue
                    else:
                        print(getadmin)
                        
                elif createopt==3:
                    break
                else:
                    print('Enter a valid Input!')
            else:
                print('Enter a valid option: ')
            

        #User Functions
        elif choice==2:
            account=input('Enter Account Number: ')
            if account.isdigit()==True:
                cur.execute('select pin from logins where id=%s and usertype="Account Holder"',(int(account),))
                data=cur.fetchone()
                if data is None:
                    print('Account not Found')
                else:
                    pin=input('Enter Pin: ')
                    if len(pin)==0 or not pin.isdigit():
                        print('Incorrect Pin!')
                    else:
                        if data[0]==int(pin):
                            while True:
                                print('*'*25)
                                showin=['Display Information','Debit amount','Credit Amount','Balance','Change Pin','All Statements','Exit']
                                for k,v in enumerate(showin,1):
                                    print(f'{k} : {v}')
                                print('*'*25)
                                option=input('Select One Option: ')
                                if option.isdigit():
                                    opt=int(option)
                                    cur.execute('select * from user_accounts where accountno=%s',(int(account),))
                                    data=cur.fetchone()
                                    obj=Bank(*data)

                                    #Function selection
                                    if opt == 1:
                                        obj.displayinfo()
                                    elif opt==2:
                                        print(obj.debit())
                                    elif opt==3:
                                        print(obj.credit())
                                    elif opt==4:
                                        print(obj.accbalance())
                                    elif opt==5:
                                        obj.pinchange()
                                    elif opt==6:
                                        obj.statements()   
                                    elif opt==7:
                                        break
                                    else:
                                        print('Enter a Valid Input!')
                                else:
                                    print('Enter Valid Input!')
                        else:
                            print('Incorrect Account Number OR Password!')
            else:
                print('Please Enter a valid Account Number: ')

        #Admin functions            
        elif choice==3:
            account=input('Enter Employee ID : ')
            if account.isdigit()==True:
                cur.execute(f'select pin from logins where id={int(account)} and usertype="Admin"')
                data=cur.fetchone()
                if data is None:
                    print('Account not Found')
                else:
                    pin=input('Enter Pin: ')
                    if len(pin)==0 or not pin.isdigit():
                        print('Incorrect Pin!')
                    else:
                        if data[0]==int(pin):
                            while True:
                                print('*'*25)
                                showadmin=['View all Users','View one Account','View all users Transactions','View one Account Transaction','View A Day Transaction','Exit']
                                for k,v in enumerate(showadmin,1):
                                    print(f'{k} : {v}')
                                print('*'*25)
                                select=int(input('Select one Option: '))
                                ad=Admin()
                                if select == 1:
                                    ad.viewallusers()
                                elif select==2:
                                    ad.viewoneaccount()
                                elif select==3:
                                    ad.viewalltransactions()
                                elif select==4:
                                    ad.viewonetransaction()
                                elif select ==5:
                                    ad.viewdaytransaction()
                                elif select==6:
                                    break
                                else:
                                    print('Enter a valid Input!')
                        else:
                            print('Incorrect ID OR Pin!')
            else:
                print('Enter Valid INput!')

        #Exit Program
        elif choice==4:
            break
            
        else:
            print('Enter a valid Input!')
    else:
        print('Enter a valid Input!')

cur.close()
con.close()   
