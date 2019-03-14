'''
Labeling script.
Run the script, then click on the figure
Relevance label: Relevant>Shift. Not Relevant>Up arrow
Sentiment label: Negative>Left arrow. Neutral>Down arrow. Positive>Right arrow
Next tweet>Enter. 
Will only go to next tweet if fully labeled or labeled as Not Relevant
Close the figure to stop the script. 
'''
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import threading
import time
import json
import emoji

class DataClass():
    def __init__(self):
        self.dataFileName = 'SampleData.json'
        self.labelFileName = 'LabeledData.json'
        self.saveJson = False
        self.nextLine = True
        self.quit = False
        self.newPlot = False
        self.relReady = False
        self.sentReady = False
        self.sentiment = 0
        self.relevant = 0
        self.relLabels  = ['Not Relevant', 'Relevant']
        self.sentLabels  = ['Negative', 'Neutral', 'Positive']
        self.triggerKeys = ['shift', 'up', 'left', 'right', 'down']
  
#Fetches tweet from the data file
class FetchTweet(threading.Thread):
    def __init__(self, data):
        threading.Thread.__init__(self)
        self.d = data
        self._period = 0.25
        self._nextCall = time.time()
        self.labeledTweets = []
        try:
            with open(self.d.labelFileName, encoding="utf8") as f:
                for line in f:
                    if line != '':
                        tweet = json.loads(line)
                        self.labeledTweets.append(tweet['id'])
        except FileNotFoundError:
            print("No labeled data, will create new file")
    
    def run(self):
        with open(self.d.dataFileName, 'r', encoding="utf8") as f:
            while True:
                if self.d.saveJson:
                    self.d.saveJson = False
                    tweet = self.d.jLine
                    tweet['isRelevant'] = self.d.relevant
                    if tweet['isRelevant']:
                        tweet['sentiment'] = self.d.sentiment
                    with open(self.d.labelFileName, 'a+', \
                              encoding="utf8") as outputFile:
                        outputFile.write(json.dumps(tweet) + '\n')
                        print("Tweet Labeled: " + str(tweet['id']))
                if self.d.nextLine:
                    self.d.nextLine = False
                    while True:
                        tweet = json.loads(f.readline())
                        if 'id' not in tweet.keys():
                            continue
                        if tweet['id'] not in self.labeledTweets:
                            break
                    self.d.jLine = tweet
                    self.d.newPlot = True
                if self.d.quit:
                    print("Labeller stopped")
                    break
                # sleep until next execution
                self._nextCall = self._nextCall + self._period;
                time.sleep(self._nextCall - time.time())
      
#Show tweet on a figure
class PlotTweet(): 
    def __init__(self, data):
        self.d = data
        self.fig = plt.figure(figsize=(7,5))
        plt.box(on=None)
        plt.tight_layout()
        self.ani = FuncAnimation(self.fig, self.run, \
                                 interval = 25, repeat=True)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.fig.canvas.mpl_connect('close_event', self.handle_close)
    
    def run(self, i):
        if self.d.newPlot:
            self.d.newPlot = False        
            tweet = self.d.jLine
            leftX = -0.05
            plt.cla()
            plt.axis('off')
            plt.text(leftX,0, self.d.jLine['id'], fontsize=8)
            plt.text(leftX,0.85, tweet['user']['name'] \
                     + " @" + tweet['user']['screen_name']  , fontsize=12)
            if tweet['in_reply_to_screen_name'] is not None:
                plt.text(leftX, 0.75, "Replying to: " \
                         + tweet['in_reply_to_screen_name'])
            plt.text(leftX, 0.45, emoji.demojize(tweet['text']), \
                     fontsize=12, wrap=True)
            if self.d.relReady:
                plt.text(leftX, 0.35, self.d.relLabels[self.d.relevant])
            if self.d.sentReady:
                plt.text(leftX, 0.25, self.d.sentLabels[self.d.sentiment])
                
    def on_key(self, event):
        if event.key == 'escape':
            self.d.quit = True
        if event.key == 'shift':
            self.d.relReady = True
            self.d.relevant = 1
        if event.key == 'up':
            self.d.relReady = True
            self.d.relevant = 0
        if event.key == 'left':
            self.d.sentReady = True
            self.d.sentiment = 0
        if event.key == 'down':
            self.d.sentReady = True
            self.d.sentiment = 1
        if event.key == 'right':
            self.d.sentReady = True
            self.d.sentiment = 2
        if event.key in self.d.triggerKeys:
            self.d.newPlot = True
        if event.key == 'enter' and \
        ((self.d.relReady and self.d.sentReady) \
        or (self.d.relReady and self.d.relevant==0)):
            self.d.nextLine = True
            self.d.relReady = False
            self.d.sentReady = False
            self.d.saveJson = True

    def handle_close(self, evt):
        print('Closed Figure')
        self.d.quit = True


##Multi thread because matplotlib plotting blocks the main thread
data = DataClass()
fetcher = FetchTweet(data)
plotter = PlotTweet(data)
fetcher.start()