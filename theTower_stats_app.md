
# Table of Contents

1.  [Stats Tracking App for The Tower Mobile Game](#orgdabb504)
    1.  [Goals/Intent](#org751ff97)
    2.  [Requirements](#orgb23b868)
    3.  [Overall Architecture](#orge060c8a)
    4.  [Features](#org0ec6289)
    5.  [Core Responsibilities](#orga64bd67)
        1.  [Rate Calculations](#orgdce9127)
        2.  [Delta Calculations](#orgee3c54b)
        3.  [Parameterized Effects](#org7314c75)
        4.  [Aggregations by Intent (Presets)](#orgbecbe46)
        5.  [Analysis Engine Invocation](#org0d35924)
        6.  [Output Shape](#orgcec8bc5)
        7.  [Module Structure (Suggested)](#org90f5a7d)
    6.  [UX Design](#org8a33764)
    7.  [Example Stat Data](#org2f25183)
    8.  [Models](#orgf44aa81)
        1.  [Game Data](#org386c69d)
        2.  [BotsParameters](#org0ef3c45)
        3.  [CardDefinition](#org916cf80)
        4.  [CardLevel / Star](#org7d02217)
        5.  [CardParameters](#org6b568e8)
        6.  [CardSlots](#org7e5fbe2)
        7.  [GuardianChipParemeters](#org0240145)
        8.  [PlayerBot](#orgfd2b5c2)
        9.  [PlayerCard](#org9e73768)
        10. [PlayerGuardianChip](#org437af44)
        11. [PlayerUltimateWeapon](#org913763d)
        12. [PresetTags](#org2826aa7)
        13. [UltimateWeaponParameters](#org95c1d04)
        14. [Unit Model](#orge37e5cc)
        15. [WikiData](#org0d3c319)
    9.  [Views](#org7837408)
        1.  [Battle History](#org7f4a791)
        2.  [Cards](#org09b9a85)
        3.  [Charts](#org5ef0f35)
        4.  [UW Progress](#org6a43b1a)
        5.  [Guardian Progress](#orgf87d161)
        6.  [Bots Progress](#org54d2847)
    10. [Management Commands](#org70e5124)
        1.  [fetch<sub>wiki</sub><sub>data</sub>](#org7c43f9f)
        2.  [add<sub>battle</sub><sub>report</sub>](#orge537000)
    11. [Repo Structure](#orge93d5e2)
    12. [Testing Standards](#org9623602)
    13. [Sprint Roadmap](#orgf4da2c1)
        1.  [Phase 1 Foundations](#orgbfbc3f2)
        2.  [Phase 2 Context](#org488dd1c)
        3.  [Phase 3 — App Structure & UX](#org326e91b)
        4.  [Phase 4 Effects](#org98d03a2)
        5.  [Phase 5 Dashboard UX <code>[100%]</code>](#org5a585c5)
        6.  [Phase 6 Expansion of Foundation and Context <code>[11%]</code>](#org312ce8f)
        7.  [Phase 7 Power Tools](#orgb6cd393)
        8.  [Phase 8 Multiple Player Support](#orgb61ce1e)
    14. [Backlog <code>[0/2]</code>](#org8dafee2)
        1.  [Normalize time handling everywhere (game time vs real time vs accelerated)](#org03ab18d)
        2.  [Required Doc Type Header (Must Prepend to All Docs)](#org76986de)
        3.  [Complete](#org85e17e9)
    15. [Codex Tasks](#org1a507f6)


<a id="orgdabb504"></a>

# Stats Tracking App for The Tower Mobile Game


<a id="org751ff97"></a>

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


<a id="orgb23b868"></a>

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


<a id="orge060c8a"></a>

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


<a id="org0ec6289"></a>

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


<a id="orga64bd67"></a>

## Core Responsibilities


<a id="orgdce9127"></a>

### Rate Calculations

-   Derived per run and over time:
-   Coins / hour
-   Coins / wave
-   Damage / wave
-   Waves / real minute
-   Resource gains per hour (cells, shards, etc.)

These back Phase 1 charts directly.


<a id="orgee3c54b"></a>

### Delta Calculations

Between two runs or windows:

-   Absolute delta
-   Percentage delta
-   Rolling averages

Examples:

-   Coins/hour before vs after unlocking a slot
-   Damage output change after a UW unlock

No interpretation — just math.


<a id="org7314c75"></a>

### Parameterized Effects

Using wiki-derived tables:

-   Effective cooldown at star level
-   % reduction or multiplier applied
-   EV calculations (e.g. wave skip)

These are:

-   Deterministic
-   Re-computable across revisions
-   Fully testable with golden tests


<a id="orgbecbe46"></a>

### Aggregations by Intent (Presets)

-   Presets act as labels, not logic.
-   Only One Preset can be active at a time
-   The engine supports:
    -   “Aggregate metrics for runs where preset X was active”
    -   “Compare metrics across presets”

It does not decide which preset is better.


<a id="org0d35924"></a>

### Analysis Engine Invocation

-   Stateless
-   Accepts:
    -   Query params (date range, tier, context)
    -   Returns DTOs only
    -   No DB writes


<a id="orgcec8bc5"></a>

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


<a id="org90f5a7d"></a>

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


<a id="org8a33764"></a>

## UX Design

-   Dark Mode Default
-   Top Dynamic Nav
    -   Docs / Admin links to the right
    -   Global Search Box
-   Maxed Out/Completed Upgrades are highlighted with a Gold Box outline


<a id="org2f25183"></a>

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


<a id="orgf44aa81"></a>

## Models


<a id="org386c69d"></a>

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


<a id="org0ef3c45"></a>

### BotsParameters

Wiki-derived, FK to PlayerBots
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.


<a id="org916cf80"></a>

### CardDefinition

Properties:

-   **Name :** string
-   **rarity:** string
-   base<sub>effect</sub>
-   max<sub>effect</sub>
-   preset<sub>tags</sub> (FK)


<a id="org7d02217"></a>

### CardLevel / Star

-   card (FK)
-   **stars:** integer
-   **value:** value of current effect (between base and max)


<a id="org6b568e8"></a>

### CardParameters

Wiki-derived, FK to PlayerCard
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.


<a id="org7e5fbe2"></a>

### CardSlots

tracker for Card Slots unlocked, maximum of 21
Modified via Admin

Properties:

-   Slot Number (label)
-   Cost integer (Gems)


<a id="org0240145"></a>

### GuardianChipParemeters

Wiki-derived, FK to PlayerGuardianChip
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.


<a id="orgfd2b5c2"></a>

### PlayerBot

Properties:

-   **bot:** FK to BotParameters
-   **unlocked:** checkbox


<a id="org9e73768"></a>

### PlayerCard

Properties:

-   card<sub>definition</sub> (FK)
-   **unlocked:** checkbox
-   **Stars:** integer 1-7
-   **Cards:** integer progress toward next level. 0, 3, 5, 8, 12, 20, 32


<a id="org437af44"></a>

### PlayerGuardianChip

Properties:

-   **chip:** FK to GuardianChipParameters
-   **unlocked:** checkbox


<a id="org913763d"></a>

### PlayerUltimateWeapon

Properties:

-   **UW:** FK to UtimateWeaponParameters
-   **unlocked:** checkbox


<a id="org2826aa7"></a>

### PresetTags

-   **Name:** string
-   Cards (FK)
-   **limit:** FK with Card Slots


<a id="org95c1d04"></a>

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


<a id="orge37e5cc"></a>

### Unit Model

Percent and 'x' multipliers use semantic wrapper (Multiplier(1.15))

Properties:

-   **raw<sub>value</sub>:** string
-   **normalized<sub>value</sub>:** decimal
-   **magnitude:** (k,10<sup>3</sup>),  (m, 10<sup>6</sup>), (b, 10<sup>9</sup>), (t, 10<sup>12</sup>), etc.
-   **unit<sub>type</sub>:** coins, damage, count, time


<a id="org0d3c319"></a>

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


<a id="org7837408"></a>

## Views


<a id="org7f4a791"></a>

### Battle History

View previously entered stats 


<a id="org09b9a85"></a>

### Cards

Combine 'Cards,' 'CardLevel' and 'CardSlots'


<a id="org5ef0f35"></a>

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


<a id="org6a43b1a"></a>

### UW Progress

-   Button to add new UW


<a id="orgf87d161"></a>

### Guardian Progress

-   Button to add new chip
-   checkbox to flag equiped


<a id="org54d2847"></a>

### Bots Progress

-   button to add new bot


<a id="org70e5124"></a>

## Management Commands


<a id="org7c43f9f"></a>

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


<a id="orge537000"></a>

### add<sub>battle</sub><sub>report</sub>

Ingest and parse battle report data from the player. This is a large blob of data shown to the player at the end of each round of the game. They will paste it into this app as plain text.

Parser should gracefully alert the player to new labels that may appear after a game update.


<a id="orge93d5e2"></a>

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


<a id="org9623602"></a>

## Testing Standards

-   Parser golden files (real pasted runs)
-   Every parser or calculation gets at least one golden test
-   Wiki scraper fixture snapshots
-   Math correctness tests (especially EV)
-   When completing code, start building/executing tests as specific as possible to the code you changed so that you can catch issues efficiently, then make your way to broader tests as you build confidence.


<a id="orgf4da2c1"></a>

## Sprint Roadmap

Each phase must be demoable without admin intervention.


<a id="orgbfbc3f2"></a>

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


<a id="org488dd1c"></a>

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


<a id="org326e91b"></a>

### DONE Phase 3 — App Structure & UX

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 09:22]</span></span>

1.  Milestones <code>[100%]</code>

    -   [X] Navigation
    -   [X] Page separation
    -   [X] Dashboards
    -   [X] Model completeness (structure, not logic)


<a id="org98d03a2"></a>

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


<a id="org5a585c5"></a>

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

10. Exit Criteria <code>[91%]</code>

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
    
    -   [ ] No new models added
    -   [X] No migrations required
    -   [X] Test suite passes unchanged
    
    \### Demo Test
    A new user can:
    
    1.  Import runs
    2.  View history
    3.  Inspect progress
    4.  Understand trends …without explanation.


<a id="org312ce8f"></a>

### Phase 6 Expansion of Foundation and Context <code>[11%]</code>

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

-   [ ] Add 2–3 more canonical rate metrics. Both of these would be best displayed as a donut chart. 
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

-   [ ] Lock down Unit Model correctness
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


<a id="orgb6cd393"></a>

### Phase 7 Power Tools

1.  TODO Add Chart Builder Modal to Charts Dashboard

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

2.  TODO Data Quality & Confidence Signals

    Players will ask:
    
    -   “Is this run weird?”
    -   “Did something change here?”
    
    Add:
    
    -   Run flags (outlier, partial, anomalous)
    -   Visual markers on charts
    -   Simple heuristics, not ML
    
    This builds trust without over-engineering.

3.  TODO Add a 'Killed By' Donut Chart

4.  TODO UW Sync Graph

    There is synergy to using some UW together, specifically Golden Tower, Blackhole and Death Wave. It's common in the meta to keep the cooldowns and durations in sync. We should have the data to chart the three together and how often they overlap/synchronize

5.  TODO Performance Guardrails

    As data grows:
    
    -   Cached derived results per view
    -   Explicit limits on chart density
    -   Warnings when comparisons get statistically thin
    
    Do this before you have 30 guild members loading it daily.

6.  TODO UX Pass

    1.  Battle History
    
        -   [ ] Sort by 'Killed By' isn't sorting properly. It should filter alphabetically
        -   [ ] Add a tip that the input can only accept 1 battle report at a time. You can add validation that makes sure 'Battle Report' and 'Battle Date' appear exactly once.
    
    2.  Charts
    
        Functionality has expanded quite a bit and usability hasn't kept up.
        
        -   [ ] Move Filters to the right column. The wider area will make the controls easier to work with.

7.  TODO Add Advice for Optimization

    Based on logged performance data, it could be possible to calculate and offer suggestions based on the data.
    
    For Example:
    
    -   Which UW to unlock next
    -   Bot properties to improve
    -   Guardian Chip properties to improve
    -   Weighted Preset Rankings


<a id="orgb61ce1e"></a>

### Phase 8 Multiple Player Support

1.  TODO Wireup Github Actions to Run Tests

    Run checks or Ruff Check, mypy ., pytest -q

2.  TODO Allow Multiple Players to Store Data

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

3.  TODO Default User

    Take some of my data and make plausible changes to store as the Default User. Allow any player to also view the default user data. 

4.  TODO Update readme.md

    -   Make sure it's still aligned with App Behavior and Features
    -   Project Status reflects docs/ revisions

5.  TODO Export / Share (Lightweight)

    -   CSV export of derived metrics
    -   PNG export of charts
    
    This dramatically increases perceived value with very little backend work.


<a id="org8dafee2"></a>

## Backlog <code>[0/2]</code>

“Out of Scope”:

-   Cloud sync
-   Real-time scraping


<a id="org03ab18d"></a>

### TODO Normalize time handling everywhere (game time vs real time vs accelerated)

Game Time can be accelerated and the rate can be changed during a run. Either via Lab Research (max of 5x) or via perks that increase it further to a variable factor (increased by additional researchs). The hard maximum is 6.25x (according to the Wiki). However the Wiki also notes "Game speed is not accurate. x5.0 speed behaves closer to x4.0 while 6.25 is closer to x5." So our handling of it is not strictly necessary. 


<a id="org76986de"></a>

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


<a id="org85e17e9"></a>

### Complete

1.  DONE Fix pytest warnings

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

2.  DONE Linking Presets/UW/Guardian Chips/Bots to battle history

    -   State "DONE"       from "TODO"       <span class="timestamp-wrapper"><span class="timestamp">[2025-12-17 Wed 14:31]</span></span>
    
    Mostly a visual tweak, but adds context and history for the player to interpert their performance history. 


<a id="org1a507f6"></a>

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
-   [ ] prompt 27

