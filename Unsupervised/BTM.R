library(BTM)
library(udpipe)
library(SnowballC) #for text Stemmign
library(hunspell) # for spell check and spelling

#Changing the working directory
setwd("Working Directory")

PA<- read.csv("tweet_text.csv", header=TRUE, sep=",", fileEncoding = "UTF-8") #importing the data as a single

print(head(PA))

#In order to turn it into a tidy text dataset, we first need to put it into a data frame.
library(dplyr)
PA$text <- lapply(PA$text, as.character) #the format was 'factor' /check class(PA$text)
PA$text<-as.character(unlist(PA$text)) #to unlist the list to character format
PA$text <- iconv(PA$text, "UTF-8", "ASCII", sub="") #To remove all the special characters from Tweets
#PA$text <- hunspell_stem(PA$text)
PA_df<- data_frame(line=1, text=PA$text) 
print(head(PA_df))

#---------------------------- Tokenization -----------------------------------
library(tidytext)
library(dplyr)
library(stringr)
data(stop_words)

#break the text into individual tokens and stem
PA_df<- PA_df %>% 
  unnest_tokens(word, text) %>% 
  filter(!str_detect(word, "^[0-9]*$")) %>%
  filter(!str_detect(word, "this")) %>%
  filter(!str_detect(word, "because")) %>%
  filter(!str_detect(word, "they")) %>%
  filter(!str_detect(word, "very")) %>%
  filter(!str_detect(word, "lan")) %>%
  filter(!str_detect(word, "emoji_face_with_tears_of_joy")) %>%
  filter(!str_detect(word, "emoji_rolling_on_the_floor_laughing")) %>%
  filter(!str_detect(word, "emoji.*")) %>%
  filter(!str_detect(word, "bitcoin")) %>%
  mutate(word = wordStem(word)) %>%
  anti_join(stop_words)  

PA_df%>% count(word, sort=TRUE)

#---------------------------- Buiding the Model -----------------------------------
## Building the model
set.seed(321)
model  <- BTM(PA_df, k = 3, beta = 0.01, iter = 1000, trace = 100, background = TRUE)

## Inspect the model - topic frequency + conditional term probabilities
model$theta

topicterms <- terms(model, top_n = 5)
topicterms