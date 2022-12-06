import praw
import wordfreq
from PyDictionary import PyDictionary

# makes it a little cleaner
dictionary = PyDictionary()

reddit = praw.Reddit(
    client_id = "",
    client_secret = "",
    password = "",
    user_agent = "",
    username = ""
)

# sets subreddit for bot to run in
subreddit = reddit.subreddit("")

# creates the template for the bot to use in its response when it detects uncommon words
reply_template = """I am a bot and I noticed that you\'ve used one or more uncommon words in
your comment. To help make Reddit more accessible to those of different backgrounds, here 
are definitions for those words: \n\n"""

# will add words as necessary if the bot regularly runs into particular words which it should
# not be defining
word_blacklist = []

# sets the range of word frequencies that count as uncommon
# a minimum frequency exists to ensure all the words are real words
min_freq = 0.00000001
max_freq = 0.000001

# the PyDictionary module outputs for non-words can be a bit difficult to work with, so this
# prevents it from happening by ensuring that only real words are passed through meaning()
def is_word(word):
    try:
        is_word = dictionary.meaning(word, disable_errors=True)
    except:
        return False
    else:
        return bool(is_word)


def uncommon_words(text):
    print('function running')
    text = text.lower().split()
    unfiltered_uncommon_words = set()
    uncommon_words_defined = {}
    for i in text:
        i_freq = wordfreq.word_frequency(i, "en")
        if i_freq < max_freq and i_freq > min_freq:
            unfiltered_uncommon_words.add(i)
    for i in unfiltered_uncommon_words:
        if is_word(i):
            uncommon_words_defined.update({i: dictionary.meaning(i)})
    return uncommon_words_defined

# continuously searches all new comments in a given subreddit
# if a comment with uncommon words is found, this function will format a reply
# and submit it 
for comment in subreddit.stream.comments():
    reply_defs = ''
    uncommon_words_defined = uncommon_words(comment.body)
    for word, pos_dict in uncommon_words_defined.items():
        for pos, definitions in pos_dict.items():
            formatted_word_def = (f"{word} ({pos.lower()}): {'; '.join(definitions)}")
            print(formatted_word_def)
            reply_defs += formatted_word_def + '\n\n'
    # this will eventually be placed with a more sophisticated logging system, but in the
    # meantime, it just ensures the bot does not try to respond to its own comments
    if 'bot' not in comment.body:
        # combines comment templates to create the final reply and then submits it
        comment.reply(reply_template + reply_defs.rstrip())
        print('\n*******Replied to comment**********\n')