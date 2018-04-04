from ua_parser import user_agent_parser
import re
import math as mt

class Fingerprint():

    ID = "id"
    COUNTER = "counter"
    CREATION_TIME = "creationDate"
    END_TIME = "endDate"

    # HTTP attributes
    ACCEPT_HTTP = "acceptHttp"
    LANGUAGE_HTTP = "languageHttp"
    USER_AGENT_HTTP = "userAgentHttp"
    ORDER_HTTP = "orderHttp"
    ADDRESS_HTTP = "addressHttp"
    CONNECTION_HTTP = "connectionHttp"
    ENCODING_HTTP = "encodingHttp"
    HOST_HTTP = "hostHttp"

    BROWSER_FAMILY = "browserFamily"
    MINOR_BROWSER_VERSION = "minorBrowserVersion"
    MAJOR_BROWSER_VERSION = "majorBrowserVersion"
    GLOBAL_BROWSER_VERSION = "globalBrowserVersion"
    OS = "os"

    # Javascript attributes
    COOKIES_JS = "cookiesJS"
    RESOLUTION_JS = "resolutionJS"
    TIMEZONE_JS = "timezoneJS"
    PLUGINS_JS = "pluginsJS"
    PLUGINS_JS_HASHED = "pluginsJSHashed"
    SESSION_JS = "sessionJS"
    DNT_JS = "dntJS"
    IE_DATA_JS = "IEDataJS"
    CANVAS_JS_HASHED = "canvasJSHashed"
    LOCAL_JS = "localJS"
    PLATFORM_JS = "platformJS"
    AD_BLOCK = "adBlock"
    RENDERER = "rendererWebGLJS"
    VENDOR = "vendorWebGLJS"

    NB_PLUGINS = "nbPlugins"

    # Flash attributes
    PLATFORM_FLASH = "platformFlash"
    FONTS_FLASH = "fontsFlash"
    FONTS_FLASH_HASHED = "fontsFlashHashed"
    LANGUAGE_FLASH = "languageFlash"
    RESOLUTION_FLASH = "resolutionFlash"

    NB_FONTS = "nbFonts"

    # Attributs de la table extensionData
    MYSQL_ATTRIBUTES = set([COUNTER, ID, CREATION_TIME, END_TIME, ADDRESS_HTTP,
                            USER_AGENT_HTTP, ACCEPT_HTTP, HOST_HTTP,
                            CONNECTION_HTTP, ENCODING_HTTP, LANGUAGE_HTTP,
                            ORDER_HTTP, PLUGINS_JS, PLATFORM_JS, COOKIES_JS,
                            DNT_JS, TIMEZONE_JS, RESOLUTION_JS, LOCAL_JS,
                            SESSION_JS, IE_DATA_JS, CANVAS_JS_HASHED,
                            FONTS_FLASH, RESOLUTION_FLASH, LANGUAGE_FLASH,
                            PLATFORM_FLASH, AD_BLOCK])

    def __init__(self, list_attributes, val_attributes):
        self.val_attributes = dict()
        for attribute in list_attributes:
            try:
                self.val_attributes[attribute] = val_attributes[attribute]
            except:
                # exception happens when the value of the attribute has to
                # be determined dynamically (ie nb plugins, browser version)
                self.val_attributes[attribute] = None

        # we reorder resolution when necessary (usefull for mobile users)
        if Fingerprint.RESOLUTION_JS in list_attributes:
            if self.val_attributes[Fingerprint.RESOLUTION_JS] != "no JS":
                split_res = self.val_attributes[Fingerprint.RESOLUTION_JS].split("x")
                if len(split_res) > 1 and split_res[1] > split_res[0]:
                    self.val_attributes[Fingerprint.RESOLUTION_JS] = split_res[1] +\
                        "x"+ split_res[0] + "x"+ split_res[2]

        if Fingerprint.PLUGINS_JS in list_attributes:
            plugins = self.getPlugins()

        if Fingerprint.ORDER_HTTP in list_attributes:
            orders = self.val_attributes[Fingerprint.ORDER_HTTP].split(" ")
            orders.sort()
            self.val_attributes[Fingerprint.ORDER_HTTP] = " ".join(orders)

        if Fingerprint.USER_AGENT_HTTP in list_attributes:
            parsedUa = user_agent_parser.Parse(val_attributes[Fingerprint.USER_AGENT_HTTP])
            self.val_attributes[Fingerprint.BROWSER_FAMILY] = parsedUa["user_agent"]["family"]
            self.val_attributes[Fingerprint.MINOR_BROWSER_VERSION] = parsedUa["user_agent"]["minor"]
            self.val_attributes[Fingerprint.MAJOR_BROWSER_VERSION] = parsedUa["user_agent"]["major"]
            try:
                self.val_attributes[Fingerprint.GLOBAL_BROWSER_VERSION] = self.val_attributes[Fingerprint.MAJOR_BROWSER_VERSION] + \
                                                                      self.val_attributes[Fingerprint.MINOR_BROWSER_VERSION]
            except:
                self.val_attributes[Fingerprint.GLOBAL_BROWSER_VERSION] = "zzzzzz"

            self.val_attributes[Fingerprint.OS] = parsedUa["os"]["family"]


    def hasJsActivated(self):
        try:
            return self.val_attributes[Fingerprint.TIMEZONE_JS] != "no JS"
        except:
            return False

    def hasFlashActivated(self):
        try:
            return self.val_attributes[Fingerprint.FONTS_FLASH] != "Flash detected but not activated (click-to-play)" and \
                self.val_attributes[Fingerprint.FONTS_FLASH] != "Flash not detected" and \
                self.val_attributes[Fingerprint.FONTS_FLASH] != "Flash detected but blocked by an extension"
        except:
            return False

    def getStartTime(self):
        return self.val_attributes[Fingerprint.CREATION_TIME]

    def getEndTime(self):
        return self.val_attributes[Fingerprint.END_TIME]

    def getTimezone(self):
        return self.val_attributes[Fingerprint.TIMEZONE_JS]

    def getUserAgent(self):
        return self.val_attributes[Fingerprint.USER_AGENT_HTTP]

    def getFonts(self):
        if self.hasFlashActivated():
            return self.val_attributes[Fingerprint.FONTS_FLASH].split("_")
        else:
            return []

    def getNumberFonts(self):
        return len(self.getFonts())

    def getPlugins(self):
        if self.hasJsActivated():
            return re.findall("Plugin [0-9]+: ([a-zA-Z -.]+)", self.val_attributes[Fingerprint.PLUGINS_JS])
        else:
            return []

    def getNumberOfPlugins(self):
        return self.val_attributes[Fingerprint.NB_PLUGINS]

    def getBrowser(self):
        return self.val_attributes[Fingerprint.BROWSER_FAMILY]

    def getOs(self):
        return self.val_attributes[Fingerprint.OS]

    def hasFlashBlockedByExtension(self):
        return self.val_attributes[Fingerprint.PLATFORM_FLASH] == "Flash detected but blocked by an extension"

    def getTimeDifference(self, fp):
        try:
            diff = self.getStartTime() - fp.getStartTime()
            return mt.fabs(diff.days + diff.seconds / (3600.0 * 24))
        except:  # for the case where we try to link blink's fingerprints
            return self.getCounter() - fp.getCounter()


    # Returns True if the plugins of the current fingerprint are a subset of another fingerprint fp or the opposite
    # Else, it returns False
    def arePluginsSubset(self, fp):
        pluginsSet1 = set(self.getPlugins())
        pluginsSet2 = set(fp.getPlugins())
        return (pluginsSet1.issubset(pluginsSet2) or pluginsSet2.issubset(pluginsSet1))

    def getNumberDifferentPlugins(self, fp):
        pluginsSet1 = set(self.getPlugins())
        pluginsSet2 = set(fp.getPlugins())
        return max(self.getNumberOfPlugins(), fp.getNumberOfPlugins()) - len(pluginsSet1.intersection(pluginsSet2))

    def getNumberExoticPluginsCommons(self, fp):
        return len(self.exoticPlugins.intersection(fp.exoticPlugins))

    # Returns True if the fonts of the current fingerprint are a subset of another fingerprint fp or the opposite
    # Else, it returns False
    def areFontsSubset(self, fp):
        fontsSet1 = set(self.getFonts())
        fontsSet2 = set(fp.getFonts())
        return (fontsSet1.issubset(fontsSet2) or fontsSet2.issubset(fontsSet1))

    # return True if 2 fingeprints belong to the same user (based on the id criteria)
    def belongToSameUser(self, fp):
        return self.val_attributes[Fingerprint.ID] == fp.val_attributes[Fingerprint.ID]

    def getId(self):
        return self.val_attributes[Fingerprint.ID]

    def getCounter(self):
        return self.val_attributes[Fingerprint.COUNTER]
