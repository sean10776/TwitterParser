import os, sys, wget, json
import tweepy as tw
from pathlib import Path

#中斷 signal
import signal
class SignalHandle(object):   
    def __init__(self, sig=signal.SIGINT):
        self.sig = sig
        self.original_handler = signal.getsignal(self.sig)
        self.interrupted = False
        self.released = False

    def __enter__(self):
        def handler(signum, frame):
            self.release()
            self.interrupted = True

        signal.signal(self.sig, handler)
        return self

    def __exit__(self, type, value, tb):
        print("wait exit")
        self.release()

    def release(self):
        if self.released:
            return False

        signal.signal(self.sig, self.original_handler)
        self.released = True
        return True

class TweetParse():
    def __init__(self) -> None:
        ck, cs = self._get_api_license()
        auth = tw.OAuthHandler(ck, cs)
        self.api = tw.API(auth)
        self.floder = ""
        pass

    def _get_api_license(self):
        # TODO read automatic
        if not Path('license.json').exists():
            raise FileNotFoundError("license.json不存在")
        with open('license.json', "r") as f:
            data = json.loads(f.read())
        try:
            consumer_key = data["consumer_key"]
            consumer_secret = data['consumer_secret']
        except KeyError as e:
            raise KeyError(f"license.json檔不含{e}")
        return consumer_key, consumer_secret

    def _generate_save_floder(self, dir, tag):
        # 建立out_dir
        save_floder = Path(f'{dir}/{tag}')
        for i in reversed(save_floder.parents):
            if not i.exists():
                i.mkdir()
        if not save_floder.exists():
            save_floder.mkdir()
        for i in ['photo', 'video', 'animated_gif']:
            if not Path(f'{save_floder}/{i}').exists():
                Path(f'{save_floder}/{i}').mkdir()
        self.floder = save_floder

    def _download_Img(self, url, type):
        file_name = url[url.rfind('/')+1:]
        if file_name in [f.name for f in self.floder.rglob('*')]:
            return
        wget.download(url, out=f'{self.floder}/{type}/{file_name}')

    def _process_tweet(self, tweet, photo = True, video_gif = True):
        try:
            media = tweet.extended_entities
            if not media:
                media = tweet.entities.get('media', [])
            else:
                media = media["media"]
            if( len(media) > 0):
                for i in media:
                    if i["type"] == 'photo' and photo:
                        url = i['media_url']
                    elif i['type'] in ['video', 'animated_gif'] and video_gif:
                        variants = i["video_info"]["variants"]
                        variants.sort(key=lambda x: x.get("bitrate", 0))
                        url = variants[-1]["url"].rsplit("?tag")[0]
                    else:
                        continue
                    # print(i['type'], url)
                    self._download_Img(url, i['type'])
        except AttributeError:
            return
            

    def parser(self, account, query, out_dir, limit, photo, video):
        with SignalHandle() as h:
            if account != "":
                self._generate_save_floder(out_dir, account)
                count = 0
                for tweet in tw.Cursor(self.api.user_timeline, id=account, tweet_mode="extended").items():
                    self._process_tweet(tweet, photo=photo, video_gif=video)
                    count += 1
                    if h.interrupted or (count > limit and limit != 0):
                        break
            if query != "":        
                self._generate_save_floder(out_dir, query)
                count = 0
                for tweet in tw.Cursor(self.api.search_tweets, q=query, include_entities=True).items():
                    self._process_tweet(tweet, photo=photo, video_gif=video)
                    if h.interrupted or (count > limit and limit != 0):
                        break
        print("done")
            

if __name__ == "__main__":
    from argparse import ArgumentParser

    arg_parser = ArgumentParser()
    arg_parser.add_argument("--account", type=str, help="Twitter 帳號", default="")
    arg_parser.add_argument('-q',"--query", type=str, help="內文活Hashtag", default="")
    arg_parser.add_argument("--out_dir", type=str, help="存檔路徑", default='./parser')
    arg_parser.add_argument("--limit", type=int, help="爬文數量", default=0)
    arg_parser.add_argument('-p',"--photo", help="是否下載圖片", action='store_true')
    arg_parser.add_argument('-v',"--video", help="是否下載影片", action='store_true')
    args = arg_parser.parse_args()
    print(args)

    parser = TweetParse()
    parser.parser(args.account, args.query, args.out_dir, args.limit, args.photo, args.video)