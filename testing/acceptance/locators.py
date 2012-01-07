
# Locates a piece of gear in the gear list. The xpath will return the <li> element representing the piece of gear
GEAR_IN_LIST = """xpath=//div[@id="gear_list_view"]/ul/li/div[contains(., "%s")]/.."""

TRIP_BY_NAME = """xpath=//.[@id='trip_list_view']//li[contains(.,'%s')]"""

INVITE_FRIENDS_BUTTON = '''xpath=//div[@class='friends_section']//button[contains(.,'Invite Friend')]'''

INVITE_TEXT_BOX = '''xpath=//textarea[@name='invitees']'''

INVITE_BUTTON = '''Invite'''

INVITED_FRIEND_BY_NAME = '''xpath=//div[@class='friends_section']/div[@class='friends_list']//*[contains(.,'%s')]'''

FRIEND_INVITE_STATUS = '''xpath=//div[@class='friends_section']/div[@class='friends_list']//*[contains(.,'%s')]/..//*[contains(.,'%s')]'''

ACCEPT_TRIP = '''xpath=//.[@id='trip_list_view']//li[contains(.,'%s')]//button[contains(.,'accept')]'''
IGNORE_TRIP = '''xpath=//.[@id='trip_list_view']//li[contains(.,'%s')]//button[contains(.,'ignore')]'''


REGISTRATION_LAST_NAME = '''xpath=//form[@id='register-form']//input[contains(@title,'Last Name')]'''
REGISTRATION_FIRST_NAME = '''xpath=//form[@id='register-form']//input[contains(@title,'First Name')]'''
REGISTRATION_EMAIL = '''xpath=//form[@id='register-form']//input[contains(@title,'Email')]'''
REGISTRATION_PASSWORD = '''xpath=//form[@id='register-form']//input[contains(@title,'New Password')]'''
REGISTRATION_CONFIRM_PASSWORD = '''xpath=//form[@id='register-form']//input[contains(@title,'Confirm Password')]'''
REGISTRATION_BIRTH_YEAR = '''xpath=//form[@id='register-form']//select[contains(@name,'year')]'''
REGISTRATION_BIRTH_DAY = '''xpath=//form[@id='register-form']//select[contains(@name,'day')]'''
REGISTRATION_BIRTH_MONTH = '''xpath=//form[@id='register-form']//select[contains(@name,'month')]'''

VIEW_GEAR_SECTION = '''xpath=//a[@href='#gear_tab']'''
SELECT_GEAR = '''Select gear'''
GEAR_INVENTORY_SCREEN = '''xpath=//*[@id='add_personal_gear']'''
GEAR_INVENTORY_ITEM_BY_NAME = '''xpath=//*[@id='add_personal_gear']/ul/li[contains(.,'%s')]'''
TRIP_PERSONAL_GEAR_LIST = '''xpath=//*[@id='trip_personal_gear']'''


