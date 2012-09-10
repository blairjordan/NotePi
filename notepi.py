#!/usr/bin/env python
import pygame, sys, time, twitter, sqlite3 as lite
from pygame.locals import *
from array import *
from cStringIO import StringIO
from tokenize import generate_tokens

# Path to wav files
wav_path = '/home/pi/notepi/wav/'

# Type your API auth details here
api = twitter.Api(consumer_key='', consumer_secret='',
access_token_key='', access_token_secret='')

# Initialize audio
pygame.init()
pygame.mixer.quit() 
pygame.mixer.init(22050, -16, 2, 4096)

# Connect to SQLite DB
con = None

try:
	con = lite.connect('notepi.db')
except lite.Error, e:
	print "Error %s:" % e.args[0]
	sys.exit

# Check whether tweet has already been played by checking the DB
def is_played( tweet_id ):
	played = None

	try:
        	cur = con.cursor()
        	cur.execute("SELECT COUNT(*) FROM played WHERE tweet_id=:tweet_id", {"tweet_id": tweet_id})
        	count = cur.fetchone()[0]
		if count != 0:
			played = True
		con.commit()

	except lite.Error, e:
        	print "Error %s:" % e.args[0]
        	sys.exit(1)

	return played

# Mark a tweet as 'played' by recording the tweet id
def mark_played( tweet_id ):
	try:
		cur = con.cursor()
		cur.execute("INSERT INTO played(tweet_id) VALUES(?)", (tweet_id,))
		con.commit()

	except lite.Error, e:
		print "Error %s:" % e.args[0]
		sys.exit(1)

	return

# Return the next Twitter sequence to play
def get_next_tweet():
	tweet_text = None
	statuses = api.GetMentions()

	for tweet in statuses:

		if not is_played( tweet.id ):
			mark_played( tweet.id )
			tweet_text = tweet.text
			break

	return tweet_text

# Return a list of notes contained in a chord
def get_chord_notes( chord_str ):

	chord = list()

        notes = ['C3','Db3','D3','Eb3','E3','F3','Gb3'
,'G3','Ab3','A3','Bb3','B3','C4']

        for note in notes:
		found = chord_str.find(note)
                if found >= 0:
                        chord.append(note)

        return chord

tweet = get_next_tweet()

if tweet:
	STRING = 1
	# Extract a list of chords from the tweet
	chords = list(token[STRING] for token 
		in generate_tokens(StringIO(tweet).readline)
		if token[STRING])

	for chord in chords:
		notes = get_chord_notes(chord)

		# Play all the notes in the chord
		for note in notes:
			note_wav = "%s%s.wav" % (wav_path, note)
			sound = pygame.mixer.Sound(note_wav)
			sound.play()
		time.sleep(1.5)

if con:
	con.close()

sys.exit()
