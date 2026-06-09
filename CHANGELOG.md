# Changelog

All notable changes to the Music Club Discord Bot will be documented in this file.

## Unreleased

- **To Do**: _Add !thisweek / !lastweek / !nextweek which posts all of that week's music_
- **To Do**: _Add ability to adjust setup features_
- **To Do**: _Change !fixdate to check the worksheet and verify the date is there before changing_
- **To Do**: _Change the way I'm handling the dockerization to allow restarts_

### 0.6.3
- Changed midnight tasks to allow for arbitrary dates.

### 0.6.2

- Fixed unintended trigger of bot (!!, !!!, etc)

### 0.6.1

- Changed the days of the week for the new club schedule.

## 0.6.0

- Added ability to change a date using !fixdate and a custom date given (e.g. !fixdate 1/1/2025)
- Added some bits of setup instructions to README.md
- Changed the days of the week for the new club schedule.
- Changed titles for commands to include the worksheet name
- Fixed error if date was not on the spreadsheet

### 0.5.7

- Fixed issue with bot confirming it has changed the date

### 0.5.6

- Added logging
- Added !restart for bot owner only but does not work dockerized
- Changed !fixdate so any user can trigger
- Fixed issue with finding the thread ID
- Fixed disconnecting exception (hopefully)

### 0.5.5

- Added .env for uploading publically on Github
- Added settings.py to clean up bot.py

### 0.5.4

- Fixed Midnight Task and !fixtitle unhandled exception in regards to the thread title character limit

### 0.5.3

- Added version number to !help
- Changed !checkdate to allow any user to check
- Fixed !fixtitle, now it posts the correct title when triggered
- Fixed !fixdate, now correctly fixes the date and notifies the user it does so

### 0.5.2

- Fixed !fixtitle in !help
- Fixed capitalization issue in gifposting
- Fixed incorrect text in a title

### 0.5.1

- Fixed date.txt location

## 0.5.0

- Added Tenor (gif) API
- Added !gif, !mood, and !vibes
- Changed !help to reflect new commands
- Fixed date change during midnight tasks

### 0.4.1

- Fixed typos

## 0.4.0

- Added !previous, !upcoming/!next, and !upupcoming
- Added !fixdate if there is a problem with what date it is in the text file
- Changed how bot handles the spreadsheet (rewrote most of it)
- Removed !yesterday and !tomorrow

### 0.3.1

- Added genres
- Changed some text
- Fixed posting nonsense (E r r) at midnight if there is no album
- Fixed problem with manually setting the thread title

### 0.3.0

- Added commands !previous and !upcoming that look at rows relative to current row (instead of checking via date)
- Added Midnight Task on Mondays for posting the week's albums to Oubliette Alumni
- Added error handling of common exceptions thrown when someone triggers a command (Index Error, Attribute Error)
- Added David Lynch
- Changed !help to reflect new commands
- Deprecated 10AM task to ping specified user to update the spreadsheet
- Removed nightly updates for #music channel on Team Rainbow Rocket

### Some logs have been lost in the ether

### 0.2.0

- Added access to google sheet via gspread for music listening activities with Oubliette Alumni
- Added nightly updates for the /mu/ essentials thread on Oubliette Alumni and #music channel on Team Rainbow Rocket
- Added Album of the Day commands for any server: !album, !yesterday, !tomorrow
- Changed !help to reflect new music group based functionality
- Removed test features

### Some logs have been lost in the ether

### 0.1.0

- Initial release of Mareanie Bot

Check [Keep a Changelog](http://keepachangelog.com/) for recommendations on how to structure this file.
