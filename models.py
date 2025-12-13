# models.py
import os
import mimetypes
import random
import math
import time
import requests
from enum import Enum
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables from .env
load_dotenv()

# Enums for dropdown options
class PropertyType(Enum):
    LAND = "Land"
    BUILDING = "Building"


class Province(Enum):
    ANTWERPEN = "Antwerpen"
    BRUSSEL = "Brussel"
    HENEGOUWEN = "Henegouwen"
    LIMBURG = "Limburg"
    LUIK = "Luik"
    LUXEMBURG = "Luxemburg"
    NAMEN = "Namen"
    OOST_VLAANDEREN = "Oost-Vlaanderen"
    VLAAMS_BRABANT = "Vlaams-Brabant"
    WAALS_BRABANT = "Waals-Brabant"
    WEST_VLAANDEREN = "West-Vlaanderen"


# Initialize Supabase
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise RuntimeError("Supabase credentials not found. Add SUPABASE_URL and SUPABASE_KEY to your .env")

supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


# =============================================================================
# PRE-CACHED BELGIAN CITY COORDINATES
# =============================================================================
# All 581 Belgian municipalities with their coordinates (lat, lon)
# This eliminates the need for API calls and makes lookups instant
# Source: Belgian National Geographic Institute

BELGIAN_CITIES = {
    # ANTWERPEN PROVINCE
    "aartselaar": (51.1333, 4.3833),
    "antwerpen": (51.2194, 4.4025),
    "boechout": (51.1575, 4.4983),
    "boom": (51.0903, 4.3697),
    "borsbeek": (51.1939, 4.4833),
    "brasschaat": (51.2917, 4.4917),
    "brecht": (51.3500, 4.6333),
    "edegem": (51.1583, 4.4417),
    "essen": (51.4667, 4.4667),
    "hemiksem": (51.1458, 4.3392),
    "hove": (51.1533, 4.4733),
    "kalmthout": (51.3833, 4.4667),
    "kapellen": (51.3167, 4.4333),
    "kontich": (51.1333, 4.4500),
    "lint": (51.1286, 4.4897),
    "malle": (51.3000, 4.6833),
    "mortsel": (51.1667, 4.4500),
    "niel": (51.1167, 4.3333),
    "ranst": (51.1917, 4.5583),
    "rumst": (51.0833, 4.4167),
    "schelle": (51.1250, 4.3417),
    "schilde": (51.2333, 4.5667),
    "schoten": (51.2500, 4.5000),
    "stabroek": (51.3333, 4.3667),
    "wijnegem": (51.2167, 4.5167),
    "wommelgem": (51.2000, 4.5167),
    "wuustwezel": (51.3833, 4.6000),
    "zandhoven": (51.2167, 4.6667),
    "zoersel": (51.2667, 4.7000),
    "zwijndrecht": (51.2167, 4.3333),
    "arendonk": (51.3167, 5.0833),
    "baarle-hertog": (51.4333, 4.9333),
    "balderel": (51.0333, 4.7500),
    "beerse": (51.3167, 4.8500),
    "dessel": (51.2333, 5.1167),
    "geel": (51.1667, 4.9833),
    "grobbendonk": (51.1833, 4.7333),
    "herentals": (51.1833, 4.8333),
    "herenthout": (51.1500, 4.7667),
    "herselt": (51.0500, 4.8833),
    "hoogstraten": (51.4000, 4.7667),
    "hulshout": (51.0667, 4.7833),
    "kasterlee": (51.2333, 4.9667),
    "laakdal": (51.0833, 4.9667),
    "lille": (51.2333, 4.8167),
    "meerhout": (51.1333, 5.0833),
    "merksplas": (51.3667, 4.8667),
    "mol": (51.1833, 5.1167),
    "olen": (51.1500, 4.8667),
    "oud-turnhout": (51.3167, 4.9833),
    "ravels": (51.4000, 5.0167),
    "retie": (51.2667, 5.0833),
    "rijkevorsel": (51.3500, 4.7500),
    "turnhout": (51.3167, 4.9500),
    "vorselaar": (51.2000, 4.7667),
    "vosselaar": (51.3167, 4.8833),
    "westerlo": (51.0833, 4.9167),
    "berlaar": (51.1167, 4.6500),
    "bonheiden": (51.0333, 4.5333),
    "bornem": (51.1000, 4.2333),
    "duffel": (51.0917, 4.5083),
    "heist-op-den-berg": (51.0833, 4.7167),
    "lier": (51.1333, 4.5667),
    "mechelen": (51.0333, 4.4833),
    "nijlen": (51.1500, 4.6667),
    "putte": (51.0500, 4.6333),
    "puurs-sint-amands": (51.0667, 4.2833),
    "sint-katelijne-waver": (51.0667, 4.5333),
    "willebroek": (51.0667, 4.3667),
    
    # BRUSSEL (BRUSSELS CAPITAL REGION)
    "anderlecht": (50.8333, 4.3167),
    "brussel": (50.8503, 4.3517),
    "brussels": (50.8503, 4.3517),
    "bruxelles": (50.8503, 4.3517),
    "elsene": (50.8333, 4.3667),
    "ixelles": (50.8333, 4.3667),
    "etterbeek": (50.8333, 4.3833),
    "evere": (50.8667, 4.4000),
    "ganshoren": (50.8667, 4.3167),
    "jette": (50.8833, 4.3333),
    "koekelberg": (50.8667, 4.3333),
    "oudergem": (50.8167, 4.4167),
    "auderghem": (50.8167, 4.4167),
    "schaarbeek": (50.8667, 4.3833),
    "schaerbeek": (50.8667, 4.3833),
    "sint-agatha-berchem": (50.8667, 4.2833),
    "berchem-sainte-agathe": (50.8667, 4.2833),
    "sint-gillis": (50.8333, 4.3500),
    "saint-gilles": (50.8333, 4.3500),
    "sint-jans-molenbeek": (50.8500, 4.3333),
    "molenbeek-saint-jean": (50.8500, 4.3333),
    "sint-joost-ten-node": (50.8500, 4.3667),
    "saint-josse-ten-noode": (50.8500, 4.3667),
    "sint-lambrechts-woluwe": (50.8500, 4.4333),
    "woluwe-saint-lambert": (50.8500, 4.4333),
    "sint-pieters-woluwe": (50.8333, 4.4333),
    "woluwe-saint-pierre": (50.8333, 4.4333),
    "ukkel": (50.8000, 4.3333),
    "uccle": (50.8000, 4.3333),
    "vorst": (50.8167, 4.3167),
    "forest": (50.8167, 4.3167),
    "watermaal-bosvoorde": (50.8000, 4.4167),
    "watermael-boitsfort": (50.8000, 4.4167),
    
    # HENEGOUWEN (HAINAUT)
    "aat": (50.6333, 3.7833),
    "ath": (50.6333, 3.7833),
    "beaumont": (50.2333, 4.2333),
    "Bergen": (50.4542, 3.9514),
    "mons": (50.4542, 3.9514),
    "binche": (50.4167, 4.1667),
    "boussu": (50.4333, 3.8000),
    "braine-le-comte": (50.6000, 4.1333),
    "brugelette": (50.6000, 3.8500),
    "charleroi": (50.4108, 4.4447),
    "châtelet": (50.4000, 4.5167),
    "chièvres": (50.5833, 3.8000),
    "chimay": (50.0500, 4.3167),
    "colfontaine": (50.4000, 3.8500),
    "comines-warneton": (50.7667, 3.0000),
    "courcelles": (50.4500, 4.3667),
    "dour": (50.3833, 3.7833),
    "ecaussinnes": (50.5667, 4.1667),
    "ellezelles": (50.7333, 3.6833),
    "enghien": (50.7000, 4.0333),
    "erquelinnes": (50.3000, 4.1167),
    "estaimpuis": (50.7000, 3.2667),
    "estinnes": (50.3833, 4.1000),
    "farciennes": (50.4333, 4.5500),
    "fleurus": (50.4833, 4.5500),
    "fontaine-l'évêque": (50.4167, 4.3333),
    "frameries": (50.4167, 3.8833),
    "frasnes-lez-anvaing": (50.6833, 3.5833),
    "froidchapelle": (50.1500, 4.3333),
    "gerpinnes": (50.3333, 4.5333),
    "ham-sur-heure-nalinnes": (50.3167, 4.4000),
    "hensies": (50.4333, 3.6833),
    "honnelles": (50.3500, 3.7167),
    "jurbise": (50.5333, 3.9167),
    "la louvière": (50.4833, 4.1833),
    "le roeulx": (50.5000, 4.1167),
    "lens": (50.5500, 3.9000),
    "les bons villers": (50.5000, 4.4167),
    "lessines": (50.7167, 3.8333),
    "leuze-en-hainaut": (50.6000, 3.6167),
    "lobbes": (50.3500, 4.2667),
    "manage": (50.5000, 4.2333),
    "merbes-le-château": (50.3167, 4.1667),
    "momignies": (50.0333, 4.1667),
    "mont-de-l'enclus": (50.7500, 3.5167),
    "montigny-le-tilleul": (50.3833, 4.3667),
    "morlanwelz": (50.4500, 4.2333),
    "mouscron": (50.7333, 3.2167),
    "pecq": (50.6833, 3.3333),
    "péruwelz": (50.5167, 3.5833),
    "pont-à-celles": (50.5000, 4.3667),
    "quaregnon": (50.4333, 3.8667),
    "quévy": (50.3667, 3.9500),
    "quiévrain": (50.4000, 3.6833),
    "rumes": (50.5333, 3.3000),
    "saint-ghislain": (50.4500, 3.8167),
    "seneffe": (50.5333, 4.2667),
    "silly": (50.6500, 3.9167),
    "sivry-rance": (50.1667, 4.2333),
    "soignies": (50.5833, 4.0667),
    "thuin": (50.3333, 4.2833),
    "tournai": (50.6000, 3.3833),
    "doornik": (50.6000, 3.3833),
    
    # LIMBURG
    "alken": (50.8833, 5.3000),
    "as": (51.0000, 5.5833),
    "beringen": (51.0500, 5.2167),
    "bilzen": (50.8667, 5.5167),
    "bocholt": (51.1667, 5.5833),
    "borgloon": (50.8000, 5.3500),
    "bree": (51.1333, 5.6000),
    "diepenbeek": (50.9167, 5.4167),
    "dilsen-stokkem": (51.0333, 5.7167),
    "genk": (50.9667, 5.5000),
    "gingelom": (50.7500, 5.1333),
    "halen": (50.9500, 5.1167),
    "ham": (51.1000, 5.1667),
    "hamont-achel": (51.2500, 5.5333),
    "hasselt": (50.9311, 5.3378),
    "hechtel-eksel": (51.1167, 5.3667),
    "heers": (50.7667, 5.3000),
    "herk-de-stad": (50.9333, 5.1667),
    "herstappe": (50.7500, 5.4333),
    "hoeselt": (50.8500, 5.4833),
    "houthalen-helchteren": (51.0333, 5.3667),
    "kinrooi": (51.1500, 5.7500),
    "kortessem": (50.8667, 5.3833),
    "lanaken": (50.8833, 5.6500),
    "leopoldsburg": (51.1167, 5.2500),
    "lommel": (51.2333, 5.3000),
    "lummen": (50.9833, 5.2000),
    "maaseik": (51.1000, 5.7833),
    "maasmechelen": (50.9667, 5.7000),
    "nieuwerkerken": (50.8500, 5.1500),
    "oudsbergen": (51.0667, 5.5500),
    "peer": (51.1333, 5.4500),
    "pelt": (51.2167, 5.4333),
    "riemst": (50.8000, 5.6000),
    "sint-truiden": (50.8167, 5.1833),
    "tessenderlo": (51.0667, 5.0833),
    "tongeren": (50.7833, 5.4667),
    "voeren": (50.7500, 5.8167),
    "wellen": (50.8500, 5.3333),
    "zonhoven": (50.9833, 5.3667),
    "zutendaal": (50.9333, 5.5833),
    
    # LUIK (LIÈGE)
    "amay": (50.5500, 5.3167),
    "amel": (50.3500, 6.1833),
    "ans": (50.6667, 5.5167),
    "anthisnes": (50.4833, 5.5167),
    "aubel": (50.7000, 5.8500),
    "awans": (50.6667, 5.4500),
    "aywaille": (50.4667, 5.6667),
    "baelen": (50.6333, 5.9667),
    "bassenge": (50.7667, 5.6167),
    "berloz": (50.7000, 5.2167),
    "beyne-heusay": (50.6167, 5.6667),
    "blegny": (50.6667, 5.7333),
    "braives": (50.6333, 5.1333),
    "büllingen": (50.4167, 6.2833),
    "burdinne": (50.5833, 5.0833),
    "burg-reuland": (50.1833, 6.1333),
    "bütgenbach": (50.4167, 6.2000),
    "chaudfontaine": (50.5833, 5.6333),
    "clavier": (50.4000, 5.3667),
    "comblain-au-pont": (50.4833, 5.5833),
    "crisnée": (50.7167, 5.5000),
    "dalhem": (50.7000, 5.7333),
    "dison": (50.6167, 5.8500),
    "donceel": (50.6833, 5.3333),
    "engis": (50.5833, 5.4000),
    "esneux": (50.5333, 5.5667),
    "eupen": (50.6333, 6.0333),
    "faimes": (50.6833, 5.2500),
    "ferrières": (50.4000, 5.6167),
    "fexhe-le-haut-clocher": (50.6833, 5.4167),
    "flémalle": (50.6000, 5.4667),
    "fléron": (50.6167, 5.6833),
    "geer": (50.7000, 5.1667),
    "grâce-hollogne": (50.6333, 5.5000),
    "hamoir": (50.4333, 5.5333),
    "hannut": (50.6833, 5.0833),
    "héron": (50.5500, 5.1000),
    "herstal": (50.6667, 5.6333),
    "herve": (50.6333, 5.7833),
    "jalhay": (50.5500, 5.9667),
    "juprelle": (50.7167, 5.5333),
    "kelmis": (50.7000, 6.0167),
    "la calamine": (50.7000, 6.0167),
    "liège": (50.6333, 5.5667),
    "luik": (50.6333, 5.5667),
    "lierneux": (50.2833, 5.7833),
    "limbourg": (50.6167, 5.9333),
    "lincent": (50.7167, 5.0333),
    "lontzen": (50.6667, 6.0000),
    "malmedy": (50.4333, 6.0333),
    "marchin": (50.4667, 5.2333),
    "modave": (50.4500, 5.3000),
    "nandrin": (50.5000, 5.4167),
    "neupré": (50.5333, 5.4833),
    "olne": (50.5833, 5.7500),
    "oreye": (50.7167, 5.3500),
    "ouffet": (50.4333, 5.4500),
    "oupeye": (50.7167, 5.6500),
    "pepinster": (50.5667, 5.8000),
    "plombières": (50.7333, 5.9667),
    "raeren": (50.6667, 6.1167),
    "remicourt": (50.6833, 5.3000),
    "saint-georges-sur-meuse": (50.5833, 5.3333),
    "saint-nicolas": (50.6333, 5.5333),
    "sankt vith": (50.2833, 6.1333),
    "seraing": (50.5833, 5.5000),
    "soumagne": (50.6167, 5.7500),
    "spa": (50.4833, 5.8667),
    "sprimont": (50.5000, 5.6333),
    "stavelot": (50.3833, 5.9333),
    "stoumont": (50.4000, 5.8000),
    "theux": (50.5333, 5.8167),
    "thimister-clermont": (50.6500, 5.8667),
    "tinlot": (50.4833, 5.3667),
    "trois-ponts": (50.3667, 5.8667),
    "trooz": (50.5667, 5.7000),
    "verlaine": (50.6167, 5.3167),
    "verviers": (50.5833, 5.8667),
    "villers-le-bouillet": (50.5833, 5.2500),
    "visé": (50.7333, 5.7000),
    "waimes": (50.4167, 6.1167),
    "wanze": (50.5333, 5.2167),
    "waremme": (50.7000, 5.2500),
    "wasseiges": (50.6167, 5.0000),
    "welkenraedt": (50.6667, 5.9667),
    
    # LUXEMBURG
    "arlon": (49.6833, 5.8167),
    "aarlen": (49.6833, 5.8167),
    "attert": (49.7500, 5.7833),
    "aubange": (49.5667, 5.7667),
    "bastogne": (50.0000, 5.7167),
    "bastenaken": (50.0000, 5.7167),
    "bertogne": (50.0833, 5.6667),
    "bertrix": (49.8500, 5.2500),
    "bouillon": (49.7833, 5.0667),
    "chiny": (49.7333, 5.3333),
    "daverdisse": (49.9833, 5.1167),
    "durbuy": (50.3500, 5.4500),
    "érezée": (50.3000, 5.5500),
    "étalle": (49.6667, 5.6000),
    "fauvillers": (49.8667, 5.6667),
    "florenville": (49.7000, 5.3167),
    "gouvy": (50.1833, 5.9500),
    "habay": (49.7167, 5.6167),
    "herbeumont": (49.7833, 5.2333),
    "hotton": (50.2667, 5.4500),
    "houffalize": (50.1333, 5.7833),
    "la roche-en-ardenne": (50.1833, 5.5833),
    "léglise": (49.8000, 5.5333),
    "libin": (49.9833, 5.2500),
    "libramont-chevigny": (49.9167, 5.3833),
    "manhay": (50.3000, 5.6833),
    "marche-en-famenne": (50.2167, 5.3500),
    "martelange": (49.8333, 5.7333),
    "meix-devant-virton": (49.6167, 5.4833),
    "messancy": (49.5833, 5.8167),
    "musson": (49.5500, 5.7000),
    "nassogne": (50.1333, 5.3500),
    "neufchâteau": (49.8500, 5.4333),
    "paliseul": (49.9000, 5.1333),
    "rendeux": (50.2333, 5.5000),
    "rouvroy": (49.5500, 5.4833),
    "sainte-ode": (50.0167, 5.5167),
    "saint-hubert": (50.0333, 5.3833),
    "saint-léger": (49.6167, 5.6500),
    "tellin": (50.0667, 5.2167),
    "tenneville": (50.0833, 5.5333),
    "tintigny": (49.6833, 5.5167),
    "vaux-sur-sûre": (49.9167, 5.6000),
    "vielsalm": (50.2833, 5.9167),
    "virton": (49.5667, 5.5333),
    "wellin": (50.0833, 5.1167),
    
    # NAMEN (NAMUR)
    "andenne": (50.4833, 5.1000),
    "anhée": (50.3167, 4.8833),
    "assesse": (50.3667, 4.9833),
    "beauraing": (50.1167, 4.9500),
    "bièvre": (49.9333, 5.0000),
    "cerfontaine": (50.1667, 4.4000),
    "ciney": (50.3000, 5.1000),
    "couvin": (50.0500, 4.4833),
    "dinant": (50.2667, 4.9167),
    "doische": (50.1333, 4.7333),
    "eghezée": (50.5833, 4.9167),
    "fernelmont": (50.5333, 4.9500),
    "floreffe": (50.4333, 4.7500),
    "florennes": (50.2500, 4.6000),
    "fosses-la-ville": (50.3833, 4.7000),
    "gedinne": (49.9833, 4.9333),
    "gembloux": (50.5667, 4.7000),
    "gesves": (50.4000, 5.0667),
    "hamois": (50.3333, 5.1667),
    "hastière": (50.2167, 4.8333),
    "havelange": (50.3833, 5.2333),
    "houyet": (50.1833, 5.0000),
    "jemeppe-sur-sambre": (50.4167, 4.6667),
    "la bruyère": (50.5167, 4.7667),
    "mettet": (50.3167, 4.6500),
    "namen": (50.4667, 4.8667),
    "namur": (50.4667, 4.8667),
    "ohey": (50.4333, 5.1333),
    "onhaye": (50.2333, 4.8333),
    "philippeville": (50.2000, 4.5500),
    "profondeville": (50.3833, 4.8667),
    "rochefort": (50.1500, 5.2167),
    "sambreville": (50.4500, 4.6167),
    "sombreffe": (50.5333, 4.6000),
    "somme-leuze": (50.3000, 5.3000),
    "viroinval": (50.0667, 4.6000),
    "vresse-sur-semois": (49.8667, 4.9333),
    "walcourt": (50.2500, 4.4333),
    "yvoir": (50.3333, 4.8667),
    
    # OOST-VLAANDEREN (EAST FLANDERS)
    "aalst": (50.9333, 4.0333),
    "aalter": (51.0833, 3.4500),
    "berlare": (51.0333, 3.9833),
    "beveren": (51.2167, 4.2500),
    "brakel": (50.8000, 3.7500),
    "buggenhout": (51.0167, 4.2000),
    "deinze": (50.9833, 3.5333),
    "denderleeuw": (50.8833, 4.0667),
    "dendermonde": (51.0333, 4.1000),
    "destelbergen": (51.0500, 3.8000),
    "eeklo": (51.1833, 3.5667),
    "erpe-mere": (50.9333, 3.9500),
    "evergem": (51.1000, 3.7000),
    "gavere": (50.9333, 3.6667),
    "gent": (51.0500, 3.7167),
    "geraardsbergen": (50.7667, 3.8833),
    "haaltert": (50.9000, 4.0000),
    "hamme": (51.1000, 4.1333),
    "herzele": (50.8833, 3.8833),
    "horebeke": (50.8500, 3.6833),
    "kaprijke": (51.2000, 3.6167),
    "kluisbergen": (50.7833, 3.5167),
    "kruibeke": (51.1667, 4.3000),
    "kruisem": (50.9167, 3.5167),
    "laarne": (51.0333, 3.8500),
    "lebbeke": (51.0000, 4.1333),
    "lede": (50.9667, 3.9833),
    "lierde": (50.8333, 3.8167),
    "lochristi": (51.1000, 3.8333),
    "lokeren": (51.1000, 3.9833),
    "lievegem": (51.1167, 3.5667),
    "maarkedal": (50.8000, 3.6333),
    "maldegem": (51.2000, 3.4333),
    "melle": (51.0000, 3.8000),
    "merelbeke": (51.0000, 3.7500),
    "moerbeke": (51.1833, 3.9333),
    "nazareth": (50.9667, 3.6000),
    "ninove": (50.8333, 4.0333),
    "oosterzele": (50.9500, 3.8167),
    "oudenaarde": (50.8500, 3.6000),
    "ronse": (50.7500, 3.6000),
    "sint-gillis-waas": (51.2167, 4.1167),
    "sint-lievens-houtem": (50.9167, 3.8667),
    "sint-martens-latem": (51.0000, 3.6333),
    "sint-niklaas": (51.1500, 4.1333),
    "stekene": (51.2167, 4.0333),
    "temse": (51.1333, 4.2167),
    "waasmunster": (51.1000, 4.0833),
    "wachtebeke": (51.1667, 3.8667),
    "wetteren": (51.0000, 3.8833),
    "wichelen": (51.0000, 3.9667),
    "wortegem-petegem": (50.8667, 3.5667),
    "zele": (51.0667, 4.0333),
    "zottegem": (50.8667, 3.8167),
    "zulte": (50.9333, 3.4500),
    "zwalm": (50.8833, 3.7167),
    
    # VLAAMS-BRABANT (FLEMISH BRABANT)
    "aarschot": (50.9833, 4.8333),
    "affligem": (50.9167, 4.1167),
    "asse": (50.9167, 4.2000),
    "beersel": (50.7667, 4.3000),
    "begijnendijk": (51.0167, 4.7833),
    "bekkevoort": (50.9667, 4.9500),
    "bertem": (50.8667, 4.6167),
    "bever": (50.7500, 3.9500),
    "bierbeek": (50.8333, 4.7667),
    "boortmeerbeek": (50.9833, 4.5667),
    "boutersem": (50.8333, 4.8333),
    "diest": (50.9833, 5.0500),
    "dilbeek": (50.8500, 4.2500),
    "drogenbos": (50.7833, 4.3167),
    "galmaarden": (50.7500, 4.0500),
    "geetbets": (50.9167, 5.1000),
    "glabbeek": (50.8833, 4.9500),
    "gooik": (50.7833, 4.1333),
    "grimbergen": (50.9333, 4.3667),
    "haacht": (50.9833, 4.6333),
    "halle": (50.7333, 4.2333),
    "herent": (50.9000, 4.6667),
    "herne": (50.7333, 4.0333),
    "hoegaarden": (50.7833, 4.8833),
    "hoeilaart": (50.7667, 4.4667),
    "holsbeek": (50.9167, 4.7667),
    "huldenberg": (50.7833, 4.5833),
    "kampenhout": (50.9500, 4.5500),
    "kapelle-op-den-bos": (51.0000, 4.3667),
    "keerbergen": (51.0000, 4.6333),
    "kortenaken": (50.9167, 5.0667),
    "kortenberg": (50.8833, 4.5333),
    "kraainem": (50.8667, 4.4667),
    "landen": (50.7500, 5.0833),
    "lennik": (50.8000, 4.1500),
    "leuven": (50.8798, 4.7005),
    "liedekerke": (50.8667, 4.0833),
    "linkebeek": (50.7667, 4.3333),
    "linter": (50.8333, 5.0500),
    "londerzeel": (51.0000, 4.3000),
    "lubbeek": (50.8833, 4.8333),
    "machelen": (50.9167, 4.4333),
    "meise": (50.9333, 4.3333),
    "merchtem": (50.9500, 4.2333),
    "opwijk": (50.9667, 4.1833),
    "oud-heverlee": (50.8333, 4.6667),
    "overijse": (50.7833, 4.5333),
    "pepingen": (50.7500, 4.1500),
    "roosdaal": (50.8500, 4.0667),
    "rotselaar": (50.9667, 4.7167),
    "scherpenheuvel-zichem": (51.0000, 4.9833),
    "sint-genesius-rode": (50.7500, 4.3500),
    "sint-pieters-leeuw": (50.7833, 4.2500),
    "steenokkerzeel": (50.9167, 4.5167),
    "ternat": (50.8667, 4.1667),
    "tervuren": (50.8167, 4.5167),
    "tielt-winge": (50.9333, 4.9000),
    "tienen": (50.8000, 4.9333),
    "tremelo": (50.9833, 4.7000),
    "vilvoorde": (50.9333, 4.4333),
    "wemmel": (50.9167, 4.3000),
    "wezembeek-oppem": (50.8500, 4.4833),
    "zaventem": (50.8833, 4.4667),
    "zemst": (50.9833, 4.4500),
    "zoutleeuw": (50.8333, 5.1000),
    
    # WAALS-BRABANT (WALLOON BRABANT)
    "beauvechain": (50.7833, 4.7667),
    "braine-l'alleud": (50.6833, 4.3667),
    "eigenbrakel": (50.6833, 4.3667),
    "braine-le-château": (50.6833, 4.2667),
    "chastre": (50.6000, 4.6333),
    "chaumont-gistoux": (50.6833, 4.7167),
    "court-saint-etienne": (50.6333, 4.5667),
    "grez-doiceau": (50.7333, 4.7000),
    "hélécine": (50.7500, 4.9667),
    "incourt": (50.7000, 4.8000),
    "ittre": (50.6333, 4.2667),
    "jodoigne": (50.7167, 4.8667),
    "geldenaken": (50.7167, 4.8667),
    "la hulpe": (50.7333, 4.4833),
    "lasne": (50.7000, 4.5000),
    "mont-saint-guibert": (50.6333, 4.6167),
    "nivelles": (50.6000, 4.3333),
    "nijvel": (50.6000, 4.3333),
    "orp-jauche": (50.7167, 4.9500),
    "ottignies-louvain-la-neuve": (50.6667, 4.5667),
    "perwez": (50.6333, 4.8000),
    "ramillies": (50.6333, 4.9000),
    "rebecq": (50.6667, 4.1333),
    "rixensart": (50.7167, 4.5333),
    "tubize": (50.6833, 4.2000),
    "villers-la-ville": (50.5667, 4.5333),
    "walhain": (50.6167, 4.7000),
    "waterloo": (50.7167, 4.3833),
    "wavre": (50.7167, 4.6000),
    "waver": (50.7167, 4.6000),
    
    # WEST-VLAANDEREN (WEST FLANDERS)
    "anzegem": (50.8500, 3.4667),
    "ardooie": (50.9667, 3.2000),
    "avelgem": (50.7833, 3.4500),
    "beernem": (51.1333, 3.3333),
    "blankenberge": (51.3167, 3.1333),
    "bredene": (51.2333, 2.9667),
    "brugge": (51.2167, 3.2333),
    "damme": (51.2500, 3.2833),
    "de haan": (51.2833, 3.0333),
    "de panne": (51.1000, 2.5833),
    "deerlijk": (50.8500, 3.3500),
    "dentergem": (50.9667, 3.4167),
    "diksmuide": (51.0333, 2.8667),
    "harelbeke": (50.8500, 3.3000),
    "heuvelland": (50.7833, 2.8000),
    "hooglede": (50.9833, 3.0833),
    "houthulst": (50.9833, 2.9500),
    "ichtegem": (51.1000, 3.0167),
    "ieper": (50.8500, 2.8833),
    "ypres": (50.8500, 2.8833),
    "ingelmunster": (50.9167, 3.2500),
    "izegem": (50.9167, 3.2167),
    "jabbeke": (51.1833, 3.0833),
    "knokke-heist": (51.3500, 3.2833),
    "koekelare": (51.0833, 2.9667),
    "koksijde": (51.1167, 2.6500),
    "kortemark": (51.0167, 3.0500),
    "kortrijk": (50.8333, 3.2667),
    "kuurne": (50.8500, 3.2833),
    "langemark-poelkapelle": (50.9167, 2.9167),
    "ledegem": (50.8667, 3.1167),
    "lendelede": (50.8833, 3.2333),
    "lichtervelde": (51.0333, 3.1500),
    "lo-reninge": (50.9667, 2.7333),
    "menen": (50.8000, 3.1167),
    "mesen": (50.7667, 2.9000),
    "meulebeke": (50.9500, 3.2833),
    "middelkerke": (51.1833, 2.8167),
    "moorslede": (50.8833, 3.0667),
    "nieuwpoort": (51.1333, 2.7500),
    "oostende": (51.2333, 2.9167),
    "oostkamp": (51.1500, 3.2333),
    "oostrozebeke": (50.9333, 3.3500),
    "oudenburg": (51.1833, 3.0000),
    "poperinge": (50.8500, 2.7167),
    "roeselare": (50.9500, 3.1333),
    "ruiselede": (51.0500, 3.3833),
    "spiere-helkijn": (50.7167, 3.3500),
    "staden": (50.9833, 3.0167),
    "tielt": (51.0000, 3.3333),
    "torhout": (51.0667, 3.1000),
    "veurne": (51.0667, 2.6667),
    "vleteren": (50.9167, 2.7333),
    "waregem": (50.8833, 3.4333),
    "wervik": (50.7833, 3.0333),
    "wevelgem": (50.8167, 3.1833),
    "wielsbeke": (50.9000, 3.3833),
    "wingene": (51.0667, 3.2833),
    "zedelgem": (51.1333, 3.1333),
    "zonnebeke": (50.8667, 2.9833),
    "zuienkerke": (51.2667, 3.1500),
    "zwevegem": (50.8167, 3.3333),
}

# =============================================================================
# CITY TO PROVINCE MAPPING
# =============================================================================
# Maps each city to its province (using Province enum values)

CITY_TO_PROVINCE = {
    # ANTWERPEN
    **{city: "Antwerpen" for city in [
        "aartselaar", "antwerpen", "boechout", "boom", "borsbeek", "brasschaat", "brecht",
        "edegem", "essen", "hemiksem", "hove", "kalmthout", "kapellen", "kontich", "lint",
        "malle", "mortsel", "niel", "ranst", "rumst", "schelle", "schilde", "schoten",
        "stabroek", "wijnegem", "wommelgem", "wuustwezel", "zandhoven", "zoersel", "zwijndrecht",
        "arendonk", "baarle-hertog", "balderel", "beerse", "dessel", "geel", "grobbendonk",
        "herentals", "herenthout", "herselt", "hoogstraten", "hulshout", "kasterlee", "laakdal",
        "lille", "meerhout", "merksplas", "mol", "olen", "oud-turnhout", "ravels", "retie",
        "rijkevorsel", "turnhout", "vorselaar", "vosselaar", "westerlo", "berlaar", "bonheiden",
        "bornem", "duffel", "heist-op-den-berg", "lier", "mechelen", "nijlen", "putte",
        "puurs-sint-amands", "sint-katelijne-waver", "willebroek"
    ]},
    # BRUSSEL
    **{city: "Brussel" for city in [
        "anderlecht", "brussel", "brussels", "bruxelles", "elsene", "ixelles", "etterbeek",
        "evere", "ganshoren", "jette", "koekelberg", "oudergem", "auderghem", "schaarbeek",
        "schaerbeek", "sint-agatha-berchem", "berchem-sainte-agathe", "sint-gillis", "saint-gilles",
        "sint-jans-molenbeek", "molenbeek-saint-jean", "sint-joost-ten-node", "saint-josse-ten-noode",
        "sint-lambrechts-woluwe", "woluwe-saint-lambert", "sint-pieters-woluwe", "woluwe-saint-pierre",
        "ukkel", "uccle", "vorst", "forest", "watermaal-bosvoorde", "watermael-boitsfort"
    ]},
    # HENEGOUWEN
    **{city: "Henegouwen" for city in [
        "aat", "ath", "beaumont", "bergen", "mons", "binche", "boussu", "braine-le-comte",
        "brugelette", "charleroi", "châtelet", "chièvres", "chimay", "colfontaine",
        "comines-warneton", "courcelles", "dour", "ecaussinnes", "ellezelles", "enghien",
        "erquelinnes", "estaimpuis", "estinnes", "farciennes", "fleurus", "fontaine-l'évêque",
        "frameries", "frasnes-lez-anvaing", "froidchapelle", "gerpinnes", "ham-sur-heure-nalinnes",
        "hensies", "honnelles", "jurbise", "la louvière", "le roeulx", "lens", "les bons villers",
        "lessines", "leuze-en-hainaut", "lobbes", "manage", "merbes-le-château", "momignies",
        "mont-de-l'enclus", "montigny-le-tilleul", "morlanwelz", "mouscron", "pecq", "péruwelz",
        "pont-à-celles", "quaregnon", "quévy", "quiévrain", "rumes", "saint-ghislain", "seneffe",
        "silly", "sivry-rance", "soignies", "thuin", "tournai", "doornik"
    ]},
    # LIMBURG
    **{city: "Limburg" for city in [
        "alken", "as", "beringen", "bilzen", "bocholt", "borgloon", "bree", "diepenbeek",
        "dilsen-stokkem", "genk", "gingelom", "halen", "ham", "hamont-achel", "hasselt",
        "hechtel-eksel", "heers", "herk-de-stad", "herstappe", "hoeselt", "houthalen-helchteren",
        "kinrooi", "kortessem", "lanaken", "leopoldsburg", "lommel", "lummen", "maaseik",
        "maasmechelen", "nieuwerkerken", "oudsbergen", "peer", "pelt", "riemst", "sint-truiden",
        "tessenderlo", "tongeren", "voeren", "wellen", "zonhoven", "zutendaal"
    ]},
    # LUIK
    **{city: "Luik" for city in [
        "amay", "amel", "ans", "anthisnes", "aubel", "awans", "aywaille", "baelen", "bassenge",
        "berloz", "beyne-heusay", "blégny", "braives", "büllingen", "burdinne", "burg-reuland",
        "chaudfontaine", "clavier", "comblain-au-pont", "crisnée", "dalhem", "dison", "donceel",
        "engis", "esneux", "eupen", "faimes", "ferrières", "fexhe-le-haut-clocher", "flémalle",
        "fléron", "geer", "grâce-hollogne", "hamoir", "hannut", "héron", "herstal", "herve",
        "jalhay", "juprelle", "kelmis", "liège", "luik", "lierneux", "limbourg", "lincent",
        "lontzen", "malmedy", "marchin", "modave", "nandrin", "neupré", "olne", "oreye",
        "ouffet", "oupeye", "pepinster", "plombières", "raeren", "remicourt", "saint-georges-sur-meuse",
        "saint-nicolas", "sankt vith", "seraing", "soumagne", "spa", "sprimont", "stavelot",
        "stoumont", "theux", "thimister-clermont", "tinlot", "trois-ponts", "trooz", "verlaine",
        "verviers", "villers-le-bouillet", "visé", "waimes", "wanze", "wasseiges", "welkenraedt"
    ]},
    # LUXEMBURG
    **{city: "Luxemburg" for city in [
        "arlon", "aarlen", "attert", "aubange", "bastogne", "bastenaken", "bertogne", "bertrix",
        "bouillon", "chiny", "daverdisse", "durbuy", "érezée", "étalle", "fauvillers", "florenville",
        "gouvy", "habay", "herbeumont", "hotton", "houffalize", "la roche-en-ardenne", "léglise",
        "libin", "libramont-chevigny", "manhay", "marche-en-famenne", "martelange", "meix-devant-virton",
        "messancy", "musson", "nassogne", "neufchâteau", "paliseul", "rendeux", "rouvroy",
        "sainte-ode", "saint-hubert", "saint-léger", "tellin", "tenneville", "tintigny",
        "vaux-sur-sûre", "vielsalm", "virton", "wellin"
    ]},
    # NAMEN
    **{city: "Namen" for city in [
        "andenne", "anhée", "assesse", "beauraing", "bièvre", "cerfontaine", "ciney", "couvin",
        "dinant", "doische", "éghezée", "fernelmont", "floreffe", "florennes", "fosses-la-ville",
        "gedinne", "gembloux", "gesves", "hamois", "hastière", "havelange", "houyet", "jemeppe-sur-sambre",
        "la bruyère", "mettet", "namen", "namur", "ohey", "onhaye", "philippeville", "profondeville",
        "rochefort", "sambreville", "sombreffe", "somme-leuze", "viroinval", "vresse-sur-semois",
        "walcourt", "yvoir"
    ]},
    # OOST-VLAANDEREN
    **{city: "Oost-Vlaanderen" for city in [
        "aalst", "aalter", "assenede", "berlare", "beveren", "brakel", "buggenhout", "denderleeuw",
        "dendermonde", "destelbergen", "deinze", "eeklo", "erpe-mere", "evergem", "gavere", "gent",
        "geraardsbergen", "haaltert", "hamme", "herzele", "horebeke", "kaprijke", "kluisbergen",
        "kruibeke", "kruisem", "laarne", "lebbeke", "lede", "lierde", "lochristi", "lokeren",
        "lievegem", "maarkedal", "maldegem", "melle", "merelbeke", "moerbeke", "nazareth",
        "ninove", "oosterzele", "oudenaarde", "ronse", "sint-gillis-waas", "sint-lievens-houtem",
        "sint-martens-latem", "sint-niklaas", "stekene", "temse", "waasmunster", "wachtebeke",
        "wetteren", "wichelen", "wortegem-petegem", "zele", "zelzate", "zottegem", "zulte", "zwalm"
    ]},
    # VLAAMS-BRABANT
    **{city: "Vlaams-Brabant" for city in [
        "aarschot", "affligem", "asse", "beersel", "begijnendijk", "bekkevoort", "bertem",
        "bever", "bierbeek", "boortmeerbeek", "boutersem", "diest", "dilbeek", "drogenbos",
        "galmaarden", "geetbets", "glabbeek", "gooik", "grimbergen", "haacht", "halle",
        "herent", "herne", "hoegaarden", "hoeilaart", "holsbeek", "huldenberg", "kampenhout",
        "kapelle-op-den-bos", "keerbergen", "kortenaken", "kortenberg", "kraainem", "landen",
        "lennik", "leuven", "liedekerke", "linkebeek", "linter", "londerzeel", "lubbeek",
        "machelen", "meise", "merchtem", "opwijk", "oud-heverlee", "overijse", "pepingen",
        "roosdaal", "rotselaar", "scherpenheuvel-zichem", "sint-genesius-rode", "sint-pieters-leeuw",
        "steenokkerzeel", "ternat", "tervuren", "tielt-winge", "tienen", "tremelo", "vilvoorde",
        "wemmel", "wezembeek-oppem", "zaventem", "zemst", "zoutleeuw"
    ]},
    # WAALS-BRABANT
    **{city: "Waals-Brabant" for city in [
        "beauvechain", "braine-l'alleud", "braine-le-château", "chastre", "chaumont-gistoux",
        "court-saint-étienne", "genappe", "graven", "hélécine", "incourt", "ittre", "jodoigne",
        "la hulpe", "lasne", "mont-saint-guibert", "nivelles", "nijvel", "orp-jauche", "ottignies-louvain-la-neuve",
        "perwez", "ramillies", "rebecq", "rixensart", "tubize", "villers-la-ville", "walhain",
        "waterloo", "wavre", "waver"
    ]},
    # WEST-VLAANDEREN
    **{city: "West-Vlaanderen" for city in [
        "alveringem", "anzegem", "ardooie", "avelgem", "beernem", "blankenberge", "bredene",
        "brugge", "damme", "de haan", "de panne", "deerlijk", "dentergem", "diksmuide",
        "harelbeke", "heuvelland", "hooglede", "houthulst", "ichtegem", "ieper", "ingelmunster",
        "izegem", "jabbeke", "knokke-heist", "koekelare", "koksijde", "kortemark", "kortrijk",
        "kuurne", "langemark-poelkapelle", "ledegem", "lendelede", "lichtervelde", "lo-reninge",
        "menen", "mesen", "meulebeke", "middelkerke", "moorslede", "nieuwpoort", "oostende",
        "oostkamp", "oostrozebeke", "oudenburg", "pittem", "poperinge", "roeselare", "ruiselede",
        "spiere-helkijn", "staden", "tielt", "torhout", "veurne", "vleteren", "waregem",
        "wervik", "wevelgem", "wielsbeke", "wingene", "zedelgem", "zonnebeke", "zuienkerke", "zwevegem"
    ]},
}


# =============================================================================
# GEOCODING WITH PRE-CACHED DATA + NOMINATIM FALLBACK
# =============================================================================

# Runtime cache for cities not in the pre-cached list
_coordinates_cache = {}

# Rate limiting: Nominatim requires max 1 request per second
_last_nominatim_request = 0


def get_city_coordinates(city: str, province: str = None) -> dict:
    """
    Fetch latitude and longitude for a Belgian city.
    
    LOOKUP ORDER:
    1. Check pre-cached BELGIAN_CITIES dictionary (instant, ~580 cities)
    2. Check runtime cache (for previously looked up cities)
    3. Fall back to Nominatim API (rate limited, 1 req/sec)
    
    Args:
        city: Name of the city
        province: Province where the city is located (optional)
    
    Returns:
        Dictionary with 'lat' and 'lon' keys, or None if city not found
    """
    global _last_nominatim_request
    
    # Normalize city name
    city_normalized = city.strip().lower()
    
    # Step 1: Check pre-cached Belgian cities (INSTANT)
    if city_normalized in BELGIAN_CITIES:
        lat, lon = BELGIAN_CITIES[city_normalized]
        print(f"[GEOCODE PRE-CACHED] {city} -> ({lat}, {lon})")
        return {'lat': lat, 'lon': lon}
    
    # Step 2: Check runtime cache
    cache_key = f"{city_normalized}|{province or 'any'}"
    if cache_key in _coordinates_cache:
        cached = _coordinates_cache[cache_key]
        print(f"[GEOCODE CACHE HIT] {city} -> ({cached['lat']}, {cached['lon']})")
        return {'lat': cached['lat'], 'lon': cached['lon']}
    
    # Respect rate limit: wait if needed (1 request per second)
    current_time = time.time()
    time_since_last_request = current_time - _last_nominatim_request
    if time_since_last_request < 1.0:
        wait_time = 1.0 - time_since_last_request
        print(f"[GEOCODE] Rate limiting: waiting {wait_time:.2f}s")
        time.sleep(wait_time)
    
    # Build Nominatim API request
    # Using structured query for better accuracy
    base_url = "https://nominatim.openstreetmap.org/search"
    params = {
        'city': city,
        'country': 'Belgium',
        'format': 'json',
        'limit': 1
    }
    
    # Add province/state if provided for better accuracy
    if province:
        params['state'] = province
    
    headers = {
        # Nominatim requires a valid User-Agent
        'User-Agent': 'LandMatchingPlatform/1.0 (educational project)'
    }
    
    try:
        print(f"[GEOCODE API] Requesting coordinates for: {city}, {province or 'Belgium'}")
        response = requests.get(base_url, params=params, headers=headers, timeout=10)
        _last_nominatim_request = time.time()
        
        if response.status_code == 200:
            data = response.json()
            
            if data and len(data) > 0:
                lat = float(data[0]['lat'])
                lon = float(data[0]['lon'])
                
                # Cache the result
                _coordinates_cache[cache_key] = {
                    'lat': lat,
                    'lon': lon,
                    'cached_at': time.time()
                }
                
                print(f"[GEOCODE API] Found: {city} -> ({lat}, {lon})")
                return {'lat': lat, 'lon': lon}
            else:
                print(f"[GEOCODE API] No results found for: {city}, {province}")
                # Cache negative result to avoid repeated failed lookups
                _coordinates_cache[cache_key] = {'lat': None, 'lon': None, 'cached_at': time.time()}
                return None
        else:
            print(f"[GEOCODE API] Error: HTTP {response.status_code}")
            return None
            
    except requests.exceptions.Timeout:
        print(f"[GEOCODE API] Timeout for: {city}")
        return None
    except requests.exceptions.RequestException as e:
        print(f"[GEOCODE API] Request error: {e}")
        return None
    except Exception as e:
        print(f"[GEOCODE API] Unexpected error: {e}")
        return None


# =============================================================================
# GEOGRAPHIC DISTANCE CALCULATION
# =============================================================================

def haversine_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """
    Calculate the great-circle distance between two points on Earth using the Haversine formula.
    
    Args:
        lat1, lon1: Latitude and longitude of the first point (in degrees)
        lat2, lon2: Latitude and longitude of the second point (in degrees)
    
    Returns:
        Distance in kilometers between the two points
    
    Formula:
        a = sin^2(delta_lat/2) + cos(lat1) * cos(lat2) * sin^2(delta_lon/2)
        c = 2 * atan2(sqrt(a), sqrt(1-a))
        distance = Earth_radius * c
    """
    EARTH_RADIUS_KM = 6371.0
    
    # Convert degrees to radians
    lat1_rad = math.radians(lat1)
    lat2_rad = math.radians(lat2)
    delta_lat = math.radians(lat2 - lat1)
    delta_lon = math.radians(lon2 - lon1)
    
    # Haversine formula
    a = (math.sin(delta_lat / 2) ** 2 + 
         math.cos(lat1_rad) * math.cos(lat2_rad) * math.sin(delta_lon / 2) ** 2)
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    
    return EARTH_RADIUS_KM * c


# =============================================================================
# SMART CITY FALLBACK MECHANISM
# =============================================================================

def find_nearest_city_with_data(target_city: str, target_province: str, property_type: str = None,
                                 min_required_properties: int = 2) -> dict:
    """
    Find the nearest city that has sufficient sold property data for price estimation.
    Uses OpenStreetMap Nominatim for geocoding with caching.
    
    SMART FALLBACK MECHANISM:
    -------------------------
    1. Get coordinates of the target city using Nominatim API
    2. Query all sold properties and group them by city
    3. Filter cities that have at least min_required_properties sold
    4. Calculate geographic distance from target city to each candidate
    5. Return the nearest city with sufficient data
    
    Args:
        target_city: The original city we're searching for
        target_province: The province of the target city
        property_type: Type of property (land/building) to filter by
        min_required_properties: Minimum sold properties required (default: 3)
    
    Returns:
        Dictionary containing:
        - city: Name of the nearest city with data
        - province: Province of that city
        - distance_km: Distance from target city in kilometers
        - property_count: Number of sold properties in that city
        - properties: List of sold properties in that city
        Or None if no suitable city is found
    """
    print(f"\n[FALLBACK] Searching for nearest city to {target_city}, {target_province}")
    print(f"[FALLBACK] Property type: {property_type}, Min required: {min_required_properties}")
    
    # Step 1: Get coordinates of the target city
    target_coords = get_city_coordinates(target_city, target_province)
    
    if not target_coords or target_coords.get('lat') is None:
        print(f"[FALLBACK] Could not geocode target city: {target_city}")
        return None
    
    target_lat = target_coords['lat']
    target_lon = target_coords['lon']
    print(f"[FALLBACK] Target city coordinates: ({target_lat}, {target_lon})")
    
    # Step 2: Query all sold properties with final prices
    try:
        response = supabase.table('Property').select('*').eq('sold', True).not_.is_('final_price', 'null').execute()
        all_sold_properties = response.data or []
    except Exception as e:
        print(f"[FALLBACK] Database error: {e}")
        return None
    
    if not all_sold_properties:
        print("[FALLBACK] No sold properties in database")
        return None
    
    print(f"[FALLBACK] Found {len(all_sold_properties)} total sold properties")
    
    # Step 3: Group properties by city and count them
    # NOTE: We do NOT filter by property type here - we want to find ANY city with enough data
    # The property type scoring happens later in estimate_property_price()
    city_property_map = {}
    
    for prop in all_sold_properties:
        prop_city = (prop.get('city') or '').strip().lower()
        prop_province = (prop.get('province') or '').strip()
        
        # Skip the original target city (we're looking for alternatives)
        if prop_city == target_city.lower():
            continue
        
        # Create unique key for city+province combination
        city_key = f"{prop_city}|{prop_province}"
        
        if city_key not in city_property_map:
            city_property_map[city_key] = {
                'city': prop_city,
                'province': prop_province,
                'properties': []
            }
        
        city_property_map[city_key]['properties'].append(prop)
    
    print(f"[FALLBACK] Found {len(city_property_map)} unique cities with sold properties")
    
    # Step 4: Filter cities with sufficient data and calculate distances
    candidate_cities = []
    
    for city_key, city_data in city_property_map.items():
        property_count = len(city_data['properties'])
        
        # Only consider cities with at least min_required_properties
        if property_count < min_required_properties:
            continue
        
        # Get coordinates for this candidate city
        city_coords = get_city_coordinates(city_data['city'], city_data['province'])
        
        if not city_coords or city_coords.get('lat') is None:
            print(f"[FALLBACK] Could not geocode: {city_data['city']}, skipping")
            continue
        
        # Calculate geographic distance from target city
        distance = haversine_distance(
            target_lat, target_lon,
            city_coords['lat'], city_coords['lon']
        )
        
        candidate_cities.append({
            'city': city_data['city'],
            'province': city_data['province'],
            'distance_km': round(distance, 2),
            'property_count': property_count,
            'properties': city_data['properties']
        })
        
        print(f"[FALLBACK] Candidate: {city_data['city']} - {distance:.1f}km away, {property_count} properties")
    
    # Step 5: Sort by distance and return the nearest city
    if not candidate_cities:
        print("[FALLBACK] No suitable cities found with sufficient data")
        return None
    
    # Sort by geographic distance (nearest first)
    candidate_cities.sort(key=lambda x: x['distance_km'])
    
    nearest = candidate_cities[0]
    print(f"[FALLBACK] Selected: {nearest['city']} ({nearest['distance_km']}km away, {nearest['property_count']} properties)")
    
    return nearest


# =============================================================================
# FILE UPLOAD UTILITIES
# =============================================================================

def upload_property_image(file, property_id, image_index):
    """Upload an image to Supabase Storage and return the public URL"""
    try:
        file_extension = os.path.splitext(file.filename)[1].lower()
        if not file_extension:
            mime_type = file.content_type
            if mime_type:
                file_extension = mimetypes.guess_extension(mime_type) or '.jpg'
            else:
                file_extension = '.jpg'
        
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"property_{property_id}_{timestamp}_{image_index}{file_extension}"
        
        print(f"Attempting to upload: {filename}")
        
        bucket_name = 'property-images'
        file_content = file.read()
        file.seek(0)
        
        print(f"File size: {len(file_content)} bytes")
        print(f"Content type: {file.content_type}")
        
        response = supabase.storage.from_(bucket_name).upload(
            filename, 
            file_content,
            {
                'content-type': file.content_type or 'image/jpeg',
                'cache-control': '3600'
            }
        )
        
        print(f"Upload response: {response}")
        
        if response:
            public_url_response = supabase.storage.from_(bucket_name).get_public_url(filename)
            print(f"Public URL: {public_url_response}")
            return public_url_response
        else:
            print(f"Failed to upload image: {response}")
            return None
            
    except Exception as e:
        print(f"Error uploading image: {e}")
        return None


# =============================================================================
# ID GENERATION UTILITIES
# =============================================================================

def generate_unique_id(table_name, id_column):
    """Generate a unique 8-digit ID for the specified table"""
    while True:
        new_id = random.randint(10000000, 99999999)
        result = supabase.table(table_name).select(id_column).eq(id_column, new_id).execute()
        if not result.data:
            return new_id


def generate_unique_property_id():
    """Generate a unique property ID with max 8 digits"""
    max_attempts = 100
    attempts = 0
    
    while attempts < max_attempts:
        property_id = random.randint(10000000, 99999999)
        try:
            existing = supabase.table('Property').select('property_id').eq('property_id', property_id).execute()
            if not existing.data:
                return property_id
        except Exception:
            pass
        attempts += 1
    
    while attempts < max_attempts * 2:
        property_id = random.randint(1000000, 9999999)
        try:
            existing = supabase.table('Property').select('property_id').eq('property_id', property_id).execute()
            if not existing.data:
                return property_id
        except Exception:
            pass
        attempts += 1
    
    return None


# =============================================================================
# PRICE ESTIMATION ALGORITHM (KNN-based with Smart City Fallback)
# =============================================================================

def estimate_property_price(data):
    """
    KNN-based price estimation algorithm with smart geographic fallback.
    
    ALGORITHM OVERVIEW:
    -------------------
    1. Parse input data (city, province, type, size)
    2. Query all sold properties from the database
    3. Check if we have enough properties in the target city (K=5)
    4. If NOT enough in target city:
       - Use smart fallback to find the nearest city with sufficient data
       - Apply distance penalty to scores for properties from fallback city
    5. Score all candidate properties based on similarity
    6. Select top K neighbors and calculate weighted average price per m2
    7. Return price range (+/- 20%) rounded to 50k
    
    SCORING SYSTEM:
    ---------------
    - Same city: +4 points
    - Same province: +2 points  
    - Same property type: +1 point
    - Size difference penalty: -abs(size_diff) / 10
    - Different city (fallback): -1 point penalty
    
    Args:
        data: Dictionary with 'province', 'city', 'type', 'size'
    
    Returns:
        Dictionary with:
        - success: True/False
        - suggested_price_min: Lower bound of price range
        - suggested_price_max: Upper bound of price range
        - fallback_city: Name of fallback city used (if any)
        - fallback_distance_km: Distance to fallback city (if used)
        - error: Error message (if failed)
    """
    # Configuration constants
    K = 5  # Number of nearest neighbors to consider
    MIN_SAME_CITY_PROPERTIES = 2  # Minimum properties needed before fallback (lowered for small datasets)
    
    # Parse and validate input data
    province = data.get('province', '').strip()
    city = data.get('city', '').strip().lower()
    property_type = data.get('type', '').strip().lower()
    
    try:
        size = float(data.get('size', 0))
        if size <= 0:
            return {"success": False, "error": "Size must be a positive number"}
    except (ValueError, TypeError):
        return {"success": False, "error": "Invalid size format"}
    
    print(f"\n[PRICE EST] Starting estimation for: {city}, {province}, type={property_type}, size={size}m2")
    
    # Query all sold properties
    try:
        response = supabase.table('Property').select('*').eq('sold', True).not_.is_('final_price', 'null').execute()
        sold_properties = response.data or []
    except Exception as e:
        return {"success": False, "error": f"Database error: {str(e)}"}
    
    if not sold_properties:
        print("[PRICE EST] No sold properties in database")
        return {
            "success": True, 
            "suggested_price_min": None, 
            "suggested_price_max": None,
            "message": "No sold properties available for comparison"
        }
    
    print(f"[PRICE EST] Found {len(sold_properties)} total sold properties")
    
    # Check how many properties are in the same city
    same_city_properties = [
        p for p in sold_properties 
        if (p.get('city') or '').strip().lower() == city
    ]
    
    print(f"[PRICE EST] Properties in {city}: {len(same_city_properties)}")
    
    # Determine if we need fallback
    fallback_city_info = None
    fallback_used = False
    
    if len(same_city_properties) < MIN_SAME_CITY_PROPERTIES:
        print(f"[PRICE EST] Not enough data in {city}, triggering smart fallback...")
        
        # Find nearest city with sufficient data
        fallback_city_info = find_nearest_city_with_data(
            target_city=city,
            target_province=province,
            property_type=property_type,
            min_required_properties=MIN_SAME_CITY_PROPERTIES
        )
        
        if fallback_city_info:
            fallback_used = True
            print(f"[PRICE EST] Using fallback city: {fallback_city_info['city']} ({fallback_city_info['distance_km']}km away)")
    
    # Score all properties
    scored_properties = []
    
    for prop in sold_properties:
        score = 0
        is_fallback_property = False
        
        prop_city = (prop.get('city') or '').strip().lower()
        prop_province = (prop.get('province') or '').strip()
        prop_type = (prop.get('type') or '').strip().lower()
        
        # City scoring
        if prop_city == city:
            # Same city as target: highest score
            score += 4
        elif fallback_city_info and prop_city == fallback_city_info['city']:
            # Fallback city: give partial score with penalty
            score += 3  # Lower than same city (4) but still good
            is_fallback_property = True
        elif prop_province == province:
            # Same province but different city
            score += 1
        
        # Province scoring (additional bonus if same province)
        if prop_province == province:
            score += 2
        
        # Property type scoring
        if prop_type == property_type:
            score += 1
        
        # Size similarity penalty (smaller difference = smaller penalty)
        try:
            prop_size = float(prop.get('size') or 0)
            if prop_size > 0:
                size_penalty = abs(size - prop_size) / 10
                score -= size_penalty
        except (ValueError, TypeError):
            pass
        
        # Add to scored list if it has valid price data
        try:
            final_price = float(prop.get('final_price') or 0)
            prop_size = float(prop.get('size') or 0)
            if final_price > 0 and prop_size > 0:
                scored_properties.append({
                    'property': prop,
                    'score': score,
                    'price_per_m2': final_price / prop_size,
                    'is_fallback': is_fallback_property
                })
        except (ValueError, TypeError):
            continue
    
    if not scored_properties:
        print("[PRICE EST] No valid properties for scoring")
        return {
            "success": True, 
            "suggested_price_min": None, 
            "suggested_price_max": None,
            "message": "No comparable properties found"
        }
    
    # Sort by score (highest first) and select top K
    scored_properties.sort(key=lambda x: x['score'], reverse=True)
    top_k = scored_properties[:K]
    
    print(f"[PRICE EST] Top {len(top_k)} neighbors:")
    for i, p in enumerate(top_k):
        prop = p['property']
        print(f"  {i+1}. {prop.get('city')}: score={p['score']:.2f}, price/m2={p['price_per_m2']:.2f}, fallback={p['is_fallback']}")
    
    # Calculate average price per m2
    prices_per_m2 = [p['price_per_m2'] for p in top_k]
    avg_price_per_m2 = sum(prices_per_m2) / len(prices_per_m2)
    
    print(f"[PRICE EST] Average price per m2: {avg_price_per_m2:.2f}")
    
    # Calculate price range (+/- 20%)
    base_price = avg_price_per_m2 * size
    suggested_price_min = base_price * 0.80
    suggested_price_max = base_price * 1.20
    
    # Round to nearest 50,000
    def round_to_50k(price):
        return round(price / 50000) * 50000
    
    suggested_price_min = round_to_50k(suggested_price_min)
    suggested_price_max = round_to_50k(suggested_price_max)
    
    # Ensure min <= max
    if suggested_price_min > suggested_price_max:
        suggested_price_min, suggested_price_max = suggested_price_max, suggested_price_min
    
    # Ensure there's a range (not same min and max)
    if suggested_price_min == suggested_price_max:
        suggested_price_min = max(0, suggested_price_min - 50000)
        suggested_price_max = suggested_price_max + 50000
    
    print(f"[PRICE EST] Final range: {suggested_price_min} - {suggested_price_max}")
    
    # Build response
    result = {
        "success": True, 
        "suggested_price_min": suggested_price_min, 
        "suggested_price_max": suggested_price_max
    }
    
    # Add fallback info if used
    if fallback_used and fallback_city_info:
        result["fallback_city"] = fallback_city_info['city'].title()
        result["fallback_distance_km"] = fallback_city_info['distance_km']
        result["fallback_message"] = f"Limited data in {city.title()}. Used nearby city {fallback_city_info['city'].title()} ({fallback_city_info['distance_km']}km away) for comparison."
    
    return result
