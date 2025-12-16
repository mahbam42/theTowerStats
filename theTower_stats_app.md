
# Table of Contents

1.  [Stats Tracking App for The Tower Mobile Game](#org804ad94)
    1.  [Goals/Intent](#org996e0af)
    2.  [Requirements](#org4520e14)
    3.  [Overall Architecture](#org2f6417b)
    4.  [Features](#orgfebd5bf)
    5.  [Core Responsibilities](#org622c658)
        1.  [Rate Calculations](#orgeed08ce)
        2.  [Delta Calculations](#orgd783592)
        3.  [Parameterized Effects](#orga26ce0a)
        4.  [Aggregations by Intent (Presets)](#org788b252)
        5.  [Analysis Engine Invocation](#org50aacd6)
        6.  [Output Shape](#orgc900de2)
        7.  [Module Structure (Suggested)](#org7d3f478)
    6.  [UX Design](#org6d928d2)
    7.  [Example Stat Data](#org3c370b1)
    8.  [Models](#org06ba1a1)
        1.  [Game Data](#orgdfdf06f)
        2.  [BotsParameters](#org91e6a67)
        3.  [CardDefinition](#org22cf80c)
        4.  [CardLevel / Star](#org3219aaf)
        5.  [CardParameters](#org31a7c16)
        6.  [CardSlots](#org32afb25)
        7.  [GuardianChipParemeters](#org84cc24a)
        8.  [PlayerBot](#org8e15d7d)
        9.  [PlayerCard](#org5b29b7c)
        10. [PlayerGuardianChip](#org276f451)
        11. [PlayerUltimateWeapon](#org6de010f)
        12. [PresetTags](#orgccdf9d6)
        13. [UltimateWeaponParameters](#org6dd4549)
        14. [Unit Model](#org7449f61)
        15. [WikiData](#orgd97cffe)
    9.  [Views](#org483833e)
        1.  [Battle History](#org6ea307d)
        2.  [Cards](#org382c58c)
        3.  [Charts](#org2f7480f)
        4.  [UW Progress](#orgd05815b)
        5.  [Guardian Progress](#org42bc551)
        6.  [Bots Progress](#orga9a69cf)
    10. [Management Commands](#org8ab538d)
        1.  [fetch<sub>wiki</sub><sub>data</sub>](#orga80896c)
        2.  [add<sub>battle</sub><sub>report</sub>](#org6c46467)
    11. [Repo Structure](#org1466e50)
    12. [Testing Standards](#orgf074ee5)
    13. [Sprint Roadmap](#org35e7827)
        1.  [Phase 1 Foundations](#org1d50c23)
        2.  [Phase 2 Context](#orga287895)
        3.  [Phase 3 — App Structure & UX](#orge550075)
        4.  [Phase 4 Effects](#orgf981f58)
        5.  [Phase 5 Dashboard UX <code>[0%]</code>](#org3b0d7ea)
    14. [Backlog <code>[0/5]</code>](#org06339de)
        1.  [Allow Multiple Players to Store](#org88f5053)
        2.  [Add Chart Builder Modal to Charts Dashboard](#orgdbcb6b2)
        3.  [Add Advice for Optimization](#org4117ed3)
        4.  [Linking Presets/UW/Guardian Chips/Bots to battle history](#orgb31181b)
        5.  [Complete](#org69078aa)


<a id="org804ad94"></a>

# Stats Tracking App for The Tower Mobile Game


<a id="org996e0af"></a>

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


<a id="org4520e14"></a>

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


<a id="org2f6417b"></a>

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


<a id="orgfebd5bf"></a>

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


<a id="org622c658"></a>

## Core Responsibilities


<a id="orgeed08ce"></a>

### Rate Calculations

-   Derived per run and over time:
-   Coins / hour
-   Coins / wave
-   Damage / wave
-   Waves / real minute
-   Resource gains per hour (cells, shards, etc.)

These back Phase 1 charts directly.


<a id="orgd783592"></a>

### Delta Calculations

Between two runs or windows:

-   Absolute delta
-   Percentage delta
-   Rolling averages

Examples:

-   Coins/hour before vs after unlocking a slot
-   Damage output change after a UW unlock

No interpretation — just math.


<a id="orga26ce0a"></a>

### Parameterized Effects

Using wiki-derived tables:

-   Effective cooldown at star level
-   % reduction or multiplier applied
-   EV calculations (e.g. wave skip)

These are:

-   Deterministic
-   Re-computable across revisions
-   Fully testable with golden tests


<a id="org788b252"></a>

### Aggregations by Intent (Presets)

-   Presets act as labels, not logic.
-   Only One Preset can be active at a time
-   The engine supports:
    -   “Aggregate metrics for runs where preset X was active”
    -   “Compare metrics across presets”

It does not decide which preset is better.


<a id="org50aacd6"></a>

### Analysis Engine Invocation

-   Stateless
-   Accepts:
    -   Query params (date range, tier, context)
    -   Returns DTOs only
    -   No DB writes


<a id="orgc900de2"></a>

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


<a id="org7d3f478"></a>

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


<a id="org6d928d2"></a>

## UX Design

-   Dark Mode Default
-   Top Dynamic Nav
    -   Docs / Admin links to the right
    -   Global Search Box
-   Maxed Out/Completed Upgrades are highlighted with a Gold Box outline


<a id="org3c370b1"></a>

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


<a id="org06ba1a1"></a>

## Models


<a id="orgdfdf06f"></a>

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


<a id="org91e6a67"></a>

### BotsParameters

Wiki-derived, FK to PlayerBots
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.


<a id="org22cf80c"></a>

### CardDefinition

Properties:

-   **Name :** string
-   **rarity:** string
-   base<sub>effect</sub>
-   max<sub>effect</sub>
-   preset<sub>tags</sub> (FK)


<a id="org3219aaf"></a>

### CardLevel / Star

-   card (FK)
-   **stars:** integer
-   **value:** value of current effect (between base and max)


<a id="org31a7c16"></a>

### CardParameters

Wiki-derived, FK to PlayerCard
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.


<a id="org32afb25"></a>

### CardSlots

tracker for Card Slots unlocked, maximum of 21
Modified via Admin

Properties:

-   Slot Number (label)
-   Cost integer (Gems)


<a id="org84cc24a"></a>

### GuardianChipParemeters

Wiki-derived, FK to PlayerGuardianChip
Immutable per revision. When the wiki changes, insert a new row — don’t overwrite.


<a id="org8e15d7d"></a>

### PlayerBot

Properties:

-   **bot:** FK to BotParameters
-   **unlocked:** checkbox


<a id="org5b29b7c"></a>

### PlayerCard

Properties:

-   card<sub>definition</sub> (FK)
-   **unlocked:** checkbox
-   **Stars:** integer 1-7
-   **Cards:** integer progress toward next level. 0, 3, 5, 8, 12, 20, 32


<a id="org276f451"></a>

### PlayerGuardianChip

Properties:

-   **chip:** FK to GuardianChipParameters
-   **unlocked:** checkbox


<a id="org6de010f"></a>

### PlayerUltimateWeapon

Properties:

-   **UW:** FK to UtimateWeaponParameters
-   **unlocked:** checkbox


<a id="orgccdf9d6"></a>

### PresetTags

-   **Name:** string
-   Cards (FK)
-   **limit:** FK with Card Slots


<a id="org6dd4549"></a>

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


<a id="org7449f61"></a>

### Unit Model

Percent and 'x' multipliers use semantic wrapper (Multiplier(1.15))

Properties:

-   **raw<sub>value</sub>:** string
-   **normalized<sub>value</sub>:** decimal
-   **magnitude:** (k,10<sup>3</sup>),  (m, 10<sup>6</sup>), (b, 10<sup>9</sup>), (t, 10<sup>12</sup>), etc.
-   **unit<sub>type</sub>:** coins, damage, count, time


<a id="orgd97cffe"></a>

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


<a id="org483833e"></a>

## Views


<a id="org6ea307d"></a>

### Battle History

View previously entered stats 


<a id="org382c58c"></a>

### Cards

Combine 'Cards,' 'CardLevel' and 'CardSlots'


<a id="org2f7480f"></a>

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


<a id="orgd05815b"></a>

### UW Progress

-   Button to add new UW


<a id="org42bc551"></a>

### Guardian Progress

-   Button to add new chip
-   checkbox to flag equiped


<a id="orga9a69cf"></a>

### Bots Progress

-   button to add new bot


<a id="org8ab538d"></a>

## Management Commands


<a id="orga80896c"></a>

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


<a id="org6c46467"></a>

### add<sub>battle</sub><sub>report</sub>

Ingest and parse battle report data from the player. This is a large blob of data shown to the player at the end of each round of the game. They will paste it into this app as plain text.

Parser should gracefully alert the player to new labels that may appear after a game update.


<a id="org1466e50"></a>

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


<a id="orgf074ee5"></a>

## Testing Standards

-   Parser golden files (real pasted runs)
-   Every parser or calculation gets at least one golden test
-   Wiki scraper fixture snapshots
-   Math correctness tests (especially EV)
-   When completing code, start building/executing tests as specific as possible to the code you changed so that you can catch issues efficiently, then make your way to broader tests as you build confidence.


<a id="org35e7827"></a>

## Sprint Roadmap

Each phase must be demoable without admin intervention.


<a id="org1d50c23"></a>

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


<a id="orga287895"></a>

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


<a id="orge550075"></a>

### DONE Phase 3 — App Structure & UX

-   State "DONE"       from              <span class="timestamp-wrapper"><span class="timestamp">[2025-12-16 Tue 09:22]</span></span>

1.  Milestones <code>[100%]</code>

    -   [X] Navigation
    -   [X] Page separation
    -   [X] Dashboards
    -   [X] Model completeness (structure, not logic)


<a id="orgf981f58"></a>

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


<a id="org3b0d7ea"></a>

### Phase 5 Dashboard UX <code>[0%]</code>

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

1.  TODO Battle History

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

2.  TODO Charts

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

3.  TODO Cards

    -   Show a utility widget with 'CardSlots' Unlocked and a button to 'Unlock Next Slot'
    -   List all Cards in a Collapsible Table
        -   Multiselect to add/create preset
        -   textbox to enter current inventory
        -   Display 'CardLevel' and 'CardParameters'
        -   Filter by Preset

4.  TODO UW Progress

5.  TODO Guardian Chip Progress

    The naming is important 

6.  TODO Bots Progress

7.  TODO Add Github Action to publish Docs to Github Pages

8.  TODO Documentation and Polish

    -   Add Material Theme, mkdocstrings-python support
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
    -   Move Phase 1, Phase 2, Phase 2.75, Phase 3, and Phase 4 under 'Development'
    -   Merge 'Management Command' section for 'fetch<sub>wiki</sub><sub>data</sub>' with 'Wiki Population' page
    -   Add Docs for Each Dashboard
        -   Callout Charts and Cards in index.md

9.  TODO Need method for handling Player Bots/Cards/UW/Gaurdian Chips

    Hasn't been built out or thought out yet.

10. Milestones

    -   [ ] All dashboards share a single visual and structural language
    -   [ ] On Battle History Player can scan, filter, and trust historical data quickly
    -   [ ] A new contributor understands the app without a walkthrough

11. Exit Criteria <code>[0%]</code>

    UX & Data Integrity:
    
    -   [ ] Dashboards display only computed outputs
    -   [ ] No dashboard performs calculations inline
    -   [ ] All filters affect views consistently
    
    Coverage:
    Every major entity has a visible dashboard:
    
    -   [ ] Battle History
    -   [ ] Charts
    -   [ ] Cards
    -   [ ] UWs
    -   [ ] Guardians
    -   [ ] Bots
    
    Stability:
    
    -   [ ] No new models added
    -   [ ] No migrations required
    -   [ ] Test suite passes unchanged
    
    \### Demo Test
    A new user can:
    
    1.  Import runs
    2.  View history
    3.  Inspect progress
    4.  Understand trends …without explanation.


<a id="org06339de"></a>

## Backlog <code>[0/5]</code>

“Out of Scope”:

-   Cloud sync
-   Real-time scraping


<a id="org88f5053"></a>

### TODO Allow Multiple Players to Store

1.  Core Principle: Everything Belongs to a Player

    Yes: every player-specific model must be bound to a Player.
    
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


<a id="orgdbcb6b2"></a>

### TODO Add Chart Builder Modal to Charts Dashboard

Let user select chart style and metrics to show\*\*\* TODO [#B] Comparison / Scenario View

Examples:

-   Run A vs Run B
-   Before vs after unlocking card slot
-   With Guardian Chip/UW X vs without

This is where the app becomes decision-making, not logging.


<a id="org4117ed3"></a>

### TODO Add Advice for Optimization

Based on logged performance data, it could be possible to calculate and offer suggestions based on the data.

For Example:

-   Which UW to unlock next
-   Bot properties to improve
-   Guardian Chip properties to improve
-   Weighted Preset Rankings


<a id="orgb31181b"></a>

### TODO Linking Presets/UW/Guardian Chips/Bots to battle history

Mostly a visual tweak, but adds context and history for the player to interpert their performance history. 


<a id="org69078aa"></a>

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

