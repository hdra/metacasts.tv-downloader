#Metacasts.tv Downloader

Download metacasts.tv videos. Requires an active subscription

## Setup:
* Download the script
* Install `requests`, `beautifulsoup4`, and `fish` via `pip` (or just install the list in `requirements.txt`.
* Login to metacasts.tv and copy the `_metacasts_session` cookie and paste it into `download.py`.
You can use the browser dev tools or any other way to obtain the cookie.


## Usage:
	python download.py 

	#Download video #10-15 only
	python download.py 10 15

