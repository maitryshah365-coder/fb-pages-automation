import os
import sys
import io
import json
import base64
import logging
import hashlib
import requests
from typing import Dict, Any, Tuple, Optional, List
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger("fb_automation")

# =========================================================================
# 1. ART STYLES & MASTER PROMPT ENGINEERING (Rotating Visual Mediums)
# =========================================================================

ART_STYLES = {
    "national_geographic_8k": {
        "label": "📷 8K Real Photography",
        "badge_bg": "rgba(15, 23, 42, 0.85)",
        "badge_color": "#38bdf8",
        "prompt_suffix": "award-winning National Geographic wildlife photograph, ultra-realistic, 8k resolution, captured with Sony Alpha 1, 400mm f/2.8 lens, natural lighting, hyper-detailed fur, feathers and eyes, authentic real life shot, cinematic depth of field, RAW photo, no cartoon, no CGI, no 3D animation, photorealistic masterpiece"
    },
    "cinematic_4k": {
        "label": "🎬 Cinematic 4K Photo",
        "badge_bg": "rgba(15, 23, 42, 0.85)",
        "badge_color": "#38bdf8",
        "prompt_suffix": "breathtaking cinematic 4K photography, dramatic natural rim light, National Geographic documentary still, shallow depth of field, real life authentic shot, ultra crisp detail, photorealistic masterpiece, no cartoon, no 3D render"
    },
    "macro_optical": {
        "label": "🔬 Optical Macro Photo",
        "badge_bg": "rgba(15, 23, 42, 0.85)",
        "badge_color": "#38bdf8",
        "prompt_suffix": "stunning optical macro nature photograph, Canon EOS R5 with 100mm f/2.8L Macro lens, genuine optical depth, ultra-sharp realistic details, real world authentic photo, National Geographic style, no CGI, no cartoon"
    },
    "aerial_documentary": {
        "label": "🦅 Aerial Real Photo",
        "badge_bg": "rgba(15, 23, 42, 0.85)",
        "badge_color": "#38bdf8",
        "prompt_suffix": "epic aerial documentary nature photography, Hasselblad medium format, ultra realistic, dramatic natural atmosphere, 8K ultra high definition real life photo, no drawing, no cartoon"
    }
}

ART_STYLE_KEYS = list(ART_STYLES.keys())

# =========================================================================
# 2. 12 FULLY DIVERSE TEMPLATE ARCHETYPES (Rotating Sequentially)
# =========================================================================

TEMPLATE_STYLES = [
    "vibrant_multicolor",     # Style 1: 4 Colored Cards + 5-Pill Color Shelf (Ref 4 & 5)
    "anatomical_pointer",     # Style 2: Biometric / Anatomy Callout Diagram (Ref 3)
    "vintage_fieldguide",     # Style 3: NatGeo / Natural History Specimen Archive (Ref 1)
    "canva_poster",           # Style 4: Illustrated Organic Nature Poster (Ref 2)
    "bento_dashboard",        # Style 5: Modern Tech Bento Grid with Big Stat Badges
    "cinematic_hero",         # Style 6: Magazine Cover with Frosted Glassmorphism
    "split_comparison",       # Style 7: Head-to-Head Comparison ("THIS VS THAT" Battlecard)
    "timeline_roadmap",       # Style 8: Vertical Stepped Process / Timeline Roadmap
    "radar_pie_infographic",  # Style 9: Circular Data Pie Wheel & Vector Badges (Ref 4)
    "encyclopedic_dossier",   # Style 10: Classified Archival File & Redacted Stamp
    "polaroid_scrapbook",     # Style 11: Explorer Field Journal & Overlapping Polaroids
    "cyber_blueprint_hud",    # Style 12: Architectural CAD Blueprint & Caliper Schematics
    "comic_pop_art",          # Style 13: Retro Pop Art Comic Strip & Speech Bursts
    "minimalist_swiss_grid"   # Style 14: Modernist Swiss Typography & Roman Numeral Grid
]

# =========================================================================
# 3. VIBRANT MULTI-COLOR PALETTES (Never Monochromatic!)
# =========================================================================

PALETTE_THEMES = {
    "pop_sky_azure": {
        "name": "Pop Azure Sky & Multicolor",
        "bg_gradient": "linear-gradient(135deg, #7ea8be 0%, #a2c4d6 100%)",
        "canvas_bg": "#7ea8be",
        "text_main": "#1e293b",
        "text_sub": "#334155",
        "text_muted": "#475569",
        "card_bg": "#ffffff",
        "card_border": "#cbd5e1",
        "accent": "#f97316",
        "accent_secondary": "#0284c7",
        "stat_colors": ["#f97316", "#10b981", "#8b5cf6", "#f43f5e"],
        "shelf_colors": ["#16a34a", "#0284c7", "#d97706", "#475569", "#db2777"]
    },
    "jungle_safari_vibrant": {
        "name": "Jungle Safari & Canary Gold",
        "bg_gradient": "linear-gradient(135deg, #1e392a 0%, #15271d 100%)",
        "canvas_bg": "#1e392a",
        "text_main": "#ffffff",
        "text_sub": "#d1fae5",
        "text_muted": "#a7f3d0",
        "card_bg": "rgba(255, 255, 255, 0.92)",
        "card_border": "#34d399",
        "accent": "#fbbf24",
        "accent_secondary": "#4ade80",
        "stat_colors": ["#eab308", "#10b981", "#06b6d4", "#f43f5e"],
        "shelf_colors": ["#22c55e", "#eab308", "#06b6d4", "#ec4899", "#8b5cf6"]
    },
    "sunset_warm_pop": {
        "name": "Sunset Tangerine & Coral Pop",
        "bg_gradient": "linear-gradient(135deg, #ffedd5 0%, #fed7aa 100%)",
        "canvas_bg": "#ffedd5",
        "text_main": "#431407",
        "text_sub": "#7c2d12",
        "text_muted": "#9a3412",
        "card_bg": "#ffffff",
        "card_border": "#fdba74",
        "accent": "#ea580c",
        "accent_secondary": "#c026d3",
        "stat_colors": ["#ea580c", "#d97706", "#7c3aed", "#e11d48"],
        "shelf_colors": ["#f97316", "#059669", "#7c3aed", "#dc2626", "#0284c7"]
    },
    "midnight_neon_spectrum": {
        "name": "Midnight Dark Neon Spectrum",
        "bg_gradient": "linear-gradient(135deg, #090d16 0%, #030712 100%)",
        "canvas_bg": "#090d16",
        "text_main": "#ffffff",
        "text_sub": "#cbd5e1",
        "text_muted": "#94a3b8",
        "card_bg": "#111827",
        "card_border": "#1f2937",
        "accent": "#38bdf8",
        "accent_secondary": "#ec4899",
        "stat_colors": ["#38bdf8", "#ec4899", "#10b981", "#f59e0b"],
        "shelf_colors": ["#06b6d4", "#ec4899", "#10b981", "#f59e0b", "#a855f7"]
    },
    "clean_editorial_white": {
        "name": "Editorial Studio White & Primary Pop",
        "bg_gradient": "linear-gradient(135deg, #f8fafc 0%, #f1f5f9 100%)",
        "canvas_bg": "#f8fafc",
        "text_main": "#0f172a",
        "text_sub": "#334155",
        "text_muted": "#64748b",
        "card_bg": "#ffffff",
        "card_border": "#e2e8f0",
        "accent": "#2563eb",
        "accent_secondary": "#dc2626",
        "stat_colors": ["#2563eb", "#dc2626", "#059669", "#d97706"],
        "shelf_colors": ["#2563eb", "#dc2626", "#059669", "#d97706", "#7c3aed"]
    },
    "pastel_dream_pop": {
        "name": "Pastel Playful Bubble Pop",
        "bg_gradient": "linear-gradient(135deg, #ede9fe 0%, #fae8ff 100%)",
        "canvas_bg": "#ede9fe",
        "text_main": "#2e1065",
        "text_sub": "#581c87",
        "text_muted": "#701a75",
        "card_bg": "#ffffff",
        "card_border": "#ddd6fe",
        "accent": "#9333ea",
        "accent_secondary": "#db2777",
        "stat_colors": ["#9333ea", "#0284c7", "#059669", "#e11d48"],
        "shelf_colors": ["#9333ea", "#0284c7", "#059669", "#e11d48", "#d97706"]
    }
}

# =========================================================================
# 4. 13 FLEET VERTICALS AUTHENTIC FALLBACK IMAGES & DATA MATRIX (100% Niche Isolated)
# =========================================================================

AUTHENTIC_VERTICAL_FALLBACKS = {
    "miniature_diorama_disaster": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=900&auto=format&fit=crop&q=80",
    "pet_owls_birds": "https://images.unsplash.com/photo-1579202673506-ca3ce28943ef?w=900&auto=format&fit=crop&q=80",
    "huskies_canine_psychology": "https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?w=900&auto=format&fit=crop&q=80",
    "humanity_and_good_deeds": "https://images.unsplash.com/photo-1488521787991-ed7bbaae773c?w=900&auto=format&fit=crop&q=80",
    "wildlife_apex_predators": "https://images.unsplash.com/photo-1561731216-c3a4d99437d5?w=900&auto=format&fit=crop&q=80",
    "ancient_empires": "https://images.unsplash.com/photo-1552832230-c0197dd311b5?w=900&auto=format&fit=crop&q=80",
    "dragons_and_fantasy_lore": "https://images.unsplash.com/photo-1518709268805-4e9042af9f23?w=900&auto=format&fit=crop&q=80",
    "football_legends": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=900&auto=format&fit=crop&q=80",
    "ocean_marine_life": "https://images.unsplash.com/photo-1568430462989-44163eb1752f?w=900&auto=format&fit=crop&q=80",
    "science_engineering_wonders": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900&auto=format&fit=crop&q=80",
    "supercars_and_hypercars": "https://images.unsplash.com/photo-1503376780353-7e6692767b70?w=900&auto=format&fit=crop&q=80",
    "oddly_satisfying_craft": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=900&auto=format&fit=crop&q=80",
    "wilderness_bushcraft_survival": "https://images.unsplash.com/photo-1504280390367-361c6d9f38f4?w=900&auto=format&fit=crop&q=80"
}

AUTHENTIC_VERTICAL_DATA = {
    "miniature_diorama_disaster": {
        "theme_name": "MINIATURE DIORAMA CRAFT & ENGINEERING",
        "badge_tag": "SCALE 1:87 CRAFT MASTERCLASS",
        "search_term": "detailed miniature diorama scale model crafting macro",
        "topics": [
            {
                "slug": "resin_water_flood",
                "title": "Hyper-Realistic Flood & Water FX",
                "latin": "Scale 1:87 • Advanced Liquid Dynamics",
                "badge": "EPOXY RESIN WATER ENGINEERING",
                "image_url": "https://images.unsplash.com/photo-1513542789411-b6a5d4f31634?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "1:87",
                "stat_primary_label": "Exact HO Proportions",
                "stat_secondary": "0.1mm",
                "stat_secondary_label": "Micro-Wire In Walls",
                "cards": [
                    {"label": "01. Epoxy Resin Ratio", "text": "2-part crystal clear epoxy resin mixed at exact 1:1 ratio prevents clouding."},
                    {"label": "02. Churning Rapids FX", "text": "Clear silicone caulk textured with wet toothpick creates dynamic churning waves."},
                    {"label": "03. Depth Color Inks", "text": "Deep sea teal alcohol ink base layered with transparent green gives 3D depth."},
                    {"label": "04. Titanium Whitewater", "text": "Titanium white acrylic dry-brushed over wave crests simulates realistic foam."}
                ],
                "callouts": [
                    {"label": "Wave Crest Texture", "text": "Clear 100% silicone textured with toothpicks creates churning whitewater."},
                    {"label": "Scale 1:87 Furniture", "text": "Hand-painted 3D resin furniture weathered with burnt umber washes."},
                    {"label": "Submerged Flooring", "text": "Gloss varnish applied prior to pour prevents wood grain from swelling."},
                    {"label": "Micro-Bubble Release", "text": "99% Isopropyl alcohol spritzed over wet resin pops all micro-bubbles instantly."},
                    {"label": "Capillary Wall Creep", "text": "Tamiya clear acrylic wash brushed up walls mimics rising moisture."},
                    {"label": "Resin Curing Heat", "text": "Poured in 4mm stages to prevent exothermic heat from melting polystyrene base."}
                ],
                "shelf_specs": [
                    {"icon": "🌊", "title": "Epoxy Pour", "desc": "Teal base with white foam crests"},
                    {"icon": "💡", "title": "SMD Lights", "desc": "3V CR2032 hidden in diorama base"},
                    {"icon": "⚡", "title": "Static Grass", "desc": "12kV ionizer stands fibers upright"},
                    {"icon": "🎨", "title": "Pastel Dust", "desc": "Mineral spirits pull grime into cracks"},
                    {"icon": "🛡️", "title": "UV Seal", "desc": "Dead-flat lacquer stops yellowing"}
                ],
                "fun_fact": [
                    "Spritzing 99% Isopropyl alcohol over wet epoxy pops all micro-bubbles in 2 seconds!",
                    "Real fine river sand sifted through coffee filters gives 100% authentic scale grit.",
                    "Mod Podge gloss sealer locks water reflections for years without yellowing."
                ]
            },
            {
                "slug": "realistic_rust_weathering",
                "title": "Industrial Rust & Peeling Paint",
                "latin": "Scale 1:87 • Multi-Layer Chemical Weathering",
                "badge": "PATINA & OXIDATION CRAFT",
                "image_url": "https://images.unsplash.com/photo-1581291518857-4e27b48ff24e?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "3-Stage",
                "stat_primary_label": "Chipping Fluid Wash",
                "stat_secondary": "12 Hrs",
                "stat_secondary_label": "Pigment Fixer Cure",
                "cards": [
                    {"label": "01. Base Oxidation Layer", "text": "Real iron powder mixed with matte medium and activated with vinegar wash."},
                    {"label": "02. Hairspray Chipping", "text": "Chipping fluid sprayed before topcoat lets you scrub off realistic scratches."},
                    {"label": "03. Oil Paint Streaking", "text": "Burnt umber oil wash dragged downward with mineral spirits simulates rain rust."},
                    {"label": "04. Matte Dust Pigments", "text": "Crushed earth pastel pigments brushed into crevices simulate decades of grime."}
                ],
                "callouts": [
                    {"label": "Surface Pitting", "text": "Baking soda stippled into wet primer creates pitted corroded metal texture."},
                    {"label": "Chipped Paint Edge", "text": "Stiff hog bristle brush dipped in warm water scrubs away outer lacquer."},
                    {"label": "Vertical Rust Stains", "text": "Raw sienna oil dots blended downward using clean odorless mineral spirits."},
                    {"label": "Friction Shine", "text": "4B graphite pencil rubbed along door handles and rails simulates bare worn steel."},
                    {"label": "Soot & Grime", "text": "Carbon black dry pigment loaded around exhaust vents and chimney tops."},
                    {"label": "Ultra-Matte Seal", "text": "Dead flat varnish coat locks pastels without altering color values."}
                ],
                "shelf_specs": [
                    {"icon": "🧪", "title": "Vinegar Rust", "desc": "Activates natural iron particle powder"},
                    {"icon": "💨", "title": "Hairspray Scrub", "desc": "Warm water removes chipping layer"},
                    {"icon": "🖌️", "title": "Oil Streaks", "desc": "Burnt umber dragged vertically"},
                    {"icon": "✏️", "title": "Graphite Edge", "desc": "4B lead rub simulates friction wear"},
                    {"icon": "🔒", "title": "Matte Fixer", "desc": "Permanently seals pastels"}
                ],
                "fun_fact": [
                    "Table salt sprinkled over wet basecoat creates authentic blistered rust patches!",
                    "Graphite pencil rubbed on metal edges gives genuine worn metallic friction shine.",
                    "Ultra-matte clear coat permanently locks pigment powders without changing color tone."
                ]
            }
        ]
    },

    "pet_owls_birds": {
        "theme_name": "OWLS & BIRDS OF PREY FIELD GUIDE",
        "badge_tag": "AVIAN BIOMECHANICS & PREDATION",
        "search_term": "owl bird of prey close up portrait wildlife",
        "topics": [
            {
                "slug": "barn_owl_silent_flight",
                "title": "Barn Owl: Silent Night Hunter",
                "latin": "Tyto alba • The Apex Acoustic Stalker",
                "badge": "RAPTOR ACOUSTICS & FLIGHT",
                "image_url": "https://images.unsplash.com/photo-1543549790-8b5f4a028cfb?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "0 dB",
                "stat_primary_label": "Flight Sound Level",
                "stat_secondary": "270°",
                "stat_secondary_label": "Head Rotation Range",
                "cards": [
                    {"label": "01. Zero-Decibel Flight", "text": "Comb-like serrated wing margins break air into micro-eddies, silencing flap noise."},
                    {"label": "02. Asymmetrical Ears", "text": "One ear is higher than the other, allowing 3D sonic triangulation of prey in snow."},
                    {"label": "03. 110° Binocular Vision", "text": "Tubular eyes locked into skull provide telescope-level depth perception at night."},
                    {"label": "04. Apex Hunting Talons", "text": "Four curved razor talons deliver 30 lbs of crushing grip force, neutralizing prey."}
                ],
                "callouts": [
                    {"label": "70° Tubular Eyes", "text": "Locked in sockets; cylindrical shape gives incredible nocturnal light gathering."},
                    {"label": "Acoustic Facial Disc", "text": "Stiff feathers channel micro-frequencies directly into auditory ear canals."},
                    {"label": "Crushing Talon Lock", "text": "Curved zygodactyl talons snap shut with 30 lbs of force on impact."},
                    {"label": "Asymmetrical Ears", "text": "Height difference between ears allows 3D acoustic triangulation."},
                    {"label": "Serrated Wing Combs", "text": "Leading-edge comb feathers break turbulence, dropping flight sound to 0 dB."},
                    {"label": "Soft Down Velvet", "text": "Velvety dorsal down absorbs high-frequency sounds during vertical dives."}
                ],
                "shelf_specs": [
                    {"icon": "🔇", "title": "0 dB Wings", "desc": "Serrated combs eliminate flap noise"},
                    {"icon": "👂", "title": "3D Sonar", "desc": "Offset ear heights triangulate mice"},
                    {"icon": "🔄", "title": "270° Swivel", "desc": "14 neck vertebrae rotate head"},
                    {"icon": "🦅", "title": "30 lb Talons", "desc": "Curved zygodactyl bone grip"},
                    {"icon": "🌙", "title": "Tubular Eyes", "desc": "Gathers starlight in pitch black"}
                ],
                "fun_fact": [
                    "A single family of barn owls consumes over 3,000 rodents every single year!",
                    "Owls cannot roll their eyes! Instead, they rotate their heads up to 270 degrees.",
                    "Their heart-shaped facial disk acts like a satellite dish, focusing sound to ears."
                ]
            }
        ]
    },

    "huskies_canine_psychology": {
        "theme_name": "SIBERIAN HUSKY & CANINE PSYCHOLOGY",
        "badge_tag": "ARCTIC ENDURANCE & BEHAVIOR",
        "search_term": "siberian husky dog snow blue eyes portrait",
        "topics": [
            {
                "slug": "husky_arctic_endurance",
                "title": "Siberian Husky: Sub-Zero Machine",
                "latin": "Canis lupus familiaris • Chukchi Heritage",
                "badge": "ARCTIC CANINE BIOLOGY",
                "image_url": "https://images.unsplash.com/photo-1537151625747-768eb6cf92b2?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "-60°C",
                "stat_primary_label": "Cold Tolerance Limit",
                "stat_secondary": "160 km",
                "stat_secondary_label": "Daily Sled Run Range",
                "cards": [
                    {"label": "01. Double-Layer Thermal Coat", "text": "Dense undercoat traps warm air; coarse guard hairs shed water, ice and snow."},
                    {"label": "02. Paw Heat Exchangers", "text": "Counter-current blood flow warms blood returning from paws before hitting the heart."},
                    {"label": "03. Metabolic Miracle", "text": "Can burn glycogen and fat simultaneously for days without suffering muscle fatigue."},
                    {"label": "04. Pack Vocal Linguistics", "text": "Vocalizes via multi-tone howls, groans, and chuffs rather than standard barking."}
                ],
                "callouts": [
                    {"label": "Almond Heterochromia", "text": "Can have two striking blue, brown, or split-color eyes with UV glare protection."},
                    {"label": "Fox-Like Tail Plume", "text": "Curled tail covers nose and face while sleeping to pre-warm freezing arctic air."},
                    {"label": "Vascular Foot Pads", "text": "Specialized webbing and tough paw pads provide natural sub-zero crampon traction."},
                    {"label": "Triangular Erect Ears", "text": "Heavily furred inner ear canals prevent frostbite in howling blizzards."},
                    {"label": "Deep Rib Cage", "text": "Expanded chest cavity houses massive aerobic lungs for non-stop hauling."},
                    {"label": "Double Insulating Coat", "text": "Undercoat so dense that snow falling on a sleeping husky will never melt!"}
                ],
                "shelf_specs": [
                    {"icon": "❄️", "title": "-60°C Frost", "desc": "Double coat traps body warmth"},
                    {"icon": "🐺", "title": "Pack Howl", "desc": "Complex harmonic vocalizations"},
                    {"icon": "🐾", "title": "Warm Paws", "desc": "Counter-current circulatory arteries"},
                    {"icon": "⚡", "title": "160km Run", "desc": "Fat-burning endurance metabolism"},
                    {"icon": "👁️", "title": "UV Eyes", "desc": "Almond shape protects from snow glare"}
                ],
                "fun_fact": [
                    "Huskies can sleep curled in deep snow at -50°C and stay completely dry and warm!",
                    "They rarely bark; instead they use melodic howls that travel up to 15 kilometers.",
                    "Their unique metabolism allows them to run 150 km a day without depleting muscle glycogen."
                ]
            }
        ]
    },

    "humanity_and_good_deeds": {
        "theme_name": "HUMANITY, EMPATHY & KINDNESS",
        "badge_tag": "TRUE STORIES THAT RESTORE FAITH",
        "search_term": "humanity helping hands kindness uplifting hope",
        "topics": [
            {
                "slug": "quiet_generosity_ripple",
                "title": "The Ripple Effect of Unseen Kindness",
                "latin": "Psychology of Empathy • Quiet Human Altruism",
                "badge": "FAITH IN HUMANITY RESTORED",
                "image_url": "https://images.unsplash.com/photo-1469571486292-0ba58a3f068b?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "14 Days",
                "stat_primary_label": "Oxytocin Happiness Boost",
                "stat_secondary": "3.2x",
                "stat_secondary_label": "Pay-It-Forward Ripple",
                "cards": [
                    {"label": "01. The Grocery Stranger", "text": "Paying forward someone's groceries creates an immediate chain reaction of 10+ acts."},
                    {"label": "02. The Biology of Empathy", "text": "Witnessing kindness releases oxytocin and dopamine, reducing cortisol in bystanders."},
                    {"label": "03. Rebuilding Quietly", "text": "True strength lies not in standing alone, but in reaching down to lift someone up."},
                    {"label": "04. Anonymous Heroes", "text": "The greatest heroes of humanity operate in silent anonymity, asking for zero praise."}
                ],
                "callouts": [
                    {"label": "Mirror Neuron Spark", "text": "Witnessing compassion fires neurological mirror circuits, prompting action."},
                    {"label": "Lower Cortisol Stress", "text": "Acts of charity reduce blood pressure and stress markers across communities."},
                    {"label": "Generosity Cascade", "text": "One selfless gesture inspires an average of three downstream acts of goodwill."},
                    {"label": "Healing Connection", "text": "Genuine listening and presence provides deeper comfort than monetary aid."},
                    {"label": "Community Solidarity", "text": "Grassroots kindness builds resilient social bonds that weather economic storms."},
                    {"label": "Enduring Legacy", "text": "People never forget how you made them feel in their darkest hour of need."}
                ],
                "shelf_specs": [
                    {"icon": "🤝", "title": "Generosity", "desc": "One act triggers 10+ downstream gifts"},
                    {"icon": "🧠", "title": "Mirror Brain", "desc": "Oxytocin surge lowers cortisol stress"},
                    {"icon": "❤️", "title": "Quiet Altruism", "desc": "True kindness seeks zero applause"},
                    {"icon": "🌟", "title": "14-Day Boost", "desc": "Happiness elevated for two weeks"},
                    {"icon": "🕊️", "title": "Resilience", "desc": "Strengthens community bonds"}
                ],
                "fun_fact": [
                    "Studies show committing one small act of kindness increases personal happiness for 14 straight days!",
                    "Empathy is scientifically contagious—communities with generous leaders show 40% lower anxiety.",
                    "A simple genuine smile activates 17 facial muscles and triggers mirror neurons in onlookers."
                ]
            }
        ]
    },

    "wildlife_apex_predators": {
        "theme_name": "APEX PREDATOR FIELD GUIDE",
        "badge_tag": "NATIONAL GEOGRAPHIC WILDLIFE REPORT",
        "search_term": "bengal tiger predator portrait wildlife national geographic",
        "topics": [
            {
                "slug": "bengal_tiger_savanna",
                "title": "Bengal Tiger: Apex Striped Striker",
                "latin": "Panthera tigris tigris • Solitary Jungle Monarch",
                "badge": "ENDANGERED SPECIES (IUCN)",
                "image_url": "https://images.unsplash.com/photo-1546182990-dffeafbe841d?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "1,050 PSI",
                "stat_primary_label": "Crushing Bite Force",
                "stat_secondary": "65 km/h",
                "stat_secondary_label": "Explosive Ambush Velocity",
                "cards": [
                    {"label": "01. Explosive Sprint Speed", "text": "65 km/h sprint velocity combined with 30-foot leap capability in dense forest."},
                    {"label": "02. Crushing Bite Force", "text": "1,050 PSI bite force crushes cervical vertebrae instantly, overpowering large prey."},
                    {"label": "03. Aquatic Dominance", "text": "Skilled swimmer known to cross 7 km rivers effortlessly and hunt inside mangroves."},
                    {"label": "04. Camouflage Biology", "text": "Prey animals see in dichromatic vision, making orange fur look identical to forest green."}
                ],
                "callouts": [
                    {"label": "Night Tapetum Lucidum", "text": "Reflective ocular layer reflects light back through retina, giving 6x human night vision."},
                    {"label": "Infrasound Roar", "text": "Low-frequency rumble below 20 Hz momentarily stuns prey nervous systems."},
                    {"label": "Retractable Claws", "text": "4-inch curved keratin claws kept razor sharp inside protective sheath pockets."},
                    {"label": "False Eye Spots", "text": "White ocelli markings on back of ears fool competitors into thinking tiger is watching."},
                    {"label": "Canine Bone Crushers", "text": "3-inch conical canine teeth packed with pressure-sensing nerves for precision bites."},
                    {"label": "Dichromatic Striping", "text": "Disruptive vertical stripes break the body silhouette against sunlit tall grass."}
                ],
                "shelf_specs": [
                    {"icon": "🦷", "title": "1,050 PSI", "desc": "Bone-crushing bite force power"},
                    {"icon": "⚡", "title": "65 km/h", "desc": "Explosive 30-foot ambush leap"},
                    {"icon": "🌊", "title": "7km Swim", "desc": "Crosses broad mangrove delta rivers"},
                    {"icon": "👁️", "title": "6x Night Eyes", "desc": "Tapetum lucidum amplifies starlight"},
                    {"icon": "🌿", "title": "Dichromatic", "desc": "Deer see orange fur as green foliage"}
                ],
                "fun_fact": [
                    "Tiger stripes are on their actual skin, not just their outer fur coat!",
                    "A tiger's roar contains low-frequency infrasound that momentarily paralyzes nearby prey.",
                    "White false 'eye spots' on the back of tiger ears deter predators from attacking behind."
                ]
            }
        ]
    },

    "ancient_empires": {
        "theme_name": "ANCIENT MILITARY HISTORY & ARCHAEOLOGY",
        "badge_tag": "LEGION & GLADIATOR TACTICAL BLUEPRINT",
        "search_term": "roman legionary gladiator ancient armor helmet history",
        "topics": [
            {
                "slug": "roman_legion_tactics",
                "title": "Roman Legion: The Testudo Shield",
                "latin": "Legio Romana • Tactical Warfare Engineering",
                "badge": "CLASSICAL ANTIQUITY BLUEPRINT",
                "image_url": "https://images.unsplash.com/photo-1568605117036-5fe5e7bab0b7?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "100%",
                "stat_primary_label": "Missile Defense Coverage",
                "stat_secondary": "22 kg",
                "stat_secondary_label": "Marching Lorica Segmentata",
                "cards": [
                    {"label": "01. Interlocking Scutum", "text": "Curved plywood shields locked top and front formed an impenetrable tortoise shell."},
                    {"label": "02. Lorica Segmentata", "text": "Steel plate strips strapped over leather offered deflection against heavy slashing."},
                    {"label": "03. The Gladius Thrust", "text": "20-inch short sword engineered for devastating underhand thrusts in tight ranks."},
                    {"label": "04. Weighted Pilum Javelin", "text": "Soft iron shank bent upon impact, rendering captured enemy shields useless."}
                ],
                "callouts": [
                    {"label": "Galea Helmet Brow", "text": "Extended neck guard and cheek plates deflected downward cavalry strikes."},
                    {"label": "Curved Plywood Scutum", "text": "Composite plywood bound with rawhide and brass boss deflected javelins."},
                    {"label": "Lorica Segmentata", "text": "Segmented iron plates laced with leather gave flexible torso protection."},
                    {"label": "Gladius Hispaniensis", "text": "Double-edged short sword optimized for lethal thrusting in close formations."},
                    {"label": "Hobnailed Caligae", "text": "Leather boots studded with iron cleats gave unstoppable traction in mud."},
                    {"label": "Weighted Pilum Tip", "text": "Pyramidal point punched through armor; shank bent to prevent throw-back."}
                ],
                "shelf_specs": [
                    {"icon": "🛡️", "title": "Testudo Shell", "desc": "Interlocked scutum shields stop arrows"},
                    {"icon": "⚔️", "title": "Gladius", "desc": "20-inch close-quarter thrusting steel"},
                    {"icon": "🎯", "title": "Pilum Javelin", "desc": "Bending soft iron disables shields"},
                    {"icon": "🪖", "title": "Lorica Armor", "desc": "Segmented iron plates over leather"},
                    {"icon": "🥾", "title": "Caligae Boots", "desc": "Hobnailed cleats grip muddy terrain"}
                ],
                "fun_fact": [
                    "A Roman legionary walked 30 kilometers daily carrying 30 kg of battle gear and entrenching tools!",
                    "The curved Scutum shield was so strong that soldiers could stand on top of a formed Testudo shell.",
                    "Pilum javelins were deliberately made with soft iron so enemy troops could never throw them back."
                ]
            }
        ]
    },

    "dragons_and_fantasy_lore": {
        "theme_name": "MYTHICAL CREATURE BESTIARY",
        "badge_tag": "ANCIENT FOLKLORE & DRAGON LORE",
        "search_term": "epic fantasy dragon illustration concept art myth",
        "topics": [
            {
                "slug": "nordic_frost_wyvern",
                "title": "Nordic Frost Wyvern: Saga Beast",
                "latin": "Draco Glacialis • Arctic Scandinavian Folklore",
                "badge": "MYTHOLOGICAL BESTIARY",
                "image_url": "https://images.unsplash.com/photo-1579783900882-c0d3dad7b119?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "40m",
                "stat_primary_label": "Leathery Wingspan",
                "stat_secondary": "2-Legged",
                "stat_secondary_label": "True Wyvern Classification",
                "cards": [
                    {"label": "01. Sub-Zero Scale Armor", "text": "Glacial crystalline scales deflect steel and absorb volcanic heat without cracking."},
                    {"label": "02. Supercooled Aerosol", "text": "Exhales liquid nitrogen aerosol that freezes biological tissue and stone instantly."},
                    {"label": "03. Two-Legged Wyvern Stance", "text": "Anatomically distinct from 4-legged dragons; uses wing-claws for cliff climbing."},
                    {"label": "04. Viking Lore & Prows", "text": "Depicted on Norse longship prow carvings as guardians of frozen sea fjords."}
                ],
                "callouts": [
                    {"label": "Crystalline Horn Spines", "text": "Chilled bone crowns channel glacial winds and signal dominance among clutches."},
                    {"label": "Cryo-Gland Throat", "text": "Internal chemical glands aerosolize volatile organic salts upon exhalation."},
                    {"label": "Diamond Hard Scales", "text": "Layered keratin plates stronger than tempered iron, immune to sub-zero brittleness."},
                    {"label": "Thermal Riding Wings", "text": "Leathery wing membrane reinforced with cartilage struts for riding blizzard updrafts."},
                    {"label": "Prehensile Tail Barb", "text": "Barbed tail acts as a weighted rudder in gales and delivers piercing counterstrikes."},
                    {"label": "Talon Anchor Claws", "text": "Curved ice-axe talons lock securely into sheer glacial seracs and cliff faces."}
                ],
                "shelf_specs": [
                    {"icon": "❄️", "title": "Cryo-Breath", "desc": "Sub-zero aerosol flash freezes stone"},
                    {"icon": "🐉", "title": "2-Legged", "desc": "Wing-claws climb sheer ice crevasses"},
                    {"icon": "💎", "title": "Diamond Scale", "desc": "Keratin armor immune to brittle cold"},
                    {"icon": "🌪️", "title": "Blizzard Wing", "desc": "40m span rides mountain thermals"},
                    {"icon": "⚔️", "title": "Tail Barb", "desc": "Whip-crack rudder for arctic gales"}
                ],
                "fun_fact": [
                    "In heraldic law, a Wyvern has only two legs, while a true Dragon possesses four legs!",
                    "Nordic sagas claimed finding shed dragon scales in snow was an omen of extreme winter storms.",
                    "Ancient Norse smiths etched serpent patterns on spearheads hoping to channel dragon fury."
                ]
            }
        ]
    },

    "football_legends": {
        "theme_name": "FOOTBALL TACTICS & PHYSICS MASTERCLASS",
        "badge_tag": "ELITE SOCCER MECHANICS",
        "search_term": "football soccer stadium match ball physics player",
        "topics": [
            {
                "slug": "magnus_effect_freekick",
                "title": "Magnus Effect: Physics of the Curve",
                "latin": "Aerodynamics of the Banana Kick • Elite Trajectory",
                "badge": "FOOTBALL AERODYNAMICS",
                "image_url": "https://images.unsplash.com/photo-1574629810360-7efbbe195018?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "600 RPM",
                "stat_primary_label": "Ball Spin Velocity",
                "stat_secondary": "130 km/h",
                "stat_secondary_label": "Terminal Strike Speed",
                "cards": [
                    {"label": "01. Asymmetrical Airflow", "text": "Spin creates high pressure on one side and low on the other, bending the ball in flight."},
                    {"label": "02. Instep Striking Zone", "text": "Striking slightly off-center with the instep imparts maximum rotational spin."},
                    {"label": "03. Turbulent Transition", "text": "As the ball slows down mid-air, drag skyrockets, causing a sudden violent dip."},
                    {"label": "04. Goalkeeper Blindspot", "text": "Visual tracking fails when flight path deviates by more than 4 meters over 0.3s."}
                ],
                "callouts": [
                    {"label": "Instep Contact Point", "text": "Striking with the medial bone of the big toe transfers 85% of kinetic energy into spin."},
                    {"label": "Spin Axis Angle", "text": "Tilt of the rotational axis dictates whether the ball curls outward or dips violently."},
                    {"label": "Boundary Layer Flow", "text": "Dimples and seam grooves drag air faster across the spinning side of the sphere."},
                    {"label": "High-Pressure Cushion", "text": "Air accumulates on the resisting face, pushing the ball toward low pressure."},
                    {"label": "Sudden Terminal Dip", "text": "Speed drops below 25 m/s, shifting airflow from turbulent to laminar, plunging into top corner."},
                    {"label": "Follow-Through Whipline", "text": "Hip rotation and locked ankle ensure pure contact without loss of rotational velocity."}
                ],
                "shelf_specs": [
                    {"icon": "⚽", "title": "600 RPM", "desc": "10 full revolutions per second"},
                    {"icon": "🌪️", "title": "Magnus Force", "desc": "Differential air pressure bends path"},
                    {"icon": "🚀", "title": "130 km/h", "desc": "Blistering strike reaches goal in 0.6s"},
                    {"icon": "📐", "title": "Seam Drag", "desc": "Dimples transition laminar airflow"},
                    {"icon": "🧤", "title": "Blindspot", "desc": "Trajectories curve outside optical cone"}
                ],
                "fun_fact": [
                    "Roberto Carlos' legendary 1997 free kick bent so violently that ball boys ducked thinking it was going wide!",
                    "A professional football can rotate at over 10 revolutions per second (600 RPM) during a curling strike.",
                    "High altitude reduces air density, cutting curve deviation by up to 25% compared to sea level."
                ]
            }
        ]
    },

    "ocean_marine_life": {
        "theme_name": "OCEAN ABYSS & MARINE MEGAFAUNA",
        "badge_tag": "DEEP SEA DISCOVERY REPORT",
        "search_term": "blue whale ocean marine deep sea humpback underwater",
        "topics": [
            {
                "slug": "blue_whale_acoustics",
                "title": "Blue Whale: Ocean's Megasonic Giant",
                "latin": "Balaenoptera musculus • Largest Creature to Ever Exist",
                "badge": "OCEANIC MEGAFAUNA",
                "image_url": "https://images.unsplash.com/photo-1518837695005-2083093ee35b?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "188 dB",
                "stat_primary_label": "Acoustic Call Volume",
                "stat_secondary": "190 Tons",
                "stat_secondary_label": "Maximum Recorded Weight",
                "cards": [
                    {"label": "01. Megasonic Infrasound", "text": "Low-frequency calls travel thousands of kilometers across entire ocean basins."},
                    {"label": "02. Heart the Size of a Car", "text": "Weighs over 400 kg; human beings could crawl through the primary aorta artery."},
                    {"label": "03. Baleen Filter Mastery", "text": "Consumes 4 tons of Antarctic krill daily by gulping Olympic pool-sized volumes."},
                    {"label": "04. SOFAR Sound Channel", "text": "Channels songs through deep oceanic thermal layers that refract sound infinitely."}
                ],
                "callouts": [
                    {"label": "Baleen Plate Comb", "text": "Hundreds of keratin plates strain tons of seawater, trapping microscopic krill swarms."},
                    {"label": "Twin Blowhole Nozzle", "text": "Exhales warm air plumes up to 9 meters high with explosive lung capacity."},
                    {"label": "Aorta Vessel Size", "text": "Heart beats only 2 to 4 times per minute during deep feeding dives."},
                    {"label": "Ventral Throat Grooves", "text": "Accordion pleats expand throat volume to swallow 100 tons of water in a single gulp."},
                    {"label": "Counter-Current Rete", "text": "Massive circulatory heat exchangers prevent freezing in polar iceberg waters."},
                    {"label": "Fluke Propulsion", "text": "Horizontal tail flukes span 8 meters, generating tons of silent forward thrust."}
                ],
                "shelf_specs": [
                    {"icon": "🐋", "title": "190 Tons", "desc": "Largest creature to ever live on Earth"},
                    {"icon": "🔊", "title": "188 dB Call", "desc": "Louder than a jet engine at takeoff"},
                    {"icon": "🦐", "title": "4 Tons Krill", "desc": "Filtered daily through baleen plates"},
                    {"icon": "🫀", "title": "Car-Size Heart", "desc": "Aorta is large enough for human crawl"},
                    {"icon": "🌊", "title": "SOFAR Layer", "desc": "Thermal channel carries sound 1,000s km"}
                ],
                "fun_fact": [
                    "A blue whale's tongue alone weighs as much as an entire adult African elephant!",
                    "Their underwater vocalizations are louder than a jet engine at takeoff (188 dB vs 140 dB).",
                    "Blue whale calves drink up to 400 liters of nutrient-rich mother's milk every single day."
                ]
            }
        ]
    },

    "science_engineering_wonders": {
        "theme_name": "SPACE & ASTROPHYSICS DOSSIER",
        "badge_tag": "COSMIC PHENOMENA & ENGINEERING",
        "search_term": "james webb telescope space galaxy nebula astrophysics",
        "topics": [
            {
                "slug": "james_webb_infrared",
                "title": "James Webb: Peering into Cosmic Dawn",
                "latin": "JWST • Infrared Space Observatory Architecture",
                "badge": "AEROSPACE MASTERPIECE",
                "image_url": "https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "6.5m",
                "stat_primary_label": "Gold Primary Mirror Width",
                "stat_secondary": "-233°C",
                "stat_secondary_label": "Sunshield Cold Operating Temp",
                "cards": [
                    {"label": "01. Gold-Coated Beryllium", "text": "18 hexagonal segments vapor-coated in 100nm of pure gold to maximize infrared."},
                    {"label": "02. 5-Layer Kapton Sunshield", "text": "Tennis-court-sized sunshield blocks solar heat, cooling optics down to -233°C."},
                    {"label": "03. Lagrange Point L2", "text": "Orbits 1.5 million km from Earth in gravitationally balanced solar shadow."},
                    {"label": "04. Time Machine Optics", "text": "Captures photons emitted over 13.5 billion years ago right after the Big Bang."}
                ],
                "callouts": [
                    {"label": "Beryllium Hex Mirrors", "text": "Ultra-lightweight metal segments aligned to 1/10,000th the thickness of a human hair."},
                    {"label": "Infrared NIRCam", "text": "Detects cosmological redshifted light piercing through dense interstellar dust clouds."},
                    {"label": "5-Layer Kapton Shield", "text": "Each membrane layer is separated by vacuum gaps, dropping temperature by over 300°C."},
                    {"label": "Secondary Mirror Tripod", "text": "Focuses bounced light back into internal cryogenic instruments behind primary array."},
                    {"label": "Star Tracker Gyroscopes", "text": "Reaction wheels and fine guidance sensors lock onto distant galaxies with zero jitter."},
                    {"label": "Solar Array Wing", "text": "Provides constant 2,000 watts of electrical power while facing perpetual sunward heat."}
                ],
                "shelf_specs": [
                    {"icon": "🔭", "title": "6.5m Mirror", "desc": "18 gold-coated beryllium segments"},
                    {"icon": "❄️", "title": "-233°C Cold", "desc": "5-layer Kapton membrane blocks heat"},
                    {"icon": "🌌", "title": "13.5B Years", "desc": "Peers back to the first cosmic stars"},
                    {"icon": "📍", "title": "L2 Orbit", "desc": "1.5 million km deep space station"},
                    {"icon": "🐝", "title": "Micro-Optics", "desc": "Detects bumblebee heat on the Moon"}
                ],
                "fun_fact": [
                    "The amount of pure gold used to coat all 18 mirrors of the James Webb is only about the size of a golf ball!",
                    "Webb operates at -233°C because warm optics would glow in infrared and blind their own sensors.",
                    "It can detect the heat signature of a bumblebee located as far away as the Moon!"
                ]
            }
        ]
    },

    "supercars_and_hypercars": {
        "theme_name": "HYPERCAR AERODYNAMICS & HORSEPOWER",
        "badge_tag": "PRECISION AUTOMOTIVE ENGINEERING",
        "search_term": "supercar hypercar carbon fiber automotive track vehicle",
        "topics": [
            {
                "slug": "active_aero_downforce",
                "title": "Active Aerodynamics: Ground Effect Physics",
                "latin": "Venturi Tunnels & Variable Downforce Systems",
                "badge": "HYPERCAR DYNAMICS",
                "image_url": "https://images.unsplash.com/photo-1542282088-72c9c27ed0cd?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "1,000 kg",
                "stat_primary_label": "Cornering Downforce",
                "stat_secondary": "2.4s",
                "stat_secondary_label": "0-100 km/h Launch Time",
                "cards": [
                    {"label": "01. Underfloor Venturi Tunnels", "text": "Accelerates air underneath chassis, creating low pressure suction that glues car to tarmac."},
                    {"label": "02. Hydraulic Airbrake Wing", "text": "Rear wing pitches to 70° angle under hard braking, doubling tire friction load."},
                    {"label": "03. Carbon Ceramic Thermal", "text": "Brake rotors withstand over 1,000°C without brake fade or fluid vapor lock."},
                    {"label": "04. Twin-Turbo Boost Vector", "text": "Electric turbos eliminate spool lag, providing linear torque across the entire rev range."}
                ],
                "callouts": [
                    {"label": "Front Splitter Vanes", "text": "Directs turbulent air away from front wheels while channeling smooth air to floor."},
                    {"label": "Carbon Tub Monocoque", "text": "Weaves continuous carbon filaments for supreme torsional rigidity under cornering Gs."},
                    {"label": "Venturi Tunnel Floor", "text": "Expands air volume at rear diffuser to create vacuum suction without adding wing drag."},
                    {"label": "Active Rear Wing Winglets", "text": "Pitches independently side-to-side to push down inside wheel during high-speed turns."},
                    {"label": "Carbon Ceramic Discs", "text": "Silicon carbide composites operate friction-free at glowing incandescent temperatures."},
                    {"label": "Titanium Inconel Exhaust", "text": "Laser-welded ultra-thin alloy sheds 20 kg while withstanding supersonic gas pulses."}
                ],
                "shelf_specs": [
                    {"icon": "🏎️", "title": "1,000kg Aero", "desc": "Suction downforce glues car to tarmac"},
                    {"icon": "🛑", "title": "Airbrake 70°", "desc": "Wing flips up instantly under heavy stop"},
                    {"icon": "🔥", "title": "1,000°C Brakes", "desc": "Carbon ceramic discs glow incandescent"},
                    {"icon": "⏱️", "title": "2.4s Launch", "desc": "AWD torque vectoring launch control"},
                    {"icon": "⚡", "title": "Venturi Floor", "desc": "Ground effect suction without drag"}
                ],
                "fun_fact": [
                    "At 250 km/h, modern hypercars generate enough downforce to theoretically drive upside down on a tunnel ceiling!",
                    "Carbon ceramic brakes run so hot under track abuse that they glow bright orange in pitch black night runs.",
                    "F1 and hypercar tires operate with optimal grip only when preheated to exactly 100°C."
                ]
            }
        ]
    },

    "oddly_satisfying_craft": {
        "theme_name": "ODDLY SATISFYING & KINETIC PHYSICS",
        "badge_tag": "MATERIAL PRECISION & SCIENCE",
        "search_term": "satisfying kinetic sand fluid dynamics macro art",
        "topics": [
            {
                "slug": "non_newtonian_fluids",
                "title": "Oobleck: The Liquid That Turns Solid",
                "latin": "Shear-Thickening Non-Newtonian Viscosity",
                "badge": "FLUID DYNAMICS ODDITY",
                "image_url": "https://images.unsplash.com/photo-1541701494587-cb58502866ab?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "100x",
                "stat_primary_label": "Instant Viscosity Surge",
                "stat_secondary": "2:1",
                "stat_secondary_label": "Cornstarch to Water Ratio",
                "cards": [
                    {"label": "01. Shear-Thickening Physics", "text": "Low impact flows like water; sudden force locks starch particles into an unyielding solid."},
                    {"label": "02. Running on Liquid", "text": "Rapid human foot strikes exert enough shear stress to run across an entire pool of Oobleck."},
                    {"label": "03. Subwoofer Dance Patterns", "text": "Placed on a bass speaker, sound vibrations create surreal walking fluid fingers."},
                    {"label": "04. Body Armor Research", "text": "Modern military engineers study shear-thickening fluids for flexible liquid body armor."}
                ],
                "callouts": [
                    {"label": "Suspension Particles", "text": "Microscopic starch granules remain suspended without fully dissolving into water."},
                    {"label": "Capillary Lubrication", "text": "Gentle movement allows water molecules to lubricate and glide past starch chains."},
                    {"label": "Hydrodynamic Jamming", "text": "Sudden force expels water from between particles, causing friction lockup."},
                    {"label": "Shear Relaxation", "text": "Once pressure is removed, water flows back between grains, returning to liquid state."},
                    {"label": "Acoustic Standing Waves", "text": "Frequency excitation creates strange solitary wave fingers that defy gravity."},
                    {"label": "Impact Energy Absorption", "text": "Disperses projectile kinetic energy laterally across millions of micro-granules."}
                ],
                "shelf_specs": [
                    {"icon": "💧", "title": "Non-Newtonian", "desc": "Viscosity changes with applied shear stress"},
                    {"icon": "🏃", "title": "Run on Water", "desc": "Rapid footsteps lock particles into solid"},
                    {"icon": "🔊", "title": "Bass Dance", "desc": "Subwoofer soundwaves sprout liquid fingers"},
                    {"icon": "🛡️", "title": "Liquid Armor", "desc": "Stiffens instantly upon projectile impact"},
                    {"icon": "🧪", "title": "2:1 Ratio", "desc": "Pure cornstarch suspended in water"}
                ],
                "fun_fact": [
                    "You can literally run and jump across a swimming pool filled with Oobleck without sinking!",
                    "If you stop moving for just half a second, you will immediately sink into the liquid like quicksand.",
                    "Liquid armor utilizing shear-thickening technology stays flexible until struck by high-velocity shrapnel."
                ]
            }
        ]
    },

    "wilderness_bushcraft_survival": {
        "theme_name": "BUSHCRAFT & WILDERNESS SURVIVAL",
        "badge_tag": "PRIMITIVE SKILLS & WILDERNESS EXPEDITION",
        "search_term": "bushcraft wilderness survival fire camp woodcraft",
        "topics": [
            {
                "slug": "bow_drill_friction_fire",
                "title": "Bow Drill: Primitive Friction Fire",
                "latin": "Thermodynamics of Wood Friction & Coal Ignition",
                "badge": "SURVIVAL MASTERCLASS",
                "image_url": "https://images.unsplash.com/photo-1510312305653-8ed496efae75?w=900&auto=format&fit=crop&q=80",
                "stat_primary": "425°C",
                "stat_primary_label": "Ember Ignition Temp",
                "stat_secondary": "90s",
                "stat_secondary_label": "Typical Coal Generation Time",
                "cards": [
                    {"label": "01. Wood Selection Pairing", "text": "Softwoods like cedar, basswood, or willow generate ideal dark insulating wood dust."},
                    {"label": "02. The V-Shaped Notch", "text": "A 45-degree pie slice cut into the hearthboard channels fine wood dust into a pile."},
                    {"label": "03. Downward Hand Bearing", "text": "Stone or lubricated hardwood handhold reduces upper friction while maximizing base heat."},
                    {"label": "04. Oxygen Tincture Breath", "text": "Gentle, rhythmic breathing blows the glowing micro-coal into a blazing tinder flame."}
                ],
                "callouts": [
                    {"label": "Hearthboard Notch", "text": "45° pie wedge cut nearly to center traps black wood dust until it reaches 425°C."},
                    {"label": "Straight Spindle Rod", "text": "Thumb-thick dry cedar dowel rounded at top and blunt at friction base."},
                    {"label": "Curved Bow Tension", "text": "Natural branch strung with 550 paracord wrapped once around center spindle."},
                    {"label": "Low-Friction Handhold", "text": "Greased socket bearing prevents top spindle heat from scorching palm."},
                    {"label": "Fibrous Tinder Nest", "text": "Buffed jute twine or dry inner cedar bark cradles coal until oxygen ignites flame."},
                    {"label": "Dark Charcoal Dust", "text": "Sign that wood has reached pyrolysis phase and is moments away from producing an ember."}
                ],
                "shelf_specs": [
                    {"icon": "🔥", "title": "425°C Ember", "desc": "Ignition achieved via raw wood friction"},
                    {"icon": "🪵", "title": "Cedar Spindle", "desc": "Thumb-thick dry dowel spins in notch"},
                    {"icon": "🏹", "title": "Cord Bow", "desc": "Rhythmic bow strokes generate coal in 90s"},
                    {"icon": "🪨", "title": "Handhold Socket", "desc": "Greased stone prevents top palm friction"},
                    {"icon": "🌬️", "title": "Oxygen Breath", "desc": "Gentle draft blows ember into flame"}
                ],
                "fun_fact": [
                    "A successful bow drill ember glows at over 400°C without any match, flint, or chemical lighter!",
                    "Ancient fire makers carried dry tinder fungus (Chaga) because it can hold a glowing ember for hours.",
                    "If your wood dust is brown, you are moving too fast with too little pressure; it must turn pitch black!"
                ]
            }
        ]
    }
}


# =========================================================================
# 5. VIRAL HOOK FORMULAS & TRENDING HASHTAG ARCHITECTURE
# =========================================================================

VIRAL_HOOK_TEMPLATES = [
    "🔥 SHOCKING TRUTH: The Secret Blueprint of {title} Explained!",
    "⚡ DID YOU KNOW? 99% Of People Have No Idea How {title} Actually Works!",
    "🧠 MIND-BLOWING MASTERCLASS: The Untold Genius of {title}!",
    "🚨 RECORD ALERT: Extreme Facts & Hidden Records of {title}!",
    "💎 THE UNTOLD STORY: Why {title} Is Completely Fascinating!",
    "🎨 HYPER-DETAILED BREAKDOWN: Step-by-Step Science of {title}!",
    "⚠️ DO NOT MISS: Fascinating Records & Anatomy of {title}!"
]

VERTICAL_TRENDING_HASHTAGS = {
    "miniature_diorama_disaster": [
        "#miniature", "#diorama", "#miniatureworld", "#scalemodel", "#resinart", "#macrocraft",
        "#scratchbuild", "#modelmaking", "#tinyworld", "#scale87", "#hyperrealistic"
    ],
    "pet_owls_birds": [
        "#owl", "#birdtok", "#owlsoftiktok", "#raptor", "#wildlifephotography", "#naturelovers",
        "#birdsofprey", "#barnowl", "#animalfacts", "#audubon"
    ],
    "huskies_canine_psychology": [
        "#husky", "#siberianhusky", "#huskylife", "#dogpsychology", "#caninebehavior",
        "#workingdog", "#doglovers", "#puppylove", "#arcticdog"
    ],
    "humanity_and_good_deeds": [
        "#humanity", "#kindness", "#faithinhumanity", "#gooddeeds", "#inspiringstories",
        "#wholesome", "#actsofkindness", "#hero", "#positivevibes"
    ],
    "wildlife_apex_predators": [
        "#wildlife", "#apexpredator", "#tiger", "#bigcats", "#safari", "#animalplanet",
        "#wildlifeonearth", "#predator", "#naturegeography", "#natgeo"
    ],
    "ancient_empires": [
        "#ancienthistory", "#romanempire", "#historybuff", "#archaeology", "#ancientrome",
        "#historicalfacts", "#gladiators", "#historylovers", "#ancientworld"
    ],
    "dragons_and_fantasy_lore": [
        "#fantasylore", "#mythology", "#dragons", "#dnd", "#worldbuilding", "#mythicalcreatures",
        "#epicfantasy", "#folklore", "#conceptart"
    ],
    "football_legends": [
        "#football", "#soccer", "#footballskills", "#cr7", "#messi", "#tactics",
        "#championsleague", "#footballhistory", "#legendarygoals"
    ],
    "ocean_marine_life": [
        "#oceanlife", "#marinebiology", "#deepsea", "#underwater", "#oceanconservation",
        "#sealife", "#whales", "#sharks", "#blueplanet"
    ],
    "science_engineering_wonders": [
        "#science", "#engineering", "#physics", "#innovation", "#stem", "#techmarvels",
        "#spaceexploration", "#scientificfacts", "#technology"
    ],
    "supercars_and_hypercars": [
        "#supercars", "#hypercars", "#carspotting", "#automotive", "#carsofinstagram",
        "#v8engine", "#exoticcars", "#horsepower", "#twinturbo"
    ],
    "oddly_satisfying_craft": [
        "#satisfying", "#oddlysatisfying", "#asmr", "#woodworking", "#craftsmanship",
        "#satisfyingvideos", "#artisan", "#maker", "#handmade"
    ],
    "wilderness_bushcraft_survival": [
        "#bushcraft", "#survival", "#wildernessculture", "#survivalgear", "#campinglife",
        "#primitive", "#outdoorsurvival", "#offgrid", "#knifeskills"
    ]
}

GLOBAL_VIRAL_TAGS = ["#DailyFacts", "#Infographic", "#ViralReels", "#ExplorePage", "#FYP", "#TrendingNow", "#DidYouKnow"]

# -------------------------------------------------------------------------
# Dynamic Hydration: Hydrate all 13 canonical fleet verticals from topic bank
# -------------------------------------------------------------------------
try:
    _bank_file = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data", "photorealistic_topic_bank.json")
    if os.path.exists(_bank_file):
        with open(_bank_file, "r", encoding="utf-8") as _bf:
            _bdata = json.load(_bf)
            if "verticals" in _bdata:
                for _vk, _vtopics in _bdata["verticals"].items():
                    if _vk not in AUTHENTIC_VERTICAL_DATA:
                        AUTHENTIC_VERTICAL_DATA[_vk] = {
                            "theme_name": _vk.upper().replace("_", " "),
                            "badge_tag": f"{_vk.upper().replace('_', ' ')} MASTERY",
                            "search_term": _vtopics[0].get("search_term", "authentic photography 8k"),
                            "topics": _vtopics
                        }
                    else:
                        AUTHENTIC_VERTICAL_DATA[_vk]["topics"] = _vtopics
                    
                    if _vtopics and "image_url" in _vtopics[0]:
                        AUTHENTIC_VERTICAL_FALLBACKS[_vk] = _vtopics[0]["image_url"]

    # Bi-directional aliases for complete backwards compatibility
    _aliases = {
        "huskies_canine_psychology": "husky_and_puppies",
        "husky_and_puppies": "huskies_canine_psychology",
        "football_legends": "football_legends_stories",
        "football_legends_stories": "football_legends",
        "ancient_empires": "ancient_empires_history",
        "ancient_empires_history": "ancient_empires",
        "oddly_satisfying_craft": "slimes_and_mini_asmr",
        "slimes_and_mini_asmr": "oddly_satisfying_craft"
    }
    for _k1, _k2 in _aliases.items():
        if _k2 in AUTHENTIC_VERTICAL_DATA and _k1 not in AUTHENTIC_VERTICAL_DATA:
            AUTHENTIC_VERTICAL_DATA[_k1] = AUTHENTIC_VERTICAL_DATA[_k2]
        if _k2 in AUTHENTIC_VERTICAL_FALLBACKS and _k1 not in AUTHENTIC_VERTICAL_FALLBACKS:
            AUTHENTIC_VERTICAL_FALLBACKS[_k1] = AUTHENTIC_VERTICAL_FALLBACKS[_k2]
except Exception as _e:
    logger.warning(f"Engine vertical hydration notice: {_e}")


class InfographicEngine:
    """
    Next-Gen Multi-Style Generative Infographic Engine:
    - 12 Distinct Template Archetypes (Multicolor Grid, Pointers, Field Guide, Canva, Bento, Cinematic,
      Split VS Comparison, Timeline Roadmap, Radar Pie Wheel, Classified Dossier, Polaroid Scrapbook, Cyber Blueprint).
    - 6 Rotating Visual Art Styles (Pixar 3D, Ghibli, 2D Vector, 8K Photo, Cyberpunk, Lithograph).
    - 6 Vibrant Multi-Color Palettes.
    - 100% Niche Isolated across all 13 Fleet Verticals.
    - Headless Chromium (Playwright) vector rendering at 1080x1350 Full HD.
    """

    def __init__(self, cache_dir: str = "temp/infographic_cache"):
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

    def fetch_image_with_art_style(
        self,
        topic: Dict[str, Any],
        search_term: str,
        art_style_key: str,
        vertical_key: str = "miniature_diorama_disaster"
    ) -> Tuple[str, str]:
        """
        Retrieves image matching the specific art style (Pixar 3D, Ghibli, 2D Vector, 8K Photo, etc.).
        Returns (image_file_path_or_url, art_style_label).
        """
        art_meta = ART_STYLES.get(art_style_key, ART_STYLES["national_geographic_8k"])
        slug = topic.get("slug", "default")
        cache_key = hashlib.md5(f"{slug}_{art_style_key}".encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.jpg")

        if os.path.exists(cache_file) and os.path.getsize(cache_file) > 10000:
            return os.path.abspath(cache_file).replace("\\", "/"), art_meta["label"]

        full_prompt = f"{topic['title']}, {search_term}, {art_meta['prompt_suffix']}"
        encoded_prompt = requests.utils.quote(full_prompt)
        poll_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=1000&nologo=true"

        try:
            res = requests.get(poll_url, timeout=18)
            if res.status_code == 200 and len(res.content) > 10000:
                with open(cache_file, "wb") as f:
                    f.write(res.content)
                return os.path.abspath(cache_file).replace("\\", "/"), art_meta["label"]
        except Exception as e:
            logger.warning(f"Error fetching AI image for {slug} ({art_style_key}): {e}")

        direct_url = topic.get("image_url")
        if direct_url:
            return direct_url, art_meta["label"]

        fallback_url = AUTHENTIC_VERTICAL_FALLBACKS.get(vertical_key, AUTHENTIC_VERTICAL_FALLBACKS["miniature_diorama_disaster"])
        return fallback_url, art_meta["label"]

    # -------------------------------------------------------------------------
    # 12 HTML TEMPLATE BUILDERS
    # -------------------------------------------------------------------------

    
    def _build_photorealistic_viral_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_data_uri: str, art_label: str) -> str:
        """Template 0: 100% Real High-Definition Full-Bleed Photography + Short Curiosity Hook."""
        chips = topic.get("chips", [])
        if not chips and topic.get("cards"):
            chips = [f"⚡ {c['label']}: {c['text'][:25]}" for c in topic["cards"][:3]]
        if not chips:
            chips = ["⚡ 100% Authentic Capture", "👁️ National Geographic Style", "🔥 Real World Phenomenon"]

        chips_html = "".join([f'<div class="fact-chip">{c}</div>' for c in chips[:3]])
        headline = topic.get("title", "WAIT TILL YOU SEE THIS... 😱").upper()
        subtitle = topic.get("subtitle", topic.get("latin", "Fascinating natural phenomenon captured in ultra-high resolution."))

        return f"""<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <style>
        @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@800;900&family=Inter:wght@500;600;700&display=swap');
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            width: 1080px;
            height: 1350px;
            background: #000000;
            font-family: 'Inter', sans-serif;
            overflow: hidden;
            position: relative;
        }}
        .bg-photo {{
            position: absolute;
            top: 0;
            left: 0;
            width: 1080px;
            height: 1350px;
            object-fit: cover;
            object-position: center;
        }}
        .vignette-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            background: linear-gradient(
                180deg,
                rgba(0, 0, 0, 0.72) 0%,
                rgba(0, 0, 0, 0.12) 35%,
                rgba(0, 0, 0, 0.35) 60%,
                rgba(0, 0, 0, 0.94) 100%
            );
        }}
        .top-container {{
            position: absolute;
            top: 48px;
            left: 48px;
            right: 48px;
            z-index: 10;
        }}
        .brand-row {{
            display: flex;
            align-items: center;
            gap: 12px;
            margin-bottom: 20px;
        }}
        .brand-badge {{
            background: rgba(255, 255, 255, 0.16);
            backdrop-filter: blur(16px);
            border: 1px solid rgba(255, 255, 255, 0.28);
            padding: 8px 18px;
            border-radius: 40px;
            display: inline-flex;
            align-items: center;
            gap: 8px;
            color: #ffffff;
            font-size: 14px;
            font-weight: 700;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .brand-check {{
            background: #38bdf8;
            color: #000;
            width: 18px;
            height: 18px;
            border-radius: 50%;
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 11px;
            font-weight: 900;
        }}
        .nature-tag {{
            background: rgba(56, 189, 248, 0.2);
            border: 1px solid rgba(56, 189, 248, 0.45);
            color: #38bdf8;
            font-size: 12px;
            font-weight: 800;
            padding: 6px 14px;
            border-radius: 20px;
            letter-spacing: 0.5px;
            text-transform: uppercase;
        }}
        .main-headline {{
            font-family: 'Montserrat', sans-serif;
            font-size: 50px;
            font-weight: 900;
            color: #ffffff;
            line-height: 1.15;
            letter-spacing: -0.5px;
            text-shadow: 0 4px 24px rgba(0, 0, 0, 0.95);
            max-width: 960px;
        }}
        .bottom-card {{
            position: absolute;
            bottom: 48px;
            left: 48px;
            right: 48px;
            z-index: 10;
            background: rgba(15, 23, 42, 0.75);
            backdrop-filter: blur(24px);
            border: 1px solid rgba(255, 255, 255, 0.18);
            border-radius: 24px;
            padding: 30px 36px;
            box-shadow: 0 20px 50px rgba(0, 0, 0, 0.6);
        }}
        .subtitle-text {{
            font-size: 22px;
            font-weight: 600;
            color: #f1f5f9;
            line-height: 1.45;
            margin-bottom: 22px;
            text-shadow: 0 2px 10px rgba(0, 0, 0, 0.5);
        }}
        .chips-row {{
            display: flex;
            gap: 12px;
            flex-wrap: wrap;
            margin-bottom: 18px;
        }}
        .fact-chip {{
            background: rgba(255, 255, 255, 0.08);
            border: 1px solid rgba(255, 255, 255, 0.18);
            color: #38bdf8;
            font-size: 15px;
            font-weight: 700;
            padding: 9px 18px;
            border-radius: 14px;
            letter-spacing: 0.3px;
        }}
        .footer-cta {{
            display: flex;
            justify-content: space-between;
            align-items: center;
            border-top: 1px solid rgba(255, 255, 255, 0.1);
            padding-top: 14px;
            font-size: 14px;
            color: #94a3b8;
            font-weight: 600;
        }}
        .cta-left {{
            color: #cbd5e1;
        }}
        .cta-right {{
            color: #38bdf8;
            font-weight: 800;
            letter-spacing: 0.5px;
        }}
    </style>
</head>
<body>
    <img src="{image_data_uri}" class="bg-photo" alt="Real High Definition Photo">
    <div class="vignette-overlay"></div>

    <div class="top-container">
        <div class="brand-row">
            <div class="brand-badge">
                <span>{page_name}</span>
                <span class="brand-check">✓</span>
            </div>
            <div class="nature-tag">📷 8K REAL CAPTURE</div>
        </div>
        <div class="main-headline">{headline}</div>
    </div>

    <div class="bottom-card">
        <div class="subtitle-text">{subtitle}</div>
        <div class="chips-row">
            {chips_html}
        </div>
        <div class="footer-cta">
            <span class="cta-left">Did you know this before? Tell us below! 👇</span>
            <span class="cta-right">SHARE & FOLLOW ↗</span>
        </div>
    </div>
</body>
</html>"""

    def _build_vibrant_multicolor_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 1: 4 Colored Stat Cards + 5-Pill Color Shelf (Ref 4 & 5)."""
        cards = topic.get("cards", [])
        stat_colors = theme.get("stat_colors", ["#f97316", "#10b981", "#8b5cf6", "#f43f5e"])
        shelf_colors = theme.get("shelf_colors", ["#16a34a", "#0284c7", "#d97706", "#475569", "#db2777"])

        stat_cards_html = ""
        sample_badges = ["87%", "24h", "0.1", "3x"]
        for idx in range(min(4, len(cards))):
            c = cards[idx]
            color = stat_colors[idx % len(stat_colors)]
            badge = sample_badges[idx]
            stat_cards_html += f"""
            <div class="stat-card" style="background: {color};">
                <div class="stat-badge">{badge}</div>
                <div class="stat-content">
                    <h4>{c['label']}</h4>
                    <p>{c['text']}</p>
                </div>
            </div>
            """

        shelf_specs = topic.get("shelf_specs", [
            {"icon": "⚡", "title": "Precision", "desc": "Highest grade execution"},
            {"icon": "🔬", "title": "Tested", "desc": "Validated under micro specs"},
            {"icon": "🌟", "title": "Record", "desc": "Top tier benchmarks"},
            {"icon": "🛡️", "title": "Durable", "desc": "Engineered for longevity"},
            {"icon": "🎯", "title": "Focus", "desc": "Laser targeted adaptation"}
        ])

        shelf_html = ""
        for idx in range(min(5, len(shelf_specs))):
            s = shelf_specs[idx]
            color = shelf_colors[idx % len(shelf_colors)]
            shelf_html += f"""
            <div class="shelf-pill" style="background: {color};">
                <div class="icon">{s['icon']}</div>
                <div class="p-title">{s['title']}</div>
                <div class="p-desc">{s['desc']}</div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Fredoka:wght@600;700&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    width: 1080px; height: 1350px;
                    background: {theme.get('bg_gradient', 'linear-gradient(135deg, #7ea8be 0%, #a2c4d6 100%)')};
                    font-family: 'Outfit', sans-serif; color: {theme['text_main']};
                    overflow: hidden; position: relative; padding: 40px;
                }}
                .top-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }}
                .brand-pill {{ background: #ffffff; padding: 10px 22px; border-radius: 30px; display: flex; align-items: center; gap: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.08); }}
                .brand-name {{ font-family: 'Fredoka', sans-serif; font-size: 20px; font-weight: 700; color: #0f172a; }}
                .badge-verified {{ background: {theme['accent_secondary']}; color: #ffffff; font-size: 11px; font-weight: 800; padding: 3px 8px; border-radius: 12px; text-transform: uppercase; }}
                .follow-pill {{ background: {theme['accent']}; color: #ffffff; font-size: 15px; font-weight: 800; padding: 10px 24px; border-radius: 30px; text-transform: uppercase; letter-spacing: 1px; box-shadow: 0 4px 15px rgba(0,0,0,0.15); }}
                .title-banner {{ font-family: 'Fredoka', sans-serif; font-size: 46px; font-weight: 700; color: {theme['text_main']}; line-height: 1.1; text-transform: uppercase; }}
                .subtitle {{ font-size: 19px; font-weight: 600; color: {theme['text_sub']}; margin-top: 6px; }}
                .main-grid {{ display: grid; grid-template-columns: 560px 1fr; gap: 25px; height: 780px; margin-top: 25px; }}
                .hero-card {{ background: {theme['card_bg']}; border-radius: 28px; padding: 20px; box-shadow: 0 15px 35px rgba(0,0,0,0.12); display: flex; flex-direction: column; position: relative; }}
                .hero-img-wrap {{ flex: 1; border-radius: 20px; overflow: hidden; position: relative; }}
                .hero-img-wrap img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .art-style-tag {{ position: absolute; top: 15px; left: 15px; background: rgba(0,0,0,0.78); backdrop-filter: blur(8px); color: #facc15; font-size: 13px; font-weight: 800; padding: 6px 14px; border-radius: 20px; text-transform: uppercase; }}
                .hero-caption {{ margin-top: 16px; background: rgba(0,0,0,0.04); border-radius: 16px; padding: 16px 20px; }}
                .hero-caption h3 {{ font-size: 20px; font-weight: 800; color: {theme['text_main']}; margin-bottom: 4px; }}
                .hero-caption p {{ font-size: 14px; line-height: 1.45; color: {theme['text_muted']}; }}
                .stats-col {{ display: flex; flex-direction: column; gap: 16px; }}
                .stat-card {{ border-radius: 20px; padding: 20px; color: #ffffff; box-shadow: 0 8px 25px rgba(0,0,0,0.1); display: flex; align-items: center; gap: 18px; }}
                .stat-badge {{ width: 75px; height: 75px; border-radius: 18px; background: rgba(255,255,255,0.25); display: flex; align-items: center; justify-content: center; font-family: 'Fredoka', sans-serif; font-size: 28px; font-weight: 700; flex-shrink: 0; }}
                .stat-content h4 {{ font-size: 18px; font-weight: 800; margin-bottom: 4px; text-transform: uppercase; }}
                .stat-content p {{ font-size: 13px; line-height: 1.4; opacity: 0.95; }}
                .bottom-shelf {{ margin-top: 25px; display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; }}
                .shelf-pill {{ border-radius: 18px; padding: 16px 14px; text-align: center; color: #ffffff; box-shadow: 0 6px 20px rgba(0,0,0,0.08); }}
                .shelf-pill .icon {{ font-size: 26px; margin-bottom: 6px; }}
                .shelf-pill .p-title {{ font-size: 14px; font-weight: 800; text-transform: uppercase; margin-bottom: 3px; }}
                .shelf-pill .p-desc {{ font-size: 11px; line-height: 1.3; opacity: 0.9; }}
                .footer-bar {{ margin-top: 20px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; font-weight: 700; color: {theme['text_sub']}; }}
            </style>
        </head>
        <body>
            <div class="top-bar">
                <div class="brand-pill"><span style="font-size: 22px;">🐾</span><span class="brand-name">{page_name.upper()}</span><span class="badge-verified">✔ VERIFIED</span></div>
                <div class="follow-pill">+ FOLLOW @{page_name.upper()}</div>
            </div>
            <div>
                <h1 class="title-banner">{topic['title']}</h1>
                <div class="subtitle">{topic.get('latin', v_data['badge_tag'])}</div>
            </div>
            <div class="main-grid">
                <div class="hero-card">
                    <div class="hero-img-wrap"><img src="{image_path}" /><div class="art-style-tag">{art_label}</div></div>
                    <div class="hero-caption"><h3>{topic['title']}</h3><p>{cards[0]['text'] if cards else 'Authentic specialized masterclass techniques.'}</p></div>
                </div>
                <div class="stats-col">{stat_cards_html}</div>
            </div>
            <div class="bottom-shelf">{shelf_html}</div>
            <div class="footer-bar"><div>{page_name.upper()} • {v_data['theme_name']}</div><div style="color: {theme['accent']};">SWIPE FOR MORE PRO TIPS ➔</div></div>
        </body>
        </html>
        """

    def _build_anatomical_pointer_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 2: Anatomical Callout Pointer Layout with SVG Connecting Lines (Ref 3)."""
        callouts = topic.get("callouts", [
            {"label": "PRIMARY ADAPTATION", "text": "Engineered for supreme survival in extreme conditions."},
            {"label": "RAPID SPRINT REFLEX", "text": "Micro-second synaptic responses optimize hunting efficiency."},
            {"label": "DURABLE SKELETAL FRAME", "text": "Specialized anatomy absorbs massive compressive impact forces."},
            {"label": "SENSORY TRIANGULATION", "text": "Multi-spectrum perception allows 3D sound and sight mapping."},
            {"label": "THERMAL REGULATION", "text": "Maintains biological equilibrium across volatile climate shifts."},
            {"label": "LETHAL STRIKE CONTACT", "text": "Delivers immense focused force with surgical precision."}
        ])[:6]

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@700;900&family=Outfit:wght@400;600;700;800&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    width: 1080px; height: 1350px;
                    background: radial-gradient(circle at 50% 45%, {theme['canvas_bg']} 0%, #050a12 100%);
                    font-family: 'Outfit', sans-serif; color: #ffffff;
                    overflow: hidden; position: relative;
                }}
                .header {{ text-align: center; padding-top: 45px; position: relative; z-index: 10; }}
                .pill-tag {{ display: inline-block; background: rgba(255, 255, 255, 0.08); border: 1px solid {theme['accent']}; color: {theme['accent']}; padding: 6px 18px; border-radius: 20px; font-size: 14px; font-weight: 800; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 12px; }}
                .title {{ font-family: 'Cinzel', serif; font-size: 44px; font-weight: 900; letter-spacing: 1.5px; color: #ffffff; text-transform: uppercase; }}
                .subtitle {{ font-size: 18px; color: #cbd5e1; letter-spacing: 1px; margin-top: 6px; }}
                .stage-container {{ position: absolute; top: 220px; left: 0; right: 0; bottom: 120px; }}
                .central-subject {{ position: absolute; top: 50%; left: 50%; transform: translate(-50%, -50%); width: 440px; height: 520px; border-radius: 24px; overflow: hidden; box-shadow: 0 20px 50px rgba(0,0,0,0.6), 0 0 40px {theme['accent']}40; border: 2px solid {theme['accent']}; z-index: 5; }}
                .central-subject img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .art-tag-pointer {{ position: absolute; bottom: 15px; left: 15px; background: rgba(0,0,0,0.85); color: {theme['accent']}; font-size: 12px; font-weight: 800; padding: 5px 12px; border-radius: 14px; z-index: 6; }}
                .callout-card {{ position: absolute; width: 280px; background: {theme['card_bg']}; backdrop-filter: blur(16px); border: 1px solid {theme['card_border']}; border-radius: 12px; padding: 14px 16px; box-shadow: 0 8px 24px rgba(0,0,0,0.4); z-index: 10; }}
                .callout-card h4 {{ font-size: 15px; font-weight: 800; color: {theme['accent']}; letter-spacing: 0.5px; text-transform: uppercase; margin-bottom: 5px; }}
                .callout-card p {{ font-size: 13px; line-height: 1.4; color: #e2e8f0; }}
                .pos-tl {{ top: 40px; left: 45px; }} .pos-ml {{ top: 290px; left: 35px; }} .pos-bl {{ bottom: 50px; left: 45px; }}
                .pos-tr {{ top: 40px; right: 45px; }} .pos-mr {{ top: 290px; right: 35px; }} .pos-br {{ bottom: 50px; right: 45px; }}
                .pointers-svg {{ position: absolute; inset: 0; width: 100%; height: 100%; pointer-events: none; z-index: 8; }}
                .footer-bar {{ position: absolute; bottom: 28px; left: 45px; right: 45px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid rgba(255,255,255,0.1); padding-top: 14px; font-size: 14px; color: #94a3b8; font-weight: 600; }}
            </style>
        </head>
        <body>
            <div class="header">
                <div class="pill-tag">{topic.get('badge', v_data['badge_tag'])}</div>
                <h1 class="title">{topic['title']}</h1>
                <div class="subtitle">{topic.get('latin', v_data['theme_name'])}</div>
            </div>
            <div class="stage-container">
                <svg class="pointers-svg" viewBox="0 0 1080 1010">
                    <path d="M 325 110 L 420 180 L 460 260" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" /><circle cx="460" cy="260" r="5" fill="{theme['accent']}" />
                    <path d="M 315 360 L 410 380 L 440 370" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" /><circle cx="440" cy="370" r="5" fill="{theme['accent']}" />
                    <path d="M 325 800 L 410 740 L 460 670" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" /><circle cx="460" cy="670" r="5" fill="{theme['accent']}" />
                    <path d="M 755 110 L 660 170 L 620 250" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" /><circle cx="620" cy="250" r="5" fill="{theme['accent']}" />
                    <path d="M 765 360 L 670 420 L 640 450" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" /><circle cx="640" cy="450" r="5" fill="{theme['accent']}" />
                    <path d="M 755 800 L 670 730 L 620 660" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" /><circle cx="620" cy="660" r="5" fill="{theme['accent']}" />
                </svg>
                <div class="central-subject"><img src="{image_path}" /><div class="art-tag-pointer">{art_label}</div></div>
                <div class="callout-card pos-tl"><h4>{callouts[0]['label']}</h4><p>{callouts[0]['text']}</p></div>
                <div class="callout-card pos-ml"><h4>{callouts[1]['label']}</h4><p>{callouts[1]['text']}</p></div>
                <div class="callout-card pos-bl"><h4>{callouts[2]['label']}</h4><p>{callouts[2]['text']}</p></div>
                <div class="callout-card pos-tr"><h4>{callouts[3]['label']}</h4><p>{callouts[3]['text']}</p></div>
                <div class="callout-card pos-mr"><h4>{callouts[4]['label']}</h4><p>{callouts[4]['text']}</p></div>
                <div class="callout-card pos-br"><h4>{callouts[5]['label']}</h4><p>{callouts[5]['text']}</p></div>
            </div>
            <div class="footer-bar"><div>{page_name.upper()} • {v_data['theme_name']}</div><div style="color: {theme['accent']}; font-weight: 700;">FOLLOW @{page_name.upper()} FOR DAILY DOSSIERS</div></div>
        </body>
        </html>
        """

    def _build_vintage_fieldguide_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 3: Vintage Naturalist / Field Guide Specimen Archive (Ref 1)."""
        cards_html = "".join([f'<div class="spec-card"><div class="spec-title">{c["label"]}</div><div class="spec-desc">{c["text"]}</div></div>' for c in topic.get("cards", [])[:4]])
        facts_html = "".join([f'<li>{f}</li>' for f in topic.get("fun_fact", [])[:3]])

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Outfit:wght@300;400;600;700;800&family=Playfair+Display:ital,wght@0,600;0,800;1,400&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background-color: #fbf8f1; font-family: 'Outfit', sans-serif; color: #18281e; overflow: hidden; position: relative; }}
                .border-frame {{ position: absolute; top: 24px; left: 24px; right: 24px; bottom: 24px; border: 2px solid #d4cbb8; pointer-events: none; }}
                .header {{ padding: 50px 60px 20px 60px; display: flex; justify-content: space-between; align-items: flex-start; }}
                .header-left h1 {{ font-family: 'Playfair Display', serif; font-size: 46px; font-weight: 800; color: #18281e; text-transform: uppercase; }}
                .header-left .latin {{ font-family: 'Playfair Display', serif; font-style: italic; font-size: 24px; color: #735338; margin-top: 6px; }}
                .badge-box {{ background: #18281e; color: #fbf8f1; padding: 10px 18px; border-radius: 8px; font-size: 14px; font-weight: 800; text-transform: uppercase; }}
                .content-grid {{ display: grid; grid-template-columns: 460px 1fr; gap: 36px; padding: 10px 60px 40px 60px; height: 1060px; }}
                .left-col {{ display: flex; flex-direction: column; gap: 16px; }}
                .spec-card {{ background: rgba(255, 255, 255, 0.88); border: 1px solid #e2dac9; border-left: 5px solid #d97706; padding: 16px 20px; border-radius: 10px; }}
                .spec-title {{ font-size: 15px; font-weight: 800; color: #d97706; text-transform: uppercase; margin-bottom: 5px; }}
                .spec-desc {{ font-size: 16px; line-height: 1.45; color: #4a5d4e; }}
                .did-you-know {{ background: rgba(230, 220, 205, 0.45); border: 1px dashed #d4cbb8; border-radius: 12px; padding: 18px; margin-top: auto; }}
                .did-you-know h4 {{ font-size: 15px; font-weight: 800; color: #18281e; text-transform: uppercase; margin-bottom: 8px; }}
                .did-you-know li {{ font-size: 14px; line-height: 1.4; color: #4a5d4e; margin-bottom: 6px; list-style-type: none; position: relative; padding-left: 18px; }}
                .did-you-know li::before {{ content: "•"; color: #d97706; font-weight: bold; font-size: 18px; position: absolute; left: 0; top: -2px; }}
                .photo-frame {{ border-radius: 16px; overflow: hidden; border: 3px solid #e2dac9; box-shadow: 0 12px 32px rgba(0,0,0,0.08); height: 100%; position: relative; }}
                .photo-frame img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .art-tag-field {{ position: absolute; bottom: 20px; left: 20px; background: rgba(24, 40, 30, 0.85); color: #fbf8f1; padding: 6px 14px; border-radius: 16px; font-size: 13px; font-weight: 800; }}
                .footer-strip {{ position: absolute; bottom: 34px; left: 60px; right: 60px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #d4cbb8; padding-top: 14px; font-size: 14px; font-weight: 600; color: #735338; }}
            </style>
        </head>
        <body>
            <div class="border-frame"></div>
            <div class="header">
                <div class="header-left"><h1>{topic['title']}</h1><div class="latin">{topic.get('latin', v_data['badge_tag'])}</div></div>
                <div class="badge-box">{topic.get('badge', v_data['badge_tag'])}</div>
            </div>
            <div class="content-grid">
                <div class="left-col">{cards_html}<div class="did-you-know"><h4>FIELD NATURALIST NOTES</h4><ul>{facts_html}</ul></div></div>
                <div class="photo-frame"><img src="{image_path}" /><div class="art-tag-field">{art_label}</div></div>
            </div>
            <div class="footer-strip"><div>{page_name.upper()} • {v_data['theme_name']}</div><div>FOLLOW @{page_name.upper()} FOR DAILY ARCHIVES</div></div>
        </body>
        </html>
        """

    def _build_canva_poster_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 4: Canva-Style Illustrated Nature Poster (Ref 2)."""
        cards = topic.get("cards", [])
        c1 = cards[0] if len(cards) > 0 else {"label": "PRIMARY FOCUS", "text": "Key biological / craft adaptation."}
        c2 = cards[1] if len(cards) > 1 else {"label": "CRITICAL METHOD", "text": "Advanced specialized technique."}

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;700;800;900&family=Playfair+Display:ital,wght@1,600;1,700&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background-color: {theme['canvas_bg']}; font-family: 'Montserrat', sans-serif; color: {theme['text_main']}; overflow: hidden; position: relative; }}
                .header-banner {{ text-align: center; padding-top: 45px; }}
                .header-banner h1 {{ font-size: 42px; font-weight: 900; color: {theme['accent']}; text-transform: uppercase; }}
                .header-banner .tagline {{ font-size: 18px; font-weight: 700; color: {theme['text_muted']}; letter-spacing: 2px; text-transform: uppercase; margin-top: 6px; }}
                .main-card {{ margin: 35px 50px; background: {theme['card_bg']}; border: 2px solid {theme['card_border']}; border-radius: 20px; padding: 26px; display: grid; grid-template-columns: 360px 1fr; gap: 30px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
                .subject-img {{ width: 100%; height: 520px; border-radius: 16px; overflow: hidden; border: 2px solid {theme['accent']}; position: relative; }}
                .subject-img img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .art-tag-canva {{ position: absolute; bottom: 15px; left: 15px; background: rgba(0,0,0,0.85); color: #facc15; font-size: 12px; font-weight: 800; padding: 5px 12px; border-radius: 14px; }}
                .pill-badge {{ display: inline-block; background: {theme['accent']}; color: #000; font-size: 13px; font-weight: 800; padding: 5px 14px; border-radius: 12px; text-transform: uppercase; margin-bottom: 8px; }}
                .details-col h2 {{ font-size: 32px; font-weight: 800; color: {theme['text_main']}; text-transform: uppercase; }}
                .details-col .latin {{ font-family: 'Playfair Display', serif; font-style: italic; font-size: 20px; color: {theme['accent']}; margin-bottom: 14px; }}
                .details-col p {{ font-size: 16px; line-height: 1.5; color: {theme['text_sub']}; }}
                .alert-box {{ background: rgba(0,0,0,0.25); border-left: 5px solid {theme['accent']}; border-radius: 10px; padding: 16px; margin-top: 18px; }}
                .alert-box h4 {{ font-size: 15px; font-weight: 800; color: {theme['accent']}; text-transform: uppercase; margin-bottom: 6px; }}
                .alert-box p {{ font-size: 14px; line-height: 1.4; color: {theme['text_sub']}; }}
                .lower-shelf {{ margin: 0 50px; display: grid; grid-template-columns: 1fr 1fr; gap: 20px; }}
                .shelf-card {{ background: {theme['card_bg']}; border: 1px solid {theme['card_border']}; border-radius: 16px; padding: 20px; }}
                .shelf-card h4 {{ font-size: 16px; font-weight: 800; color: {theme['accent']}; margin-bottom: 6px; text-transform: uppercase; }}
                .shelf-card p {{ font-size: 14px; line-height: 1.45; color: {theme['text_sub']}; }}
                .footer-strip {{ position: absolute; bottom: 24px; left: 50px; right: 50px; display: flex; justify-content: space-between; align-items: center; border-top: 1px solid {theme['card_border']}; padding-top: 14px; font-size: 14px; color: {theme['text_muted']}; font-weight: 700; }}
            </style>
        </head>
        <body>
            <div class="header-banner"><h1>{topic['title']}</h1><div class="tagline">{v_data['badge_tag']}</div></div>
            <div class="main-card">
                <div class="subject-img"><img src="{image_path}" /><div class="art-tag-canva">{art_label}</div></div>
                <div class="details-col">
                    <div><div class="pill-badge">{topic.get('badge', v_data['badge_tag'])}</div><h2>{topic['title']}</h2><div class="latin">{topic.get('latin', v_data['theme_name'])}</div><p>{c1['text']}</p></div>
                    <div class="alert-box"><h4>⚠️ KEY METHODOLOGY & SPECS</h4><p>{c2['text']}</p></div>
                </div>
            </div>
            <div class="lower-shelf">
                <div class="shelf-card"><h4>PRO SPECIFICATIONS</h4><p>{topic.get('fun_fact', ['Authentic verified field facts'])[0]}</p></div>
                <div class="shelf-card"><h4>FIELD DISPATCH</h4><p>{topic.get('fun_fact', ['Authentic verified field facts'])[-1]}</p></div>
            </div>
            <div class="footer-strip"><div>{page_name.upper()} • {v_data['theme_name']}</div><div style="color: {theme['accent']};">FOLLOW @{page_name.upper()} FOR DAILY DOSSIERS</div></div>
        </body>
        </html>
        """

    def _build_bento_dashboard_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 5: Modern Bento Grid Dashboard with Big Stat Meters."""
        stat1 = topic.get("stat_primary", "100%")
        stat1_lbl = topic.get("stat_primary_label", "Peak Performance Metric")
        stat2 = topic.get("stat_secondary", "0.1mm")
        stat2_lbl = topic.get("stat_secondary_label", "Micro-Engineering Precision")

        cards = topic.get("cards", [])
        c1 = cards[0] if len(cards) > 0 else {"label": "TECHNIQUE 01", "text": "Precision material calibration."}
        c2 = cards[1] if len(cards) > 1 else {"label": "TECHNIQUE 02", "text": "Dynamic chemical surface bonding."}
        c3 = cards[2] if len(cards) > 2 else {"label": "TECHNIQUE 03", "text": "Sub-surface refraction and polish."}

        pills = topic.get("fun_fact", ["Pure precision grade materials guaranteed.", "Tested under rigorous conditions.", "Verified by leading field naturalists."])[:3]

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Space+Grotesk:wght@700&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background-color: {theme['canvas_bg']}; font-family: 'Outfit', sans-serif; color: {theme['text_main']}; overflow: hidden; position: relative; padding: 40px; }}
                .header-bar {{ display: flex; justify-content: space-between; align-items: center; margin-bottom: 25px; }}
                .header-left h1 {{ font-family: 'Space Grotesk', sans-serif; font-size: 38px; font-weight: 700; text-transform: uppercase; color: {theme['text_main']}; }}
                .header-left .sub {{ color: {theme['text_muted']}; font-size: 16px; margin-top: 4px; }}
                .badge-live {{ background: {theme['accent']}; color: #000; font-size: 13px; font-weight: 800; padding: 6px 14px; border-radius: 20px; text-transform: uppercase; }}
                .bento-grid {{ display: grid; grid-template-columns: 1fr 1fr 1fr; grid-template-rows: 240px 380px 240px 180px; gap: 18px; }}
                .card {{ background: {theme['card_bg']}; border: 1px solid {theme['card_border']}; border-radius: 18px; padding: 22px; position: relative; overflow: hidden; display: flex; flex-direction: column; justify-content: space-between; }}
                .card-photo {{ grid-column: 1 / 3; grid-row: 1 / 3; padding: 0; border: 2px solid {theme['card_border']}; }}
                .card-photo img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .card-photo .overlay-tag {{ position: absolute; bottom: 20px; left: 20px; right: 20px; background: rgba(15, 23, 42, 0.85); backdrop-filter: blur(10px); border: 1px solid rgba(255,255,255,0.15); padding: 16px 20px; border-radius: 12px; }}
                .overlay-tag h3 {{ font-size: 22px; font-weight: 800; color: {theme['accent']}; margin-bottom: 4px; }}
                .overlay-tag p {{ font-size: 14px; color: #cbd5e1; }}
                .card-stat1 {{ grid-column: 3 / 4; grid-row: 1 / 2; background: {theme['card_bg']}; border-color: {theme['accent']}; }}
                .stat-number {{ font-size: 50px; font-weight: 900; color: {theme['accent']}; line-height: 1; }}
                .stat-label {{ font-size: 14px; font-weight: 700; color: {theme['text_sub']}; text-transform: uppercase; }}
                .card-stat2 {{ grid-column: 3 / 4; grid-row: 2 / 3; background: {theme['card_bg']}; border-color: {theme['accent_secondary']}; }}
                .card-stat2 .stat-number {{ color: {theme['accent_secondary']}; }}
                .card-mid1 {{ grid-column: 1 / 2; grid-row: 3 / 4; border-top: 4px solid {theme['accent']}; }}
                .card-mid2 {{ grid-column: 2 / 3; grid-row: 3 / 4; border-top: 4px solid {theme['accent_secondary']}; }}
                .card-mid3 {{ grid-column: 3 / 4; grid-row: 3 / 4; border-top: 4px solid #06b6d4; }}
                .card-tag {{ font-size: 13px; font-weight: 800; text-transform: uppercase; margin-bottom: 8px; }}
                .card h4 {{ font-size: 18px; font-weight: 800; color: {theme['text_main']}; margin-bottom: 6px; }}
                .card p {{ font-size: 14px; line-height: 1.45; color: {theme['text_muted']}; }}
                .card-bottom {{ grid-column: 1 / 4; grid-row: 4 / 5; display: flex; flex-direction: row; align-items: center; justify-content: space-between; padding: 18px 24px; background: rgba(0,0,0,0.3); border: 1px solid {theme['card_border']}; }}
                .bottom-pill {{ flex: 1; margin: 0 8px; background: {theme['card_bg']}; border-radius: 10px; padding: 12px 14px; text-align: center; border: 1px solid {theme['card_border']}; }}
                .bottom-pill .pill-val {{ font-size: 14px; font-weight: 700; color: {theme['text_sub']}; }}
                .footer-strip {{ position: absolute; bottom: 12px; left: 40px; right: 40px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; color: {theme['text_muted']}; font-weight: 600; }}
            </style>
        </head>
        <body>
            <div class="header-bar">
                <div class="header-left"><h1>{topic['title']}</h1><div class="sub">{topic.get('latin', v_data['badge_tag'])}</div></div>
                <div class="badge-live">{topic.get('badge', v_data['badge_tag'])}</div>
            </div>
            <div class="bento-grid">
                <div class="card card-photo"><img src="{image_path}" /><div class="overlay-tag"><h3>{topic['title']}</h3><p>{c1['text']}</p></div></div>
                <div class="card card-stat1"><div class="stat-number">{stat1}</div><div><div class="stat-label">{stat1_lbl}</div></div></div>
                <div class="card card-stat2"><div class="stat-number">{stat2}</div><div><div class="stat-label">{stat2_lbl}</div></div></div>
                <div class="card card-mid1"><div class="card-tag" style="color: {theme['accent']};">{c1['label']}</div><h4>{c1['label']}</h4><p>{c1['text']}</p></div>
                <div class="card card-mid2"><div class="card-tag" style="color: {theme['accent_secondary']};">{c2['label']}</div><h4>{c2['label']}</h4><p>{c2['text']}</p></div>
                <div class="card card-mid3"><div class="card-tag" style="color: #06b6d4;">{c3['label']}</div><h4>{c3['label']}</h4><p>{c3['text']}</p></div>
                <div class="card card-bottom">
                    <div class="bottom-pill"><div class="pill-val">{pills[0]}</div></div>
                    <div class="bottom-pill"><div class="pill-val">{pills[1]}</div></div>
                    <div class="bottom-pill"><div class="pill-val">{pills[2]}</div></div>
                </div>
            </div>
            <div class="footer-strip"><div>{page_name.upper()} • {v_data['theme_name']}</div><div style="color: {theme['accent']}; font-weight: 700;">FOLLOW @{page_name.upper()} FOR DAILY SECRETS</div></div>
        </body>
        </html>
        """

    def _build_cinematic_hero_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 6: NatGeo Modern Magazine Cover with Frosted Glassmorphism."""
        cards = topic.get("cards", [])
        c1 = cards[0] if len(cards) > 0 else {"label": "SPECS 01", "text": "Masterclass observation."}
        c2 = cards[1] if len(cards) > 1 else {"label": "SPECS 02", "text": "Biological efficiency."}

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Bebas+Neue&family=Outfit:wght@400;600;700;800&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background-color: #000000; font-family: 'Outfit', sans-serif; color: #ffffff; overflow: hidden; position: relative; }}
                .hero-bg {{ position: absolute; inset: 0; width: 100%; height: 100%; object-fit: cover; display: block; }}
                .gradient-mask {{ position: absolute; inset: 0; background: linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.92) 80%); }}
                .top-masthead {{ position: relative; z-index: 10; padding: 50px 60px; }}
                .category-badge {{ display: inline-block; background: {theme['accent']}; color: #000; font-size: 14px; font-weight: 800; letter-spacing: 2px; padding: 6px 16px; border-radius: 4px; text-transform: uppercase; }}
                .headline-title {{ font-family: 'Bebas Neue', sans-serif; font-size: 78px; letter-spacing: 1px; line-height: 0.95; margin-top: 14px; text-transform: uppercase; color: #ffffff; text-shadow: 0 4px 20px rgba(0,0,0,0.8); }}
                .latin-sub {{ font-size: 20px; color: {theme['accent']}; margin-top: 6px; font-weight: 600; letter-spacing: 1px; }}
                .glass-panel {{ position: absolute; bottom: 90px; left: 60px; right: 60px; background: rgba(15, 23, 42, 0.78); backdrop-filter: blur(20px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 20px; padding: 30px; display: grid; grid-template-columns: 1fr 1fr; gap: 30px; z-index: 10; box-shadow: 0 20px 50px rgba(0,0,0,0.6); }}
                .stat-box h4 {{ font-size: 18px; font-weight: 800; color: {theme['accent']}; text-transform: uppercase; margin-bottom: 8px; }}
                .stat-box p {{ font-size: 15px; line-height: 1.5; color: #e2e8f0; }}
                .footer-strip {{ position: absolute; bottom: 28px; left: 60px; right: 60px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; color: #94a3b8; font-weight: 700; z-index: 10; }}
            </style>
        </head>
        <body>
            <img class="hero-bg" src="{image_path}" />
            <div class="gradient-mask"></div>
            <div class="top-masthead">
                <div class="category-badge">{topic.get('badge', v_data['badge_tag'])}</div>
                <h1 class="headline-title">{topic['title']}</h1>
                <div class="latin-sub">{topic.get('latin', v_data['theme_name'])}</div>
            </div>
            <div class="glass-panel">
                <div class="stat-box"><h4>{c1['label']}</h4><p>{c1['text']}</p></div>
                <div class="stat-box"><h4>{c2['label']}</h4><p>{c2['text']}</p></div>
            </div>
            <div class="footer-strip"><div>{page_name.upper()} • {v_data['theme_name']}</div><div style="color: {theme['accent']};">FOLLOW @{page_name.upper()} FOR DAILY DOSSIERS</div></div>
        </body>
        </html>
        """

    def _build_split_comparison_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 7: Head-to-Head Comparative Battlecard ('THIS VS THAT')."""
        cards = topic.get("cards", [])
        c1 = cards[0] if len(cards) > 0 else {"label": "SPEC A", "text": "Ultra-precision calibration"}
        c2 = cards[1] if len(cards) > 1 else {"label": "SPEC B", "text": "Conventional execution"}
        c3 = cards[2] if len(cards) > 2 else {"label": "SPEC C", "text": "Microsecond tactical reflex"}
        c4 = cards[3] if len(cards) > 3 else {"label": "SPEC D", "text": "Resilient structural endurance"}

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Bebas+Neue&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background: {theme.get('bg_gradient', 'linear-gradient(135deg, #090d16 0%, #1a2333 100%)')}; font-family: 'Outfit', sans-serif; color: #ffffff; overflow: hidden; position: relative; padding: 40px; }}
                .vs-header {{ text-align: center; margin-bottom: 25px; }}
                .vs-title {{ font-family: 'Bebas Neue', sans-serif; font-size: 58px; letter-spacing: 2px; color: #ffffff; text-transform: uppercase; line-height: 1; }}
                .vs-sub {{ font-size: 16px; color: {theme['accent']}; font-weight: 800; text-transform: uppercase; letter-spacing: 1.5px; margin-bottom: 4px; }}
                .split-container {{ display: grid; grid-template-columns: 1fr 1fr; gap: 26px; height: 1000px; position: relative; }}
                .side-card {{ background: {theme['card_bg']}; border: 2px solid {theme['card_border']}; border-radius: 24px; padding: 22px; display: flex; flex-direction: column; justify-content: space-between; box-shadow: 0 15px 40px rgba(0,0,0,0.3); }}
                .side-card.left {{ border-top: 6px solid {theme['accent']}; }}
                .side-card.right {{ border-top: 6px solid {theme['accent_secondary']}; }}
                .side-badge {{ display: inline-block; padding: 8px 16px; border-radius: 20px; font-size: 13px; font-weight: 900; text-transform: uppercase; text-align: center; }}
                .side-card.left .side-badge {{ background: {theme['accent']}; color: #000; }}
                .side-card.right .side-badge {{ background: {theme['accent_secondary']}; color: #fff; }}
                .side-img {{ height: 300px; border-radius: 16px; overflow: hidden; margin: 14px 0; border: 2px solid rgba(255,255,255,0.1); }}
                .side-img img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .spec-row {{ background: rgba(0,0,0,0.25); border: 1px solid rgba(255,255,255,0.08); border-radius: 12px; padding: 12px 14px; margin-bottom: 10px; }}
                .spec-row h5 {{ font-size: 13px; font-weight: 800; text-transform: uppercase; margin-bottom: 3px; }}
                .spec-row p {{ font-size: 13px; line-height: 1.35; color: #cbd5e1; }}
                .summary-verdict {{ border-radius: 12px; padding: 12px 14px; font-size: 12px; font-weight: 700; text-align: center; text-transform: uppercase; letter-spacing: 0.5px; }}
                .vs-circle {{ position: absolute; top: 38%; left: 50%; transform: translate(-50%, -50%); width: 72px; height: 72px; border-radius: 50%; background: #ffffff; color: #000000; font-family: 'Bebas Neue', sans-serif; font-size: 34px; font-weight: 900; display: flex; align-items: center; justify-content: center; box-shadow: 0 0 35px rgba(255,255,255,0.9); z-index: 10; border: 4px solid {theme['accent']}; }}
                .footer-bar {{ position: absolute; bottom: 20px; left: 40px; right: 40px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; color: #94a3b8; font-weight: 700; }}
            </style>
        </head>
        <body>
            <div class="vs-header">
                <div class="vs-sub">⚡ HEAD-TO-HEAD BATTLECARD • {v_data['badge_tag']}</div>
                <h1 class="vs-title">{topic['title']}</h1>
            </div>
            <div class="split-container">
                <div class="vs-circle">VS</div>
                <div class="side-card left">
                    <div class="side-badge">PRO LEVEL SPECIFICATION</div>
                    <div class="side-img"><img src="{image_path}" /></div>
                    <div class="spec-row"><h5 style="color:{theme['accent']};">⚡ {c1['label']}</h5><p>{c1['text']}</p></div>
                    <div class="spec-row"><h5 style="color:{theme['accent']};">🎯 {c3['label']}</h5><p>{c3['text']}</p></div>
                    <div class="spec-row"><h5 style="color:{theme['accent']};">🏆 PEAK BENCHMARK</h5><p>{topic.get('stat_primary', '100%')} • {topic.get('stat_primary_label', 'Peak Output Index')}</p></div>
                    <div class="summary-verdict" style="background:{theme['accent']}25; color:{theme['accent']}; border:1px solid {theme['accent']};">
                        VERDICT: MAXIMUM RELIABILITY & EFFICIENCY
                    </div>
                </div>
                <div class="side-card right">
                    <div class="side-badge">CONVENTIONAL / BASELINE</div>
                    <div class="side-img"><img src="{image_path}" style="filter: grayscale(40%) contrast(0.9);" /></div>
                    <div class="spec-row"><h5 style="color:{theme['accent_secondary']};">⚠️ {c2['label']}</h5><p>{c2['text']}</p></div>
                    <div class="spec-row"><h5 style="color:{theme['accent_secondary']};">📉 {c4['label']}</h5><p>{c4['text']}</p></div>
                    <div class="spec-row"><h5 style="color:{theme['accent_secondary']};">⏳ BASELINE LIMIT</h5><p>{topic.get('stat_secondary', 'Standard')} • {topic.get('stat_secondary_label', 'Standard Tolerance Margin')}</p></div>
                    <div class="summary-verdict" style="background:{theme['accent_secondary']}25; color:{theme['accent_secondary']}; border:1px solid {theme['accent_secondary']};">
                        VERDICT: SUBJECT TO PERFORMANCE DEGRADATION
                    </div>
                </div>
            </div>
            <div class="footer-bar"><div>{page_name.upper()} • {v_data['theme_name']}</div><div style="color: {theme['accent']};">SWIPE FOR MORE COMPARISONS ➔</div></div>
        </body>
        </html>
        """

    def _build_timeline_roadmap_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 8: Vertical Stepped Process / Timeline Roadmap."""
        cards = topic.get("cards", [])
        milestones = [
            {"step": "01", "phase": "FOUNDATION & PREPARATION", "text": cards[0]["text"] if len(cards) > 0 else "Initial surface calibration."},
            {"step": "02", "phase": "PRIMARY EXECUTION", "text": cards[1]["text"] if len(cards) > 1 else "Direct structural application."},
            {"step": "03", "phase": "MICRO-TEXTURING & FX", "text": cards[2]["text"] if len(cards) > 2 else "Advanced layer texturing."},
            {"step": "04", "phase": "FINAL PERFECTION", "text": cards[3]["text"] if len(cards) > 3 else "Permanent sealing and validation."}
        ]

        steps_html = ""
        for m in milestones:
            steps_html += f"""
            <div class="timeline-item">
                <div class="node-circle">{m['step']}</div>
                <div class="node-content">
                    <div class="node-phase">{m['phase']}</div>
                    <div class="node-text">{m['text']}</div>
                </div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Fredoka:wght@700&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background: {theme.get('bg_gradient', 'linear-gradient(135deg, #0f172a 0%, #1e293b 100%)')}; font-family: 'Outfit', sans-serif; color: #ffffff; overflow: hidden; position: relative; padding: 45px; }}
                .header-bar {{ margin-bottom: 25px; }}
                .tag {{ display: inline-block; background: {theme['accent']}; color: #000; font-size: 13px; font-weight: 800; padding: 6px 14px; border-radius: 20px; text-transform: uppercase; margin-bottom: 8px; }}
                .title {{ font-family: 'Fredoka', sans-serif; font-size: 46px; font-weight: 700; text-transform: uppercase; }}
                .timeline-wrapper {{ display: grid; grid-template-columns: 460px 1fr; gap: 35px; height: 1000px; }}
                .left-column {{ display: flex; flex-direction: column; justify-content: space-between; }}
                .visual-side {{ height: 700px; border-radius: 24px; overflow: hidden; border: 2px solid {theme['card_border']}; position: relative; box-shadow: 0 15px 40px rgba(0,0,0,0.4); }}
                .visual-side img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .art-tag-time {{ position: absolute; bottom: 20px; left: 20px; background: rgba(0,0,0,0.85); color: {theme['accent']}; font-size: 13px; font-weight: 800; padding: 6px 14px; border-radius: 20px; }}
                .pro-callout {{ background: rgba(15, 23, 42, 0.85); border: 2px solid {theme['accent']}; border-radius: 18px; padding: 20px; box-shadow: 0 10px 30px rgba(0,0,0,0.3); }}
                .pro-callout h4 {{ font-size: 14px; font-weight: 800; color: {theme['accent']}; text-transform: uppercase; margin-bottom: 6px; }}
                .pro-callout p {{ font-size: 13px; line-height: 1.45; color: #cbd5e1; }}
                .timeline-col {{ display: flex; flex-direction: column; justify-content: space-between; position: relative; padding-left: 20px; }}
                .timeline-line {{ position: absolute; left: 45px; top: 35px; bottom: 35px; width: 4px; background: {theme['accent']}; z-index: 1; }}
                .timeline-item {{ display: flex; align-items: flex-start; gap: 20px; position: relative; z-index: 5; }}
                .node-circle {{ width: 52px; height: 52px; border-radius: 50%; background: {theme['accent']}; color: #000000; font-family: 'Fredoka', sans-serif; font-size: 22px; font-weight: 700; display: flex; align-items: center; justify-content: center; flex-shrink: 0; box-shadow: 0 0 20px {theme['accent']}80; }}
                .node-content {{ background: #ffffff; border: 1px solid {theme['card_border']}; border-radius: 16px; padding: 20px 22px; flex: 1; box-shadow: 0 8px 25px rgba(0,0,0,0.2); }}
                .node-phase {{ font-size: 13px; font-weight: 900; color: {theme['accent']}; text-transform: uppercase; margin-bottom: 4px; }}
                .node-text {{ font-size: 14px; line-height: 1.45; color: #1e293b; font-weight: 600; }}
                .footer-bar {{ position: absolute; bottom: 20px; left: 45px; right: 45px; display: flex; justify-content: space-between; align-items: center; font-size: 14px; color: #94a3b8; font-weight: 700; }}
            </style>
        </head>
        <body>
            <div class="header-bar">
                <div class="tag">🚀 STEP-BY-STEP WORKBENCH BLUEPRINT</div>
                <h1 class="title">{topic['title']}</h1>
            </div>
            <div class="timeline-wrapper">
                <div class="left-column">
                    <div class="visual-side"><img src="{image_path}" /><div class="art-tag-time">{art_label}</div></div>
                    <div class="pro-callout">
                        <h4>💡 BLUEPRINT BENCHMARK NOTE</h4>
                        <p>{topic.get('fun_fact', ['Masterclass craft sequence'])[0]}</p>
                    </div>
                </div>
                <div class="timeline-col">
                    <div class="timeline-line"></div>
                    {steps_html}
                </div>
            </div>
            <div class="footer-bar"><div>{page_name.upper()} • {v_data['theme_name']}</div><div style="color: {theme['accent']};">SWIPE FOR NEXT LESSON ➔</div></div>
        </body>
        </html>
        """

    def _build_radar_pie_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 9: Circular Data Pie Wheel & Vector Badges (Ref 4)."""
        shelf_specs = topic.get("shelf_specs", [
            {"icon": "⚡", "title": "Precision", "desc": "Highest grade execution"},
            {"icon": "🔬", "title": "Tested", "desc": "Validated under micro specs"},
            {"icon": "🌟", "title": "Record", "desc": "Top tier benchmarks"},
            {"icon": "🛡️", "title": "Durable", "desc": "Engineered for longevity"},
            {"icon": "🎯", "title": "Focus", "desc": "Laser targeted adaptation"}
        ])
        shelf_colors = ["#16a34a", "#d97706", "#0284c7", "#7c3aed", "#db2777"]

        arched_pills_html = ""
        for idx in range(min(5, len(shelf_specs))):
            s = shelf_specs[idx]
            c = shelf_colors[idx % len(shelf_colors)]
            arched_pills_html += f"""
            <div class="arched-pill" style="background: {c};">
                <div class="arch-icon-bubble">{s['icon']}</div>
                <div class="arch-title">{s['title']}</div>
                <div class="arch-desc">{s['desc']}</div>
            </div>
            """

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Space+Grotesk:wght@700&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background: #5a7d90; font-family: 'Outfit', sans-serif; color: #ffffff; overflow: hidden; position: relative; padding: 40px; }}
                .corner-peel {{ position: absolute; top: 0; right: 0; width: 120px; height: 120px; background: linear-gradient(135deg, transparent 50%, #84cc16 50%); }}
                .header h1 {{ font-family: 'Space Grotesk', sans-serif; font-size: 44px; font-weight: 800; text-transform: uppercase; line-height: 1.1; }}
                .header .sub {{ font-size: 18px; color: #e2e8f0; font-weight: 600; margin-top: 6px; }}
                .data-row {{ display: grid; grid-template-columns: 480px 1fr; gap: 24px; margin-top: 24px; height: 380px; }}
                .pie-box {{ background: #ffffff; border-radius: 20px; padding: 20px; display: flex; flex-direction: column; align-items: center; justify-content: center; box-shadow: 0 15px 35px rgba(0,0,0,0.15); }}
                .pie-svg {{ width: 230px; height: 230px; }}
                .pie-legend {{ display: grid; grid-template-columns: 1fr 1fr; gap: 8px; width: 100%; margin-top: 12px; font-size: 13px; font-weight: 700; color: #1e293b; }}
                .legend-item {{ display: flex; align-items: center; gap: 6px; }}
                .legend-dot {{ width: 12px; height: 12px; border-radius: 4px; }}
                .image-box {{ border-radius: 20px; overflow: hidden; border: 3px solid #ffffff; box-shadow: 0 15px 35px rgba(0,0,0,0.15); position: relative; }}
                .image-box img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .art-badge {{ position: absolute; top: 15px; left: 15px; background: rgba(0,0,0,0.8); color: #facc15; font-size: 12px; font-weight: 800; padding: 5px 12px; border-radius: 12px; }}
                .bottom-grid {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-top: 22px; }}
                .metric-card {{ border-radius: 16px; padding: 18px; color: #ffffff; }}
                .metric-card h3 {{ font-size: 34px; font-weight: 900; line-height: 1; margin-bottom: 4px; }}
                .metric-card h5 {{ font-size: 13px; font-weight: 800; text-transform: uppercase; }}
                .metric-card p {{ font-size: 12px; opacity: 0.9; margin-top: 4px; line-height: 1.35; }}
                .card-1 {{ background: #ea580c; }} .card-2 {{ background: #16a34a; }} .card-3 {{ background: #7c3aed; }} .card-4 {{ background: #0284c7; }}
                .arched-shelf {{ display: grid; grid-template-columns: repeat(5, 1fr); gap: 14px; margin-top: 22px; height: 280px; }}
                .arched-pill {{ border-radius: 18px 18px 12px 12px; padding: 18px 12px; color: #ffffff; display: flex; flex-direction: column; align-items: center; text-align: center; box-shadow: 0 10px 25px rgba(0,0,0,0.15); justify-content: space-between; }}
                .arch-icon-bubble {{ width: 44px; height: 44px; border-radius: 50%; background: #ffffff; display: flex; align-items: center; justify-content: center; font-size: 22px; margin-bottom: 6px; box-shadow: 0 4px 10px rgba(0,0,0,0.2); }}
                .arch-title {{ font-size: 14px; font-weight: 800; text-transform: uppercase; margin-bottom: 4px; }}
                .arch-desc {{ font-size: 12px; line-height: 1.35; opacity: 0.95; }}
                .pro-summary-ribbon {{ background: rgba(15, 23, 42, 0.88); border: 1px solid rgba(255, 255, 255, 0.2); border-left: 6px solid #84cc16; border-radius: 14px; padding: 16px 20px; margin-top: 22px; display: flex; align-items: center; gap: 18px; box-shadow: 0 10px 25px rgba(0,0,0,0.2); }}
                .ribbon-badge {{ background: #84cc16; color: #000; font-size: 12px; font-weight: 900; padding: 6px 14px; border-radius: 20px; letter-spacing: 1px; text-transform: uppercase; white-space: nowrap; }}
                .ribbon-text {{ font-size: 14px; line-height: 1.4; color: #e2e8f0; font-weight: 600; }}
                .footer {{ position: absolute; bottom: 18px; left: 40px; right: 40px; display: flex; justify-content: space-between; font-size: 14px; font-weight: 700; color: #e2e8f0; }}
            </style>
        </head>
        <body>
            <div class="corner-peel"></div>
            <div class="header"><h1>{topic['title']}</h1><div class="sub">{topic.get('latin', v_data['badge_tag'])}</div></div>
            <div class="data-row">
                <div class="pie-box">
                    <svg class="pie-svg" viewBox="0 0 36 36">
                        <circle r="16" cx="18" cy="18" fill="none" stroke="#ea580c" stroke-width="8" stroke-dasharray="45 100" stroke-dashoffset="0" />
                        <circle r="16" cx="18" cy="18" fill="none" stroke="#16a34a" stroke-width="8" stroke-dasharray="28 100" stroke-dashoffset="-45" />
                        <circle r="16" cx="18" cy="18" fill="none" stroke="#7c3aed" stroke-width="8" stroke-dasharray="18 100" stroke-dashoffset="-73" />
                        <circle r="16" cx="18" cy="18" fill="none" stroke="#0284c7" stroke-width="8" stroke-dasharray="9 100" stroke-dashoffset="-91" />
                    </svg>
                    <div class="pie-legend">
                        <div class="legend-item"><div class="legend-dot" style="background:#ea580c;"></div> 45% Primary Force</div>
                        <div class="legend-item"><div class="legend-dot" style="background:#16a34a;"></div> 28% Surface Grip</div>
                        <div class="legend-item"><div class="legend-dot" style="background:#7c3aed;"></div> 18% Aerodynamics</div>
                        <div class="legend-item"><div class="legend-dot" style="background:#0284c7;"></div> 9% Thermal Dissipation</div>
                    </div>
                </div>
                <div class="image-box"><img src="{image_path}" /><div class="art-badge">{art_label}</div></div>
            </div>
            <div class="bottom-grid">
                <div class="metric-card card-1"><h3>45%</h3><h5>Peak Velocity</h5><p>Exerts maximum force at primary impact zone.</p></div>
                <div class="metric-card card-2"><h3>28%</h3><h5>Micro Texture</h5><p>Sub-millimeter friction grooves stabilize path.</p></div>
                <div class="metric-card card-3"><h3>18%</h3><h5>Thermal Balance</h5><p>Absorbs kinetic heat without degradation.</p></div>
                <div class="metric-card card-4"><h3>9%</h3><h5>Reserve Output</h5><p>Instantaneous surge capacity under stress.</p></div>
            </div>
            <div class="arched-shelf">
                {arched_pills_html}
            </div>
            <div class="pro-summary-ribbon">
                <div class="ribbon-badge">DATA VALIDATION</div>
                <div class="ribbon-text">{topic.get('fun_fact', ['Telemetry records validated through deep-sea acoustic hydrophones.'])[0]}</div>
            </div>
            <div class="footer"><div>{page_name.upper()} • {v_data['theme_name']}</div><div>FOLLOW @{page_name.upper()} FOR DAILY DATA</div></div>
        </body>
        </html>
        """

    def _build_encyclopedic_dossier_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 10: Classified Archival File & Redacted Stamp."""
        cards = topic.get("cards", [])
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Courier+Prime:wght@400;700&family=Outfit:wght@600;800;900&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background-color: #e5ded2; font-family: 'Courier Prime', monospace; color: #1c1917; overflow: hidden; position: relative; padding: 45px; }}
                .stamp-classified {{ position: absolute; top: 40px; right: 50px; border: 4px solid #dc2626; color: #dc2626; padding: 8px 18px; font-family: 'Outfit', sans-serif; font-size: 20px; font-weight: 900; letter-spacing: 3px; transform: rotate(4deg); text-transform: uppercase; border-radius: 6px; box-shadow: 0 0 10px rgba(220,38,38,0.2); }}
                .dossier-id {{ font-size: 14px; font-weight: 700; color: #78716c; letter-spacing: 2px; text-transform: uppercase; margin-bottom: 8px; }}
                .main-title {{ font-family: 'Outfit', sans-serif; font-size: 48px; font-weight: 900; text-transform: uppercase; color: #1c1917; line-height: 1.05; margin-bottom: 25px; }}
                .dossier-grid {{ display: grid; grid-template-columns: 480px 1fr; gap: 30px; height: 1020px; }}
                .left-dossier-col {{ display: flex; flex-direction: column; justify-content: space-between; height: 100%; }}
                .polaroid-holder {{ background: #ffffff; padding: 18px; border-radius: 8px; box-shadow: 0 10px 30px rgba(0,0,0,0.15); height: 560px; display: flex; flex-direction: column; }}
                .polaroid-img {{ flex: 1; overflow: hidden; border-radius: 4px; position: relative; }}
                .polaroid-img img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .polaroid-caption {{ font-size: 14px; font-weight: 700; color: #44403c; text-align: center; margin-top: 12px; letter-spacing: 1px; }}
                .typewriter-col {{ display: flex; flex-direction: column; justify-content: space-between; height: 100%; }}
                .file-card {{ background: rgba(255,255,255,0.75); border: 1px solid #d6cfc4; border-left: 6px solid #1c1917; padding: 18px 22px; border-radius: 6px; }}
                .file-card h4 {{ font-family: 'Outfit', sans-serif; font-size: 15px; font-weight: 900; color: #1c1917; text-transform: uppercase; margin-bottom: 6px; }}
                .file-card p {{ font-size: 14px; line-height: 1.5; color: #44403c; }}
                .barcode-strip {{ position: absolute; bottom: 15px; left: 45px; right: 45px; border-top: 2px solid #a8a29e; padding-top: 12px; display: flex; justify-content: space-between; align-items: center; font-size: 13px; font-weight: 700; color: #78716c; }}
            </style>
        </head>
        <body>
            <div class="stamp-classified">CLASSIFIED ARCHIVE</div>
            <div class="dossier-id">RECORD REF // #{topic['slug'].upper()}</div>
            <h1 class="main-title">{topic['title']}</h1>
            <div class="dossier-grid">
                <div class="left-dossier-col">
                    <div class="polaroid-holder">
                        <div class="polaroid-img"><img src="{image_path}" /></div>
                        <div class="polaroid-caption">FIGURE 1.0 • {art_label.upper()}</div>
                    </div>
                    <div class="file-card" style="border-left-color:#dc2626;">
                        <h4>SECURITY PROTOCOL & DISPATCH</h4>
                        <p>{topic.get('fun_fact', ['Verified document file'])[0]}</p>
                    </div>
                    <div class="file-card" style="border-left-color:#0284c7;">
                        <h4>TACTICAL THRESHOLD EVALUATION</h4>
                        <p>BENCHMARK: {topic.get('stat_primary', '99.4%')} • TOLERANCE: {topic.get('stat_secondary', '0.05mm')}</p>
                    </div>
                </div>
                <div class="typewriter-col">
                    <div class="file-card"><h4>SECTION 01: NOMENCLATURE</h4><p>{topic.get('latin', v_data['badge_tag'])}</p></div>
                    <div class="file-card"><h4>SECTION 02: PRIMARY MECHANISM</h4><p>{cards[0]['text'] if len(cards) > 0 else 'Direct observation notes.'}</p></div>
                    <div class="file-card"><h4>SECTION 03: TACTICAL SPECIFICATION</h4><p>{cards[1]['text'] if len(cards) > 1 else 'Sub-surface structural analysis.'}</p></div>
                    <div class="file-card"><h4>SECTION 04: RECORD BENCHMARKS</h4><p>{cards[2]['text'] if len(cards) > 2 else 'Verified threshold records.'}</p></div>
                    <div class="file-card"><h4>SECTION 05: FIELD AUTHORIZATION</h4><p>DISPATCHED BY @{page_name.upper()} • OFFICIAL LEDGER ARCHIVES</p></div>
                </div>
            </div>
            <div class="barcode-strip"><div>|||||||||||||||||||||||||||||||||||||||||||||</div><div>CONFIDENTIAL DISPATCH // {page_name.upper()}</div></div>
        </body>
        </html>
        """

    def _build_polaroid_scrapbook_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 11: Explorer Field Journal & Overlapping Polaroids."""
        cards = topic.get("cards", [])
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Caveat:wght@700&family=Outfit:wght@400;600;700;800;900&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background-color: #f3ede2; font-family: 'Outfit', sans-serif; color: #292524; overflow: hidden; position: relative; padding: 45px; }}
                .scrapbook-header {{ text-align: center; margin-bottom: 25px; }}
                .pinned-title {{ font-family: 'Caveat', cursive; font-size: 58px; font-weight: 700; color: #44403c; line-height: 1; }}
                .scrap-sub {{ font-size: 16px; font-weight: 800; color: #d97706; letter-spacing: 2px; text-transform: uppercase; margin-top: 6px; }}
                .scrapbook-stage {{ display: grid; grid-template-columns: 500px 1fr; gap: 35px; height: 1020px; }}
                .left-scrap-col {{ display: flex; flex-direction: column; justify-content: space-between; height: 100%; }}
                .polaroid-frame {{ background: #ffffff; padding: 20px; border-radius: 12px; box-shadow: 0 20px 40px rgba(0,0,0,0.12); transform: rotate(-2deg); height: 580px; display: flex; flex-direction: column; position: relative; }}
                .washi-tape {{ position: absolute; top: -14px; left: 35%; width: 140px; height: 32px; background: rgba(217, 119, 6, 0.7); transform: rotate(3deg); border-radius: 4px; }}
                .polaroid-pic {{ flex: 1; border-radius: 6px; overflow: hidden; }}
                .polaroid-pic img {{ width: 100%; height: 100%; object-fit: cover; display: block; }}
                .polaroid-handwriting {{ font-family: 'Caveat', cursive; font-size: 26px; font-weight: 700; color: #44403c; text-align: center; margin-top: 14px; }}
                .notes-col {{ display: flex; flex-direction: column; justify-content: space-between; height: 100%; }}
                .sticky-note {{ background: #fef08a; border-radius: 12px; padding: 22px; box-shadow: 0 10px 25px rgba(0,0,0,0.08); transform: rotate(1.5deg); color: #713f12; }}
                .sticky-note h4 {{ font-family: 'Caveat', cursive; font-size: 32px; font-weight: 700; margin-bottom: 6px; }}
                .sticky-note p {{ font-size: 15px; line-height: 1.45; font-weight: 600; }}
                .journal-card {{ background: #ffffff; border-radius: 16px; padding: 18px 20px; box-shadow: 0 8px 25px rgba(0,0,0,0.06); }}
                .journal-card h5 {{ font-size: 14px; font-weight: 800; color: #d97706; text-transform: uppercase; margin-bottom: 4px; }}
                .journal-card p {{ font-size: 14px; line-height: 1.45; color: #57534e; }}
                .footer-scrap {{ position: absolute; bottom: 20px; left: 45px; right: 45px; display: flex; justify-content: space-between; font-size: 14px; font-weight: 700; color: #78716c; }}
            </style>
        </head>
        <body>
            <div class="scrapbook-header">
                <div class="scrap-sub">📔 EXPLORER FIELD JOURNAL • {v_data['badge_tag']}</div>
                <h1 class="pinned-title">{topic['title']}</h1>
            </div>
            <div class="scrapbook-stage">
                <div class="left-scrap-col">
                    <div class="polaroid-frame">
                        <div class="washi-tape"></div>
                        <div class="polaroid-pic"><img src="{image_path}" /></div>
                        <div class="polaroid-handwriting">Field Sketch • {art_label}</div>
                    </div>
                    <div class="journal-card" style="border-left: 6px solid #d97706;">
                        <h5>DID YOU KNOW?</h5>
                        <p>{topic.get('fun_fact', ['Field discovery notes'])[0]}</p>
                    </div>
                    <div class="journal-card" style="border-left: 6px solid #16a34a;">
                        <h5>EXPEDITION BENCHMARK</h5>
                        <p>VERIFIED RECORD: {topic.get('stat_primary', 'Standard')} • TOLERANCE: {topic.get('stat_secondary', 'Optimal')}</p>
                    </div>
                </div>
                <div class="notes-col">
                    <div class="sticky-note">
                        <h4>💡 Field Discovery Note</h4>
                        <p>{cards[0]['text'] if len(cards) > 0 else 'Remarkable nature and craft adaptation observed on workbench.'}</p>
                    </div>
                    <div class="journal-card">
                        <h5>KEY OBSERVATION 01</h5>
                        <p>{cards[1]['text'] if len(cards) > 1 else 'Sub-surface structural behavior recorded under high magnification.'}</p>
                    </div>
                    <div class="journal-card">
                        <h5>KEY OBSERVATION 02</h5>
                        <p>{cards[2]['text'] if len(cards) > 2 else 'Resilient performance benchmarks under extreme stress testing.'}</p>
                    </div>
                    <div class="journal-card">
                        <h5>KEY OBSERVATION 03</h5>
                        <p>{cards[3]['text'] if len(cards) > 3 else 'Environmental adaptation confirmed through continuous field trials.'}</p>
                    </div>
                </div>
            </div>
            <div class="footer-scrap"><div>{page_name.upper()} • {v_data['theme_name']}</div><div style="color: #d97706;">FOLLOW @{page_name.upper()} FOR DAILY SCRAPBOOK NOTES</div></div>
        </body>
        </html>
        """

    def _build_cyber_blueprint_hud_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 12: Architectural CAD Blueprint & Caliper Schematics."""
        cards = topic.get("cards", [])
        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Share+Tech+Mono&family=Space+Grotesk:wght@700&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{ width: 1080px; height: 1350px; background-color: #0b1d3a; font-family: 'Share Tech Mono', monospace; color: #38bdf8; overflow: hidden; position: relative; padding: 40px; }}
                .cad-grid {{ position: absolute; inset: 0; background-image: linear-gradient(rgba(56, 189, 248, 0.12) 1px, transparent 1px), linear-gradient(90deg, rgba(56, 189, 248, 0.12) 1px, transparent 1px); background-size: 30px 30px; pointer-events: none; }}
                .cad-header {{ display: flex; justify-content: space-between; align-items: flex-start; margin-bottom: 25px; position: relative; z-index: 10; }}
                .cad-title h1 {{ font-family: 'Space Grotesk', sans-serif; font-size: 42px; font-weight: 700; color: #ffffff; text-transform: uppercase; }}
                .cad-title .sub {{ color: #38bdf8; font-size: 16px; margin-top: 4px; }}
                .cad-stamp {{ border: 2px solid #38bdf8; padding: 8px 16px; font-size: 12px; font-weight: 700; text-align: center; color: #ffffff; background: rgba(56, 189, 248, 0.1); }}
                .blueprint-grid {{ display: grid; grid-template-columns: 560px 1fr; gap: 30px; height: 1000px; position: relative; z-index: 10; }}
                .cad-left-col {{ display: flex; flex-direction: column; justify-content: space-between; height: 100%; }}
                .cad-drawing-box {{ border: 2px solid #38bdf8; position: relative; padding: 20px; background: rgba(11, 29, 58, 0.85); box-shadow: 0 0 40px rgba(56, 189, 248, 0.2); height: 720px; display: flex; flex-direction: column; }}
                .cad-caliper-top {{ text-align: center; font-size: 13px; color: #facc15; margin-bottom: 8px; }}
                .cad-img-wrap {{ flex: 1; border: 1px dashed rgba(56, 189, 248, 0.5); overflow: hidden; position: relative; }}
                .cad-img-wrap img {{ width: 100%; height: 100%; object-fit: cover; display: block; filter: saturate(1.2); }}
                .cad-crosshair-tl {{ position: absolute; top: 10px; left: 10px; font-size: 18px; color: #38bdf8; }}
                .cad-crosshair-br {{ position: absolute; bottom: 10px; right: 10px; font-size: 18px; color: #38bdf8; }}
                .hud-radar-box {{ background: rgba(15, 23, 42, 0.9); border: 1px solid #0284c7; border-left: 5px solid #38bdf8; padding: 18px 20px; }}
                .hud-radar-box h4 {{ font-family: 'Space Grotesk', sans-serif; font-size: 15px; color: #38bdf8; text-transform: uppercase; margin-bottom: 4px; }}
                .hud-radar-box p {{ font-size: 13px; line-height: 1.4; color: #bae6fd; }}
                .cad-specs-col {{ display: flex; flex-direction: column; justify-content: space-between; height: 100%; }}
                .cad-spec-card {{ background: rgba(15, 23, 42, 0.9); border: 1px solid #0284c7; border-left: 5px solid #facc15; padding: 16px 20px; }}
                .cad-spec-card h4 {{ font-family: 'Space Grotesk', sans-serif; font-size: 15px; color: #ffffff; text-transform: uppercase; margin-bottom: 4px; }}
                .cad-spec-card p {{ font-size: 13px; line-height: 1.45; color: #bae6fd; }}
                .cad-data-table {{ width: 100%; border-collapse: collapse; font-size: 12px; }}
                .cad-data-table th, .cad-data-table td {{ border: 1px solid rgba(56, 189, 248, 0.3); padding: 8px 10px; text-align: left; }}
                .cad-data-table th {{ background: rgba(56, 189, 248, 0.15); color: #ffffff; }}
                .status-badge {{ background: rgba(16, 185, 129, 0.2); border: 1px solid #10b981; color: #34d399; font-weight: 700; font-size: 13px; padding: 10px; text-align: center; }}
                .footer-cad {{ position: absolute; bottom: 18px; left: 40px; right: 40px; display: flex; justify-content: space-between; font-size: 13px; color: #38bdf8; z-index: 10; border-top: 1px solid rgba(56,189,248,0.3); padding-top: 8px; }}
            </style>
        </head>
        <body>
            <div class="cad-grid"></div>
            <div class="cad-header">
                <div class="cad-title"><h1>{topic['title']}</h1><div class="sub">SCHEMATIC DIAGRAM // {v_data['badge_tag']}</div></div>
                <div class="cad-stamp">PROJECT: {page_name.upper()}<br>REV: 4.0 ACTIVE</div>
            </div>
            <div class="blueprint-grid">
                <div class="cad-left-col">
                    <div class="cad-drawing-box">
                        <div class="cad-caliper-top">| <--------- 1:87 SCALE CALIBRATION ---------> |</div>
                        <div class="cad-img-wrap">
                            <div class="cad-crosshair-tl">+</div><div class="cad-crosshair-br">+</div>
                            <img src="{image_path}" />
                        </div>
                    </div>
                    <div class="hud-radar-box">
                        <h4>SYSTEM CALIBRATION NOTE</h4>
                        <p>{topic.get('fun_fact', ['System engineering diagram'])[0]}</p>
                    </div>
                </div>
                <div class="cad-specs-col">
                    <div class="cad-spec-card"><h4>[SECTION 01: ARCHITECTURE]</h4><p>{cards[0]['text'] if len(cards) > 0 else 'Direct structural analysis.'}</p></div>
                    <div class="cad-spec-card"><h4>[SECTION 02: KINETIC PROFILE]</h4><p>{cards[1]['text'] if len(cards) > 1 else 'Sub-surface friction index.'}</p></div>
                    <div class="cad-spec-card"><h4>[SECTION 03: TOLERANCE MARGIN]</h4><p>{cards[2]['text'] if len(cards) > 2 else 'Verified operating tolerances.'}</p></div>
                    <table class="cad-data-table">
                        <tr><th>PARAM</th><th>RATING</th></tr>
                        <tr><td>TOLERANCE</td><td>±0.05 mm</td></tr>
                        <tr><td>PEAK OUTPUT</td><td>{topic.get('stat_primary', '99.4% OPTIMAL')}</td></tr>
                        <tr><td>PRESSURE</td><td>{topic.get('stat_secondary', '1,050 PSI')}</td></tr>
                        <tr><td>MEDIUM</td><td>{art_label}</td></tr>
                    </table>
                    <div class="status-badge">🟢 SCHEMATIC 100% VALIDATED & CERTIFIED</div>
                </div>
            </div>
            <div class="footer-cad"><div>CAD ARCHIVE REF: {topic['slug'].upper()}</div><div>AUTHORIZED BY @{page_name.upper()}</div></div>
        </body>
        </html>
        """

    def _build_comic_pop_art_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 13: Retro Pop Art Comic Strip & Speech Bursts."""
        cards = topic.get("cards", [])
        c1 = cards[0] if len(cards) > 0 else {"label": "POW! SPEC 01", "text": "Supreme dynamic response."}
        c2 = cards[1] if len(cards) > 1 else {"label": "ZAP! SPEC 02", "text": "High impact kinetic agility."}
        c3 = cards[2] if len(cards) > 2 else {"label": "WHAM! SPEC 03", "text": "Microsecond precision."}
        c4 = cards[3] if len(cards) > 3 else {"label": "BOOM! SPEC 04", "text": "Unmatched anatomical force."}

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Bangers&family=Outfit:wght@600;800;900&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    width: 1080px;
                    height: 1350px;
                    background-color: #fef08a;
                    background-image: radial-gradient(#fde047 20%, transparent 20%), radial-gradient(#facc15 20%, transparent 20%);
                    background-size: 24px 24px;
                    background-position: 0 0, 12px 12px;
                    font-family: 'Outfit', sans-serif;
                    color: #0f172a;
                    overflow: hidden;
                    position: relative;
                    padding: 40px;
                }}
                .comic-banner {{
                    background: #dc2626;
                    border: 5px solid #000000;
                    box-shadow: 8px 8px 0 #000000;
                    padding: 16px 24px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 25px;
                    transform: rotate(-1deg);
                }}
                .comic-banner h1 {{
                    font-family: 'Bangers', cursive;
                    font-size: 50px;
                    color: #ffffff;
                    letter-spacing: 2px;
                    text-shadow: 3px 3px 0 #000000;
                    text-transform: uppercase;
                    line-height: 1;
                }}
                .action-burst {{
                    background: #facc15;
                    border: 3px solid #000000;
                    box-shadow: 4px 4px 0 #000000;
                    padding: 6px 16px;
                    font-family: 'Bangers', cursive;
                    font-size: 22px;
                    color: #000000;
                    letter-spacing: 1px;
                    transform: rotate(4deg);
                }}
                .comic-grid {{
                    display: grid;
                    grid-template-columns: 520px 1fr;
                    gap: 30px;
                    height: 980px;
                }}
                .comic-panel-hero {{
                    background: #ffffff;
                    border: 5px solid #000000;
                    box-shadow: 10px 10px 0 #000000;
                    display: flex;
                    flex-direction: column;
                    padding: 16px;
                    position: relative;
                }}
                .hero-img-box {{
                    flex: 1;
                    border: 3px solid #000000;
                    overflow: hidden;
                    position: relative;
                }}
                .hero-img-box img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                }}
                .speech-bubble {{
                    background: #ffffff;
                    border: 4px solid #000000;
                    border-radius: 20px;
                    padding: 16px 20px;
                    margin-top: 14px;
                    position: relative;
                    box-shadow: 5px 5px 0 #000000;
                }}
                .speech-bubble::before {{
                    content: '';
                    position: absolute;
                    top: -16px;
                    left: 40px;
                    border-width: 0 14px 16px 14px;
                    border-style: solid;
                    border-color: transparent transparent #000000 transparent;
                }}
                .speech-bubble p {{
                    font-size: 15px;
                    font-weight: 800;
                    color: #000000;
                    line-height: 1.4;
                }}
                .cards-stack {{
                    display: flex;
                    flex-direction: column;
                    gap: 18px;
                }}
                .comic-card {{
                    border: 4px solid #000000;
                    box-shadow: 7px 7px 0 #000000;
                    padding: 18px 22px;
                    border-radius: 12px;
                }}
                .comic-card h4 {{
                    font-family: 'Bangers', cursive;
                    font-size: 26px;
                    letter-spacing: 1px;
                    margin-bottom: 4px;
                    text-transform: uppercase;
                }}
                .comic-card p {{
                    font-size: 14px;
                    line-height: 1.45;
                    font-weight: 700;
                }}
                .c-yellow {{ background: #fef08a; }}
                .c-cyan {{ background: #a5f3fc; }}
                .c-pink {{ background: #fbcfe8; }}
                .c-orange {{ background: #fed7aa; }}
                .art-badge-pop {{
                    position: absolute;
                    top: 25px;
                    right: 25px;
                    background: #3b82f6;
                    color: #ffffff;
                    border: 3px solid #000000;
                    box-shadow: 4px 4px 0 #000000;
                    font-family: 'Bangers', cursive;
                    font-size: 18px;
                    padding: 4px 14px;
                    transform: rotate(-3deg);
                }}
                .comic-footer {{
                    position: absolute;
                    bottom: 16px;
                    left: 40px;
                    right: 40px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-family: 'Bangers', cursive;
                    font-size: 20px;
                    color: #000000;
                    letter-spacing: 1px;
                }}
            </style>
        </head>
        <body>
            <div class="comic-banner">
                <h1>{topic['title']}</h1>
                <div class="action-burst">🔥 TOP SECRET DOSSIER</div>
            </div>
            <div class="comic-grid">
                <div class="comic-panel-hero">
                    <div class="art-badge-pop">{art_label.upper()}</div>
                    <div class="hero-img-box"><img src="{image_path}" /></div>
                    <div class="speech-bubble">
                        <p>“{topic.get('fun_fact', ['An extraordinary biological craft wonder'])[0]}”</p>
                    </div>
                </div>
                <div class="cards-stack">
                    <div class="comic-card c-yellow">
                        <h4 style="color: #b45309;">⚡ {c1['label']}</h4>
                        <p style="color: #78350f;">{c1['text']}</p>
                    </div>
                    <div class="comic-card c-cyan">
                        <h4 style="color: #0369a1;">💥 {c2['label']}</h4>
                        <p style="color: #0c4a6e;">{c2['text']}</p>
                    </div>
                    <div class="comic-card c-pink">
                        <h4 style="color: #be185d;">🎯 {c3['label']}</h4>
                        <p style="color: #831843;">{c3['text']}</p>
                    </div>
                    <div class="comic-card c-orange">
                        <h4 style="color: #c2410c;">🌟 {c4['label']}</h4>
                        <p style="color: #7c2d12;">{c4['text']}</p>
                    </div>
                </div>
            </div>
            <div class="comic-footer">
                <div>SERIES ARCHIVE // {page_name.upper()} • {v_data['badge_tag']}</div>
                <div>FOLLOW @{page_name.upper()} FOR NEXT EPISODE ➔</div>
            </div>
        </body>
        </html>
        """

    def _build_minimalist_swiss_grid_html(self, page_name: str, topic: Dict[str, Any], v_data: Dict[str, Any], theme: Dict[str, Any], image_path: str, art_label: str) -> str:
        """Template 14: Modernist Swiss Typography & Roman Numeral Grid."""
        cards = topic.get("cards", [])
        c1 = cards[0] if len(cards) > 0 else {"label": "SURFACE DYNAMICS", "text": "Engineered equilibrium under load."}
        c2 = cards[1] if len(cards) > 1 else {"label": "KINETIC EFFICIENCY", "text": "Continuous mechanical precision."}
        c3 = cards[2] if len(cards) > 2 else {"label": "ACOUSTIC PROFILE", "text": "Near-zero sound signature emission."}
        c4 = cards[3] if len(cards) > 3 else {"label": "STRUCTURAL INTEGRITY", "text": "Resilient internal matrix."}

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Playfair+Display:ital,wght@0,700;0,900;1,700&family=Space+Grotesk:wght@400;600;700&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    width: 1080px;
                    height: 1350px;
                    background-color: #0a0a0c;
                    font-family: 'Space Grotesk', sans-serif;
                    color: #ffffff;
                    overflow: hidden;
                    position: relative;
                    padding: 55px;
                }}
                .swiss-header {{
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-end;
                    border-bottom: 2px solid rgba(255, 255, 255, 0.2);
                    padding-bottom: 25px;
                    margin-bottom: 35px;
                }}
                .swiss-header h1 {{
                    font-family: 'Playfair Display', serif;
                    font-size: 48px;
                    font-weight: 900;
                    line-height: 1.05;
                    letter-spacing: -0.5px;
                    text-transform: uppercase;
                }}
                .swiss-header .index-no {{
                    font-size: 15px;
                    font-weight: 700;
                    color: {theme['accent']};
                    letter-spacing: 3px;
                    text-transform: uppercase;
                }}
                .swiss-content {{
                    display: grid;
                    grid-template-columns: 480px 1fr;
                    gap: 40px;
                    height: 940px;
                }}
                .swiss-image-col {{
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }}
                .swiss-frame {{
                    height: 720px;
                    border-radius: 4px;
                    overflow: hidden;
                    border: 1px solid rgba(255, 255, 255, 0.15);
                    position: relative;
                }}
                .swiss-frame img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                }}
                .swiss-plaque {{
                    background: rgba(255, 255, 255, 0.05);
                    border: 1px solid rgba(255, 255, 255, 0.1);
                    padding: 20px 24px;
                    border-left: 4px solid {theme['accent']};
                }}
                .swiss-plaque h5 {{
                    font-size: 13px;
                    font-weight: 700;
                    color: {theme['accent']};
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    margin-bottom: 4px;
                }}
                .swiss-plaque p {{
                    font-size: 14px;
                    line-height: 1.45;
                    color: #cbd5e1;
                }}
                .swiss-grid-col {{
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }}
                .swiss-entry {{
                    border-bottom: 1px solid rgba(255, 255, 255, 0.12);
                    padding-bottom: 20px;
                }}
                .entry-num {{
                    font-family: 'Playfair Display', serif;
                    font-size: 40px;
                    font-weight: 700;
                    color: {theme['accent']};
                    line-height: 1;
                    margin-bottom: 6px;
                }}
                .entry-label {{
                    font-size: 15px;
                    font-weight: 700;
                    color: #ffffff;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 6px;
                }}
                .entry-text {{
                    font-size: 14px;
                    line-height: 1.45;
                    color: #94a3b8;
                }}
                .swiss-footer {{
                    position: absolute;
                    bottom: 25px;
                    left: 55px;
                    right: 55px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 13px;
                    font-weight: 600;
                    color: #64748b;
                    border-top: 1px solid rgba(255, 255, 255, 0.1);
                    padding-top: 15px;
                }}
            </style>
        </head>
        <body>
            <div class="swiss-header">
                <div>
                    <div class="index-no">ARCHIVE COMPILATION // {v_data['badge_tag']}</div>
                    <h1>{topic['title']}</h1>
                </div>
                <div style="text-align: right;">
                    <div style="font-size: 26px; font-weight: 900; color: {theme['accent']};">№ {topic.get('stat_primary', '01')}</div>
                    <div style="font-size: 12px; color: #94a3b8; text-transform: uppercase;">INDEX RATING</div>
                </div>
            </div>
            <div class="swiss-content">
                <div class="swiss-image-col">
                    <div class="swiss-frame">
                        <img src="{image_path}" />
                    </div>
                    <div class="swiss-plaque">
                        <h5>SYSTEM AUTHENTICATION</h5>
                        <p>{topic.get('fun_fact', ['Curated benchmark documentation'])[0]}</p>
                    </div>
                </div>
                <div class="swiss-grid-col">
                    <div class="swiss-entry">
                        <div class="entry-num">I.</div>
                        <div class="entry-label">{c1['label']}</div>
                        <div class="entry-text">{c1['text']}</div>
                    </div>
                    <div class="swiss-entry">
                        <div class="entry-num">II.</div>
                        <div class="entry-label">{c2['label']}</div>
                        <div class="entry-text">{c2['text']}</div>
                    </div>
                    <div class="swiss-entry">
                        <div class="entry-num">III.</div>
                        <div class="entry-label">{c3['label']}</div>
                        <div class="entry-text">{c3['text']}</div>
                    </div>
                    <div class="swiss-entry">
                        <div class="entry-num">IV.</div>
                        <div class="entry-label">{c4['label']}</div>
                        <div class="entry-text">{c4['text']}</div>
                    </div>
                </div>
            </div>
            <div class="swiss-footer">
                <div>CURATED BY @{page_name.upper()} • {v_data['theme_name'].upper()}</div>
                <div style="color: {theme['accent']};">FOLLOW @{page_name.upper()} FOR ARCHIVAL EDITIONS</div>
            </div>
        </body>
        </html>
        """

    # -------------------------------------------------------------------------
    # MAIN RENDERING DISPATCHER (Supports All 14 Templates)
    # -------------------------------------------------------------------------

    def render_infographic(
        self,
        page_name: str,
        vertical_key: str,
        topic: Dict[str, Any],
        output_path: str,
        template_name: Optional[str] = None,
        theme_name: Optional[str] = None,
        art_style_name: Optional[str] = None,
        target_hashtags: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """
        Renders a Full HD 1080x1350 graphic using Playwright Chromium:
        - Cycles through 14 distinct template archetypes.
        - Cycles through 6 distinct art styles (Pixar 3D, Ghibli, 2D Vector, 8K Photo, Cyberpunk, Lithograph).
        - Cycles through 6 vibrant multi-color palettes.
        - 100% Niche Isolated.
        """
        os.makedirs(os.path.dirname(os.path.abspath(output_path)), exist_ok=True)

        v_data = AUTHENTIC_VERTICAL_DATA.get(vertical_key, AUTHENTIC_VERTICAL_DATA["miniature_diorama_disaster"])

        # Determine art style
        if not art_style_name or art_style_name not in ART_STYLES:
            h_art = int(hashlib.md5(f"{page_name}_{topic['slug']}_art".encode()).hexdigest(), 16)
            art_style_name = ART_STYLE_KEYS[h_art % len(ART_STYLE_KEYS)]

        # Determine template
        if not template_name or template_name not in TEMPLATE_STYLES:
            h_val = int(hashlib.md5(f"{page_name}_{topic['slug']}".encode()).hexdigest(), 16)
            template_name = TEMPLATE_STYLES[h_val % len(TEMPLATE_STYLES)]

        # Determine theme
        theme_keys = list(PALETTE_THEMES.keys())
        if not theme_name or theme_name not in PALETTE_THEMES:
            h_theme = int(hashlib.md5(f"{topic['slug']}_{template_name}".encode()).hexdigest(), 16)
            theme_name = theme_keys[h_theme % len(theme_keys)]

        theme = PALETTE_THEMES[theme_name]

        # Fetch image with specific art style
        image_local_or_url, art_label = self.fetch_image_with_art_style(
            topic, v_data.get("search_term", ""), art_style_name, vertical_key=vertical_key
        )

        # Convert image to base64 Data URI to guarantee 100% reliable Playwright Chromium rendering
        image_data_uri = image_local_or_url
        try:
            if os.path.exists(image_local_or_url) and os.path.getsize(image_local_or_url) > 500:
                with open(image_local_or_url, "rb") as fh:
                    b64 = base64.b64encode(fh.read()).decode("utf-8")
                    image_data_uri = f"data:image/jpeg;base64,{b64}"
            elif image_local_or_url.startswith("http"):
                cache_name = hashlib.md5(image_local_or_url.encode()).hexdigest() + ".jpg"
                cached_img = os.path.join(self.cache_dir, cache_name)
                if not os.path.exists(cached_img) or os.path.getsize(cached_img) < 1000:
                    try:
                        r = requests.get(image_local_or_url, timeout=12)
                        if r.status_code == 200 and len(r.content) > 1000:
                            with open(cached_img, "wb") as fh:
                                fh.write(r.content)
                    except Exception as e:
                        logger.warning(f"Failed to cache remote image {image_local_or_url}: {e}")
                if os.path.exists(cached_img) and os.path.getsize(cached_img) > 1000:
                    with open(cached_img, "rb") as fh:
                        b64 = base64.b64encode(fh.read()).decode("utf-8")
                        image_data_uri = f"data:image/jpeg;base64,{b64}"
        except Exception as e:
            logger.warning(f"Base64 conversion note: {e}")

        # Dispatch to appropriate template builder:
        # Default to 100% Real Photorealistic Viral Poster (No cartoon, No Pixar 3D)
        if template_name == "photorealistic_viral" or True:
            html_content = self._build_photorealistic_viral_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "vibrant_multicolor":
            html_content = self._build_vibrant_multicolor_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "anatomical_pointer":
            html_content = self._build_anatomical_pointer_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "bento_dashboard":
            html_content = self._build_bento_dashboard_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "canva_poster":
            html_content = self._build_canva_poster_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "cinematic_hero":
            html_content = self._build_cinematic_hero_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "split_comparison":
            html_content = self._build_split_comparison_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "timeline_roadmap":
            html_content = self._build_timeline_roadmap_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "radar_pie_infographic":
            html_content = self._build_radar_pie_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "encyclopedic_dossier":
            html_content = self._build_encyclopedic_dossier_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "polaroid_scrapbook":
            html_content = self._build_polaroid_scrapbook_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "cyber_blueprint_hud":
            html_content = self._build_cyber_blueprint_hud_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "comic_pop_art":
            html_content = self._build_comic_pop_art_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        elif template_name == "minimalist_swiss_grid":
            html_content = self._build_minimalist_swiss_grid_html(page_name, topic, v_data, theme, image_data_uri, art_label)
        else:
            html_content = self._build_vintage_fieldguide_html(page_name, topic, v_data, theme, image_data_uri, art_label)

        # Render using Playwright Chromium
        render_success = False
        try:
            from playwright.sync_api import sync_playwright
            with sync_playwright() as p:
                browser = p.chromium.launch(headless=True)
                page = browser.new_page(viewport={"width": 1080, "height": 1350}, device_scale_factor=1.0)
                page.set_content(html_content, wait_until="networkidle")
                page.screenshot(path=output_path, type="png")
                browser.close()
            render_success = True
        except Exception as e:
            logger.warning(f"Playwright render encountered an issue: {e}")

        # Fallback to PIL if Playwright is unavailable
        if not render_success or not os.path.exists(output_path):
            canvas = Image.new("RGB", (1080, 1350), (15, 23, 42))
            draw = ImageDraw.Draw(canvas)
            draw.rectangle([(20, 20), (1060, 1330)], outline=(245, 158, 11), width=3)
            draw.text((60, 60), topic["title"].upper(), fill=(255, 255, 255))
            draw.text((60, 120), page_name.upper(), fill=(245, 158, 11))
            canvas.save(output_path, "PNG")

        # Ensure output is clean 1080x1350 RGB PNG
        with Image.open(output_path) as im:
            if im.mode != "RGB":
                im = im.convert("RGB")
            if im.size != (1080, 1350):
                im = im.resize((1080, 1350), Image.Resampling.LANCZOS)
            im.save(output_path, "PNG", quality=95)

        logger.info(f"Rendered [{template_name} | {theme_name} | {art_style_name}] Infographic: {output_path}")

        # Generate High-CTR Punchy Short Title (Zero Essay Titles!)
        seed = int(hashlib.md5(f"{page_name}_{topic['slug']}_{template_name}".encode()).hexdigest(), 16)
        viral_title = topic.get("title", "Wait Till You See This... 😱")

        cards = topic.get("cards", [])
        fun_facts = topic.get("fun_fact", ["An extraordinary phenomenon verified by field specialists!"])
        featured_fact = fun_facts[seed % len(fun_facts)] if isinstance(fun_facts, list) else str(fun_facts)

        facts_preview = ""
        if cards:
            facts_preview = f"🔍 Key Highlights:\n• {cards[0]['label']}: {cards[0]['text']}\n"
            if len(cards) > 1:
                facts_preview += f"• {cards[1]['label']}: {cards[1]['text']}\n"

        # Assemble Curated Trending Hashtags
        combined_tags = []
        if target_hashtags:
            for t in target_hashtags:
                clean_t = t.strip()
                if not clean_t.startswith("#"):
                    clean_t = f"#{clean_t}"
                if clean_t.lower() not in [x.lower() for x in combined_tags]:
                    combined_tags.append(clean_t)

        niche_tags = VERTICAL_TRENDING_HASHTAGS.get(vertical_key, [])
        for t in niche_tags:
            if t.lower() not in [x.lower() for x in combined_tags]:
                combined_tags.append(t)

        topic_tag = f"#{topic['slug'].replace('_', '')}"
        if topic_tag.lower() not in [x.lower() for x in combined_tags]:
            combined_tags.append(topic_tag)

        for t in GLOBAL_VIRAL_TAGS:
            if t.lower() not in [x.lower() for x in combined_tags]:
                combined_tags.append(t)

        final_hashtags = combined_tags[:14]
        hashtags_str = " ".join(final_hashtags)

        if topic.get("caption"):
            caption = f"{topic['caption']}\n\n👉 Follow @{page_name}\n\n{hashtags_str}"
        else:
            caption = (
                f"{viral_title}\n\n"
                f"📌 {topic.get('subtitle', topic.get('latin', 'Real Discovery'))}\n\n"
                f"{facts_preview}\n"
                f"💬 Did you know this before? Tell us below! 👇\n"
                f"👉 Follow @{page_name} for daily authentic discoveries!\n\n"
                f"{hashtags_str}"
            )

        return {
            "image_path": output_path,
            "title": viral_title,
            "caption": caption,
            "hashtags": hashtags_str,
            "topic_slug": topic["slug"],
            "template_name": template_name,
            "theme_name": theme_name,
            "art_style_name": art_style_name
        }
