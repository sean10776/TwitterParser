# TwitterParser
 TwitterAPI爬蟲下載影片or圖片

 Twitter.py旁要包含<br>
 `license.json`
 ```json
 {
    "consumer_key": "consumer key put here",
    "consumer_secret": "consumer secret put here"
 }
 ```

### 使用方式

- 搜尋帳號
 ```
 python .\TwitterParse.py -a "@帳號名稱" -q -v
 ```

- 搜尋關鍵字
 ```
 python .\TwitterParse.py -q "關鍵字/Hashtag" -q -v
 ```

- 指定路徑
```
 python .\TwitterParse.py -q "關鍵字/Hashtag" -od "路徑" -q -v
```