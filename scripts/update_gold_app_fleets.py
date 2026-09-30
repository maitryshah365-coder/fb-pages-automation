import os

files = ['docs/js/gold_app.js', 'web/js/gold_app.js']

old_uk4 = """const FLEET_UK_04_IDS = [
  "1076375522219372", // Titan Archive
  "997596213442388",  // Sovereign Signal
  "1025542247301378", // Sunny Dusk Stories
  "981214481738903",  // Silver Oak Social
  "929190903615356",  // Mitchell Gabriel
  "803824339488556",  // Smith Arthur
  "762765990263739",  // Robinson Stephen
  "871774779344742",  // Powell Gabriel
  "746108741929454",  // Rodriguez Scott
  "818808074651170",  // Roberts Richard
  "417387901468629"   // Serendipity Spark
];"""

new_uk4 = """const FLEET_UK_04_IDS = [
  "1076375522219372", // Titan Archive
  "997596213442388",  // Sovereign Signal
  "1025542247301378", // Sunny Dusk Stories
  "981214481738903",  // Silver Oak Social
  "929190903615356",  // Mitchell Gabriel
  "803824339488556",  // Smith Arthur
  "762765990263739",  // Robinson Stephen
  "871774779344742",  // Powell Gabriel
  "746108741929454",  // Rodriguez Scott
  "818808074651170",  // Roberts Richard
  "417387901468629",  // Serendipity Spark
  "857530914106167"   // Robinson Jerry
];"""

old_uk7 = """const FLEET_UK_07_IDS = [
  "1191247700748920", // Dead Languages
  "1304768466050503", // Curse The Dawn
  "1338114526042607", // Cure For Monday
  "1315483674976229", // Cruel Mercy
  "1195883193618072", // Choke The Static
  "802518939617506",  // Lee Charles
  "896072510245887",  // Cooper Billy
  "864838050041932",  // Lee Daniel
  "870975689430311",  // Martin John
  "479102298617718",  // Corner Spe
  "208233979039379"   // Memes & Mischief
];"""

new_uk7 = """const FLEET_UK_07_IDS = [
  "1191247700748920", // Dead Languages
  "1304768466050503", // Curse The Dawn
  "1338114526042607", // Cure For Monday
  "1315483674976229", // Cruel Mercy
  "1195883193618072", // Choke The Static
  "802518939617506",  // Lee Charles
  "896072510245887",  // Cooper Billy
  "864838050041932",  // Lee Daniel
  "870975689430311",  // Martin John
  "479102298617718",  // Corner Spe
  "208233979039379",  // Memes & Mischief
  "755318371007926"   // Alexander Christopher
];"""

old_usa4 = """const FLEET_USA_04_IDS = [
  "usa4_p01_apex_house",
  "usa4_p02_quantum_house",
  "usa4_p03_drift_valley",
  "usa4_p04_dreams_of_life",
  "usa4_p05_end_every",
  "usa4_p06_executive_empire",
  "usa4_p07_im_joker",
  "usa4_p08_iron_covenant",
  "usa4_p09_iron_momentum",
  "usa4_p10_me_the",
  "usa4_p11_quiet_harbor",
  "usa4_p12_radiant_reverie",
  "usa4_p13_bit_creative",
  "usa4_p14_atlas_authority",
  "usa4_p15_blissful_paradox"
];"""

new_usa4 = """const FLEET_USA_04_IDS = [
  "497577420112654",  // Apex House
  "487987684400252",  // Quantum House
  "960803123790692",  // Drift Valley
  "923484537514216",  // Dreams Of Life
  "511317578722941",  // End Every
  "416325608224715",  // Executive Empire
  "467407709785240",  // I'm Joker
  "223604537511488",  // Iron Covenant
  "730487193489250",  // Iron Momentum
  "514016115120845",  // Me The
  "1009759155555480", // Quiet Harbor
  "922808234251176",  // Radiant Reverie
  "288008221072106",  // Bit Creative
  "243414155514799",  // Atlas Authority
  "921493174379801"   // Blissful Paradox
];"""

for path in files:
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Normalize line endings
    content = content.replace('\r\n', '\n')
    old_uk4_norm = old_uk4.replace('\r\n', '\n')
    old_uk7_norm = old_uk7.replace('\r\n', '\n')
    old_usa4_norm = old_usa4.replace('\r\n', '\n')

    assert old_uk4_norm in content, f'old_uk4 not found in {path}'
    content = content.replace(old_uk4_norm, new_uk4.replace('\r\n', '\n'))

    assert old_uk7_norm in content, f'old_uk7 not found in {path}'
    content = content.replace(old_uk7_norm, new_uk7.replace('\r\n', '\n'))

    assert old_usa4_norm in content, f'old_usa4 not found in {path}'
    content = content.replace(old_usa4_norm, new_usa4.replace('\r\n', '\n'))

    with open(path, 'w', encoding='utf-8') as f:
        f.write(content)
    print('Updated fleets in:', path)

print('All JS fleet registries synchronized successfully!')
