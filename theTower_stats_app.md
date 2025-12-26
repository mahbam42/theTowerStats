
# Table of Contents

1.  [Stats Tracking App for The Tower Mobile Game](#org6bc8116)
    1.  [Goals/Intent](#org7ae6b0e)
    2.  [Requirements](#org15acf6a)
    3.  [Overall Architecture](#org4ba79a8)
    4.  [Features](#orgaa25c6a)
    5.  [Core Responsibilities](#org8a5ae07)
        1.  [Rate Calculations](#org30c2d4d)
        2.  [Delta Calculations](#org929114e)
        3.  [Parameterized Effects](#orgfd76c4a)
        4.  [Aggregations by Intent (Presets)](#org128ac5e)
        5.  [Analysis Engine Invocation](#orga9173e5)
        6.  [Output Shape](#org6705e20)
        7.  [Module Structure (Suggested)](#org83322e1)
    6.  [UX Design](#orgce75efa)
    7.  [Example Stat Data](#orga246af8)
    8.  [Models](#org2190708)
        1.  [Game Data](#orgfbc157c)
        2.  [BotsParameters](#orgddc20a0)
        3.  [CardDefinition](#org142e68f)
        4.  [CardLevel / Star](#org4adbf5d)
        5.  [CardParameters](#org4939a53)
        6.  [CardSlots](#org46f1dfd)
        7.  [GuardianChipParemeters](#org9d13ca5)
        8.  [PlayerBot](#org186ed57)
        9.  [PlayerCard](#orgfa29f63)
        10. [PlayerGuardianChip](#org324d700)
        11. [PlayerUltimateWeapon](#org1125a4b)
        12. [PresetTags](#org4e4d8ce)
        13. [UltimateWeaponParameters](#org9473155)
        14. [Unit Model](#orgf73ec44)
        15. [WikiData](#org6e3d4a3)
    9.  [Views](#org0bbf8c7)
        1.  [Battle History](#orga48cf07)
        2.  [Cards](#org012c065)
        3.  [Charts](#org4ad0131)
        4.  [UW Progress](#org3c093b3)
        5.  [Guardian Progress](#org32aa2b4)
        6.  [Bots Progress](#orgb9e117e)
    10. [Management Commands](#org524b474)
        1.  [fetch<sub>wiki</sub><sub>data</sub>](#org706a2e1)
        2.  [add<sub>battle</sub><sub>report</sub>](#orga82028c)
    11. [Repo Structure](#org68e1f43)
    12. [Testing Standards](#org1dff837)
    13. [Sprint Roadmap](#org1cbc3c1)
        1.  [Phase 1 Foundations](#orge4864dd)
        2.  [Phase 2 Context](#org8e76d31)
        3.  [Phase 3 — App Structure & UX](#orgfed99e7)
        4.  [Phase 4 Effects](#orgfdbc9ff)
        5.  [Phase 5 Dashboard UX <code>[100%]</code>](#org2d7f882)
        6.  [Phase 6 Expansion of Foundation and Context <code>[33%]</code>](#orge0780d6)
        7.  [Phase 7 Power Tools <code>[100%]</code>](#org6f8cc14)
        8.  [Phase 8 Multiple Player Support](#org36657fe)
        9.  [Phase 9 Deploy and Clean out Backlog <code>[100%]</code>](#orgc5fdabf)
        10. [Phase 10 v0.2.0](#org62a0c69)
        11. [Phase 10B Additional UX](#org57c2d00)
        12. [Phase 11 Bug Fixes <code>[6/6]</code>](#orgb60c2c8)
        13. [Bugs/Enhancements <code>[23/25]</code>](#orgd5e9c28)
    14. [Backlog <code>[2/5]</code>](#org023e374)
        1.  [Exploratory Pattern Analysis (v0.X.0)](#org5fb4eea):kMeans:enhancement:
        2.  [Hide Deathwave on UW Sync Chart](#orgeb993a9)
        3.  [Required Doc Type Header (Must Prepend to All Docs)](#orgd3026b1)
        4.  [Wmhat-If Scenarios](#orgfdf7785)
        5.  [Ranked Recommendations](#orgeaf26f0)
        6.  [Complete](#org11f7507)
    15. [Codex Tasks](#orgce29b85)

****Codex:**** So help me I will end you if I ever see you checkout or touch this file. Refer to agents.md if you stumble upon this file again.

<!&#x2013;
NOTE:
This document was reconstructed after a tooling failure.
Content has been manually reviewed for accuracy.
If discrepancies are found, refer to git history where available.
&#x2013;>


<a id="org6bc8116"></a>

# Stats Tracking App for The Tower Mobile Game


<a id="org7ae6b0e"></a>

## Goals/Intent

-   Import data via raw text paste from The Tower either after a round or from 'Battle History'
    -   Will check to dedupe imports
    -   Can delete saved runs
-   Stats are then tracked and charted over time via Analysis Engine
    -   Computed Rates per Round over time
    -   Deltas between Rounds
-   Values are parsed from Raw Values stored in the DB and normalized/derived never destroyed
-   Responsive Layout/UI
    -   Battle Results form is designed for mobile


<a id="org15acf6a"></a>

## Requirements

python
django
Chart.js
Foundation
Sass
sqlite
pytest
pytest-django
ruff
mypy


<a id="org4ba79a8"></a>

## Overall Architecture

Raw Game Data
   ↓ (parser)
Normalized Units
   ↓
Analysis Engine  ←──── Player Context
   ↓
Derived Metrics
   ↓
Charts / Views


<a id="orgaa25c6a"></a>

## Features

-   **Import Data:** Page to drop in Round Results.
-   **Charts:** Overview of Progress over time
-   **Card Library:** log and show card collection progress. Based on the work done here, <https://docs.google.com/spreadsheets/d/1vmIA7SMLtjAY8OooS8JC8hod0Lgvr5WsXB5vIStBJJg/edit?usp=sharing>
    -   Card Preset Tagging
        Tag Cards into groupings and then filter display by groupings. Each card can be a part of multiple presets
    -   Widget to show Card Slots unlocked with button to unlock next slot and label to show cost
        Maximum allowed for each preset
-   **Wiki Scraper:** Pull Data from the Fandom Wiki via Management Command
    Manual Buttons to check for update and fetch updates.
    Cite source
    Name property links to wiki page as well
    -   Pull tables
    -   Extract rows and columns
    -   Normalize text (%, seconds, multipliers)

Targets:

-   Bots Upgrades
-   Cards
-   Guardian Chips
-   UW Upgrade Table


<a id="org8a5ae07"></a>

## Core Responsibilities


<a id="org30c2d4d"></a>

### Rate Calculations

-   Derived per run and over time:
-   Coins / hour
-   Coins / wave
-   Damage / wave
-   Waves / real minute
-   Resource gains per hour (cells, shards, etc.)

These back Phase 1 charts directly.


<a id="org929114e"></a>

### Delta Calculations

Between two runs or windows:

-   Absolute delta
-   Percentage delta
-   Rolling averages

Examples:

-   Coins/hour before vs after unlocking a slot
-   Damage output change after a UW unlock

No interpretation — just math.


<a id="orgfd76c4a"></a>

### Parameterized Effects

Using wiki-derived tables:

-   Effective cooldown at star level
-   % reduction or multiplier applied
-   EV calculations (e.g. wave skip)

These are:

-   Deterministic
-   Re-computable across revisions
-   Fully testable with golden tests


<a id="org128ac5e"></a>

### Aggregations by Intent (Presets)

-   Presets act as labels, not logic.
-   Only One Preset can be active at a time
-   The engine supports:
    -   “Aggregate metrics for runs where preset X was active”
    -   “Compare metrics across presets”

It does not decide which preset is better.


<a id="orga9173e5"></a>

### Analysis Engine Invocation

-   Stateless
-   Accepts:
    -   Query params (date range, tier, context)
    -   Returns DTOs only
    -   No DB writes


<a id="org6705e20"></a>

### Output Shape

All outputs should conform to a small set of DTO-style objects:

    DerivedMetric(
        key="coins_per_hour",
        value=Decimal,
        unit="coins/hour",
        run_id=UUID,
        context={...}
    )
    
    MetricSeries(
        key="coins_per_hour",
        points=[(timestamp, value), ...],
        context={tier, preset, uw, guardian}
    )

This maps cleanly to Chart.js datasets.


<a id="org83322e1"></a>

### Module Structure (Suggested)

analysis/
├── engine.py          # orchestration
├── rates.py           # per-hour, per-wave math
├── deltas.py          # comparisons
├── effects.py         # wiki-parameter-based calculations
├── aggregations.py    # preset / context grouping
├── dto.py             # output shapes
├── tests/
│   ├── test<sub>rates.py</sub>
│   ├── test<sub>effects.py</sub>
│   └── fixtures/


<a id="orgce75efa"></a>

## UX Design

-   Dark Mode Default
-   Top Dynamic Nav
    -   Docs / Admin links to the right
    -   Global Search Box
-   Maxed Out/Completed Upgrades are highlighted with a Gold Box outline


<a id="orga246af8"></a>

## Example Stat Data

Can be exported at the end of a round or retrieved from 'Battle History' 

\#+BEGIN<sub>SRC</sub> 
Battle Report
Battle Date	Dec 07, 2025 21:59
Game Time	10h 24m 52s
Real Time	2h 17m 23s
Tier	7
Wave	1301
Killed By	Boss
Coins earned	17.55M
Coins per hour	7.67M
Cash earned	$55.90M
Interest earned	$2.13M
Gem Blocks Tapped	3
Cells Earned	346
Reroll Shards Earned	373
Combat
Damage dealt	111.78q
Damage Taken	19.19B
Damage Taken Wall	3.39B
Damage Taken While Berserked	0
Damage Gain From Berserk	x0.00
Death Defy	1
Lifesteal	1.44M
Projectiles Damage	9.66q
Projectiles Count	450.74K
Thorn damage	433.07T
Orb Damage	11.35q
Enemies Hit by Orbs	2.84K
Land Mine Damage	3.40q
Land Mines Spawned	21340
Rend Armor Damage	0
Death Ray Damage	0
Smart Missile Damage	0
Inner Land Mine Damage	0
Chain Lightning Damage	81.18q
Death Wave Damage	8.72T
Tagged by Deathwave	6523
Swamp Damage	5.47q
Black Hole Damage	0
Electrons Damage	0
Utility
Waves Skipped	229
Recovery Packages	320
Free Attack Upgrade	687
Free Defense Upgrade	638
Free Utility Upgrade	653
HP From Death Wave	0.00
Coins From Death Wave	136.82K
Cash From Golden Tower	$18.91M
Coins From Golden Tower	2.18M
Coins From Black Hole	0
Coins From Spotlight	50.55K
Coins From Orb	0
Coins from Coin Upgrade	5.71M
Coins from Coin Bonuses	9.20M
Enemies Destroyed
Total Enemies	76623
Basic	46959
Fast	10196
Tank	10620
Ranged	7745
Boss	106
Protector	144
Total Elites	75
Vampires	24
Rays	24
Scatters	27
Saboteur	0
Commander	0
Overcharge	0
Destroyed By Orbs	2842
Destroyed by Thorns	18
Destroyed by Death Ray	0
Destroyed by Land Mine	8135
Destroyed in Spotlight	9112
Bots
Flame Bot Damage	264.78T
Thunder Bot Stuns	1.00K
Golden Bot Coins Earned	17.41K
Destroyed in Golden Bot	629
Guardian
Damage	18.75T
Summoned enemies	0
Guardian coins stolen	0
Coins Fetched	17.73K
Gems	1
Medals	1
Reroll Shards	12
Cannon Shards	0
Armor Shards	0
Generator Shards	3
Core Shards	0
Common Modules	0
Rare Modules	0
\#+END<sub>SR</sub>


<a id="org2190708"></a>

## Models


<a id="orgfbc157c"></a>

### Game Data

This is a large blob of data shown to the player at the end of each round of the game. They will paste it into this app as plain text. Consider this a snapshot at import time.

Properties:

-   **RawText:** string (raw input from user)
-   **ParsedAt:** datestring of when it was created
-   **checksum:** for deduping imports

\### Subordinate Classes:  

1.  RunProgress

    -   **tier:** integer
    -   **battle date:** datestring
    -   **real time:** duration
    -   **wave:** integer
    -   **killed by:** string

2.  RunEarnings

    -   **Coins earned:** 
    
    -   **Coins per hour:** 
    
    -   **Cash earned:** 
    
    -   **Interest earned:** 
    
    -   **Gem Blocks Tapped:** 
    
    -   **Cells Earned:** 
    
    -   **Reroll Shards Earned:** 

3.  RunCombat

    -   Damage dealt	111.78q
    -   Damage Taken	19.19B
    -   Damage Taken Wall	3.39B
    -   Damage Taken While Berserked	0
    -   Damage Gain From Berserk	x0.00
    -   Death Defy	1
    -   Lifesteal	1.44M
    -   Projectiles Damage	9.66q
    -   Projectiles Count	450.74K
    -   Thorn damage	433.07T
    -   Orb Damage	11.35q
    -   Enemies Hit by Orbs	2.84K
    -   Land Mine Damage	3.40q
    -   Land Mines Spawned	21340
    -   Rend Armor Damage	0
    -   Death Ray Damage	0
    -   Smart Missile Damage	0
    -   Inner Land Mine Damage	0
    -   Chain Lightning Damage	81.18q
    -   Death Wave Damage	8.72T
    -   Tagged by Deathwave	6523
    -   Swamp Damage	5.47q
    -   Black Hole Damage	0
    -   Electrons DamageDamage dealt	111.78q
    -   Damage Taken	19.19B
    -   Damage Taken Wall	3.39B
    -   Damage Taken While Berserked	0
    -   Damage Gain From Berserk	x0.00
    -   Death Defy	1
    -   Lifesteal	1.44M
    -   Projectiles Damage	9.66q
    -   Projectiles Count	450.74K
    -   Thorn damage	433.07T
    -   Orb Damage	11.35q
    -   Enemies Hit by Orbs	2.84K
    -   Land Mine Damage	3.40q
    -   Land Mines Spawned	21340
    -   Rend Armor Damage	0
    -   Death Ray Damage	0
    -   Smart Missile Damage	0
    -   Inner Land Mine Damage	0
    -   Chain Lightning Damage	81.18q
    -   Death Wave Damage	8.72T
    -   Tagged by Deathwave	6523
    -   Swamp Damage	5.47q
    -   Black Hole Damage	0
    -   Electrons Damage

4.  RunUtility

    Waves Skipped	229
    Recovery Packages	320
    Free Attack Upgrade	687
    Free Defense Upgrade	638
    Free Utility Upgrade	653
    HP From Death Wave	0.00
    Coins From Death Wave	136.82K
    Cash From Golden Tower	$18.91M
    Coins From Golden Tower	2.18M
    Coins From Black Hole	0
    Coins From Spotlight	50.55K
    Coins From Orb	0
    Coins from Coin Upgrade	5.71M
    Coins from Coin Bonuses	9.20M

5.  RunEnemies

    Total Enemies	76623
    Basic	46959
    Fast	10196
    Tank	10620
    Ranged	7745
    Boss	106
    Protector	144
    Total Elites	75
    Vampires	24
    Rays	24
    Scatters	27
    Saboteur	0
    Commander	0
    Overcharge	0
    Destroyed By Orbs	2842
    Destroyed by Thorns	18
    Destroyed by Death Ray	0
    Destroyed by Land Mine	8135
    Destroyed in Spotlight	9112

6.  RunBots

    Flame Bot Damage	264.78T
    Thunder Bot Stuns	1.00K
    Golden Bot Coins Earned	17.41K
    Destroyed in Golden Bot	629

7.  RunGuardian

    Damage	18.75T
    Summoned enemies	0
    Guardian coins stolen	0
    Coins Fetched	17.73K
    Gems	1
    Medals	1
    Reroll Shards	12
    Cannon Shards	0
    Armor Shards	0
    Generator Shards	3
    Core Shards	0
    Common Modules	0
    Rare Modules	0


<a id="orgddc20a0"></a>

### BotsParameters

Wiki-derived, FK to PlayerBots
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.


<a id="org142e68f"></a>

### CardDefinition

Properties:

-   **Name :** string
-   **rarity:** string
-   base<sub>effect</sub>
-   max<sub>effect</sub>
-   preset<sub>tags</sub> (FK)


<a id="org4adbf5d"></a>

### CardLevel / Star

-   card (FK)
-   **stars:** integer
-   **value:** value of current effect (between base and max)


<a id="org4939a53"></a>

### CardParameters

Wiki-derived, FK to PlayerCard
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.


<a id="org46f1dfd"></a>

### CardSlots

tracker for Card Slots unlocked, maximum of 21
Modified via Admin

Properties:

-   Slot Number (label)
-   Cost integer (Gems)


<a id="org9d13ca5"></a>

### GuardianChipParemeters

Wiki-derived, FK to PlayerGuardianChip
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.


<a id="org186ed57"></a>

### PlayerBot

Properties:

-   **bot:** FK to BotParameters
-   **unlocked:** checkbox


<a id="orgfa29f63"></a>

### PlayerCard

Properties:

-   card<sub>definition</sub> (FK)
-   **unlocked:** checkbox
-   **Stars:** integer 1-7
-   **Cards:** integer progress toward next level. 0, 3, 5, 8, 12, 20, 32


<a id="org324d700"></a>

### PlayerGuardianChip

Properties:

-   **chip:** FK to GuardianChipParameters
-   **unlocked:** checkbox


<a id="org1125a4b"></a>

### PlayerUltimateWeapon

Properties:

-   **UW:** FK to UtimateWeaponParameters
-   **unlocked:** checkbox


<a id="org4e4d8ce"></a>

### PresetTags

-   **Name:** string
-   Cards (FK)
-   **limit:** FK with Card Slots


<a id="org9473155"></a>

### UltimateWeaponParameters

Wiki-derived, FK to PlayerUtimateWeapon
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.

-   Object for each UW (Spotlight, Golden Tower, Death Wave, Smart Missle, Chrono Field, Poison Swamp, Inner Land Mine, Black Hole
-   Tracks 3 properties for each, stone cost and stones invested
-   Will need CLI script to import from CSV data

Properties:

-   **UW Name:** string
-   **Property Name:** string
-   **Cost:** integer (stones)
-   **Spent:** integer (stones)


<a id="orgf73ec44"></a>

### Unit Model

Percent and 'x' multipliers use semantic wrapper (Multiplier(1.15))

Properties:

-   **raw<sub>value</sub>:** string
-   **normalized<sub>value</sub>:** decimal
-   **magnitude:** (k,10<sup>3</sup>),  (m, 10<sup>6</sup>), (b, 10<sup>9</sup>), (t, 10<sup>12</sup>), etc.
-   **unit<sub>type</sub>:** coins, damage, count, time


<a id="org6e3d4a3"></a>

### WikiData

Stores the anchor names and retrived data caches for Card, Ultimate Weapons, and Guardian Chips. Entities not seen in the most recent scrape are marked deprecated but retained.

-   Page URL
-   Cannonical Name
-   EntityID
-   content<sub>hash</sub>
-   source<sub>section</sub> (table / row / column)
-   first<sub>seen</sub>
-   last<sub>seen</sub>
-   parse<sub>version</sub>


<a id="org0bbf8c7"></a>

## Views


<a id="orga48cf07"></a>

### Battle History

View previously entered stats 


<a id="org012c065"></a>

### Cards

Combine 'Cards,' 'CardLevel' and 'CardSlots'


<a id="org4ad0131"></a>

### Charts

Charts are configured via URL params initially; saved views are out of scope.

Pretty dashboard of metrics over time (filterable by date range and tier)

-   Default View is by Event (start is 12/9/2025 00:00 UTC)
-   Filter by Tier or all

Top Level Charts:

-   Coins Earned (line)
-   Coins per Hour (line)

Sub Charts:

-   Cash Earned
-   Cells Earned
-   Reroll Dice Earned

1.  UW Performance

    Breakdown and Comparison Views of RunCombat filtered to Given UW

2.  Guardian Stats

    Breakdown and comparison views of RunGuardian over time

3.  Comparison Charts

    Phase 2 Charts (Contextual Overlays)
    
    -   Same metric, different tiers
    -   With / without specific preset active
    -   Moving averages

4.  Derived Metrics

    -   Effective cooldown reduction
    -   Coins per wave vs wave number


<a id="org3c093b3"></a>

### UW Progress

-   Button to add new UW


<a id="org32aa2b4"></a>

### Guardian Progress

-   Button to add new chip
-   checkbox to flag equiped


<a id="orgb9e117e"></a>

### Bots Progress

-   button to add new bot


<a id="org524b474"></a>

## Management Commands


<a id="org706a2e1"></a>

### fetch<sub>wiki</sub><sub>data</sub>

args:

-   cards
-   bots
-   ultimate<sub>weapons</sub>
-   guardian<sub>chips</sub>
-   all (grabs all of the above)
-   **&#x2013;check:** dry-run to find deltas

Explicit idempotency guarantee

Logging output format (even briefly)
Example:

-   “Logs entity added / changed / unchanged counts”


<a id="orga82028c"></a>

### add<sub>battle</sub><sub>report</sub>

Ingest and parse battle report data from the player. This is a large blob of data shown to the player at the end of each round of the game. They will paste it into this app as plain text.

Parser should gracefully alert the player to new labels that may appear after a game update.


<a id="org68e1f43"></a>

## Repo Structure

theTower<sub>stats</sub><sub>app</sub>
├── analysis               # analysis/ contains no Django models or ORM access.
│   ├── engine.py          # orchestration
│   ├── rates.py           # per-hour, per-wave math
│   ├── deltas.py          # comparisons
│   ├── effects.py         # wiki-parameter-based calculations
│   ├── aggregations.py    # preset / context grouping
│   └── dto.py             # output shapes
├── archive                # misc project files excluded from the repo
├── core
│   └── <span class="underline"><span class="underline">pycache</span></span>
├── docs
│   ├── 01<sub>Introduction</sub>
│   ├── 02<sub>Quickstart</sub>
│   ├── 03<sub>Navigation</sub>
│   └── &#x2026;
├── theTower<sub>stats</sub><sub>app</sub>
│   ├── <span class="underline"><span class="underline">pycache</span></span>
│   ├── management
│   ├── migrations
│   ├── templates
│   ├── templatetags
│   ├── utils
│   └── views
├── scripts
├── static
├── tests
│   ├── <span class="underline"><span class="underline">pycache</span></span>
│   ├── test<sub>rates.py</sub>
│   ├── test<sub>effects.py</sub>
│   └── fixtures/
└── &#x2026;


<a id="org1dff837"></a>

## Testing Standards

-   Parser golden files (real pasted runs)
-   Every parser or calculation gets at least one golden test
-   Wiki scraper fixture snapshots
-   Math correctness tests (especially EV)
-   When completing code, start building/executing tests as specific as possible to the code you changed so that you can catch issues efficiently, then make your way to broader tests as you build confidence.


<a id="org1cbc3c1"></a>

## Sprint Roadmap

Each phase must be demoable without admin intervention.


<a id="orge4864dd"></a>

### DONE Phase 1 Foundations

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-14 Sun 16:44]</span></span>

1.  Milestones

    -   [X] AnalysisEngine scaffold
    -   [X] Rate calculations (coins/hour, waves/hour)
    -   [X] One time-series chart wired end-to-end

2.  Exit Criteria <code>[100%]</code>

    Goal: Prove the end-to-end pipeline works.
    
    -   [X] A pasted Battle Report:
        -   Is parsed without crashing
        -   Creates a GameData record and all subordinate Run\* records
    -   [X] Duplicate imports are rejected via checksum
    -   [X] Unknown labels are surfaced to the user (non-fatal)
    
    Analysis Engine
    
    -   [X] AnalysisEngine can be invoked with:
        -   [X] a date range
        -   [X] no player context
    -   [X] At least one rate calculation is implemented and tested:
        e.g. coins<sub>per</sub><sub>hour</sub>
    
    Charting
    One Chart.js line chart:
    
    -   [X] Uses data only from MetricSeries
    -   [X] Updates when date range changes
    
    Testing:
    
    -   At least:
        -   [X] 1 parser golden test
        -   [X] 1 rate calculation golden test
    -   [X] Test suite passes with no skipped tests


<a id="org8e76d31"></a>

### DONE Phase 2 Context

-   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 10:33]</span></span>
-   State "IN PROGRESS" from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 09:22] </span></span>   
    Needs revisiting

1.  Milestones

    -   [X] Tier filtering
    -   [X] Preset filtering
    -   [X] Delta calculations

2.  Exit Criteria <code>[100%]</code>

    Context Filters
    
    -   [X] Tier filter affects:
        -   analysis output
        -   chart display
    -   [X] Preset filter:
        -   allows selecting one active preset
        -   correctly limits aggregation scope
    
    Delta Calculations
    
    -   [X] At least one delta metric exists:
        -   absolute and percentage
    
    -   [X] Delta calculations:
        -   work between arbitrary time windows
        -   are covered by golden tests
    
    UX
    
    -   [X] UI clearly shows when filters are active
    -   [X] Clearing filters returns to baseline view
    
    Testing
    At least:
    
    -   [X] 1 delta golden test
    -   [X] 1 aggregation test using presets


<a id="orgfed99e7"></a>

### DONE Phase 3 — App Structure & UX

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 09:22]</span></span>

1.  Milestones <code>[100%]</code>

    -   [X] Navigation
    -   [X] Page separation
    -   [X] Dashboards
    -   [X] Model completeness (structure, not logic)


<a id="orgfdbc9ff"></a>

### DONE Phase 4 Effects

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 11:35]</span></span>

1.  Scraping Sources and Corrective Behavior

    -   [X] Need a Management Command to Purge WikiData, Bot Definitions, Bot Levels, Bot Parameters, Guardian Chip Definitions, Guardian Chip levels, Guardian Chip Parameters, UW Definitions, UW Levels, UW Parameters.
    
    -   Each parameter can be upgraded individually, so they aren't in sync by level. Current level/level unlocked can be tracked within Parameters.
    -   Note parameters like Range, Duration and Cooldown are unique to each UW, Bot, or Chip
    
    1.  Bots
    
        The scraper fetchs the wrong data/table. The 4 parameters for each bot share a cost value for the upgrades. Upgrades are purchased individually, so level isn't shared across them.
        
        The cost is in Medals.
        
        The labs tables are outside of the current scope.
        
        -   **Thunder Bot:** Duration, Cooldown, Linger, Range. All that data is in the first table on <https://the-tower-idle-tower-defense.fandom.com/wiki/Thunder_Bot>
        -   **Flame Bot:** Damage Reduction, Cooldown, Damage, Range. <https://the-tower-idle-tower-defense.fandom.com/wiki/Flame_Bot>
        -   **Golden Bot:** Duration, Cooldown, Bonus, Range. <https://the-tower-idle-tower-defense.fandom.com/wiki/Golden_Bot>
        -   **Amplify Bot:** Duration, Cooldown, Bonus, Range. <https://the-tower-idle-tower-defense.fandom.com/wiki/Amplify_Bot>
    
    2.  Ultimate Weapons
    
        -   3 Parameters each, can be upgraded individually by level.
        -   Cost is in Stones
        -   Labs and Ultimate Weapon Plus are out outside of the current scope for tracking
        -   Similar to Bots, all levels are in the first table for each UW page, with an anchor for #Basic<sub>Upgrades</sub>
        
        -   **Chain Lightning:** Damage, Quantity, Chance <https://the-tower-idle-tower-defense.fandom.com/wiki/Chain_Lightning>
        
        -   **Death Wave:** Damage Multiplier, Effect Wave, Cooldown <https://the-tower-idle-tower-defense.fandom.com/wiki/Death_Wave#Basic_Upgrades>
        
        -   **Golden Tower:** Coins Multiplier, Duration, Cooldown <https://the-tower-idle-tower-defense.fandom.com/wiki/Golden_Tower#Basic_Upgrades>
        
        -   **Spotlight:** Coins Bonus, Angle, Quantity (number of active spotlights) <https://the-tower-idle-tower-defense.fandom.com/wiki/Spotlight#Basic_Upgrades>
        
        -   **Smart Missles:** Damage Multiplier, Quantity, Cooldown <https://the-tower-idle-tower-defense.fandom.com/wiki/Smart_Missiles#Basic_Upgrades>
        
        -   **Chrono Field:** Duration, Slow, Cooldown <https://the-tower-idle-tower-defense.fandom.com/wiki/Chrono_Field#Basic_Upgrades>
        
        -   **Inner Land Mines:** Damage %, Quantity, Cooldown <https://the-tower-idle-tower-defense.fandom.com/wiki/Inner_Land_Mines#Basic_Upgrades>
        
        -   **Poison Swamp:** Damage Multiplier, Duration, Cooldown <https://the-tower-idle-tower-defense.fandom.com/wiki/Poison_Swamp#Basic_Upgrades>
        
        -   **Black Hole:** Size, Duration Cooldown <https://the-tower-idle-tower-defense.fandom.com/wiki/Black_Hole#Basic_Upgrades>
    
    3.  Guardian Chips
    
        -   There are currently 5 chips available
        -   Costs are in Bits
        -   3 Parameters Each
        -   All information is located on <https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian> with a unique anchor for each chip
        
        -   **Ally:** Recovery Amount, Cooldown, Max Recovery <https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian#Ally>
        -   **Attack:** Percentage, Cooldown, Targets
            These are tracked in Battle Reports <https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian#Attack>
        -   **Fetch:** Cooldown, Find Chance %, Double Find Chance
            These are tracked in Battle Reports. Note there is an irrelevant table above Upgrades for this chip  <https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian#Fetch>
        -   **Bounty:** Multiplier, Cooldown, Targets
            <https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian#Bounty>
        -   **Summon:** Cooldown, Duration, Cash Bonus
            <https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian#Summon>
    
    4.  Cards
    
        -   All listed on <https://the-tower-idle-tower-defense.fandom.com/wiki/Cards#List_of_Cards>
        -   'Description' Column explains target and how it's modified
        -   Card Slots are unlocked with Gems.

2.  Milestones

    -   [X] CardParameters → effective values
    -   [X] UW / Guardian parameterized metrics
    -   [X] Derived metrics charts

3.  Exit Criteria <code>[100%]</code>

    Wiki Effects Infrastructure
    
    -   [X] At least one complete pipeline:
        -   scrape → version → reference → compute
    -   [X] Demonstrated on one entity type (pick one):
        -   UW or Bot or Guardian
    -   [X] Wiki revision change produces different derived output
    -   [X] Golden test proving revision safety
    -   [X] One derived effect chart rendered dynamically
    
    Parameterized Effects
    
    -   [X] At least one wiki-derived parameter table is:
        -   scraped
        -   versioned
        -   referenced by the Analysis Engine
    
    -   [X] At least one effect calculation exists:
        -   e.g. effective cooldown or EV of wave skip
    
    Derived Metrics
    
    -   [X] Derived metrics:
        -   are computed dynamically
        -   are not persisted
    -   [X] Derived metrics appear as charts:
        -   alongside raw metrics
        -   with correct units
    
    Backward Safety
    
    -   [X] Changing wiki parameters:
        -   does not invalidate existing runs
        -   produces different derived results when re-run
    
    Testing
    
    -   At least:
        -   [X] 1 golden test for a parameterized effect
        -   [X] 1 test validating revision behavior


<a id="org2d7f882"></a>

### DONE Phase 5 Dashboard UX <code>[100%]</code>

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-18 Thu 10:46]</span></span>

Goal:

-   Turn the analysis engine outputs into clear, usable, player-facing dashboards.
-   No new math. No new scraping logic. No new domain models.

Previous drafts indicated using Tailwind CSS for this project. We will now be implementing Foundation Framework.

General conventions across all Dashboards:

-   Nav Header
-   Global Search Box
-   Links to Docs and Admin
-   Apply Foundation styles consistently
-   Establish shared dashboard components:
    -   Filters (Tier, Date Range, Preset)
    -   Empty states
    -   Loading states

1.  DONE Battle History

    -   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 16:54]</span></span>
    -   State "IN PROGRESS" from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 14:13]</span></span>
    -   Display Results in a Styled Table with Sortable Columns
    -   Include:
        -   Killed By	Boss
        -   Coins earned	1.24M
        -   Coins per hour	4.24M
        -   Cash earned	$1.00M
        -   Interest earned	$220.24K
        -   Gem Blocks Tapped	1
        -   Cells Earned	0
        -   Reroll Shards Earned	94
    -   Filter by Tier, Killed By
    -   Can be paginated
    
    1.  DONE Need Widget to add new Battle History
    
        -   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 16:06]</span></span>
        -   State "IN PROGRESS" from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 16:00] </span></span>   
            make it collapsible
        
        It got moved to Charts/. It should also be at the top of Battle History.
    
    2.  DONE Need to Populate New Columns
    
        -   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 16:01]</span></span>
        
        Killed By, Coins Earned, Interest, Gem Blocks, Cells Earned, Reroll all empty. Need to reparse previous Battle Reports
    
    3.  DONE Table Columns should be sortable
    
        -   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 16:01]</span></span>
        
        Click on header to sort table

2.  DONE Charts

    -   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-18 Thu 10:46]</span></span>
    -   State "IN PROGRESS" from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 16:55] </span></span>   
        vastly improved but need to build out support for Bots/UWs/Guardian Chips before they show properly on Charts.
    
    Pretty dashboard of metrics over time (filterable by date range and tier)
    
    Support:
    
    -   Date range filter. Default View is by Event (start is 12/9/2025 00:00 UTC)
    -   Tier filter
    -   Ensure all charts consume MetricSeries only
    -   Select Chart from Multiselect Dropdown Menu
    
    Top Level Charts:
    
    -   Coins Earned (line)
    -   Coins per Hour (line)
    
    Sub Charts:
    
    -   Cash Earned
    -   Cells Earned
    -   Reroll Dice Earned
    
    -   UW Performance
        
            Breakdown and Comparison Views of RunCombat filtered to Given UW
            - List unlocked UWs
            - Show parameter levels + effective values
    -   Guardian Stats
        
            Breakdown and comparison views of RunGuardian over time
            Equipped State
            Parameter Summary
    -   Bots Stats
    -   Comparison Charts
        -   Same metric, different tiers
        -   With / without specific preset active
        -   Moving averages
    -   Derived Metrics
        -   Effective cooldown reduction
        -   Coins per wave vs wave number

3.  DONE Documentation and Polish

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 16:01]</span></span>
    
    the tone and structure I'm  aiming for: professional, concise, technically accurate but still readable for non-technical users. 
    
    -   Consistent, hierarchical headings → perfect for generating a table of contents automatically in Google Docs.
    -   Clear sectioning by task flow (Overview → Setup → Operation → Advanced → Appendix).
    -   Step-by-step procedures with short bullet or numbered lists.
    -   Cautions and notes highlighted distinctly (we can use blockquotes and icons)
    -   Simple, non-code formatting — short, direct action verbs instead of command line snippets.
    
    -   [ ] Add Material Theme, mkdocstrings-python support
        Similar to mscrInventory's mkdocs.yml
        
            
            theme:
              name: material
              language: en
              palette:
                - scheme: default
                  primary: indigo
                  accent: blue
              features:
                - navigation.instant
                - navigation.sections
                - navigation.expand
                - navigation.path
                - navigation.top
                - search.suggest
                - search.highlight
                - search.share
                - toc.integrate
                - content.tabs.link
                - content.code.copy
              icon:
                repo: fontawesome/brands/github
            
            markdown_extensions:
              - admonition
              - toc:
                  permalink: true
              - footnotes
              - tables
              - fenced_code
              - codehilite:
                  guess_lang: false
              - def_list
              - attr_list
              - md_in_html
              - admonition
              - pymdownx.details
              - pymdownx.extra
              - pymdownx.superfences
              - pymdownx.highlight
              - pymdownx.inlinehilite
              - pymdownx.snippets
              - pymdownx.magiclink
              - pymdownx.mark
              - pymdownx.keys
              - pymdownx.tasklist:
                  custom_checkbox: true
              - pymdownx.emoji:
                  emoji_generator: !!python/name:pymdownx.emoji.to_svg
            
              plugins:
              - search
              - mkdocstrings:
                  handlers:
            	python:
            	  paths: ["."]
            	  options:
            	    show_source: true
            	    docstring_style: google
            	    merge_init_into_class: true
              - autorefs
    -   [ ] Move Phase 1, Phase 2, Phase 2.75, Phase 3, and Phase 4 under 'Development'
    -   [ ] Merge 'Management Command' section for 'fetch<sub>wiki</sub><sub>data</sub>' with 'Wiki Population' page
    -   [ ] Add Docs for Each Dashboard
        -   Callout Charts and Cards in index.md
    
    -   [ ] Add mkdocstrings pages for commands/API/etc.

4.  DONE Need method for handling Player Bots/Cards/UW/Gaurdian Chips

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 16:01]</span></span>
    
    Hasn't been built out or thought out yet.

5.  DONE Cards <code>[100%]</code>

    -   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 18:04]</span></span>
    -   State "IN PROGRESS" from "DONE"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 16:45] </span></span>   
        scope creep!
    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:58]</span></span>
    -   Show a utility widget with 'CardSlots' Unlocked and a button to 'Unlock Next Slot'
    -   List all Cards in a Collapsible Table
        -   Multiselect to add/create preset relationship to a card.
        -   textbox to enter current inventory
        -   Display 'CardLevel' and 'CardParameters'
        -   Filter by Preset
    
    1.  DONE Inventory needs to track progress toward next level
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:11]</span></span>
        
        Cards have 7 levels of boost and progress to the next level at 0, 3, 5, 8, 12, 20, and 32. So the 'inventory' field will be used to track progress to the next tier. If you have 4 stars for a card, inventory would reflect collected up to 12 (next threshold).
        
        -   ****NEED**** to decide how to roll over to higher tiers. If a player has 18/20 needed and collects 3 from the in game store. The new result would be 1/32.
        -   Highlight rows to denote rarity
        -   Highlight cards that are maxed out level 7 32/32 collected.
    
    2.  DONE Parameter Column should be populated with card<sub>definition.description</sub>
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:11]</span></span>
    
    3.  DONE Need a Filter Reset button for Presets
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:11]</span></span>
        
        There should be an easier way that editing the Query String in the URL 
    
    4.  DONE Preset Membership should be styled as badges
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:11]</span></span>
        
        <https://get.foundation/sites/docs/badge.html>
        
        -   Colored with at least 6 different colors. Can be assigned on creation.
    
    5.  DONE Preset Tags Widget labels should be styled to match and be clickable links to apply the filter
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:11]</span></span>
    
    6.  DONE Remove Card Library Block
    
        -   State "DONE"       from "WAIT"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:11]</span></span>
        -   State "WAIT"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 17:38] </span></span>   
            haven't decided yet
        
        It's big and not necessary. 
    
    7.  DONE Battle History <-> Preset Linking
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:11]</span></span>
    
    8.  DONE Card Slots Widget should be functional
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:58]</span></span>
        
        Shows count of unlocked card slots and Gems cost of next slot
    
    9.  DONE Table Columns should be wortable
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 18:04]</span></span>
    
    10. DONE Filter by Maxed/Unmaxed Cards
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 18:04]</span></span>
    
    11. DONE Show Level Effect in Parameters
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 18:04]</span></span>
        
        For 'Attack Speed':
        Increase tower attack speed by x #
        
        Should read:
        Increase tower attack speed by x 2.15 (for level 7)

6.  DONE UW Progress

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 15:53]</span></span>
        -   Clean up source of 'Unknown' Parameters. There should only be 3 for each UW
            -   Exactly 3 parameters per UW
                ParameterKey registry validation
                No “Unknown” rendering path in the UI
                
                If a parameter can’t be resolved, fail loudly in dev and show a controlled warning in prod. This will save you pain when Chips/Bots inherit the same components.
                
                -   Call the core UI unit something like: "UpgradeableEntityDashboard"
                    
                    That mental model will pay off when you duplicate this for:
                    
                    -   Ultimate Weapons
                    
                    -   Guardian Chips
                    
                    -   Bots
        -   Add button to unlock each UW
            -   Dashboard should be sorted with unlocked UWs at the top
            -   Optional filter:
                -   Unlocked only
                -   Locked only
            -   For locked UWs:
                -   Replace parameter rows with a clean locked state panel
                -   Show:
                    -   Unlock cost
                    -   Short description / role (1 line)
                    -   “Unlock” CTA
        -   Show a summary of Upgrades for each UW
            -   Total Stones invested
            -   Key headline stat
                -   Compute the lifetime contribution of each UW based on Battle Report
                -   Each UW has exactly one “headline stat”
                    It must map to:
                    -   A known Run\* model field, or
                    -   A derived metric you already track
                -   Summary row should explicitly say:
                    “No battles recorded yet”
        -   Show Current Upgrade Level and Value
        -   Add buttons to level up each parameter
            -   Optimistic UI update + server validation
            
            -   Button locks until response returns
        
        -   Show next upgrade value and cost (Cost is in Stones)
            -   Disable or visually lock the level-up button when maxed
            -   Clearly label MAX
            -   When showing: Current value → Next value
                Visually emphasize the delta:
                -   +X%
                -   −0.3s
                -   +2 targets

7.  DONE Guardian Chip Progress

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 17:14]</span></span>
    
    The naming is important
    
    This dashboard will be similar to 'Ulitmate Weapons'
    
    -   Each Chip needs a checkbox for 'active'
        -   Currently only 2 can be active during a round of the game
    -   Upgrade Costs are in Bits
    -   Exactly 3 parameters per Guardian Chip
        ParameterKey registry validation
        No “Unknown” rendering path in the UI
    
    1.  DONE Need Hero Block for the 'Active Chips'
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 17:14]</span></span>
        -   Display the two marked active at the top of the dashboard
        -   Only two chips can be active at a time (this may change in future updates
        -   

8.  DONE Bots Progress

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 16:31]</span></span>
        This dashboard will be similar to 'Ulitmate Weapons'
        -   Exactly 4 parameters per Bot
            ParameterKey registry validation
            No “Unknown” rendering path in the UI
        -   Once unlocked each bot is permantly active
        -   Upgrade Costs are in Medals
    
    1.  DONE Bots Dashboard check math on 'total medals invested'
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 17:14]</span></span>
        
        It's showing values before any upgrades have been applied 

9.  Milestones

    -   [X] All dashboards share a single visual and structural language
    -   [X] On Battle History Player can scan, filter, and trust historical data quickly
    -   [X] A new contributor understands the app without a walkthrough

10. Exit Criteria <code>[100%]</code>

    UX & Data Integrity:
    
    -   [X] Dashboards display only computed outputs
    -   [X] No dashboard performs calculations inline
    -   [X] All filters affect views consistently
    
    Coverage:
    Every major entity has a visible dashboard:
    
    -   [X] Battle History
    -   [X] Charts
    -   [X] Cards
    -   [X] UWs
    -   [X] Guardians
    -   [X] Bots
    
    Stability:
    
    -   [X] No new models added
    -   [X] No migrations required
    -   [X] Test suite passes unchanged
    
    \### Demo Test
    A new user can:
    
    1.  Import runs
    2.  View history
    3.  Inspect progress
    4.  Understand trends …without explanation.


<a id="orge0780d6"></a>

### DONE Phase 6 Expansion of Foundation and Context <code>[33%]</code>

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-18 Thu 14:53]</span></span>

What’s done has been minimal by design. Now we can expand it to feel “real”. Make foundational rates, units, and context provably correct, visibly coherent, and ready to support higher-order comparisons.

****Foundation First****

Nothing else should proceed until this is locked.

A. Canonical Rate Metrics

-   Coins Earned by Source → ✅ good candidate for donut

-   Guardian Chip Performance → split into:
    -   Contribution metrics (damage, coins, summons)
    
    -   Fetch metrics (gems, shards, modules)

****Refinements****

-   Explicitly define:
    -   Which metrics roll up into Coins Earned by Source
    
    -   Which are excluded but cross-referenced

-   Add a schema note:
    -   \`MetricCategory = {economy, combat, fetch, utility}\`

****Exit Criteria****

Each rate metric:

-   Is derived from Battle Reports only

-   Appears in exactly one category

-   Has a deterministic total (sum of sources = total coins)

****Units Class****

This is a value wrapper and  a validation layer

-   Start as validation + formatting only

-   No runtime math yet beyond normalization

Tests

-   Explicit unit tests for:
    -   % vs x vs time
    
    -   Magnitude safety (K / M / B / T)
    
    -   Mixed-unit rejection (fail fast)

****Exit Criteria****

-   Any metric with ambiguous units fails validation

-   No dashboard renders a value without a unit contract

****Foundations:****
Revisit the work from phase 1 and expand it

-   [X] Add 2–3 more canonical rate metrics. Both of these would be best displayed as a donut chart. 
    -   Coins Earned by Source:
        The following values are available in Battle Reports. We should track them and show the breakdown of Coin sources. 
        -   Coins From Death Wave	119.49K
        -   Cash From Golden Tower	$45.27M
        -   Coins From Golden Tower	3.72M
        -   Coins From Black Hole	0
        -   Coins From Spotlight	41.37K
        -   Coins From Orb	0
        -   Coins from Coin Upgrade	7.23M
        -   Coins from Coin Bonuses	9.61M
    -   Guardian Chip Performance:
        Also already in Battle History. metrics should be split by unit type.
        -   Damage	2.49T
        -   Summoned enemies	0 quantity
        -   Guardian coins stolen	0 quantity (and should be included in 'Coins Earned by Source'
        -   Coins Fetched	16.62K quantity (and should be included in 'Coins Earned by Source'
        -   Gems	1 this and the remaining metrics can all be combined as 'Fetch metrics'
        -   Medals	1
        -   Reroll Shards
        -   Cannon Shards	3
        -   Armor Shards	0
        -   Generator Shards	3
        -   Core Shards	0
        -   Common Modules	0
        -   Rare Modules	0

-   [X] Lock down Unit Model correctness
    -   Explicit tests for %, x, time units, magnitudes

-   ****Why this matters:****
    
        Every chart, comparison, and recommendation later assumes these rates are correct and consistent.

****Context:****
Revisit and build on phase 2 work

-   [ ] Preset filtering edge cases
    -   No preset selected
    -   Preset selected but no matching runs
-   [ ] Tier + Preset + Date range combinations
    Explicit Precedence:
    1.  Date Range
    2.  Preset
    3.  Tier
    4.  Empty states must:
        -   Render UI
        -   Return typed but empty MetricSeries

Golden Test

-   Your “context matrix” test is excellent. Make it mandatory.

****Exit Criteria:****

-   Same metric + same raw data + different contexts:
    -   Same schema
    
    -   Predictable empty/non-empty behavior
    
    -   No silent fallbacks

-   [ ] Rolling windows (last N runs, last N days)
-   [ ] Add:
    -   One “context matrix” golden test
        -   Same metric, same data
        -   Different context inputs
        -   Assert expected shape, not just values

****Effective Value****

-   [ ] Effective Value vs Base Value
    
    For each parameter, show:
    
    -   Base value (raw level value)
    -   Effective value (after cards, labs, relics, etc.)
    
    This reinforces the mental model you’ve been building everywhere else:
    GameData → Derived Metrics → What actually happens in a run.
    
    just a tooltip or expandable row that says “+X% from Cards” is enough.
    
    Guidance:
    
    -   Keep this read-only
    
    -   Tooltip / expandable row only
    
    -   No recommendations yet
    
    ****Exit Criteria:****
    
    -   Every parameter row can explain:
    
    -   Base value
        -   Effective value
        
        -   At least one contributing modifier

****Efficiency Metrics****
  Examples:

-   Stones per % improvement
-   Stones per second saved
-   Relative efficiency compared to other UWs

This is powerful, but it opens balance and interpretation questions. Best added once the core dashboards are stable.

Keep this as a Phase 6 appendix only:

-   Spec definitions

-   Sample calculations

-   No UI beyond maybe one static comparison table

This prevents balance arguments from stalling Phase 6.

****Documentation****

-   [X] Add Github Action to publish Docs to Github Pages
-   [ ] Phase 6 Concepts” doc:
    -   Units
    -   Effective vs Base
    -   Context
    -   Why donut charts are used

****Phase 6 Exit Criteria:****

-   All displayed rates:
    -   Have validated units
    
    -   Are derived from canonical sources

-   Context changes:
    -   Never change metric meaning, only scope

-   Effective values:
    -   Are visible and explainable everywhere parameters appear

-   No efficiency or recommendation logic depends on undocumented assumptions


<a id="org6f8cc14"></a>

### DONE Phase 7 Power Tools <code>[100%]</code>

-   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 13:50]</span></span>
-   State "IN PROGRESS" from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-18 Thu 19:34] </span></span>   
    Needs to be manually tested/UAT pass

1.  DONE Add Chart Builder Modal to Charts Dashboard

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 12:51]</span></span>
    
    Let user select chart style and metrics to show. The Chart Builder is not a UI feature — it’s a schema and contract feature.
    
    Before UI polish:
    
    -   A ChartConfig DTO
        -   metric key(s)
        -   chart type
        -   grouping (time, tier, preset)
        -   smoothing / aggregation options
    
    Validation rules:
    
    -   Which metrics are compatible
    -   Which comparisons make sense
    -   A small, explicit allowed surface
    -   No arbitrary math
    -   No free-form queries
        **\*** TODO [#A] Comparison / Scenario View and Snapshots
    
    Examples:
    
    -   Run A vs Run B
    -   Before vs after unlocking card slot
    -   With Guardian Chip/UW X vs without
    
    This is where the app becomes decision-making, not logging.
    
    Named snapshots:
    
    -   “Before unlocking UW X”
    -   “Post Guardian Fetch upgrade”
    
    These become reusable comparison anchors in charts

2.  DONE Data Quality & Confidence Signals

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 12:09]</span></span>
    
    Players will ask:
    
    -   “Is this run weird?”
    -   “Did something change here?”
    
    Add:
    
    -   Run flags (outlier, partial, anomalous)
    -   Visual markers on charts
    -   Simple heuristics, not ML
    
    This builds trust without over-engineering.

3.  DONE UW Sync Graph

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 13:49]</span></span>
    
    There is synergy to using some UW together, specifically Golden Tower, Blackhole and Death Wave. It's common in the meta to keep the cooldowns and durations in sync. We should have the data to chart the three together and how often they overlap/synchronize

4.  DONE Performance Guardrails

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 12:53]</span></span>
    
    As data grows:
    
    -   Cached derived results per view
    -   Explicit limits on chart density
    -   Warnings when comparisons get statistically thin
    
    Do this before you have 30 guild members loading it daily.

5.  DONE UX Pass

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 12:52]</span></span>
    
    1.  Battle History
    
        -   [ ] Sort by 'Killed By' isn't sorting properly. It should filter alphabetically
        -   [ ] Add a tip that the input can only accept 1 battle report at a time. You can add validation that makes sure 'Battle Report' and 'Battle Date' appear exactly once.
    
    2.  Charts
    
        Functionality has expanded quite a bit and usability hasn't kept up.
        
        -   [ ] Move Filters to the right column. The wider area will make the controls easier to work with.

6.  DONE Add Advice for Optimization

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 12:53]</span></span>
    
    Based on logged performance data, it could be possible to calculate and offer suggestions based on the data.
    
    For Example:
    
    -   Which UW to unlock next
    -   Bot properties to improve
    -   Guardian Chip properties to improve
    -   Weighted Preset Rankings

7.  DONE Validation Gatekeepers

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 12:52]</span></span>
    -   DTO used end to end
        Introduce a single persisted/serializable DTO (and version it), use it for snapshot storage, and have the UI submit that DTO (or a strict field set) that round-trips without lossy transforms; add tests that snapshot round-trip reproduces identical DTO.
    -   analysis accepts ChartConfig and returns DTOs only
        Create an analysis-layer entrypoint like analysis/chart<sub>builder.py</sub> that takes a validated ChartConfig (or builder DTO) and returns DTOs (series + metadata + comparison datasets) without any template/render knowledge; refactor core/charting/render.py to become pure formatting; add tests that renderer doesn’t compute business logic.
    -   UI shows only valid combinations
        Add dynamic option filtering based on registry + current selections (hide/disable + explain), not just post-validate. Likely a small endpoint that returns allowed combinations, or richer JS rules that consult metric metadata embedded in the page. Add UI tests that invalid combinations cannot be selected.
    -   snapshots reusable across dashboards
        What’s missing: Snapshots can be saved/loaded in the Charts modal, but they’re not a reusable “anchor” across other dashboards/pages.
        What I need: Decide what “reusable across dashboards” means in this app (e.g., global context selector applied to Charts + Battle History + Progress pages), then implement a shared snapshot picker (base template or shared component), and update multiple views to consume it consistently. Add integration tests for at least two pages.
        
        ****You got it. In the future charts/snapshots on the progress dashboards is exactly what this app needs****
    -   known patch boundaries
        Add a deterministic source of patch boundary dates (settings constant, config file, or small model if you want admin-managed), pass them into render<sub>charts</sub>(&#x2026;, patch<sub>boundaries</sub>=&#x2026;), and add tests + a user-facing note describing what the boundary marker means.
    -   overlap windows displayed
        Compute overlap intervals (e.g., list of [start, end] windows) and display them (table under chart and/or ****visual band annotations****). Add tests for interval extraction.    
        ****Just the visual band will suffice, no need for the table. We should also add Golden Bot to this chart.****
    -   advice consumes chart comparisons + snapshot deltas
        Define an Advice input contract that takes (a) a validated chart comparison config and/or (b) two snapshot references, then computes deltas strictly from existing metric series outputs; add trace links (“based on chart X, scopes A/B”) and tests proving it’s derived from those DTOs.
    -   “Insufficient data” degradation
        Implement explicit insufficiency detection (e.g., <N runs per scope, missing values, empty windows) and return a structured advice item that says “Insufficient data” + why; add tests for empty and thin scopes.


<a id="org36657fe"></a>

### DONE Phase 8 Multiple Player Support

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 15:42]</span></span>

Phase 8 is the point where the app stops being “your stats tracker” and becomes a shared system.
Everything else (advice, exports, demos) hangs off that fact.

\## At a high level, Phase 8 has three pillars:

1.  Multi-player data isolation (core)

2.  Trustable, explainable advice (behavioral layer)

3.  Light sharing and demo affordances (polish & adoption)

Only #1 is truly non-negotiable. The others are value multipliers.

Execution order matters: Pillar 1 must be complete and validated before Pillars 2 or 3 begin.

\## What Phase 8 Is Not

To keep it clean, Phase 8 should not try to:

-   Introduce simulations or RNG modeling

-   Add cloud sync or real-time features

-   Solve balance questions

-   Become a recommendation engine that “knows best”

\## The real success criterion for Phase 8 is simple:

Thirty guild members can use this daily without seeing, affecting, or confusing each other’s data—and they trust what the app tells them.

1.  DONE Pillar 1: Multiple Player Support (Foundational, Blocking)

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 14:59]</span></span>
    
    1.  Core Principle: Everything Belongs to a Player
    
        ****Analysis Engine is always player-scoped, even if there’s only one player.****
        Every player-specific model must be bound to a Player.
        
        Recommended structure:
        
            from django.contrib.auth.models import User
            
            class Player(models.Model):
                user = models.OneToOneField(User, on_delete=models.CASCADE)
                display_name = models.CharField(max_length=64)
                created_at = models.DateTimeField(auto_now_add=True)
        
        Then every mutable/progress model gets:
        
            player = models.ForeignKey(Player, on_delete=models.CASCADE)
        
        This includes:
        
        -   player<sub>cards</sub>
        -   player<sub>relics</sub>
        -   player<sub>labs</sub>
        -   battle<sub>report</sub>
        -   run<sub>history</sub>
        -   sim<sub>results</sub>
        -   etc.
    
    2.  Authorization
    
        Use groups + permissions, not custom flags.
        
        Suggested groups
        
        <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
        
        
        <colgroup>
        <col  class="org-left" />
        
        <col  class="org-left" />
        </colgroup>
        <thead>
        <tr>
        <th scope="col" class="org-left">Group</th>
        <th scope="col" class="org-left">Purpose</th>
        </tr>
        </thead>
        
        <tbody>
        <tr>
        <td class="org-left">admin</td>
        <td class="org-left">me</td>
        </tr>
        
        
        <tr>
        <td class="org-left">player</td>
        <td class="org-left">Default</td>
        </tr>
        </tbody>
        </table>
        
        You can enforce almost everything via queryset filtering, not permissions alone.
    
    3.  Queryset Filtering Is the Real Security Layer
    
        Permissions stop access.
        Querysets prevent data leaks.
        
        Pattern you’ll use everywhere
        
            def get_queryset(self):
                user = self.request.user
                if user.is_superuser:
            	return Model.objects.all()
                return Model.objects.filter(player__user=user)
        
        This applies to:
        
        -   Admin
        -   API views
        -   List views
        -   Export endpoints
        -   Sim endpoints
        
        If you forget this once, players see each other’s data.
        
        ****Any view that forgets to filter by player is considered a bug, not a feature gap.****
    
    4.  Django Admin: Lock It Down Properly
    
        ModelAdmin example
        
            class PlayerCardAdmin(admin.ModelAdmin):
                def get_queryset(self, request):
            	qs = super().get_queryset(request)
            	if request.user.is_superuser:
            	    return qs
            	return qs.filter(player__user=request.user)
            
                def save_model(self, request, obj, form, change):
            	if not change:
            	    obj.player = request.user.player
            	super().save_model(request, obj, form, change)
        
        Also:
        
        Remove player from editable fields for non-admins
        
        Use readonly<sub>fields</sub> where possible
    
    5.  API Layer (Even If You Don’t Build One Yet)
    
        Design as if you will.
        
        Never accept player<sub>id</sub> from the client
        
        Always derive it from request.user.
        
        ❌ Bad
        
        { "player<sub>id</sub>": 12, "wave": 4500 }
        
        ✅ Good
        
        player = request.user.player
        
        This avoids spoofing and simplifies logic everywhere.
    
    6.  Shared vs Player-Scoped Models (Important Distinction)
    
        You’ll have three categories of models:
        
        A. Global Reference Data (NO player FK)
        
        Cards
        
        Relics
        
        Labs
        
        Enemies
        
        Waves
        
        Balance constants
        
        These are read-only.
        
        B. Player State (HAS player FK)
        
        PlayerCard
        
        PlayerRelic
        
        PlayerLabProgress
        
        Unlocks
        
        Inventory
        
        C. Derived / Cached Results (HAS player FK)
        
        BattleReport
        
        SimulationRun
        
        AggregatedStats
        
        You can safely delete category C anytime.
    
    7.  Data Migration & Onboarding Flow
    
        You’ll need a clean onboarding path:
        
        User creates account
        
        Auto-create Player via signal
        
        Assign default group player
        
        Initialize baseline progress rows
        
        @receiver(post<sub>save</sub>, sender=User)
        def create<sub>player</sub>(sender, instance, created, \*\*kwargs):
            if created:
                Player.objects.create(user=instance)
        
        -   [ ] Existing single-player data is migrated into a Player record named 'mahbam42'

2.  DONE Precondition: Advice Language Enforcement Pass

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 14:59]</span></span>
    
    Goal:
    Ensure all advice output is non-imperative, non-authoritative, and explainable.
    
    Scan all Advice for Optimization outputs and related copy.
    
    Replace any imperative, prescriptive, or superlative language
    (“should”, “best”, “optimal”, “recommended”, etc.) with descriptive, comparative phrasing.
    
    Do not change underlying logic, metrics, or thresholds.
    
    If advice cannot be rewritten without becoming imperative, degrade it to
    “Insufficient data to draw a conclusion.”
    
    Validate that all advice remains scoped, explainable, and traceable to charts or snapshots.
    
    Enforcement Rule (Canonical)
    
    Advice outputs must never use imperative or superlative language
    (e.g. “should”, “best”, “optimal”, “recommended”, “must”).
    
    Allowed Language Patterns
    
    -   “Shows higher/lower performance…”
    
    -   “Appears more efficient under these conditions…”
    
    -   “Based on the following comparison…”
    
    -   “Data suggests…”
    
    -   “Insufficient data to conclude…”
    
    Disallowed Patterns
    
    -   “You should…”
    
    -   “Best upgrade…”
    
    -   “Optimal path…”
    
    -   “Always / Never”
    
    -   “Clearly better” (without scope)

3.  DONE Pillar 2: Advice Becomes Safe, Scoped, and Goal-Aware

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 14:59]</span></span>
    
    \## Advice Becomes Goal-Aware
    
    Introduce explicit player intent.
    
    Example intents:
    
    -   Economy / farming
    
    -   Progression / wave push
    
    -   Hybrid
    
    Key rule:
    
    -   Intent is declared, never inferred.
    
    This avoids creepy ML and keeps trust.
    
    Advice now becomes:
    
    -   “For your selected goal: Farming…”
    
    -   Same advice engine
    
    -   Different filters + weights
    
    -   Advice remains comparative and descriptive; ranked or prescriptive recommendations remain out of scope.
    
    \## Weighted Efficiency Models
    
    Phase 7 already computes:
    
    -   Stones per %
    
    -   Seconds per cooldown
    
    -   Coins per wave deltas
    
    Phase 8 adds:
    
    -   Weighting based on intent
    
    -   Transparent formulas
    
    Example:
    
    Efficiency Score =
    (coin<sub>delta</sub> \* economy<sub>weight</sub>)
    
    -   (wave<sub>delta</sub> \* progression<sub>weight</sub>)
    -   (upgrade<sub>cost</sub> \* penalty)
    
    \### Requirements:
    
    -   Weights are visible
    
    -   Editable
    
    -   Default presets provided
    
    -   No hidden math.

4.  DONE Pillar 3: Demo, Export, and Adoption Features (Non-Blocking)

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 14:59]</span></span>
    
    1.  DONE Demo User
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-20 Sat 10:29]</span></span>
        
        Take some of my data and make plausible changes to store as the Default User. Allow any player to also view the default user data as a preview/demo of the app. 
    
    2.  DONE Export / Share (Lightweight)
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-20 Sat 10:29]</span></span>
        -   CSV export of derived metrics
        -   PNG export of charts
        
        This dramatically increases perceived value with very little backend work.

5.  DONE Wireup Github Actions to Run Tests

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 15:42]</span></span>
    
    Run checks or Ruff Check, mypy ., pytest -q


<a id="orgc5fdabf"></a>

### DONE Phase 9 Deploy and Clean out Backlog <code>[100%]</code>

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-20 Sat 10:07]</span></span>

This is “trust + deployment” phase

You can confidently deploy when all Blocking items are complete, even if none of the Nice-to-Have items are.

-   closes the multi-player trust loop,

-   aligns docs, UI, and behavior,

-   removes ambiguity before outside users touch it,

-   makes the app deployable without apologies.

1.  DONE Add a 'Killed By' Donut Chart

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 19:43]</span></span>
    
    I thought we did this, but now I don't see it&#x2026;
    
    This is Data completeness confirmation and a useful sanity check visualization

2.  DONE Scope and Apply Permissions (Blocking)

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 19:43]</span></span>
    
    Need to assign Player and Admin permissions. The groups were created but the Permissions were never assigned. This may require a migration to assign them out. 
    
    Audit every view, admin, and export endpoint for player scoping

3.  DONE On the UW Dashboard Runs Used is not updating appropriately  (Blocking)

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 19:43]</span></span>
    
    Based on Battle Reports the 'runs used' should be >0. 

4.  DONE Cite Sources from the Wiki     :docs:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 19:58]</span></span>
    
    The docs should credit the Wiki early and often.

5.  DONE Name property links to wiki page as well

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 19:58]</span></span>
    
    Cards, UWs, Bots, Guardian Chips names should all link to the respective Wiki pages for additional information. They should be appropriately marked as external links. 

6.  DONE User Gmmuide Operation     :docs:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 19:58]</span></span>
    
    "Note Battle History surfaces only what exists in your imported text. If a label never appeared in the report, it will not be synthesized here."
    
    This note doesn't make sense. The Battle History is a read-only summary provided by the Game. So assume a player is pasting the full summary into our app every time.
    
    “This app does not invent or infer missing values.”
    “What you see reflects what the game reported.”

7.  DONE Deployment  (Blocking)

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-20 Sat 10:07]</span></span>
    
    Prepare App for deployment on Railway
    
    1.  Django Checklist:
    
        ?: (security.W004) You have not set a value for the SECURE<sub>HSTS</sub><sub>SECONDS</sub> setting. If your entire site is served only over SSL, you may want to consider setting a value and enabling HTTP Strict Transport Security. Be sure to read the documentation first; enabling HSTS carelessly can cause serious, irreversible problems.
        ?: (security.W008) Your SECURE<sub>SSL</sub><sub>REDIRECT</sub> setting is not set to True. Unless your site should be available over both SSL and non-SSL connections, you may want to either set this setting True or configure a load balancer or reverse-proxy server to redirect all connections to HTTPS.
        ?: (security.W009) Your SECRET<sub>KEY</sub> has less than 50 characters, less than 5 unique characters, or it's prefixed with 'django-insecure-' indicating that it was generated automatically by Django. Please generate a long and random value, otherwise many of Django's security-critical features will be vulnerable to attack.
        ?: (security.W012) SESSION<sub>COOKIE</sub><sub>SECURE</sub> is not set to True. Using a secure-only session cookie makes it more difficult for network traffic sniffers to hijack user sessions.
        ?: (security.W016) You have 'django.middleware.csrf.CsrfViewMiddleware' in your MIDDLEWARE, but you have not set CSRF<sub>COOKIE</sub><sub>SECURE</sub> to True. Using a secure-only CSRF cookie makes it more difficult for network traffic sniffers to steal the CSRF token.
        ?: (security.W018) You should not have DEBUG set to True in deployment.
        ?: (security.W020) ALLOWED<sub>HOSTS</sub> must not be empty in deployment.
    
    2.  Railway Deployment Guide
    
        <https://docs.railway.com/guides/django>
    
    3.  DONE Consolidate CSS and JS to static/
    
        -   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 21:40]</span></span>
    
    4.  DONE Prepare migration to Postgres
    
        -   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 21:40]</span></span>

8.  DONE Hide Admin Link if logged in as non admin/superuser

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 17:11]</span></span>

9.  DONE On UW/Bots/Guardian Chip Dashboards add a Decrease Level Button

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 17:11]</span></span>
    
    Safe guard in case a user accidently clicks upgrade by mistake

10. DONE Move UW Sync Graph to Bottom of Dashboard

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 17:11]</span></span>

11. DONE Amend how Death Wave works

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 19:57]</span></span>
    
    Specifically for our Sync Chart, but also as a point of information in the docs.
    
    The Death Wave is a single, powerful wave that deals damage based on a "damage pool."
    Damage Pool: This pool accumulates damage through multiple activations, rather than resetting with each new use, signaled by the Death Wave taking on a blue tint. The damage pool only decreases by the exact amount required to destroy enemies, factoring in any bonuses. This can deal damage through armored enemies.
    Persistence: The Death Wave remains active within your tower’s range until the damage pool is depleted.
    
    So depending on conditions Death Wave can persist for a long period. Including beyond it's cool down time, so it resets and remains active until the damage pool is depleated. 

12. DONE Clean Up and Revise Development Docs

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 20:21]</span></span>
    
    Make them all consistent in style and format. And put them in order -right now the phase 6 concepts is listed after everything else. 

13. DONE Runs Used on UW Dashboard

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 20:21]</span></span>
    
    It's still not right. It's showing 14 for all unlocked UWs. But I've only had Blackhole via Perk Upgrades, on a few of the runs I've added to the app.
    
    Each UW has a row in Battle Reports that we can use to track when a UW was active in a round.
    
    -   **Black Hole:** Black Hole Damage
    -   **Chain Lightning:** Chain Lightning Damage
    -   **Golden Tower:** Coins From Golden Tower (Under RunUtility)
    -   **Death Wave:** Death Wave Damage
    -   **Spotlight:** Destroyed in Spotlight (Under RunEnemies
    -   **Chrono Field:** There doesn't appear to be a metric for Chrono Field. So this one might alwys be 0 until the Game updates. We can note it in the docs that it doesn't work.
    -   **Poison Swamp:** Swamp Damage
    -   **Inner Land Mines:** Inner Land Mine Damage
    -   **Smart Missiles:** Smart Missile Damage
    
    If each of those metrics have a value greater than 0, that UW was active during a run.
    
    We should also note in the docs that false positives will occur and skew these counts. Because via Lab Research, Spotlight can fire missiles and the damage is logged in the same target we're using for Smart Missiles. Inner Land Mines can be deployed with a Module (Space Displacer) that we aren't tracking.

14. DONE Add Wiki External Links on Dashboards

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 20:21]</span></span>
    
    Cards, UWs, Bots, Guardian Chips

15. DONE Remove UW Sync from Nav Bar.

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 20:21]</span></span>
    
    And update tests for it. 

16. DONE How does a player create a snapshot

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-20 Sat 10:06]</span></span>
    
    I dont see a UI element for it, nor is it covered in the documentation


<a id="org62a0c69"></a>

### DONE Phase 10 v0.2.0

-   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 15:17]</span></span>

“Stabilize, standardize, and clarify the product surface.”

Phase 10 Goal:

-   Improve clarity, consistency, and usability across the app

-   Reduce cognitive load in charts and navigation

-   Establish release hygiene (README, CHANGELOG, versioning)

-   Prepare the codebase and UI for iterative public use

Non-Goals:

-   No new metrics, advice logic, or analysis behavior

-   No schema changes beyond version metadata

-   No new permissions or player concepts

1.  Release & Maintainability

    1.  DONE Update readme.md
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 14:27]</span></span>
        -   Make sure it's still aligned with App Behavior and Features
        -   Project Status marks v0.1.0 Release
            and reflects docs/ revisions
            -   Can add brief summary of v0.2.0 work in progress and coming soon
        -   Add link to the app deployed on Railway thetowerstats.up.railway.app
    
    2.  DONE Implement ChangeLog.md
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 14:27]</span></span>
        
        Add to Docs and link in README.md
        
        -   Start initially with brief summary of work leading to v0.1.0 release and point to Developer Docs for additional detail.
        
        -   A CHANGELOG.md template Codex must maintain
            -   A “breaking change checklist” it must run before suggesting version bumps
            
            -   CHANGELOG entries must link to:
                -   Phase number
                
                -   Developer doc (if applicable)
        
        -   Moving forward there will be changes to agents.md and conventions for maintaining CHANGELOG.md
    
    3.  DONE Extend Python Versioning in Django.yml
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 14:27]</span></span>
        
        The app has been built and working with Python 3.14, but I don't think any of it requires the latest bleeding edge. 
        
        Specifically add python3.13.11 to match Railway's Environment
    
    4.  DONE Write Phase 9 Developer Docs
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 14:27]</span></span>

2.  UX & Interaction Refinement (Core UX)

    -   All spacing must resolve to the design scale
    -   All buttons must be primary or secondary — no ad-hoc styles
    -   Charts must use the shared palette registry
    
    1.  DONE Global Theming & Styling Suggestions
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 14:27]</span></span>
            A. Introduce a ********design scale********
            
            Define (and enforce):
            
            -   1 spacing unit (e.g., 4px or 8px)
            -   3 text sizes: label / body / heading
            -   2 button styles: primary / secondary
            
            Right now spacing feels “organic” rather than intentional.
            
            B. Charts need stronger contrast
            
            -   Axis labels are slightly too faint
            -   Gridlines compete with data at times
            
            Suggestions:
            
            -   Reduce gridline opacity
            -   Increase line thickness slightly
            -   Use consistent color palette across all charts (even comparisons)
            
            C. Color = meaning, not decoration
            
            You’re already data-driven—lean into that:
            
            -   One color for “coins”
            -   One for “progression”
            -   One for “comparison”
            
            Users should start recognizing metrics by color without reading labels.
    
    2.  DONE Navigation Bar Cleanup (Important)
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 14:27]</span></span>
        
        ****Constraints:****
        
        -   Max 4 primary nav items
        
        -   Anything else must live in:
            -   “More” dropdown or
            
            -   Contextual sub-nav
        
        -   Context controls must never disappear.
        
        -   Visualization controls may collapse.
        
        A. Fix wrapping by design, not luck
        
        Your top nav is trying to do too much in one row.
        
        ********Recommended pattern:********
        
        -   ********Left:******** Product name + primary sections (max 4)
        -   ********Right:******** Search, Docs, Account menu
        
        Move secondary links into:
        
        -   A “More” dropdown
        -   Or contextual sub-nav per section
        
        Example:
        
        \\\`\\\`\\\`
        theTowerStats | Charts | Battle History | Cards | More ▾
        				   🔍 Docs  👤
        \\\`\\\`\\\`
        
        B. Highlight current section strongly
        
        Right now section changes are subtle.
        
        -   Use:
            -   Bold text
            -   Bottom border
            -   Accent color
            -   Make it unmissable which dashboard you’re on
        
        This matters as the app grows.
    
    3.  DONE Improve Charts Controls
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 14:27]</span></span>
        
        > Key Principles
        > - Context defines scope, not visualization
        > - Charts are the focal point
        > - Advanced tools are opt-in
        
        -   Break the “Monolithic Controls” Problem
            
            A. Split controls into ********layers********, not one column
            
            Right now everything lives in a single vertical Filters panel, which forces users to mentally parse too much at once.
            
            ********Suggested structure (top → bottom):********
            
            1.  Context (always visible, compact)\\\*\\\*
                
                -   Date range
                -   Tier
                -   Preset
                -   Rolling window (if enabled)
                
                These define ****what data**** you’re looking at. They should feel global and stable.
            
            2.  Chart Definition (collapsible / modal)
                
                -   Metric(s)
                -   Chart type
                -   Group by
                -   Comparison mode
                
                This is ****how data is visualized****. It should not compete visually with context.
            
            3.  Advanced / Analysis (collapsed by default)
                
                1.  Moving average window
                2.  Snapshot comparison
                3.  Goal-aware weights
                
                These are power-user tools. Hide them unless explicitly opened.
                
                > ********Key principle:********
                > If a control doesn’t change the chart ****immediately****, it probably belongs behind a disclosure.
        
        B. Replace the giant sidebar with a ********Chart Control Bar********
        
        Instead of a right-hand monolith:
        
        -   Add a ********horizontal control bar above the chart(s)********:
            -   Metric selector (pill-style multiselect)
            -   Date range
            -   Tier
            -   Preset
            -   “⚙ Advanced” button
        
        It also reduces eye travel and keeps the chart as the focal point.
        
        C. Turn Chart Builder into a ********guided flow********
        
        Chart Builder is powerful, but cognitively heavy.
        
        ********Improve by:********
        
        -   Step-based layout:
            1.  Select metric(s)
            2.  Choose visualization
            3.  Group & compare
        -   Disable steps until prerequisites are met
        -   Show a live preview thumbnail
        
        This reinforces that it’s an ****intentional action****, not just “more filters.”
        
        1.  Improve Visual Hierarchy (Low Effort, High Impact)
            
            A. Use section headers with purpose
            
            Right now headers are informational but not directional.
            
            Example improvement:
            
            -   ********Filters******** → “Data Scope”
            -   ********Charts******** → “What to Measure”
            -   ********Advice******** → “Insights from Current View”
        
        Add 1-line helper text under headers where needed.
        
        B. Reduce label repetition
        
        You repeat context in multiple places:
        
        \\\*\\\* “Active context”
        
        -   Filter labels
        -   Chart titles
        
        -   Make “Active context” a compact breadcrumb-style line:
            
            \\\`\\\`\\\`
            Dec 9–17 • All tiers • All presets • No rolling window
            \\\`\\\`\\\`
        -   Let charts inherit this implicitly.
            
            C. De-emphasize rarely-used buttons
            
            Buttons like:
            
            -   “Export derived metrics”
            -   Snapshot save/load
            -   CSV exports
            
            Should be:
            
            -   Secondary buttons
            -   Icon-based
            -   Or inside an overflow menu (⋯)
            
            Right now they visually compete with primary actions.
        
        ********Exit Criteria:********
        
        -   Replace right-hand monolithic sidebar with:
            -   Horizontal Chart Control Bar
            -   Collapsible Advanced panel
        -   Context controls always visible
        -   Chart Builder becomes step-based and gated
        -   Active context rendered once as breadcrumb
        -   Secondary actions moved to overflow menu
    
    4.  TODO Make Charts Dashboard more Mobile Friendly
    
        On mobile, the primary task is viewing trends, not configuring charts.
        
        -   Filters, Advice, Goal Aware Comparison, Compare and Quick Import should be collapsible
        -   Move Quick Import to the Bottom
        -   Move Charts to the Top
        -   The break point seems to be around 630px wide
    
    5.  DONE Implement Search
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 14:54]</span></span>
        
        Search should have global scope within the app. 


<a id="org57c2d00"></a>

### DONE Phase 10B Additional UX

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 08:26]</span></span>

Additional Phase 10 Exit Definition:

-   Tests are classifiable and runnable by intent
-   Tournament data cannot contaminate normal analytics
-   Mobile UI has no obvious footguns
-   Primary actions are visually prioritized

Non-Goals for Phase 10:

-   No metric rebalance

-   No new derived stats

-   No schema changes beyond classification fields

1.  DONE Test Suite Health (Blocking)

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 08:25]</span></span>
    
    Defined unit and integration, but none of the tests use them, so you can’t easily run “fast unit only” vs “full integration” in CI/local.
    
    -   [ ] Add callouts for Regression and Golden as an additional markers (orthogonal) for fixture-driven, checksum/snapshot-style tests.
    -   [ ] Start using @pytest.mark.unit for pure functions/DTO parsing
    -   [ ] Use @pytest.mark.integration for anything with @pytest.mark.django<sub>db</sub>, views, commands, model interactions, wiki ingestion/rebuild, migrations.
    -   [ ] Add Test Taxonomy and Markings to Developer Docs, and fast vs full coverage
        -   [ ] Add one canonical example per category in the dev docs:
            -   1 unit test
            -   1 integration test
            -   1 regression/golden test
    -   [ ] Enforce markers in CI:
        -   Fail CI if a test has no marker.
        -   Add a pytest.ini section documenting intent (unit ≠ fast by accident)
    -   [ ] Each test must have exactly one speed marker (unit | integration), and may optionally have one semantic marker (regression | golden)
    
    Acceptance criteria
    
    -   [ ] pytest -m unit runs fast (< X seconds locally).
    -   [ ] CI has at least two jobs: unit and full.
    -   [ ] Dev docs include a short Test Taxonomy section.

2.  DONE Battle History Needs to Account for Tournament Runs.

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 08:25]</span></span>
    
    Battle Reports with 3+, 5+, 8+, etc are from Tournament Rounds and should be highlighted and separate from normal round tiers. There are modified enemy stats and added scaling battle conditions that make Tournament Rounds different from the corrisponding tiers.
    
    Tournament runs are inferred from existing fields (e.g. tier labels like 3+, 5+, 8+)
    
    Classification is:
    
    -   computed in Python
    
    -   applied in queries, serializers, or view logic
    
    -   UI and analytics use the derived classification
    
    Example (conceptual, not code):
    
    -   Tier ends with + → run<sub>type</sub> = tournament
    
    -   Numeric prefix → tournament<sub>bracket</sub>
    
    Treat Tournament Runs as a first-class dimension, not a visual tag:
    
    -   Add run<sub>type</sub> = normal | tournament
    
    -   Add tournament<sub>bracket</sub> = 3+ | 5+ | 8+ | …
    
    In UI:
    
    -   Visually separate (badge + background tint is enough)
    
    -   Default filters exclude tournaments unless explicitly enabled
    
    In metrics:
    
    -   Ensure tournaments are excluded from baseline averages unless opted in
    
    Scope control:
    
    -   Do not rebalance metrics in Phase 10
    
    -   Do not introduce new derived stats yet. Just classification + visibility.
    
    -   One function / property:
        -   is<sub>tournament</sub>(run)
        
        -   tournament<sub>bracket</sub>(run)
    
    -   Do not re-infer in templates or JS
    
    -   Do not scatter regex checks

3.  DONE Condense "Signed in as <user>"

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 08:25]</span></span>
    
    Either just the user name, or an icon + <user>
    
    Desktop: 👤 username
    
    Mobile: avatar/icon only, username on hover/tap
    
    Make the username the dropdown trigger (reduces nav clutter)

4.  DONE Hide Demo Data Button on Mobile

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 08:25]</span></span>
    
    Mobile: move to overflow menu or settings
    
    Desktop: keep visible but secondary-styled


<a id="orgb60c2c8"></a>

### Phase 11 Bug Fixes <code>[6/6]</code>

1.  DONE UW/Guardian Chip/Bots Dashboards (Blocking)     :bug:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 14:19]</span></span>
    -   [ ] Flip the Level Up / Level Down buttons.
        Level Up:
        
        -   Primary button
        -   Larger size
        -   Above Level Down
        
        Level Down:
        
        -   Secondary / danger style
    
    Disable Level Up when capped
    
    Disable Level Down at level 0
    
    Acceptance criteria:
    
    -   Primary CTA visually obvious
    
    -   No accidental downgrades
    
      **\*** TODO [#A] Manually tag Tournament Runs (0.2.x)
    The game visually indicates Tournament runs, but the plain text Battle Report does not.
    
    Need to add a manual flag to 'Add Battle Report' to flag runs as Tournament Runs. 

2.  DONE Normalize time handling everywhere (game time vs real time vs accelerated) (v0.2.0x)     :bug:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 14:19]</span></span>
    
    Game Time can be accelerated and the rate can be changed during a run. Either via Lab Research (max of 5x) or via perks that increase it further to a variable factor (increased by additional researchs). The hard maximum is 6.25x (according to the Wiki). However the Wiki also notes "Game speed is not accurate. x5.0 speed behaves closer to x4.0 while 6.25 is closer to x5." So our handling of it is not strictly necessary.
    
    Explicitly do not retroactively recompute historical metrics.

3.  DONE Revise project<sub>structure.md</sub> (v0.2.0x)     :bug:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 14:19]</span></span>
    
    It's outdated and needs expansion

4.  DONE Move ##Test taxonomy & markings to a dedicated testing page (v0.2.0x)     :bug:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 14:19]</span></span>
    
    Under Development Documentation.

5.  DONE URL redirection from remote source (Blocking)     :bug:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 15:31]</span></span>
    
    There are 51 detected occurances&#x2026; Apply the fix as a global function, fix where \`return redirect(redirect<sub>to</sub>)\` appears. 
    
    Direct calls to redirect(user<sub>supplied</sub><sub>value</sub>) are forbidden.
    All redirects must pass through safe<sub>redirect</sub>()
    
    For Django application, you can use the function url<sub>has</sub><sub>allowed</sub><sub>host</sub><sub>and</sub><sub>scheme</sub> to check that a URL is safe to redirect to, as shown in the following example:
    
        from django.http import HttpResponseRedirect
        from django.shortcuts import redirect
        from django.utils.http import url_has_allowed_host_and_scheme
        from django.views import View
        
        class RedirectView(View):
            def get(self, request, *args, **kwargs):
        	target = request.GET.get('target', '')
        	if url_has_allowed_host_and_scheme(target, allowed_hosts=None):
        	    return HttpResponseRedirect(target)
        	else:
        	    # ignore the target and redirect to the home page
        	    return redirect('/')
    
    Note that url<sub>has</sub><sub>allowed</sub><sub>host</sub><sub>and</sub><sub>scheme</sub> handles backslashes correctly, so no additional processing is required.

6.  DONE Wiki Population (v0.2.0x)     :bug:

    -   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 15:31]</span></span>
    -   State "IN PROGRESS" from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 14:33] </span></span>   
        Card Slot Updated still chasing Guardian Slot Issue
    -   [X] fetch<sub>wiki</sub><sub>data</sub> needs a &#x2013;target all arg
    -   [X] fetch<sub>wiki</sub><sub>data</sub> and rebuild<sub>wiki</sub><sub>definitions</sub> should have a pretty summary of deltas at the end.
        Especially when using &#x2013;target all.


<a id="orgd5e9c28"></a>

### Bugs/Enhancements <code>[23/25]</code>

1.  DONE Error Updating Guardian Upgrade Table     :bug:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 18:51]</span></span>
    -   [ ] Fix traceback error in production environment (it works in Dev)
        Command: python3 manage.py rebuild<sub>wiki</sub><sub>definitions</sub> &#x2013;target all &#x2013;write
        
        Traceback:
        
            raise ValueError(
              f"Guardian upgrade table drift for slug={slug}: expected 3 parameters, got {pairs!r}"
            )
            ValueError: Guardian upgrade table drift for slug=ally: expected 3 parameters, got []
        
        Expected Result:
        Retrieve 3 parameters from Wiki, 'Recovery Amount,' 'Cooldown (s),' 'Max Recovery' from <https://the-tower-idle-tower-defense.fandom.com/wiki/Guardian#Ally> table name 'Upgrades.'

2.  DONE Import Battle Report Not Working     :bug:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 16:23]</span></span>
    
    Battle Reports aren't being imported from the dashboard or charts quick import.
    
    I pasted in a battle report, clicked 'import battle report', the page reloaded but the battle isn't showing in the history table. This problem arose probably yesterday because I'm not seeing some other reports I tried to load, but I definitely caught it just now.
    Tried in Production and repeated the results in Dev.
    
    Expected result: Adding a battle report succeeds and is shown in the table and accesible in charts.
    
    Fix Battle Report import parsing for space-separated headers
    
    1.  DONE Battle Report Ingest Errors fail silently in Production
    
        -   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 16:23]</span></span>
        -   State "IN PROGRESS" from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 16:23] </span></span>   
            Production ingest errors no longer fail silently: core/views.py now catches unexpected exceptions from ingest<sub>battle</sub><sub>report</sub> when DEBUG=False, adds a safe non-field form error, and shows a user-visible message (still re-raises in dev).
        
        Should show validation error to players in production with debug = 0(/false)

3.  DONE Manually tag Battle Report as Tournament     :bug:

    -   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 16:23]</span></span>
    -   State "IN PROGRESS" from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 16:22] </span></span>   
        Added BattleReportProgress.is<sub>tournament</sub> (+ migration) in gamedata/models.py + gamedata/migrations/0005<sub>battlereportprogress</sub><sub>is</sub><sub>tournament.py</sub>.
        Added is<sub>tournament</sub> checkbox to BattleReportImportForm in core/forms.py.
        Wired checkbox into both import entrypoints (Battle History + Charts quick import) in core/views.py and displayed it in core/templates/core/battle<sub>history.html</sub> + core/templates/core/dashboard.html.
        Updated filtering so tournament-tagged runs are excluded by default everywhere that honors “Include tournaments” (core/views.py).
    
    The game adds visual markers to denote a Tournament round, but it's not indicated in the plain text we ingest. So we need to add a toggle to the Battle History dashboard and 'quick import' on Charts to mark a log as tournament or not. 

4.  DONE Cards Dashboard Enhancements (v0.x.x)     :enhancement:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 19:15]</span></span>
    
    1.  DONE Select Multiple Cards to Assign/Create Preset
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 18:59]</span></span>
        
        Add a checkbox to each card row to Assign or Create Preset
    
    2.  DONE On Cards Dashboard Level Column should by labeled "Next Level"
    
        -   State "DONE"       from "DELEGATED"  <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 19:14]</span></span>
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 18:59]</span></span>

5.  DONE Preset Labels should be better explained in the Docs

    -   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 16:57]</span></span>
    
    Currently states "Preset labels are shown as badges so you can scan for the context you assigned during import"
    
    Better language:
    Presets define card groupings (unlocked via Lab Research 'Card Presets'). The Game currently allows for 6 presets to be set, this app allows as many as you'd like. Define and set Presets from the Cards Dashboard.
    Presets can also be assigned to Battle Reports to track card usage over time. 
    
    1.  DONE Update copy in the Docs
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-23 Tue 13:50]</span></span>
        -   [ ] Overview
        -   [ ] Battle History
        -   [ ] Cards
    
    2.  DONE Add brief description of Presets to Cards Dashboard
    
        -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-23 Tue 13:50]</span></span>
        
        Add a block under the presets filter on the left

6.  DONE Chart Taxonomy (Codex-friendly)

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:18]</span></span>
    
    Think in three axes:
    
    1.  What system does this describe?
    
    2.  What question does it answer?
    
    3.  Is it absolute or relative?
    
    Charts must answer one of:
    
    -   “What did I get?”
    -   “Where did damage come from?”
    -   “What killed enemies?”
    
    Charts that answer “How should I play?” are out of scope.
    
    1.  Rebuild Chart Classifications
    
        -   Economy (What did this run produce?)
            
            -   Coins
            -   Cash
            -   Cells
            -   Reroll Shards
            
            Examples:
            
            -   Coins by Source
            -   Coins from Ultimate Weapons
            -   Cash Earned per Run
            -   Cash by Source (e.g. Golden Tower, Interest)
            -   Cells Earned per Run
        
        Reroll Shards Earned per Run
        
        -   Damage (Where did damage come from?)
            
            -   Damage by Source (absolute)
            -   Damage Contribution (relative / %)
            
            Examples:
            
            -   Damage by Source (stacked bar)
            -   % of Total Damage by Source (donut or stacked)
            -   Damage vs Enemies Destroyed (comparative)
        -   Enemy Destruction (“What actually killed enemies?”)
            Enemy Destruction charts must compute totals from child rows, never from Battle Report totals.
            
            -   Destruction by Source
            -   Enemy Type Distribution
            
            Exanples:
            
            -   Enemies Destroyed by Source (donut + %)
            -   Enemy Type Breakdown (Basic / Fast / Tank / Ranged / Boss)
            -   Destroyed in Spotlight / Golden Bot (as sources, not enemy types)
        -   Efficiency
            
            -   Time-normalized metrics
            
            Examples:
            
            -   Coins per Hour
            -   Waves per Hour
            -   Enemies Destroyed per Hour
    
    2.  Chart Types
    
        -   Distribution
            Donut, stacked bar
            → must show % explicitly
        
        -   Contribution
            Relative share of a whole
            → requires a derived denominator
        
        -   Absolute Totals
            Bars, timelines
            → no implied comparison
        
        -   Comparative
            Two related metrics side-by-side
            → must share units or be clearly labeled

7.  DONE On Charts Dashboard, Charts should show by date or by battle log     :enhancement:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:19]</span></span>
    
    Charts would be more clear if they also showed by battle report instead of only daily totals. 

8.  DONE Filter Charts by Event Dates     :enhancement:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:19]</span></span>
    
    Events are 14 Days long. The previous event started on 12/09/2025 to 12/22/2025 and the current event is 12/23/2025 to 01/08/2026.
    
    Charts should have a default date range of the current event start to end, buttons to move backward or forward (to end of current), and preserve the current manual date range fields.
    
    Documentation should be updated to reflect this. And a note should be added to the Date Range controls that they coorispond to the 'In Game Events'

9.  DONE Add Damage Charts/Metrics

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:19]</span></span>
    -   Total Damage
        take 'damage dealt' as total
    
    Use the following metrics from 'Battle Report':
    
    -   Projectiles Damage	17.94Q
    
    -   Thorn damage	267.27Q
    
    -   Orb Damage	3.36s
    
    -   Land Mine Damage	331.60q
    
    -   Rend Armor Damage	0
    
    -   Death Ray Damage	13.61q
    
    -   Smart Missile Damage	1.79q
    
    -   Inner Land Mine Damage	0
    
    -   Chain Lightning Damage	24.00Q
    
    -   Death Wave Damage	10.62T
    
    -   Swamp Damage	0
    
    -   Black Hole Damage	1.56Q
    
    -   Electrons Damage	0
    
    Note that 'Land Mine Damage' and 'Inner Land Mine Damage' are separate metrics, Land Mine is a defense workshop, ILM is a UW. 

10. DONE % of total damage by source as stacked bar per battle report

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:19]</span></span>

11. DONE Damage vs Destroyed By stacked bar

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:19]</span></span>

12. DONE Orb Effectiveness

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:19]</span></span>
    
    Composite view:
    
    -   Orb Damage
    
    -   Enemies Hit by Orbs
    
    -   Enemies Destroyed by Orbs

13. DONE Add Coins from UWs Charts/Metrics

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:19]</span></span>
    
    Add a donut chart tracking the following from Battle Reports Utility section. 
    
    -   Coins From Death Wave	165.52K
    
    -   Coins From Golden Tower	4.61M
    
    -   Coins From Black Hole	0
    
    -   Coins From Spotlight	94.30K

14. DONE Add 'Enemies Destroyed' Donut to Charts/Metrics

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:19]</span></span>
    
    Add the following from Battle Report Enemies Destroyed
    
    -   Basic	150877
    -   Fast	46543
    -   Tank	56081
    -   Ranged	38140
    -   Boss	349
    -   Protector	0
    -   Vampires	116
    -   Rays	133
    -   Scatters	125
    -   Saboteur	0
    -   Commander	0
    -   Overcharge	0
    
    There is an asymmetry found in the game's reported 'total enemies' and 'total elites' that doesn't align with the summed totals of reported enemy types. Therefore we will ignore those metrics and roll our own to avoid misleading charts. This should be clearly stated in the docs. 

15. DONE Cash Charts

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:19]</span></span>
    
    Economy → Cash (Definition)
    
    Cash represents in-run purchasing power.
    It is not progression currency and does not persist across runs.
    
    Cash charts answer:
    
    “How much in-run buying power did this run generate, and from where?”
    
    -   Cash Earned (total, absolute)
    -   Interest Earned
    -   Cash From Golden Tower
    
    Optional (if already parsed):
    
    -   Any other explicit “Cash From X” fields the game exposes later

16. DONE Card Parameter description should replace placeholder unit with current level value     :enhancement:

    -   State "DONE"       from "IN PROGRESS" <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 12:32]</span></span>
    -   State "IN PROGRESS" from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 18:59] </span></span>   
        Some work done but not complete
    
    Instead of showing 'for [x] sec' or 'by #%' the description should reflect the current card level values
    
    For example:
    
    -   **Critical Coin "Increase critical chance by +#%":** Should read "Increase critical chance by +\*\*27\*\*%" for level 5
    -   **Damage "Increase tower damage by x #":** Should read "Increase tower damage by ****4.00**** #" for level 7/maxed
    
    Card descriptions must be rendered from structured parameter data, not static strings.
    
    Any card description containing placeholder tokens ([x], #, %, sec) must be replaced at render-time with the effective value for the card’s current level. If card level is 0 placeholder is permitted.
    
    The displayed value must be computed using:
    
    -   base value
    -   per-level scaling
    -   current card level
    -   max-level cap (if applicable)
    
    No placeholder text may remain once the computation succeeds.
    
    Completion criteria:
    
    -   No unresolved placeholders remain anywhere in the Cards Dashboard
    
    -   All cards render level-correct values consistently
    
    -   Failure to meet any criterion means the task is incomplete
    
    -   Prompt38Validation.yml accurately marked complete

17. DONE Pr 1-3 Tweaks

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:18]</span></span>
    -   [X] Need to inject Start and End Dates in Context Fields for Charts to display properly on page load
    -   [X] Add an 'All' button next to Previous/Last (Range is from first Battle Report to Present)
    -   [X] 'More options' shouldn't be muted
    -   [X] Previous and Next should show below date range fields
        The Context Form needs to be arranged like this:
        Context
        <start> <end> <granularity> <tier> <preset>
        <previous> <next> <all>
        <chart builder> <apply> <clear>
    
    Charts: default to Event window and add Event navigation, add per-run granularity toggle, add stacked/bar variants for damage breakdowns

18. DONE In the UW Sync Graph exclude Death Wave from Cumulative Overlap calculation

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:28]</span></span>
    
    Since we don't have a duration for Death Wave, the overlap shows a very small percentage. 

19. DONE In the UW Sync Graph don't show the UWs/Bots at 0

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 13:28]</span></span>
    
    They don't fire until the first cooldown when a run starts. 

20. DONE Create a new Goals Dashboard

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 15:58]</span></span>
    
    Create a new dashboard and widgets for players to specify a target upgrade level and calculate the total currancy needed.
    
    A player will select a parameter from UWs/Bots/Guardian Chips and the level they want to target.
    
    The new dashboard will show all tracked parameters. A small widget will show the relevant metrics on the respective dashboards.
    
    The dashboard and widgets will label the currency (stones, bits, medals)
    
    -   We don't need a status column, we do need behavior for when a goal is reached. The goal should be hidden from the table. We can add a toggle to 'show completed'
    -   Make targets validate against max level from Bot parameter levels / Guardian chip parameter levels / Ultimate weapon parameter levels (clamp or show a clear error).
    -   Store both target<sub>level</sub> and an optional notes/label per goal (lets players group goals like “Next milestone” without affecting analysis). -I like it!
    -   Persist an explicit assumed<sub>current</sub><sub>level</sub> flag/value when current is missing (so totals are traceable even if player data changes later).
    -   Add a “last recalculated” timestamp and show which cost-table revision/source is used (ties nicely to your “source wikidata” keying). -I don't think we need it, but build it out clean and compartmentalized so it's easy to remove.
    -   Provide quick actions: “Set target = max”, “+1 level”, “Clear goal”. -We don't need " +1 level" (that's already shown on the dashboards.
    -   Widget UX: show top 3 by remaining cost + “View all goals” link (make sure the link uses the safe-redirect helper if any next param is involved).
    -   Testing: add golden tests for totals using real rows from the parameter-level tables (catches cost table changes immediately).
    
    1.  Refinements:
    
        -   [X] New goals need to  be created via a modal. Only show active goals on the Goals Dashboard.
        -   [X] Get rid of optional label field
        -   [X] Target needs to be a dropdown populated with the level number, delta, and cost
        -   [X] On UWs/Bots/Guardian Chips Dashboard the Goals pane needs to be hidden if there is not active goals.
        -   [X] In the Add Goal Modal, fix the rows showing no delta (see screenshot)
        -   [X] In the Add Goal Modal, the target delta needs to show the increase from current level. Not just +2 for each.

21. DONE Add mkdocstrings pages for Analytics/, Core/Charting/, Core/Parsers/

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 18:58]</span></span>
    
    Add to mkdocs.yml under 'Reference' 

22. DONE Update Readme.md, changelog to v0.3.0

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 18:59]</span></span>
    
    Summarize last few commits. Call out Cards and Charts Enhancements, Goals Dashboard, and Docs additions. You can run \`git log -16\` to review progress
    
    Our current changelog is at 0.2.2 (in progress) and published releases on Github are 0.2.1. I think we can safely say we can tag our work as 0.3.0, would you agree? 

23. DONE On Railway run rebuild<sub>wiki</sub><sub>definitions</sub> &#x2013;target cards after deploying v0.3.0

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-25 Thu 19:26]</span></span>

24. TODO On Cards Dashboard Add a Total Cards Progress Widget under preset tags

    <table border="2" cellspacing="0" cellpadding="6" rules="groups" frame="hsides">
    
    
    <colgroup>
    <col  class="org-left" />
    
    <col  class="org-left" />
    
    <col  class="org-left" />
    
    <col  class="org-left" />
    </colgroup>
    <tbody>
    <tr>
    <td class="org-left">Cards Remaining:</td>
    <td class="org-left">{#}</td>
    <td class="org-left">Total Cards:</td>
    <td class="org-left">{#}</td>
    </tr>
    
    
    <tr>
    <td class="org-left">Maxed Cards</td>
    <td class="org-left">{#}</td>
    <td class="org-left">Progress:</td>
    <td class="org-left">{%}</td>
    </tr>
    
    
    <tr>
    <td class="org-left">Gems Needed</td>
    <td class="org-left">{#}</td>
    <td class="org-left">Events:</td>
    <td class="org-left">{#}</td>
    </tr>
    </tbody>
    </table>
    
    {#} represents calculated values based on app data
    {%} represents precentage calculations
    
    Currently there are 31 Cards and you need to collect 80 copies to max level 7, so Total Cards will equal 2480. Cards Remaining will be calculated by Total Cards minus Card Copies collected.
    
    Maxed Cards will be a count of how many cards are 32/32 Collected
    
    Progress will be calculated by Total Cards minus Cards Remaing divided by Total Cards
    
    Gems Needed will be calculated by Cards Remaining divided by 10 (round up) times 200. Cards are typically purchased 10 at a time for 200 gems.
    
    Events will be calculated by Gems Needed divided by 1600. There is a standard Event Mission to buy 80 Cards, so 200 gems times 8 gives us 1600.

25. TODO On Battle History Dashboard

    Add a Highest Wave table under Filters.
    
    Shows Each Tier with a run logged and the highest wave reached. Below that show the top 3 Tournament Logs.
    
    Note: Currently Tier 21 is the Highest possible. But to avoid clutter we'll base the table on Tiers logged in this app. 


<a id="org023e374"></a>

## Backlog <code>[2/5]</code>

“Out of Scope”:

-   Cloud sync
-   Real-time scraping


<a id="org5fb4eea"></a>

### TODO Exploratory Pattern Analysis (v0.X.0)     :kMeans:enhancement:

Guiding Principles:

-   K-means is not an optimization engine and not advice logic.

It’s a lens.

-   Players should never feel measured against others — only contextualized by them.

-   Its role is to answer:
    
    > “What kinds of runs exist in the data, without us naming them first?”

-   Run Archetypes (descriptive only)
    
    Clusters emerge like:
    
    -   Short / high-yield
    
    -   Long / low-risk
    
    -   Volatile / high-variance

These are labels applied after clustering, not baked into the model.

1.  Better context for advice (without commands)

Instead of:

“You should invest more in X”

You get:

“Runs similar to this one often emphasize X over Y.”

That’s a huge philosophical win for your system.

1.  A future bridge to personalization

Later still, this becomes:

-   “You tend to play in Cluster C”

-   “This run deviated from your usual cluster”

Still observational. Still safe.

To future-proof it now, I’d lock these in:

-   Clustering operates on MetricSeries snapshots only

-   Never used as an input to simulations or projections

-   Never produces imperative language

-   Fully explainable feature vector per cluster

-   Can be turned off entirely with no loss of functionality

In other words: insight, not dependency.

Responsible ways to do global exploratory analytics

1.  Aggregation first, always

No raw runs, no individual trajectories.

Safe:

-   Cluster centroids

-   Distribution ranges

-   Percentile bands

Never:

-   “Players like X”

-   Sample runs you can inspect

-   Cluster sizes that reveal minority behaviors

-   Opt-in visibility, not opt-out

This is key.

-   Players participate in aggregation by default (that’s normal analytics)

-   Viewing global patterns is opt-in

-   UI copy explains what isn’t shown as clearly as what is

Example:

> “These patterns summarize thousands of runs. Individual players and runs are never visible.”

1.  Language rules (this is huge)

You already care about this, so lean into it.

Allowed:

-   “Common patterns”

-   “Observed tendencies”

-   “Frequently co-occurring choices”

Banned:

-   “Best”, “optimal”, “top players”

-   “Most successful builds”

-   “What winning players do”

This prevents status pressure from forming.

1.  Self-relative framing by default

Global data should always be anchored back to the player, not shown raw.

Instead of:

> “Cluster B averages 2.3M coins/hr”

Show:

> “Your run falls near the center of a common cluster that emphasizes coin efficiency over wave depth.”

The global context exists only to explain their data.

1.  Minimum population thresholds

A classic but necessary guardrail.

-   No global insight is shown unless N ≥ some threshold

-   Prevents early users from being “the dataset”

-   Prevents deanonymization through edge cases

You can even surface this transparently:

“Global patterns unlock after enough data is available.”

If done right, global clustering becomes:

-   A mirror, not a scoreboard

-   Educational, not prescriptive

-   Optional, not normative

That’s rare in game-adjacent tools — and a real differentiator.

If clustering ever looks like:

-   leaderboard-adjacent

-   ranking-adjacent

-   “top cluster”

-   “advanced players tend to…”

****You’ve violated your core difference.****

K-means belongs entirely inside of analysis

-   It explains patterns in metrics

-   It never evaluates players

-   It never assigns value

-   It never implies success


<a id="orgeb993a9"></a>

### TODO Hide Deathwave on UW Sync Chart

Add an optional toggle to show/hide the Death Wave activation markers (so the schedule focuses on GT/BH overlap), while still keeping everything descriptive.


<a id="orgd3026b1"></a>

### TODO Required Doc Type Header (Must Prepend to All Docs)

Every document authored or modified by Codex must begin with exactly one of the following headers, placed at the very top of the file.

    User Guide Document
    <!--
    DOC TYPE: User Guide
    AUDIENCE: Players / Non-technical users
    PURPOSE: Explain how to use the feature, not how it is built
    TONE: Professional, concise, non-technical
    -->
    
    Developer / Progress Document
    <!--
    DOC TYPE: Developer Documentation
    AUDIENCE: Contributors / Maintainers
    PURPOSE: Explain internal behavior, architecture, or project status
    TONE: Technical, precise, implementation-aware
    -->

****Enforcement Rules****

-   Exactly one Doc Type Header is allowed per document
-   The header must appear before any headings or content
-   The selected doc type determines:
    -   Tone
    -   Structure
    -   Allowed level of technical detail
-   If the document content conflicts with the declared Doc Type, the document is considered invalid and must be rewritten

****Default Behavior****

If Codex is unsure which header to use:

-   Default to User Guide
-   Exclude internal details
-   Favor task-based explanations

1.  Checklist

    Doc Type Validation
    
    -   [ ] A Doc Type Header is present at the very top of the document
    -   [ ] Exactly one Doc Type Header is used
    -   [ ] The content matches the declared Doc Type
    
    User Guide Documents (if applicable)
    
    -   [ ] Written for non-technical users
    -   [ ] No internal model, class, or file names mentioned
    -   [ ] No code blocks or CLI instructions
    -   [ ] Uses clear, action-oriented language
    -   [ ] Explains how to use the feature, not how it works internally
    
    Structure & Readability
    
    -   [ ] Uses consistent hierarchical headings (H1 → H4 only)
    -   [ ] Headings alone form a usable Table of Contents
    -   [ ] Follows task flow where applicable:
        -   Overview
        -   When to Use This
        -   How to Use
        -   How to Read the Results
        -   Notes & Limitations
    -   [ ] Steps are short and limited to one action each
    
    Tone & Formatting
    
    -   [ ] Professional and concise
    -   [ ] No slang or casual phrasing
    -   [ ] Notes and cautions are clearly called out using blockquotes
    -   [ ] Avoids unnecessary technical detail
    
    Final Sanity Check
    
    -   [ ] A new user could follow this document without external explanation
    -   [ ] The document reads as instructions, not a design or implementation spec

2.  Reminder Prompt

    Before writing any documentation, select and prepend the appropriate Doc Type Header.
    Follow the documentation standards defined in agents.md.
    If writing a User Guide, prioritize clarity for non-technical users, avoid internal details, and follow the required task-based structure.
    Validate the final document against the Documentation Self-Check Checklist before completing the task.


<a id="orgfdf7785"></a>

### CANCELED Wmhat-If Scenarios

-   State "CANCELED"   from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-22 Mon 09:01] </span></span>   
    don't want to implement it

This is where simulations might enter — but cautiously.

Examples:

“If Golden Tower cooldown were reduced by 1 level…”

“Projected coin gain range if X upgraded next”

Still deterministic:

Based on historical deltas

No RNG modeling

No balance speculation


<a id="orgeaf26f0"></a>

### CANCELED Ranked Recommendations

-   State "CANCELED"   from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-21 Sun 18:19] </span></span>   
    Wrong paradigm for this app

Only now do you allow:

“Top 3 upgrades for your goal”

“Best next unlock based on your data”

Guardrails:

Always link back to:

Charts

Comparisons

Assumptions

Always show:

Why

Based on how much data

What would change the recommendation

This keeps it defensible.


<a id="org11f7507"></a>

### Complete

1.  DONE Review Docs and Note Revisions     :Max:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-19 Fri 17:24]</span></span>

2.  DONE Phase 5 Summary was written as a user facing doc     :docs:

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-18 Thu 19:33]</span></span>
    
    Should be written as Developer / Progress Documentation. And appropriately filed under 'Development

3.  DONE Fix pytest warnings

    CLOSED: <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 11:01]</span></span>
    
    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 11:01]</span></span>
    
    definitions/models.py:279
      /Users/mrmax/projects/theTowerStats/definitions/models.py:279: RemovedInDjango60Warning: CheckConstraint.check is deprecated in favor of \`.condition\`.
        models.CheckConstraint(
    
    definitions/models.py:343
      /Users/mrmax/projects/theTowerStats/definitions/models.py:343: RemovedInDjango60Warning: CheckConstraint.check is deprecated in favor of \`.condition\`.
        models.CheckConstraint(
    
    definitions/models.py:407
      /Users/mrmax/projects/theTowerStats/definitions/models.py:407: RemovedInDjango60Warning: CheckConstraint.check is deprecated in favor of \`.condition\`.
        models.CheckConstraint(
    
    &#x2013; Docs: <https://docs.pytest.org/en/stable/how-to/capture-warnings.html>

4.  DONE Linking Presets/UW/Guardian Chips/Bots to battle history

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:31]</span></span>
    
    Mostly a visual tweak, but adds context and history for the player to interpert their performance history. 


<a id="orgce29b85"></a>

## Codex Tasks

-   [X] prompt 16
-   [X] prompt 17
-   [X] prompt 18
-   [X] prompt 19 cards improvements
-   [X] prompt 20 Battle History ↔ Preset Tagging
-   [X] prompt 21 UW Dashboard
-   [X] prompt 22 Bots/Guardian Chips Dashboards
-   [X] prompt 24 Cards Dashboard Enhancements
-   [X] prompt 23 phase 5 exit criteria validation
-   [X] prompt 25 phase 6 work
-   [X] prompt 26 Phase 6 Addendum: Base vs Effective Value + Modifier Explanations
-   [X] prompt 27 Phase 6 Validation Checklist
-   [X] prompt 28 Phase 7 Power Tools
-   [X] prompt 28 Validation Checklist
-   [X] prompt 29 Phase 8, Pillar 1: Multiple Player Support
-   [X] prompt 29 Multiple Player Support Checklist
-   [X] prompt 30 Phase 8, Pillar 2: Trustable, Explainable, Goal-Aware Advice
-   [X] prompt 30 Trustable, Explainable, Goal-Aware Advice Validation
-   [X] prompt 31 Phase 8, Pillar 3: Demo, Export, and Adoption Features
-   [X] port<sub>and</sub><sub>adoption</sub> checklist
-   [X] prompt 32 Phase 9A Cleanup, Trust, and Documentation (Non-Deployment)
-   [X] prompt 32 Validation
-   [X] prompt 33 Deployment Prep
-   [X] prompt 33 Validation
-   [X] prompt 34 Stabilize, standardize, and clarify
-   [X] Phase 10 Validation
-   [X] prompt 35 phase 10b
-   [X] prompt 36 phase 11 bug fixes
-   [X] promt 37 Charts Enhancements
-   [X] prompt 37 validation
-   [X] prompt38Validation.md

-   [ ] version1.0.md

