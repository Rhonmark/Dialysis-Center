def user_input_validation(username, password):
    if not username and not password:
        return "Both fields must be answered"
    if not username:
        return "Username must be filled"
    if not password:
        return "Password must be filled"
    if len(username) < 8:
        return "Username must be at least 8 characters"
    if len(password) < 6:
        return "Password must be at least 6 characters"
    return 

def login_validation(username, password):
    validation_result = user_input_validation(username, password)
    if validation_result:
        return validation_result
    if username in ['Username must be at least 8 characters']:
        return "Username must be filled"
    if password in ['Password must be at least 6 characters']:
        return "Password must be filled"
    return 

def register_validation(username, password, secret_answer):
    validation_result = user_input_validation(username, password)
    if validation_result:
        return validation_result
    if username in ['Username must be at least 8 characters']:
        return "Username must be filled"
    if password in ['Password must be at least 6 characters']:
        return "Password must be filled"
    if secret_answer in ['Enter secret question answer']:
        return "Secret Answer must be filled"
    return

def forgot_validator(password, confirm_password):
    
    if len(password) < 6 or len(confirm_password) < 6:
        print("Password must be at least 6 characters")
        return 
    if password in ["Enter new password", ""]:
        print("Input cannot be missing...")
        return
    if confirm_password in ["Confirm new password", ""]:
        print("Input cannot be missing...")
        return
    if password != confirm_password:
        print("Confirm your password...")
        return
    
    return None

def null_validator(username, password, secret_answer):
    fields = {
        username: "Username must be at least 8 characters or cannot be empty!",
        password: "Password must be at least 6 characters or cannot be empty!",
        secret_answer: "Secret Answer must be filled!"
    }
    for field, message in fields.items():
        if field in ["", message]:
            print(message)
            return True
    return False
