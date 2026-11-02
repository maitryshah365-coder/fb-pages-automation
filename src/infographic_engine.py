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

# =========================================================================
# 1. ART STYLES & MASTER PROMPT ENGINEERING (Rotating Visual Mediums)
# =========================================================================

ART_STYLES = {
    "pixar_3d": {
        "label": "🎨 Pixar 3D Animated Style",
        "badge_bg": "rgba(249, 115, 22, 0.9)",
        "badge_color": "#ffffff",
        "prompt_suffix": "charming Pixar 3D animated character render, Octane render, cute expressive features, soft subsurface scattering, Disney animation aesthetic, Unreal Engine 5, 8k render, vibrant colorful studio lighting, clean isolated background"
    },
    "ghibli_anime": {
        "label": "🌸 Studio Ghibli Watercolor",
        "badge_bg": "rgba(16, 185, 129, 0.9)",
        "badge_color": "#ffffff",
        "prompt_suffix": "Studio Ghibli aesthetic, anime watercolor art, hand-painted gouache illustration, Hayao Miyazaki style, vibrant colorful anime scenery, lush natural lighting, nostalgic masterpiece, painted sky"
    },
    "flat_vector_canva": {
        "label": "📐 2D Flat Vector Infographic",
        "badge_bg": "rgba(139, 92, 246, 0.9)",
        "badge_color": "#ffffff",
        "prompt_suffix": "modern flat vector illustration, clean lines, minimalist graphic design, colorful infographic vector art, bold vibrant shapes, isolated, canva sticker art, sharp edges"
    },
    "photorealistic_8k": {
        "label": "📷 8K National Geographic",
        "badge_bg": "rgba(234, 88, 12, 0.9)",
        "badge_color": "#ffffff",
        "prompt_suffix": "hyper-realistic photography, 8k resolution, National Geographic editorial photo, macro lens f/2.8, studio lighting, razor sharp depth of field, dramatic cinematic lighting"
    },
    "cyberpunk_neon": {
        "label": "⚡ Cyberpunk Neon Schematics",
        "badge_bg": "rgba(6, 182, 212, 0.9)",
        "badge_color": "#000000",
        "prompt_suffix": "cyberpunk neon aesthetic, glowing holographic HUD schematics, electric cyan and magenta rim lighting, futuristic octane render, dark obsidian background, high tech"
    },
    "vintage_lithograph": {
        "label": "📜 Vintage Archival Lithograph",
        "badge_bg": "rgba(180, 83, 9, 0.9)",
        "badge_color": "#ffffff",
        "prompt_suffix": "vintage Victorian natural history lithograph, fine copperplate etching, antique colored botanical plate, Ernst Haeckel scientific illustration style, archival parchment paper"
    }
}

ART_STYLE_KEYS = list(ART_STYLES.keys())

# =========================================================================
# 2. TEMPLATE ARCHETYPES (Rotating Layouts)
# =========================================================================

TEMPLATE_STYLES = [
    "vibrant_multicolor",   # Style 1: 4 Vibrant Colored Cards + 5-Pill Color Shelf (Ref 4 & 5)
    "anatomical_pointer",   # Style 2: Biometric / Anatomy Callout Diagram (Ref 3)
    "vintage_fieldguide",   # Style 3: NatGeo / Natural History Specimen Archive (Ref 1)
    "canva_poster",         # Style 4: Illustrated Organic Nature Poster (Ref 2)
    "bento_dashboard",      # Style 5: Modern Tech Bento Grid with Big Stat Badges
    "cinematic_hero"        # Style 6: Magazine Cover with Frosted Glassmorphism
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
# 4. 13 FLEET VERTICALS AUTHENTIC DATA MATRIX (100% Niche Isolated)
# =========================================================================

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
                "image_url": "https://images.unsplash.com/photo-1508873696983-2df5293cb32f?w=900&auto=format&fit=crop&q=80",
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
                "image_url": "https://images.unsplash.com/photo-1563889362352-b0492c224f61?w=900&auto=format&fit=crop&q=80",
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
                "image_url": "https://images.unsplash.com/photo-1579952363873-27f3bde9be2e?w=900&auto=format&fit=crop&q=80",
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
                "image_url": "https://images.unsplash.com/photo-1579783902614-a3fb3927b675?w=900&auto=format&fit=crop&q=80",
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


class InfographicEngine:
    """
    Next-Gen Multi-Style Generative Infographic Engine:
    - 6 Rotating Art Styles for Imagery: Pixar 3D, Ghibli Anime, Flat Vector, 8K Photo, Cyberpunk, Lithograph.
    - 6 Distinct Template Archetypes (Vibrant Multicolor Grid, Anatomical Pointers, Bento Dashboard, Canva Poster, Field Guide, Cinematic Hero).
    - 6 Vibrant Multi-Color Palettes (Sky Blue, Jungle Safari, Sunset Pop, Midnight Neon, Editorial White, Pastel Bubble).
    - Automatic Style, Theme, and Art-Style Rotation on every post.
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
        art_style_key: str
    ) -> Tuple[str, str]:
        """
        Retrieves image matching the specific art style (Pixar 3D, Ghibli, 2D Vector, 8K Photo, etc.).
        Returns (image_file_path_or_url, art_style_label).
        """
        art_meta = ART_STYLES.get(art_style_key, ART_STYLES["pixar_3d"])
        slug = topic.get("slug", "default")
        cache_key = hashlib.md5(f"{slug}_{art_style_key}".encode()).hexdigest()
        cache_file = os.path.join(self.cache_dir, f"{cache_key}.jpg")

        if os.path.exists(cache_file) and os.path.getsize(cache_file) > 10000:
            return os.path.abspath(cache_file).replace("\\", "/"), art_meta["label"]

        # Build smart art-style prompt
        full_prompt = f"{topic['title']}, {search_term}, {art_meta['prompt_suffix']}"
        encoded_prompt = requests.utils.quote(full_prompt)
        poll_url = f"https://image.pollinations.ai/prompt/{encoded_prompt}?width=800&height=1000&nologo=true"

        try:
            res = requests.get(poll_url, timeout=12)
            if res.status_code == 200 and len(res.content) > 10000:
                with open(cache_file, "wb") as f:
                    f.write(res.content)
                return os.path.abspath(cache_file).replace("\\", "/"), art_meta["label"]
        except Exception as e:
            logger.warning(f"Error fetching AI image for {slug} ({art_style_key}): {e}")

        # Fallback to direct verified image if AI call fails
        direct_url = topic.get("image_url")
        if direct_url:
            return direct_url, art_meta["label"]

        return "https://images.unsplash.com/photo-1543549790-8b5f4a028cfb?w=800&auto=format&fit=crop&q=80", art_meta["label"]

    # -------------------------------------------------------------------------
    # HTML TEMPLATE BUILDERS
    # -------------------------------------------------------------------------

    def _build_vibrant_multicolor_html(
        self,
        page_name: str,
        topic: Dict[str, Any],
        v_data: Dict[str, Any],
        theme: Dict[str, Any],
        image_path: str,
        art_label: str
    ) -> str:
        """Vibrant Multicolor Layout: 4 Color Stat Cards + 5-Pill Color Shelf (Matching Ref 4 & 5)."""
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
                    width: 1080px;
                    height: 1350px;
                    background: {theme.get('bg_gradient', 'linear-gradient(135deg, #7ea8be 0%, #a2c4d6 100%)')};
                    font-family: 'Outfit', sans-serif;
                    color: {theme['text_main']};
                    overflow: hidden;
                    position: relative;
                    padding: 40px;
                }}
                .top-bar {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 25px;
                }}
                .brand-pill {{
                    background: #ffffff;
                    padding: 10px 22px;
                    border-radius: 30px;
                    display: flex;
                    align-items: center;
                    gap: 10px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.08);
                }}
                .brand-name {{
                    font-family: 'Fredoka', sans-serif;
                    font-size: 20px;
                    font-weight: 700;
                    color: #0f172a;
                }}
                .badge-verified {{
                    background: {theme['accent_secondary']};
                    color: #ffffff;
                    font-size: 11px;
                    font-weight: 800;
                    padding: 3px 8px;
                    border-radius: 12px;
                    text-transform: uppercase;
                }}
                .follow-pill {{
                    background: {theme['accent']};
                    color: #ffffff;
                    font-size: 15px;
                    font-weight: 800;
                    padding: 10px 24px;
                    border-radius: 30px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    box-shadow: 0 4px 15px rgba(0,0,0,0.15);
                }}
                .header-box {{
                    margin-bottom: 25px;
                }}
                .title-banner {{
                    font-family: 'Fredoka', sans-serif;
                    font-size: 46px;
                    font-weight: 700;
                    color: {theme['text_main']};
                    line-height: 1.1;
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .subtitle {{
                    font-size: 19px;
                    font-weight: 600;
                    color: {theme['text_sub']};
                    margin-top: 6px;
                }}
                .main-grid {{
                    display: grid;
                    grid-template-columns: 560px 1fr;
                    gap: 25px;
                    height: 780px;
                }}
                .hero-card {{
                    background: {theme['card_bg']};
                    border-radius: 28px;
                    padding: 20px;
                    box-shadow: 0 15px 35px rgba(0,0,0,0.12);
                    display: flex;
                    flex-direction: column;
                    position: relative;
                }}
                .hero-img-wrap {{
                    flex: 1;
                    border-radius: 20px;
                    overflow: hidden;
                    position: relative;
                }}
                .hero-img-wrap img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                }}
                .art-style-tag {{
                    position: absolute;
                    top: 15px;
                    left: 15px;
                    background: rgba(0,0,0,0.78);
                    backdrop-filter: blur(8px);
                    color: #facc15;
                    font-size: 13px;
                    font-weight: 800;
                    padding: 6px 14px;
                    border-radius: 20px;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                }}
                .hero-caption {{
                    margin-top: 16px;
                    background: rgba(0,0,0,0.04);
                    border-radius: 16px;
                    padding: 16px 20px;
                }}
                .hero-caption h3 {{
                    font-size: 20px;
                    font-weight: 800;
                    color: {theme['text_main']};
                    margin-bottom: 4px;
                }}
                .hero-caption p {{
                    font-size: 14px;
                    line-height: 1.45;
                    color: {theme['text_muted']};
                }}
                .stats-col {{
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }}
                .stat-card {{
                    border-radius: 20px;
                    padding: 20px;
                    color: #ffffff;
                    box-shadow: 0 8px 25px rgba(0,0,0,0.1);
                    display: flex;
                    align-items: center;
                    gap: 18px;
                }}
                .stat-badge {{
                    width: 75px;
                    height: 75px;
                    border-radius: 18px;
                    background: rgba(255,255,255,0.25);
                    display: flex;
                    align-items: center;
                    justify-content: center;
                    font-family: 'Fredoka', sans-serif;
                    font-size: 28px;
                    font-weight: 700;
                    flex-shrink: 0;
                }}
                .stat-content h4 {{
                    font-size: 18px;
                    font-weight: 800;
                    margin-bottom: 4px;
                    text-transform: uppercase;
                }}
                .stat-content p {{
                    font-size: 13px;
                    line-height: 1.4;
                    opacity: 0.95;
                }}
                .bottom-shelf {{
                    margin-top: 25px;
                    display: grid;
                    grid-template-columns: repeat(5, 1fr);
                    gap: 14px;
                }}
                .shelf-pill {{
                    border-radius: 18px;
                    padding: 16px 14px;
                    text-align: center;
                    color: #ffffff;
                    box-shadow: 0 6px 20px rgba(0,0,0,0.08);
                }}
                .shelf-pill .icon {{
                    font-size: 26px;
                    margin-bottom: 6px;
                }}
                .shelf-pill .p-title {{
                    font-size: 14px;
                    font-weight: 800;
                    text-transform: uppercase;
                    margin-bottom: 3px;
                }}
                .shelf-pill .p-desc {{
                    font-size: 11px;
                    line-height: 1.3;
                    opacity: 0.9;
                }}
                .footer-bar {{
                    margin-top: 20px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 14px;
                    font-weight: 700;
                    color: {theme['text_sub']};
                }}
            </style>
        </head>
        <body>
            <div class="top-bar">
                <div class="brand-pill">
                    <span style="font-size: 22px;">🐾</span>
                    <span class="brand-name">{page_name.upper()}</span>
                    <span class="badge-verified">✔ VERIFIED</span>
                </div>
                <div class="follow-pill">+ FOLLOW @{page_name.upper()}</div>
            </div>
            <div class="header-box">
                <h1 class="title-banner">{topic['title']}</h1>
                <div class="subtitle">{topic.get('latin', v_data['badge_tag'])}</div>
            </div>
            <div class="main-grid">
                <div class="hero-card">
                    <div class="hero-img-wrap">
                        <img src="{image_path}" />
                        <div class="art-style-tag">{art_label}</div>
                    </div>
                    <div class="hero-caption">
                        <h3>{topic['title']}</h3>
                        <p>{cards[0]['text'] if cards else 'Authentic specialized craftsmanship and masterclass techniques.'}</p>
                    </div>
                </div>
                <div class="stats-col">
                    {stat_cards_html}
                </div>
            </div>
            <div class="bottom-shelf">
                {shelf_html}
            </div>
            <div class="footer-bar">
                <div>{page_name.upper()} • {v_data['theme_name']}</div>
                <div style="color: {theme['accent']};">SWIPE FOR MORE PRO TIPS ➔</div>
            </div>
        </body>
        </html>
        """

    def _build_vintage_fieldguide_html(
        self,
        page_name: str,
        topic: Dict[str, Any],
        v_data: Dict[str, Any],
        theme: Dict[str, Any],
        image_path: str,
        art_label: str
    ) -> str:
        """Vintage Naturalist / Field Guide Specimen Archive (Ref 1)."""
        cards_html = ""
        for c in topic.get("cards", [])[:4]:
            cards_html += f"""
            <div class="spec-card">
                <div class="spec-title">{c['label']}</div>
                <div class="spec-desc">{c['text']}</div>
            </div>
            """

        facts_html = ""
        for f in topic.get("fun_fact", [])[:3]:
            facts_html += f"<li>{f}</li>"

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Cinzel:wght@600;800&family=Outfit:wght@300;400;600;700;800&family=Playfair+Display:ital,wght@0,600;0,800;1,400&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    width: 1080px;
                    height: 1350px;
                    background-color: #fbf8f1;
                    font-family: 'Outfit', sans-serif;
                    color: #18281e;
                    overflow: hidden;
                    position: relative;
                }}
                .border-frame {{
                    position: absolute;
                    top: 24px; left: 24px; right: 24px; bottom: 24px;
                    border: 2px solid #d4cbb8;
                    pointer-events: none;
                }}
                .header {{
                    padding: 50px 60px 20px 60px;
                    display: flex;
                    justify-content: space-between;
                    align-items: flex-start;
                }}
                .header-left h1 {{
                    font-family: 'Playfair Display', serif;
                    font-size: 46px;
                    font-weight: 800;
                    letter-spacing: -0.5px;
                    line-height: 1.1;
                    color: #18281e;
                    text-transform: uppercase;
                }}
                .header-left .latin {{
                    font-family: 'Playfair Display', serif;
                    font-style: italic;
                    font-size: 24px;
                    color: #735338;
                    margin-top: 6px;
                }}
                .badge-box {{
                    background: #18281e;
                    color: #fbf8f1;
                    padding: 10px 18px;
                    border-radius: 8px;
                    font-size: 14px;
                    font-weight: 800;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                }}
                .content-grid {{
                    display: grid;
                    grid-template-columns: 460px 1fr;
                    gap: 36px;
                    padding: 10px 60px 40px 60px;
                    height: 1060px;
                }}
                .left-col {{
                    display: flex;
                    flex-direction: column;
                    gap: 16px;
                }}
                .spec-card {{
                    background: rgba(255, 255, 255, 0.88);
                    border: 1px solid #e2dac9;
                    border-left: 5px solid #d97706;
                    padding: 16px 20px;
                    border-radius: 10px;
                    box-shadow: 0 4px 12px rgba(0,0,0,0.03);
                }}
                .spec-title {{
                    font-size: 15px;
                    font-weight: 800;
                    letter-spacing: 0.5px;
                    color: #d97706;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }}
                .spec-desc {{
                    font-size: 16px;
                    line-height: 1.45;
                    color: #4a5d4e;
                }}
                .did-you-know {{
                    background: rgba(230, 220, 205, 0.45);
                    border: 1px dashed #d4cbb8;
                    border-radius: 12px;
                    padding: 18px;
                    margin-top: auto;
                }}
                .did-you-know h4 {{
                    font-size: 15px;
                    font-weight: 800;
                    color: #18281e;
                    text-transform: uppercase;
                    letter-spacing: 1px;
                    margin-bottom: 8px;
                }}
                .did-you-know li {{
                    font-size: 14px;
                    line-height: 1.4;
                    color: #4a5d4e;
                    margin-bottom: 6px;
                    list-style-type: none;
                    position: relative;
                    padding-left: 18px;
                }}
                .did-you-know li::before {{
                    content: "•";
                    color: #d97706;
                    font-weight: bold;
                    font-size: 18px;
                    position: absolute;
                    left: 0;
                    top: -2px;
                }}
                .photo-frame {{
                    border-radius: 16px;
                    overflow: hidden;
                    border: 3px solid #e2dac9;
                    box-shadow: 0 12px 32px rgba(0,0,0,0.08);
                    height: 100%;
                    position: relative;
                }}
                .photo-frame img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                }}
                .art-tag-field {{
                    position: absolute;
                    bottom: 20px;
                    left: 20px;
                    background: rgba(24, 40, 30, 0.85);
                    color: #fbf8f1;
                    padding: 6px 14px;
                    border-radius: 16px;
                    font-size: 13px;
                    font-weight: 800;
                }}
                .footer-strip {{
                    position: absolute;
                    bottom: 34px;
                    left: 60px; right: 60px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-top: 1px solid #d4cbb8;
                    padding-top: 14px;
                    font-size: 14px;
                    font-weight: 600;
                    color: #735338;
                }}
                .footer-strip .brand {{
                    font-weight: 800;
                    letter-spacing: 1px;
                    color: #18281e;
                }}
            </style>
        </head>
        <body>
            <div class="border-frame"></div>
            <div class="header">
                <div class="header-left">
                    <h1>{topic['title']}</h1>
                    <div class="latin">{topic.get('latin', v_data['badge_tag'])}</div>
                </div>
                <div class="badge-box">{topic.get('badge', v_data['badge_tag'])}</div>
            </div>
            <div class="content-grid">
                <div class="left-col">
                    {cards_html}
                    <div class="did-you-know">
                        <h4>FIELD NATURALIST NOTES</h4>
                        <ul>{facts_html}</ul>
                    </div>
                </div>
                <div class="photo-frame">
                    <img src="{image_path}" />
                    <div class="art-tag-field">{art_label}</div>
                </div>
            </div>
            <div class="footer-strip">
                <div class="brand">{page_name.upper()} • {v_data['theme_name']}</div>
                <div>FOLLOW @{page_name.upper()} FOR DAILY ARCHIVES</div>
            </div>
        </body>
        </html>
        """

    def _build_anatomical_pointer_html(
        self,
        page_name: str,
        topic: Dict[str, Any],
        v_data: Dict[str, Any],
        theme: Dict[str, Any],
        image_path: str,
        art_label: str
    ) -> str:
        """Anatomical Callout Pointer Layout with SVG Connecting Lines (Ref 3)."""
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
                    width: 1080px;
                    height: 1350px;
                    background: radial-gradient(circle at 50% 45%, {theme['canvas_bg']} 0%, #050a12 100%);
                    font-family: 'Outfit', sans-serif;
                    color: #ffffff;
                    overflow: hidden;
                    position: relative;
                }}
                .header {{
                    text-align: center;
                    padding-top: 45px;
                    position: relative;
                    z-index: 10;
                }}
                .pill-tag {{
                    display: inline-block;
                    background: rgba(255, 255, 255, 0.08);
                    border: 1px solid {theme['accent']};
                    color: {theme['accent']};
                    padding: 6px 18px;
                    border-radius: 20px;
                    font-size: 14px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    margin-bottom: 12px;
                }}
                .title {{
                    font-family: 'Cinzel', serif;
                    font-size: 44px;
                    font-weight: 900;
                    letter-spacing: 1.5px;
                    color: #ffffff;
                    text-transform: uppercase;
                }}
                .subtitle {{
                    font-size: 18px;
                    color: #cbd5e1;
                    letter-spacing: 1px;
                    margin-top: 6px;
                }}
                .stage-container {{
                    position: absolute;
                    top: 220px;
                    left: 0; right: 0; bottom: 120px;
                }}
                .central-subject {{
                    position: absolute;
                    top: 50%; left: 50%;
                    transform: translate(-50%, -50%);
                    width: 440px;
                    height: 520px;
                    border-radius: 24px;
                    overflow: hidden;
                    box-shadow: 0 20px 50px rgba(0,0,0,0.6), 0 0 40px {theme['accent']}40;
                    border: 2px solid {theme['accent']};
                    z-index: 5;
                }}
                .central-subject img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                }}
                .art-tag-pointer {{
                    position: absolute;
                    bottom: 15px; left: 15px;
                    background: rgba(0,0,0,0.85);
                    color: {theme['accent']};
                    font-size: 12px;
                    font-weight: 800;
                    padding: 5px 12px;
                    border-radius: 14px;
                    z-index: 6;
                }}
                .callout-card {{
                    position: absolute;
                    width: 280px;
                    background: {theme['card_bg']};
                    backdrop-filter: blur(16px);
                    border: 1px solid {theme['card_border']};
                    border-radius: 12px;
                    padding: 14px 16px;
                    box-shadow: 0 8px 24px rgba(0,0,0,0.4);
                    z-index: 10;
                }}
                .callout-card h4 {{
                    font-size: 15px;
                    font-weight: 800;
                    color: {theme['accent']};
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                    margin-bottom: 5px;
                }}
                .callout-card p {{
                    font-size: 13px;
                    line-height: 1.4;
                    color: #e2e8f0;
                }}
                .pos-tl {{ top: 40px; left: 45px; }}
                .pos-ml {{ top: 290px; left: 35px; }}
                .pos-bl {{ bottom: 50px; left: 45px; }}
                .pos-tr {{ top: 40px; right: 45px; }}
                .pos-mr {{ top: 290px; right: 35px; }}
                .pos-br {{ bottom: 50px; right: 45px; }}
                .pointers-svg {{
                    position: absolute;
                    inset: 0; width: 100%; height: 100%;
                    pointer-events: none;
                    z-index: 8;
                }}
                .footer-bar {{
                    position: absolute;
                    bottom: 28px;
                    left: 45px; right: 45px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-top: 1px solid rgba(255,255,255,0.1);
                    padding-top: 14px;
                    font-size: 14px;
                    color: #94a3b8;
                    font-weight: 600;
                }}
                .footer-brand {{
                    color: #ffffff;
                    font-weight: 800;
                    letter-spacing: 1px;
                }}
                .footer-cta {{
                    color: {theme['accent']};
                    font-weight: 700;
                }}
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
                    <path d="M 325 110 L 420 180 L 460 260" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" />
                    <circle cx="460" cy="260" r="5" fill="{theme['accent']}" />
                    <path d="M 315 360 L 410 380 L 440 370" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" />
                    <circle cx="440" cy="370" r="5" fill="{theme['accent']}" />
                    <path d="M 325 800 L 410 740 L 460 670" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" />
                    <circle cx="460" cy="670" r="5" fill="{theme['accent']}" />
                    <path d="M 755 110 L 660 170 L 620 250" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" />
                    <circle cx="620" cy="250" r="5" fill="{theme['accent']}" />
                    <path d="M 765 360 L 670 420 L 640 450" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" />
                    <circle cx="640" cy="450" r="5" fill="{theme['accent']}" />
                    <path d="M 755 800 L 670 730 L 620 660" fill="none" stroke="{theme['accent']}" stroke-width="2" stroke-dasharray="4,4" />
                    <circle cx="620" cy="660" r="5" fill="{theme['accent']}" />
                </svg>
                <div class="central-subject">
                    <img src="{image_path}" />
                    <div class="art-tag-pointer">{art_label}</div>
                </div>
                <div class="callout-card pos-tl">
                    <h4>{callouts[0]['label']}</h4>
                    <p>{callouts[0]['text']}</p>
                </div>
                <div class="callout-card pos-ml">
                    <h4>{callouts[1]['label']}</h4>
                    <p>{callouts[1]['text']}</p>
                </div>
                <div class="callout-card pos-bl">
                    <h4>{callouts[2]['label']}</h4>
                    <p>{callouts[2]['text']}</p>
                </div>
                <div class="callout-card pos-tr">
                    <h4>{callouts[3]['label']}</h4>
                    <p>{callouts[3]['text']}</p>
                </div>
                <div class="callout-card pos-mr">
                    <h4>{callouts[4]['label']}</h4>
                    <p>{callouts[4]['text']}</p>
                </div>
                <div class="callout-card pos-br">
                    <h4>{callouts[5]['label']}</h4>
                    <p>{callouts[5]['text']}</p>
                </div>
            </div>
            <div class="footer-bar">
                <div class="footer-brand">{page_name.upper()} • {v_data['theme_name']}</div>
                <div class="footer-cta">FOLLOW @{page_name.upper()} FOR DAILY DOSSIERS</div>
            </div>
        </body>
        </html>
        """

    def _build_canva_poster_html(
        self,
        page_name: str,
        topic: Dict[str, Any],
        v_data: Dict[str, Any],
        theme: Dict[str, Any],
        image_path: str,
        art_label: str
    ) -> str:
        """Canva-Style Illustrated Nature Poster with Organic Dividers and Taxonomy (Ref 2)."""
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
                body {{
                    width: 1080px;
                    height: 1350px;
                    background-color: {theme['canvas_bg']};
                    font-family: 'Montserrat', sans-serif;
                    color: {theme['text_main']};
                    overflow: hidden;
                    position: relative;
                }}
                .header-banner {{
                    position: relative;
                    z-index: 10;
                    text-align: center;
                    padding-top: 45px;
                }}
                .header-banner h1 {{
                    font-size: 42px;
                    font-weight: 900;
                    letter-spacing: 1.5px;
                    color: {theme['accent']};
                    text-transform: uppercase;
                    line-height: 1.1;
                }}
                .header-banner .tagline {{
                    font-size: 18px;
                    font-weight: 700;
                    color: {theme['text_muted']};
                    letter-spacing: 2px;
                    text-transform: uppercase;
                    margin-top: 6px;
                }}
                .main-card {{
                    position: relative;
                    z-index: 10;
                    margin: 35px 50px;
                    background: {theme['card_bg']};
                    border: 2px solid {theme['card_border']};
                    border-radius: 20px;
                    padding: 26px;
                    display: grid;
                    grid-template-columns: 360px 1fr;
                    gap: 30px;
                    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
                }}
                .subject-img {{
                    width: 100%;
                    height: 520px;
                    border-radius: 16px;
                    overflow: hidden;
                    border: 2px solid {theme['accent']};
                    position: relative;
                }}
                .subject-img img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                }}
                .art-tag-canva {{
                    position: absolute;
                    bottom: 15px; left: 15px;
                    background: rgba(0,0,0,0.85);
                    color: #facc15;
                    font-size: 12px;
                    font-weight: 800;
                    padding: 5px 12px;
                    border-radius: 14px;
                }}
                .details-col {{
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }}
                .pill-badge {{
                    display: inline-block;
                    background: {theme['accent']};
                    color: #000;
                    font-size: 13px;
                    font-weight: 800;
                    padding: 5px 14px;
                    border-radius: 12px;
                    text-transform: uppercase;
                    margin-bottom: 8px;
                }}
                .details-col h2 {{
                    font-size: 32px;
                    font-weight: 800;
                    color: {theme['text_main']};
                    text-transform: uppercase;
                }}
                .details-col .latin {{
                    font-family: 'Playfair Display', serif;
                    font-style: italic;
                    font-size: 20px;
                    color: {theme['accent']};
                    margin-bottom: 14px;
                }}
                .details-col p {{
                    font-size: 16px;
                    line-height: 1.5;
                    color: {theme['text_sub']};
                }}
                .alert-box {{
                    background: rgba(0,0,0,0.25);
                    border-left: 5px solid {theme['accent']};
                    border-radius: 10px;
                    padding: 16px;
                    margin-top: 18px;
                }}
                .alert-box h4 {{
                    font-size: 15px;
                    font-weight: 800;
                    color: {theme['accent']};
                    text-transform: uppercase;
                    margin-bottom: 6px;
                }}
                .alert-box p {{
                    font-size: 14px;
                    line-height: 1.4;
                    color: {theme['text_sub']};
                }}
                .lower-shelf {{
                    margin: 0 50px;
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 20px;
                }}
                .shelf-card {{
                    background: {theme['card_bg']};
                    border: 1px solid {theme['card_border']};
                    border-radius: 16px;
                    padding: 20px;
                }}
                .shelf-card h4 {{
                    font-size: 16px;
                    font-weight: 800;
                    color: {theme['accent']};
                    margin-bottom: 6px;
                    text-transform: uppercase;
                }}
                .shelf-card p {{
                    font-size: 14px;
                    line-height: 1.45;
                    color: {theme['text_sub']};
                }}
                .footer-strip {{
                    position: absolute;
                    bottom: 24px;
                    left: 50px; right: 50px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    border-top: 1px solid {theme['card_border']};
                    padding-top: 14px;
                    font-size: 14px;
                    color: {theme['text_muted']};
                    font-weight: 700;
                }}
            </style>
        </head>
        <body>
            <div class="header-banner">
                <h1>{topic['title']}</h1>
                <div class="tagline">{v_data['badge_tag']}</div>
            </div>
            <div class="main-card">
                <div class="subject-img">
                    <img src="{image_path}" />
                    <div class="art-tag-canva">{art_label}</div>
                </div>
                <div class="details-col">
                    <div>
                        <div class="pill-badge">{topic.get('badge', v_data['badge_tag'])}</div>
                        <h2>{topic['title']}</h2>
                        <div class="latin">{topic.get('latin', v_data['theme_name'])}</div>
                        <p>{c1['text']}</p>
                    </div>
                    <div class="alert-box">
                        <h4>⚠️ KEY METHODOLOGY & SPECS</h4>
                        <p>{c2['text']}</p>
                    </div>
                </div>
            </div>
            <div class="lower-shelf">
                <div class="shelf-card">
                    <h4>PRO SPECIFICATIONS</h4>
                    <p>{topic.get('fun_fact', ['Authentic verified field facts'])[0]}</p>
                </div>
                <div class="shelf-card">
                    <h4>FIELD DISPATCH</h4>
                    <p>{topic.get('fun_fact', ['Authentic verified field facts'])[-1]}</p>
                </div>
            </div>
            <div class="footer-strip">
                <div>{page_name.upper()} • {v_data['theme_name']}</div>
                <div style="color: {theme['accent']};">FOLLOW @{page_name.upper()} FOR DAILY DOSSIERS</div>
            </div>
        </body>
        </html>
        """

    def _build_bento_dashboard_html(
        self,
        page_name: str,
        topic: Dict[str, Any],
        v_data: Dict[str, Any],
        theme: Dict[str, Any],
        image_path: str,
        art_label: str
    ) -> str:
        """Modern Bento Grid Dashboard with Massive Stat Meters."""
        stat1 = topic.get("stat_primary", "100%")
        stat1_lbl = topic.get("stat_primary_label", "Peak Performance Metric")
        stat2 = topic.get("stat_secondary", "0.1mm")
        stat2_lbl = topic.get("stat_secondary_label", "Micro-Engineering Precision")

        cards = topic.get("cards", [])
        c1 = cards[0] if len(cards) > 0 else {"label": "TECHNIQUE 01", "text": "Precision material calibration."}
        c2 = cards[1] if len(cards) > 1 else {"label": "TECHNIQUE 02", "text": "Dynamic chemical surface bonding."}
        c3 = cards[2] if len(cards) > 2 else {"label": "TECHNIQUE 03", "text": "Sub-surface refraction and polish."}

        pills = topic.get("fun_fact", [
            "Pure precision grade materials guaranteed.",
            "Tested under rigorous conditions.",
            "Verified by leading field naturalists."
        ])[:3]

        return f"""
        <!DOCTYPE html>
        <html>
        <head>
            <meta charset="UTF-8">
            <style>
                @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;600;700;800;900&family=Space+Grotesk:wght@700&display=swap');
                * {{ margin: 0; padding: 0; box-sizing: border-box; }}
                body {{
                    width: 1080px;
                    height: 1350px;
                    background-color: {theme['canvas_bg']};
                    font-family: 'Outfit', sans-serif;
                    color: {theme['text_main']};
                    overflow: hidden;
                    position: relative;
                    padding: 40px;
                }}
                .header-bar {{
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    margin-bottom: 25px;
                }}
                .header-left h1 {{
                    font-family: 'Space Grotesk', sans-serif;
                    font-size: 38px;
                    font-weight: 700;
                    letter-spacing: 0.5px;
                    text-transform: uppercase;
                    color: {theme['text_main']};
                }}
                .header-left .sub {{
                    color: {theme['text_muted']};
                    font-size: 16px;
                    margin-top: 4px;
                }}
                .badge-live {{
                    background: {theme['accent']};
                    color: #000;
                    font-size: 13px;
                    font-weight: 800;
                    padding: 6px 14px;
                    border-radius: 20px;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                }}
                .bento-grid {{
                    display: grid;
                    grid-template-columns: 1fr 1fr 1fr;
                    grid-template-rows: 240px 380px 240px 180px;
                    gap: 18px;
                }}
                .card {{
                    background: {theme['card_bg']};
                    border: 1px solid {theme['card_border']};
                    border-radius: 18px;
                    padding: 22px;
                    position: relative;
                    overflow: hidden;
                    display: flex;
                    flex-direction: column;
                    justify-content: space-between;
                }}
                .card-photo {{
                    grid-column: 1 / 3;
                    grid-row: 1 / 3;
                    padding: 0;
                    border: 2px solid {theme['card_border']};
                }}
                .card-photo img {{
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    display: block;
                }}
                .card-photo .overlay-tag {{
                    position: absolute;
                    bottom: 20px; left: 20px; right: 20px;
                    background: rgba(15, 23, 42, 0.85);
                    backdrop-filter: blur(10px);
                    border: 1px solid rgba(255,255,255,0.15);
                    padding: 16px 20px;
                    border-radius: 12px;
                }}
                .overlay-tag h3 {{
                    font-size: 22px;
                    font-weight: 800;
                    color: {theme['accent']};
                    margin-bottom: 4px;
                }}
                .overlay-tag p {{
                    font-size: 14px;
                    color: #cbd5e1;
                }}
                .card-stat1 {{
                    grid-column: 3 / 4;
                    grid-row: 1 / 2;
                    background: {theme['card_bg']};
                    border-color: {theme['accent']};
                }}
                .stat-number {{
                    font-size: 50px;
                    font-weight: 900;
                    color: {theme['accent']};
                    line-height: 1;
                }}
                .stat-label {{
                    font-size: 14px;
                    font-weight: 700;
                    color: {theme['text_sub']};
                    text-transform: uppercase;
                    letter-spacing: 0.5px;
                }}
                .card-stat2 {{
                    grid-column: 3 / 4;
                    grid-row: 2 / 3;
                    background: {theme['card_bg']};
                    border-color: {theme['accent_secondary']};
                }}
                .card-stat2 .stat-number {{
                    color: {theme['accent_secondary']};
                }}
                .card-mid1 {{
                    grid-column: 1 / 2;
                    grid-row: 3 / 4;
                    border-top: 4px solid {theme['accent']};
                }}
                .card-mid2 {{
                    grid-column: 2 / 3;
                    grid-row: 3 / 4;
                    border-top: 4px solid {theme['accent_secondary']};
                }}
                .card-mid3 {{
                    grid-column: 3 / 4;
                    grid-row: 3 / 4;
                    border-top: 4px solid #06b6d4;
                }}
                .card-tag {{
                    font-size: 13px;
                    font-weight: 800;
                    letter-spacing: 1px;
                    text-transform: uppercase;
                    margin-bottom: 8px;
                }}
                .card h4 {{
                    font-size: 18px;
                    font-weight: 800;
                    color: {theme['text_main']};
                    margin-bottom: 6px;
                }}
                .card p {{
                    font-size: 14px;
                    line-height: 1.45;
                    color: {theme['text_muted']};
                }}
                .card-bottom {{
                    grid-column: 1 / 4;
                    grid-row: 4 / 5;
                    display: flex;
                    flex-direction: row;
                    align-items: center;
                    justify-content: space-between;
                    padding: 18px 24px;
                    background: rgba(0,0,0,0.3);
                    border: 1px solid {theme['card_border']};
                }}
                .bottom-pill {{
                    flex: 1;
                    margin: 0 8px;
                    background: {theme['card_bg']};
                    border-radius: 10px;
                    padding: 12px 14px;
                    text-align: center;
                    border: 1px solid {theme['card_border']};
                }}
                .bottom-pill .pill-val {{
                    font-size: 14px;
                    font-weight: 700;
                    color: {theme['text_sub']};
                }}
                .footer-strip {{
                    position: absolute;
                    bottom: 12px;
                    left: 40px; right: 40px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 13px;
                    color: {theme['text_muted']};
                    font-weight: 600;
                }}
                .footer-strip .follow {{
                    color: {theme['accent']};
                    font-weight: 700;
                }}
            </style>
        </head>
        <body>
            <div class="header-bar">
                <div class="header-left">
                    <h1>{topic['title']}</h1>
                    <div class="sub">{topic.get('latin', v_data['badge_tag'])}</div>
                </div>
                <div class="badge-live">{topic.get('badge', v_data['badge_tag'])}</div>
            </div>
            <div class="bento-grid">
                <div class="card card-photo">
                    <img src="{image_path}" />
                    <div class="overlay-tag">
                        <h3>{topic['title']}</h3>
                        <p>{c1['text']}</p>
                    </div>
                </div>
                <div class="card card-stat1">
                    <div class="stat-number">{stat1}</div>
                    <div><div class="stat-label">{stat1_lbl}</div></div>
                </div>
                <div class="card card-stat2">
                    <div class="stat-number">{stat2}</div>
                    <div><div class="stat-label">{stat2_lbl}</div></div>
                </div>
                <div class="card card-mid1">
                    <div class="card-tag" style="color: {theme['accent']};">{c1['label']}</div>
                    <h4>{c1['label']}</h4>
                    <p>{c1['text']}</p>
                </div>
                <div class="card card-mid2">
                    <div class="card-tag" style="color: {theme['accent_secondary']};">{c2['label']}</div>
                    <h4>{c2['label']}</h4>
                    <p>{c2['text']}</p>
                </div>
                <div class="card card-mid3">
                    <div class="card-tag" style="color: #06b6d4;">{c3['label']}</div>
                    <h4>{c3['label']}</h4>
                    <p>{c3['text']}</p>
                </div>
                <div class="card card-bottom">
                    <div class="bottom-pill"><div class="pill-val">{pills[0]}</div></div>
                    <div class="bottom-pill"><div class="pill-val">{pills[1]}</div></div>
                    <div class="bottom-pill"><div class="pill-val">{pills[2]}</div></div>
                </div>
            </div>
            <div class="footer-strip">
                <div>{page_name.upper()} • {v_data['theme_name']}</div>
                <div class="follow">FOLLOW @{page_name.upper()} FOR DAILY SECRETS</div>
            </div>
        </body>
        </html>
        """

    def _build_cinematic_hero_html(
        self,
        page_name: str,
        topic: Dict[str, Any],
        v_data: Dict[str, Any],
        theme: Dict[str, Any],
        image_path: str,
        art_label: str
    ) -> str:
        """NatGeo Modern Magazine Cover with Frosted Glassmorphism (Ref 1/Hero)."""
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
                body {{
                    width: 1080px;
                    height: 1350px;
                    background-color: #000000;
                    font-family: 'Outfit', sans-serif;
                    color: #ffffff;
                    overflow: hidden;
                    position: relative;
                }}
                .hero-bg {{
                    position: absolute;
                    inset: 0; width: 100%; height: 100%;
                    object-fit: cover;
                    display: block;
                }}
                .gradient-mask {{
                    position: absolute;
                    inset: 0;
                    background: linear-gradient(180deg, rgba(0,0,0,0.7) 0%, rgba(0,0,0,0.1) 40%, rgba(0,0,0,0.92) 80%);
                }}
                .top-masthead {{
                    position: relative;
                    z-index: 10;
                    padding: 50px 60px;
                }}
                .category-badge {{
                    display: inline-block;
                    background: {theme['accent']};
                    color: #000;
                    font-size: 14px;
                    font-weight: 800;
                    letter-spacing: 2px;
                    padding: 6px 16px;
                    border-radius: 4px;
                    text-transform: uppercase;
                }}
                .headline-title {{
                    font-family: 'Bebas Neue', sans-serif;
                    font-size: 78px;
                    letter-spacing: 1px;
                    line-height: 0.95;
                    margin-top: 14px;
                    text-transform: uppercase;
                    color: #ffffff;
                    text-shadow: 0 4px 20px rgba(0,0,0,0.8);
                }}
                .latin-sub {{
                    font-size: 20px;
                    color: {theme['accent']};
                    margin-top: 6px;
                    font-weight: 600;
                    letter-spacing: 1px;
                }}
                .glass-panel {{
                    position: absolute;
                    bottom: 90px;
                    left: 60px; right: 60px;
                    background: rgba(15, 23, 42, 0.78);
                    backdrop-filter: blur(20px);
                    border: 1px solid rgba(255, 255, 255, 0.2);
                    border-radius: 20px;
                    padding: 30px;
                    display: grid;
                    grid-template-columns: 1fr 1fr;
                    gap: 30px;
                    z-index: 10;
                    box-shadow: 0 20px 50px rgba(0,0,0,0.6);
                }}
                .stat-box h4 {{
                    font-size: 18px;
                    font-weight: 800;
                    color: {theme['accent']};
                    text-transform: uppercase;
                    margin-bottom: 8px;
                }}
                .stat-box p {{
                    font-size: 15px;
                    line-height: 1.5;
                    color: #e2e8f0;
                }}
                .footer-strip {{
                    position: absolute;
                    bottom: 28px;
                    left: 60px; right: 60px;
                    display: flex;
                    justify-content: space-between;
                    align-items: center;
                    font-size: 14px;
                    color: #94a3b8;
                    font-weight: 700;
                    z-index: 10;
                }}
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
                <div class="stat-box">
                    <h4>{c1['label']}</h4>
                    <p>{c1['text']}</p>
                </div>
                <div class="stat-box">
                    <h4>{c2['label']}</h4>
                    <p>{c2['text']}</p>
                </div>
            </div>
            <div class="footer-strip">
                <div>{page_name.upper()} • {v_data['theme_name']}</div>
                <div style="color: {theme['accent']};">FOLLOW @{page_name.upper()} FOR DAILY DOSSIERS</div>
            </div>
        </body>
        </html>
        """

    # -------------------------------------------------------------------------
    # MAIN RENDERING DISPATCHER
    # -------------------------------------------------------------------------

    def render_infographic(
        self,
        page_name: str,
        vertical_key: str,
        topic: Dict[str, Any],
        output_path: str,
        template_name: Optional[str] = None,
        theme_name: Optional[str] = None,
        art_style_name: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Renders a Full HD 1080x1350 graphic using Playwright Chromium:
        - Cycles through 6 distinct art styles (Pixar 3D, Ghibli, 2D Vector, 8K Photo, Cyberpunk, Lithograph).
        - Cycles through 6 distinct templates and 6 vibrant multi-color palettes.
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
            topic, v_data.get("search_term", ""), art_style_name
        )

        # Build appropriate HTML
        if template_name == "vibrant_multicolor":
            html_content = self._build_vibrant_multicolor_html(page_name, topic, v_data, theme, image_local_or_url, art_label)
        elif template_name == "anatomical_pointer":
            html_content = self._build_anatomical_pointer_html(page_name, topic, v_data, theme, image_local_or_url, art_label)
        elif template_name == "bento_dashboard":
            html_content = self._build_bento_dashboard_html(page_name, topic, v_data, theme, image_local_or_url, art_label)
        elif template_name == "canva_poster":
            html_content = self._build_canva_poster_html(page_name, topic, v_data, theme, image_local_or_url, art_label)
        elif template_name == "cinematic_hero":
            html_content = self._build_cinematic_hero_html(page_name, topic, v_data, theme, image_local_or_url, art_label)
        else:
            html_content = self._build_vintage_fieldguide_html(page_name, topic, v_data, theme, image_local_or_url, art_label)

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

        caption = (
            f"🔥 {topic['title']} — {v_data['badge_tag']}\n\n"
            f"Mastering the authentic secrets of {topic['title']}:\n"
            f"Swipe through to discover the exact mechanics, techniques, and pro insights!\n\n"
            f"👉 Follow @{page_name} for daily field guides!\n\n"
            f"#{topic['slug']} #{vertical_key} #Infographic #{art_style_name} #Explore #FYP"
        )

        return {
            "image_path": output_path,
            "title": topic["title"],
            "caption": caption,
            "topic_slug": topic["slug"],
            "template_name": template_name,
            "theme_name": theme_name,
            "art_style_name": art_style_name
        }
