# dcinside 갤러리 크롤러
## config.json
1. `gallery_id` 항목을 크롤링 하고자하는 갤러리의 `id`로 설정  
2. `start_from` 항목을 자신이 크롤링을 시작하고자 글의 번호로 설정  
3. `save_dir` 항목을 크롤링된 데이터가 저장될 폴더의 경로로 설정  

## 크롤러 실행하기  
1. [Python](https://www.python.org/downloads/)을 설치한다.  
    - Python 3.11 이상 버전을 권장  
2. [git](https://git-scm.com/downloads)을 설치한다.  
3. 크롤러를 설치할 폴더에서 터미널(cmd, powershell, bash, etc...)을 실행한다.  
4. `git clone https://github.com/sinsoon1229/dcinside-gallery-crawler` 명령어를 입력하여 크롤러를 설치한다.  
5. `cd ./dc-inside-crawler` 명령어를 실행하여 크롤러가 설치된 폴더로 이동한다.  
6. 터미널에 다음 후속 명령어 `pip install -r ./requirements.txt`를 입력하여 요구 패키지를 설치한다.  
또는, 크롤러를 실행하여 요구 패키지를 자동으로 설치한다.  
7. 크롤러를 실행하고 싶다면 `4번`~`5번`과 마찬가지로 해당 폴더에서 실행한 터미널에서 `python ./main.py` 명령어를 입력한다.  
크롤러를 종료하고 싶다면, 터미널에서 Ctrl-C를 입력하여 안정적으로 크롤러를 종료시킨다.  
