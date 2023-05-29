from flask import request, render_template, Blueprint, session
from datetime import datetime
import random
from models.model_fund_transfer import Beneficiarydetails, Usertranscation, Userdata
import time

usertranscation = Usertranscation()

transfer_ctrl = Blueprint("transfer", __name__, static_folder='static', template_folder='templates')

act_page = 'transfer'

def transfer_funds(account_name, account_number, source): 
    user_session = session.get('name')
    user_session_otp = session.get('otp_valid')
    if not user_session or not user_session_otp:
        #print("In Transfer functuon username is: ", user_found)
        return render_template('index.html')
    else:
        if request.method=='POST':
            accname_in = account_name
            accnumber_in = account_number
            transamount_in = request.form['amount']
            accname_found = Userdata.find_data_one({'Name': accname_in})
            accnumber_found = Userdata.find_data_one({'Accno': accnumber_in})
            current_user_found = Userdata.find_data_one({'userid': user_session})
            current_user_name = current_user_found["Name"]
            current_user_accno = current_user_found["Accno"]
            current_date = datetime.today().strftime('%d-%m-%Y')
            current_time = datetime.today().strftime('%H:%M')
            trans_preffix = str(random.randint(999, 10000))
            trans_suffix = str(datetime.today().strftime('%d%m%Y%H%M'))
            trans_id = trans_preffix + trans_suffix
              

            if not accname_found and not accnumber_found and not transamount_in:
                msg = "Please Enter Valid Details"
                if source == 'onetimetransfer' :
                    return render_template('onetime-transfer.html', active_page = act_page, transfermsg = msg, logedin_user = user_session)
                else:
                    return (transfer(msg))
                
            if not accname_found:
                msg = "Account Name not found"  
                if source == 'onetimetransfer' :
                    return render_template('onetime-transfer.html', active_page = act_page, transfermsg = msg, logedin_user = user_session)
                else:
                    return (transfer(msg))
                                   
            if not accnumber_found:
                    msg = "Account Number not found"
                    if source == 'onetimetransfer' :
                      return render_template('onetime-transfer.html', active_page = act_page, transfermsg = msg, logedin_user = user_session)
                    else:
                      return (transfer(msg))
                      #return render_template('transfer.html', transfermsg = msg, logedin_user = user_session)
            if not transamount_in:
                    msg = "Please enter a valid amount"
                    if source == 'onetimetransfer' :
                      return render_template('onetime-transfer.html', active_page = act_page, transfermsg = msg, logedin_user = user_session)
                    else:
                      return (transfer(msg))
                    
            
            if accnumber_in == current_user_found["Accno"]:
                    msg = "Cannot Transfer to Self"
                    if source == 'onetimetransfer' :
                      return render_template('onetime-transfer.html', active_page = act_page, transfermsg = msg, logedin_user = user_session)
                    else:
                      return (transfer(msg))

        
            if accname_in == accname_found["Name"] and accnumber_in == accnumber_found["Accno"]:
                current_user_before_bal = float(current_user_found["Accbal"])
                if current_user_before_bal < float(transamount_in):
                    msg = "Insufficient Balance"
                    if source == 'onetimetransfer' :
                      return render_template('onetime-transfer.html', active_page = act_page, transfermsg = msg, logedin_user = user_session)
                    else:
                      return (transfer(msg))
            
            if accname_found:
                end_user_account_status = accname_found['Activation_status'] 
                if end_user_account_status == 'Suspended' or end_user_account_status == 'Pending':
                    msg = "Account is " + end_user_account_status + ". Transfer Failed"
                    if source == 'onetimetransfer' :
                        return render_template('onetime-transfer.html', active_page = act_page, transfermsg = msg, logedin_user = user_session)
                    else:
                        return (transfer(msg))
                  
                else:
                        end_user_id = accnumber_found["userid"]
                        end_user_name = accnumber_found["Name"]
                        current_bal = accnumber_found["Accbal"]
                        current_user_acc_number = current_user_found["Accno"]
                        Current_user_after_bal = float(float(current_user_before_bal) - float(transamount_in))
                        Transfer_bal = float(float(current_bal) + float(transamount_in))

                        # End User Balance and Transactions Update
                        end_user_acc = { "Accno": accnumber_in }
                        end_user_new_bal = { "$set": { "Accbal": Transfer_bal } }
                        Userdata.update(end_user_acc, end_user_new_bal)

                        accnumber_found = Userdata.get_data_one({'Accno': accnumber_in})
                        end_user_updated_bal = accnumber_found["Accbal"]

                        col_transactions_enduser= end_user_id + 'transactions'
                        #db_end_user_transactions = Usertranscation.save(transactions_enduser)
                        input_enduser = {"userid":end_user_id,"Name":end_user_name,"Accno":accnumber_in,"TransID":trans_id,"Fromaccname":current_user_name,"Fromaccno":current_user_accno,"Toaccno":accnumber_in,"Amount":transamount_in,"Transtype":"cr","Date":current_date,"Time":current_time,"Accbal":end_user_updated_bal,"Transdate": datetime.now()}
                        
                        usertranscation.save(col_transactions_enduser, input_enduser)
                        
                        #Current user Balance and Transactions Update
                        current_user_acc = { "Accno": current_user_acc_number }
                        current_user_new_bal = { "$set": { "Accbal": Current_user_after_bal } }

                        col_transactions_currentuser= user_session + 'transactions'
                        #db_current_user_transactions = db_name[transactions_currentuser]
                        Userdata.update(current_user_acc, current_user_new_bal)
                        time.sleep(1)
                        current_user_found = Userdata.get_data_one({'userid': user_session})
                        current_user_updated_bal = current_user_found["Accbal"]
                        usertranscation.save(col_transactions_currentuser, {"userid":user_session,"Name":current_user_name,"Accno":current_user_accno,"TransID":trans_id,"Fromaccname":current_user_name,"Fromaccno":current_user_accno, "Toaccno":accnumber_in,"Amount":transamount_in,"Transtype":"dr","Date":current_date,"Time":current_time,"Accbal":current_user_updated_bal,"Transdate": datetime.now()} )
                        return render_template('transfer-sucess.html', active_page = act_page, transamount = transamount_in, accname=accname_in, accnumber = accnumber_in, transcation_id = trans_id, logedin_user = user_session)

def user_benificary_list(found_list, new_list):
    for i in found_list:
                del i['_id']
                for j in i.values():
                    new_list.append(j)
                    #print("type if list is : ", type(beneficiary_list1))
    #print("list 1: ", new_list)
    beneficiary_list = [new_list[x:x+2] for x in range(0, len(new_list), 2)]
    #print("beneficiary_list", beneficiary_list)
    beni_list_join = ['-'.join(sublist) for sublist in beneficiary_list]
    final_beneficiary_list = [beni_list_join[x:x+1] for x in range(0, len(beni_list_join), 1)]
    #print("final_beneficiary_list", final_beneficiary_list)
    return final_beneficiary_list

@transfer_ctrl.route("/onetime-transfer",methods=["POST", "GET"])
def onetime_transfer():    
    user_session = session.get('name')
    user_session_otp = session.get('otp_valid')
    if not user_session or not user_session_otp:
        #print("In Transfer functuon username is: ", user_found)
        return render_template('index.html')
    else:
        user_session = session.get('name')
        act_page = 'transfer'
        #input_userdata = {'userid': user_session}
        #userdata_found = Userdata.get_data(input_userdata)
        return render_template('onetime-transfer.html', active_page = act_page, logedin_user = user_session)

@transfer_ctrl.route("/transfer",methods=["POST", "GET"])
def transfer(transfer_message=''):    
    user_session = session.get('name')
    user_session_otp = session.get('otp_valid')
    if not user_session or not user_session_otp:
        #print("In Transfer functuon username is: ", user_found)
        return render_template('index.html')
    else:
        user_beneficiary_found = Beneficiarydetails.get_user_accno(user_session)
        if not user_beneficiary_found:
            #print("No Record Found")
            msg = 'No Beneficiary Found for ' +  user_session + '. Please add Beneficiary or use one time Transfer.'
            return render_template('transfer.html', active_page = act_page, messages1 = msg, logedin_user = user_session)
        else:
            beneficiary_list1 = []
            msg = 'Please select Account Details to Transfer'
            final_beneficiary_list = user_benificary_list(user_beneficiary_found, beneficiary_list1 )
            return render_template('transfer.html', active_page = act_page, transfermsg = transfer_message, data = final_beneficiary_list, messages = msg, logedin_user = user_session)

@transfer_ctrl.route("/add-beneficiary",methods=["POST", "GET"])
def add_beneficiary():    
    user_session = session.get('name')
    user_session_otp = session.get('otp_valid')
    if not user_session or not user_session_otp:
        #print("In Transfer functuon username is: ", user_found)
        return render_template('index.html')
    else:
        user_session = session.get('name')
        return render_template('add-beneficiary.html', active_page = act_page, logedin_user = user_session)

@transfer_ctrl.route("/api/v1/add-beneficiary",methods=["POST", "GET"])
def api_add_beneficiary(): 
    user_session = session.get('name')
    user_session_otp = session.get('otp_valid')
    if not user_session or not user_session_otp:
        #print("In Transfer functuon username is: ", user_found)
        return render_template('index.html')
    else:
        if request.method=='POST':
            accname_in = request.form['accname']
            accnumber_in = request.form['accno']
            #accname_found = db_userdata.find_one({'Name': accname_in})
            accname_found = Userdata.get_userdata('Name', accname_in )
            accnumber_found = Userdata.get_userdata('Accno', accnumber_in)
            
            current_user_found = Userdata.get_data_one({'userid': user_session})
            #current_user_name = current_user_found["Name"]
          
            current_user_accno = current_user_found["Accno"]
            if not accname_found and not accnumber_found:
                msg = "Please Enter Valid Details"
                return render_template('add-beneficiary.html', active_page = act_page, add_beneficiary_msg = msg, logedin_user = user_session)

            if not accname_found:
                msg = "Account Name not found"
                return render_template('add-beneficiary.html', active_page = act_page, add_beneficiary_msg = msg, logedin_user = user_session)
            if not accnumber_found:
                 msg = "Account Number not found"
                 return render_template('add-beneficiary.html', active_page = act_page, add_beneficiary_msg = msg, logedin_user = user_session)
            if current_user_accno == accnumber_found["Accno"]:
                 print("Current user account found is: ", current_user_accno)
                 print("Account number of 3rd party : ", accnumber_found["Accno"] )
                 msg = "Cannnot Add Self Acc as Beneficiary"
                 return render_template('add-beneficiary.html', active_page = act_page, add_beneficiary_msg = msg, logedin_user = user_session)
            
            if accname_in == accname_found["Name"] and accnumber_in == accnumber_found["Accno"]:
                user_beneficary_found = Beneficiarydetails.get_data_accno('userid', user_session, 'Accno', accnumber_in)
                #print("Current user benificary found is: ", user_beneficary_found)
                if user_beneficary_found:
                    msg =  accnumber_in + " is already added as Beneficiary"
                    return render_template('add-beneficiary.html', active_page = act_page, add_beneficiary_msg = msg, logedin_user = user_session)
                else:
                    #update current user Beneficiary list
                    Beneficiarydetails.save({"userid":user_session,"Name":accname_in,"Accno":accnumber_in})
                    return render_template('add-beneficiary-sucess.html', active_page = act_page, accname=accname_in, accnumber = accnumber_in, logedin_user = user_session)
    return render_template('add-beneficiary.html', logedin_user = user_session)


@transfer_ctrl.route("/delete-beneficiary",methods=["POST", "GET"])
def delete_beneficiary(): 
    user_session = session.get('name')
    user_session_otp = session.get('otp_valid')
    if not user_session or not user_session_otp:
        #print("In Transfer functuon username is: ", user_found)
        return render_template('index.html')
    else:
        user_beneficiary_found = Beneficiarydetails.get_user_accno(user_session)
        #user_beneficiary_found_list = list(user_beneficiary_found)
        #usr_data = user_data_found["TransID"]
        if not user_beneficiary_found:
            #print("No Record Found")
            msg = 'No Beneficiary Found for ' +  user_session + '. Please add Beneficiary or use one time Transfer.'
            return render_template('delete-beneficiary.html', active_page = act_page, messages1 = msg, logedin_user = user_session)
        else:
            beneficiary_list1 = []
            print("In delete benificary")
            msg = 'Please select Beneficiary to delete'
            final_beneficiary_list = user_benificary_list(user_beneficiary_found, beneficiary_list1 )
            return render_template('delete-beneficiary.html', active_page = act_page, data = final_beneficiary_list, messages = msg, logedin_user = user_session)

@transfer_ctrl.route("/api/v1/delete-beneficiary",methods=["POST", "GET"])
def api_delete_beneficiary(): 
    user_session = session.get('name')
    user_session_otp = session.get('otp_valid')
    if not user_session or not user_session_otp:
        #print("In Transfer functuon username is: ", user_found)
        return render_template('index.html')
    else:
        if request.method=='POST':
            user_beneficiary_input = request.form.get('Benificary')
            user_confirmation_input = request.form.get("confirmation")
            if user_beneficiary_input == 'Choose Account:':
                msg = 'Please select Beneficiary'
                return render_template('delete-beneficiary.html', active_page = act_page, deletemsg = msg, messages = msg, logedin_user = user_session)
            else:
                user_beneficiary_list = user_beneficiary_input.split("-")
                accname_in = user_beneficiary_list[0]
                accnumber_in = user_beneficiary_list[1]
                print("acc name in :", accname_in)
                print("acc number in :", accnumber_in)
                if user_confirmation_input == 'yes':
                    #print ("Cmd is :", Beneficiarydetails.delete_data(user_session, accnumber_in))
                    Beneficiarydetails.delete_data(user_session, accnumber_in)
                    return render_template('del-beneficiary-sucess.html', active_page = act_page, accname=accname_in, accnumber = accnumber_in, logedin_user = user_session)
                else:
                    msg = "Please type yes"
                    return render_template('delete-beneficiary.html', active_page = act_page, messages = msg, deletemsg = msg, logedin_user = user_session)
    return render_template('delete-beneficiary.html')

        
@transfer_ctrl.route("/api/v1/onetimetransferfund",methods=["POST", "GET"])
def onetime_transfer_funds():
    if request.method=='POST':
        accname_in = request.form['accname']
        accnumber_in = request.form['accno']
        from_source = 'onetimetransfer'
        #transamount_in = request.form['amount']
        return transfer_funds(accname_in, accnumber_in,from_source)

@transfer_ctrl.route("/api/v1/beneficiarytransferfund",methods=["POST", "GET"])

def beneficiary_transfer_funds():
    if request.method=='POST':
        user_beneficiary_input = request.form.get('Benificary')
        user_beneficiary_list = user_beneficiary_input.split("-")
        accname_in = user_beneficiary_list[0]
        accnumber_in = user_beneficiary_list[1]
        from_source = 'beneficiarytransfer'
        return transfer_funds(accname_in, accnumber_in, from_source)

