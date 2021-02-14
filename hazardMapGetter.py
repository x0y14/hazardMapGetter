from bs4 import BeautifulSoup
import requests
import json
import re


class Shelter:
    def __init__(self, name: str, address: str, call_number: str, coordinate: dict, related_page: str):
        self.name = name
        self.address = address
        self.call_number = call_number
        self.coordinate = coordinate
        self.related_page = related_page


class HazardMapGetter:
    def __init__(self):
        self.version = 0.1

    @staticmethod
    def dump_json(file_name: str, data: dict):
        with open(f'./shelters/{file_name}', 'w') as f:
            json.dump(data, f, sort_keys=False, ensure_ascii=False)
        print(f"[INFO] dump success to './shelters/{file_name}'.")

    # 北区(https://www.city.kita.tokyo.jp/shisetsu/bosai/hinanjo/)
    @staticmethod
    def get_kita_shelters_json() -> dict:
        uri = "https://www.city.kita.tokyo.jp/shisetsu/bosai/hinanjo/"
        res = requests.get(uri)
        if (res.status_code != 200):
            raise Exception("error")
        soup = BeautifulSoup(res.content, "html.parser")
        div_tmp_contents = soup.find("div", attrs={"id": "tmp_contents"})
        shelters = div_tmp_contents.find("ul").find_all("li")

        # shelter_info: list[Shelter] = []

        shelters_info = {
            "shelters": []
        }

        for s in shelters:
            data = s.find("a")

            # 避難所名
            name = data.text
            if "（" in name:
                name = name.split("（")[0]
                # "北区役所滝野川分庁舎（旧滝野川中学校）" -> "北区役所滝野川分庁舎"

            endpoint = data.get("href")
            r = requests.get(f"https://www.city.kita.tokyo.jp{endpoint}")
            info_page = BeautifulSoup(r.content, "html.parser")

            # 住所 & 電話番号
            info = info_page.find("div", attrs={"id": "tmp_contents"}).find("table").find_all("tr")

            # place holder
            address = ""
            call_number = ""
            related_page = ""

            for j in info:
                if (td_data := j.find("td")) is not None:
                    address_or_call_number = td_data.find("p").text
                    if address_or_call_number[0] == "0":
                        call_number = address_or_call_number
                    elif (address_or_call_number[0] != "0") and (any(_.isdigit() for _ in address_or_call_number)):
                        address = address_or_call_number
                    else:
                        related_page = address_or_call_number

            # place_holder
            coordinate = {"lat": "", "lng": ""}
            gmap_url = (info_page.find("div", attrs={"id": "tmp_gmap_link"}).find("ul").find_all("li"))[0].find(
                "a").get("href")
            c = gmap_url.replace("https://maps.google.com/maps?q=", "").split(",")
            coordinate["lat"] = c[0]
            coordinate["lng"] = c[1]

            shelter = {
                "name": name,
                "address": address,
                "call_number": call_number,
                "capacity": 0,
                "coordinate": coordinate,
                "related_page": related_page,
            }
            shelters_info["shelters"].append(shelter)

            # shelter_info.append(shelter)

        return shelters_info

    # 板橋区(https://www.city.itabashi.tokyo.jp/area/itabashi_bousai)
    @staticmethod
    def get_itabashi_shelters_json():
        hinanjo_point_uri = "https://www.city.itabashi.tokyo.jp/area/itabashi_bousai/data/geojson/hinanjo_point.geojson?_=1612865400304"
        hinanjo_other_uri = "https://www.city.itabashi.tokyo.jp/area/itabashi_bousai/data/geojson/hinanjo_other.geojson?_=1612865400305"

        hp = requests.get(hinanjo_point_uri)
        ho = requests.get(hinanjo_other_uri)
        if (hp.status_code != 200) or (ho.status_code != 200):
            raise Exception("error")

        shelters_info = {
            "shelters": []
        }

        # jetbrainsに注意されたので、まとめる。
        shpo = []
        # 通常
        shpo.extend(hp.json()["features"])
        # その他
        shpo.extend(ho.json()["features"])

        for shltr in shpo:

            if shltr["properties"]["電話"] is None:
                call_number = ""
            elif "-" in shltr["properties"]["電話"]:
                call_number = shltr["properties"]["電話"]
            else:
                call_number_regex = re.match(r"\(([0-9]*)\)([0-9]*)", str(shltr["properties"]["電話"]))
                call_number = f"03-{call_number_regex.group(1)}-{call_number_regex.group(2)}"


            if shltr["properties"]["収容可能"] is None:
                capa = 0
            else:
                capa = shltr["properties"]["収容可能"]
                if "，" in capa:
                    capa = capa.replace('，', "")
                capa = int(capa)

            shelters_info["shelters"].append(
                {
                    # "category": "hinanjo",
                    # "area": shltr["properties"]["地域センタ"],
                    "name": shltr["properties"]["施設名"],
                    "address": shltr["properties"]["所在地"],
                    "call_number": call_number,
                    "capacity": capa,
                    "coordinate": {
                        "lat": shltr["geometry"]["coordinates"][1],
                        "lng": shltr["geometry"]["coordinates"][0],
                    },
                    "related_page": ""
                }
            )

        return shelters_info

    # 豊島区(http://www.city.toshima.lg.jp/042/bosai/taisaku/yobo/kokorogamae/007197.html)
    # pdf(http://www.city.toshima.lg.jp/042/bosai/taisaku/yobo/kokorogamae/documents/oomotemenn.pdf)
    # から手動で抜き出した。
    def get_toshima_shelters_json(self):
        toshima_template = self.gen_shelters_json_template(
            items=[
                ("name", "str"),
                ("address", "str"),
                ("call_number", "str"),
                ("capacity", "int"),
                ("coordinate", "coordinate"),
                ("related_page", "str"),
            ], duplicate=34
        )
        return toshima_template

    # 豊島区みたいに要素が少ないもの、あまり親切に作られていないもの、から情報を手動で抜き出す時用の手助け関数。
    @staticmethod
    def gen_shelters_json_template(items: list[(str, str)], duplicate: int):
        # gen
        # item format (item_name: str, type: str)
        # place_holder: {str: "", int: 0, list: [], coordinate: {"lat": (None)null, "lng": (None)null}}
        shelters_info = {
            "shelters": []
        }

        shelter = {}
        for i in items:
            # itemのタイプが不明でないもののみ取り扱いたい。。
            if i[1] not in ['int', 'str', 'list', 'coordinate']:
                raise Exception("Item type must be in ['int', 'str', 'list', 'coordinate'].")

            # 重複を禁止したい。
            if shelter.get(i[0]):
                raise Exception("Duplicates are prohibited.")

            # 各々。
            if i[1] == "str":
                shelter[i[0]] = ""
            elif i[1] == "int":
                shelter[i[0]] = 0
            elif i[1] == "list":
                shelter[i[0]] = []
            elif i[1] == "coordinate":
                shelter[i[0]] = {"lat": None, "lng": None}
            else:
                raise Exception("unknown type")

        for d in range(duplicate):
            shelters_info["shelters"].append(shelter)

        return shelters_info

    # 練馬区(https://www.city.nerima.tokyo.jp/kurashi/bosai/jishinokitara/hinanjo/hinanjyoitiran.html)
    @staticmethod
    def get_nerima_shelters_json():

        shelters_info = {
            "shelters": []
        }

        header = {"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15"}
        res = requests.get("https://www.city.nerima.tokyo.jp/kurashi/bosai/jishinokitara/hinanjo/hinanjyoitiran.html", headers=header)
        if res.status_code != 200:
            raise Exception("error")
        page = BeautifulSoup(res.content, "html.parser")

        # program

        # 避難拠点のみ。
        for tr in page.find_all("tr"):
            # shelter_number.textするとエラー出る。
            # いらない情報なので直さない。
            shelter_number = tr.find("td", class_="center")
            if (shelter_number is None) or (not shelter_number.text.isdigit()):
                continue

            # print(tr.find_all("td", class_="center")[0].text)

            shelter_name = tr.find("a", class_="externalLink").text

            # shelterの住所の書き方バラバラなのでたくさん試す。
            # 滅びろ練馬区。
            for td in tr.find_all("td"):
                if "号" in td.text:
                    shelter_address = td.text

            # print(f"{shelter_name}: {shelter_address}")
            # ("name", "str"),
            # ("address", "str"),
            # ("call_number", "str"),
            # ("coordinate", "coordinate"),
            # ("related_page", "str"),

            shelters_info["shelters"].append(
                {
                    "name": shelter_name,
                    "address": shelter_address,
                    "call_number": "",
                    "capacity": 0,
                    "coordinate": {
                        "lat": None,
                        "lng": None,
                    },
                    "related_page": "",
                }
            )
        return shelters_info



