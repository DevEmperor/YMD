# YMD (Youtube Music Downloader)

**YMD (Youtube Music Downloader) is a command line tool for downloading content from Youtube Music.**



## Dependencies

- Python 3.6 or higher
- git and pip



## Installation and preparation

1. Clone this git-repository:

   ```bash
   git clone https://github.com/DevEmperor/ymd.git
   ```

2. install the dependencies (python libraries):

   ```bash
   pip3 install -r requirements.txt
   ```

**Only if you want YMD to add lyrics to your tracks:**

3. visit [https://genius.com/api-clients/new](https://genius.com/api-clients/new) and create a new API client (enter only "App Name" and "App Website URL"; you can set "App Website URL" to the URL of this repository), then click on "Generate Access Token" and copy the token into the configuration section of "_ymd.py_"


4. Run YMD:
   ```bash
   python3 ymd.py
   ```


## Usage

1. Run YMD with `python3 ymd.py`
2. Enter the path to your output directory. (If you always want to export to the same folder, you can also enter the path in the configuration section of "*ymd.py*")
3. Enter a URL from Youtube Music and press ENTER. YMD will download the track / album / playlist and collects all Metadata (+ Lyrics if you added an API key for Genius). 



## License

YMD is under the terms of the [Apapche 2.0 license](https://www.apache.org/licenses/LICENSE-2.0), following all clarifications stated in the [license file](https://raw.githubusercontent.com/DevEmperor/YMD/master/LICENSE)
