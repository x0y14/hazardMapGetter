from hazardMapGetter import HazardMapGetter
import json

if __name__ == '__main__':
    hmg = HazardMapGetter()
    # sh = hmg.get_kita_shelters_json()
    # hmg.dump_json("kita.json", sh)
    # itabashi = hmg.get_itabashi_shelters_json()
    # hmg.dump_json("itabashi.json", itabashi)
    # # toshima = hmg.get_toshima_shelters_json()
    # # hmg.dump_json("toshima.json", toshima)
    # nerima = hmg.get_nerima_shelters_json()
    # hmg.dump_json("nerima.json", nerima)
    # hmg.get_coordinate_from_address("練馬区練馬1丁目17番1号")

    hmg.change_shelters_info_formatting("toshima", "豊島区")
