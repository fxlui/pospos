# imnotpopo 16/05/18

# Importing the necessary modules used in the program
import sys, time, operator, sip, itertools, datetime, hashlib, re, math
from functools import partial
from PyQt5 import uic, QtCore, QtWidgets
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtWidgets import (QWidget, QApplication, QMessageBox)
from PyQt5.QtWebEngineWidgets import QWebEngineView
userlist = []
generated = False

def loadDB(dbfile):
    # A generic function to load database from given .db file
    import sqlite3, os
    from sqlite3 import Error
    if os.path.exists(dbfile) == True: # 1 - Check if file exists
        try: # 2 - Try to connect to database
            dbname = sqlite3.connect(dbfile)
        except Error as e: # 2 - If error occurs, print error and return error type
            print(e)
            return "Error 1"
            self.openHelp(101)
        return dbname
    else: # 1 - If not show error and return error type
        return "Error 2"
        self.openHelp(101)

class Ui(QWidget):
    def connectSG(self, obj, sig, function):
        # Connect signals to functions & try to disconnect existing connections (if any)
        objfull = operator.attrgetter(obj+"."+sig)(self)
        funcfull = operator.attrgetter(function)(self)
        try: objfull.disconnect()
        except Exception: pass
        objfull.connect(funcfull)

### INITALIZATION OF LOGIN SCREEN
    def __init__(self):
        super(Ui, self).__init__()
        uic.loadUi('ui/login.ui', self)
        # Connect functions using self.connectSG
        self.connectSG("loginb","clicked","Login")
        self.connectSG("uidbox","textEdited","newTitle")
        self.connectSG("pwdbox","textEdited","newTitle")
        self.show()
        # Declare global variables
        # -- "currentwindow" is used throughout the program to
        # -- allow it to detect the current function.
        global currentwindow, udbconnect
        currentwindow = 0
        udbconnect = loadDB("db/user.db") # Load user database(user.db)
        # If error occurs, disable Login function and show error type
        if udbconnect == "Error 1":
            self.title.setText("Database Error")
            self.title.setStyleSheet("color: red;")
            self.loginb.setEnabled(False)
            self.uidbox.setEnabled(False)
            self.pwdbox.setEnabled(False)
        elif udbconnect == "Error 2":
            self.title.setText("No Database File")
            self.title.setStyleSheet("color: red;")
            self.loginb.setEnabled(False)
            self.uidbox.setEnabled(False)
            self.pwdbox.setEnabled(False)
        else:
            # If connection succeessful, append users info to userlist
            userlist.clear()
            cur = udbconnect.cursor()
            cur.execute("SELECT * FROM Users")
            rows = cur.fetchall()
            for row in rows:
                userlist.append(row)
        global settpm,powerpm,helppm,returnpm
        settpm = QPixmap("img/setting.png")
        powerpm = QPixmap("img/power.png")
        helppm = QPixmap("img/help.png")
        returnpm = QPixmap("img/return.png")

    def newTitle(self):
        # Changes the title to "Login" after input is changed
        self.title.setText("Login")
        self.title.setStyleSheet("color: black;")
        self.loginb.setEnabled(True)

### BELOW ARE FUNCTIONS USED THROUGHOUT THE PROGRAM

## KEYPRESS: BINDS KEYBOARD INPUT TO FUNCTIONS
    def keyPressEvent(self, qKeyEvent):
        # Connect Enter Key to Login function
        if qKeyEvent.key() == QtCore.Qt.Key_Return \
        and currentwindow == 0 and self.loginb.isEnabled() == True:
            self.Login()
        # Connect Enter Key to Add to cart function
        if qKeyEvent.key() == QtCore.Qt.Key_Return \
        and currentwindow == 99:
            self.addItem(itemid_arg)
        if qKeyEvent.key() == QtCore.Qt.Key_Escape \
        and currentwindow == 99:
            self.CoItemBuy(False)
        if qKeyEvent.key() == QtCore.Qt.Key_Return \
        and currentwindow == 4:
            self.Payment()

### LOGIN DETAILS VALIDATION
    def Login(self):
        uid = str(self.uidbox.text())
        pwd = str(self.pwdbox.text())
        hashpwd = hashlib.sha256(pwd.encode('ascii')).hexdigest() # Encode input with SHA-256
        usercur = udbconnect.cursor() # Compare input with database
        usercur.execute("""SELECT * FROM Users WHERE Users.Username = ?""",(uid,))
        rows = usercur.fetchall()
        if len(rows) != 1:
            self.title.setText("Incorrect Details")
            self.title.setStyleSheet("color: red;")
            self.uidbox.clear()
            self.pwdbox.clear()
            return
        else:
            user = rows[0]
        if uid == user[1] and hashpwd == user[2]:
            self.title.setText("Success")
            self.title.setStyleSheet("color: green;")
            self.uidbox.clear()
            self.pwdbox.clear()
            pwd = ""
            if user[3] == 1:
                self.Main(user[0],1,user[1])
            elif user[3] == 2:
                self.Main(user[0],2,user[1])
        elif uid == user[1] and hashpwd != user[2]:
            self.title.setText("Password Error")
            self.title.setStyleSheet("color: red;")
            self.pwdbox.clear()
        else:
            self.title.setText("Incorrect Details")
            self.title.setStyleSheet("color: red;")
            self.uidbox.clear()
            self.pwdbox.clear()

### DASHBOARD FUNCTION
    def Main(self,uid,utype,uname):
        dber = loadDB('db/items.db')
        # If any error occurs during access of items.db, shows error and stops program
        if dber == "Error 1":
            choice = QMessageBox.information(self, 'DB ERROR 1',
                "Stock Database Error.", QMessageBox.Ok,
                 QMessageBox.Ok)
            self.title.setText("Database Error")
            self.title.setStyleSheet("color: red;")
            self.loginb.setEnabled(False)
            return
        elif dber == "Error 2":
            choice = QMessageBox.information(self, 'DB ERROR 2',
                "Cannot locate stock database file.", QMessageBox.Ok,
                 QMessageBox.Ok)
            self.title.setText("Database Error")
            self.title.setStyleSheet("color: red;")
            self.loginb.setEnabled(False)
            return
        else:
            # Loads the items from the database to 
            # display overview of the store
            OOSitem = 0
            soldamount = 0
            cur = dber.cursor()
            cur.execute("SELECT * FROM Items ORDER BY ID DESC LIMIT 1;")
            itemcount = cur.fetchone()
            localitemlist = []
            cur.execute("SELECT * FROM Items")
            rows = cur.fetchall()
            for row in rows:
                localitemlist.append(row)
            for i in range(len(localitemlist)):
                if localitemlist[i][6] == 0:
                    OOSitem += 1
                soldamount += localitemlist[i][7]
            dber.close()
        app.closeAllWindows()
        super(Ui, self).__init__()
        uic.loadUi('ui/admin2.ui', self)
        # Passes the user information as global variables for later use.
        global currentwindow, GBuid, GBuname, GButype
        GBuid = uid
        GBuname = uname
        GButype = utype
        cartlist = []
        currentwindow = 1
        uname = userlist[uid][1]
        self.unamelbl.setText(uname)
        # Bolds text and changes the color of the out of stock count if it is not 0.
        if OOSitem != 0:
            self.ooslbl.setText('''<b>Out Of Stock: <font style="color:red">'''+str(OOSitem))
        else:
            self.ooslbl.setText('''<b>Out Of Stock: </b>None''')
        # Fills in the labels with user details.
        self.signoutbtn.setIcon(QIcon(powerpm))
        self.settingsbtn.setIcon(QIcon(settpm))
        self.helpbtn.setIcon(QIcon(helppm))
        self.connectSG("signoutbtn","clicked","Exit")
        self.helpbtn.clicked.connect(partial(self.openHelp, currentwindow))
        self.incomelbl.setText("<b>Item Sold: </b>"+str(int(soldamount)))
        self.settingsbtn.clicked.connect(lambda: self.Settings(uid,utype))
        self.findbtn.clicked.connect(lambda: self.findItem(uid,utype))
        self.connectSG("stockbtn","clicked","stockControl")
        # Creates auto-update timer for displaying real-time clock.
        self.timer = QtCore.QTimer(self)
        self.timer.timeout.connect(lambda: self.datelbl.setText('\n{dt.day} {dt:%b} {dt.year}\n{dt:%H}:{dt:%M}:{dt:%S}\n'.format(dt = datetime.datetime.now())))
        self.timer.start(1000)
        self.itemcountlbl.setText("<b>Current Items: </b>"+str(itemcount[0]))
        self.datelbl.setText('\n{dt.day} {dt:%b} {dt.year}\n{dt:%H}:{dt:%M}:{dt:%S}\n'.format(dt = datetime.datetime.now()))
        global itemlist
        itemlist = self.loadItemF()
        self.show()
        global generated
        if utype == 2:
            # If user is sales remove "Manage Stock" section
            self.stockbtn.deleteLater()
        elif utype == 1 and generated == False:
            # Auto-generates the report if it's a Sunday.
            if datetime.date.today().weekday() == 6:
                # Saves generated status so the report will not be
                # generate repeatedly every time the function is executed.
                with open("AutoGenerateState",'r') as f:
                    data = f.read()
                if data == "True":
                    generated == True
                    return
                alert = QMessageBox.information(self, 'Alert',
                    "Today is a Sunday. This week's report has been auto-generated.",
                     QMessageBox.Ok, QMessageBox.Ok)
                self.generateReport()
                generated == True # Update generated status
                with open('AutoGenerateState', 'w') as f:
                    f.write("True")
            elif datetime.date.today().weekday() != 6:
                with open('AutoGenerateState', 'w') as f:
                    f.write("False")

### SETTINGS FUNCTION - ACCOUNT MANAGEMENT
    def Settings(self,uid,utype): # Loads the GUI for settings screen
        app.closeAllWindows()
        super(Ui, self).__init__()
        uic.loadUi('ui/settings.ui', self)
        self.returnbtn.setIcon(QIcon(returnpm))
        self.helpbtnST.setIcon(QIcon(helppm))
        self.returnbtn.clicked.connect(lambda: self.Main(uid,utype,0))
        self.confirmbtn_2.clicked.connect(lambda: self.changePW(uid,utype))
        # Disable "create account" function if user type is "sales"
        if utype == 2:
            self.tabWidget_2.setTabEnabled(1, False)
        elif utype == 1:
            self.createbtn_2.clicked.connect(lambda: self.newUSR(uid,utype))
        self.tabWidget_2.currentChanged.connect(self.tabChange)
        global currentwindow
        currentwindow == -1
        self.helpbtnST.clicked.connect(partial(self.openHelp, -1))
        self.show()

    def changePW(self,uid,utype): # Validates the password inputs
        currpwd = str(self.currpwdbox.text())
        newpwd = str(self.newpwdbox_2.text())
        if currpwd == newpwd:
            choice = QMessageBox.information(self, 'Passwords are the same!',
                "Passwords cannot be the same.", QMessageBox.Ok,
                 QMessageBox.Ok)
            self.currpwdbox.clear()
            self.newpwdbox_2.clear()
        elif bool(not newpwd or newpwd.isspace()) == True:
            choice = QMessageBox.information(self, 'New password is empty!',
                "New password is empty.", QMessageBox.Ok,
                 QMessageBox.Ok)
            self.currpwdbox.clear()
            self.newpwdbox_2.clear()
        else:
            hashcurrpwd = hashlib.sha256(currpwd.encode('ascii')).hexdigest()
            correctpwd = userlist[uid][2]
            # Creates new account if password is correct, and inputs are in correct format
            if hashcurrpwd == correctpwd:
                hashpwd = hashlib.sha256(newpwd.encode('ascii')).hexdigest()
                cur = udbconnect.cursor()
                cur.execute("""UPDATE Users SET Password=? WHERE ID=?""",(hashpwd,uid))
                udbconnect.commit()
                choice = QMessageBox.information(self, 'Password changed succeessfully.',
                "Password changed succeessfully.\nLogging out...", QMessageBox.Ok,
                 QMessageBox.Ok)
                self.Exit()
                self.uidbox.setText(GBuname)
            else:
                choice = QMessageBox.information(self, 'Incorrect current password',
                "Incorrect current password.", QMessageBox.Ok,
                 QMessageBox.Ok)
                self.currpwdbox.clear()
                self.newpwdbox_2.clear()

    def newUSR(self,uid,utype): # Reads user input
        newuid = str(self.newusridbox_2.text())
        newusrpwd = str(self.newusrpwdbox_2.text())
        currpwd = str(self.currpwdbox.text())
        hashcurrpwd = hashlib.sha256(currpwd.encode('ascii')).hexdigest()
        correctpwd = userlist[uid][2]
        if hashcurrpwd == correctpwd: # Verifying current password
            pass
        else:
            choice = QMessageBox.information(self, 'Error',
            "Incorrect current password.", QMessageBox.Ok,
            QMessageBox.Ok)
            return
        # Checking user type selected
        if self.adminrb_2.isChecked() == True:
            newtype = 1
        elif self.salesrb_2.isChecked() == True:
            newtype = 2
        else:
            newtype = False
            choice = QMessageBox.information(self, 'Error',
            "Please select a user type.", QMessageBox.Ok,
            QMessageBox.Ok)
            return
        # Checking if username contains space
        if ' ' in newuid:
            newtype = False
            choice = QMessageBox.information(self, 'Error',
            "Username cannot contain space.", QMessageBox.Ok,
            QMessageBox.Ok)
            return
        # Checking if inputs are valid, if yes create account
        if newtype == False:
            return
        else:
            # Check if inputs are empty.
            if bool(not newusrpwd or newusrpwd.isspace()) == True or bool(not newuid or newuid.isspace()):
                alert = QMessageBox.information(self, 'Empty info!',
                    "Username/password is empty.", QMessageBox.Ok,
                 QMessageBox.Ok)
            else:
                hashnewpwd = hashlib.sha256(newusrpwd.encode('ascii')).hexdigest()
                cur = udbconnect.cursor()
                try:
                    newid = int(userlist[-1][0]) + 1
                    # Updates the database with the new password, logs the user out.
                    cur.execute("""INSERT INTO Users(ID,Username,Password,Type) VALUES(?,?,?,?)""",(newid,newuid,hashnewpwd,newtype))
                    udbconnect.commit()
                    choice = QMessageBox.information(self, 'New user created succeessfully.',
                    "New user created succeessfully.", QMessageBox.Ok,
                    QMessageBox.Ok)
                    userlist.clear()
                    cur = udbconnect.cursor()
                    cur.execute("SELECT * FROM Users")
                    rows = cur.fetchall()
                    for row in rows:
                        userlist.append(row)
                except Exception as e:
                    print(e)
                    choice = QMessageBox.information(self, 'User creating failed',
                    "Username already exists.", QMessageBox.Ok,
                    QMessageBox.Ok)
                    self.openHelp(105)
                    self.tabWidget_2.setFocus()
            self.tabChange()

    def tabChange(self):
        # Clears all the sensitive inputs after tab is switched
        self.currpwdbox.clear()
        self.newpwdbox_2.clear()
        self.newusridbox_2.clear()
        self.newusrpwdbox_2.clear()
        self.adminrb_2.setChecked(False)
        self.salesrb_2.setChecked(False)

### FIND & SELL FUNCTION
    def findItem(self,uid,utype): # Load the "Find Item" GUI
        app.closeAllWindows()
        super(Ui, self).__init__()
        uic.loadUi('ui/find.ui', self)
        global currentwindow
        if currentwindow == 4:
            pass
        else:
            global cartlist
            cartlist = []
        currentwindow = 2
        self.helpbtn.clicked.connect(partial(self.openHelp, currentwindow))
        self.returnbtn.setIcon(QIcon(returnpm)) 
        self.helpbtn.setIcon(QIcon(helppm))
        self.searchbar.textChanged.connect(lambda: self.searchItemF(itemlist))
        self.returnbtn.clicked.connect(lambda: self.Main(uid,utype,0))
        itemcounter = 0
        for itemid,count in cartlist:
            itemcounter += count
        self.cartlbl.setText(str(itemcounter)+" item(s) in the shopping cart")
        self.connectSG("nextbutton","clicked","CartReview")
        self.show()
        # Loads the items in the database, gets "itemlist" variable
        global itemlist
        itemlist = self.loadItemF()

    def loadItemF(self):
        # Create layouts corresponding to the number of items in the database
        itemlist=[]
        dber = loadDB('db/items.db')
        if dber == "Error 1": # If error occurs, show error
            choice = QMessageBox.information(self, 'DB ERROR 1',
                "Database Error.", QMessageBox.Ok,
                 QMessageBox.Ok)
            return
        elif dber == "Error 2":
            choice = QMessageBox.information(self, 'DB ERROR 2',
                "Cannot find database file.", QMessageBox.Ok,
                 QMessageBox.Ok)
            return
        else: # connection succeessful
            pass
        cur = dber.cursor()
        cur.execute("SELECT * FROM Items")
        rows = cur.fetchall()
        for row in rows:
            itemlist.append(row)
        if currentwindow == 1 or currentwindow == 7:
            return itemlist
        dber.close()
        rowNum = int(float(int(itemlist[-1][0])/3)//1) + 1
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        for i in range(1, rowNum+1):
            layout = QtWidgets.QHBoxLayout()
            layout.setObjectName("rowlayout"+str(i))
            self.verticalLayout.addLayout(layout)
            setattr(self, "rowlayout"+str(i), layout)
        for item in itemlist:
            self.scrollItem(item)
        return itemlist

    def scrollItem(self, item):
        # This function is used to calculate the number of rows needed, and
        # to create buttons corresponding to the items in the database.
        try: self.loadinglbl.deleteLater()
        except Exception: pass
        itemid = item[0]
        try:
            item[8]
            ifSearch = True
        except Exception:
            ifSearch = False
        if ifSearch == False:
            rownum, loca = divmod(itemid/3, 1)
        elif ifSearch == True:
            rownum, loca = divmod(item[8]/3, 1)
        if loca == 0:
            rownum = rownum - 1
        rowname = "rowlayout" + str(int(rownum)+1)
        row = getattr(self, rowname)
        # PYQT code to create and stylize a button
        button = QtWidgets.QToolButton()
        button.setToolButtonStyle(QtCore.Qt.ToolButtonTextUnderIcon)
        sizePolicy = QtWidgets.QSizePolicy(QtWidgets.QSizePolicy.Expanding, QtWidgets.QSizePolicy.Fixed)
        button.setSizePolicy(sizePolicy)
        button.setIcon(QIcon(QPixmap("img/item/"+str(itemid)+"-fs8.png")))
        button.setIconSize(QtCore.QSize(120,120))
        button.setMinimumSize(QtCore.QSize(0, 200))
        button.setStyleSheet(".QToolButton {\n"
"  padding: 10px;\n"
"  font-size: 13pt;\n"
"  border: 1px solid #686868;\n"
"  border-radius: 4px;\n"
"  color: rgba(2,2,2,0.9);\n"
"  text-align: center;\n"
"  background: #efefef;\n"
"  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1, stop: 0 #FFFFFF, stop: 1 #E0E0E0);\n"
"}"
".QToolButton:hover {\n"
"  background-color: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,stop: 0 #efefef, stop: 1 #d1d1d1);\n"
"}"
)
        button.setText(item[1])
        # Connects the button to CoItemBuy function
        try: button.clicked.disconnect()
        except Exception: pass
        button.clicked.connect(partial(self.CoItemBuy,itemid))
        row.addWidget(button)

    def clearLayout(self, layout): # Function for deleting layout
        if layout is not None:
            while layout.count():
                item = layout.takeAt(0)
                widget = item.widget()
                if widget is not None:
                    widget.deleteLater()
                else:
                    self.clearLayout(item.layout())
            sip.delete(layout)

    def searchItemF(self, itemlist):
        # Searchs the database and returns search results
        keyword = str(self.searchbar.text())
        if keyword == "" or keyword.isspace() == True:
            self.clearLayout(self.verticalLayout)
            self.loadItemF()
            return
        else:
            pass
        result_list = []
        # Search in the list using regex expression
        for item in itemlist:
            searchObj = re.search(r'.*{0}.*'.format(keyword), item[1], re.M|re.I)
            if searchObj:
                result_list.append(item)
        result_list = list(k for k,_ in itertools.groupby(result_list))
        listnum = len(result_list)
        for i in range (0, listnum):
            result_list[i] = result_list[i] + (i+1,)
        rowNum = int(float(int(listnum+1)/3)//1) + 1
        # Clears the layout and re-adds the buttons
        self.clearLayout(self.verticalLayout)
        self.verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        self.verticalLayout.setContentsMargins(0, 0, 0, 0)
        self.verticalLayout.setObjectName("verticalLayout")
        for i in range(1, rowNum+1):
            layout = QtWidgets.QHBoxLayout()
            layout.setObjectName("rowlayout"+str(i))
            self.verticalLayout.addLayout(layout)
            setattr(self, "rowlayout"+str(i), layout)
        for item in result_list:
            self.scrollItem(item)

    def CoItemBuy(self, itemid):
        # Enables/disables the selecting window based on status of the details screen
        if itemid == False:
            global currentwindow
            currentwindow = 3
            self.close()
            Flag = True
            self.returnbtn.setEnabled(Flag)
            self.searchbar.setEnabled(Flag)
            self.scrollArea.setEnabled(Flag)
            self.nextbutton.setEnabled(Flag)
            itemcounter = 0
            totalprice = 0
            for item in cartlist:
                itemcounter += item[1]
                totalprice += item[1] * itemlist[item[0]][4]
            self.cartlbl.setText(str(itemcounter)+" item(s) in the shopping cart \n$"\
                +str(math.ceil(totalprice*100)/100)+" total currently")
        else:
            Flag = False
            self.returnbtn.setEnabled(Flag)
            self.searchbar.setEnabled(Flag)
            self.scrollArea.setEnabled(Flag)
            self.nextbutton.setEnabled(Flag)
            self.ItemBuy(itemid)

    def ItemBuy(self, itemid): # Loads the item detail GUI
        super(Ui, self).__init__()
        uic.loadUi('ui/buyitem.ui', self)
        self.helpbtnB.setIcon(QIcon(helppm))
        self.returnbtnB.clicked.connect(lambda: self.CoItemBuy(False))
        self.addcart.clicked.connect(lambda: self.addItem(itemid))
        self.itemname.setText('''<font size="25pt">'''+itemlist[itemid-1][3]+\
            ''' / <b><font size="30pt">'''+itemlist[itemid-1][1])
        window.setWindowTitle(itemlist[itemid-1][1])
        self.itemdesc.setText(itemlist[itemid-1][2])
        self.itemprice.setText("$"+str(itemlist[itemid-1][4]))
        self.itemimg.setPixmap(QPixmap("img/item/"+str(itemid)+"-fs8.png").scaled(300,300,QtCore.Qt.KeepAspectRatio,transformMode=QtCore.Qt.SmoothTransformation))
        self.qtyBox.setMaximum(itemlist[itemid-1][6])
        self.connectSG("qtyBox","valueChanged","ItemBuyUpdateTotal")
        self.ItemBuyUpdateTotal()
        global currentwindow
        currentwindow = 99
        self.helpbtnB.clicked.connect(partial(self.openHelp, 99))
        global itemid_arg
        itemid_arg = itemid
        self.show()

    def closeEvent(self, event):
        # Ignore "close window/program" request if selecting itemshutdown
        if currentwindow == 99:
            self.CoItemBuy(False)

    def ItemBuyUpdateTotal(self):
        # Update the total price count after user finishes selecting
        total = float(self.itemprice.text().replace("$", "")) * self.qtyBox.value()
        self.itemtotal.setText("$"+str(math.ceil(total*100)/100))

    def addItem(self, itemid): # Adds the selected item to the "cartlist"
        qty = self.qtyBox.value()
        currentstock = int(itemlist[itemid-1][6])
        if currentstock <= 0: # Stop if current is out of stock
            choice = QMessageBox.information(self, 'Out of stock',
                "Item is out of stock.", QMessageBox.Ok,
                 QMessageBox.Ok)
            self.CoItemBuy(False)
            return
        elif currentstock < qty: # Stop if quantity exceeds current stock level
            choice = QMessageBox.information(self, 'Out of stock',
                "Item only has {} left.".format(currentstock), QMessageBox.Ok,
                 QMessageBox.Ok)
            self.CoItemBuy(False)
        else:
            AlreadyAdded = False
            if qty == 0:
                self.CoItemBuy(False)
                return
            for item in cartlist:
                if item[0] == itemid-1: # Checking if item has already been added
                    if (item[1] + qty)>currentstock: # Check if new quantity exceeds current stock level
                        choice = QMessageBox.information(self, 'Out of stock',
                            "Item only has {} left.".format(currentstock), QMessageBox.Ok,
                            QMessageBox.Ok)
                        item[1] = currentstock
                        AlreadyAdded = True
                        self.CoItemBuy(False)
                        return
                    else:
                        pass
                    item[1] = item[1] + qty # Adds new quantity into the list
                    AlreadyAdded = True
                else:
                    pass
            if not AlreadyAdded: # If not already added, add the item normally
                cartlist.append([itemid-1, qty])
            choice = QMessageBox.information(self, 'Item added succeessfully',
                "Item added succeessfully.", QMessageBox.Ok,
                 QMessageBox.Ok)
            self.CoItemBuy(False)
            return

### CHECKOUT FUNCTION
    def CartReview(self): # Loads the shopping cart GUI and adds items to the layout
        app.closeAllWindows()
        super(Ui, self).__init__()
        uic.loadUi('ui/cart.ui', self)
        global currentwindow
        currentwindow = 4
        self.helpbtn.clicked.connect(partial(self.openHelp, currentwindow))
        self.returnbtn.setIcon(QIcon(returnpm))
        self.helpbtn.setIcon(QIcon(helppm))
        verticalLayout = QtWidgets.QVBoxLayout(self.scrollAreaWidgetContents)
        verticalLayout.setContentsMargins(0, 0, 0, 0)
        verticalLayout.setObjectName("verticalLayout")
        itemcounter = 0
        totalprice = 0
        spinboxnum = 0
        for itemid,count in cartlist: # A for loop used to generate the widgets
            layout = QtWidgets.QHBoxLayout()
            itemimg = QtWidgets.QLabel()
            itemimg.setPixmap(QPixmap("img/item/"+str(itemid+1)+"-fs8.png").scaled(65,65,QtCore.Qt.KeepAspectRatio,transformMode=QtCore.Qt.SmoothTransformation))
            itemimg.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(itemimg)
            itemname = QtWidgets.QLabel()
            itemname.setText(itemlist[itemid][1])
            layout.addWidget(itemname)
            itemprice = QtWidgets.QLabel()
            itemprice.setText("$"+str(itemlist[itemid][4]))
            layout.addWidget(itemprice)
            spinboxname = "itemspin"+str(spinboxnum)
            setattr(self, spinboxname, QtWidgets.QSpinBox())
            itemspin = getattr(self, spinboxname)
            itemspin.setMaximum(itemlist[itemid-1][6])
            itemspin.setValue(count)
            try: itemspin.valueChanged.disconnect()
            except Exception: pass
            itemspin.valueChanged.connect(partial(self.SpinValid, spinboxnum))
            layout.addWidget(itemspin)
            itemtotal = QtWidgets.QLabel()
            itemtotal.setText("$"+str(math.ceil((count * itemlist[itemid][4])*100)/100))
            layout.addWidget(itemtotal)
            verticalLayout.addLayout(layout)
            itemcounter += count
            totalprice += count * itemlist[itemid][4]
            spinboxnum += 1
        scrollSize = spinboxnum * 121 + 16
        self.scrollAreaWidgetContents.setMinimumSize(QtCore.QSize(0,scrollSize))
        self.totallbl.setText("Total: "+str(itemcounter)+" item(s) in the cart, $"+str(math.ceil(totalprice*100)/100))
        self.NextBT.clicked.connect(self.Payment)
        self.EmptyButton.clicked.connect(self.emptyCart)
        self.returnbtn.clicked.connect(lambda: self.findItem(GBuid,GButype))
        self.show()

    def SpinValid(self, spinid): # Adjust the number of items based on user input
        spinbox = getattr(self, "itemspin"+str(spinid))
        count = spinbox.value()
        itemid = cartlist[spinid][0]
        stocknum = itemlist[itemid][6]
        if count == 0: # Delete item if item count is set to 0
            choice = QMessageBox.question(self, 'Are you sure you want to remove this item?',
                '''Are you sure you want to remove "'''+itemlist[itemid][1]+'''" ?''', QMessageBox.Ok,
                 QMessageBox.Cancel)
            if choice == QMessageBox.Cancel:
                spinbox.setValue(count+1)
                return
            else:
                for i in range(0,len(cartlist)):
                    if cartlist[i][0] == itemid:
                        cartlist.pop(i)
                        break
                self.CartReview()
        elif count > stocknum: # Stop when item count exceeds available stock
            choice = QMessageBox.information(self, 'No more stock!',
                itemlist[itemid][1]+" only has "+str(stocknum)+" left.", QMessageBox.Ok)
            spinbox.setValue(stocknum)
            return
        else: # If everything is OK continue as normal
            for item in cartlist:
                if item[0] == itemid:
                    item[1] = count
            self.CartReview() # Return

    def emptyCart(self): # Empties the shopping cart based on user input
        choice = QMessageBox.question(self, 'Are you sure you want to empty cart?',
                '''Are you sure you want to empty all the items in the cart?''', QMessageBox.Ok,
                 QMessageBox.Cancel)
        if choice == QMessageBox.Cancel:
            return
        elif choice == QMessageBox.Ok:
            global cartlist
            cartlist.clear()
            self.findItem(GBuid,GButype)
        else:
            pass

    def Payment(self): # Loads the payment GUI
        if len(cartlist) == 0:
            alert = QMessageBox.information(self, 'No items selected.',
                '''No items selected.''', QMessageBox.Ok)
            return
        app.closeAllWindows()
        super(Ui, self).__init__()
        uic.loadUi('ui/payment.ui', self)
        self.returnbtn.setIcon(QIcon(returnpm))
        self.helpbtn.setIcon(QIcon(helppm))
        totalprice = 0
        for i in range(len(cartlist)): # Add the items from cartlist to the table
            rowPosition = self.reviewtable.rowCount()
            self.reviewtable.insertRow(rowPosition)
            self.reviewtable.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(itemlist[cartlist[i][0]][0])))
            self.reviewtable.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(str(itemlist[cartlist[i][0]][1])))
            self.reviewtable.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem("$"+str(itemlist[cartlist[i][0]][4])))
            self.reviewtable.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(str(cartlist[i][1])))
            self.reviewtable.setItem(rowPosition , 4, QtWidgets.QTableWidgetItem(\
                "$"+str(math.ceil((cartlist[i][1] * itemlist[cartlist[i][0]][4])*100)/100)))
            totalprice += (cartlist[i][1] * itemlist[cartlist[i][0]][4])
        self.reviewtable.setRowCount(len(cartlist))
        self.finalpricelbl.setText("$"+str(math.ceil(totalprice*100)/100))
        self.returnbtn.clicked.connect(self.CartReview)
        self.finalbtn.clicked.connect(self.Checkout)
        global currentwindow
        currentwindow = 5
        self.helpbtn.clicked.connect(partial(self.openHelp, currentwindow))
        self.show()

    def Checkout(self): # Loads the checkout finish GUI
        from random import randint
        app.closeAllWindows()
        super(Ui, self).__init__()
        uic.loadUi('ui/checkout.ui', self)
        self.helpbtn.setIcon(QIcon(helppm))
        global currentwindow
        currentwindow = 6
        self.helpbtn.clicked.connect(partial(self.openHelp, currentwindow))
        filename = '{}'.format(\
            datetime.datetime.now().strftime("%d%m%Y-%H%M%S-")+str(randint(100, 999)))
        self.finishbtn.clicked.connect(lambda: self.Main(GBuid,GButype,GBuname))
        saledb = loadDB('db/sales.db')  # Store details in sales.db
        error = False
        if saledb == "Error 1": # If error occurs, show error
            choice = QMessageBox.information(self, 'DB ERROR 1',
                "Database Error.", QMessageBox.Ok,
                 QMessageBox.Ok)
            error = True
        elif saledb == "Error 2":
            choice = QMessageBox.information(self, 'DB ERROR 2',
                "Cannot find database file.", QMessageBox.Ok,
                 QMessageBox.Ok)
            error = True
        else:
            pass
        dber2 = loadDB('db/items.db') # Connects to items.db
        if dber2 == "Error 1":
            choice = QMessageBox.information(self, 'DB ERROR 1',
                "Database Error.", QMessageBox.Ok,
                 QMessageBox.Ok)
            error = True
        elif dber2 == "Error 2":
            choice = QMessageBox.information(self, 'DB ERROR 2',
                "Cannot find database file.", QMessageBox.Ok,
                 QMessageBox.Ok)
            error = True
        else:
            pass
        if error == True: # If errors occur during accessing, returns to the last function
            self.Payment()
            return
        cur = saledb.cursor()
        cur2 = dber2.cursor()
        itemid = ""
        totalprice = 0
        for i in range(len(cartlist)): # Add the item details into the HTML string, which will be used to generate PDF
            itemid += str(itemlist[cartlist[i][0]][0]) + "-" + str(cartlist[i][1]) + ","
            countstock = (cartlist[i][1])
            itemstock = itemlist[cartlist[i][0]][6] - countstock
            itemsold = itemlist[cartlist[i][0]][7] + countstock
            cur2.execute('''update Items set StockLeft=? , UnitSold=? where ID == ?''',\
                (itemstock, itemsold, itemlist[cartlist[i][0]][0]))
            totalprice += (cartlist[i][1] * itemlist[cartlist[i][0]][4])
        date = datetime.datetime.now().strftime("%d/%m/%Y")
        time = datetime.datetime.now().strftime("%H:%M:%S")
        cur.execute("""INSERT INTO Sales(SaleID,ItemID,Date,Time,Total,SaleUser) VALUES(?,?,?,?,?,?)""",\
            (filename,itemid,date,time,str(math.ceil(totalprice*100)/100),GBuid))
        saledb.commit()
        dber2.commit()
        dber2.close()
        saledb.close()
        self.show()
        self.buyReceipt(filename)

    def buyReceipt(self, filename): # Generates the receipt as a pdf file in /receipts
        import pdfreceipt
        with open('receiptHTML.txt', 'r') as HTMLfile:
            HTMLstring = HTMLfile.read()
        totalprice = 0
        for i in range(len(cartlist)): # Add the item details into the HTML string, which will be used to generate PDF
            itemid = str(itemlist[cartlist[i][0]][0])
            itemname = str(itemlist[cartlist[i][0]][1])
            itemcost = "  $"+str(itemlist[cartlist[i][0]][4])
            itemqty = str(cartlist[i][1])
            itemtotal = "  $"+str(math.ceil((cartlist[i][1] * itemlist[cartlist[i][0]][4])*100)/100)
            HTMLtable = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".\
            format(itemid, itemname, itemcost, itemqty, itemtotal)
            HTMLstring += HTMLtable
            totalprice += (cartlist[i][1] * itemlist[cartlist[i][0]][4])
        HTMLstring += "</tbody></table>"
        HTMLstring = HTMLstring.format(filename,\
            (datetime.datetime.now().strftime("%d/%m/%Y %H:%M:%S")),GBuname,str(math.ceil(totalprice*100)/100))
        pdf = pdfreceipt.pdfpdf() # Generates PDF using imported "pyPDF" module
        pdf.add_page()
        pdf.write_html(HTMLstring)
        pdf.output("receipts/RECEIPT_"+filename+".pdf", 'F')
        alert = QMessageBox.information(self, 'Receipt generated.',
                '''Receipt generated at "{}". \nOpen receipt?'''.format("receipts/RECEIPT_"+filename+".pdf"), QMessageBox.Close, QMessageBox.Open)
        if alert == QMessageBox.Open:
            import subprocess, os # Detects the OS platform and opens the PDF file
            directory = os.getcwd()
            filepath = directory + "/receipts/RECEIPT_"+filename+".pdf"
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', filepath))
            elif os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                subprocess.call(('xdg-open', filepath))
            pass
        else:
            pass

### STOCK CONTROL FUNCTION
    def stockControl(self): # Loads the stock control GUI
        app.closeAllWindows()
        super(Ui, self).__init__()
        uic.loadUi('ui/stock.ui', self)
        self.helpbtn.setIcon(QIcon(helppm))
        global currentwindow, itemlist
        currentwindow = 7
        self.helpbtn.clicked.connect(partial(self.openHelp, currentwindow))
        itemlist = self.loadItemF()
        for i in range(len(itemlist)):
            rowPosition = self.itemtable.rowCount()
            self.itemtable.insertRow(rowPosition)
            self.itemtable.setItem(rowPosition , 0, QtWidgets.QTableWidgetItem(str(itemlist[i][1])))
            self.itemtable.setItem(rowPosition , 1, QtWidgets.QTableWidgetItem(str(itemlist[i][5])))
            self.itemtable.setItem(rowPosition , 2, QtWidgets.QTableWidgetItem(str(itemlist[i][4])))
            self.itemtable.setItem(rowPosition , 3, QtWidgets.QTableWidgetItem(str(itemlist[i][6])))
            self.itemtable.setItem(rowPosition , 4, QtWidgets.QTableWidgetItem(str(itemlist[i][7])))
            self.itemtable.setRowCount(i+1)
        self.itemtable.cellDoubleClicked.connect(self.stockDetails)
        self.itemtable.setRowCount(len(itemlist))
        self.returnbtn.setIcon(QIcon(returnpm))
        self.returnbtn.clicked.connect(partial(self.Main,GBuid,GButype,GBuname))
        self.reportbtnB.clicked.connect(self.generateReport)
        self.show()

    def stockDetails(self, row, column): # Loads the item details GUI
        app.closeAllWindows()
        super(Ui, self).__init__()
        uic.loadUi('ui/stockitem.ui', self)
        self.helpbtnB.setIcon(QIcon(helppm))
        global currentwindow
        currentwindow = 8
        self.helpbtn.clicked.connect(partial(self.openHelp, currentwindow))
        self.namebox.setText(str(itemlist[row][1]))
        self.namebox.textChanged.connect(partial(self.updateDetails,"name",row))
        self.descbox.setPlainText(str(itemlist[row][2]))
        self.descbox.textChanged.connect(partial(self.updateDetails,"desc",row))
        self.cstockbo.setValue(int(itemlist[row][6]))
        self.cstockbo.valueChanged.connect(partial(self.updateDetails,"cstock",row))
        self.sstockbo.setValue(int(itemlist[row][7]))
        self.ppricebox.setValue(float(itemlist[row][5]))
        self.ppricebox.valueChanged.connect(partial(self.updateDetails,"pprice",row))
        self.spricebox.setValue(float(itemlist[row][4]))
        self.spricebox.valueChanged.connect(partial(self.updateDetails,"sprice",row))
        self.itemimg.setPixmap(QPixmap("img/item/"+str(itemlist[row][0])+"-fs8.png").scaled(200,200,QtCore.Qt.KeepAspectRatio,transformMode=QtCore.Qt.SmoothTransformation))
        self.itemimg.setAlignment(QtCore.Qt.AlignCenter)
        self.titlelbl.setText("Manage <b>Item "+str(itemlist[row][0]))
        global changedlist
        changedlist = []
        self.returnbtnB.clicked.connect(partial(self.updateDetails,False,row))
        self.savebtn.clicked.connect(partial(self.updateDetails,row,row))
        self.show()

    def updateDetails(self, state, itemid):
        # Decides code used based on edit status (see below for explanation)
        if state == False and not changedlist: # if Return is clicked and nothing is changed:
            self.stockControl()
            return
        elif state == False and changedlist and itemid != 99: # if Return is clicked and changes are made:
            alert = QMessageBox.information(self, 'Alert',
                "Do you want to save the changes?", QMessageBox.Ok,
                 QMessageBox.Cancel)
            if alert == QMessageBox.Ok:
                self.updateDetails(itemid,99)
            elif alert == QMessageBox.Cancel:
                self.stockControl()
                return
        elif isinstance(state, int) == True and changedlist: # if changes are made and Save is clicked, update DB:
            dber2 = loadDB('db/items.db')
            if dber2 == "Error 1":
                choice = QMessageBox.information(self, 'DB ERROR 1',
                    "Database Error.", QMessageBox.Ok,
                     QMessageBox.Ok)
                error = True
            elif dber2 == "Error 2":
                choice = QMessageBox.information(self, 'DB ERROR 2',
                    "Cannot find database file.", QMessageBox.Ok,
                     QMessageBox.Ok)
                error = True
            else:
                pass
            if 'error' in locals():
                self.stockControl()
                return
            cur2 = dber2.cursor()
            for changeditem in changedlist: # Pushes the changed information to the database
                if changeditem == "name":
                    newname = self.namebox.text()
                    cur2.execute('''update Items set Name=? where ID == ?''',\
                        (newname, itemlist[state][0]))
                elif changeditem == "desc":
                    newdesc = self.descbox.toPlainText()
                    cur2.execute('''update Items set Description=? where ID == ?''',\
                        (newdesc, itemlist[state][0]))
                elif changeditem == "cstock":
                    newcstock = self.cstockbo.value()
                    cur2.execute('''update Items set StockLeft=? where ID == ?''',\
                        (newcstock, itemlist[state][0]))
                elif changeditem == "pprice":
                    newpprice = math.ceil(float(self.ppricebox.value())*100)/100
                    cur2.execute('''update Items set PurchasePrice=? where ID == ?''',\
                        (newpprice, itemlist[state][0]))
                elif changeditem == "sprice":
                    newsprice = math.ceil(float(self.spricebox.value())*100)/100
                    cur2.execute('''update Items set SoldPrice=? where ID == ?''',\
                        (newsprice, itemlist[state][0]))
            dber2.commit()
            dber2.close()
            choice = QMessageBox.information(self, 'Success',
                    "Stock details updated.", QMessageBox.Ok,
                     QMessageBox.Ok)
            self.stockControl()
            return
        elif isinstance(state, int) == True and not changedlist: # if Save is clicked but nothing is changed:
            self.stockControl()
            return
        else: # add changed item to changedlist
            if not state in changedlist: # Check if already added
                changedlist.append(state)

    def generateReport(self): # Generates the weekly report
        dber = loadDB('db/sales.db')
        saleslist = []
        rangelist = []
        if dber == "Error 1":
            choice = QMessageBox.information(self, 'DB ERROR 1',
                "Stock Database Error.", QMessageBox.Ok,
                 QMessageBox.Ok)
            return
        elif dber == "Error 2":
            choice = QMessageBox.information(self, 'DB ERROR 2',
                "Cannot locate stock database file.", QMessageBox.Ok,
                 QMessageBox.Ok)
            return
        else:
            cur = dber.cursor()
        from datetime import datetime, timedelta
        dt = datetime.now() # Get the current date and calculate the current week
        weekstart = dt - timedelta(days=dt.weekday())
        weekend = weekstart + timedelta(days=6)
        delta = timedelta(days=1)
        d = weekstart
        while d <= weekend:
            datestring = d.strftime("%d/%m/%Y")
            cur.execute("""SELECT * FROM Sales WHERE Sales.Date = ?""",(datestring,))
            rows = cur.fetchall()
            for row in rows:
                rangelist.append(row)
            d += delta
        # Old solution: inefficient as goes through entire list
        '''for sale in saleslist:
            date = sale[2]
            delta = timedelta(days=1)
            d = weekstart
            while d <= weekend:
                if d.strftime("%d/%m/%Y") == date:
                    rangelist.append(sale)
                d += delta'''
        if rangelist == []:
            choice = QMessageBox.information(self, 'Alert',
                "No transactions during the current week.", QMessageBox.Ok,
                 QMessageBox.Ok)
            return
        else:
            pass
        dber.close()
        import pdfreceipt # Add the item details into the HTML string, which will be used to generate PDF
        with open('reportHTML-1.txt', 'r') as HTMLfile:
            HTMLstring = HTMLfile.read()
        with open('reportHTML-2.txt', 'r') as HTMLfile:
            HTMLstring2 = HTMLfile.read()
        totalprice = 0
        for i in range(len(rangelist)): # Generating HTML for the first half of report:
            sale = rangelist[i]
            saleid = str(sale[0])
            saledate = str(sale[2])
            saletime = str(sale[3])
            fsaleitem = ""
            saleitems = list(filter(None, [x.strip() for x in str(sale[1]).split(',')]))
            saletotal = "$"+str(sale[4])
            for item in saleitems:
                iteml = list(filter(None,[x.strip() for x in item.split('-')]))
                itemid = int(iteml[0])
                itemname = itemlist[itemid-1][1]
                if len(saleitems) == 1:
                    fsaleitem += itemname + " * " + str(iteml[1])
                    itemcount = 1
                else:
                    itemcount = len(saleitems)
            if itemcount == 1:
                HTMLtable = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".\
                format(saleid, saledate, saletime, fsaleitem, saletotal)
            else:
                # If there are more than 1 item purchased in 1 transaction, 
                # generates an empty row in the table for a cleaner report. 
                item1 = list(filter(None, [x.strip() for x in saleitems[0].split('-')]))
                item1name = itemlist[int(item1[0])-1][1] + " * " + str(item1[1])
                HTMLtable = "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td> </td></tr>".\
                format(saleid, saledate, saletime, item1name)
                for i in range(1,len(saleitems)):
                    currentitem = list(filter(None, [x.strip() for x in saleitems[i].split('-')]))
                    if i == len(saleitems) - 1:
                        HTMLtable += '''<tr><td> </td><td> </td><td> </td><td>{}</td><td>{}</td></tr>'''.\
                        format(itemlist[int(currentitem[0])-1][1] + " * " + str(currentitem[1]), saletotal)
                    else:
                        HTMLtable += '''<tr><td> </td><td> </td><td> </td><td>{}</td><td> </td></tr>'''.\
                        format(itemlist[int(currentitem[0])-1][1] + " * " + str(currentitem[1]))
            HTMLstring += HTMLtable
            totalprice += sale[4]
        HTMLstring += "</tbody></table>"
        HTMLstring = HTMLstring.format(weekstart.strftime("%d %b %Y"),\
            weekend.strftime("%d %b %Y"),str(math.ceil(totalprice*100)/100))
        HTMLstring += HTMLstring2
        # --- Generating HTML for the second half of report: ---
        totalitems = ""
        for sale in rangelist:
            ids = sale[1]
            totalitems += ids
        # - Tallies same items which appear in different transactions.
        itemsale = list(filter(None, [x.strip() for x in totalitems.split(',')]))
        import collections
        counter = collections.Counter(itemsale)
        no_dup_itemsale = [x for n, x in enumerate(itemsale) if x not in itemsale[:n]]
        for items in counter.most_common():
            items = list(items)
            if items[1] != 1:
                no_dup_itemsale.remove(items[0])
                d = items[0][:-1]
                d += str(items[1])
                no_dup_itemsale.append(d)
        totalsold = 0
        totalincome = 0
        for sale in no_dup_itemsale:
            sale = list(filter(None, [x.strip() for x in sale.split('-')]))
            item = itemlist[int(sale[0])-1]
            itemid = item[0]
            itemname = item[1]
            soldstock = sale[1]
            totalsold += int(soldstock)
            stockleft = item[6]
            if int(stockleft) == 0:
                stockleft = """<b>""" + str(stockleft) + "</b>"
            income = (float(item[4]) - float(item[5])) * int(sale[1])
            totalincome += income
            income = str(math.ceil(income*100)/100)
            HTMLstring += "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".\
            format(itemid, itemname, soldstock, stockleft, "$"+income)
        HTMLstring += "</tbody></table>"
        HTMLstring = HTMLstring.format(totalsold,str(math.ceil(totalincome*100)/100))
        HTMLstring += "<p>Generated at " + datetime.now().strftime("%a %d/%m/%Y %H:%M:%S") +\
        "</p><p>Notice: Report might not be up-to-date if not generated on last day of week."
        # --- End of HTML editing, starts to generate PDF using "pyPDF" module ---
        pdf = pdfreceipt.pdfpdf()
        pdf.add_page()
        pdf.write_html(HTMLstring)
        filename = "reports/REPORT_"+weekstart.strftime("%d%m%Y")+"<->"+weekend.strftime("%d%m%Y")+".pdf"
        pdf.output(filename, 'F')
        alert = QMessageBox.information(self, 'Report generated.',
                '''Report generated at "{}". Open Report?'''.format(filename), QMessageBox.Close, QMessageBox.Open)
        if alert == QMessageBox.Open:
            import subprocess, os
            directory = os.getcwd()
            filepath = directory + "/" + filename
            # Detects the OS platform and opens the PDF file
            if sys.platform.startswith('darwin'):
                subprocess.call(('open', filepath))
            elif os.name == 'nt':
                os.startfile(filepath)
            elif os.name == 'posix':
                subprocess.call(('xdg-open', filepath))
            pass
        else:
            pass

## OPENHELP: OPENS ONLINE HELP
    def openHelp(self, helpid):
        import os, webbrowser
        directory = os.getcwd()
        url = "/help/{}.html".format(str(helpid))
        if sys.platform == 'darwin': # For macOS
            url = 'file://' + directory + url
            webbrowser.get().open(url,new=0)
        else:
            webbrowser.open(url,new=0)

    def Exit(self):
        # Exits the program, 
        # closes connections to the database, 
        # empties the current user status.
        global GBuid,GBuname,GButype,port
        GBuid = None
        GBuname = None
        GButype = None
        port = None
        try: udbconnect.close()
        except Exception: pass
        app.closeAllWindows()
        self.__init__()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = Ui()
    sys.exit(app.exec_())