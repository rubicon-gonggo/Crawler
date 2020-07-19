import argparse
import json
import requests
import time
import traceback
from pprint import pprint

parser = argparse.ArgumentParser(description='크롤링 결과를 POST로 PRODUCTION에 반영')
parser.add_argument('--endpoint',
                    required=True,
                    type=str,
                    help='production endpoint')

if __name__ == "__main__":

    args = parser.parse_args()
    endpoint = args.endpoint
    uri = endpoint + "/production/api/crawler/"

    with open("page_ids.json", "r") as f:
        page_ids_dict = json.load(f)

    page_ids = list(page_ids_dict.keys())
    page_ids.reverse()

    for page_id in page_ids:
        try:
            with open("json/{}.json".format(page_id), "r") as f:
                data = json.load(f)
            if not data:
                continue
            cond = ("winner_announce_date" in list(data.keys()))

            if cond == True:
                data["winner_announce_date"] = data["winner_announce_date"]
                winner_announce_date = data["winner_announce_date"]
            else:
                data["winner_announce_date"] = "미정"
                winner_announce_data = "미정"

            if len(winner_announce_date) > 15:
                data["winner_announce_date"] = winner_announce_date.split("\n")[
                    0]

            status = page_ids_dict[str(page_id)]["status"]
            region = page_ids_dict[str(page_id)]["region"]

            data["status"] = status
            data["region"] = [region]

            json_data = json.dumps(data)

            res = requests.post(uri,
                                data=json_data,
                                headers={'content-type': 'application/json'})

            if res.status_code == 200:
                print("{} in {}".format(res.status_code, page_id))
            else:
                print("fail in {}".format(page_id))
                print("message : {}".format(res))
                raise RuntimeError("http status code is not 200")

        except Exception as e:
            print("Exception : {}".format(e))
            print("page id : {}".format(page_id))
            traceback.print_exc()
