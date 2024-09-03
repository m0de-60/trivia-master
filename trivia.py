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
from configparser import RawConfigParser  # For Trivia

# declare data map
pdata = {}

# Set up logging (optional)
logging.basicConfig(filename='./zcorelog.txt', level=logging.DEBUG)  # For error and debug logging
pdata['debuglog'] = 'on'  # turn 'on' for testing, otherwise 'off'

# For remote loading (required for plugin modules)
def plugin_chk_():
    return True

# For start up loading (required if importing system module functions)
def system_req_():
    return 'sys_zcore'

# shutting down the module
def plugin_exit_():
    global pdata
    mprint(f'Shutting down...')
    for x in range(len(pdata['server'])):
        server = pdata['server'][x]
        for y in range(len(pdata[server, 'channel'])):
            chan = pdata[server, 'channel'][x].replace('#', '')
            if pdata[server, chan]['thread'] != '0':
                pdata[server, chan]['thread'].join()
            continue
        continue
    pdata = {}
    return

# stopping the module on specific server and it's channels (connection loss)
# SSLError and OSError reconnects from zCore
def plugin_stop_(server):
    global pdata
    if pdata != {}:
        mprint(f'Core Override: Trivia has been stopped on {server} by zCore')
        for x in range(len(pdata[server, 'channel'])):
            trivia(server, pdata[server, 'channel'][x], 'inter')
            continue
        return 1
    return 0

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
    pdata['c_hour'] = pc.cnfread('trivia.cnf', 'trivia', 'hour')  # Last saved hour of the day (no minutes)
    pdata['c_day'] = pc.cnfread('trivia.cnf', 'trivia', 'day')  # Last saved day of the year
    pdata['c_week'] = pc.cnfread('trivia.cnf', 'trivia', 'week')  # Last saved week of the year
    pdata['c_month'] = pc.cnfread('trivia.cnf', 'trivia', 'month')  # Last saved month of the year
    pdata['c_year'] = pc.cnfread('trivia.cnf', 'trivia', 'year')  # Last saved year
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
            # pdata[server, chan]['fpotd'] = '0'
            # time control (for hourly, daily, weekly, etc)
            pdata[server, chan]['time_control'] = pc.cnfread('trivia.cnf', server, 'time_control')
            pdata[server, chan]['control_main'] = ''  # Main control thread for #channel on server
            pdata[server, chan]['control_timer1'] = '0'  # control timer for hourly stats
            # pdata[server, chan]['control_timer2'] = '0'  # control timer for daily, weekly and monthly stats
            # pdata[server, chan]['control_timer3'] = '0'  # control timer for alltime and yearly
            pdata[server, chan]['controlA'] = '0'  # for timer1 event tracking do not change
            # pdata[server, chan]['controlB'] = '0'  # for timer2 event tracking do not change
            # pdata[server, chan]['controlC'] = '0'  # for timer3 event tracking do not change
            # pdata[server, chan]['control_run'] = False
            tok = 'h,d,w,m,y'
            token = tok.split(',')
            for z in range(len(token)):
                dckt = server + '_tcd'
                chantag = chan + '_' + token[z]
                if pc.cnfexists('trivia.cnf', dckt, chantag) is False:
                    pc.cnfwrite('trivia.cnf', dckt, chantag, '0')
                    pdata[server, chan][token[z]] = ''
                    continue
                elif pc.cnfread('trivia.cnf', dckt, chantag) == '0':
                    pdata[server, chan][token[z]] = ''
                    continue
                else:
                    pdata[server, chan][token[z]] = pc.cnfread('trivia.cnf', dckt, chantag)
                    continue
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
    username = pc.gettok(jdata[0], 0, b'!')
    username = username.replace(b':', b'')
    dusername = username.decode()
    channel = jdata[2].replace(b':', b'')
    dchannel = channel.decode()
    dchannel = dchannel.lower()
    chan = dchannel.replace('#', '')

    if server not in pdata['server']:
        return

    if dchannel not in pdata[server, 'channel']:
        return

    if pdata['trivia'] is True and dusername.lower() == pdata[server, 'botname'].lower():
        time.sleep(0.75)
        await trivia(server, dchannel, 'start')
        return

    if pdata[server, chan]['trivia'] is True and pdata[server, chan]['game'] != 0:
        if pdata[server, chan]['game'] == 'time':
            ctime = 20 - round(time.time() - float(pdata[server, chan]['timer']))
            if ctime < 0:
                await trivia(server, dchannel, 'stop')
                time.sleep(1)
                await trivia(server, dchannel, 'start')
                return
            # need to check for time errors here and restart trivia
            #
            time.sleep(0.05)
            pc.privmsg_(server, channel, '\x0315,1Welcome to \x02\x0311,1Trivia-Master\x02\x0310,1 on ' + channel.decode() + '! \x0315,1Next question in\x02\x033,1 ' + str(ctime) + ' \x02\x0315,1seconds. Use \x0310,1!thelp\x0315,1 for help.\x03')
            return
        if pdata[server, chan]['game'] == 'play':
            time.sleep(0.05)
            hintmsg = pdata[server, chan]['hint']
            if pdata[server, chan]['hints'] > 1:
                hintmsg = pdata[server, chan]['hint2']
            if pdata[server, chan]['hints'] > 2:
                hintmsg = pdata[server, chan]['hint3']
            pc.privmsg_(server, channel, '\x0315,1Welcome to \x02\x0311,1Trivia-Master\x02\x0310,1 on ' + channel.decode() + '!\x0315,1 Use \x0310,1!thelp\x0315,1 for help. \x02\x033,1CURRENT TRIVIA:\x02\x0315,1 ' + pdata[server, chan]['question'] + ' \x02\x033,1HINT:\x02\x0310,1 ' + str(hintmsg) + '\x03')
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
    chandat = server + '_' + chan

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
                time.sleep(0.04)
                pc.privmsg_(server, channel, '\x0315,1New question coming up in\x02\x033,1 ' + str(ctime) + ' \x02\x03seconds.')
                return

        if mdata[4].lower() == b'skip' and pdata[server, chan]['trivia'] is False:
            time.sleep(0.05)
            pc.privmsg_(server, channel, 'Trivia is not currently enabled.')
            return

        # !trivia on
        if mdata[4].lower() == b'on':
            if pdata[server, chan]['trivia'] is True:
                time.sleep(0.05)
                pc.notice_(server, username, 'Trivia is already enabled.')
            else:
                pdata[server, chan]['trivia'] = True
                time.sleep(0.05)
                # pc.privmsg_(server, channel, 'Trivia has been enabled.')
                await trivia(server, dchannel, 'start')

        # !trivia off
        if mdata[4].lower() == b'off':
            if pdata[server, chan]['trivia'] is False:
                time.sleep(0.05)
                pc.notice_(server, username, 'Trivia is already disabled.')
            else:
                pdata[server, chan]['trivia'] = False
                time.sleep(0.05)
                # pc.notice_(server, username, 'Trivia has been disabled.')
                await trivia(server, dchannel, 'stop')

    # ------------------------------------------------------------------------------------------------------------------
    # !thelp - displays help
    elif mdata[3].lower() == b':!thelp' or mdata[3].lower() == b':!help':
        if pdata[server, chan]['trivia'] is False:
            return
        time.sleep(0.05)
        pc.privmsg_(server, channel, '\x02\x0315,1Trivia Commands:\x02\x033,1   !myscore   !highscore   !fastest   !streaks   !thelp\x03')
        pc.privmsg_(server, channel, '\x02\x0315,1Trivia Commands:\x02\x033,1   !alltime  or  !a    !hourly  or  !h    !daily  or  !d    !weekly  or  !w    !monthly  or  !m    !yearly  or  !y\x03')
        return
    # ------------------------------------------------------------------------------------------------------------------
    # !myscore - displays user score and statistics
    elif mdata[3].lower() == b':!myscore' or mdata[3] == b':!score':
        if pdata[server, chan]['trivia'] is False:
            return
        if len(mdata) == 5 and mdata[3] == b':!score':
            username = mdata[4]
            dusername = str(username.decode()).lower()
        if pc.cnfexists('trivia.cnf', server + '_' + chan, dusername) is False:
            pc.privmsg_(server, channel, '\x02\x0311,1' + str(username.decode()) + '\x02\x0315,1 has not played yet.\x03')
            return
        score = '\x0310,1[\x033,1Score:\x0311,1 ' + str(playerstats(server, channel, dusername, 'score')) + '\x0310,1]'
        wins = '\x0310,1[\x033,1Wins:\x0311,1 ' + str(playerstats(server, channel, dusername, 'wins')) + '\x0310,1]'
        streak = '\x0310,1[\x033,1Longest Streak:\x0311,1 ' + str(playerstats(server, channel, dusername, 'streak')) + '\x0310,1]'
        best = '\x0310,1[\x033,1Best Time:\x0311,1 ' + str(playerstats(server, channel, dusername, 'best')) + '\x0310,1]\x03'
        stats = '\x02\x0315,1PLAYER SCORE:\x02\x0310,1    ' + username.decode() + '    ' + score + wins + streak + best
        # add stuff here so can be toggled from privmsg or notice
        time.sleep(0.5)
        pc.privmsg_(server, channel, stats)
        return

    # ------------------------------------------------------------------------------------------------------------------
    # !highscore - displays high scores
    elif mdata[3].lower() == b':!highscore':
        if pdata[server, chan]['trivia'] is False:
            return
        if pc.cnfread('trivia.cnf', chandat, 'cache') == 0:
            pc.privmsg(server, channel, '\x0315,1There are currently no high scores.\x03')
            return
        await score_keep(server, channel, 'hs')
        return

    # ------------------------------------------------------------------------------------------------------------------
    # !streaks - displays winning streaks
    elif mdata[3].lower() == b':!streaks':
        if pdata[server, chan]['trivia'] is False:
            return
        if pc.cnfread('trivia.cnf', chandat, 'cache') == 0:
            pc.privmsg(server, channel, '\x0315,1There are currently no streaks.\x03')
            return
        await score_keep(server, channel, 'st')
        return

    # ------------------------------------------------------------------------------------------------------------------
    # !fastest - displays fastest players
    # Does not work, here for documentation
    # Needs good way of sorting floating number values
    elif mdata[3].lower() == b':!fastest':
        if pdata[server, chan]['trivia'] is False:
            return
        if pc.cnfread('trivia.cnf', chandat, 'cache') == 0:
            pc.privmsg(server, channel, '\x0315,1There are currently no fastest times.\x03')
            return
        await score_keep(server, channel, 'fp')
        return

    # ------------------------------------------------------------------------------------------------------------------
    # Timely Functions

    # !today -----------------------------------------------------------------------------------------------------------
    # General description of hourly and daily scores
    # elif mdata[3].lower() == b':!today' or mdata[3].lower() == b':!t':
    #   describe the daily top player, all time high score, longest streak and fastest time
    
    # !hourly or !h ----------------------------------------------------------------------------------------------------
    elif mdata[3].lower() == b':!hourly' or mdata[3].lower() == b':!h':
        if pdata[server, chan]['trivia'] is False or pdata[server, chan]['time_control'] == 'off':
            return
        await time_event(server, dchannel, 'hourly', 'req')
        return
    # !daily or !d -----------------------------------------------------------------------------------------------------
    elif mdata[3].lower() == b':!daily' or mdata[3].lower() == b':!d':
        if pdata[server, chan]['trivia'] is False or pdata[server, chan]['time_control'] == 'off':
            return
        await time_event(server, dchannel, 'daily', 'req')
        return
    # !weekly or !w ----------------------------------------------------------------------------------------------------
    elif mdata[3].lower() == b':!weekly' or mdata[3].lower() == b':!w':
        if pdata[server, chan]['trivia'] is False or pdata[server, chan]['time_control'] == 'off':
            return
        await time_event(server, dchannel, 'weekly', 'req')
        return
    # !monthly or !m ---------------------------------------------------------------------------------------------------
    elif mdata[3].lower() == b':!monthly' or mdata[3].lower() == b':!m':
        if pdata[server, chan]['trivia'] is False or pdata[server, chan]['time_control'] == 'off':
            return
        await time_event(server, dchannel, 'monthly', 'req')
        return
    # !yearly or !y ----------------------------------------------------------------------------------------------------
    elif mdata[3].lower() == b':!yearly' or mdata[3].lower() == b':!y':
        if pdata[server, chan]['trivia'] is False or pdata[server, chan]['time_control'] == 'off':
            return
        await time_event(server, dchannel, 'yearly', 'req')
        return
    # !alltime or !a ----------------------------------------------------------------------------------------------------
    elif mdata[3].lower() == b':!alltime' or mdata[3].lower() == b':!a':
        if pdata[server, chan]['trivia'] is False or pdata[server, chan]['time_control'] == 'off':
            return
        await time_event(server, dchannel, 'alltime', 'req')
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
                pc.privmsg_(server, channel, '\x02\x0310,1' + username.decode() + '\x02   \x0315,1Wins\x0311,1 ' + str(pdata[server, chan]['points']) + ' points!    \x02\x033,1ANSWER ---->\x02 ' + pdata[server, chan]['answer'] + '    \x02\x0315,1TIME:\x02\x0311,1 ' + str(totaltime) + ' seconds\x03')
                wins = int(playerstats(server, channel, dusername, 'wins')) + 1
                playerstats(server, channel, dusername, 'wins', 'c', str(wins))
                points = int(playerstats(server, channel, dusername, 'score')) + int(pdata[server, chan]['points'])
                playerstats(server, channel, dusername, 'score', 'c', str(points))
                if playerstats(server, channel, dusername, 'best') != 'NA' and totaltime < float(playerstats(server, channel, dusername, 'best')):
                    pc.privmsg_(server, channel, '\x02\x0310,1' + username.decode() + '\x02   \x0311,1Set a new best time record!   \x02\x038,1>\x0311,1 ' + str(totaltime) + ' seconds\x038,1 <\x02\x03')
                    playerstats(server, channel, dusername, 'best', 'c', str(totaltime))
                if playerstats(server, channel, dusername, 'best') == 'NA':
                    playerstats(server, channel, dusername, 'best', 'c', str(totaltime))
                # set up for timely stats
                if pdata[server, chan]['time_control'] == 'on':
                    await time_event(server, channel.decode(), 'add', username.decode(), pdata[server, chan]['points'])
                # set up for winning streak
                if pdata[server, chan]['streakname'] != dusername:
                    pdata[server, chan]['streakcount'] = 0
                pdata[server, chan]['streakname'] = dusername
                pdata[server, chan]['streakcount'] += 1
                if pdata[server, chan]['streakcount'] > int(playerstats(server, channel.decode(), dusername, 'streak')):
                    playerstats(server, channel.decode(), dusername, 'streak', 'c', str(pdata[server, chan]['streakcount']))
                if pdata[server, chan]['streakcount'] > 1:
                    time.sleep(0.2)
                    pc.privmsg_(server, channel, '\x02\x0310,1' + username.decode() + '\x02   \x0315,1Won\x02\x033,1 ' + str(pdata[server, chan]['streakcount']) + ' \x02\x0315,1in a row!   \x02\x0311,1 * WINNING STREAK *\x02\x03')
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
        pc.privmsg_(server, channel.encode(), '\x02\x0314,1Trivia Master \x033,1   v' + pdata['pversion'] + '\x02\x0315,1    Now running:\x0310,1 \x02' + cmsg + '\x02\x03')
        time.sleep(1)
        pdata[server, chan]['game'] = 'time'
        # time control
        if pdata[server, chan]['time_control'] == 'on':
            pdata[server, chan]['control_timer1'] = time.time()
            # pdata[server, chan]['control_timer2'] = time.time()
            # pdata[server, chan]['control_timer3'] = time.time()

        # pdata[server, chan]['control_main'] = threading.Thread(target=time_control, args=(server, channel,), daemon=True)
        # pdata[server, chan]['control_main'].start()

        # mprint(f'AWAIT NEXT')
        await trivia(server, channel, 'next')

    # ------------------------------------------------------------------------------------------------------------------
    # interrupt trivia (similar to 'stop' but used when connection is interrupted)
    # trivia(server, channel, 'inter')
    if opt == 'inter':
        mprint(f'TRIVIA INTERRUPT: {server} {channel}')
        pdata[server, chan]['timerun'] = False
        pdata[server, chan]['game'] = '0'
        pdata[server, chan]['mode'] = '0'
        freetriv(server, channel)
        pdata[server, chan]['streakname'] = '0'
        pdata[server, chan]['streakcount'] = 0
        pdata[server, chan]['thread'].join()
        return

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
        pc.privmsg_(server, channel.encode(), '\x02\x0314,1Trivia Master \x033,1   v' + pdata['pversion'] + '\x02\x0315,1    Stopped.\x03')
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
            pc.privmsg_(server, channel.encode(), '\x0315,1Next question in\x02\x033,1 20 \x02\x0315,1seconds...\x03')
            pdata[server, chan]['thread'] = threading.Thread(target=timer, args=(server, channel,), daemon=True)
            pdata[server, chan]['thread'].start()

    # ------------------------------------------------------------------------------------------------------------------
    # ask question
    # trivia(server, channel, 'ask')
    if opt == 'ask':
        pdata[server, chan]['game'] = 'play'
        pdata[server, chan]['response'] = time.time()
        pdata[server, chan]['pointimer'] = time.time()
        pc.privmsg_(server, channel.encode(), '\x02\x0310,1[\x033,1\x02No.\x02 ' + str(pdata[server, chan]['qnum']) + ' ' + pdata[server, chan]['category'] + '\x0310,1]\x0315,1   \x02 ' + pdata[server, chan]['question'] + '\x03')
        pc.privmsg_(server, channel.encode(), '\x0315,1First hint in\x02\x033,1 20 \x02\x0315,1seconds...\x03')

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
        pc.privmsg_(server, channel.encode(), '\x02\x0314,1Hint # ' + str(pdata[server, chan]['hints']) + ': ' + str(hint) + '\x02\x03')
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
        pc.privmsg_(server, channel.encode(), '\x02\x0311,1Time is up!\x02\x0315,1    The answer is:\x02\x033,1 ' + pdata[server, chan]['answer'] + '\x03\x02')
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
        totalerr = '0^0'
        if cat == 'all':
            # pc.notice_(server, duser.encode(), 'Check All')
            mprint('Checking all trivia categories for errors...')
            for x in range(len(pdata['category'])):
                filename = './qafiles/' + pdata['category'][x] + '.txt'
                mprint('Checking file ' + cat.lower() + '.txt for trivia errors...')
                errnum = t_file_clean(filename)
                mprint('Error check for ' + pdata['category'][x] + '.txt complete. [Errors fixed: ' + str(pc.gettok(errnum, 1, '^')) + '] [Errors removed: ' + str(pc.gettok(errnum, 0, '^')) + ' and stored in ./qafiles/qlog.txt]')
                err = int(pc.gettok(totalerr, 0, '^')) + int(pc.gettok(errnum, 0, '^'))
                fix = int(pc.gettok(totalerr, 1, '^')) + int(pc.gettok(errnum, 1, '^'))
                totalerr = str(err) + '^' + str(fix)
                continue
            mprint('Error checking for all trivia categories is complete. [Errors fixed: ' + str(pc.gettok(totalerr, 1, '^')) + '] [Errors removed: ' + str(pc.gettok(totalerr, 0, '^')) + ' and stored in ./zcore/qafiles/qlog.txt]')
            pc.notice_(server, duser.encode(), '[T-M] * Check All complete. [Errors fixed: ' + str(pc.gettok(totalerr, 1, '^')) + '] [Errors removed: ' + str(pc.gettok(totalerr, 0, '^')) + ' and stored in ./qafiles/qlog.txt]')
            return
        else:
            filename = './qafiles/' + cat.lower() + '.txt'
            # pc.notice_(server, duser.encode(), 'Checking ' + cat.lower())
            mprint('Checking file ' + cat.lower() + '.txt for trivia errors...')
            errnum = t_file_clean(filename)
            mprint('Error check for ' + cat.lower() + '.txt complete. [Errors fixed: ' + str(pc.gettok(errnum, 1, '^')) + '] [Errors removed: ' + str(pc.gettok(errnum, 0, '^')) + ' and stored in ./qafiles/qlog.txt]')
            pc.notice_(server, duser.encode(), '[T-M] * Category check for ' + cat.lower() + ' complete. [Errors fixed: ' + str(pc.gettok(errnum, 1, '^')) + '] [Errors removed: ' + str(pc.gettok(errnum, 0, '^')) + ' and stored in ./qafiles/qlog.txt]')
            return

# End trivia() =========================================================================================================

# ======================================================================================================================
# Trivia category file cleaner
# File must exist in qafiles folder in zCore directory. ./zcore/qafiles/filename.txt
# ### Improperly formatted trivia data will cause errors in the game.
# ### BUG REMOVAL!! Make sure to scan all new trivia files to fix or remove
# to add better correction for ':'

def t_file_clean(filename):
    # Scan the file for improperly formatted questions
    fname = filename
    file = open(fname, 'r')
    filelines = file.readlines()
    # filelines = filelines.splitlines()
    # properly formatted questions are stored in the 'clean file'
    c_file = open('./qafiles/cleanfile.txt', 'a')
    # improperly formatted questions are removed and stored in the qlog.txt
    qlog = open('./qafiles/qlog.txt', 'a')
    # how many errors are found? Starts with 0 same for fixes
    errnum = 0
    fixnum = 0
    # lasttok = ''
    # l_tok1 = ''
    # l_tok2 = ''
    # tokenc = 0
    # scanning for and removing improperly formatted questions
    for x in range(len(filelines)):
        fileline = filelines[x].replace('\n', '')
        # Remove questions that do not contain proper token seperator character " ` " (grave accent mark)
        if pc.numtok(fileline, '`') != 2:
            errnum += 1
            qlog.write('ERR-BAD-SYN: ' + fileline + '\n')
            continue
        else:
            q = pc.gettok(fileline, 0, '`')
            a = pc.gettok(fileline, 1, '`')
            # print(f'Q: {q} TOK: {pc.numtok(q, ': ')}')

            # answer is present in question
            if a in q:
                errnum += 1
                qlog.write('ERR-BAD-FRM: ' + fileline + '\n')
                continue

            # Remove 5 letter answers that contain white spaces
            if len(a) == 5 and pc.numtok(a, ' ') > 1:
                errnum += 1
                qlog.write('ERR-5-CHR: ' + fileline + '\n')
                continue

            # Fix erroneous colan formats
            # Category: Question
            if pc.numtok(q, ': ') == 2:
                q = pc.gettok(q, 1, ': ')
                fixnum += 1
                qlog.write('ERR-FIX-MOD1: ' + fileline + '\n')
                c_file.write(str(q) + '`' + str(a) + '\n')
                continue

            # Fix erroneous colan formats (remove Category: and leave Sub-Category:)
            # Category: Sub-category: Question
            if pc.numtok(q, ': ') == 3:
                q = pc.gettok(q, 1, ': ') + ': ' + pc.gettok(q, 2, ': ')
                fixnum += 1
                # print(f'PRINTEST: {q}`{a}')
                qlog.write('ERR-FIX-MOD2: ' + fileline + '\n')
                c_file.write(str(q) + '`' + str(a) + '\n')
                continue

            # Category : Question
            if pc.numtok(q, ' : ') == 2:
                q = pc.gettok(q, 1, ' : ')
                fixnum += 1
                qlog.write('ERR-FIX-MOD3: ' + fileline + '\n')
                c_file.write(str(q) + '`' + str(a) + '\n')
                continue

            # Category:Question
            if pc.numtok(q, ':') == 2:
                q = pc.gettok(q, 1, ':')
                fixnum += 1
                qlog.write('ERR-FIX-MOD4: ' + fileline + '\n')
                c_file.write(str(q) + '`' + str(a) + '\n')
                continue

            # Remove erroneous excessive colon formats
            if pc.numtok(q, ':') >= 4:
                errnum += 1
                qlog.write('ERR-TOK-EXC: ' + fileline + '\n')
                continue

            # Properly formatted question, write to file.
            c_file.write(fileline + '\n')
            continue
    file.close()
    c_file.close()
    qlog.close()
    # removing old and resaving the 'cleaned list' as the category file.
    pc.remfile(filename)
    pc.renamefile('./qafiles/cleanfile.txt', filename)
    # returns the number of errors found and fixed or removed
    return str(errnum) + '^' + str(fixnum)

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
    while pdata[server, chan]['game'] != '0':
        if pdata[server, chan]['timerun'] is False:  # ???
            break

        # if pdata[server, chan]['game'] == '0':  # This is useful or not idk
        #    pdata[server, chan]['timerun'] = False
        #    break

        time.sleep(0.1)
        # after timer sleep, check stats
        if pdata[server, chan]['timerun'] is False:
            break

        # Time Control (only performed between questions on a 1 hour timer!)
        if pdata[server, chan]['time_control'] == 'on' and pdata[server, chan]['game'] == 'time':

            # hour has changed
            if pdata['c_hour'] != pc.chour():
                pc.cnfwrite('trivia.cnf', 'trivia', 'hour', str(pc.chour()))
                pdata['c_hour'] = pc.chour()
                pdata[server, chan]['control_timer1'] = time.time()
                pdata[server, chan]['controlA'] = '0'
                mprint(f'Hour has changed to: {pdata['c_hour']}')
                asyncio.run(time_event(server, channel, 'hourly', 'new'))

            # day has changed
            if pdata['c_day'] != pc.cday():
                pc.cnfwrite('trivia.cnf', 'trivia', 'day', str(pc.cday()))
                pdata['c_day'] = pc.cday()
                mprint(f'Day has changed to: {pdata['c_day']}')
                asyncio.run(time_event(server, channel, 'daily', 'new'))

            # week has changed
            if pdata['c_week'] != pc.cweek():
                pc.cnfwrite('trivia.cnf', 'trivia', 'week', str(pc.cweek()))
                pdata['c_week'] = pc.cweek()
                mprint(f'Week has changed to: {pdata['c_week']}')
                asyncio.run(time_event(server, channel, 'weekly', 'new'))

            # month has changed
            if pdata['c_month'] != pc.cmonth():
                pc.cnfwrite('trivia.cnf', 'trivia', 'month', str(pc.cmonth()))
                pdata['c_month'] = pc.cmonth()
                mprint(f'Month has changed to: {pdata['c_month']}')
                asyncio.run(time_event(server, channel, 'monthly', 'new'))

            # year has changed
            if pdata['c_year'] != pc.cyear():
                pc.cnfwrite('trivia.cnf', 'trivia', 'year', str(pc.cyear()))
                pdata['c_year'] = pc.cyear()
                mprint(f'Year has changed to: {pdata['c_year']}')
                asyncio.run(time_event(server, channel, 'yearly', 'new'))

            tcu = time.time() - float(pdata[server, chan]['control_timer1'])

            # 10 minutes - Today's Top Players
            if round(tcu) >= 600 and pdata[server, chan]['controlA'] == '0':
                pdata[server, chan]['controlA'] = 'A'
                asyncio.run(time_event(server, channel, 'daily', 'auto'))
            # 20 minutes - All Time Top Players
            elif round(tcu) >= 1200 and pdata[server, chan]['controlA'] == 'A':
                pdata[server, chan]['controlA'] = 'B'
                asyncio.run(time_event(server, channel, 'alltime', 'auto'))
            # 30 minutes - Hourly Top Players
            elif round(tcu) >= 1800 and pdata[server, chan]['controlA'] == 'B':
                pdata[server, chan]['controlA'] = 'C'
                asyncio.run(time_event(server, channel, 'hourly', 'auto'))
            # 40 minutes - Weekly Top Players
            elif round(tcu) >= 2400 and pdata[server, chan]['controlA'] == 'C':
                pdata[server, chan]['controlA'] = 'D'
                asyncio.run(time_event(server, channel, 'weekly', 'auto'))
            # 50 minutes - Monthly Top Players
            elif round(tcu) >= 3000 and pdata[server, chan]['controlA'] == 'D':
                pdata[server, chan]['controlA'] = 'E'
                asyncio.run(time_event(server, channel, 'monthly', 'auto'))
            # 59min 59seconds 59 milsec - end of timer, restart
            elif tcu >= 3599.9983 and pdata[server, chan]['controlA'] == 'E':
                pdata[server, chan]['controlA'] = '0'
                pdata[server, chan]['control_timer1'] = time.time()

        # regular operating stuff
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

# ======================================================================================================================
# VARIOUS TOP-10, HIGH SCORE, ETC FUNCTIONS

# ----------------------------------------------------------------------------------------------------------------------
# Score Keeper used for !highscore and !fastest
async def score_keep(server, channel, args):
    global pdata
    chan = channel.lower()
    chan = chan.decode()
    chan = chan.replace('#', '')
    chan_dat = server + '_' + chan
    parser = RawConfigParser()
    datagot = ''
    if args == 'hs' or args == 'st' or args == 'fp':
        datagot = []
    # if args == 'fp':
    #    datagot = {}
    score_msg = ''
    parser.read('trivia.cnf')
    for name, value in parser.items(chan_dat):
        datkey = '%s' % name
        if datkey == 'cache':
            continue
        if args == 'hs':
            if score_msg == '':
                score_msg = '\x02\x0315,1HIGH SCORES:\x02   '
            if playerstats(server, channel, datkey, 'score') == '0' or playerstats(server, channel, datkey, 'score') == 0:
                continue
            else:
                datagot.append(str(playerstats(server, channel, datkey, 'score')) + '^' + datkey)
            continue
        if args == 'fp':
            if score_msg == '':
                score_msg = '\x02\x0315,1FASTEST PLAYERS:\x02 '
            if playerstats(server, channel, datkey, 'best') == 'NA':
                continue
            else:
                datagot.append(str(playerstats(server, channel, datkey, 'best')) + '^' + datkey)
            continue
        if args == 'st':
            if score_msg == '':
                score_msg = '\x02\x0315,1BEST STREAKS:\x02   '
            if playerstats(server, channel, datkey, 'streak') == '0' or playerstats(server, channel, datkey, 'streak') == 0:
                continue
            if int(playerstats(server, channel, datkey, 'streak')) <= 1:
                continue
            else:
                datagot.append(str(playerstats(server, channel, datkey, 'streak')) + '^' + datkey)
                continue
        continue
    if datagot == [] or datagot == {}:
        score_msg = score_msg + '\x034,1 None!\x02\x03'
        pc.privmsg_(server, channel.encode(), score_msg)
        return

    # if args == 'fp':
    #    print(f'{datagot}')
    #    # datagot.sort(reverse=False)
    #    # print(f'{datagot}')
    #    return

    if args == 'hs' or args == 'st':
        # There was a sorting bug here, thank you to katia for fixing this! :)
        datagot.sort(key=lambda o: int(o.split('^')[0]), reverse=True)  # katia fixed this

    if args == 'fp':
        # Used the same method as katia but changed to float.
        datagot.sort(key=lambda o: float(o.split('^')[0]), reverse=False)

    if len(datagot) > 1:
        for x in range(len(datagot)):
            if x == 0:
                if args == 'fp':
                    score_msg = score_msg + eep(datagot[x]) + ' seconds'
                else:
                    score_msg = score_msg + eep(datagot[x])
            else:
                if args == 'fp':
                    score_msg = score_msg + ' \x02\x0310,1|\x02 ' + eep(datagot[x]) + ' seconds'
                else:
                    score_msg = score_msg + ' \x02\x0310,1|\x02 ' + eep(datagot[x])

            if x == 4:
                break
            else:
                continue

    if len(datagot) == 1:
        score_msg = score_msg + eep(datagot[0])

    pc.privmsg_(server, channel, score_msg)
    return

# ¯\_(o.O)_/¯ Is this Sparta? (This actually just seperates and formats player score)
def eep(wildeep):  # This is quite the useful tool
    wild = pc.gettok(wildeep, 1, '^')
    eep_ = pc.gettok(wildeep, 0, '^')
    return str('\x0310,1' + wild + '\x033,1 ' + eep_)

# ----------------------------------------------------------------------------------------------------------------------
# Top Players stats for various time control events
# async def time_event(server, channel, spec, args, ext='', exc=''):
async def time_event(server, channel, spec, args, ext=''):
    global pdata

    chan = str(channel.replace('#', '')).lower()
    chandat = server + '_' + chan
    tcd = server + '_tcd'

    # time_event('serverid', '#channel', 'start')
    # start timers
    # if args == 'start':
    #    pdata[server, chan]['control_run'] = True
    #    pdata[server, chan]['control_timer1'] = time.time()
    #    start = ''

    # time_event(server, channel, 'add', 'username', 'points')
    if spec == 'add':
        user = args
        points = ext
        toklist = 'h,d,w,m,y'
        tok = toklist.split(',')
        setbreak = False
        for x in range(len(tok)):
            if pdata[server, chan][tok[x]] == '':
                pdata[server, chan][tok[x]] = str(points) + '^' + user
                chand = chan + '_' + tok[x]
                pc.cnfwrite('trivia.cnf', tcd, chand, pdata[server, chan][tok[x]])
                continue
            else:
                stok = pdata[server, chan][tok[x]].split(',')
                for y in range(len(stok)):
                    usr = pc.gettok(stok[y], 1, '^')
                    if usr.lower() == user.lower():
                        math = int(pc.gettok(stok[y], 0, '^')) + int(points)
                        newtok = str(math) + '^' + user
                        if len(stok) == 1:
                            pdata[server, chan][tok[x]] = newtok
                        else:
                            pdata[server, chan][tok[x]] = pc.reptok(pdata[server, chan][tok[x]], y, ',', newtok)
                        setbreak = True
                        break
                    else:
                        chand = chan + '_' + tok[x]
                        pc.cnfwrite('trivia.cnf', tcd, chand, pdata[server, chan][tok[x]])
                        continue
                if setbreak is False:
                    pdata[server, chan][tok[x]] = pdata[server, chan][tok[x]] + ',' + str(points) + '^' + user
            chand = chan + '_' + tok[x]
            pc.cnfwrite('trivia.cnf', tcd, chand, pdata[server, chan][tok[x]])
            continue
        return

    # time_event('serverid', '#channel', 'hourly', args, ext)
    # hourly player scores
    if spec == 'hourly':
        if args == 'req':
            if pdata[server, chan]['h'] == '':
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Hourly:\x02\x0310,1 No players have yet to score this hour!\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Hourly top players:\x02\x0310,1 ' + cont_sort(pdata[server, chan]['h']) + '\x03')
                return
        if args == 'new':
            if pdata[server, chan]['h'] != '':
                if pdata['c_hour'] != '0':
                    pc.privmsg_(server, channel.encode(), '\x02\x0311,1Top Players This Hour:\x02\x0310,1 ' + cont_sort(pdata[server, chan]['h']) + '\x03')
                    pc.privmsg_(server, channel.encode(), '\x02\x0311,1Hourly Top Players\x02\x0310,1 have been reset for a new hour!\x03')
                pc.cnfwrite('trivia.cnf', server + '_tcd', chan + '_h', '0')
                pdata[server, chan]['h'] = ''
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Hourly:\x02\x0310,1 No players scored in the last hour!\x03')
                return
        if args == 'auto':
            if pdata[server, chan]['h'] != '':
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Hourly Top Players:\x02\x0310,1 ' + cont_sort(pdata[server, chan]['h']) + '\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Hourly:\x02\x0310,1 No players scored recently!\x03')
                return
    # time_event('serverid', '#channel', 'daily', args, ext)
    # daily player scores
    if spec == 'daily':
        if args == 'req':
            if pdata[server, chan]['d'] == '':
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Daily:\x02\x0310,1 No players have scored today!\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1Today's Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['d']) + '\x03')
                return
        if args == 'new':
            if pdata[server, chan]['d'] != '':
                if pdata['c_day'] != '0':
                    pc.privmsg_(server, channel.encode(), '\x02\x0311,1Yesterdays Top Players:\x02\x0310,1 ' + cont_sort(pdata[server, chan]['d']) + '\x03')
                    pc.privmsg_(server, channel.encode(), "\x02\x0311,1Today's Top Players\x02\x0310,1 have been reset for a new day!\x03")
                pc.cnfwrite('trivia.cnf', server + '_tcd', chan + '_d', '0')
                pdata[server, chan]['d'] = ''
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Daily:\x02\x0310,1 No players have scored yesterday! It is a new day\x03')
                return
        if args == 'auto':
            if pdata[server, chan]['d'] != '':
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1Today's Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['d']) + '\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Daily:\x02\x0310,1 No players scored today!\x03')
                return

    # time_event('serverid', '#channel', 'weekly', args, ext)
    if spec == 'weekly':
        if args == 'req':
            if pdata[server, chan]['w'] == '':
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Weekly:\x02\x0310,1 No players have scored this week!\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1Weekly Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['w']) + '\x03')
                return
        if args == 'new':
            if pdata[server, chan]['w'] != '':
                if pdata['c_week'] != '0':
                    pc.privmsg_(server, channel.encode(), "\x02\x0311,1Last Week's Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['w']) + '\x03')
                    pc.privmsg_(server, channel.encode(), "\x02\x0311,1Weekly Top Players\x02\x0310,1 have been reset for a new week!\x03")
                pdata[server, chan]['w'] = ''
                pc.cnfwrite('trivia.cnf', server + '_tcd', chan + '_w', '0')
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Weekly:\x02\x0310,1 No players have scored last week! It is a new week.\x03')
                return
        if args == 'auto':
            if pdata[server, chan]['w'] != '':
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1Weekly Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['w']) + '\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Weekly:\x02\x0310,1 No players scored this week!\x03')
                return

    # time_event('serverid', '#channel', 'monthly', args, ext)
    if spec == 'monthly':
        if args == 'req':
            if pdata[server, chan]['m'] == '':
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Monthly:\x02\x0310,1 No players have scored this month!\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1Monthly Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['m']) + '\x03')
                return
        if args == 'new':
            if pdata[server, chan]['m'] != '':
                if pdata['c_month'] != '0':
                    pc.privmsg_(server, channel.encode(), "\x02\x0311,1Last Month's Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['m']) + '\x03')
                    pc.privmsg_(server, channel.encode(), "\x02\x0311,1Monthly Top Players\x02\x0310,1 have been reset for a new month!\x03")
                pc.cnfwrite('trivia.cnf', server + '_tcd', chan + '_m', '0')
                pdata[server, chan]['m'] = ''
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Monthly:\x02\x0310,1 No players scored last month! It is a new month.\x03')
                return
        if args == 'auto':
            if pdata[server, chan]['m'] != '':
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1Monthly Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['m']) + '\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Monthly:\x02\x0310,1 No players scored this month!\x03')
                return

    # time_event('serverid', '#channel', 'yearly', args, ext)
    if spec == 'yearly':
        if args == 'req':
            if pdata[server, chan]['y'] == '':
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Yearly:\x02\x0310,1 No players have scored this year!\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1Yearly Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['y']) + '\x03')
                return
        if args == 'new':
            if pdata[server, chan]['y'] != '':
                if pdata['c_year'] != '0':
                    pc.privmsg_(server, channel.encode(), "\x02\x0311,1Last Year's Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['y']) + '\x03')
                    pc.privmsg_(server, channel.encode(), "\x02\x0311,1Yearly Top Players\x02\x0310,1 have been reset for a new week!\x03")
                pc.cnfwrite('trivia.cnf', server + '_tcd', chan + '_y', '0')
                pdata[server, chan]['y'] = ''
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Yearly:\x02\x0310,1 No players have scored last year! It is a new year.\x03')
                return
        if args == 'auto':
            if pdata[server, chan]['y'] != '':
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1Yearly Top Players:\x02\x0310,1 " + cont_sort(pdata[server, chan]['y']) + '\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1Yearly:\x02\x0310,1 No players have scored this year!\x03')
                return

    # time_event('serverid', '#channel', 'alltime', args, ext)
    if spec == 'alltime':
        # datagot = ''
        parser = RawConfigParser()
        tokstr = ''
        parser.read('trivia.cnf')
        for name, value in parser.items(chandat):
            datkey = '%s' % name
            if datkey == 'cache':
                continue
            if str(playerstats(server, channel, datkey, 'score')) == '0':
                continue
            if tokstr == '':
                tokstr = str(playerstats(server, channel, datkey, 'score')) + '^' + datkey
                continue
            tokstr = tokstr + ',' + str(playerstats(server, channel, datkey, 'score')) + '^' + datkey
            continue
        if args == 'req':
            if tokstr == '':
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1All-Time:\x02\x0310,1 No players have scored yet!\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1All-Time Top Players:\x02\x0310,1 " + cont_sort(tokstr) + '\x03')
                return
        if args == 'auto':
            if tokstr != '':
                pc.privmsg_(server, channel.encode(), "\x02\x0311,1All-Time Top Players:\x02\x0310,1 " + cont_sort(tokstr) + '\x03')
                return
            else:
                pc.privmsg_(server, channel.encode(), '\x02\x0311,1All-Time:\x02\x0310,1 No players have scored yet!\x03')
                return

def cont_sort(cont_data):
    data = cont_data.split(',')
    datalist = []
    for x in range(len(data)):
        datalist.append(data[x])
        continue
    datalist.sort(key=lambda o: int(o.split('^')[0]), reverse=True)
    sorter = ''
    for x in range(len(datalist)):
        if x > 9:
            return sorter
        newtok = '\x0310,1' + pc.gettok(datalist[x], 1, '^') + '\x033,1 ' + pc.gettok(datalist[x], 0, '^')
        if sorter == '':
            sorter = newtok
            continue
        else:
            sorter = sorter + ' \x0311,1| ' + newtok
            continue
    return sorter


# ######################################
# Testing zone (will be removed from released version)
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