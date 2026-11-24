#!/usr/bin/env python3
"""news-image 23 Nov 2026 -- v3 broadsheet, 1024x1024 PNG, deterministic.

Written from scratch for the make.fun news-image-20261123 bounty
(entry @koitalk). 60 Monday-pure stories from NEWS_23NOV.md:
3 leads + 12 medium + 45 Also Today, plus the resolved late finals
(MNF Commanders 22-20 Bengals; Brentford 4-0 Everton; Levante 1-1
Elche; Monza 3-0 Fiorentina) and the verified market closes.

Body text uses a hand-drawn 5x7 bitmap font (6px advance, 9px line
pitch): deliberately spacious, never a denser body font. No external
font files, no timestamps, no randomness -- re-runs are byte-identical.
"""
import hashlib
import os

from PIL import Image, ImageDraw

W, H = 1024, 1024
HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "entry.png")

INK = (18, 18, 18)
PAPER = (250, 247, 238)
RED = (178, 34, 34)
BLUE = (30, 80, 130)

# ---------------------------------------------------------------- font: 5x7
# Each glyph is 7 rows of 5 cells ('#' = ink). Lowercase keeps the same
# 7-row cell with x-height 5 and descenders on rows 6-7, so 'g', 'j',
# 'p', 'q', 'y' drop below the baseline like real text.
FONT = {
    "A": (".###.", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "B": ("####.", "#...#", "#...#", "####.", "#...#", "#...#", "####."),
    "C": (".####", "#....", "#....", "#....", "#....", "#....", ".####"),
    "D": ("####.", "#...#", "#...#", "#...#", "#...#", "#...#", "####."),
    "E": ("#####", "#....", "#....", "####.", "#....", "#....", "#####"),
    "F": ("#####", "#....", "#....", "####.", "#....", "#....", "#...."),
    "G": (".####", "#....", "#....", "#.###", "#...#", "#...#", ".###."),
    "H": ("#...#", "#...#", "#...#", "#####", "#...#", "#...#", "#...#"),
    "I": (".###.", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "J": ("..###", "...#.", "...#.", "...#.", "...#.", "#..#.", ".##.."),
    "K": ("#...#", "#..#.", "#.#..", "##...", "#.#..", "#..#.", "#...#"),
    "L": ("#....", "#....", "#....", "#....", "#....", "#....", "#####"),
    "M": ("#...#", "##.##", "#.#.#", "#.#.#", "#...#", "#...#", "#...#"),
    "N": ("#...#", "##..#", "##..#", "#.#.#", "#..##", "#..##", "#...#"),
    "O": (".###.", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "P": ("####.", "#...#", "#...#", "####.", "#....", "#....", "#...."),
    "Q": (".###.", "#...#", "#...#", "#...#", "#.#.#", "#..#.", ".##.#"),
    "R": ("####.", "#...#", "#...#", "####.", "#.#..", "#..#.", "#...#"),
    "S": (".####", "#....", "#....", ".###.", "....#", "....#", "####."),
    "T": ("#####", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "U": ("#...#", "#...#", "#...#", "#...#", "#...#", "#...#", ".###."),
    "V": ("#...#", "#...#", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "W": ("#...#", "#...#", "#...#", "#.#.#", "#.#.#", "##.##", "#...#"),
    "X": ("#...#", "#...#", ".#.#.", "..#..", ".#.#.", "#...#", "#...#"),
    "Y": ("#...#", "#...#", ".#.#.", "..#..", "..#..", "..#..", "..#.."),
    "Z": ("#####", "....#", "...#.", "..#..", ".#...", "#....", "#####"),
    "a": (".....", ".....", ".###.", "....#", ".####", "#...#", ".###."),
    "b": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "####."),
    "c": (".....", ".....", ".####", "#....", "#....", "#....", ".####"),
    "d": ("....#", "....#", ".####", "#...#", "#...#", "#...#", ".####"),
    "e": (".....", ".....", ".###.", "#...#", "#####", "#....", ".###."),
    "f": ("..##.", ".#..#", ".#...", "####.", ".#...", ".#...", ".#..."),
    "g": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "h": ("#....", "#....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "i": (".....", "..#..", ".....", ".##..", "..#..", "..#..", ".###."),
    "j": (".....", "...#.", ".....", "..##.", "...#.", "...#.", ".##.."),
    "k": ("#....", "#....", "#.#..", "#.#..", "##...", "#.#..", "#..#."),
    "l": (".##..", "..#..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "m": (".....", ".....", "##.#.", "#.#.#", "#.#.#", "#.#.#", "#.#.#"),
    "n": (".....", ".....", "####.", "#...#", "#...#", "#...#", "#...#"),
    "o": (".....", ".....", ".###.", "#...#", "#...#", "#...#", ".###."),
    "p": (".....", ".....", "####.", "#...#", "#...#", "####.", "#...."),
    "q": (".....", ".....", ".####", "#...#", "#...#", ".####", "....#"),
    "r": (".....", ".....", "#.##.", "##..#", "#....", "#....", "#...."),
    "s": (".....", ".....", ".####", "#....", ".###.", "....#", "####."),
    "t": (".#...", ".#...", "####.", ".#...", ".#...", ".#...", "..##."),
    "u": (".....", ".....", "#...#", "#...#", "#...#", "#...#", ".###."),
    "v": (".....", ".....", "#...#", "#...#", "#...#", ".#.#.", "..#.."),
    "w": (".....", ".....", "#...#", "#...#", "#.#.#", "#.#.#", ".#.#."),
    "x": (".....", ".....", "#...#", ".#.#.", "..#..", ".#.#.", "#...#"),
    "y": (".....", ".....", "#...#", "#...#", "#...#", ".####", "....#"),
    "z": (".....", ".....", "#####", "...#.", "..#..", ".#...", "#####"),
    "0": (".###.", "#...#", "#..##", "#.#.#", "##..#", "#...#", ".###."),
    "1": ("..#..", ".##..", "..#..", "..#..", "..#..", "..#..", ".###."),
    "2": (".###.", "#...#", "....#", "...#.", "..#..", ".#...", "#####"),
    "3": ("####.", "....#", "....#", ".###.", "....#", "....#", "####."),
    "4": ("...#.", "..##.", ".#.#.", "#..#.", "#####", "...#.", "...#."),
    "5": ("#####", "#....", "####.", "....#", "....#", "#...#", ".###."),
    "6": (".###.", "#....", "#....", "####.", "#...#", "#...#", ".###."),
    "7": ("#####", "....#", "...#.", "...#.", "..#..", "..#..", "..#.."),
    "8": (".###.", "#...#", "#...#", ".###.", "#...#", "#...#", ".###."),
    "9": (".###.", "#...#", "#...#", ".####", "....#", "....#", ".###."),
}

# ---------------------------------------------------------------- punctuation
FONT.update({
    " ": (".....", ".....", ".....", ".....", ".....", ".....", "....."),
    ".": (".....", ".....", ".....", ".....", ".....", ".##..", ".##.."),
    ",": (".....", ".....", ".....", ".....", ".##..", ".##..", ".#..."),
    ";": (".....", ".....", ".##..", ".....", ".##..", ".##..", ".#..."),
    ":": (".....", ".....", ".##..", ".....", ".##..", ".....", ".##.."),
    "!": ("..#..", "..#..", "..#..", "..#..", "..#..", ".....", "..#.."),
    "?": (".###.", "#...#", "....#", "...#.", "..#..", ".....", "..#.."),
    "'": ("..#..", "..#..", ".#...", ".....", ".....", ".....", "....."),
    '"': (".#.#.", ".#.#.", ".....", ".....", ".....", ".....", "....."),
    "(": ("...#.", "..#..", ".#...", ".#...", ".#...", "..#..", "...#."),
    ")": (".#...", "..#..", "...#.", "...#.", "...#.", "..#..", ".#..."),
    "-": (".....", ".....", ".....", ".###.", ".....", ".....", "....."),
    "/": ("....#", "....#", "...#.", "..#..", ".#...", "#....", "#...."),
    "%": ("#...#", "#..#.", "..#..", ".#...", "#..#.", "#...#", "....."),
    "+": (".....", "..#..", "..#..", "#####", "..#..", "..#..", "....."),
    "=": (".....", ".....", "#####", ".....", "#####", ".....", "....."),
    "$": ("..#..", ".####", "#.#..", ".###.", "..#.#", "####.", "..#.."),
    "&": (".##..", "#..#.", "#..#.", ".#...", "#.#.#", "#..#.", ".##.#"),
    "*": (".....", ".#.#.", "..#..", "#####", "..#..", ".#.#.", "....."),
    "#": (".#.#.", ".#.#.", "#####", ".#.#.", "#####", ".#.#.", ".#.#."),
    "@": (".###.", "#...#", "#.###", "#.#.#", "#.##.", "#....", ".###."),
    "_": (".....", ".....", ".....", ".....", ".....", ".....", "#####"),
    "[": (".###.", ".#...", ".#...", ".#...", ".#...", ".#...", ".###."),
    "]": (".###.", "...#.", "...#.", "...#.", "...#.", "...#.", ".###."),
    "<": ("...#.", "..#..", ".#...", "#....", ".#...", "..#..", "...#."),
    ">": (".#...", "..#..", "...#.", "....#", "...#.", "..#..", ".#..."),
    "|": ("..#..", "..#..", "..#..", "..#..", "..#..", "..#..", "..#.."),
    "\\": ("#....", "#....", ".#...", "..#..", "...#.", "....#", "....#"),
})
UNKNOWN = FONT["?"]


def text_w(s, scale=1):
    return len(s) * 6 * scale


def draw_text(d, x, y, s, scale=1, color=INK):
    """Draw ASCII string with the 5x7 bitmap font. Returns width used."""
    cx = x
    for ch in s:
        g = FONT.get(ch, UNKNOWN)
        for r in range(7):
            row = g[r]
            for c in range(5):
                if row[c] == "#":
                    d.rectangle(
                        [cx + c * scale, y + r * scale,
                         cx + (c + 1) * scale - 1, y + (r + 1) * scale - 1],
                        fill=color,
                    )
        cx += 6 * scale
    return cx - x


def draw_centered(d, cx, y, s, scale=1, color=INK):
    draw_text(d, cx - text_w(s, scale) // 2, y, s, scale, color)


def wrap(text, max_chars):
    """Greedy word wrap: breaks only at spaces, never inside a word."""
    lines, cur = [], ""
    for word in text.split(" "):
        if len(word) > max_chars:
            raise ValueError("word too long for column: %r" % word)
        if cur and len(cur) + 1 + len(word) > max_chars:
            lines.append(cur)
            cur = word
        else:
            cur = cur + " " + word if cur else word
    if cur:
        lines.append(cur)
    return lines


def bar(d, x, y, w, h, text, fg=(250, 247, 238), bg=INK, scale=1):
    """Inverted headline bar: solid block with light text."""
    d.rectangle([x, y, x + w - 1, y + h - 1], fill=bg)
    draw_text(d, x + 4, y + (h - 7 * scale) // 2, text, scale, fg)

# ------------------------------------------------------------------- the news
# All 60 stories are Monday-pure per NEWS_23NOV.md (3 leads + 12 medium
# + 45 Also Today). No story, figure or event outside that research.
LEADS = [
    {
        "kicker": "LEAD 1 | CLIMATE", "place": "ANTALYA",
        "head": ["COP31", "COLLAPSES"],
        "body": "190+ nations failed to agree a pact with no mention of "
                "fossil fuels. Guterres voiced 'deep disappointment'. "
                "Australia's opposition wants Chris Bowen out after "
                "A$150m spent. Next: Addis Ababa 2027.",
        "caption": "ANTALYA: NO FOSSIL FUELS IN THE TEXT",
    },
    {
        "kicker": "LEAD 2 | UKRAINE", "place": "KYIV REGION",
        "head": ["KYIV MOURNS", "14 DEAD"],
        "body": "Rescuers pulled a 7-year-old boy and a 79-year-old woman "
                "alive from a five-storey block in Dymer, where the toll "
                "rose to 11. Two more died in Vyshneve, one in Bila "
                "Tserkva. 23 Nov was a day of mourning.",
        "caption": "DYMER: 11 DEAD IN THE BLOCK",
    },
    {
        "kicker": "LEAD 3 | LIBYA", "place": "BENGHAZI",
        "head": ["MERKURY SINKS", "AT BENGHAZI"],
        "body": "The corvette Merkury partly sank and burned in Benghazi "
                "port after a suspected drone strike. Ten crew were hurt. "
                "The UN mission in Libya demanded an 'immediate, "
                "independent' probe.",
        "caption": "BENGHAZI: MERKURY BURNS",
    },
]

MEDIUMS = [
    ("NATO EMERGENCY SESSION ON POLAND MISSILES",
     "The North Atlantic Council met in Brussels over three Russian Kh-101 "
     "missiles that fell in Poland on 20 Nov. Poland sought more air "
     "defence but will not invoke Article 4. No formal communique had "
     "been issued; SACEUR approved forward AWACS deployment."),
    ("BAHRAIN URGES UN ACTION OVER IRAN STRIKE",
     "Bahrain urged the UN Security Council to act and Iran to pay full "
     "compensation for a 21 Nov strike on Sitra island that hurt two "
     "people. Saudi Arabia and the UAE condemned it. Al Jazeera said at "
     "least 25 merchant ships have been hit near Hormuz in seven days."),
    ("UKRAINE DRONES HIT RUSSIAN OIL SITES",
     "Ukraine's long-range drones hit the Kaleykino oil pumping station "
     "in Tatarstan, about 1,500 km from the front, and the "
     "Novoshakhtinsk refinery in Rostov, which caught fire. Russia "
     "claimed it intercepted 170 Ukrainian drones overnight."),
    ("REUTERS: SAUDI SHADOW OVER FAILED COP31",
     "Negotiators told Reuters Saudi officials had routine access to the "
     "Turkish presidency while other meetings were repeatedly cancelled. "
     "Riyadh led resistance to fossil-fuel language. Ireland's Darragh "
     "O'Brien: 'This COP has been hijacked by oil states.'"),
    ("CIKANDE CANDY FACTORY FIRE: 24 DEAD",
     "Indonesia confirmed 24 dead in the fire at the Fonusa Agung Mulia "
     "factory in Cikande, Banten, on 21 Nov; about 30 are still missing "
     "and 29 survived. DNA identification could take weeks."),
    ("NVIDIA BRINGS BACK JENSEN HUANG AS CEO",
     "Nvidia's board unanimously restored Jensen Huang as CEO, president "
     "and director, 11 days after he resigned on 12 Nov amid reports of "
     "an affair. Shares jumped about 30% on Monday. Board, SEC and "
     "Congress inquiries continue; Huang testifies on 1 Dec."),
    ("OIL SLIPS AS AI SELL-OFF SPREADS",
     "Oil fell in Asian trade on Monday as a global equities sell-off "
     "driven by AI worries spread to commodities, though Gulf shipping "
     "attacks limited losses. Brent fell 28 cents to $92.29 a barrel in "
     "early trade."),
    ("'EL CHAPO ISIDRO' ARREST RISKS CARTEL WAR",
     "The arrest of Fausto Isidro Meza Flores, head of the Beltran Leyva "
     "cartel, in Guasave on 21 Nov threatens a bloody succession fight, "
     "the WSJ wrote. The FBI fugitive, with a $5m reward, was caught "
     "with US help."),
    ("ASIAN MARKETS OPEN LOWER; KOSPI SINKS 4%",
     "Asian markets opened lower on Monday as the tech and AI sell-off "
     "continued: South Korea's tech-heavy market fell 4%, while China, "
     "Hong Kong and Australia also dropped, following a brutal Friday on "
     "Wall Street."),
    ("TAJIKISTAN FORMALLY LEAVES THE ICC",
     "The EU regretted Tajikistan's formal withdrawal from the ICC's "
     "Rome Statute, notified on 22 Nov. It takes effect on 20 Nov 2027, "
     "one year after notice, under Article 127."),
    ("IRAN STILL OPEN TO DEAL TO END US WAR",
     "Foreign Minister Abbas Araghchi said Iran remains open to a deal "
     "to end the war with the United States, begun by US and Israeli air "
     "strikes on Iran on 28 Feb 2026. A Qatari delegation visited "
     "Tehran on Friday."),
    ("HOUTHIS TARGET SAUDI; DEFENCES INTERCEPT",
     "The Saudi-led coalition said its air defences stopped a Houthi "
     "drone heading for Riyadh and, on Saturday night, a ballistic "
     "missile aimed at western Saudi Arabia, in a weekend series."),
]

# Also Today, items 16-60 in research order. Headline in caps, then text.
ALSO = [
    "ODESA SCHOOLS GO REMOTE 23-27 NOV as strikes wrecked the grid, "
    "cutting power, heating, water.",
    "DRONE STRIKE WOUNDS 2 IN KHARKIV on Monday morning in the "
    "Shevchenkivskyi district, at 05:14 UTC.",
    "MALTA-FLAGGED SHIP HIT off Benghazi by an explosive drone boat on "
    "Sunday night; all crew evacuated.",
    "SPARTA II TOWED OUT of Finnish waters on Sunday night; 16 crew "
    "evacuated, one slightly hurt.",
    "SWEDISH GRIPEN PILOT HELD FIRE over Poland as bad weather blocked "
    "a positive ID on the missiles.",
    "TWO TANKERS HIT NEAR HORMUZ on Saturday, one in the engine room; "
    "Iran reported a ship ablaze on a mine.",
    "IRGC CLAIMS DOWNING OF US MQ-9 drone over Qeshm island in the "
    "Strait of Hormuz, Iranian media reported.",
    "SAUDI ARABIA CONDEMNS IRAN attack on 'brotherly' Bahrain; Bahrain "
    "hosts the US Navy's Fifth Fleet HQ.",
    "LEBANON ARMY SEIZES 264 KG OF EXPLOSIVES and arrests three people, "
    "Arab News reported on Monday.",
    "MBS MEETS BULGARIAN PM RUMEN RADEV in Riyadh, Arab News reported "
    "on Monday.",
    "PAKISTAN MINISTER HOPES FOR US-IRAN DEAL, Arab News reported on "
    "Monday.",
    "NEPAL PM BALEN SHAH MEETS MODI in India on Monday and opens a new "
    "Nepal-India rail service.",
    "INDIA-NZ TEST DRAWN at Wellington; NZ 368 and 239/5 held India's "
    "720/9, Nicholls 175* Player of the Match.",
    "MANIBELA STRIKE HITS PHILIPPINES for two days from Monday; the "
    "government offers free rides in Manila.",
    "VISAYAS GRID ON RED AND YELLOW ALERT on Monday, GMA News "
    "reported.",
    "THREE WEATHER SYSTEMS BRING RAIN to Luzon and Mindanao on Monday, "
    "GMA News reported.",
    "49ERS ROUT VIKINGS 35-10 IN MEXICO CITY at the Azteca in the NFL's "
    "return after four years away.",
    "LIONS AND BEARS BOTH 8-2 before Thanksgiving: Detroit beat Tampa "
    "Bay 31-21; Chicago beat New Orleans 21-13.",
    "BILLS 26-9 DOLPHINS; COWBOYS 51-30 TITANS - Bills won six straight; "
    "Prescott threw 4 TDs and ran for one.",
    "CHIEFS 34-7 CARDINALS; PANTHERS 35-33 RAVENS; EAGLES 19-16 "
    "STEELERS - Mahomes 3 TDs; Eagles end skid.",
    "GIANTS HOLD OFF JAGUARS 23-18 with a red-zone stand; JJ McCarthy "
    "threw for 173 yards and a TD.",
    "CHICAGO FED INDEX FALLS TO -0.06 in October, down from +0.05 in "
    "September; the 3-month average fell to -0.05.",
    "AP TOP 25: GEORGIA, UTAH, NOTRE DAME STAY 1-2-3; Big Ten shut out "
    "of the top five, a first since 2021.",
    "HEAT WIN SEVENTH STRAIGHT OVER THUNDER; Bam Adebayo posts a "
    "triple-double as both sides miss their stars.",
    "SABRES BEAT LIGHTNING 6-2 as Tage Thompson scores twice on Sunday "
    "night.",
    "REAL MADRID BEAT CELTA VIGO 2-1 at the Bernabeu, weekend reports "
    "summarised on Monday said.",
    "ALCARAZ REACHES ATP FINALS TITLE MATCH, Monday's sports pages "
    "reported.",
    "KANSAS CITY WIN NWSL; MESSI'S MIAMI LOSE in the MLS playoffs, "
    "Monday's sports pages reported.",
    "RIEMANN CLAIM: LEAN CERTIFIES the 17m-line proof code; Maynard "
    "gives 98-99% survival odds. No audit yet.",
    "ROBOT SUB FINDS VOLCANIC ACTIVITY in the Mariana Trench, never "
    "seen before.",
    "DNA OF JONATHAN, 194, offers clues to why the giant tortoise ages "
    "so slowly.",
    "MILKY WAY SIMULATION HITS RECORD RESOLUTION using three "
    "supercomputers, with Tokyo researchers involved.",
    "GOOGLE SIGNS GEOTHERMAL POWER DEAL for 50 MW in Oregon as AI "
    "data-centre demand grows.",
    "ZIPLINE HIRES UBER EXEC ANTHONY LE ROUX to lead Africa operations "
    "ahead of expansion.",
    "ENGINEERED BACTERIA TURN PLANT SUGAR INTO LIPIDS, Chinese Academy "
    "of Sciences researchers reported.",
    "PRIME EDITING NEARS PROGRAMMABLE GENOME REWRITING, installing "
    "edits without cutting both DNA strands.",
    "MRI REVEALS PEAT MOSS GROWING TIPS to aid peatland restoration, "
    "researchers reported.",
    "BANGLADESH PLANS 25,000 NEW SME ENTREPRENEURS and 2.5m jobs by "
    "2031.",
    "GOLD RISES 2.52% TO $3,604.10 in Monday's morning briefing as "
    "investors moved to safety.",
    "CHARGERS QB JUSTIN HERBERT ENTERS CONCUSSION PROTOCOL after a "
    "27-24 loss to the Jets.",
    "BRONCOS BEAT RAIDERS 38-24, honouring Tom Jackson, Broncos great "
    "and ESPN analyst who died aged 75.",
    "ISRAELI STRIKE IN GAZA KILLS AT LEAST 3, including UNRWA worker "
    "Adel Al-Helo in Jabalia; three more hurt.",
    "UN AND US CONDEMN RSF DRONE STRIKE ON KHARTOUM, 4 dead and a UN "
    "building damaged; Sudan blamed Ethiopia.",
    "ISRAELI LEADERS CONDEMN SETTLER ARSON in the West Bank; Gadi "
    "Eisenkot called it 'Jewish terrorism'.",
    "GERMAN FACTORY PMI RISES TO 55.0 in November, from 53.4; Novartis "
    "reported positive Leqvio results.",
]

MARKET_L1 = ("MARKETS  |  S&P 500 7,237.17 +4.73%  |  NASDAQ 24,089.56 "
             "+6.51%  |  DOW 49,595.31 +3.01%  |  NVIDIA +31.48% TO $165.05")
MARKET_L2 = ("STOXX 600 637.84 +1.9%  |  KOSPI 4,708.54 -3.31%  |  GOLD "
             "$3,671.80 (SNAPSHOT 15:20 UTC)  |  BRENT $89.10 (SNAPSHOT)")
FINAL_L1 = ("LATE FINAL - MNF: COMMANDERS 22-20 BENGALS. MCPHERSON 56-YD "
            "FG, 0:46 LEFT; DANIELS DROVE 64 YDS, ROOKIE DREW STEVENS "
            "26-YD FG AS TIME EXPIRED.")
FINAL_L2 = ("EUROPE: BRENTFORD 4-0 EVERTON  |  LEVANTE 1-1 ELCHE  |  "
            "MONZA 3-0 FIORENTINA  |  NATO COMMUNIQUE STILL NOT ISSUED.")
SOURCES = ("SOURCES: REUTERS, AP, CNN, BBC, AL JAZEERA, AFP, WSJ, FT, "
           "GUARDIAN, SKY SPORTS, ANTARA, GMA NEWS, ESPN, NATO.INT, "
           "BENGALS.COM - MONDAY 23 NOVEMBER 2026")

# ------------------------------------------------------------------ masthead
def draw_masthead(d):
    d.rectangle([12, 8, 1011, 10], fill=INK)
    title = "THE WORLD IN ONE PAGE"
    draw_text(d, (W - text_w(title, 4)) // 2, 12, title, 4, INK)
    d.rectangle([260, 44, 763, 45], fill=RED)
    draw_centered(d, W // 2, 48, "MONDAY 23 NOVEMBER 2026", 2, INK)
    draw_centered(d, W // 2, 66,
                  "60 STORIES FROM ONE MONDAY | ANTALYA | KYIV | BENGHAZI",
                  1, INK)
    d.rectangle([12, 78, 1011, 79], fill=INK)


# ------------------------------------------------------- lead illustrations
def caption_strip(d, x0, text):
    d.rectangle([x0 + 1, 166, x0 + 322, 174], fill=INK)
    draw_centered(d, x0 + 162, 167, text, 1, (250, 247, 238))


def draw_lead1(d, x0):
    # COP31, Antalya: summit hall on the coast, pact crossed out.
    d.rectangle([x0 + 1, 101, x0 + 322, 132], fill=(183, 214, 232))
    d.ellipse([x0 + 272, 108, x0 + 296, 132], fill=(242, 201, 76),
              outline=(220, 170, 40))
    d.polygon([(x0 + 1, 132), (x0 + 60, 110), (x0 + 120, 132)],
              fill=(122, 142, 162))
    d.polygon([(x0 + 80, 132), (x0 + 160, 106), (x0 + 240, 132)],
              fill=(100, 124, 150))
    d.rectangle([x0 + 1, 132, x0 + 322, 140], fill=(232, 214, 170))
    d.rectangle([x0 + 118, 112, x0 + 206, 132], fill=(255, 255, 255),
                outline=INK)
    d.ellipse([x0 + 148, 102, x0 + 176, 116], fill=(255, 255, 255),
              outline=INK)
    for cx in (x0 + 130, x0 + 146, x0 + 178, x0 + 194):
        d.line([cx, 118, cx, 132], fill=INK)
    d.rectangle([x0 + 158, 124, x0 + 166, 132], fill=INK)
    d.line([x0 + 112, 102, x0 + 112, 118], fill=INK)
    d.rectangle([x0 + 112, 102, x0 + 120, 108], fill=(30, 60, 150))
    d.line([x0 + 212, 102, x0 + 212, 118], fill=INK)
    d.rectangle([x0 + 204, 102, x0 + 212, 108], fill=RED)
    d.rectangle([x0 + 232, 114, x0 + 264, 130], fill=(255, 255, 255),
                outline=INK)
    d.line([x0 + 233, 115, x0 + 263, 129], fill=RED, width=2)
    d.line([x0 + 263, 115, x0 + 233, 129], fill=RED, width=2)
    d.rectangle([x0 + 1, 140, x0 + 322, 165], fill=(64, 130, 178))
    for wy in (146, 152, 158, 163):
        for wx in range(x0 + 8, x0 + 312, 28):
            d.line([wx, wy, wx + 14, wy], fill=(255, 255, 255))
    caption_strip(d, x0, LEADS[0]["caption"])


def draw_lead2(d, x0):
    # Dymer: ruined block at dawn, crane and floodlights over rubble.
    d.rectangle([x0 + 1, 101, x0 + 322, 150], fill=(52, 58, 74))
    for sx, sy in ((x0 + 20, 108), (x0 + 45, 118), (x0 + 300, 110),
                   (x0 + 270, 122), (x0 + 250, 106), (x0 + 130, 106)):
        d.rectangle([sx, sy, sx + 1, sy + 1], fill=(255, 255, 255))
    d.rectangle([x0 + 1, 140, x0 + 322, 150], fill=(214, 130, 70))
    d.polygon([(x0 + 24, 165), (x0 + 70, 108), (x0 + 96, 108),
               (x0 + 60, 165)], fill=(238, 220, 140))
    d.polygon([(x0 + 90, 165), (x0 + 90, 112), (x0 + 150, 112),
               (x0 + 164, 120), (x0 + 178, 116), (x0 + 192, 126),
               (x0 + 210, 122), (x0 + 210, 165)], fill=(150, 148, 142),
              outline=INK)
    lit = {(x0 + 116, 130), (x0 + 152, 142), (x0 + 98, 154)}
    for wy in (118, 130, 142, 154):
        for wx in (x0 + 98, x0 + 116, x0 + 134, x0 + 152, x0 + 170,
                   x0 + 188):
            if wx >= x0 + 170 and wy == 118:
                continue
            col = (240, 200, 90) if (wx, wy) in lit else (40, 40, 40)
            d.rectangle([wx, wy, wx + 9, wy + 7], fill=col)
    d.polygon([(x0 + 196, 165), (x0 + 214, 150), (x0 + 232, 165)],
              fill=(110, 105, 95))
    d.polygon([(x0 + 222, 165), (x0 + 238, 154), (x0 + 254, 165)],
              fill=(95, 90, 82))
    d.line([x0 + 292, 104, x0 + 292, 150], fill=(230, 180, 40), width=2)
    d.line([x0 + 292, 106, x0 + 238, 106], fill=(230, 180, 40), width=2)
    d.line([x0 + 250, 106, x0 + 250, 128], fill=(230, 180, 40))
    d.rectangle([x0 + 247, 128, x0 + 253, 134], outline=(230, 180, 40))
    d.rectangle([x0 + 246, 134, x0 + 254, 140], fill=(120, 120, 120))
    caption_strip(d, x0, LEADS[1]["caption"])


def draw_lead3(d, x0):
    # Benghazi: the corvette Merkury listing and burning in port.
    d.rectangle([x0 + 1, 101, x0 + 322, 130], fill=(190, 205, 215))
    d.line([x0 + 40, 108, x0 + 40, 130], fill=(70, 80, 90), width=2)
    d.line([x0 + 40, 110, x0 + 80, 110], fill=(70, 80, 90), width=2)
    d.line([x0 + 40, 110, x0 + 70, 130], fill=(70, 80, 90))
    d.line([x0 + 280, 106, x0 + 280, 130], fill=(70, 80, 90), width=2)
    d.line([x0 + 250, 108, x0 + 280, 108], fill=(70, 80, 90), width=2)
    d.line([x0 + 280, 108, x0 + 258, 130], fill=(70, 80, 90))
    d.ellipse([x0 + 148, 106, x0 + 170, 120], fill=(120, 120, 120))
    d.ellipse([x0 + 162, 100, x0 + 182, 114], fill=(120, 120, 120))
    d.ellipse([x0 + 178, 108, x0 + 194, 120], fill=(120, 120, 120))
    d.rectangle([x0 + 1, 130, x0 + 322, 165], fill=(52, 110, 160))
    for wy in (158, 163):
        for wx in range(x0 + 8, x0 + 312, 28):
            d.line([wx, wy, wx + 14, wy], fill=(255, 255, 255))
    d.polygon([(x0 + 108, 138), (x0 + 232, 144), (x0 + 226, 158),
               (x0 + 114, 152)], fill=(60, 64, 70), outline=INK)
    d.rectangle([x0 + 140, 128, x0 + 180, 140], fill=(92, 97, 102),
                outline=INK)
    d.line([x0 + 160, 128, x0 + 160, 116], fill=INK)
    d.rectangle([x0 + 160, 116, x0 + 168, 121], fill=RED)
    d.polygon([(x0 + 186, 140), (x0 + 192, 128), (x0 + 198, 140)],
              fill=(230, 120, 30))
    d.polygon([(x0 + 189, 140), (x0 + 192, 132), (x0 + 196, 140)],
              fill=(240, 190, 60))
    d.polygon([(x0 + 208, 142), (x0 + 212, 134), (x0 + 216, 142)],
              fill=(230, 120, 30))
    d.rectangle([x0 + 284, 108, x0 + 296, 112], fill=INK)
    d.line([x0 + 280, 106, x0 + 300, 106], fill=INK)
    d.line([x0 + 282, 114, x0 + 298, 114], fill=INK)
    caption_strip(d, x0, LEADS[2]["caption"])


LEAD_DRAW = [draw_lead1, draw_lead2, draw_lead3]


def draw_leads(d):
    for i, lead in enumerate(LEADS):
        x0 = [12, 350, 688][i]
        bar(d, x0, 86, 324, 11, lead["kicker"])
        draw_text(d, x0 + 320 - text_w(lead["place"], 1), 87,
                  lead["place"], 1, (250, 247, 238))
        d.rectangle([x0, 100, x0 + 323, 175], outline=INK)
        LEAD_DRAW[i](d, x0)
        y = 182
        for line in lead["head"]:
            draw_text(d, x0, y, line, 2, INK)
            y += 15
        lines = wrap(lead["body"], 54)
        assert len(lines) <= 4, "lead %d body wraps to %d lines" % (
            i + 1, len(lines))
        for j, line in enumerate(lines):
            draw_text(d, x0, 214 + j * 9, line, 1, INK)


# ------------------------------------------------------------------- the map
CONTINENTS = [
    [(-168, 66), (-140, 70), (-120, 72), (-95, 72), (-85, 70), (-75, 62),
     (-55, 52), (-60, 45), (-75, 35), (-80, 25), (-90, 20), (-105, 20),
     (-115, 30), (-125, 40), (-150, 60), (-168, 66)],
    [(-80, 10), (-60, 5), (-35, -5), (-40, -20), (-55, -35), (-70, -55),
     (-75, -40), (-80, -20), (-80, 10)],
    [(-10, 36), (0, 44), (10, 45), (20, 40), (28, 36), (30, 42),
     (25, 50), (15, 55), (10, 58), (5, 60), (-5, 58), (-10, 50),
     (-10, 36)],
    [(-17, 15), (-10, 35), (10, 37), (30, 32), (35, 28), (43, 12),
     (51, 10), (40, -5), (35, -20), (20, -35), (12, -18), (8, 4),
     (-8, 5), (-17, 15)],
    [(30, 42), (40, 45), (50, 50), (60, 55), (70, 70), (90, 75),
     (110, 75), (130, 72), (160, 66), (178, 65), (160, 60), (140, 40),
     (130, 35), (120, 25), (105, 10), (100, 8), (90, 15), (80, 8),
     (75, 20), (65, 25), (55, 25), (45, 30), (35, 36), (30, 42)],
    [(113, -22), (114, -30), (130, -32), (140, -38), (150, -37),
     (153, -27), (146, -19), (142, -11), (135, -12), (126, -14),
     (113, -22)],
    [(130, 31), (137, 34), (140, 38), (141, 42), (144, 44), (140, 40),
     (138, 36), (132, 33), (130, 31)],
    [(167, -45), (174, -41), (178, -38), (175, -36), (172, -41),
     (167, -45)],
    [(44, -16), (47, -15), (50, -16), (49, -20), (45, -25), (43, -21),
     (44, -16)],
]
# name, lat, lon, label dx, label dy (label offset from the pin)
PINS = [
    ("BRUSSELS", 50.85, 4.35, -52, -12),
    ("KYIV", 50.45, 30.52, -38, -12),
    ("ANTALYA", 36.9, 30.7, 6, 2),
    ("BENGHAZI", 32.1, 20.07, -54, 8),
    ("GAZA", 31.5, 34.5, 6, 8),
    ("KHARTOUM", 15.6, 32.5, 6, 12),
    ("BAHRAIN", 26.2, 50.6, 6, -12),
    ("RIYADH", 24.6, 46.7, -6, 8),
    ("KALEYKINO", 55.0, 52.0, 6, -12),
    ("CIKANDE", -6.2, 106.3, 6, -4),
    ("MANILA", 14.6, 121.0, 6, -4),
    ("WELLINGTON", -41.3, 174.8, -66, -4),
]


def map_xy(lon, lat):
    return (12 + (lon + 170) / 360.0 * 1000,
            394 - (lat + 58) / 142.0 * 120)


def draw_map(d):
    draw_text(d, 12, 260, "THE WORLD ON MONDAY - WHERE THE NEWS HAPPENED",
              1, INK)
    d.ellipse([918, 260, 925, 267], fill=RED, outline=(255, 255, 255))
    draw_text(d, 928, 260, "NEWS PIN", 1, INK)
    d.rectangle([12, 274, 1011, 394], fill=(176, 212, 232), outline=INK)
    for lon in range(-150, 181, 30):
        x = map_xy(lon, 0)[0]
        d.line([x, 274, x, 394], fill=(205, 210, 215))
    for lat in (-30, 0, 30, 60):
        y = map_xy(0, lat)[1]
        d.line([12, y, 1011, y], fill=(205, 210, 215))
    for poly in CONTINENTS:
        pts = [map_xy(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=(226, 216, 178), outline=(150, 138, 96))
    for name, lat, lon, dx, dy in PINS:
        px, py = map_xy(lon, lat)
        lx, ly = int(px) + dx, int(py) + dy
        d.line([px, py, lx + 2, ly + 3], fill=INK)
        d.ellipse([px - 4, py - 4, px + 4, py + 4],
                  fill=(255, 255, 255))
        d.ellipse([px - 3, py - 3, px + 3, py + 3], fill=RED)
        w = text_w(name, 1)
        d.rectangle([lx - 1, ly - 1, lx + w + 1, ly + 8],
                    fill=(255, 255, 255))
        draw_text(d, lx, ly, name, 1, INK)


# --------------------------------------------------------------------- body
def draw_body(d):
    bar(d, 12, 454, 1000, 12, "THE WORLD IN BRIEF - 12 TOP STORIES, 45 MORE")
    draw_text(d, 1012 - 4 - text_w("60 STORIES", 1), 456, "60 STORIES", 1,
              (250, 247, 238))
    cols = [12, 348, 684]
    cw = 326
    y_top, y_bot = 470, 1012
    max_chars = cw // 6
    items = []
    for head, body in MEDIUMS:
        assert len(head) <= max_chars, "medium headline too long: %r" % head
        items.append(("med", head, wrap(body, max_chars)))
    items.append(("sec", "ALSO TODAY", []))
    for text in ALSO:
        items.append(("also", None, wrap(text, max_chars)))
    col, y = 0, y_top
    used = [0, 0, 0]
    counts = {"med": 0, "also": 0}
    for kind, head, lines in items:
        if kind == "med":
            h = 9 + 1 + 9 * len(lines) + 3
        elif kind == "sec":
            h = 11 + 2
        else:
            h = 9 * len(lines) + 2
        if y + h > y_bot + 1:
            used[col] = y - y_top
            col += 1
            y = y_top
            if col > 2:
                raise SystemExit("BODY OVERFLOW: out of columns at %r"
                                 % (head or lines,))
        x = cols[col]
        if kind == "med":
            bar(d, x, y, cw, 9, head)
            for j, line in enumerate(lines):
                draw_text(d, x, y + 10 + j * 9, line, 1, INK)
            counts["med"] += 1
        elif kind == "sec":
            bar(d, x, y, cw, 11, "ALSO TODAY", bg=RED)
            draw_text(d, x + cw - 4 - text_w("45 STORIES", 1), y + 2,
                      "45 STORIES", 1, (250, 247, 238))
        else:
            for j, line in enumerate(lines):
                draw_text(d, x, y + j * 9, line, 1, INK)
            counts["also"] += 1
        y += h
    used[col] = y - y_top
    assert counts["med"] == 12 and counts["also"] == 45, counts
    print("body columns used px: %s (capacity %d each)" % (used, y_bot - y_top))
    print("stories placed: 3 leads + %d medium + %d also = %d"
          % (counts["med"], counts["also"],
             3 + counts["med"] + counts["also"]))


def main():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    draw_masthead(d)
    draw_leads(d)
    draw_map(d)
    d.rectangle([12, 400, 1011, 428], outline=INK)
    draw_text(d, 18, 405, MARKET_L1, 1, INK)
    draw_text(d, 18, 416, MARKET_L2, 1, INK)
    draw_text(d, 12, 434, FINAL_L1, 1, INK)
    draw_text(d, 12, 444, FINAL_L2, 1, INK)
    draw_body(d)
    draw_text(d, 12, 1015, SOURCES, 1, INK)
    img.save(OUT, format="PNG")
    data = open(OUT, "rb").read()
    print("saved %s: %d bytes, sha256 %s"
          % (OUT, len(data), hashlib.sha256(data).hexdigest()))


if __name__ == "__main__":
    main()
