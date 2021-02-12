from hazardMapGetter import HazardMapGetter
import json

if __name__ == '__main__':
    hmg = HazardMapGetter()
    # sh = hmg.get_kita_shelters_json()
    # hmg.dump_json("kita.json", sh)
    itabashi = hmg.get_itabashi_shelters_json()
    hmg.dump_json("itabashi.json", itabashi)