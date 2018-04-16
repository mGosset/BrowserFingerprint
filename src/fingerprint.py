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

    CONSISTENT = "consistent"

    # Attributs de la table extensionData
    MYSQL_ATTRIBUTES = set([COUNTER, ID, CREATION_TIME, END_TIME, ADDRESS_HTTP,
                            USER_AGENT_HTTP, ACCEPT_HTTP, HOST_HTTP,
                            CONNECTION_HTTP, ENCODING_HTTP, LANGUAGE_HTTP,
                            ORDER_HTTP, PLUGINS_JS, PLUGINS_JS_HASHED, PLATFORM_JS, COOKIES_JS,
                            DNT_JS, TIMEZONE_JS, RESOLUTION_JS, LOCAL_JS,
                            SESSION_JS, IE_DATA_JS, CANVAS_JS_HASHED,
                            FONTS_FLASH, RESOLUTION_FLASH, LANGUAGE_FLASH,
                            PLATFORM_FLASH, AD_BLOCK])

    ANALYSIS_ATTRIBUTES = [COUNTER, ID, CREATION_TIME, END_TIME, ADDRESS_HTTP, USER_AGENT_HTTP, ACCEPT_HTTP,
                           CONNECTION_HTTP, ENCODING_HTTP, LANGUAGE_HTTP, ORDER_HTTP, PLUGINS_JS_HASHED,
                           PLATFORM_JS, COOKIES_JS, DNT_JS, TIMEZONE_JS, RESOLUTION_JS, LOCAL_JS, SESSION_JS,
                           CANVAS_JS_HASHED, FONTS_FLASH_HASHED, RESOLUTION_FLASH, LANGUAGE_FLASH, PLATFORM_FLASH,
                           BROWSER_FAMILY, GLOBAL_BROWSER_VERSION, MINOR_BROWSER_VERSION, MAJOR_BROWSER_VERSION, OS,
                           RENDERER, VENDOR, PLUGINS_JS]

    def __init__(self, val_attributes):
        self.val_attributes = dict()
        for attribute in val_attributes:
            try:
                self.val_attributes[attribute] = val_attributes[attribute]
            except:
                # exception happens when the value of the attribute has to
                # be determined dynamically (ie nb plugins, browser version)
                self.val_attributes[attribute] = None

        # we reorder resolution when necessary (usefull for mobile users)
        if Fingerprint.RESOLUTION_JS in val_attributes:
            if self.val_attributes[Fingerprint.RESOLUTION_JS] != "no JS":
                split_res = self.val_attributes[Fingerprint.RESOLUTION_JS].split("x")
                if len(split_res) > 1 and split_res[1] > split_res[0]:
                    self.val_attributes[Fingerprint.RESOLUTION_JS] = split_res[1] +\
                        "x"+ split_res[0] + "x"+ split_res[2]

        if Fingerprint.ORDER_HTTP in val_attributes:
            orders = self.val_attributes[Fingerprint.ORDER_HTTP].split(" ")
            orders.sort()
            self.val_attributes[Fingerprint.ORDER_HTTP] = " ".join(orders)

        if Fingerprint.USER_AGENT_HTTP in val_attributes:
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

    def hasPlatformInconsistency(self):
        if self.hasJsActivated():
            try:
                plat = ""
                platUa = self.getOs()[0:3].lower()
                if self.hasFlashActivated():
                    platFlash = self.val_attributes[Fingerprint.PLATFORM_FLASH][0:3].lower()
                    plat = platFlash
                else:
                    platJs = self.val_attributes[Fingerprint.PLATFORM_JS][0:3].lower()
                    plat = platJs
                    if (platUa == "lin" or platUa=="ubu" or platUa =="ios" or platUa=="and") and self.val_attributes[Fingerprint.PLUGINS_JS].find(".dll") > -1:
                        return True
                    if platUa.startswith("ip") and self.val_attributes[Fingerprint.PLUGINS_JS].lower().find("flash") > -1:
                        return True
                    if (platUa == "win" or platUa == "mac" or platUa == "ios") and self.val_attributes[Fingerprint.PLUGINS_JS].find(".so") > -1:
                        return True
                    if (platUa == "ubu" or platUa == "win" or platUa == "lin") and self.val_attributes[Fingerprint.PLUGINS_JS].find(".plugin") > -1:
                        return True
                incons = not(plat == platUa)
                if plat == "lin" and platUa == "and":
                    incons = False
                elif plat == "lin" and platUa == "ubu":
                    incons = False
                elif plat == "x64" and platUa == "win":
                    incons = False
                elif plat == "ipa" and platUa == "ios":
                    incons = False
                elif plat == "iph" and platUa == "ios":
                    incons = False
                elif plat == "" and platUa == "":
                    incons = True

                elif plat == "lin" and platUa == "and":
                    incons = False
                elif plat == "lin" and platUa == "ubu":
                    incons = False
                elif plat == "x64" and platUa == "win":
                    incons = False
                elif plat == "ipa" and platUa == "ios":
                    incons = False
                elif plat == "iph" and platUa == "ios":
                    incons = False
                elif plat == "ipo" and platUa == "ios":
                    incons = False
                elif self.getOs() == "Windows Phone" and plat == "arm":
                    incons = False
                elif plat == "arm" and self.val_attributes[Fingerprint.USER_AGENT_HTTP].find("SIM") > -1:
                    incons = False
                elif platUa == "chr" and plat == "lin":
                    incons = False
                elif self.val_attributes[Fingerprint.USER_AGENT_HTTP].find("Touch") > -1 and plat == "arm":
                    incons = False
                elif platUa == "oth":
                    incons = False
                elif plat == "" and platUa == "":
                    incons = True

                return incons
            except:
                return True
        else:
            raise ValueError("Javascript is not activated")

    def getStartTime(self):
        return self.val_attributes[Fingerprint.CREATION_TIME]

    def getEndTime(self):
        return self.val_attributes[Fingerprint.END_TIME]

    def getTimezone(self):
        return self.val_attributes[Fingerprint.TIMEZONE_JS]

    def getUserAgent(self):
        return self.val_attributes[Fingerprint.USER_AGENT_HTTP]

    def getLanguages(self):
        return self.val_attributes[Fingerprint.LANGUAGE_HTTP]

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
