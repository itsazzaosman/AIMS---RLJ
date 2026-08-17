from core.models import SettingTemplate

template = SettingTemplate.objects.filter(name='new_user_registration').first()
if template:
    template.setting = "Your One-Time Password (OTP) for account activation is: {{ user.confirmation_code }} \n\nYou can enter this code at the following link:\n{{ core_confirm_account_url }}"
    template.save()
    print("Template updated successfully!")
else:
    print("Template not found.")
