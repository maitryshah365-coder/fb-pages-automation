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
# Authentic Domain-Specific Data Matrix (100% Niche Isolated)
# -------------------------------------------------------------------------
AUTHENTIC_VERTICAL_DATA = {
    "miniature_diorama_disaster": {
        "theme_name": "MINIATURE DIORAMA CRAFT & ENGINEERING",
        "badge_tag": "SCALE MODELING & MACRO CRAFT",
        "palette": {
            "bg": (15, 23, 42),          # Slate Obsidian Workbench
            "primary": (255, 255, 255),
            "sub": (148, 163, 184),
            "card_bg": (30, 41, 59, 230),
            "card_border": (51, 65, 85),
            "accent": (245, 158, 11),     # Amber Gold
            "footer_bg": (2, 6, 23)
        },
        "search_term": "detailed miniature diorama scale model crafting macro",
        "topics": [
            {
                "slug": "resin_water_flood",
                "title": "HYPER-REALISTIC WATER & FLOOD FX",
                "sub": "Scale 1:87 HO Diorama • Advanced Liquid Dynamics",
                "badge": "EPOXY RESIN WATER ENGINEERING",
                "cards": [
                    {"label": "01. MATERIAL & MIXING", "text": "2-part crystal clear epoxy resin mixed at exact 1:1 ratio to prevent cloudy curing."},
                    {"label": "02. WAVE & CURRENT TECHNIQUE", "text": "Clear silicone caulk sculpted with wet toothpick creates dynamic churning rapids."},
                    {"label": "03. DEPTH COLOR GRADING", "text": "Deep sea teal alcohol ink base layered with transparent green gives 3D depth."},
                    {"label": "04. MICRO-FOAM HIGHLIGHTS", "text": "Titanium white acrylic dry-brushed over wave crests simulates churning whitewater."}
                ],
                "fun_fact": [
                    "• Pure 99% Isopropyl alcohol spritzed over wet resin instantly pops all micro-bubbles!",
                    "• Real fine river sand sifted through coffee filters gives 100% authentic scale grit.",
                    "• Mod Podge gloss sealer preserves water reflections for years without yellowing."
                ]
            },
            {
                "slug": "realistic_rust_weathering",
                "title": "INDUSTRIAL RUST & WEATHERING SECRETS",
                "sub": "HO Scale Rolling Stock • Realistic Oxidation",
                "badge": "WEATHERING & PATINA CRAFT",
                "cards": [
                    {"label": "01. BASE OXIDATION LAYER", "text": "Real iron powder mixed with matte medium and activated with vinegar wash."},
                    {"label": "02. HAIRSPRAY CHIPPING TECHNIQUE", "text": "Chipping fluid sprayed before topcoat lets you scrub off micro-scratches."},
                    {"label": "03. OIL PAINT STREAKING", "text": "Burnt umber oil wash dragged downward with mineral spirits simulates rain rust."},
                    {"label": "04. MATTE DUST PIGMENTS", "text": "Crushed earth pastel pigments brushed into crevices simulate decades of grime."}
                ],
                "fun_fact": [
                    "• Table salt sprinkled over wet paint creates authentic blistered rust patches!",
                    "• Graphite pencil rubbed on metal edges gives genuine worn metallic friction shine.",
                    "• Ultra-matte clear coat permanently locks pigment powders without changing color tone."
                ]
            },
            {
                "slug": "micro_led_wiring_hacks",
                "title": "MICRO-LED WIRING & ILLUMINATION HACKS",
                "sub": "0402 SMD LEDs • Miniature Electrical Systems",
                "badge": "MINIATURE ELECTRONICS",
                "cards": [
                    {"label": "01. 0402 SMD MICRO LIGHTS", "text": "1.0mm x 0.5mm surface-mount LEDs fit inside miniature lamps, headlights and lanterns."},
                    {"label": "02. INVISIBLE ENAMELED WIRE", "text": "0.1mm magnet wire routed through grooves inside walls hides all wiring completely."},
                    {"label": "03. RESISTOR PROTECTION", "text": "1K ohm 1/4W resistor on the positive lead prevents fragile micro-LEDs from burning out."},
                    {"label": "04. COIN CELL POWER SUPPLY", "text": "Single CR2032 3V button battery hidden inside diorama base powers up to 8 micro-lights."}
                ],
                "fun_fact": [
                    "• Flickering candle LEDs wired into miniature fireplaces create ultra-realistic flame motion!",
                    "• Fiber optic strands (0.5mm) split a single LED light into 10 illuminated dashboard dials.",
                    "• Magnetic reed switches let you turn diorama lights on/off with a magnet outside the case!"
                ]
            }
        ]
    },
    "pet_owls_birds": {
        "theme_name": "OWLS & BIRDS OF PREY FIELD GUIDE",
        "badge_tag": "WILD RAPTOR BIOLOGY & BEHAVIOR",
        "palette": {
            "bg": (248, 246, 238),        # NatGeo Cream
            "primary": (24, 38, 28),
            "sub": (95, 110, 92),
            "card_bg": (255, 255, 255, 240),
            "card_border": (220, 215, 200),
            "accent": (217, 119, 6),      # Amber Ochre
            "footer_bg": (25, 35, 28)
        },
        "search_term": "owl bird of prey close up portrait wildlife",
        "topics": [
            {
                "slug": "barn_owl_silent_flight",
                "title": "BARN OWL: SILENT NIGHT HUNTER",
                "sub": "Tyto alba • Nocturnal Acoustic Predator",
                "badge": "RAPTOR ACOUSTICS & FLIGHT",
                "cards": [
                    {"label": "01. ZERO-DECIBEL FLIGHT", "text": "Comb-like serrated wing margins break air into micro-eddies, silencing all wing flap noise."},
                    {"label": "02. ASYMMETRICAL EARS", "text": "One ear is higher than the other, allowing 3D sonic triangulation of mice under deep snow."},
                    {"label": "03. 110-DEGREE BINOCULAR VISION", "text": "Tubular eyes locked into skull provide telescope-level depth perception in total darkness."},
                    {"label": "04. APEX HUNTING TALONS", "text": "Four curved razor talons deliver 30 lbs of crushing grip force, neutralizing prey instantly."}
                ],
                "fun_fact": [
                    "• A single family of barn owls consumes over 3,000 rodents every single year!",
                    "• Owls cannot roll their eyes! Instead, they rotate their heads up to 270 degrees.",
                    "• Their heart-shaped facial disk channels sound waves directly into their hidden ears."
                ]
            }
        ]
    },
    "wildlife_apex_predators": {
        "theme_name": "APEX PREDATOR FIELD GUIDE",
        "badge_tag": "NATIONAL GEOGRAPHIC WILDLIFE REPORT",
        "palette": {
            "bg": (248, 246, 238),        # NatGeo Cream
            "primary": (24, 38, 28),
            "sub": (95, 110, 92),
            "card_bg": (255, 255, 255, 240),
            "card_border": (220, 215, 200),
            "accent": (217, 119, 6),
            "footer_bg": (25, 35, 28)
        },
        "search_term": "wildlife apex predator high definition photography",
        "topics": [
            {
                "slug": "bengal_tiger_savanna",
                "title": "BENGAL TIGER: APEX STRIPED STRIKER",
                "sub": "Panthera tigris tigris • Solitary Jungle Hunter",
                "badge": "ENDANGERED SPECIES (IUCN)",
                "cards": [
                    {"label": "01. HUNTING SPRINT SPEED", "text": "Explosive 65 km/h sprint velocity combined with 30-foot leap capability in dense forest."},
                    {"label": "02. CRUSHING BITE FORCE", "text": "1,050 PSI bite force crushes cervical vertebrae instantly, overpowering 1,000 kg prey."},
                    {"label": "03. AQUATIC DOMINANCE", "text": "Skilled swimmer known to cross 7 km rivers effortlessly and hunt prey inside mangroves."},
                    {"label": "04. CAMOUFLAGE BIOLOGY", "text": "Prey animals see in dichromatic vision, making orange fur look identical to forest green."}
                ],
                "fun_fact": [
                    "• Tiger stripes are on their actual skin, not just their outer fur coat!",
                    "• A tiger's roar contains low-frequency infrasound that momentarily paralyzes nearby prey.",
                    "• White false 'eye spots' on the back of tiger ears deter predators from attacking behind."
                ]
            }
        ]
    },
    "humanity_and_good_deeds": {
        "theme_name": "HUMANITY, EMPATHY & KINDNESS",
        "badge_tag": "TRUE STORIES THAT RESTORE FAITH",
        "palette": {
            "bg": (255, 248, 242),        # Warm Peach / Linen
            "primary": (30, 41, 59),
            "sub": (100, 116, 139),
            "card_bg": (255, 255, 255, 245),
            "card_border": (241, 225, 210),
            "accent": (225, 29, 72),      # Rose Crimson
            "footer_bg": (15, 23, 42)
        },
        "search_term": "humanity helping hands kindness uplifting hope",
        "topics": [
            {
                "slug": "quiet_generosity_ripple",
                "title": "THE RIPPLE EFFECT OF UNSEEN KINDNESS",
                "sub": "Inspiring True Human Stories • Quiet Altruism",
                "badge": "FAITH IN HUMANITY RESTORED",
                "cards": [
                    {"label": "01. THE STRANGER AT THE COUNTER", "text": "Paying forward someone's groceries creates an immediate chain reaction of 10+ acts."},
                    {"label": "02. THE PSYCHOLOGY OF EMPATHY", "text": "Witnessing kindness releases oxytocin and dopamine, reducing cortisol stress across bystanders."},
                    {"label": "03. REBUILDING A LIFE QUIETLY", "text": "True strength lies not in standing alone, but in reaching down to lift someone back onto their feet."},
                    {"label": "04. THE UNSEEN HEROES", "text": "The greatest heroes of humanity operate in silent anonymity, asking for zero praise or applause."}
                ],
                "fun_fact": [
                    "• Studies show committing one small act of kindness increases personal happiness for 14 straight days!",
                    "• Empathy is scientifically contagious—communities with generous leaders show 40% lower anxiety.",
                    "• A simple genuine smile activates 17 facial muscles and triggers mirror neurons in onlookers."
                ]
            }
        ]
    },
    "dragons_and_fantasy_lore": {
        "theme_name": "MYTHICAL CREATURE BESTIARY",
        "badge_tag": "ANCIENT FOLKLORE & DRAGON LORE",
        "palette": {
            "bg": (11, 15, 25),           # Deep Fantasy Midnight
            "primary": (255, 255, 255),
            "sub": (148, 163, 184),
            "card_bg": (20, 27, 45, 240),
            "card_border": (45, 60, 90),
            "accent": (56, 189, 248),     # Electric Frost Cyan
            "footer_bg": (3, 7, 18)
        },
        "search_term": "epic fantasy dragon illustration high detail concept art",
        "topics": [
            {
                "slug": "nordic_frost_wyvern",
                "title": "NORDIC FROST WYVERN: SAGA BEAST",
                "sub": "Draco Glacialis • Arctic Scandinavian Folklore",
                "badge": "MYTHOLOGICAL BESTIARY",
                "cards": [
                    {"label": "01. SUB-ZERO SUB-ZERO ARMOR", "text": "Glacial crystalline scales deflect steel weaponry and absorb volcanic heat without cracking."},
                    {"label": "02. LIQUID NITROGEN BREATH", "text": "Exhales supercooled aerosol that freezes biological tissue and stone structures on contact."},
                    {"label": "03. BATS-WING WINGSPAN", "text": "Two-legged wyvern anatomy with 40-meter leathery wings suited for riding blizzard thermals."},
                    {"label": "04. VIKING CHRONICLES", "text": "Depicted on Norse longship prow carvings as guardians of icy navigational mountain fjords."}
                ],
                "fun_fact": [
                    "• In traditional heraldry, a Wyvern has only two legs, while a true Dragon has four legs!",
                    "• Nordic sagas believed finding shed dragon scales in snow was an omen of extreme winter storms.",
                    "• Ancient Norse warriors forged spearheads with serpent patterns hoping to capture wyvern fury."
                ]
            }
        ]
    }
}

class InfographicEngine:
    """
    Production-Grade Infographic Render Engine:
    - 100% Niche Isolated: Miniature gets diorama craft, Owls get birds, Tigers get wildlife.
    - Zero Text Overflow: Dynamic font scaling + multi-line bounding calculations.
    - Zero Missing Glyphs: Clean typographic bullets, zero broken emoji boxes.
    - Full HD 1080x1350 (4:5 Portrait) sharp contrast.
    """

    def __init__(self, cache_dir: str = "temp/infographic_cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

        # Cross-platform fonts
        bold_paths = [
            "C:/Windows/Fonts/segoeuib.ttf", "C:/Windows/Fonts/arialbd.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSansBold.ttf"
        ]
        reg_paths = [
            "C:/Windows/Fonts/segoeui.ttf", "C:/Windows/Fonts/arial.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/freefont/FreeSans.ttf"
        ]
        italic_paths = [
            "C:/Windows/Fonts/segoeuii.ttf", "C:/Windows/Fonts/ariali.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"
        ]

        self.font_bold = next((p for p in bold_paths if os.path.exists(p)), None)
        self.font_reg = next((p for p in reg_paths if os.path.exists(p)), None)
        self.font_italic = next((p for p in italic_paths if os.path.exists(p)), self.font_reg)

    def _get_font(self, font_path: Optional[str], size: int) -> ImageFont.ImageFont:
        if font_path and os.path.exists(font_path):
            try:
                return ImageFont.truetype(font_path, size)
            except Exception:
                pass
        return ImageFont.load_default()

    def fetch_niche_image(self, search_query: str, fallback_bg_color: Tuple[int, int, int]) -> Image.Image:
        """Fetches HD photography matching the specific search term with zero tiger leaks."""
        cache_hash = hashlib.md5(search_query.encode("utf-8")).hexdigest()
        cache_path = os.path.join(self.cache_dir, f"{cache_hash}.jpg")

        if os.path.exists(cache_path):
            try:
                return Image.open(cache_path).convert("RGBA")
            except Exception:
                pass

        # Clean search URL with prompt
        encoded_query = search_query.replace(' ', '%20')
        url = f"https://image.pollinations.ai/prompt/high%20quality%20photography%20of%20{encoded_query}?width=800&height=1100&nologo=true"
        
        try:
            res = requests.get(url, timeout=12)
            if res.status_code == 200 and len(res.content) > 10000:
                with open(cache_path, "wb") as f:
                    f.write(res.content)
                return Image.open(io.BytesIO(res.content)).convert("RGBA")
        except Exception as e:
            logger.warning(f"Image fetch network error for '{search_query}': {e}")

        # If network fails, build an elegant geometric/gradient visual card (NOT a random animal!)
        fallback = Image.new("RGBA", (800, 1100), fallback_bg_color)
        f_draw = ImageDraw.Draw(fallback)
        for y in range(1100):
            factor = y / 1100.0
            r = int(fallback_bg_color[0] * (1 - factor * 0.4))
            g = int(fallback_bg_color[1] * (1 - factor * 0.4))
            b = int(fallback_bg_color[2] * (1 - factor * 0.4))
            f_draw.line([(0, y), (800, y)], fill=(r, g, b, 255))
        return fallback

    def render_infographic(
        self,
        page_name: str,
        vertical_key: str,
        topic: Dict[str, Any],
        output_path: str
    ) -> Dict[str, Any]:
        """
        Renders an ultra-sharp 1080x1350 graphic with:
        - Exact niche-specific color palette.
        - Dynamic 2-line wrapped title with auto-font scaling so it NEVER clips into the photo.
        - Zero missing glyphs (Unicode bullets • and clean borders).
        """
        W, H = 1080, 1350

        # Retrieve authentic vertical metadata
        v_data = AUTHENTIC_VERTICAL_DATA.get(vertical_key, AUTHENTIC_VERTICAL_DATA["miniature_diorama_disaster"])
        colors = v_data["palette"]

        canvas = Image.new("RGBA", (W, H), colors["bg"])
        draw = ImageDraw.Draw(canvas)

        # 1. Dynamic Title Header (With Auto-Shrink to prevent text clipping)
        title_text = topic["title"].upper()
        
        # Calculate optimal font size for title (max width: 480px)
        max_title_w = 475
        base_title_size = 46
        f_title = self._get_font(self.font_bold, base_title_size)

        # Word wrap title
        words = title_text.split()
        title_lines = []
        cur_t = []
        for w in words:
            test_t = " ".join(cur_t + [w])
            if draw.textbbox((0, 0), test_t, font=f_title)[2] <= max_title_w:
                cur_t.append(w)
            else:
                if cur_t:
                    title_lines.append(" ".join(cur_t))
                cur_t = [w]
        if cur_t:
            title_lines.append(" ".join(cur_t))

        # If more than 2 lines, shrink font size
        if len(title_lines) > 2:
            base_title_size = 36
            f_title = self._get_font(self.font_bold, base_title_size)
            # re-wrap
            title_lines = []
            cur_t = []
            for w in words:
                test_t = " ".join(cur_t + [w])
                if draw.textbbox((0, 0), test_t, font=f_title)[2] <= max_title_w:
                    cur_t.append(w)
                else:
                    if cur_t:
                        title_lines.append(" ".join(cur_t))
                    cur_t = [w]
            if cur_t:
                title_lines.append(" ".join(cur_t))

        # Draw wrapped title lines
        ty = 50
        for tl in title_lines[:2]:
            draw.text((55, ty), tl, font=f_title, fill=colors["primary"])
            ty += (base_title_size + 8)

        # Subtitle
        f_sub = self._get_font(self.font_italic, 22)
        draw.text((55, ty + 2), topic.get("sub", ""), font=f_sub, fill=colors["sub"])

        # Category Badge Box
        f_badge = self._get_font(self.font_bold, 16)
        badge_text = topic.get("badge", v_data["badge_tag"])
        b_bbox = draw.textbbox((0, 0), badge_text, font=f_badge)
        b_w = b_bbox[2] - b_bbox[0] + 28
        b_box = [(55, ty + 38), (55 + b_w, ty + 74)]
        draw.rounded_rectangle(b_box, radius=6, fill=colors.get("card_border", (50, 60, 75)))
        draw.text((69, ty + 44), badge_text, font=f_badge, fill=colors["accent"])

        # 2. HD Subject Image Frame (Right Half)
        search_query = f"{topic['title']} {v_data['search_term']}"
        photo = self.fetch_niche_image(search_query, colors["card_bg"][:3])
        
        photo_box = (545, 50, 1025, 1180)
        target_w = photo_box[2] - photo_box[0]
        target_h = photo_box[3] - photo_box[1]

        pw, ph = photo.size
        scale = max(target_w / pw, target_h / ph)
        new_w, new_h = int(pw * scale), int(ph * scale)
        photo_resized = photo.resize((new_w, new_h), Image.Resampling.LANCZOS)
        
        left = (new_w - target_w) // 2
        top = (new_h - target_h) // 2
        cropped = photo_resized.crop((left, top, left + target_w, top + target_h))

        mask = Image.new("L", (target_w, target_h), 0)
        mask_draw = ImageDraw.Draw(mask)
        mask_draw.rounded_rectangle([(0, 0), (target_w, target_h)], radius=22, fill=255)
        canvas.paste(cropped, (photo_box[0], photo_box[1]), mask)

        draw.rounded_rectangle(
            [(photo_box[0], photo_box[1]), (photo_box[2], photo_box[3])],
            radius=22,
            outline=colors["card_border"],
            width=2
        )

        # 3. Left Side 4 Authentic Niche Cards
        f_card_label = self._get_font(self.font_bold, 20)
        f_card_body = self._get_font(self.font_reg, 18)

        card_y = ty + 90
        card_w = 465
        card_h = 145
        card_gap = 16

        for c_idx, c_data in enumerate(topic.get("cards", [])[:4]):
            draw.rounded_rectangle(
                [(55, card_y), (55 + card_w, card_y + card_h)],
                radius=14,
                fill=colors["card_bg"],
                outline=colors["card_border"],
                width=1
            )
            # Colored Left Accent Bar
            draw.rounded_rectangle(
                [(57, card_y + 12), (63, card_y + card_h - 12)],
                radius=3,
                fill=colors["accent"]
            )

            # Label
            draw.text((75, card_y + 16), c_data["label"], font=f_card_label, fill=colors["primary"])

            # Text wrapping
            words = c_data["text"].split()
            lines = []
            cur_l = []
            for w in words:
                test_l = " ".join(cur_l + [w])
                if draw.textbbox((0, 0), test_l, font=f_card_body)[2] <= (card_w - 40):
                    cur_l.append(w)
                else:
                    lines.append(" ".join(cur_l))
                    cur_l = [w]
            if cur_l:
                lines.append(" ".join(cur_l))

            by = card_y + 52
            for line in lines[:3]:
                draw.text((75, by), line, font=f_card_body, fill=colors["sub"])
                by += 25

            card_y += card_h + card_gap

        # 4. Bottom Left "DID YOU KNOW?" Authentic Callout Box
        f_fun_title = self._get_font(self.font_bold, 20)
        f_fun_body = self._get_font(self.font_reg, 17)

        fun_box = [(55, 915), (520, 1180)]
        draw.rounded_rectangle(fun_box, radius=16, fill=colors["card_bg"], outline=colors["card_border"], width=1)
        draw.text((75, 935), "DID YOU KNOW? - PRO SECRETS", font=f_fun_title, fill=colors["accent"])
        
        fy = 975
        for fact_line in topic.get("fun_fact", [])[:3]:
            # Word wrap fact lines
            f_words = fact_line.split()
            f_wrapped = []
            f_cur = []
            for fw in f_words:
                test_f = " ".join(f_cur + [fw])
                if draw.textbbox((0, 0), test_f, font=f_fun_body)[2] <= 425:
                    f_cur.append(fw)
                else:
                    f_wrapped.append(" ".join(f_cur))
                    f_cur = [fw]
            if f_cur:
                f_wrapped.append(" ".join(f_cur))

            for fl in f_wrapped[:2]:
                draw.text((75, fy), fl, font=f_fun_body, fill=colors["sub"])
                fy += 23
            fy += 6

        # 5. Clean Footer Bar (No broken emoji boxes)
        f_footer = self._get_font(self.font_bold, 20)
        footer_box = [(55, 1220), (W - 55, 1295)]
        draw.rounded_rectangle(footer_box, radius=14, fill=colors["footer_bg"])

        footer_left = f"{page_name.upper()}  •  {v_data['theme_name']}"
        draw.text((85, 1242), footer_left, font=f_footer, fill=colors["sub"])

        footer_right = f"FOLLOW @{page_name.upper()}"
        fr_w = draw.textbbox((0, 0), footer_right, font=f_footer)[2]
        draw.text((W - 85 - fr_w, 1242), footer_right, font=f_footer, fill=colors["accent"])

        # Save Ultra Sharp Image
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)
        canvas = canvas.convert("RGB")
        canvas.save(output_path, "PNG", quality=95)
        logger.info(f"Rendered Niche-Accurate Infographic: {output_path}")

        # Construct viral caption + hashtags
        caption = (
            f"🔥 {topic['title']} — {v_data['badge_tag']}\n\n"
            f"Mastering the secrets behind {topic['title']}:\n"
            f"Swipe through to discover the exact techniques, scales, and pro secrets!\n\n"
            f"👉 Follow @{page_name} for daily visual guides!\n\n"
            f"#{topic['slug']} #{vertical_key} #DailyGuide #ProTips #Explore #FYP"
        )

        return {
            "image_path": output_path,
            "title": topic["title"],
            "caption": caption,
            "topic_slug": topic["slug"]
        }
