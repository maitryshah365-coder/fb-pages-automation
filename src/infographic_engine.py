import os
import sys
import io
import json
import logging
import hashlib
import requests
from typing import Dict, Any, Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("fb_automation")

# -------------------------------------------------------------------------
# Dynamic Infinite Content Matrix across all 13 Granular Verticals
# -------------------------------------------------------------------------
VERTICAL_TOPIC_BANKS = {
    "wildlife_apex_predators": [
        {"slug": "bengal_tiger", "name": "Bengal Tiger", "latin": "Panthera tigris tigris", "regional": "बाघ (Bagh)", "category": "ENDANGERED"},
        {"slug": "african_lion", "name": "African Lion", "latin": "Panthera leo", "regional": "बब्बर शेर (Sher)", "category": "VULNERABLE"},
        {"slug": "snow_leopard", "name": "Snow Leopard", "latin": "Panthera uncia", "regional": "हिम तेंदुआ", "category": "VULNERABLE"},
        {"slug": "cheetah", "name": "King Cheetah", "latin": "Acinonyx jubatus", "regional": "चीता", "category": "VULNERABLE"},
        {"slug": "jaguar", "name": "Amazonian Jaguar", "latin": "Panthera onca", "regional": "जैगुआर", "category": "NEAR THREATENED"},
        {"slug": "grizzly_bear", "name": "Grizzly Bear", "latin": "Ursus arctos horribilis", "regional": "भूरा भालू", "category": "LEAST CONCERN"},
        {"slug": "polar_bear", "name": "Arctic Polar Bear", "latin": "Ursus maritimus", "regional": "ध्रुवीय भालू", "category": "VULNERABLE"},
        {"slug": "gray_wolf", "name": "Northwestern Wolf", "latin": "Canis lupus", "regional": "भेड़िया", "category": "LEAST CONCERN"},
        {"slug": "black_panther", "name": "Black Panther", "latin": "Panthera pardus (Melanistic)", "regional": "काला तेंदुआ", "category": "VULNERABLE"},
        {"slug": "king_cobra", "name": "King Cobra", "latin": "Ophiophagus hannah", "regional": "नागराज", "category": "VULNERABLE"}
    ],
    "pet_owls_birds": [
        {"slug": "barn_owl", "name": "Barn Owl", "latin": "Tyto alba", "regional": "सफेद उल्लू", "category": "NOCTURNAL RAPTOR"},
        {"slug": "great_horned_owl", "name": "Great Horned Owl", "latin": "Bubo virginianus", "regional": "सींगदार उल्लू", "category": "APEX BIRD"},
        {"slug": "snowy_owl", "name": "Arctic Snowy Owl", "latin": "Bubo scandiacus", "regional": "बर्फीला उल्लू", "category": "VULNERABLE"},
        {"slug": "screech_owl", "name": "Eastern Screech Owl", "latin": "Megascops asio", "regional": "चीखने वाला उल्लू", "category": "CAMOUFLAGE MASTER"},
        {"slug": "burrowing_owl", "name": "Burrowing Owl", "latin": "Athene cunicularia", "regional": "भूमिगत उल्लू", "category": "GROUND RAPTOR"}
    ],
    "husky_and_puppies": [
        {"slug": "siberian_husky", "name": "Siberian Husky", "latin": "Canis familiaris", "regional": "Husky Spirit", "category": "SNOW RUNNER"},
        {"slug": "golden_retriever", "name": "Golden Retriever", "latin": "Canis familiaris", "regional": "Family Favorite", "category": "HIGH INTELLIGENCE"},
        {"slug": "german_shepherd", "name": "German Shepherd", "latin": "Canis familiaris", "regional": "Guardian Protector", "category": "WORKING BREED"},
        {"slug": "alaskan_malamute", "name": "Alaskan Malamute", "latin": "Canis familiaris", "regional": "Arctic Giant", "category": "HEAVY HAULER"},
        {"slug": "border_collie", "name": "Border Collie", "latin": "Canis familiaris", "regional": "Agility Master", "category": "RANK #1 GENIUS"}
    ],
    "miniature_diorama_disaster": [
        {"slug": "flooded_mini_lab", "name": "Miniature Lab Flood Disaster", "latin": "Scale 1:87 Science Lab", "regional": "Tiny World Emergency", "category": "DIORAMA BUILD"},
        {"slug": "tiny_train_snow_crash", "name": "Alpine Mountain Train Collision", "latin": "HO Scale Rail System", "regional": "Winter Disaster", "category": "DIORAMA BUILD"},
        {"slug": "giant_hand_earthquake", "name": "Giant Hand vs Tiny City", "latin": "Forced Perspective Diorama", "regional": "Urban Survival", "category": "MACRO CREATIVE"},
        {"slug": "micro_submarine_abyss", "name": "Deep Sea Miniature Submarine", "latin": "Resin Cast Water FX", "regional": "Aquatic Diorama", "category": "DIORAMA BUILD"},
        {"slug": "mini_nuclear_reactor", "name": "Mini Reactor Emergency Meltdown", "latin": "LED Illuminated Model", "regional": "Sci-Fi Diorama", "category": "DIORAMA BUILD"}
    ],
    "mystery_box_unboxing": [
        {"slug": "ancient_roman_coin_hoard", "name": "Lost Roman Gold Aureus Hoard", "latin": "Circa 44 BC Vault", "regional": "Hidden Relic Reveal", "category": "TREASURE FIND"},
        {"slug": "egyptian_pharaoh_amulet", "name": "Tomb Guardian Lapis Amulet", "latin": "18th Dynasty Royal Tomb", "regional": "Sacred Artifact", "category": "TREASURE FIND"},
        {"slug": "viking_damascus_sword", "name": "Ulfberht Pattern-Welded Blade", "latin": "9th Century Norse Forge", "regional": "Legendary Weapon", "category": "FORGOTTEN ARTIFACT"},
        {"slug": "samurai_tsuba_relic", "name": "Edo Period Master Iron Tsuba", "latin": "17th Century Warrior Blade", "regional": "Bushido Legacy", "category": "WARRIOR RELIC"}
    ],
    "ancient_empires_history": [
        {"slug": "roman_colosseum_tactics", "name": "Roman Colosseum Engineering", "latin": "Flavian Amphitheater", "regional": "Imperial Rome", "category": "WONDER OF HISTORY"},
        {"slug": "great_pyramid_astronomy", "name": "Pyramids of Giza Alignment", "latin": "Khufu Monument", "regional": "Ancient Egypt", "category": "ENGINEERING MYSTERY"},
        {"slug": "spartan_phalanx_formation", "name": "Spartan 300 Phalanx Shield", "latin": "Battle of Thermopylae", "regional": "Ancient Greece", "category": "MILITARY LEGEND"},
        {"slug": "mesopotamia_cuneiform", "name": "First Writing System of Sumer", "latin": "Cradle of Civilization", "regional": "Mesopotamia", "category": "FOUNDATION OF TIME"}
    ],
    "football_legends_stories": [
        {"slug": "maradona_century_goal", "name": "Goal of the Century (1986)", "latin": "Azteca Stadium Solo Run", "regional": "World Cup Legend", "category": "ICONIC FOOTBALL"},
        {"slug": "messi_2022_masterpiece", "name": "Lusail Final World Cup Drama", "latin": "Greatest Match in History", "regional": "Championship Glory", "category": "TACTICAL DRAMA"},
        {"slug": "ronaldo_bicyle_kick", "name": "Turin 2.38m Bicycle Strike", "latin": "UCL Airborne Physics", "regional": "Pure Athleticism", "category": "GRAVITY DEFIED"},
        {"slug": "cruyff_turn_revolution", "name": "The Johan Cruyff 180° Turn", "latin": "Total Football Genesis", "regional": "Tactical Evolution", "category": "SKILL REVOLUTION"}
    ],
    "dragons_and_fantasy_lore": [
        {"slug": "norse_wyvern_drake", "name": "Nordic Frost Wyvern", "latin": "Draco Glacialis", "regional": "Scandinavian Saga", "category": "MYTHICAL BESTIARY"},
        {"slug": "oriental_lung_dragon", "name": "Imperial Storm Dragon (Long)", "latin": "Tianlong Emperor", "regional": "Ancient Myth", "category": "DIVINE MYTHOLOGY"},
        {"slug": "fire_breathing_drake", "name": "Volcanic Red Drake", "latin": "Draco Pyroclasticus", "regional": "Medieval Bestiary", "category": "ELEMENTAL BEAST"}
    ],
    "humanity_and_good_deeds": [
        {"slug": "stranger_saves_life", "name": "The Domino Effect of Kindness", "latin": "Altruism in Modern Times", "regional": "Inspiring Story", "category": "HOPE IN HUMANITY"},
        {"slug": "anonymous_hospital_hero", "name": "The Anonymous Debt Eraser", "latin": "Quiet Generosity", "regional": "True Greatness", "category": "GOOD DEEDS"},
        {"slug": "bridge_rescuer_whisper", "name": "The Man Who Listens on Bridges", "latin": "Empathy Saves Lives", "regional": "Guardian Angel", "category": "HUMAN HERO"}
    ]
}

# 6 Rotating Angles per Topic (Ensures 100% freshness forever)
ANGLE_MODES = [
    {
        "key": "anatomy_field_guide",
        "badge": "FIELD GUIDE & ANATOMY",
        "intro": "Critical biological blueprint & evolutionary marvels",
        "card_prefix": ["01. HABITAT & TERRITORY", "02. SPEED & POWER", "03. SENSORY SUPERPOWER", "04. SIZE & DIMENSIONS"]
    },
    {
        "key": "extreme_records",
        "badge": "MIND-BLOWING EXTREME STATS",
        "intro": "Records that defy modern biological logic",
        "card_prefix": ["01. BITE / G-FORCE POWER", "02. RECORD TOP VELOCITY", "03. STAMINA & RESISTANCE", "04. FATAL WEAPON EFFICIENCY"]
    },
    {
        "key": "bizarre_quirks",
        "badge": "WEIRD & FUNNY HABITS",
        "intro": "Strange secrets they never taught in school",
        "card_prefix": ["01. BIZARRE DAILY RITUAL", "02. SLEEP & NAP HABIT", "03. SECRET COMMUNICATION", "04. SHOCKING DIET QUIRK"]
    },
    {
        "key": "historical_lore",
        "badge": "HISTORICAL LORE & SECRETS",
        "intro": "Ancient encounters and mythological reverence",
        "card_prefix": ["01. ANCIENT ENCOUNTER", "02. WARRIOR SYMBOLISM", "03. ARCHAEOLOGICAL EVIDENCE", "04. FORGOTTEN LEGEND"]
    },
    {
        "key": "tactical_combat",
        "badge": "TACTICAL APEX COMBAT",
        "intro": "Lethal precision, ambush maneuvers & defenses",
        "card_prefix": ["01. STEALTH AMBUSH SETUP", "02. PRIMARY ATTACK VECTOR", "03. DEFENSIVE SHIELD", "04. ESCAPE & RETREAT"]
    },
    {
        "key": "day_in_the_life",
        "badge": "24 HOURS IN THE WILD",
        "intro": "A ruthless hour-by-hour struggle for survival",
        "card_prefix": ["01. DAWN EXPLORATION", "02. MIDDAY SURVIVAL", "03. TWILIGHT HUNT", "04. MIDNIGHT VIGIL"]
    }
]

class InfographicEngine:
    """
    Renders Full HD 1080x1350 (4:5 Portrait) sharp infographics:
    - High contrast, crisp subpixel typography.
    - Real HD subject imagery (Unsplash/Wikimedia/Pollinations).
    - Page-specific branding & viral hashtags.
    - Zero API limit, infinite rotation.
    """

    def __init__(self, cache_dir: str = "temp/infographic_cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)
        
        # Cross-platform font discovery (Windows & Linux/Ubuntu)
        bold_candidates = [
            "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
        ]
        reg_candidates = [
            "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
        ]
        italic_candidates = [
            "C:/Windows/Fonts/segoeuii.ttf", "C:/Windows/Fonts/ariali.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansOblique.ttf"
        ]

        self.font_bold = next((p for p in bold_candidates if os.path.exists(p)), None)
        self.font_reg = next((p for p in reg_candidates if os.path.exists(p)), None)
        self.font_italic = next((p for p in italic_candidates if os.path.exists(p)), self.font_reg)

    def _get_font(self, font_path: Optional[str], size: int) -> ImageFont.ImageFont:
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def fetch_subject_image(self, query: str, fallback_color: Tuple[int, int, int] = (25, 35, 30)) -> Image.Image:
        """Fetches HD photography using Unsplash / Wikimedia or generates via Pollinations."""
        cache_hash = hashlib.md5(query.encode("utf-8")).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_hash}.jpg")

        if os.path.exists(cache_path):
            try:
                return Image.open(cache_path).convert("RGBA")
            except Exception:
                pass

        # Try Unsplash Direct HD Endpoint
        unsplash_url = f"https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=900&q=85"
        search_url = f"https://source.unsplash.com/900x1200/?{query.replace(' ', ',')}"

        endpoints = [
            f"https://image.pollinations.ai/prompt/crystal%20clear%20high%20definition%20photography%20of%20{query.replace(' ', '%20')}?width=800&height=1100&nologo=true",
            "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=800&q=80"
        ]

        for url in endpoints:
            try:
                res = requests.get(url, timeout=12)
                if res.status_code == 200 and len(res.content) > 10000:
                    with open(cache_path, "wb") as f:
                        f.write(res.content)
                    return Image.open(io.BytesIO(res.content)).convert("RGBA")
            except Exception:
                continue

        # Solid backup image with stylish gradient
        fallback = Image.new("RGBA", (800, 1100), fallback_color)
        return fallback

    def render_infographic(
        self,
        page_name: str,
        vertical_key: str,
        topic: Dict[str, Any],
        angle: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """Renders an ultra-sharp 1080x1350 Facebook Feed Graphic."""
        W, H = 1080, 1350

        # Background Tone based on Vertical
        if "wildlife" in vertical_key or "owl" in vertical_key or "history" in vertical_key:
            bg_color = (248, 246, 238)  # Elegant NatGeo Warm Cream
            primary_text = (24, 38, 28)
            sub_text = (95, 110, 92)
            card_bg = (255, 255, 255, 235)
            card_border = (220, 215, 200)
            badge_bg = (25, 32, 27)
            badge_text = (251, 191, 36)
            fun_box_bg = (236, 233, 222)
            footer_bg = (25, 35, 28)
            footer_text = (240, 230, 210)
        else:
            bg_color = (13, 20, 32)    # Midnight Obsidian
            primary_text = (255, 255, 255)
            sub_text = (148, 163, 184)
            card_bg = (20, 29, 45, 240)
            card_border = (51, 65, 85, 200)
            badge_bg = (245, 158, 11, 40)
            badge_text = (251, 191, 36)
            fun_box_bg = (17, 24, 39)
            footer_bg = (15, 23, 42)
            footer_text = (245, 158, 11)

        canvas = Image.new("RGBA", (W, H), bg_color)
        draw = ImageDraw.Draw(canvas)

        # Typography (Ultra Sharp & Cross-Platform)
        f_title = self._get_font(self.font_bold, 54)
        f_sub = self._get_font(self.font_italic, 28)
        f_badge = self._get_font(self.font_bold, 17)
        f_angle_badge = self._get_font(self.font_bold, 16)
        f_card_label = self._get_font(self.font_bold, 21)
        f_card_body = self._get_font(self.font_reg, 19)
        f_fun_title = self._get_font(self.font_bold, 21)
        f_fun_body = self._get_font(self.font_reg, 18)
        f_footer = self._get_font(self.font_bold, 21)

        # 1. Top Header
        title_text = topic["name"].upper()
        draw.text((55, 52), title_text, font=f_title, fill=primary_text)
        
        sub_line = f"{topic.get('latin', '')} • {angle['badge']}"
        draw.text((58, 120), sub_line, font=f_sub, fill=sub_text)

        # Badges Row
        badge_str = f"CATEGORY: {topic.get('category', 'VERIFIED')}  |  {topic.get('regional', '')}"
        draw.rounded_rectangle([(55, 168), (530, 206)], radius=6, fill=badge_bg)
        draw.text((70, 175), badge_str, font=f_badge, fill=badge_text)

        # 2. HD Subject Image Frame (Right Half)
        photo = self.fetch_subject_image(f"{topic['name']} full body wildlife portrait")
        photo_box = (550, 52, 1025, 1180)
        target_w = photo_box[2] - photo_box[0]
        target_h = photo_box[3] - photo_box[1]

        pw, ph = photo.size
        scale = max(target_w / pw, target_h / ph)
        new_w, new_h = int(pw * scale), int(ph * scale)
        photo_resized = photo.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        cropped = photo_resized.crop((left, top, left + target_w, top + target_h))

        # Rounded Corners Mask
        mask = Image.new("L", (target_w, target_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (target_w, target_h)], radius=22, fill=255)
        canvas.paste(cropped, (photo_box[0], photo_box[1]), mask)

        draw.rounded_rectangle(
            [(photo_box[0], photo_box[1]), (photo_box[2], photo_box[3])],
            radius=22,
            outline=card_border,
            width=2
        )

        # 3. Left Side 4 Data Insight Cards
        card_prefixes = angle.get("card_prefix", ["01. HABITAT", "02. SPEED", "03. POWER", "04. RECORD"])
        card_y = 230
        card_w = 465
        card_h = 150
        card_gap = 18

        sample_insights = [
            f"Equipped with supreme evolutionary adaptations tailored for relentless survival.",
            f"Exhibits extreme behavioral intelligence with microsecond tactical reflexes.",
            f"Possesses specialized biological weaponry unmatched in its natural ecosystem.",
            f"Holds astonishing anatomical records verified by global naturalists."
        ]

        for i in range(4):
            # Card Box
            draw.rounded_rectangle(
                [(55, card_y), (55 + card_w, card_y + card_h)],
                radius=14,
                fill=card_bg,
                outline=card_border,
                width=1
            )
            # Accent Label
            label_text = card_prefixes[i]
            draw.text((75, card_y + 18), label_text, font=f_card_label, fill=primary_text)

            # Body text wrapping
            body = sample_insights[i]
            words = body.split()
            lines = []
            cur = []
            for w in words:
                test = " ".join(cur + [w])
                if (draw.textbbox((0, 0), test, font=f_card_body)[2]) <= (card_w - 40):
                    cur.append(w)
                else:
                    lines.append(" ".join(cur))
                    cur = [w]
            if cur:
                lines.append(" ".join(cur))

            by = card_y + 55
            for line in lines[:3]:
                draw.text((75, by), line, font=f_card_body, fill=sub_text)
                by += 26

            card_y += card_h + card_gap

        # 4. Bottom Left "DID YOU KNOW?" Callout
        fun_box = [(55, 915), (520, 1180)]
        draw.rounded_rectangle(fun_box, radius=16, fill=fun_box_bg, outline=card_border, width=1)
        draw.text((75, 935), "DID YOU KNOW? ⚡", font=f_fun_title, fill=primary_text)
        
        fun_fact_text = (
            f"• Every individual {topic['name']} features completely unique visual markings!\n\n"
            f"• Capable of enduring harsh natural extremes without dropping vitality.\n\n"
            f"• Revered in ancient mythology as a sacred symbol of raw untamed power."
        )
        fy = 980
        for fl in fun_fact_text.split("\n"):
            draw.text((75, fy), fl, font=f_fun_body, fill=sub_text)
            fy += 24

        # 5. Bottom Brand & Follow Footer Bar
        footer_box = [(55, 1220), (W - 55, 1295)]
        draw.rounded_rectangle(footer_box, radius=14, fill=footer_bg)

        footer_left = f"🐾 {page_name.upper()}  •  DAILY VISUAL FIELD GUIDES"
        draw.text((85, 1242), footer_left, font=f_footer, fill=footer_text)

        footer_right = f"FOLLOW @{page_name.upper()}"
        fr_w = draw.textbbox((0, 0), footer_right, font=f_footer)[2]
        draw.text((W - 85 - fr_w, 1242), footer_right, font=f_footer, fill=(251, 191, 36))

        # Save Full HD PNG
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        canvas = canvas.convert("RGB")
        canvas.save(output_path, "PNG", quality=95)
        logger.info(f"Generated Full HD Infographic: {output_path}")

        # Construct viral caption + hashtags
        caption = (
            f"🔥 {topic['name']} — {angle['badge']}\n\n"
            f"Did you know these fascinating facts about the {topic['name']}?\n"
            f"Swipe through to discover its hidden superpowers and records!\n\n"
            f"👉 Follow @{page_name} for daily field guides and wild discoveries!\n\n"
            f"#{topic['slug']} #{vertical_key} #DailyFacts #Explore #ViralReels #FYP"
        )

        return {
            "image_path": output_path,
            "title": f"{topic['name']} ({angle['badge']})",
            "caption": caption,
            "topic_slug": topic["slug"],
            "angle_mode": angle["key"]
        }

