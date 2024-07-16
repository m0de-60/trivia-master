#! /usr/bin/python3
# Mode60 Ultra-beta Prototype
# ======================================================================================================================
# Title.............: 'Trivia-Master I'
# Filename..........: trivia.py (zCore plugin module)
# Version...........: 1.00
# Author............: Neo Nemesis
# Description.......: Interactive trivia game
# Remarks...........: This is the prototype-II build of zCore plugin module
# Author Notes......: This is just a ultra-beta demonstration and not an official release.
# ======================================================================================================================
# Import whatever python stuff is needed here
import sys_zcore as pc  # Required for sys_zcore scripting features
import asyncio  # Required
import logging  # Optional, only if you want to log debug (mprint) to log.txt file
# Other Imports (as needed)
import time  # For Trivia
import random  # For Trivia
import threading  # For Trivia

# declare data map
pdata = {}

# Set up logging (optional)
logging.basicConfig(filename='./zcorelog.txt', level=logging.DEBUG)  # For error and debug logging
pdata['debuglog'] = 'on'  # turn 'on' for testing, otherwise 'off'

# For remote and terminal loading (required for plugin modules)
def plugin_chk_():
    return True

# For start up loading (required if importing system module functions)
def system_req_():
    return 'sys_zcore'

def plugin_exit_():
    global pdata
    mprint(f'Shutting down...')
    pdata = {}

# Start up init
def plugin_init_():
    global pdata  # always call this first from every function

    # -[ Plugin Title ]-------------------------------------------------------------------------------------------------
    pdata['ptitle'] = 'Trivia Master'  # title of plugin (anything)
    pdata['pversion'] = '1.00'  # version (anything)
    pdata['pauthor'] = 'Neo Nemesis'  # who wrote it
    pdata['mreqver'] = '0.1x'

    # ############## TRIVIA CONTROL ################
    # Trivia Control
    pdata['trivia'] = False  # Automatically start trivia (False to disable)
    # Trivia Control
    # ##############################################

    # ############## MODULE PRINT ################
    pdata['moduleprint'] = True  # Screen printing, True For testing, normally False
    # ############################################

    # -[ Assign Data to map from trivia.cnf ] ----------------------------------------------------------------------------

    # Trivia stuff
    pdata['startmode'] = 'random'  # change to different start modes, random, 123, randcat
    pdata['categories'] = pc.cnfread('trivia.cnf', 'trivia', 'categories').lower()  # category list
    pdata['category'] = pdata['categories'].split(',')  # individual category name pdata['category'][x]
    pdata['defmode'] = 'random'  # default start mode
    # IRC stuff
    pdata['serverlist'] = pc.cnfread('trivia.cnf', 'trivia', 'serverlist').lower()  # server list
    pdata['server'] = pdata['serverlist'].split(',')
    # run thru the list for server and decalre channel specific data
    for x in range(len(pdata['server'])):
        server = pdata['server'][x]
        # declare channel data
        pdata[server, 'channels'] = pc.cnfread('trivia.cnf', server, 'channels').lower()
        pdata[server, 'botname'] = pc.cnfread('zcore.cnf', server, 'botname')
        # declare each server/channel
        pdata[server, 'channel'] = pdata[server, 'channels'].split(',')
        # trivia stuff
        for y in range(len(pdata[server, 'channel'])):
            # check if channel data exists, if not create entry
            # chann = pdata[server, 'channel'][y].lower()
            # if pc.cnfexists('trivia.cnf', server + '_' + chann.decode(), 'cache') is False:
            #    pc.cnfwrite('trivia.cnf', server + '_' + chann.decode(), 'cache', '0')
            # set channel stats
            chan = pdata[server, 'channel'][y].replace('#', '')
            chan = chan.lower()
            pdata[server, chan] = {}
            pdata[server, chan]['data'] = server + '_' + chan
            if pc.cnfexists('trivia.cnf', pdata[server, chan]['data'], 'cache') is False:
                pc.cnfwrite('trivia.cnf', pdata[server, chan]['data'], 'cache', '0')
            pdata[server, chan]['trivia'] = False  # Is trivia playing True or not playing False
            pdata[server, chan]['game'] = '0'  # current game logic position
            pdata[server, chan]['mode'] = '0'  # current game mode (random, 123, randcat)
            pdata[server, chan]['category'] = '0'  # current category
            pdata[server, chan]['file'] = '0'  # category filename (no path)
            pdata[server, chan]['question'] = '0'  # current question
            pdata[server, chan]['answer'] = '0'  # current answer
            pdata[server, chan]['hints'] = -1  # Keeps track of how many hints (max 3)
            pdata[server, chan]['hint'] = '0'  # Keeps track of actual hint (*****)
            pdata[server, chan]['qnum'] = 0  # Keeps track of the question number
            pdata[server, chan]['timer'] = '0'  # For timer
            pdata[server, chan]['timerun'] = False  # For timer
            pdata[server, chan]['thread'] = '0'  # For timer
            pdata[server, chan]['pointimer'] = '0'  # for keeping track of points decline as hints are revealed
            pdata[server, chan]['points'] = '0'  # keeps track of winnable points
            pdata[server, chan]['response'] = '0'  # keeps track of response times
            pdata[server, chan]['streakname'] = '0'
            pdata[server, chan]['streakcount'] = 0
            continue
        continue

    # data map complete
    mprint(f'{pdata['ptitle']} * Version: {pdata['pversion']} By: {pdata['pauthor']} - Loaded successfully.')

# Screen printing [*REQUIRED FUNCTION*]---------------------------------------------------------------------------------
# For module printing and testing purposes after plugin is loaded use this instead of print()
# function name 'mprint' can be anything you define
# set pdata['moduleprint'] = False above to disable
def mprint(string):
    global pdata  # always call this first from every function
    if pdata['moduleprint'] is True:
        print(f'[T-M] * {string}')  # This can be print(f'{string}') or print(f'Anything: {string}')
    # logging is optional
    if pdata['debuglog'] == 'on':
        logging.debug(f'[T-M] * {string}')  # Make sure to copy the same text format for cleaner logging!
    return
# End mprint() ---------------------------------------------------------------------------------------------------------

# EVENTS ---------------------------------------------------------------------------------------------------------------

# ----------------------------------------------------------------------------------------------------------------------
# evt_join('servername', b':Username!~Host@mask.net JOIN :#Channel')
# JOIN
async def evt_join(server, joindata):
    global pdata
    jdata = joindata.split(b' ')
    # username = pc.gettok(jdata[0], 0, b'!')
    # username = username.replace(b':', b'')
    channel = jdata[2].replace(b':', b'')
    dchannel = channel.decode()
    dchannel = dchannel.lower()
    chan = dchannel.replace('#', '')

    if server not in pdata['server']:
        return

    if dchannel not in pdata[server, 'channel']:
        return

    if pdata[server, chan]['trivia'] is True:
        if pdata[server, chan]['game'] == 'time':
            ctime = 20 - round(time.time() - float(pdata[server, chan]['timer']))
            time.sleep(0.5)
            pc.privmsg_(server, channel, '\x0315,1Welcome to\x0310,1 ' + channel.decode() + ', \x0315,1Next question in\x02\x036,1 ' + str(ctime) + ' \x02\x0315,1seconds.')
        if pdata[server, chan]['game'] == 'play':
            time.sleep(0.5)
            hintmsg = pdata[server, chan]['hint']
            if pdata[server, chan]['hints'] > 1:
                hintmsg = pdata[server, chan]['hint2']
            if pdata[server, chan]['hints'] > 2:
                hintmsg = pdata[server, chan]['hint3']
            pc.privmsg_(server, channel, '\x0315,1Welcome to\x0310,1 ' + channel.decode() + ', \x02\x038,1CURRENT TRIVIA:\x02\x0315,1 ' + pdata[server, chan]['question'] + ' \x02\x038,1HINT:\x02\x0310,1 ' + str(hintmsg) + '\x03')
            return
    else:
        return

# ----------------------------------------------------------------------------------------------------------------------
# evt_privmsg('servername', b':Username!~Host@mask.net PRIVMSG target :Message data')
# PRIVMSG
# (( TRIVIA COMMANDS AND CORRECT ANSWER INPUT ))
async def evt_privmsg(server, message):
    global pdata  # always call this first from every function
    mdata = message.split(b' ')
    umsg = pc.gettok(message, 2, b':')
    umsg = umsg.decode()
    umsg = umsg.lower()
    # split up the message into single words and values
    username = pc.gettok(mdata[0], 0, b'!')
    username = username.replace(b':', b'')
    dusername = username.decode()
    dusername = dusername.lower()
    channel = mdata[2]
    dchannel = channel.decode()
    dchannel = dchannel.lower()
    chan = dchannel.replace('#', '')

    if server not in pdata['server']:
        return

    if dchannel not in pdata[server, 'channel'] and b'#' in mdata[2]:
        return

    # mprint(f'umsg: {umsg}')

    # keep data case lower

    # /privmsg commands
    if b'#' not in mdata[2] and pc.is_admin(server, dusername) is True:
        # --------------------------------------------------------------------------------------------------------------
        # /privmsg botname rem-q category X
        # Removes question #X from the specified category
        if mdata[3].lower() == b':rem-q' and pc.is_botmaster(dusername) is True:
            if len(mdata) != 6:
                pc.notice_(server, username, '[T-M] * ERROR: Invalid syntax. /msg <botname> rem-q X')
                return
            mdata5 = mdata[5].decode()
            if mdata5.isnumeric() is False or isinstance(str(mdata5), float) is True:
                pc.notice_(server, username, '[T-M] * ERROR: Invalid syntax. /msg <botname> rem-q X')
                return
            cat = mdata[4].decode()
            filename = './qafiles/' + cat.lower() + '.txt'
            if pc.iistok(pdata['categories'], cat.lower(), ',') is False or pc.isfile(filename) is False:
                pc.notice_(server, username, '[T-M] * ERROR: Category ' + cat.lower() + ' not found.')
                return
            qnum = mdata5
            file = open(filename, 'r')
            filelines = file.readlines()
            if int(qnum) > len(filelines) or int(qnum) <= 0:
                pc.notice_(server, username, '[T-M] * ERROR: Question No.' + str(qnum) + ' exceeds the category ' + cat.lower() + '. This category contains: ' + str(len(filelines)) + ' questions')
                return
            file = open(filename, 'r')
            filelines = file.readlines()
            file.close()
            open(filename, 'w').close()
            file = open(filename, 'a')
            for x in range(len(filelines)):
                if x + 1 == int(qnum):
                    continue
                file.write(filelines[x])
                continue
            pc.notice_(server, username, '[T-M] * Question No.' + str(qnum) + ' successfully removed from category ' + cat.lower() + '.')
            mprint(f'Trivia question No.{str(qnum)} has been removed from ./qafiles/{cat.lower()}.txt by {username.decode()} - {pc.cdate()} - {pc.ctime()}')
            return
        # --------------------------------------------------------------------------------------------------------------
        # /privmsg botname add-q category ^question text`answer text
        # Add a question and answer to specified category (bot master only)
        if mdata[3].lower() == b':add-q' and pc.is_botmaster(dusername) is True:
            if len(mdata) < 6 or pc.numtok(message, b'^') != 2:
                pc.notice_(server, username, '[T-M] * ERROR: Invalid syntax. /msg <botname> add-q ^question text goes here here`the answer text')
                return
            if pc.numtok(message, b'^') != 2:
                pc.notice_(server, username, '[T-M] * ERROR: Invalid syntax. /msg <botname> add-q ^question text goes here here`the answer text')
                return
            cat = mdata[4].decode()
            filename = './qafiles/' + cat.lower() + '.txt'
            new_q = pc.gettok(message, 1, b'^')
            if pc.numtok(new_q, b'`') != 2:
                pc.notice_(server, username, '[T-M] * ERROR: Invalid syntax. /msg <botname> add-q ^question text goes here here`the answer text')
                return
            if pc.iistok(pdata['categories'], cat.lower(), ',') is False or pc.isfile(filename) is False:
                pc.notice_(server, username, '[T-M] * ERROR: Category ' + cat.lower() + ' not found.')
                return
            print(f'Here')
            new_q = new_q.decode()
            file = open(filename, 'a')
            file.write('\n' + new_q)
            file.close()
            # pc.txtwrite(filename, new_q)
            pc.notice_(server, username, '[T-M] * New question successfully added to category ' + cat.lower() + '.')
            mprint(f'New trivia question added to ./qafiles/{cat.lower()}.txt by {username.decode()} - {pc.cdate()} - {pc.ctime()}')
            return
        # --------------------------------------------------------------------------------------------------------------
        # /privmsg botname clean <category>
        # /privmsg botname clean all
        # This cleans the specified category file, and stores all bad lines in a seperate log for review
        if mdata[3].lower() == b':clean' and pc.is_botmaster(dusername) is True:
            if len(mdata) < 5:
                pc.notice_(server, username, '[T-M] * ERROR: Invalid syntax. /msg <botname> clean <category>')
                return
            cat = mdata[4].decode()
            if cat.lower() == 'all':
                pc.notice_(server, username, '[T-M] * Checking all category files for errors...')
                await trivia(server, dusername, 'clean', 'all')
                return
            filename = './qafiles/' + cat.lower() + '.txt'
            if pc.isfile(filename) is False:
                pc.notice_(server, username, '[T-M] * ERROR: Category ' + cat.lower() + ' file not found.')
                return
            else:
                pc.notice_(server, username, '[T-M] * Checking category ' + cat.lower() + ' for errors...')
                await trivia(server, dusername, 'clean', cat.lower())
                return
        return

    # ------------------------------------------------------------------------------------------------------------------
    # !testing (botmaster and admin only)
    if mdata[3].lower() == b':!testing' and pc.is_admin(server, dusername) is True:
        pc.privmsg_(server, channel, 'Testing ABC')

    # ------------------------------------------------------------------------------------------------------------------
    # !trivia cammond (!trivia on/off category) (botmaster and admin only)
    elif mdata[3].lower() == b':!trivia' and len(mdata) > 4:

        if pc.is_admin(server, dusername) is False:
            return

        # !trivia skip
        if mdata[4].lower() == b'skip' and pdata[server, chan]['trivia'] is True:
            if pdata[server, chan]['game'] == 'play':
                await trivia(server, channel.decode(), 'skip')
                return
            if pdata[server, chan]['game'] == 'time':
                ctime = 20 - round(time.time() - float(pdata[server, chan]['timer']))
                time.sleep(0.4)
                pc.privmsg_(server, channel, '\x0315,1New question coming up in\x02\x036,1 ' + str(ctime) + ' \x02\x03seconds.')
                return

        if mdata[4].lower() == b'skip' and pdata[server, chan]['trivia'] is False:
            time.sleep(0.5)
            pc.privmsg_(server, channel, 'Trivia is not currently enabled.')
            return

        # !trivia on
        if mdata[4].lower() == b'on':
            if pdata[server, chan]['trivia'] is True:
                time.sleep(0.5)
                pc.notice_(server, username, 'Trivia is already enabled.')
            else:
                pdata[server, chan]['trivia'] = True
                time.sleep(0.5)
                # pc.privmsg_(server, channel, 'Trivia has been enabled.')
                await trivia(server, dchannel, 'start')

        # !trivia off
        if mdata[4].lower() == b'off':
            if pdata[server, chan]['trivia'] is False:
                time.sleep(0.5)
                pc.notice_(server, username, 'Trivia is already disabled.')
            else:
                pdata[server, chan]['trivia'] = False
                time.sleep(0.5)
                # pc.notice_(server, username, 'Trivia has been disabled.')
                await trivia(server, dchannel, 'stop')

    # ------------------------------------------------------------------------------------------------------------------
    # !myscore - displays user score and statistics
    elif mdata[3].lower() == b':!myscore':
        if pdata[server, chan]['trivia'] is False:
            return
        if pc.cnfexists('trivia.cnf', server + '_' + chan, dusername) is False:
            pc.privmsg_(server, channel, str(username.decode()) + 'you have not played yet.')
            return
        score = '\x037,1[\x036,1Score:\x038,1 ' + str(playerstats(server, channel, dusername, 'score')) + '\x037,1]'
        wins = '\x037,1[\x036,1Wins:\x038,1 ' + str(playerstats(server, channel, dusername, 'wins')) + '\x037,1]'
        streak = '\x037,1[\x036,1Longest Streak:\x038,1 ' + str(playerstats(server, channel, dusername, 'streak')) + '\x037,1]'
        best = '\x037,1[\x036,1Best Time:\x038,1 ' + str(playerstats(server, channel, dusername, 'best')) + '\x037,1]\x03'
        stats = '\x02\x0315,1PLAYER SCORE:\x02\x0310,1    ' + username.decode() + '    ' + score + wins + streak + best
        # add stuff here so can be toggled from privmsg or notice
        time.sleep(0.5)
        pc.privmsg_(server, channel, stats)
        return

    # ------------------------------------------------------------------------------------------------------------------
    # User answer input for Trivia
    else:
        if pdata[server, chan]['game'] == 'play':
            if umsg == pdata[server, chan]['answer'].lower():
                if isplayer(server, channel, dusername) is False:
                    playerstats(server, channel.decode(), dusername, 'new')
                # pdata[server, chan]['thread'].join()
                # pc.privmsg_(server, channel, 'Correct')
                totaltime = round(time.time() - pdata[server, chan]['response'], 2)
                pdata[server, chan]['game'] = 'win'
                pdata[server, chan]['timerun'] = False
                pc.privmsg_(server, channel, '\x02\x0310,1' + username.decode() + '\x02   \x0315,1Wins\x037,1 ' + str(pdata[server, chan]['points']) + ' \x0315,1points!    \x02\x038,1ANSWER ---->\x02 ' + pdata[server, chan]['answer'] + '    \x02\x0315,1TIME:\x02\x037,1 ' + str(totaltime) + ' seconds\x03')
                wins = int(playerstats(server, channel, dusername, 'wins')) + 1
                playerstats(server, channel, dusername, 'wins', 'c', str(wins))
                points = int(playerstats(server, channel, dusername, 'score')) + int(pdata[server, chan]['points'])
                playerstats(server, channel, dusername, 'score', 'c', str(points))
                if playerstats(server, channel, dusername, 'best') == 'NA' or totaltime < float(playerstats(server, channel, dusername, 'best')):
                    pc.privmsg_(server, channel, '\x02\x0310,1' + username.decode() + '\x02   \x037,1Set a new best time record!   \x02\x038,1>\x036,1 ' + str(totaltime) + ' seconds\x038,1 <\x02\x03')
                    playerstats(server, channel, dusername, 'best', 'c', str(totaltime))
                # set up for winning streak
                if pdata[server, chan]['streakname'] != dusername:
                    pdata[server, chan]['streakcount'] = 0
                pdata[server, chan]['streakname'] = dusername
                pdata[server, chan]['streakcount'] += 1
                if pdata[server, chan]['streakcount'] > int(playerstats(server, channel.decode(), dusername, 'streak')):
                    playerstats(server, channel.decode(), dusername, 'streak', 'c', str(pdata[server, chan]['streakcount']))
                if pdata[server, chan]['streakcount'] > 1:
                    time.sleep(0.2)
                    pc.privmsg_(server, channel, '\x02\x0310,1' + username.decode() + '\x02   \x0315,1Won\x02\x036,1 ' + str(pdata[server, chan]['streakcount']) + ' \x02\x0315,1in a row!   \x02\x037,1 * WINNING STREAK *\x02\x03')
                time.sleep(1.25)
                freetriv(server, dchannel)
                await trivia(server, dchannel, 'next')
# End of EVENTS --------------------------------------------------------------------------------------------------------

# ======================================================================================================================
# Main trivia function

async def trivia(server, channel, opt, cat='', opt2=''):
    global pdata
    chan = str(channel.replace('#', '')).lower()
    cmsg = ''

    # ------------------------------------------------------------------------------------------------------------------
    # Start trivia
    # trivia(server, channel, 'start', 'mode', 'category')
    if opt == 'start':
        mprint(f'TRIVIA STARTED: {server} {channel} {cat}')
        # pdata[server, chan]['game'] = '0'
        if cat == '' or cat == 'random':
            pdata[server, chan]['mode'] = 'random'
            pdata[server, chan]['trivia'] = True
            cmsg = 'Random Trivia'
        elif cat == '123':
            pdata[server, chan]['mode'] = '123'
            cmsg = '123 Trivia'
            if opt2 != '':
                pdata[server, chan]['category'] = opt2
        elif cat == 'randcat':
            pdata[server, chan]['mode'] = 'randcat'
            cmsg = 'Random Category'
            if opt2 != '':
                pdata[server, chan]['category'] = opt2
        pc.privmsg_(server, channel.encode(), '\x02\x0314,1Trivia Master \x036,1   v' + pdata['pversion'] + '\x02\x0315,1    Now running:\x037,1 \x02' + cmsg + '\x02\x03')
        time.sleep(1)
        pdata[server, chan]['game'] = 'time'
        # mprint(f'AWAIT NEXT')
        await trivia(server, channel, 'next')

    # ------------------------------------------------------------------------------------------------------------------
    # stop trivia
    # trivia(server, channel, 'stop')
    if opt == 'stop':
        mprint(f'TRIVIA STOPPED: {server} {channel}')
        pdata[server, chan]['timerun'] = False
        pdata[server, chan]['game'] = '0'
        pdata[server, chan]['mode'] = '0'
        freetriv(server, channel)
        pdata[server, chan]['streakname'] = '0'
        pdata[server, chan]['streakcount'] = 0
        pc.privmsg_(server, channel.encode(), '\x02\x0314,1Trivia Master \x036,1   v' + pdata['pversion'] + '\x02\x0315,1    Stopped.\x03')
        return
    # ------------------------------------------------------------------------------------------------------------------
    # next question
    # trivia(server, channel, 'next')
    if opt == 'next':
        # mprint(f'BEGIN NEXT')
        pdata[server, chan]['game'] = 'time'
        if pdata[server, chan]['mode'] == 'random':
            # mprint(f'BEGIN NEXT RANDOM')
            # set category data
            catnum = random.randint(0, len(pdata['category']))
            catnum = catnum - 1
            # mprint(f'catnum: {catnum}')
            pdata[server, chan]['category'] = pdata['category'][catnum]
            filename = './qafiles/' + pdata['category'][catnum] + '.txt'
            # mprint(f'file: {filename}')
            file = open(filename, 'r')
            filelines = file.readlines()
            pdata[server, chan]['qnum'] = random.randint(0, len(filelines))
            qnum = pdata[server, chan]['qnum'] - 1
            # mprint(f'qnum: {qnum}')
            # need to fix this
            pdata[server, chan]['question'] = pc.gettok(filelines[qnum], 0, '`')
            pdata[server, chan]['answer'] = pc.gettok(filelines[qnum], 1, '`').replace('\n', '')
            pdata[server, chan]['points'] = 10000  # Starting points at 1000

            mprint(f'CAT: {pdata[server, chan]['category']} NUM: {pdata[server, chan]['qnum']}')
            mprint(f'File: {filename}')
            mprint(f'Q: {pdata[server, chan]['question']}')
            mprint(f'A: {pdata[server, chan]['answer']}')

            # set hint data
            pdata[server, chan]['hints'] = -1

            # pdata[server, chan]['hint'] = hint_gen(pdata[server, chan]['answer'], 0)
            # mprint(f'Hint 0: {pdata[server, chan]['hint']}')
            pdata[server, chan]['hint'] = randomizer(pdata[server, chan]['answer'], 0)

            # pdata[server, chan]['hint1'] = hint_gen(pdata[server, chan]['answer'], 1, pdata[server, chan]['hint'])
            # mprint(f'Hint 1: {pdata[server, chan]['hint1']}')
            pdata[server, chan]['hint1'] = randomizer(pdata[server, chan]['answer'], 1, pdata[server, chan]['hint'])

            # pdata[server, chan]['hint2'] = hint_gen(pdata[server, chan]['answer'], 2, pdata[server, chan]['hint1'])
            # mprint(f'Hint 2: {pdata[server, chan]['hint2']}')
            pdata[server, chan]['hint2'] = randomizer(pdata[server, chan]['answer'], 2, pdata[server, chan]['hint1'])

            # pdata[server, chan]['hint3'] = hint_gen(pdata[server, chan]['answer'], 3, pdata[server, chan]['hint2'])
            # mprint(f'Hint 3: {pdata[server, chan]['hint3']}')
            pdata[server, chan]['hint3'] = randomizer(pdata[server, chan]['answer'], 3, pdata[server, chan]['hint2'])

            # timer data

            pdata[server, chan]['timerun'] = True
            pdata[server, chan]['timer'] = time.time()
            pc.privmsg_(server, channel.encode(), '\x0315,1Next question in\x02\x036,1 20 \x02\x0315,1seconds...\x03')
            pdata[server, chan]['thread'] = threading.Thread(target=timer, args=(server, channel,), daemon=True)
            pdata[server, chan]['thread'].start()

    # ------------------------------------------------------------------------------------------------------------------
    # ask question
    # trivia(server, channel, 'ask')
    if opt == 'ask':
        pdata[server, chan]['game'] = 'play'
        pdata[server, chan]['response'] = time.time()
        pdata[server, chan]['pointimer'] = time.time()
        pc.privmsg_(server, channel.encode(), '\x02\x0310,1[\x02No.\x02' + str(pdata[server, chan]['qnum']) + ' ' + pdata[server, chan]['category'] + ']\x0315,1   \x02 ' + pdata[server, chan]['question'] + '\x03')
        pc.privmsg_(server, channel.encode(), '\x0315,1First hint in\x02\x036,1 20 \x02\x0315,1seconds...\x03')

        # testing
        # mprint(f'Q: {pdata[server, chan]['question']}')
        # mprint(f'A: {pdata[server, chan]['answer']}')

        # timer info
        pdata[server, chan]['timerun'] = True
        pdata[server, chan]['timer'] = time.time()
        pdata[server, chan]['hints'] = 0
        pdata[server, chan]['thread'] = threading.Thread(target=timer, args=(server, channel,), daemon=True)
        pdata[server, chan]['thread'].start()

    # ------------------------------------------------------------------------------------------------------------------
    # give hints
    # trivia(server, channel, 'hint')
    if opt == 'hint':

        # determine points (old way, to be removed)
        # math = int(pdata[server, chan]['points']) - 2500
        # pdata[server, chan]['points'] = str(math)

        pdata[server, chan]['game'] = 'play'
        pdata[server, chan]['hints'] += 1
        # create hint!!
        hintx = 'hint' + str(pdata[server, chan]['hints'])
        hint = pdata[server, chan][hintx]
        pc.privmsg_(server, channel.encode(), '\x02\x0315,1Hint # ' + str(pdata[server, chan]['hints']) + ':\x02\x0310,1 ' + hint + '\x03')
        # hint = hint_gen(ans, int(pdata[server, chan]['hints']), hnt)
        # pc.privmsg_(server, channel.encode(), 'Hint #' + str(pdata[server, chan]['hints']) + ': ' + hint)

        # set timer
        pdata[server, chan]['timerun'] = True
        pdata[server, chan]['timer'] = time.time()
        pdata[server, chan]['thread'] = threading.Thread(target=timer, args=(server, channel,), daemon=True)
        pdata[server, chan]['thread'].start()

    # ------------------------------------------------------------------------------------------------------------------
    # time is up
    # trivia(server, channel, 'timeup')
    if opt == 'timeup':
        pdata[server, chan]['game'] = 'timeup'
        pdata[server, chan]['timerun'] = False
        pdata[server, chan]['streakname'] = '0'
        pdata[server, chan]['streakcount'] = 0
        pc.privmsg_(server, channel.encode(), '\x02\x037,1Time is up!\x02\x0315,1    The answer is:\x02\x036,1 ' + pdata[server, chan]['answer'] + '\x03\x02')
        time.sleep(1)
        freetriv(server, channel)
        await trivia(server, channel, 'next')

    # ------------------------------------------------------------------------------------------------------------------
    # skip question
    # trivia(server, channel, 'skip')
    if opt == 'skip':
        pdata[server, chan]['game'] = 'skip'
        pdata[server, chan]['timerun'] = False
        pc.privmsg_(server, channel.encode(), '\x0315,1Skipping question...\x03')
        time.sleep(1)
        freetriv(server, channel)
        await trivia(server, channel, 'next')

    # ------------------------------------------------------------------------------------------------------------------
    # Check category file(s) for issues or errors and store bad lines in seperate log file
    # trivia(server, <dusername>, 'clean', 'category')
    if opt == 'clean':
        # duser = channel.decode()
        # duser = duser.lower()
        duser = channel
        totalerr = 0
        if cat == 'all':
            # pc.notice_(server, duser.encode(), 'Check All')
            mprint('Checking all trivia categories for errors...')
            for x in range(len(pdata['category'])):
                filename = './qafiles/' + pdata['category'][x] + '.txt'
                mprint('Checking file ' + cat.lower() + '.txt for trivia errors...')
                errnum = t_file_clean(filename)
                if errnum != 0:
                    mprint('Error check for ' + pdata['category'][x] + '.txt complete. Errors removed: ' + str(errnum) + ' and stored in ./qafiles/qlog.txt')
                else:
                    mprint('Error check for ' + pdata['category'][x] + '.txt complete. Errors found: ' + str(errnum))
                totalerr = totalerr + errnum
                continue
            mprint('Error checking for all trivia categories is complete. Errors found and removed: ' + str(totalerr))
            pc.notice_(server, duser.encode(), '[T-M] * Check All complete. Errors found and removed: ' + str(totalerr))
            return
        else:
            filename = './qafiles/' + cat.lower() + '.txt'
            # pc.notice_(server, duser.encode(), 'Checking ' + cat.lower())
            mprint('Checking file ' + cat.lower() + '.txt for trivia errors...')
            errnum = t_file_clean(filename)
            if errnum != 0:
                mprint('Error check for ' + cat.lower() + '.txt complete. Errors removed: ' + str(errnum) + ' and stored in ./qafiles/qlog.txt')
                pc.notice_(server, duser.encode(), '[T-M] * Checking complete. Errors removed: ' + str(errnum))
            else:
                mprint('Error check for ' + cat.lower() + '.txt complete. Errors found: ' + str(errnum))
                pc.notice_(server, duser.encode(), '[T-M] * Checking complete. Errors found: ' + str(errnum))
            return

# End trivia() =========================================================================================================

# ======================================================================================================================
# Trivia category file cleaner
# File must exist in qafiles folder in zCore directory. zcore/qafiles/filename.txt
def t_file_clean(filename):
    # Scan the file for improperly formatted questions
    fname = filename
    file = open(fname, 'r')
    filelines = file.readlines()
    # properly formatted questions are stored in the 'clean file'
    c_file = open('./qafiles/cleanfile.txt', 'a')
    # improperly formatted questions are removed and stored in the qlog.txt
    qlog = open('./qafiles/qlog.txt', 'a')
    # how many errors are found? Starts with 0
    errnum = 0
    # scanning for and removing improperly formatted questions
    for x in range(len(filelines)):
        if pc.numtok(filelines[x], '`') != 2:
            errnum += 1
            qlog.write(filelines[x])
            continue
        else:
            c_file.write(filelines[x])
            continue
    file.close()
    c_file.close()
    qlog.close()
    # saving the 'cleaned list' as the category file.
    open(fname, 'w').close()
    file = open(fname, 'a')
    c_file = open('./qafiles/cleanfile.txt', 'r')
    filelines = c_file.readlines()
    # errnum = 0
    for x in range(len(filelines)):
        # errnum += 1
        file.write(filelines[x])
        continue
    c_file.close()
    pc.remfile('./qafiles/cleanfile.txt')
    # returns the number of errors found
    return errnum

# ----------------------------------------------------------------------------------------------------------------------
# free up resources (test)
def freetriv(server, channel):
    global pdata
    chan = channel.lower()
    chan = chan.replace('#', '')
    pdata[server, chan]['question'] = '0'
    pdata[server, chan]['answer'] = '0'
    pdata[server, chan]['hints'] = -1  # Keeps track of how many hints (max 3)
    pdata[server, chan]['hint'] = '0'  # Keeps track of actual hint (*****)
    pdata[server, chan]['qnum'] = 0
    pdata[server, chan]['timer'] = '0'  # For timer
    pdata[server, chan]['timerun'] = False  # For timer
    pdata[server, chan]['thread'] = '0'  # For timer
    pdata[server, chan]['points'] = '0'
    pdata[server, chan]['response'] = '0'
    return

# ======================================================================================================================
# Trivia timer
# Controls the game position and turn
# async def timer(server, channel):
def timer(server, channel):
    global pdata
    chan = channel.replace('#', '')
    chan = chan.lower()
    # while pdata[server, chan]['timerun'] is True:
    while True:
        if pdata[server, chan]['timerun'] is False:
            break

        # if pdata[server, chan]['game'] == '0':  # This is useful or not idk
        #    pdata[server, chan]['timerun'] = False
        #    break

        time.sleep(0.1)
        # after timer sleep, check stats

        # if pdata[server, chan]['mode'] == '0' or pdata[server, chan]['game'] == '0':
        #     pdata[server, chan]['timerun'] = False
        #     break
        if pdata[server, chan]['timerun'] is False:
            break

        # points decrease every 5 seconds until time is up
        if pdata[server, chan]['game'] == 'play':
            if pdata[server, chan]['pointimer'] == '0':
                pdata[server, chan]['pointimer'] = time.time()
            if round(time.time() - float(pdata[server, chan]['pointimer'])) >= 5 and pdata[server, chan]['points'] < 10000:
                pdata[server, chan]['pointimer'] = '0'
                math = pdata[server, chan]['points'] - pc.rand(435, 535)
                pdata[server, chan]['points'] = math
            if round(time.time() - float(pdata[server, chan]['pointimer'])) >= 10 and pdata[server, chan]['points'] == 10000:
                pdata[server, chan]['pointimer'] = '0'
                math = pdata[server, chan]['points'] - pc.rand(435, 535)
                pdata[server, chan]['points'] = math

        # 20 second trivia cycle
        if round(time.time() - float(pdata[server, chan]['timer'])) >= 20:  # 5:
            # ask the question
            if pdata[server, chan]['hints'] == -1:
                pdata[server, chan]['timerun'] = False
                asyncio.run(trivia(server, channel, 'ask'))
                break
            # out of time
            elif pdata[server, chan]['hints'] >= 3:
                if pdata[server, chan]['game'] != '0':
                    pdata[server, chan]['timerun'] = False
                    asyncio.run(trivia(server, channel, 'timeup'))
                    break
            # give hints
            else:
                if pdata[server, chan]['game'] != '0':
                    pdata[server, chan]['timerun'] = False
                    asyncio.run(trivia(server, channel, 'hint'))
                    break
        continue
    # mprint(f'TIMER END: {server} {channel}')
    # pdata[server, chan]['timerun'] = False
    return
# End timer() ==========================================================================================================

# ======================================================================================================================
# isplayer(server, chan, user)
# returns True if player profile exists for server_chan
def isplayer(server, channel, user):
    chan = str(channel.decode()).replace('#', '')
    chan = chan.lower()
    if pc.cnfexists('trivia.cnf', server + '_' + chan, user) is True:
        return True
    else:
        return False
# End isplayer() =======================================================================================================

# ======================================================================================================================
# PLAYER STATS
# playerstats(espernet, bytes('#testwookie', 'utf-8'), 'neo_nemesis', 'score')
def playerstats(server, channel, user, stat, opt='', data=''):
    try:
        chan = str(channel.decode()).replace('#', '')  # removes '#' and converts to lower case
    except AttributeError:
        chan = str(channel.replace('#', '')).lower()
    chan = chan.lower()

    # ------------------------------------------------------------------------------------------------------------------
    # playerstats(server, channel, user, stat)
    # returns requested player info
    if opt == '' and stat != 'new':
        stattok = pc.cnfread('trivia.cnf', server + '_' + chan, user)
        if stat == 'score':
            return pc.gettok(stattok, 0, ',')
        if stat == 'wins':
            return pc.gettok(stattok, 1, ',')
        if stat == 'streak':
            return pc.gettok(stattok, 2, ',')
        if stat == 'best':
            return pc.gettok(stattok, 3, ',')

    # ------------------------------------------------------------------------------------------------------------------
    # playerstats(server, channel, user, 'new')
    # creates token list for new player (or overwrites existing entry with '0,0,0,NA'
    if opt == '' and stat == 'new':
        pc.cnfwrite('trivia.cnf', server + '_' + chan, user, '0,0,0,NA')
        return 1

    # ------------------------------------------------------------------------------------------------------------------
    # playerstats(server, channel, user, stat, 'c', 'newdata')
    # changes specified stat to 'newdata' (Failure returns -1, success returns 1)
    if opt == 'c':
        stattok = pc.cnfread('trivia.cnf', server + '_' + chan, user)
        token = stattok.split(',')
        # new = ''
        if stat == 'score':
            new = str(data) + ',' + token[1] + ',' + token[2] + ',' + token[3]
        elif stat == 'wins':
            new = token[0] + ',' + str(data) + ',' + token[2] + ',' + token[3]
        elif stat == 'streak':
            new = token[0] + ',' + token[1] + ',' + str(data) + ',' + token[3]
        elif stat == 'best':
            new = token[0] + ',' + token[1] + ',' + token[2] + ',' + str(data)
        else:
            return -1
        pc.cnfwrite('trivia.cnf', server + '_' + chan, user, new)
        return 1
# End playerstats() ====================================================================================================

# ======================================================================================================================
# HINT GENERATOR
    # randomizer('answer', '0,1,2,3', '******')
    # Generates hints with a 3 step randomization.
    #
    # randomizer('test answer', 0) - Returns: '**** ******' Used for setting Hint #1
    #
    # randomizer('test answer', 1, '**** ******') - Returns: '**s* *n****' Or variant. Hint #1 (used for hint #2)
    #
    # randomizer('test answer', 2, '**s* *n****') - Returns: 't*st *n*w**' Or variant. Hint #2 (used for hint #3)
    #
    # randomizer('test answer', 3, 't*st *n*w**') - Returns: 't*st *nsw*r' Or variant. Hint #3 (last one)
    #
    # randomizer(answer, opt, hstr)
    #    answer ** the text string containing the answer to the trivia questions
    #    opt    ** the option 0, 1, 2 or 3. No quotes.
    #    hstr   ** the current hint string
# ======================================================================================================================

# Hint testing function
# Returns the 4 stages (0-3) of a given answer hint. (not logged)
# syntax: hinting('answer text')
def hinting(answer):
    print(f'TRIVIA ANSWER ------------> {answer}')
    hint0 = randomizer(str(answer), 0)
    print(f'TRIVIA HINT 0: {hint0}')
    hint1 = randomizer(answer, 1, hint0)
    print(f'TRIVIA HINT 1: {hint1}')
    hint2 = randomizer(answer, 2, hint1)
    print(f'TRIVIA HINT 2: {hint2}')
    hint3 = randomizer(answer, 3, hint2)
    print(f'TRIVIA HINT 3: {hint3}')
    return

# ----------------------------------------------------------------------------------------------------------------------
# Hint Randomizer
# input answer and current hint to receive a new hint
# answer is text string answer
# opt is number of allowable revealed characters
# hint is the current hint

def randomizer(answer, opt, hintdata=''):
    string = list(answer)
    if hintdata != '':
        hint = list(hintdata)
    else:
        hint = {}
    # ------------------------------------------------------------------------------------------------------------------
    # Set initial hint
    if opt == 0:
        # hint = {}
        for x in range(len(string)):
            if string[x] == ' ':
                hint[x] = ' '
                continue
            hint[x] = '*'
        return hint_assemble(hint)

    # ------------------------------------------------------------------------------------------------------------------
    # Length of 1 character answer input (always returns '*')
    if len(string) == 1:
        return '*'
    # ------------------------------------------------------------------------------------------------------------------
    # Length of 2 character answer input
    if len(string) == 2:
        if opt == 1:
            return '**'
        if opt == 2:
            if random.randint(1, 2) == 1:
                return string[0] + '*'
            else:
                return '*' + string[1]
        if opt == 3:
            return hintdata
    # ------------------------------------------------------------------------------------------------------------------
    # Length of 3 character answer input
    if len(string) == 3:
        if opt == 1:
            return '***'
        if opt == 2:
            if random.randint(1, 3) == 1:
                return string[0] + '**'
            elif random.randint(1, 3) == 2:
                return '*' + string[1] + '*'
            else:
                return '**' + string[2]
        if opt == 3:
            # hint = {}
            for x in range(len(string)):
                # print(f'TRIVIA LOOP NUMBER X: {x}')
                try:
                    if hint[x] == '*':
                        hint[x] = string[x]
                        return hint_assemble(hint)
                    else:
                        continue
                except IndexError:
                    string = string.remove(string[x])
                    # mprint(f'ERROR FIX *!* TRIVIA LOOP NUMBER X: {x} ANSWER LENGTH: {len(string)} STRING: {string} REPAIRED')
                    continue

    # ------------------------------------------------------------------------------------------------------------------
    # Length of 4 character answer input
    if len(string) == 4:
        if opt == 1:
            return '****'
        if opt == 2:
            rnd = random.randint(0, 3)
            if rnd == 0:
                return string[0] + '***'
            if rnd == 1:
                return '*' + string[1] + '**'
            if rnd == 2:
                return '**' + string[2] + '*'
            if rnd == 3:
                return '***' + string[3]
        if opt == 3:
            rnda = random.randint(0, 3)
            if hint[rnda] == '*':
                hint[rnda] = string[rnda]
            while True:
                for x in range(len(string)):
                    # rnda = random.randint(0, 3)
                    if hint[x] == ' ' or hint[x] != '*':
                        continue
                    if hint[x] == '*' and random.randint(0, 3) == 2:
                        hint[x] = string[x]
                        return hint_assemble(hint)
                if hint_count(hint) <= 2:
                    continue
                return hint_assemble(hint)

    # ------------------------------------------------------------------------------------------------------------------
    # Length of 5 characters
    if len(string) == 5:
        if opt == 1:

            # print('HINT-GEN; SELECT 1')
            rndb = random.randint(0, len(string) - 1)
            if hint[rndb] == '*':
                hint[rndb] = string[rndb]
            return hint_assemble(hint)

        if opt == 2:
            while True:
                # print('HINT-GEN; SELECT 2')
                hint = list(hintdata)
                for x in range(len(string)):
                    # if random.randint(0, len(string)) == x or random.randint(0, len(string)) == x:
                    if random.randint(0, len(string)) == x:
                        hint[x] = string[x]
                        continue
                if hint == string:
                    continue
                if hint_count(hint) < 3:
                    continue
                if hint_count(hint) == 4:
                    continue
                return hint_assemble(hint)

        if opt == 3:
            hint = list(hintdata)
            while True:
                # print('HINT-GEN; SELECT 3')
                for x in range(len(string)):
                    if hint[x] == '*':
                        if random.randint(0, len(string)) == x or random.randint(0, len(string)) == x:
                            hint[x] = string[x]
                            if float(hint_count(hint)) < percent(80, len(string)):
                                continue
                            else:
                                return hint_assemble(hint)
                if hint_count(hint) <= 3:
                    # print('HINT-GEN; SELECT 3 -- Less than 3')
                    continue
                # if hint_count(hint) == len(string):
                if hint == string:
                    # print('HINT-GEN; SELECT 3 -- Too long')
                    hint[4] = '*'
                    return hint_assemble(hint)
                return hint_assemble(hint)
    # ------------------------------------------------------------------------------------------------------------------
    # length of 6 characters or more
    if len(string) >= 6:

        if opt == 1:
            while True:
                # print('HINT-GEN; SELECT 4')
                for x in range(len(string)):
                    if float(hint_count(hint)) > percent(35, len(string)):
                        break
                    if random.randint(0, len(string)) == x or random.randint(0, len(string)) == x:
                        hint[x] = string[x]
                        continue
                    if random.randint(0, len(string)) == x or random.randint(0, len(string)) == x:
                        hint[x] = string[x]
                        continue
                if hint_count(hint) <= 1:
                    continue
                if float(hint_count(hint)) > percent(35, len(string)):
                    hint = list(hintdata)
                    continue
                return hint_assemble(hint)

        if opt == 2:
            scount = 1
            while True:
                # print('HINT-GEN; SELECT 5')
                for x in range(len(string)):
                    if float(hint_count(hint)) > percent(65, len(string)):
                        break
                    if random.randint(0, len(string)) == x or random.randint(0, len(string)) == x:
                        hint[x] = string[x]
                        continue
                    if random.randint(0, len(string)) == x or random.randint(0, len(string)) == x:
                        hint[x] = string[x]
                        continue
                scount += 1
                if scount > 4:
                    return hint_assemble(hint)
                if float(hint_count(hint)) < percent(50, len(string)):
                    continue
                if float(hint_count(hint)) > percent(70, len(string)):
                    hint = list(hintdata)
                    continue
                return hint_assemble(hint)

        if opt == 3:
            scount = 1
            while True:
                # print(f'HINT-GEN; SELECT 6 {scount}')
                for x in range(len(string)):
                    if float(hint_count(hint)) >= percent(85, len(string)):
                        break
                    if hint[x] == '*':
                        if random.randint(0, len(string)) == x or random.randint(0, len(string)) == x:
                            hint[x] = string[x]
                            continue
                        # if random.randint(0, len(string)) == x or random.randint(0, len(string)) == x:
                        #    hint[x] = string[x]
                        #    continue
                # if hint_count(hint) >= len(string):
                #    hint = list(hintdata)
                #    continue
                scount += 1
                if scount > 4:
                    return hint_assemble(hint)
                if hint == string:
                    # print('HINT-GEN; SELECT 6 -- 100%')
                    srand = random.randint(0, len(string) - 1)
                    hint[srand] = '*'
                    return hint_assemble(hint)
                if float(hint_count(hint)) < percent(70, len(string)):
                    # print('HINT-GEN; SELECT 6 -- less than 70%')
                    continue
                if float(hint_count(hint)) > percent(90, len(string)):
                    # print('HINT-GEN; SELECT 6 -- greater than 90%')
                    # hint = list(hintdata)
                    # continue
                    return hint_assemble(hint)
                return hint_assemble(hint)

# -------------------------------------------------------------------------------
# Returns a floating number percentage of a whole number value. percent(P%, X)
# used in trivia hint randomizer
# percent(50, 200) returns 100.0     50% of 200
# percent(50, 5) returns 2.5         50% of 5
# percent(30, 3) returns 0.9         30% of 3
def percent(per, value):
    math = per * value / 100
    # print(f'Percent: {math}')
    return math
# End Hint Generator ===================================================================================================

# ======================================================================================================================
# Assembles hints that are in a list-array
# ----------------------------------------------------------------------------------------------------------------------
def hint_assemble(hintdata):
    string = ''
    for x in range(len(hintdata)):
        string = string + hintdata[x]
        continue
    # print(f'hintdata: {string}')
    return string
# ======================================================================================================================

# ======================================================================================================================
# Counts the number of revealed characters in given hint
# ----------------------------------------------------------------------------------------------------------------------
def hint_count(eanswer):
    count = 0
    for c in range(len(eanswer)):
        if eanswer[c] == '*':
            continue
        if eanswer[c] != '*' and eanswer[c] != ' ':
            count += 1
            continue
    # print(f'eanswer: {eanswer}')
    return count
# ======================================================================================================================


# print(f'{pc.is_admin('freenode', 'End3r')}')

# ######################################
# Testing zone
test1 = False
test2 = False

# basic hint input test
if test1 is True:
    hinting('z')
    hinting('zx')
    hinting('300')
    hinting('4000')
    hinting('fiver')
    hinting('sixchr')
    hinting('006000')
    hinting('ABC 123')
    hinting('test answer')
    hinting('longer test answer')
    hinting('a very long testing answer')
    hinting('a little longer testing answer')

if test2 is True:
    print(f'{playerstats('espernet', bytes('#testwookie', 'utf-8'), 'neo_nemesis', 'score')}')
    print(f'{playerstats('espernet', bytes('#testwookie', 'utf-8'), 'neo_nemesis', 'wins')}')
    print(f'{playerstats('espernet', bytes('#testwookie', 'utf-8'), 'neo_nemesis', 'streak')}')
    print(f'{playerstats('espernet', bytes('#testwookie', 'utf-8'), 'neo_nemesis', 'best')}')