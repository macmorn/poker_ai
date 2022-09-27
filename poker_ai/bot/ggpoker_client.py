from collections import defaultdict
from email.utils import localtime
import cv2
import pyautogui
import numpy as np
import time
import utils
import logging

PLAYERS_SECTION_REL= {
    "0":{
    
    "card_1":{
        "top_left":(0.42,0.73),
        "top_right":(0.47,0.73),
        "bottom_left":(0.42,0.83),
        "bottom_right":(0.47,0.83)
    },
    "card_2":{
        "top_left":(0.49,0.73),
        "top_right":(0.53,0.73),
        "bottom_left":(0.49,0.82),
        "bottom_right":(0.53,0.82)
    },
    "playfield":{
        "top_left":(0.4,0.6),
        "top_right":(0.6,0.6),
        "bottom_left":(0.4,0.95),
        "bottom_right":(0.6,0.95)
    },
    "chips_count":{
        "top_left":(0.46,0.90),
        "top_right":(0.55,0.90),
        "bottom_left":(0.46,0.95),
        "bottom_right":(0.55,0.95)
    }
    },
    "1":{
    "playfield":{
        "top_left":(0.0,0.35),
        "top_right":(0.2,0.35),
        "bottom_left":(0.0,0.6),
        "bottom_right":(0.2,0.6)
    }
    },    
    "2":{
    "playfield":{
        "top_left":(0.41,0.07),
        "top_right":(0.57,0.07),
        "bottom_left":(0.41,0.35),
        "bottom_right":(0.57,0.35)
    },
    },
    "3":{
    "playfield":{
        "top_left":(0.78,0.35),
        "top_right":(1.0,0.35),
        "bottom_left":(0.78,0.6),
        "bottom_right":(1.0,0.6)
    },
    }
}

class GGPokerClient:
    def __init__(self):
        self.assets=self._initialize_assets()
        self.window_coordinates=self._locate_window()
        self.width=self.window_coordinates["top_right"][0]-self.window_coordinates["top_left"][0]
        self.height=self.window_coordinates["bottom_left"][1]-self.window_coordinates["top_left"][1]
        self.board_map=self._intialize_board_map()
    
    def survey_field(self):
        pass

    def _update_window_screenshot(self):
        self.window_screenshot_raw=pyautogui.screenshot(region=(self.window_coordinates["top_left"][0],self.window_coordinates["top_left"][1],self.width,self.height))
        self.window_screenshot_grey=cv2.cvtColor(np.array(self.window_screenshot_raw), cv2.COLOR_RGB2GRAY)

    def _initialize_assets(self):
        assets = {}
        assets["dealer_button"] = cv2.imread("poker_ai/bot/assets/dealer_button.png", cv2.IMREAD_GRAYSCALE)
        assets["fold"] = cv2.imread("poker_ai/bot/assets/fold.png", cv2.IMREAD_GRAYSCALE)
        assets["all_in"] = cv2.imread("poker_ai/bot/assets/all_in.png", cv2.IMREAD_GRAYSCALE)
        assets["club"] = cv2.imread("poker_ai/bot/assets/club.png", cv2.IMREAD_GRAYSCALE)
        assets["diamond"] = cv2.imread("poker_ai/bot/assets/diamond.png", cv2.IMREAD_GRAYSCALE)
        assets["heart"] = cv2.imread("poker_ai/bot/assets/heart.png", cv2.IMREAD_GRAYSCALE)
        assets["spade"] = cv2.imread("poker_ai/bot/assets/spade.png", cv2.IMREAD_GRAYSCALE)
        assets["top_left"] = cv2.imread("poker_ai/bot/assets/top_left.png", cv2.IMREAD_GRAYSCALE)
        assets["top_right"] = cv2.imread("poker_ai/bot/assets/top_right.png", cv2.IMREAD_GRAYSCALE)
        assets["bottom_left"] = cv2.imread("poker_ai/bot/assets/bottom_left.png", cv2.IMREAD_GRAYSCALE)
        assets["player_ingame"] = cv2.imread("poker_ai/bot/assets/player_ingame.png", cv2.IMREAD_GRAYSCALE)
        assets["player_ingame2"] = cv2.imread("poker_ai/bot/assets/player_ingame2.png", cv2.IMREAD_GRAYSCALE)

        for key, value in assets.items():
            if value is None:
                raise ValueError(f"Could not load asset {key}")
        return assets

    def _locate_window(self, threshold=0.8, debug=True):
        """Function to find edges of poker window. 
        Relies on assets of corner elements, scale sensitive so element screenshots should be retaken on target device.

        Args:
            threshold (float, optional): _description_. Defaults to 0.8.
            debug_vis (bool, optional): _description_. Defaults to False.
        """
        #set threshold for detection sensitivity
        threshold=threshold

        #make dict of marker files and sizes to match against
        markers=defaultdict(dict)
        for e in ["top_left", "top_right", "bottom_left"]:
            markers[e]["template"]=self.assets[e]
            markers[e]["w"], markers[e]["h"] = markers[e]["template"].shape[::-1]

        #start continuous checking for window
        print("Locating window...")
        while True:
            window_coordinates=defaultdict(dict)
            img=pyautogui.screenshot()
            img_rgb=cv2.cvtColor(np.array(img), cv2.COLOR_RGB2BGR)#this only visualizes
            img_gray = cv2.cvtColor(img_rgb, cv2.COLOR_BGR2GRAY)
            
            for k, v in markers.items():
                result = cv2.matchTemplate(img_gray, v["template"], cv2.TM_CCOEFF_NORMED)
                min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(result)
                if max_val < threshold:
                    if debug==True:
                        print(f"Only {max_val} found for {k}, retrying...")
                    continue
                if k == "top_left":
                    window_coordinates[k]=max_loc
                elif k == "top_right":
                    window_coordinates[k]=(max_loc[0]+v["w"], max_loc[1])
                elif k == "bottom_left":
                    window_coordinates[k]=(max_loc[0], max_loc[1]+v["h"])
            if len(window_coordinates) == 3:
                print("Window found!")
                width=window_coordinates["top_right"][0]-window_coordinates["top_left"][0]
                window_coordinates["bottom_right"]=(window_coordinates["bottom_left"][0]+width, window_coordinates["bottom_left"][1])

                break
                

        return window_coordinates

    def _intialize_board_map(self) -> dict:
        """Function to initialize the playfield map.
        """
        playfield_map = defaultdict(dict)
        for k, v in PLAYERS_SECTION_REL.items():
            for k2, v2 in v.items():
                playfield_map[k][k2] = {
                    "top_left": (int(v2["top_left"][0] * self.width),
                                    int(v2["top_left"][1] * self.height)),
                    "top_right": (int(v2["top_right"][0] * self.width),
                                    int(v2["top_right"][1] * self.height)),
                    "bottom_left": (int(v2["bottom_left"][0] * self.width),
                                    int(v2["bottom_left"][1] * self.height)),
                    "bottom_right": (int(v2["bottom_right"][0] * self.width),
                                    int(v2["bottom_right"][1] * self.height))
                    
                }

        return playfield_map

    def is_asset_in_bbox(self, asset, bbox : dict, threshold=0.7, debug_vis=True):
        """Function to check if element is inside bounding box.
            Takes in image and bouing box dict.

        Args:
            asset (image array): img array from assets dict
            bb (dict): bounding box dict with standard keys

        Returns:
            bool: True if element is inside bounding box
        """
        section=self.window_screenshot_grey[bbox["top_left"][1]:bbox["bottom_left"][1], bbox["top_left"][0]:bbox["top_right"][0]]
        for factors in [1, 0.97, 0.93]:
            scaled_asset=utils.resize_image(asset, factors)        
            res=cv2.matchTemplate(section, scaled_asset, cv2.TM_CCOEFF_NORMED)
            
            min_val, max_val, min_loc, max_loc = cv2.minMaxLoc(res)
            if max_val > threshold:
                if debug_vis==True:
                    print(f"Found asset at {max_loc} with scale factor {factors}")
                return True
            else:
                return False
    
    def _measure_relative_cursor_position_realtime(self):
        """Helper function that prints the relative location in the screen.
        For debugging purposes.
        """
        while True:
            x, y = pyautogui.position()
            rel_x=(x-self.window_coordinates["top_left"][0])/self.width
            rel_y= (y-self.window_coordinates["top_left"][1])/self.height
            print(f"Relative pixels: {round(rel_x,2)}, {round(rel_y,2)})")
            time.sleep(3)

    def _draw_bb_areas_interest(self):
        """Helper function that draws the bounding boxes of al the areas of interest.
        For debugging purposes."""
        if self.playfield_map & self.window_screenshot_grey:

            for k, v in self.playfield_map.items():
                for k2, v2 in v.items():
                    
                    self.window_screenshot_grey=c._draw_bb_with_coordinates(self.window_screenshot_grey, v2, k+k2)

            cv2.imshow("window", self.window_screenshot_grey)
            cv2.waitKey()
        
        elif self.window_screenshot_grey:
            print("No playfield map available")
        elif self.playfield_map:
            print("No screenshot available")
        else:
            print("No screenshot AND playfield map available")

    @staticmethod
    def _draw_bb_with_coordinates(image , bb : dict, text : str = None):
        """Helper function to draw bounding box on screenshot.
        For debugging purposes.

        Args:
            bb (dict): bounding box dict
        """
        cv2.rectangle(image, bb["top_left"], bb["bottom_right"], 255, 2)
        if text:
            cv2.putText(image, text, bb["top_left"], cv2.FONT_HERSHEY_SIMPLEX, 0.5, 255, 2)

        return image


if __name__ == "__main__":
    c=GGPokerClient()
    logging.info("GGPokerClient initialized")
    while True:
        #update frame and check if players are in game
        c._update_window_screenshot()
        players=[]
        suits={}
        for k, v in c.board_map.items():
            if k == "0":
                if c.is_asset_in_bbox(c.assets["player_ingame"], c.board_map[k]["playfield"], threshold=0.8, debug_vis=True):
                    players.append(k)
                for suit in ["spade", "heart", "diamond", "club"]:
                    if c.is_asset_in_bbox(c.assets[suit], c.board_map[k]["card_1"], threshold=0.8, debug_vis=True):
                        suits["card1"](suit)
                    if c.is_asset_in_bbox(c.assets[suit], c.board_map[k]["card_2"], threshold=0.8, debug_vis=True):
                        suits["card2"](suit)
            else:
                if c.is_asset_in_bbox(c.assets["player_ingame2"], c.board_map[k]["playfield"], threshold=0.8, debug_vis=True):
                    players.append(k) 
           
        
        print(f"At {time.localtime()} Players in game: {players}, total: {len(players)} \n Suits in hand: {suits}")

