from bs4 import BeautifulSoup
import requests


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
        # self.parser = BeautifulSoup(r.text, "html.parser")

    # 北区
    def get_kita_city_shelters(self) -> list[Shelter]:
        uri = "https://www.city.kita.tokyo.jp/shisetsu/bosai/hinanjo/"
        res = requests.get(uri)
        soup = BeautifulSoup(res.content, "html.parser")
        div_tmp_contents = soup.find("div", attrs={"id": "tmp_contents"})
        shelters = div_tmp_contents.find("ul").find_all("li")

        shelter_info: list[Shelter] = []

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
            gmap_url = (info_page.find("div", attrs={"id": "tmp_gmap_link"}).find("ul").find_all("li"))[0].find("a").get("href")
            c = gmap_url.replace("https://maps.google.com/maps?q=", "").split(",")
            coordinate["lat"] = c[0]
            coordinate["lng"] = c[1]

            print(f"{name}({address}) ['tell'='{call_number}', 'geo'=({coordinate['lat']}, {coordinate['lng']})]")
            shelter = Shelter(
                name=name,
                address=address,
                call_number=call_number,
                coordinate=coordinate,
                related_page=related_page
            )
            shelter_info.append(shelter)

        return shelter_info
