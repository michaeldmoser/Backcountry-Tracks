
# Locates a piece of gear in the gear list. The xpath will return the <li> element representing the piece of gear
GEAR_IN_LIST = """xpath=//div[@id="gear_list_view"]/ul/li/div[contains(., "%s")]/.."""

TRIP_BY_NAME = """xpath=//.[@id='trip_list_view']//li[contains(.,'%s')]"""

INVITE_FRIENDS_BUTTON = '''xpath=//div[@class='friends_section']//button[contains(.,'Invite Friend')]'''

INVITE_TEXT_BOX = '''xpath=//textarea[@name='invitees']'''

INVITE_BUTTON = '''Invite'''

INVITED_FRIEND_BY_NAME = '''xpath=//div[@class='friends_section']/div[@class='friends_list']//*[contains(.,'%s')]'''

FRIEND_INVITE_STATUS = '''xpath=//div[@class='friends_section']/div[@class='friends_list']//*[contains(.,'%s')]/..//*[contains(.,'%s')]'''

ACCEPT_TRIP = '''xpath=//.[@id='trip_list_view']//li[contains(.,'%s')]//button[contains(.,'accept')]'''

