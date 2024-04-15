# dcinside 갤러리 크롤러
## config.json
1. `gallery_id` 항목을 크롤링 하고자하는 갤러리의 `id`로 설정  
2. `start_from` 항목을 자신이 크롤링을 시작하고자 글의 번호로 설정  
3. `save_dir` 항목을 크롤링된 데이터가 저장될 폴더의 경로로 설정  

## 크롤러 실행하기  
1. Python을 설치한다.  
- Python 3.11 이상을 권장  
2. git CLI을 설치한다.  
3. 크롤러를 다운받을 폴더에서 터미널(powershell, bash, terminal etc...)을 실행한다.  
4. `git clone https://github.com/sinsoon1229/dcinside-gallery-crawler` 명령어를 입력하여 크롤러를 설치한다.  
5. 터미널에 다음 후속 명령어 `pip install -r ./requirements.txt`를 입력하여 요구 패키지를 설치한다.  
- 해당 항목을 무시하고 `6번`에서 설명하는 대로 크롤러를 실행시켜도 요구 패키지가 설치되나, 한번 더 크롤러를 실행해야하는 번거로움과 안정성을 위해 본 항목을 따를 것을 추천드립니다.  
6. 크롤러를 실행하고 싶다면 `3번`과 마찬가지로 해당 폴더에서 터미널을 실행한 후 `python ./main.py` 명령어를 입력한다.  
크롤러를 종료하고 싶다면, 터미널에서 Ctrl-C를 입력하여 정상적으로 크롤러를 종료시키는 것을 권장드립니다.  
