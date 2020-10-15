from imaplib import IMAP4_SSL
import time
import email
from numpy.random import randint
from twilio.rest import Client
import sys
import json
from pprint import pprint


gmail = IMAP4_SSL('imap.gmail.com',993)


class gmail_imap():

    Username = ""
    Password = ""
    

    def __init__(self,username,password):

        self.Username = username
        self.Password = password
        self.LoginState = False
        self.Change = False
        self.Unseen = False

    def Login(self):
        
        try:
            
            gmail.login(self.Username,self.Password)
            self.LoginState = True
        
        except Exception as e:
            
            self.LoginState = False
            print(str(e))

    def LogOut(self):
       
        try:
            
            gmail.logout()
            self.LoginState = False
        
        except Exception as e:
            
            self.LoginState = False
            print(str(e))       

    def Search_Mailbox(self,mailbox,printB):

        Number_Unseen = 0        
        try:
            
            if self.LoginState is False:
                
                self.Login()
            
            else:      
               
                pass
            
            gmail.select(mailbox)

            typ , data = gmail.search(None,'UnSeen')

            Number_Unseen = len(data[0].split())
            
            if not printB:
                pass
            else:
                print(Number_Unseen)

        except Exception as e:
            print(str(e))

        return Number_Unseen


    def Check_For_Change(self,mailbox,previous_unseen):

        new_unseen =self.Search_Mailbox(mailbox,True)

        if new_unseen != 0:
            
            if new_unseen != previous_unseen:
                print("unseen emails:{}".format(new_unseen))
                
                self.Unseen = True
                self.Change = True
            
            else:
                
                self.Unseen = True
                self.Change = False
                
                print("no change,unseen emails: {}".format(previous_unseen))

        else:
            self.Change = False
            self.Unseen = False
            print("no unseen messages")

    def read_unseen(self,mailbox,ifprint):

        From_Email_ = ""
        subject = ""
        subjects = []
        from_emails = []

        try:
            
            if self.LoginState is False:
                self.Login()
            else:
                pass

            gmail.select(mailbox)    

            rv, data = gmail.search(None, "UnSeen")
            
            if rv != 'OK':
                
                print("No messages found!")
                return

            for num in data[0].split():
                
                rv, data = gmail.fetch(num, '(RFC822)')
                
                if rv != 'OK':
                    
                    print("ERROR getting message", num)
                    return

                msg = email.message_from_bytes(data[0][1])
                hdr = email.header.make_header(email.header.decode_header(msg['Subject']))
                from_addr = email.header.make_header(email.header.decode_header(msg['from']))
                
                subject = str(hdr)
                from_ = str(from_addr).split()
                

                From_ = list(from_[1])
                

                for i in From_:
                    
                    if i == '<' or i == '>':
                        
                        i = None
                    
                    else:
                        
                        From_Email_ = From_Email_ + i

                num_ = list(str(num))
                num__ = ""

                for i in num_:
                    
                    if i == 'b':
                        i = None
                    
                    else:
                        num__ = num__ + i 

                if ifprint != True:
                    
                    pass

                else: 
                    
                    print("email number : {},subject: {}".format(str(num__), subject))
                    print("from address : {}".format(From_Email_))
                    
                    print("")
                    print("")

                from_emails.append(From_Email_)
                subjects.append(subject)

        except Exception as e:

            print(str(e))

        return from_emails , subjects

        

    def ImportantEmail(self , mailbox, ImportantEmailIDArray):
        
        From_Email_Addresses = []

        try:
            
            if self.LoginState is False:
                self.Login()
            else:
                pass

            gmail.select(mailbox)    

            rv, data = gmail.search(None, "UnSeen")
            if rv != 'OK':
                print("No messages found!")
                return

            for num in data[0].split():
                rv, data = gmail.fetch(num, '(RFC822)')
                if rv != 'OK':
                    print("ERROR getting message", num)
                    return

                msg = email.message_from_bytes(data[0][1])
               
                from_addr = email.header.make_header(email.header.decode_header(msg['from']))
                from_ = str(from_addr).split()

                From_ = list(from_[1])
                From_Email_Address = ""

                for i in From_:
                    if i == '<' or i == '>':
                        i = None
                    else:
                        From_Email_Address = From_Email_Address + i
                
                
                j = 0

                for i in ImportantEmailIDArray:
                    
                    if i == From_Email_Address:
                        From_Email_Addresses.append(From_Email_Address)
                    else:
                        pass
                    j = j + 1

                if len(From_Email_Addresses) != None or len(From_Email_Addresses) != 0:

                    for i in From_Email_Addresses:
                        print("from email id : {}".format(i))
                else:
                    print("no important emails")

        except Exception as e:

            print(str(e))

        return From_Email_Addresses 


class JSONhandler():

    def __init__(self,file_name):

        self.FileName = file_name

    def WriteData(self,data):

        try:
            
            with open(self.FileName,"w") as write_file:

                json.dump(data,write_file)

        except Exception as e:

            print(str(e))

    def ReadData(self):

        data = ""
  
        try:
           
            with open(self.FileName) as file:

                    data = json.load(file)

        except Exception as e:

            print(str(e))

        return data

    def GenerateData(self,username,verification,phonenumber):
        
        data_dictionary = {
        "username":username,
        "verification":verification,
        "phonenumber":phonenumber,
        
        }

        return data_dictionary

    def GetUserDataFromFile(self):

        data = ""

        phonenumber_ = ""
        

        try:

            data = self.ReadData()

            phonenumber_ = data["phonenumber"]


        except Exception as e:

            print(str(e))

        return phonenumber_

class SMS():

    PhoneNumber = None
    auth = None
    sid = None
    gmail_imap_obj = None

    def __init__(self,phno,AccSID,AccAuth,gmail_imap_obj):

        self.PhoneNumber = phno
        self.Verified = False
        self.auth = AccAuth
        self.sid = AccSID
        self.gmail_imap_obj = gmail_imap_obj
        self.RegisteredNumber = self.PhoneNumber
        

    def create_client_twilio(self):

        twilio_client = Client(self.sid,self.auth)
        return twilio_client

    def verify(self,client):
        
        file_name = "{}-data-file.json".format(self.gmail_imap_obj.Username)

        json_handler = JSONhandler(file_name)

        try:
            
            ver_num = ""
            Ver_Num = [None,None,None,None,None]

            for i in range(len(Ver_Num)):
                Ver_Num[i] = randint(0,9)

            for num in Ver_Num:
                ver_num += str(num)
            
            ver_num = str(ver_num)
            
            body_sms = "your verification number : {}".format(ver_num)

            message = client.messages.create(from_='+447480535431',body=body_sms,to=self.PhoneNumber)
            print(message.sid)

            time.sleep(5)

            input_num = input("enter verification number: ")

            if input_num != None:
                
                if input_num == ver_num:

                    print("verification success")
                    self.Verified = True

                    data = json_handler.GenerateData(self.gmail_imap_obj.Username,
                        self.Verified,self.PhoneNumber)

                    json_handler.WriteData(data)

                else:

                    print("verification failed")
                    self.Verified = False

                    data = json_handler.GenerateData(self.gmail_imap_obj.Username,
                        self.Verified,self.PhoneNumber)

                    json_handler.WriteData(data)
            else:

                print("verification failed")
                self.Verified = False

                data = json_handler.GenerateData(self.gmail_imap_obj.Username,
                        self.Verified,self.PhoneNumber)

                json_handler.WriteData(data)

        except Exception as e:

            print(str(e))

            sys.exit()

    def CheckVerification(self,ifPrint):
        
        file_name = "{}-data-file.json".format(self.gmail_imap_obj.Username)

        data = ""

        try:

            json_handler = JSONhandler(file_name)
            data = json_handler.ReadData()

            #pprint(data)
            
            self.Verified = bool(data["verification"])
            
            Number_ = data["phonenumber"]
            self.RegisteredNumber = Number_

            if self.RegisteredNumber == str(self.PhoneNumber):

                self.Verified = True

            else:

                self.Verified = False

        except Exception as e:

            print(str(e))

        
        if ifPrint == True:

            pprint("VERIFICATION STATUS : {}".format(data["verification"]))

        else:

            pass


    def send_sms_unseen_emails(self,client,mailbox):
        
        try:

            #self.CheckVerification(False)
            self.verified = True

            gmail_imap_client = self.gmail_imap_obj
            
            from_emails_array , subject_array = gmail_imap_client.read_unseen(mailbox,False)


            if self.Verified == True:

                if len(from_emails_array) != None or len(from_emails_array) != 0:
                
                    for email_id , subject in zip(from_emails_array,subject_array):

                        body_sms = "email from {} , subject of the email is {} ".format(email_id,subject)
                        message = client.messages.create(from_='+447480535431',body=body_sms,to=self.PhoneNumber)
                        
                        print(message.sid)

                else:

                    print("no unseen emails")

            else:

                self.verify(client)
                
                self.CheckVerification(False)

                if self.Verified == True:

                    if len(from_emails_array) != None or len(from_emails_array) != 0: 
                        
                        for email_id , subject in zip(from_emails_array,subject_array):

                            body_sms = "email from {} , subject of the email is {} ".format(email_id,subject)
                            message = client.messages.create(from_='+447480535431',body=body_sms,to=self.PhoneNumber)
                            
                            print(message.sid)

                    elif len(from_email_addresses) is None or len(from_email_addresses) == 0:

                        print("no unseen emails")
                else:

                    sys.exit()

        except Exception as e:

            print(str(e))

            sys.exit()

    def ImportantEmailSMS(self,form_addr_array,client,mailbox):
        
        try:

            self.CheckVerification(False)
            
            gmail_imap_client = self.gmail_imap_obj
            from_email_addresses = gmail_imap_client.ImportantEmail(mailbox,form_addr_array)

            
            if self.Verified == True:

                if len(from_email_addresses) is not None or len(from_email_addresses) != 0:

                    for i in from_email_addresses:
                        
                        body_sms = "email from {}".format(i) +"to your account : {}".format(self.gmail_imap_obj.Username)+"this email id is under your important email id's "
                        message = client.messages.create(from_='+447480535431',body=body_sms,to=self.PhoneNumber)
                    
                        print(message.sid)

                elif len(from_email_addresses) is None or len(from_email_addresses) == 0:

                    print("No important emails")
            
            else:

                print("verification of Phone Number required")
                self.verify(client)

                self.CheckVerification(True)

                if self.Verified != True:

                    sys.exit()

                else:

                    if len(from_email_addresses) is not None or len(from_email_addresses) != 0:

                        for i in from_email_addresses:
                            
                            body_sms = "email from {}".format(i) +"to your account : {}".format(self.gmail_imap_obj.Username)+"this email id is under your important email id's "
                            message = client.messages.create(from_='+447480535431',body=body_sms,to=self.PhoneNumber)
                        
                            print(message.sid)
                    else:

                        print("No important emails")

        except Exception as e:

            print(str(e))

            sys.exit()

    def GetImportantEmailIds(AddImportantEmailIds):

        important_email_id_array = []

        if AddImportantEmailIds == True:

            email_id_to_input = input("enter email id to add to array")

            important_email_id_array.append(email_id_to_input)

        return important_email_id_array

    def StoreImportantEmails(self,important_emails_array,keepPastEmails):

        file_name = "{}-important-emails-file.json".format(self.gmail_imap_obj.Username)
        json_handler = JSONhandler(file_name)

        if keepPastEmails == True:

            data = json_handler.ReadData()
            data = array(data)
            data = data.append(important_emails_array)

            for i , email in zip(len(data),data):

                data = {str(i):str(email)}

                json_handler.WriteData(data)

        else:

            for i , email in zip(len(data),data):

                data = {str(i):str(email)}

                json_handler.WriteData(data)


    def GetImportantEmailIDs(self,ImportantEmailBOOL):

        file_name = "{}-important-emails-file.json".format(self.gmail_imap_obj.Username)
        json_handler = JSONhandler(file_name)

        imporatant_emails_from_json = []

        if ImportantEmailBOOL == True:

            data = json_handler.ReadData()

            for i in data :
                
                imporatant_emails_from_json.append(i)
        else:

            pass

        return imporatant_emails_from_json
        




if __name__ == '__main__':



    lambda_unseen = lambda mailbox,printIF: acc1.Search_Mailbox(mailbox,printIF)
    lambda_create_client = lambda sms: sms.create_client_twilio()

    acc_auth = '7e52bf4397e1f5df708ad82ad1cbec10'
    
    acc_sid = 'ACdeb332f64a8d62aead2ad61bd57b3a2f'
    


    USERNAME = input("enter gmail acc username: ")
    
    PASSWORD = input("enter gmail acc password: ")

    account = gmail_imap(USERNAME,PASSWORD)

    user_file_name = "{}-data-file.json".format(USERNAME)

    user_file_data = JSONhandler(user_file_name)
    
    Load_Previous_Data = input("do you want to load previous data (yes/no): ")

    if Load_Previous_Data == "yes":

        phonenumber_past_data = ""

        try:

            phonenumber_past_data = user_file_data.GetUserDataFromFile()

        except Exception as e:

            print(str(e))

        if phonenumber_past_data == None or phonenumber_past_data == "":

            print("no past data to load!!")

            PHONENUMBER = input("enter phone number: ")

            sms = SMS(phonenumber_past_data,acc_sid,acc_auth,account)

        else:
         
            sms = SMS(phonenumber_past_data,acc_sid,acc_auth,account)


    else:

         PHONENUMBER = input("enter phone number: ")
         
         sms = SMS(PHONENUMBER,acc_sid,acc_auth,account)

    
    important_emails_settings = input("do you want to enable important emails: ")


    important_email_id_array = []

    if important_emails_settings == "True":

        end_adding_emails = False

       

        while str(end_adding_emails == "False"):

            email_id_input = input("enter email id to be added to important email id's: ")
            
            end_adding_emails = input("do you want to add more email id's (True/False): ")

            important_email_id_array.append(email_id_input)


    
    sms.verify(lambda_create_client(sms))

    sms.CheckVerification(False)

    if sms.Verified == True:

        pass 

    else:

        sms.verify(lambda_create_client(sms))
        
        sms.CheckVerification(True)

    #mailbox_input = input("enter mailbox to be used : ")

    mailbox_input = "inbox"
    
    while True:

        if important_emails_settings == "True":

            try:

                sms.ImportantEmailSMS(important_email_id_array,lambda_create_client(sms),mailbox_input,USERNAME)

            except Exception as e:

                print(str(e))

                sys.exit()

        else:

            try:

                sms.send_sms_unseen_emails(lambda_create_client(sms),mailbox_input)

            except Exception as e:

                print(str(e))

                sys.exit()





































































