"""
Validation.py

This file will serve to control the instagram website through the webDriver
"""

from explicit import waiter, XPATH
from time import sleep

from Common import Constants, StringResources
from Library import Browser

class InstagramController:
    def __init__(self):
        self.Browser = None

    ''' 
    Initialize the instagram controller, and webDriver and save the instance
    '''
    def initialize_controller(self):
         self.Browser = Browser.Browser()
         self.Browser.initialize_browser()

    '''
    Stop the controller and quit the webdriver browser
    '''
    def stop_controller(self):
        if self.Browser is not None:
            self.Browser.stop_browser()
    
    '''
    Log into instagram using the input username and password
    '''
    def do_login(self, username, password):
        try:
            self.Browser.get_website(Constants.INSTAGRAM_LOGIN_URL)
            sleep(Constants.INSTAGRAM_IDDLE_WAIT_SECONDS)

            # Login with the input credentials
            self.Browser.find_element_by_name(Constants.INSTAGRAM_USERNAME_FIELD).send_keys(username)
            self.Browser.find_element_by_name(Constants.INSTAGRAM_PASSWORD_FIELD).send_keys(password)
            
            self.Browser.find_element_by_tag(Constants.INSTAGRAM_LOGIN_FORM_NAME).submit()
        
            # Sleep needed to put in the 2 factor code
            print(StringResources.INSTAGRAM_TWO_FACTOR_AUTH_MESSAGE)
            sleep(Constants.INSTAGRAM_LOGIN_WAIT_SECONDS)
        
            # Click both not now buttons
            self.Browser.find_elements_by_x_path(Constants.INSTAGRAM_NOT_NOW_BUTTON_XPATH, 1).click()    
            self.Browser.find_elements_by_x_path(Constants.INSTAGRAM_NOT_NOW_BUTTON_XPATH, 1).click()
            
            # Wait for the user dashboard page to load
            self.Browser.web_driver_wait(Constants.INSTAGRAM_LOGIN_LOAD_WAIT_SECONDS, Constants.INSTAGRAM_SEE_ALL_NAME)
            
            return True

        except Exception as e:
            print(StringResources.EXCEPTION_MESSAGE.format(e))
            return False
            
    '''
    Scrape the followers / following list for the input account.
    2 Modes of Operation:
        1 - To get the people that the account follows
        2 - To get the people that follow the account
    '''
    def scrape_account_people(self, account, mode):
        #Load the page for the account
        print(StringResources.INSTAGRAM_ACCOUNT_PAGE_MESSAGE.format(account))
        self.Browser.get_website(Constants.INSTAGRAM_FORMATTABLE_URL.format(account))
    
        link, listXPath = "", ""
    
        # If mode == 2 get the people that follow the account
        # Else the people the account follows
        if mode == 1:
            print(StringResources.INSTAGRAM_LOAD_FOLLOWERS_MESSAGE.format(account))
            link = Constants.INSTAGRAM_FOLLOWERS_LINK_NAME  
            listXPath = Constants.INSTAGRAM_FOLLOWERS_X_PATH 
            print(StringResources.INSTAGRAM_FOUND_FOLLOWERS_MESSAGE)
        else:
            print(StringResources.INSAGRAM_LOAD_FOLLOWING_MESSAGE.format(account))
            link = Constants.INSTAGRAM_FOLLOWING_LINK_NAME
            listXPath = Constants.INSTAGRAM_FOLLOWING_X_PATH
            print(StringResources.INSTAGRAM_FOUND_FOLLOWING_MESSAGE)

        totalCount = self.get_count_number(account, link, listXPath)
        print("\t{0}".format(totalCount))
    
        # Use CSS to get the nth children
        followerCss = Constants.INSTAGRAM_PEOPLE_CSS 
        peopleSet = set()

        # Create and return a set of all the following/followers
        # We need to scroll the modal in order for the next few followers to load
        try:
            for followerIndex in range(1, totalCount):
                follower = waiter.find_element(self.Browser.webDriver, Constants.followerCss.format(followerIndex))
                followerName = follower.text
                peopleSet.add(followerName)
                print(StringResources.INSTAGRAM_PERSON_ITEM_TEXT.format(followerIndex, followerName))

                self.Browser.execute_input_script(Constants.INSTAGRAM_MODAL_SCOLL_TEXT, follower)

        except Exception as e:
            # Sometimes instagram lies, and the follower count is wrong
            print(StringResources.INSTAGRAM_LIES_TEXT.format(type(e).__name__))
        finally:
            return peopleSet
        
    '''
    Gets the following or followers count for the input account.
    Takes in the username, linkName and linkXPath
    '''    
    def get_count_number(self, account, link, listXPath):
        # Click the Following / Followers link
        self.Browser.find_element_by_link(link).click()    
        
        # Wait for the modal to load    
        waiter.find_element(self.Browser.webDriver, Constants.INSTAGRAM_PEOPLE_COUNT_DIV, by=XPATH)    
        totalCount = int((self.Browser.find_elements_by_x_path(listXPath, 1).text).replace(',',''))
    
        return totalCount