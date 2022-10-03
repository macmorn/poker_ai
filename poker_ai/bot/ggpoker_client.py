from collections import defaultdict
import cv2
import pyautogui
import mss
import numpy as np
import time
import utils
import logging

from poker_ai.poker.card import Card

PLAYERS_SECTION_REL= {
    "0":{
    
    "card_1":{
        "top_left":(0.43,0.73),
        "top_right":(0.475,0.73),
        "bottom_left":(0.43,0.83),
        "bottom_right":(0.475,0.83)
    },
    "card_2":{
        "top_left":(0.485,0.73),
        "top_right":(0.53,0.73),
        "bottom_left":(0.485,0.825),
        "bottom_right":(0.53,0.825)
    },
    "playfield":{
        "top_left":(0.4,0.6),
        "top_right":(0.6,0.6),
        "bottom_left":(0.4,0.95),
        "bottom_right":(0.6,0.95)
    },
    "chips_count":{
        "top_left":(0.445,0.895),
        "top_right":(0.56,0.895),
        "bottom_left":(0.445,0.95),
        "bottom_right":(0.56,0.95)
    },
    "bet_amount":{
        "top_left":(0.44,0.675),
        "top_right":(0.54,0.675),
        "bottom_left":(0.44,0.71),
        "bottom_right":(0.54,0.71) 
    },
    "fold":{
        "top_left":(0.74,0.91),
        "top_right":(0.74,0.91),
        "bottom_left":(0.74,0.91),
        "bottom_right":(0.74,0.91) 
    },
    "all_in":{
        "top_left":(0.91,0.91),
        "top_right":(0.91,0.91),
        "bottom_left":(0.91,0.91),
        "bottom_right":(0.91,0.91) 
    },
    },
    
    "1":{
    "playfield":{
        "top_left":(0.0,0.35),
        "top_right":(0.2,0.35),
        "bottom_left":(0.0,0.6),
        "bottom_right":(0.2,0.6)
    },
    "chips_count":{
        "top_left":(0.03,0.515),
        "top_right":(0.14,0.515),
        "bottom_left":(0.03,0.555),
        "bottom_right":(0.14,0.555)
    },
    "bet_amount":{
        "top_left":(0.15,0.5),
        "top_right":(0.22,0.5),
        "bottom_left":(0.15,0.53),
        "bottom_right":(0.22,0.53) 
    }
    },    
    "2":{
    "playfield":{
        "top_left":(0.41,0.07),
        "top_right":(0.57,0.07),
        "bottom_left":(0.41,0.35),
        "bottom_right":(0.57,0.35)
    },
    "chips_count":{
        "top_left":(0.45,0.23),
        "top_right":(0.56,0.23),
        "bottom_left":(0.45,0.28),
        "bottom_right":(0.56,0.28)
    },
    "bet_amount":{
        "top_left":(0.46,0.325),
        "top_right":(0.55,0.325),
        "bottom_left":(0.46,0.36),
        "bottom_right":(0.55,0.36) 
    }
    },
    "3":{
    "playfield":{
        "top_left":(0.78,0.35),
        "top_right":(1.0,0.35),
        "bottom_left":(0.78,0.6),
        "bottom_right":(1.0,0.6)
    },
    "chips_count":{
        "top_left":(0.87,0.515),
        "top_right":(0.98,0.515),
        "bottom_left":(0.87,0.555),
        "bottom_right":(0.98,0.555)
    },
    "bet_amount":{
        "top_left":(0.78,0.5),
        "top_right":(0.84,0.5),
        "bottom_left":(0.78,0.54),
        "bottom_right":(0.84,0.54) 
    }
    }
}

COLOR_RED=(21,21,203)
COLOR_GREY=(143,143,143)
COLOR_WHITE=(242,242,242)

class GGPoker_Client:
    def __init__(self):
        #TODO: window manager goes here
        pass

class AoF_Client(GGPoker_Client):
    """This client if for the AoF game on GGPoker.
    """

    def __init__(self, scale=1.0,quadrant=None):
        super().__init__()
        self.scale=scale
        self.quadrant=quadrant #TODO: use this in finding window coordinates
        self.assets=self._initialize_assets()
        self.sct = mss.mss() #screenshot engine
        self.window_coordinates =self._locate_window()
        self.width=self.window_coordinates["top_right"][0]-self.window_coordinates["top_left"][0]
        self.height=self.window_coordinates["bottom_left"][1]-self.window_coordinates["top_left"][1]
        self.board_map=self._intialize_board_map()
        self._update_window_screenshot()
        self.current_round=0
    
    def survey_field(self):
        pass

    def _measure_relative_cursor_position_realtime(self):
        """Helper function that prints the relative location in the screen.
        For debugging purposes.
        """
        while True:
            x, y = pyautogui.position()
            self._update_window_screenshot()
            rel_x=(x-self.window_coordinates["top_left"][0])/self.width
            rel_y= (y-self.window_coordinates["top_left"][1])/self.height
            print(f"Relative pixels: {round(rel_x,2)}, {round(rel_y,2)})")
            try:
                color=self.window_screenshot_bgr[int(rel_y*self.height),int(rel_x*self.width)]
                print(f"Color at cursor: {color}")
            except:
                print("Color not found")
            time.sleep(3)


    def _draw_bb_areas_interest(self):
        """Helper function that draws the bounding boxes of al the areas of interest.
        For debugging purposes."""
        for k, v in self.board_map.items():
            for k2, v2 in v.items():
                
                self.window_screenshot_grey=utils.draw_bb_with_coordinates(self.window_screenshot_grey, v2, k+k2)

        cv2.imshow("window", self.window_screenshot_grey)
        cv2.waitKey()

    def _update_window_screenshot(self):
        monitor={"top":self.window_coordinates["top_left"][1],
        "left":self.window_coordinates["top_left"][0],
        "width":self.width,
        "height":self.height}
        window_screenshot_raw=self.sct.grab(monitor=monitor)
        self.window_screenshot_bgr=cv2.cvtColor(np.array(window_screenshot_raw), cv2.COLOR_BGRA2BGR)
        self.window_screenshot_grey=cv2.cvtColor(np.array(window_screenshot_raw), cv2.COLOR_BGRA2GRAY)

    def _initialize_assets(self):
        assets = {}
        assets["dealer_button"] = cv2.imread("poker_ai/bot/assets/dealer_button.png", cv2.IMREAD_GRAYSCALE)
        assets["fold"] = cv2.imread("poker_ai/bot/assets/fold.png", cv2.IMREAD_GRAYSCALE)
        assets["all_in"] = cv2.imread("poker_ai/bot/assets/all_in.png", cv2.IMREAD_GRAYSCALE)
        assets["clubs"] = cv2.imread("poker_ai/bot/assets/cards/clubs.png", cv2.IMREAD_GRAYSCALE)
        assets["diamonds"] = cv2.imread("poker_ai/bot/assets/cards/diamonds.png", cv2.IMREAD_GRAYSCALE)
        assets["hearts"] = cv2.imread("poker_ai/bot/assets/cards/hearts.png", cv2.IMREAD_GRAYSCALE)
        assets["spades"] = cv2.imread("poker_ai/bot/assets/cards/spades.png", cv2.IMREAD_GRAYSCALE)
        assets["top_left"] = cv2.imread("poker_ai/bot/assets/top_left.png", cv2.IMREAD_GRAYSCALE)
        assets["top_right"] = cv2.imread("poker_ai/bot/assets/top_right.png", cv2.IMREAD_GRAYSCALE)
        assets["bottom_left"] = cv2.imread("poker_ai/bot/assets/bottom_left.png", cv2.IMREAD_GRAYSCALE)
        assets["player_ingame"] = cv2.imread("poker_ai/bot/assets/player_ingame.png", cv2.IMREAD_GRAYSCALE)
        assets["opp_cards"] = cv2.imread("poker_ai/bot/assets/opp_cards.png", cv2.IMREAD_GRAYSCALE)
        assets["2"] = cv2.imread("poker_ai/bot/assets/cards/2.png", cv2.IMREAD_GRAYSCALE)
        assets["3"] = cv2.imread("poker_ai/bot/assets/cards/3.png", cv2.IMREAD_GRAYSCALE)
        assets["4"] = cv2.imread("poker_ai/bot/assets/cards/4.png", cv2.IMREAD_GRAYSCALE)
        assets["5"] = cv2.imread("poker_ai/bot/assets/cards/5.png", cv2.IMREAD_GRAYSCALE)
        assets["6"] = cv2.imread("poker_ai/bot/assets/cards/6.png", cv2.IMREAD_GRAYSCALE)
        assets["7"] = cv2.imread("poker_ai/bot/assets/cards/7.png", cv2.IMREAD_GRAYSCALE)
        assets["8"] = cv2.imread("poker_ai/bot/assets/cards/8.png", cv2.IMREAD_GRAYSCALE)
        assets["9"] = cv2.imread("poker_ai/bot/assets/cards/9.png", cv2.IMREAD_GRAYSCALE)
        assets["10"] = cv2.imread("poker_ai/bot/assets/cards/10.png", cv2.IMREAD_GRAYSCALE)
        assets["J"] = cv2.imread("poker_ai/bot/assets/cards/J.png", cv2.IMREAD_GRAYSCALE)
        assets["Q"] = cv2.imread("poker_ai/bot/assets/cards/Q.png", cv2.IMREAD_GRAYSCALE)
        assets["K"] = cv2.imread("poker_ai/bot/assets/cards/K.png", cv2.IMREAD_GRAYSCALE)
        assets["A"] = cv2.imread("poker_ai/bot/assets/cards/A.png", cv2.IMREAD_GRAYSCALE)
        assets["call"] = cv2.imread("poker_ai/bot/assets/call.png", cv2.IMREAD_GRAYSCALE)

        for key, value in assets.items():
            if value is None:
                raise ValueError(f"Could not load asset {key}")
        return assets

    def _locate_window(self, threshold=0.7, scale= 1.0, debug=False):
        """Function to find edges of poker window. 
        Relies on assets of corner elements, scale sensitive so element screenshots should be retaken on target device.

        Args:
            threshold (float, optional): _description_. Defaults to 0.8.
            debug_vis (bool, optional): _description_. Defaults to False.
        """
        #set threshold for detection sensitivity
        threshold=threshold

        #start continuous checking for window
        print("Locating window...")
        while True:
            window_coordinates={}
            img = np.array(self.sct.grab(self.sct.monitors[1]))
            img=cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            found=defaultdict(dict)
            for ancor in ["bottom_left", "top_right", "top_left"]:
                scaled=utils.resize_image(self.assets[ancor], scale)
                result = cv2.matchTemplate(img, scaled, cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val < threshold:
                    if debug==True:
                        logging.debug(f"Only {max_val} found for {ancor} at scale {scale}, retrying...")
                    #break out of loop if any of the anchors is not found
                    break
                else:
                    found[ancor]["loc"]=max_loc
                    found[ancor]["h"], found[ancor]["w"]=scaled.shape
            if len(found) == 3:
                    logging.info(f"Window found at scale{scale}!")
                    width=found["top_right"]["loc"][0]-found["top_left"]["loc"][0]

                    window_coordinates["top_left"]=found["top_left"]["loc"]
                    window_coordinates["top_right"]=(found["top_right"]["loc"][0]+found["top_right"]["w"], found["top_right"]["loc"][1])
                    window_coordinates["bottom_left"]=(found["bottom_left"]["loc"][0], found["bottom_left"]["loc"][1]+found["bottom_left"]["h"])
                    window_coordinates["bottom_right"]=(window_coordinates["bottom_left"][0]+width, window_coordinates["bottom_left"][1])
                    
                    return window_coordinates        
            #return found corners and scale to be used to scale all other elements
        

    def _intialize_board_map(self) -> dict:
        """Function to initialize the playfield map.
        """
        board_map = defaultdict(dict)
        for k, v in PLAYERS_SECTION_REL.items():
            for k2, v2 in v.items():
                board_map[k][k2] = {
                    "top_left": (int(v2["top_left"][0] * self.width),
                                    int(v2["top_left"][1] * self.height)),
                    "top_right": (int(v2["top_right"][0] * self.width),
                                    int(v2["top_right"][1] * self.height)),
                    "bottom_left": (int(v2["bottom_left"][0] * self.width),
                                    int(v2["bottom_left"][1] * self.height)),
                    "bottom_right": (int(v2["bottom_right"][0] * self.width),
                                    int(v2["bottom_right"][1] * self.height))
                    
                }

        return board_map

    def _is_asset_in_bbox(self, asset, bbox : dict, threshold=0.8, angle : int=None, debug=False):
        """Function to check if element is inside bounding box.
            Takes in image and bouing box dict.
            Works well for some but not others.

        Args:
            asset (image array): img array from assets dict
            bb (dict): bounding box dict with standard keys

        Returns:
            bool: True if element is inside bounding box
        """
        
        full_img=self.window_screenshot_grey
        section=utils.crop_image_by_bbox(full_img, bbox)
        scaled_asset=utils.resize_image(asset, self.scale)  
        if angle:
            if debug:
                print(f"Trying angle {angle}")
            rot_asset=utils.rotate_image_by_angle(scaled_asset, angle)
            if utils.match_over_threshold(section, rot_asset, threshold, debug) == True:
                return True
            
            return False
        else:
            return utils.match_over_threshold(section, scaled_asset, threshold, debug)

    def get_active_players(self):
            """Function to find active players.
            """
            active_players = []
            for k, v in self.board_map.items():
                if self.is_player_active(k):
                    active_players.append(k)
            return active_players

    def get_player_bet_amount(self, player_i="0"):
            """Function to get player bet.
            """
            bet = None
            sc = self.window_screenshot_grey
            section=utils.crop_image_by_bbox(sc, self.board_map[player_i]["bet_amount"])
            #make high contrast for easy detection
            section=utils.make_high_contrast(section, adaptive=False)
            #remove background
            cv2.floodFill(section, None, (1,1), 0)
            cv2.floodFill(section, None, (section.shape[1]-1,section.shape[0]-1), 0)
            bet = utils.do_OCR(section)
            bet = bet.replace("$", "")
            bet = bet.replace("BB", "")
            bet = bet.replace(",", "")
            if bet == "":
                return 0
            bet =float(bet)
            return bet
    
    def get_player_chips_amount(self, player_i="0"):
        """Function to get player bet.
        """
        chips = None
        sc = self.window_screenshot_grey
        section=utils.crop_image_by_bbox(sc, self.board_map[player_i]["chips_count"])
        #make high contrast for easy detection
        section=utils.make_high_contrast(section, adaptive=False)
        #remove background
        cv2.floodFill(section, None, (1,1), 0)
        cv2.floodFill(section, None, (section.shape[1]-1,section.shape[0]-1), 0)
        chips = utils.do_OCR(section,psm=11 )
        chips = chips.replace("$", "")
        chips = chips.replace("BB", "")
        chips = chips.replace(",", "")
        if chips == "":
            return 0
        chips =float(chips)
        return chips

    def get_player_cards(self, player_i="0", threshold=0.75):
            """Function to get suited cards of player.
            """
            suited_cards=[]
            for k, v in self.board_map[player_i].items():
                if k=="card_1" or k=="card_2":
                    section_color=utils.crop_image_by_bbox(self.window_screenshot_bgr, v)
                    is_red=utils.is_color_in_image(section_color, COLOR_RED)
                    section_contrast=utils.crop_image_by_bbox(self.window_screenshot_grey, v)   
                    #make high contrast for easy detection  
                    section_contrast=utils.make_high_contrast(section_contrast) 
                    #rotate card depending on angle  
                    if k == "card_1":
                        section_contrast=utils.rotate_image_by_angle(section_contrast, 5)
                    if k == "card_2":
                        section_contrast=utils.rotate_image_by_angle(section_contrast, -5)
                    #extract rank
                    rank=self._value_in_image(section_contrast, threshold=threshold)
                    if rank:                       
                        if is_red:
                            suit=self._suit_in_image(section_contrast, threshold=threshold, subset="red")
                        else:
                            suit=self._suit_in_image(section_contrast, threshold=threshold, subset="black")
                        if suit:
                            suited_cards.append({"rank":rank, "suit":suit})
            
            #transform to model card representation
            suited_cards=[Card(rank=c["rank"], suit=c["suit"]) for c in suited_cards]
            if len(suited_cards)==2:
                return suited_cards
            elif len(suited_cards)==1:
                print("Only one card found", suited_cards)
            return {}

    def _suit_in_image(self,  image : dict, threshold=0.9, subset="all"):
        """Helper function to get suit is in image.
        """
        found={}
        if subset=="red":
            suits=["hearts", "diamonds"]
        elif subset=="black":
            suits=["spades", "clubs"]
        else:
            suits=["spades", "hearts", "diamonds", "clubs"]
        for suit in suits:
            template = utils.resize_image(self.assets[suit], self.scale)
            #make high contrast
            template=utils.make_high_contrast(template)
            match = cv2.minMaxLoc(cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED))  
            if match[1] > threshold:
                found[suit]=match[1]

        if len(found)>0:
            return max(found, key=found.get)
        else:
            return None
    
    def _value_in_image(self,  image : dict, threshold=0.8):
        """Helper function to get value is in image.
        """
        found={}
        for value in ["A", "K", "Q", "J", "10", "9", "8", "7", "6", "5", "4", "3", "2"]:
            template = utils.resize_image(self.assets[value], self.scale)
            #make high contrast
            template=utils.make_high_contrast(template)
            match = cv2.minMaxLoc(cv2.matchTemplate(image, template, cv2.TM_CCOEFF_NORMED))  
            if match[1] > threshold:
                found[value]=match[1]

        if len(found)>0:
            return max(found, key=found.get)
        else:
            return None
    
    @property
    def is_my_turn(self):
        """Function to check if it is my turn.
        """
        return utils.match_over_threshold(self.window_screenshot_grey, self.assets["fold"], threshold=0.7)
    
    @property
    def _dealer(self):
        """Helper function to get dealer index.
        """
        for k, v in self.board_map.items():
            if self._is_asset_in_bbox(self.assets["dealer_button"], v["playfield"], threshold=0.7):   
                return k
        else:
            return None
    
    @property
    def my_cards_dealt(self):
        """Function to check if cards are dealt to my player.
        """
        card_1_crop=utils.crop_image_by_bbox(self.window_screenshot_bgr, self.board_map["0"]["card_1"])
        card_2_crop=utils.crop_image_by_bbox(self.window_screenshot_bgr, self.board_map["0"]["card_2"])

        fist_dealt=utils.is_color_in_image(card_1_crop, COLOR_WHITE, exact=True) or utils.is_color_in_image(card_2_crop, COLOR_GREY, exact=True)
        second_dealt=utils.is_color_in_image(card_2_crop, COLOR_WHITE, exact=True) or utils.is_color_in_image(card_2_crop, COLOR_GREY, exact=True)
        
        if fist_dealt or second_dealt:
            return True
        else:
            return False

    def is_player_active(self, player_i):
        """Function to check if player is active.
        """
        if player_i=="0":
            return self.my_cards_dealt

        else:
            template=self.assets["opp_cards"]
        if self._is_asset_in_bbox(template, self.board_map[player_i]["playfield"], threshold=0.7):
            return True
        else:
            return False

    def check_player_action(self, player_i, wait_n_seconds=8):
        """Function to check if player is acting.
        """
        start=time.time()

        while True:

            elapsed=time.time()-start
            if elapsed>wait_n_seconds:
                Exception ("Player action not found")
            else:
                self._update_window_screenshot()
                if self.is_player_active(player_i) == False:
                    return "fold"         
                elif self._is_asset_in_bbox(self.assets["call"], self.board_map[player_i]["playfield"], threshold=0.7):
                    return "raise"
                elif self._is_asset_in_bbox(self.assets["all_in"], self.board_map[player_i]["playfield"], threshold=0.7):
                    return "raise"
                else:
                    continue
                    
                   
    def get_player_order(self):
        """Function to get player order, regardless of player number.
        """
        dealer=self._dealer
        active=self.get_active_players()
        if len(active)==2:
            player_order =active[active.index(dealer):]+active[:active.index(dealer)]
            return player_order
        else:
            #make triple len copy of list starting from dealer
            extended=(active[active.index(dealer):]+active[:active.index(dealer)])*3
            player_order = extended[3:3+len(active)]
                
            return player_order
    
    def take_action(self, action, click=True, time:float = 1.0):
        """Function to take action.
        """
        VALID_ACTIONS=["fold", "all_in"]
        if time > 10.0:
            self.log.error("Time is too long")
            time=4.20


        if action in VALID_ACTIONS:
            if click:
                x=self.board_map["0"][action]["top_left"][0]+self.window_coordinates["top_left"][0]
                y=self.board_map["0"][action]["top_left"][1]+self.window_coordinates["top_left"][1]
                utils.human_cursor_click(x=x,y=y, time=time)
            else:
                x=self.window_coordinates["top_left"][0]+20
                y=self.window_coordinates["top_left"][1]+20
                utils.human_cursor_click(x=x,y=y)
                time.sleep(0.5)
                if action=="fold":
                    pyautogui.press("q")
                elif action=="all_in":
                    pyautogui.press("e")
            time.sleep(1)
            if self.is_my_turn:
                Exception("Action not taken")
            
            
        else:
            Exception(f"Action not recognized, must be one of {VALID_ACTIONS}")

    def wait_for_next_round(self):
        """Function to wait for next round.
        Checks if the dealer changed.
        """
        while True:
            dealer=self._dealer
            time.sleep(0.2)
            self._update_window_screenshot()
            
            if (dealer !=self._dealer) & (self._dealer != None):
                break
            else:
                continue

if __name__ == "__main__":
    c=AoF_Client()
    logging.info("GGPokerClient initialized")
    #TODO: see if I have cards, then determine order, then check in order if players are acting unti an action is detected, then construct history for me once its my turn
    while True:
        logging.info("Waiting for new round")
        c.wait_for_next_round()
        logging.info("New round detected")