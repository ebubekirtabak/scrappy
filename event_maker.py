import sys
import time

import kthread
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver import ActionChains
from selenium.webdriver.common.keys import Keys

from logger import Logger
from helpers.variable_helpers import VariableHelpers


class EventMaker:

    driver = None

    def __init__(self, driver, selenium_helper=None):
        self.driver = driver
        self.selenium_helper = selenium_helper
        self.logger = Logger()

    def push_event(self, driver, event):
        if driver is not None:

            try:
                if 'selector' in event:
                    element = driver.find_element_by_xpath(event['selector'])
                else:
                    element = driver

                if element is not None:
                    if 'delay' in event:
                        time.sleep(event['delay'])

                    for action in event['actions']:
                        if 'delay' in action:
                            time.sleep(action['delay'])

                        switcher = {
                            "click": self.set_click,
                            "scroll": self.set_scroll,
                            "style": self.set_style,
                            "scroll_to_element": self.set_scroll_to_element,
                            "excute_script": self.set_excute_script,
                            "$_GET_VARIABLE": self.get_variable,
                            "$_SET_VARIABLE": self.set_variable,
                            "nothing": self.set_nothing,
                        }

                        func = switcher.get(action['type'], lambda: "nothing")
                        func(element, action)

                        if 'sleep' in action:
                            time.sleep(action['sleep'])

                    if 'sleep' in event:
                        time.sleep(event['sleep'])

            except NoSuchElementException as e:
                self.logger.set_error_log("-- NoSuchElementException: " + str(e), True)
                type, value, traceback = sys.exc_info()
                if hasattr(value, 'filename'):
                    print('Error %s: %s' % (value.filename, value.strerror))
                    Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))
            except Exception as e:
                self.logger.set_error_log("Push Event ->: " + str(e), True)
                type, value, traceback = sys.exc_info()
                if hasattr(value, 'filename'):
                    print('Error %s: %s' % (value.filename, value.strerror))
                    Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))

        else:
            return None

    def push_event_to_element(self, element, events):
        try:
            for event in events:
                if 'delay' in event:
                    time.sleep(event['delay'])
                if 'selector' in event:
                    element = element.find_element_by_xpath(event['selector'])

                for action in event['actions']:
                    if 'delay' in action:
                        time.sleep(action['delay'])

                    type = action['type']
                    if type == 'click':
                        self.set_click(element, action)
                    elif type == 'navigate_to':
                        self.driver.navigate().to(action['to'])
                    elif type == 'click_action_element':
                        self.set_click_action_element(self.driver, action)
                    elif type == 'click_with_command':
                        self.set_click_with_command(element, action)
                    elif type == "scroll_to_element":
                        self.set_scroll_to_element(element)
                    elif type == 'scroll':
                        self.set_scroll(element, action)
                    elif type == 'style':
                        self.set_style(element, action)
                    elif type == 'set_attr':
                        self.set_attr(element, action)
                    elif type == 'excute_script':
                        self.set_excute_script(element, action)
                    elif type == 'download':
                        thread = kthread.KThread(target=self.selenium_helper.download_loop,
                                                 args=(element, action))
                        thread.start()

                    if 'sleep' in action:
                        time.sleep(action['sleep'])

                if 'sleep' in event:
                    time.sleep(event['sleep'])

        except NoSuchElementException as e:
            self.logger.set_error_log("-- NoSuchElementException: " + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                print('Error %s: %s' % (value.filename, value.strerror))
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))
        except Exception as e:
            self.logger.set_error_log("Push Event To Element () ->: " + str(e), True)
            type, value, traceback = sys.exc_info()
            if hasattr(value, 'filename'):
                print('Error %s: %s' % (value.filename, value.strerror))
                Logger().set_error_log('Error %s: %s' % (value.filename, value.strerror))

            print("Push Event To Element () ->: " + str(e))

    def set_click_with_command(self, element, action):
        action = ActionChains(self.driver).key_down(Keys.CONTROL)
        action.move_to_element(element)
        action.click()
        action.perform()

    def set_scroll_to_element(self, element, action=None):
        desired_y = (element.size['height'] / 2) + element.location['y']
        window_h = self.driver.execute_script('return window.innerHeight')
        window_y = self.driver.execute_script('return window.pageYOffset')
        current_y = (window_h / 2) + window_y
        scroll_y_by = desired_y - current_y

        self.driver.execute_script("window.scrollBy(0, arguments[0]);", scroll_y_by)

    def set_click_action_element(self, element, action):
        if 'selector' in action:
            element = element.find_element_by_xpath(action['selector'])
            element.click()

    def set_click(self, element, action):
        element.click()

    def set_scroll(self):
        return ""

    def set_nothing(self, element, action):
        pass

    def set_style(self, element, action):
        scriptSetAttrValue = "arguments[0].setAttribute(arguments[1],arguments[2])"
        self.driver.execute_script(scriptSetAttrValue, element, 'style', action['style'])

    def set_attr(self, element, action):
        scriptSetAttrValue = "arguments[0].setAttribute(arguments[1],arguments[2])"
        self.driver.execute_script(scriptSetAttrValue, element, action['attr'], action['attr_value'])

    def set_excute_script(self, element, action):
        self.driver.execute_script(action['script'])

    def get_variable(self, element, script_actions):
        if 'value' in script_actions:
            VariableHelpers().set_variable(
                script_actions['variable_name'],
                script_actions['value'])
        else:
            VariableHelpers().set_variable(script_actions['variable_name'],
                                           element.get_attribute(script_actions['attribute_name']))

    def set_variable(self, element, script_actions):
        target = script_actions['target_attr']
        value = VariableHelpers().get_variable(script_actions['variable_name'])
        if target == 'send_keys':
            element.send_keys(value)
        else:
            self.driver.execute_script("arguments[0]." + target + " = '" + value + "';", element)

    def download(self):
        pass

    def nothing(self, element, action):
        return ""


