from pytube import YouTube
import random

class Que:
    def __init__(self):
        self.curr = None
        self.is_playing = False
        self.index = -1
        self.arr = []

    def Change_song(self):
        self.curr = self.arr[self.index]

    def add(self, yt, isPlaylist=False):
        self.arr.append(yt)

        if (self.curr == None):
            self.Change_song()

        if (not isPlaylist):
            return f'"{yt.title}" has been added to que to possition [{self.Lenght()}/{self.Lenght()}]'

    def Currently_playing(self):
        return f"Songs/{self.curr}.mp4"

    def Next(self):
        if (self.Check_next()):
            self.index += 1
            self.Change_song()
            return True
        return False 
    
    def Check_next(self):
        return self.Check_in_bounds(self.index+1)

    def Lenght(self):
        return len(self.arr)
    
    def Lenght_to_end(self):
        return self.Lenght() - self.index - 1  

    def Previous(self):
        if (self.Check_previous()):
            self.index -= 2
            return True
        return False  
    
    def Check_previous(self):
        return self.Check_in_bounds(self.index-1)

    def Delete(self, pos):
        if self.Check_in_bounds(pos):
            del self.arr[pos]
            return True
        return False

    def Go_to_start(self):
        self.index = -1
    
    def Go_to(self, pos):
        if (self.Check_in_bounds(pos-1)):
            self.index = pos - 2
            return True
        return False
    

    def Check_in_bounds(self, pos):
        if (pos < 0 or pos > self.Lenght()-1):
            return False
        return True
    
    def clear(self):
        self.curr = None
        self.is_playing = False
        self.index = -1
        self.arr = []

    def Get_random(self):
        self.index = random.randint(0, self.Lenght()-1)
        self.Change_song()

    def shuffle(self):
        random.shuffle(self.arr)