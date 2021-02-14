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

    # hmg.change_shelters_info_formatting("toshima", "豊島区")

    # これお金かかる。
    print('change_shelters_info_formatting...')
    hmg.change_shelters_info_formatting("kita", "北区")
    hmg.change_shelters_info_formatting("itabashi", "板橋区")
    hmg.change_shelters_info_formatting("toshima", "豊島区")
    hmg.change_shelters_info_formatting("nerima", "練馬区")

    print('load_json...')
    kita = hmg.load_json("kita_extended")
    itabashi = hmg.load_json("itabashi_extended")
    toshima = hmg.load_json("toshima_extended")
    nerima = hmg.load_json("nerima_extended")

    print('extend...')
    shs = []
    shs.extend(kita["shelters"])
    shs.extend(itabashi["shelters"])
    shs.extend(toshima["shelters"])
    shs.extend(nerima["shelters"])

    print('insert_shelters_info...')
    hmg.insert_shelters_info(shs)
    print('done.')





