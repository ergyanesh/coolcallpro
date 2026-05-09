"""
One-shot mapper: city slug → GHCN-D station ID for the 115 published cities.

Reads:  scripts/ghcnd-stations.txt (NOAA inventory, ~78k US stations)
        scripts/city_data_map.json (our 115-city list w/ K-prefix codes)
Writes: scripts/city_data_map.json (adds ghcnd_station_id field)

Strategy:
  1. Hand-override mapping for cities where the K-prefix airport code is
     known (e.g., KATL → USW00013874). These bypass the auto-matcher because
     city-name string matching alone produces wrong picks (e.g., "Del Rio"
     matched as El Paso's nearest city in the same state).
  2. For any city not in the override list, run a strict scorer that
     requires both (a) the city's primary word in the station name and
     (b) an airport keyword (AIRPORT, AP, INTL).

Pure ICAO → WBAN mapping would be cleaner but requires another lookup
table NOAA doesn't expose directly. Hand-overrides are the practical fix.
"""
import json
import re
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
INV = Path(__file__).resolve().parent / "ghcnd-stations.txt"
MAP = Path(__file__).resolve().parent / "city_data_map.json"

HAND_OVERRIDES = {
    # Major hubs where K-prefix maps to a specific WBAN
    "atlanta-ga":         "USW00013874",  # KATL Hartsfield
    "houston-tx":         "USW00012960",  # KIAH Bush Intercontinental
    "fort-worth-tx":      "USW00003927",  # KDFW
    "el-paso-tx":         "USW00023044",  # KELP
    "kansas-city-mo":     "USW00003947",  # KMCI
    "chicago-il":         "USW00094846",  # KORD
    "new-york-city-ny":   "USW00094728",  # KNYC Central Park
    "newark-nj":          "USW00014734",  # KEWR
    "miami-fl":           "USW00012839",  # KMIA
    "honolulu-hi":        "USW00022521",  # KHNL
    "anchorage-ak":       "USW00026451",  # KANC
    "san-francisco-ca":   "USW00023234",  # KSFO
    "los-angeles-ca":     "USW00023174",  # KLAX
    "seattle-wa":         "USW00024233",  # KSEA
    "boston-ma":          "USW00014739",  # KBOS Logan
    "philadelphia-pa":    "USW00013739",  # KPHL
    "washington-dc":      "USW00013743",  # KDCA Reagan
    "minneapolis-mn":     "USW00014922",  # KMSP
    "denver-co":          "USW00003017",  # KDEN
    "phoenix-az":         "USW00023183",  # KPHX
    "dallas-tx":          "USW00013960",  # KDAL Love Field
    "san-diego-ca":       "USW00023188",  # KSAN
    "san-antonio-tx":     "USW00012921",  # KSAT
    "san-jose-ca":        "USW00023293",  # KSJC
    "austin-tx":          "USW00013904",  # KAUS
    "jacksonville-fl":    "USW00013889",  # KJAX
    "indianapolis-in":    "USW00093819",  # KIND
    "columbus-oh":        "USW00014821",  # KCMH
    "charlotte-nc":       "USW00013881",  # KCLT
    "detroit-mi":         "USW00094847",  # KDTW
    "memphis-tn":         "USW00013893",  # KMEM
    "louisville-ky":      "USW00093821",  # KSDF
    "baltimore-md":       "USW00093721",  # KBWI
    "milwaukee-wi":       "USW00014839",  # KMKE
    "albuquerque-nm":     "USW00023050",  # KABQ
    "tucson-az":          "USW00023160",  # KTUS
    "fresno-ca":          "USW00093193",  # KFAT
    "sacramento-ca":      "USW00023232",  # KSAC Executive
    "long-beach-ca":      "USW00023129",  # KLGB
    "mesa-az":            "USW00023183",  # uses PHX
    "virginia-beach-va":  "USW00013737",  # uses Norfolk KORF
    "colorado-springs-co":"USW00093037",  # KCOS
    "raleigh-nc":         "USW00013722",  # KRDU
    "omaha-ne":           "USW00094918",  # KOMA
    "oakland-ca":         "USW00023230",  # KOAK
    "tulsa-ok":           "USW00013968",  # KTUL
    "wichita-ks":         "USW00003928",  # KICT
    "new-orleans-la":     "USW00012916",  # KMSY
    "tampa-fl":           "USW00012842",  # KTPA
    "cleveland-oh":       "USW00014820",  # KCLE
    "bakersfield-ca":     "USW00023155",  # KBFL
    "aurora-co":          "USW00003017",  # uses DEN
    "anaheim-ca":         "USW00093184",  # uses KSNA
    "santa-ana-ca":       "USW00093184",  # KSNA
    "riverside-ca":       "USW00003171",  # KRIV
    "stockton-ca":        "USW00023237",  # KSCK
    "lexington-ky":       "USW00093820",  # KLEX
    "henderson-nv":       "USW00023169",  # uses LAS
    "saint-paul-mn":      "USW00014922",  # uses MSP
    "st-paul-mn":         "USW00014922",
    "cincinnati-oh":      "USW00093814",  # KCVG
    "pittsburgh-pa":      "USW00094823",  # KPIT
    "plano-tx":           "USW00003927",  # uses DFW
    "lincoln-ne":         "USW00014939",  # KLNK
    "buffalo-ny":         "USW00014733",  # KBUF
    "fort-wayne-in":      "USW00014827",  # KFWA
    "jersey-city-nj":     "USW00094728",  # uses NYC
    "chula-vista-ca":     "USW00023188",  # uses SAN
    "norfolk-va":         "USW00013737",  # KORF
    "chesapeake-va":      "USW00013737",  # uses Norfolk
    "winston-salem-nc":   "USW00013723",  # uses Greensboro KGSO
    "irving-tx":          "USW00003927",  # uses DFW
    "garland-tx":         "USW00003927",  # uses DFW
    "scottsdale-az":      "USW00023183",  # uses PHX
    "glendale-az":        "USW00023183",  # uses PHX
    "north-las-vegas-nv": "USW00023169",  # uses LAS
    "irvine-ca":          "USW00093184",  # uses SNA
    "fremont-ca":         "USW00023293",  # uses SJC
    "boise-id":           "USW00024131",  # KBOI
    "spokane-wa":         "USW00024157",  # KGEG
    "richmond-va":        "USW00013740",  # KRIC
    "rochester-ny":       "USW00014768",  # KROC
    "modesto-ca":         "USW00023258",  # KMOD
    "fayetteville-nc":    "USW00013714",  # KFAY
    "tacoma-wa":          "USW00024233",  # uses SEA
    "oxnard-ca":          "USW00093110",  # KOXR
    "fontana-ca":         "USW00003171",  # uses RIV
    "moreno-valley-ca":   "USW00003171",  # uses RIV
    "huntington-beach-ca":"USW00093184",  # uses SNA
    "glendale-ca":        "USW00023174",  # uses LAX
    "des-moines-ia":      "USW00014933",  # KDSM
    "yonkers-ny":         "USW00094728",  # uses NYC
    "shreveport-la":      "USW00013957",  # KSHV
    "augusta-ga":         "USW00003820",  # KAGS
    "mobile-al":          "USW00013894",  # KMOB
    "little-rock-ar":     "USW00013963",  # KLIT
    "amarillo-tx":        "USW00023047",  # KAMA
    "akron-oh":           "USW00014895",  # KCAK
    "huntsville-al":      "USW00003856",  # KHSV
    "grand-rapids-mi":    "USW00094860",  # KGRR
    "salt-lake-city-ut":  "USW00024127",  # KSLC
    "tallahassee-fl":     "USW00093805",  # KTLH
    "worcester-ma":       "USW00094746",  # KORH
    "newport-news-va":    "USW00013741",  # KPHF
    "knoxville-tn":       "USW00013891",  # KTYS
    "providence-ri":      "USW00014765",  # KPVD
    "fort-lauderdale-fl": "USW00012849",  # KFLL
    "chattanooga-tn":     "USW00013882",  # KCHA
    "tempe-az":           "USW00023183",  # uses PHX
    "ontario-ca":         "USW00003102",  # KONT
    "vancouver-wa":       "USW00024229",  # uses PDX
    "rancho-cucamonga-ca":"USW00003171",  # uses RIV
    "santa-rosa-ca":      "USW00023213",  # KSTS
    "salem-or":           "USW00024232",  # KSLE
    "corona-ca":          "USW00003171",  # uses RIV
    "eugene-or":          "USW00024221",  # KEUG
    "elk-grove-ca":       "USW00023232",  # uses SAC
    "salinas-ca":         "USW00023273",  # KSNS
    "garden-grove-ca":    "USW00093184",  # uses SNA
    "pasadena-ca":        "USW00023174",  # uses LAX
    "rockford-il":        "USW00094822",  # KRFD
    "pomona-ca":          "USW00003171",  # uses RIV
    "torrance-ca":        "USW00023174",  # uses LAX
    "syracuse-ny":        "USW00014771",  # KSYR
    "kansas-city-ks":     "USW00003947",  # uses MCI
    "charleston-sc":      "USW00013880",  # KCHS
    "columbia-sc":        "USW00013883",  # KCAE
    "greenville-sc":      "USW00013886",  # KGSP
    "savannah-ga":        "USW00003822",  # KSAV
    "macon-ga":           "USW00003813",  # KMCN
    "athens-ga":          "USW00013873",  # KAHN
    "lubbock-tx":         "USW00023042",  # KLBB
    "killeen-tx":         "USW00003901",  # uses Robert Gray
    "frisco-tx":          "USW00003927",  # uses DFW
    "mckinney-tx":        "USW00003927",  # uses DFW
    "denton-tx":          "USW00003927",  # uses DFW
    "fort-collins-co":    "USW00094016",  # KFNL
    "peoria-il":          "USW00014842",  # KPIA
    "aurora-il":          "USW00094892",  # KARR
    "joliet-il":          "USW00094872",  # KJOT
    "naperville-il":      "USW00094822",  # uses RFD
    "elgin-il":           "USW00094892",  # uses ARR
    "springfield-mo":     "USW00013995",  # KSGF
    "springfield-il":     "USW00093822",  # KSPI
    "springfield-ma":     "USW00014739",  # uses BOS
    "evansville-in":      "USW00093817",  # KEVV
    "south-bend-in":      "USW00014848",  # KSBN
    "cedar-rapids-ia":    "USW00094910",  # KCID
    "davenport-ia":       "USW00094982",  # KDVN
    "topeka-ks":          "USW00013996",  # KTOP
    "overland-park-ks":   "USW00003947",  # uses MCI
    "olathe-ks":          "USW00003947",  # uses MCI
    "fremont-ne":         "USW00094918",  # uses OMA
    "fargo-nd":           "USW00014914",  # KFAR
    "bismarck-nd":        "USW00024011",  # KBIS
    "rapid-city-sd":      "USW00024090",  # KRAP
    "sioux-falls-sd":     "USW00014944",  # KFSD
    "billings-mt":        "USW00024033",  # KBIL
    "missoula-mt":        "USW00024153",  # KMSO
    "great-falls-mt":     "USW00024143",  # KGTF
    "idaho-falls-id":     "USW00024156",  # KIDA
    "casper-wy":          "USW00024089",  # KCPR
    "cheyenne-wy":        "USW00024018",  # KCYS
    "reno-nv":            "USW00023185",  # KRNO
    "carson-city-nv":     "USW00023185",  # uses RNO
    "las-vegas-nv":       "USW00023169",  # KLAS
    "santa-fe-nm":        "USW00023050",  # uses ABQ
    "west-valley-city-ut":"USW00024127",  # uses SLC
    "provo-ut":           "USW00024174",  # KPVU
    "ogden-ut":           "USW00024127",  # uses SLC
    "albany-ny":          "USW00014735",  # KALB
    "wilmington-de":      "USW00013781",  # KILG
    "allentown-pa":       "USW00014737",  # KABE
    "harrisburg-pa":      "USW00014711",  # KMDT
    "lancaster-pa":       "USW00014737",  # uses ABE
    "paterson-nj":        "USW00014734",  # uses EWR
    "elizabeth-nj":       "USW00014734",  # uses EWR
    "trenton-nj":         "USW00014792",  # KTTN
    "manchester-nh":      "USW00014710",  # KMHT
    "burlington-vt":      "USW00014742",  # KBTV
    "hartford-ct":        "USW00014740",  # KBDL
    "bridgeport-ct":      "USW00094702",  # KHVN nearby
    "stamford-ct":        "USW00094728",  # uses NYC
    "lowell-ma":          "USW00014739",  # uses BOS
    "cambridge-ma":       "USW00014739",  # uses BOS
    "portland-me":        "USW00014764",  # KPWM
    "augusta-me":         "USW00014605",  # KAUG
    "bangor-me":          "USW00014606",  # KBGR
    "concord-nh":         "USW00014745",  # KCON
    "juneau-ak":          "USW00025309",  # KJNU
    "fairbanks-ak":       "USW00026411",  # KFAI
    "jackson-ms":         "USW00003940",  # KJAN
    "charleston-wv":      "USW00013866",  # KCRW
    "toledo-oh":          "USW00094830",  # KTOL
    "dayton-oh":          "USW00093815",  # KDAY
    "lansing-mi":         "USW00014836",  # KLAN
    "ann-arbor-mi":       "USW00094847",  # uses DTW
    "sterling-heights-mi":"USW00094847",  # uses DTW
    "warren-mi":          "USW00094847",  # uses DTW
    "fort-myers-fl":      "USW00012894",  # KRSW
    "orlando-fl":         "USW00012815",  # KMCO
    "st-petersburg-fl":   "USW00092806",  # KPIE
    "saint-petersburg-fl":"USW00092806",
    "hialeah-fl":         "USW00012839",  # uses MIA
    "cape-coral-fl":      "USW00012894",  # uses RSW
    "miramar-fl":         "USW00012849",  # uses FLL
    "pembroke-pines-fl":  "USW00012849",  # uses FLL
    "hollywood-fl":       "USW00012849",  # uses FLL
    "gainesville-fl":     "USW00003820",  # uses GNV station? KGNV
    "lakeland-fl":        "USW00092806",  # uses PIE
    "kissimmee-fl":       "USW00012815",  # uses MCO
    "port-st-lucie-fl":   "USW00012849",  # uses FLL
    "saint-louis-mo":     "USW00013994",  # KSTL
    "st-louis-mo":        "USW00013994",
    "independence-mo":    "USW00003947",  # uses MCI
    "columbia-mo":        "USW00003945",  # KCOU
    "lees-summit-mo":     "USW00003947",  # uses MCI
    "ofallon-mo":         "USW00013994",  # uses STL
    "st-charles-mo":      "USW00013994",  # uses STL
    "kansas-city-mo":     "USW00003947",
    "tulsa-ok":           "USW00013968",
    "oklahoma-city-ok":   "USW00013967",  # KOKC
    "norman-ok":          "USW00003967",  # KOUN
    "lawton-ok":          "USW00013966",  # KLAW
    "broken-arrow-ok":    "USW00013968",  # uses TUL
    "edmond-ok":          "USW00013967",  # uses OKC
    "moore-ok":           "USW00013967",  # uses OKC
    "midwest-city-ok":    "USW00013967",  # uses OKC
    "stillwater-ok":      "USW00013967",  # uses OKC
    "enid-ok":            "USW00013967",  # uses OKC
    "muskogee-ok":        "USW00013968",  # uses TUL
    "bartlesville-ok":    "USW00013968",  # uses TUL
    "shawnee-ok":         "USW00013967",  # uses OKC
    "ponca-city-ok":      "USW00013967",  # uses OKC
    "ardmore-ok":         "USW00013966",  # uses LAW
    "bethany-ok":         "USW00013967",  # uses OKC
    "duncan-ok":          "USW00013966",  # uses LAW
    "yukon-ok":           "USW00013967",  # uses OKC
    "del-city-ok":        "USW00013967",  # uses OKC
}


def main():
    inv_text = INV.read_text(encoding="utf-8", errors="replace")
    cities = json.loads(MAP.read_text(encoding="utf-8"))

    # Parse station inventory once
    by_state = {}
    for line in inv_text.splitlines():
        if len(line) < 85:
            continue
        sid = line[0:11].strip()
        if not sid.startswith("US"):
            continue
        st = line[38:40].strip()
        nm = line[41:71].strip()
        wmo = line[80:85].strip()
        by_state.setdefault(st, []).append({"id": sid, "name": nm, "wmo": wmo})

    # Match each city
    matched = {}
    unmatched = []
    for slug, e in cities.items():
        if slug in HAND_OVERRIDES:
            matched[slug] = HAND_OVERRIDES[slug]
            continue
        # Strict scorer for non-overridden cities
        st = e["state"]
        candidates = by_state.get(st, [])
        primary = re.split(r"[ .'-]", e["city"].upper())[0]
        if len(primary) < 4:
            primary = e["city"].upper().replace(" ", "")
        scored = []
        for s in candidates:
            n = s["name"].upper()
            score = 0
            if primary in n:
                score += 20
            if "AIRPORT" in n or n.endswith(" AP") or " AP " in n or "AIRPRT" in n:
                score += 10
            if "INTL" in n or "INTERNATIONAL" in n:
                score += 5
            if s["id"].startswith("USW"):
                score += 3
            if s["wmo"]:
                score += 2
            if score >= 25:
                scored.append((score, s))
        scored.sort(key=lambda x: (-x[0], x[1]["id"]))
        if scored:
            matched[slug] = scored[0][1]["id"]
        else:
            unmatched.append(slug)

    # Emit summary
    print(f"Matched:   {len(matched)} of {len(cities)}")
    print(f"Unmatched: {len(unmatched)}")
    for slug in unmatched:
        e = cities[slug]
        print(f"  - {slug:25s} (city={e['city']}, state={e['state']}, K={e['noaa_station']})")

    # Write back
    for slug, sid in matched.items():
        cities[slug]["ghcnd_station_id"] = sid
    MAP.write_text(json.dumps(cities, indent=2), encoding="utf-8")
    print(f"\nUpdated {MAP}")


if __name__ == "__main__":
    main()
