# Manual Testing Guide

This page is **Developer Documentation**. It defines manual QA coverage for theTowerStats.

## Overview

Manual testing confirms end-to-end behavior that is difficult to automate, such as data import flows, chart rendering, and per-user scoping. This guide is divided into **Golden Tests** (deterministic, baseline checks) and **Integration Tests** (cross-feature workflows).

## Test Data & Accounts

- Create a new user with a unique username prefix: `test_*`.
- Use a clean browser profile or incognito session for each full pass.
- Use the provided Battle Reports to the new test user in [Sample Battle Reports](#sample-battle-reports).
- If the three reports are not visible after login, stop and request the data to be added.

## Golden Tests

Golden Tests validate deterministic outputs using the provided three Battle Reports. These checks should be repeatable and produce identical results for every tester.

### Golden Test 1: Account creation and access

1. Open the app in a new session.
2. Select **Sign in**.
3. Create a new user named `test_<unique>` with a password.
4. Sign in with the new user.
5. Confirm the top navigation shows signed-in options (Battle History, Charts, Cards, Ultimate Weapons, Guardian Chips, Bots).
6. Sign out and sign back in to confirm credentials persist.

**Expected**
- The account is created successfully and can log in immediately.
- Navigation updates to the signed-in experience after login.

### Golden Test 2: Battle Reports present and parsed

1. Select **Battle History**.
2. Confirm exactly three rows are present (the preloaded Battle Reports).
3. For each row, open the Battle Report detail (or review the row values) and compare against the report text:
   - Battle date
   - Tier
   - Highest wave
   - Killed by
   - Coins earned
   - Cash earned
   - Interest earned
   - Gem blocks (if present)
   - Cells earned (if present)
   - Reroll shards (if present)
4. Confirm missing values show an em dash (—) instead of a fabricated number.

**Expected**
- All visible values match the report text exactly.
- Missing values display as an em dash (—), not zero or a guessed value.

### Golden Test 3: Preset labeling and filtering

1. In **Battle History**, set a preset label (for example, `golden-a`) on the first report.
2. Set a different preset label (for example, `golden-b`) on the second report.
3. Leave the third report without a preset.
4. Use the **Preset** filter to show only `golden-a`.
5. Clear the filter and repeat for `golden-b`.

**Expected**
- Preset badges appear on the correct rows.
- The preset filter returns only the matching rows.
- The report without a preset never appears in a filtered preset view.

### Golden Test 4: Sorting and diagnostics

1. In **Battle History**, sort by **Highest wave** ascending, then descending.
2. Sort by **Coins earned** ascending, then descending.
3. Observe **Killed By (diagnostic)** and compare counts to the visible table rows.

**Expected**
- Sorting toggles between ascending and descending order for each column.
- Diagnostic counts match the currently visible rows.

### Golden Test 5: Charts values and filters

1. Select **Charts**.
2. Choose a metric that is present in all three reports (for example, **Coins earned** or **Highest wave**).
3. Confirm exactly three data points appear.
4. Apply a **Tier** filter that should include only one or two of the reports.
5. Verify the chart updates to match the filtered count.
6. Repeat with the **Preset** filter (`golden-a`, `golden-b`).

**Expected**
- Chart points correspond to the same three reports in Battle History.
- Filters reduce the chart to the same subset as Battle History.

### Golden Test 6: Derived metric calculation

1. In **Charts**, select a derived metric (for example, **Coins/real hour**).
2. For one report, calculate the expected value manually using the report’s coins and run duration.
3. Compare the chart value to the manual calculation, allowing for the same rounding shown in the UI.

**Expected**
- Derived values align with the manual calculation and visible rounding rules.

### Golden Test 7: Progress pages default state

1. Open **Cards**.
2. Open **Ultimate Weapons**.
3. Open **Guardian Chips**.
4. Open **Bots**.
5. Confirm each page loads without errors and shows default or empty state values for a new account.

**Expected**
- Each page renders successfully for a new user.
- Default counts and progress values are shown, with no unexpected data.

## Integration Tests

Integration Tests validate cross-feature workflows and navigation across the app.

### Integration Test 1: Import flow (if manual import data is available)

1. In **Battle History**, open **Add Battle Report**.
2. Paste one of the provided Battle Reports into the input.
3. Enter a preset label (for example, `import-check`).
4. Select **Import Battle Report**.
5. Confirm the table shows one additional row and the preset badge is visible.

**Expected**
- The import succeeds without errors.
- The new row contains values that match the report text.

> **Note**
> If the three reports are preloaded and you do not want duplicates, use a separate `test_import_*` user for this test.

### Integration Test 2: Demo data isolation

1. Select **View demo data** in the top navigation.
2. Visit **Battle History** and **Charts**.
3. Confirm the demo data appears and is different from your user data.
4. Select **Exit demo**.
5. Return to **Battle History** and confirm your three reports are shown again.

**Expected**
- Demo data is read-only and distinct from the user’s data.
- Exiting demo mode restores the user’s own Battle Reports.

### Integration Test 3: Chart comparison mode

1. Open **Charts**.
2. Switch the chart to **Comparison** mode.
3. Select two runs from the available Battle Reports (or two date windows).
4. Review the comparison output.

**Expected**
- The comparison view renders without errors.
- The comparison is based on the selected runs or dates.

### Integration Test 4: Search and navigation consistency

1. In the top navigation, select the search field.
2. Search for a preset label you created earlier (for example, `golden-a`).
3. Open the preset result from the search list.
4. Confirm **Charts** opens with the preset filter applied.
5. Clear the preset filter and navigate to **Battle History**.
6. Confirm the labeled report still exists in the table.

**Expected**
- Search results include the preset label from the signed-in account.
- Opening the preset result applies the preset filter on Charts.
- Battle History still contains the labeled report after navigation.

### Integration Test 5: Progress tracking persistence

1. In **Cards**, update the inventory of one card and apply a preset tag.
2. Refresh the page.
3. Confirm the updated inventory value and preset tag are still present.
4. Repeat for one entry in **Ultimate Weapons**, **Guardian Chips**, and **Bots**.

**Expected**
- Updates persist after refresh.
- Preset tags remain visible and filterable where available.

## Reporting

When reporting a failure, capture:

- The page and action sequence leading to the issue.
- The username used (`test_*`).
- Whether demo mode was active.
- A screenshot or copy of the error message, if available.
- The relevant Battle Report text snippet when the issue involves parsing.

## Sample Battle Reports

### Sample 1

Battle Report
Battle Date	Dec 21, 2025 13:18
Game Time	11h 4m 50s
Real Time	2h 46m 15s
Tier	8
Wave	1141
Killed By	Boss
Coins earned	16.89M
Coins per hour	6.09M
Cash earned	$43.25M
Interest earned	$2.26M
Gem Blocks Tapped	3
Cells Earned	209
Reroll Shards Earned	302
Combat
Damage dealt	68.74q
Damage Taken	15.29B
Damage Taken Wall	3.09B
Damage Taken While Berserked	21.80B
Damage Gain From Berserk	x8.00
Death Defy	0
Lifesteal	28.31M
Projectiles Damage	9.84q
Projectiles Count	337.50K
Thorn damage	144.62T
Orb Damage	2.76q
Enemies Hit by Orbs	1.63K
Land Mine Damage	621.66T
Land Mines Spawned	23462
Rend Armor Damage	0
Death Ray Damage	0
Smart Missile Damage	396.21T
Inner Land Mine Damage	0
Chain Lightning Damage	54.83q
Death Wave Damage	9.91T
Tagged by Deathwave	4464
Swamp Damage	0
Black Hole Damage	0
Electrons Damage	0
Utility
Waves Skipped	0
Recovery Packages	696
Free Attack Upgrade	561
Free Defense Upgrade	554
Free Utility Upgrade	549
HP From Death Wave	0.00
Coins From Death Wave	130.70K
Cash From Golden Tower	$17.75M
Coins From Golden Tower	2.34M
Coins From Black Hole	0
Coins From Spotlight	47.49K
Coins From Orb	0
Coins from Coin Upgrade	6.74M
Coins from Coin Bonuses	7.34M
Enemies Destroyed
Total Enemies	79462
Basic	49365
Fast	10418
Tank	11021
Ranged	7777
Boss	114
Protector	130
Total Elites	51
Vampires	19
Rays	12
Scatters	20
Saboteur	0
Commander	0
Overcharge	0
Destroyed By Orbs	1630
Destroyed by Thorns	11
Destroyed by Death Ray	0
Destroyed by Land Mine	3618
Destroyed in Spotlight	8720
Bots
Flame Bot Damage	102.66T
Thunder Bot Stuns	828
Golden Bot Coins Earned	19.18K
Destroyed in Golden Bot	623
Guardian
Damage	40.45T
Summoned enemies	0
Guardian coins stolen	0
Coins Fetched	12.92K
Gems	3
Medals	0
Reroll Shards	27
Cannon Shards	3
Armor Shards	6
Generator Shards	6
Core Shards	3
Common Modules	1
Rare Modules	0

### Sample 2

Battle Report
Battle Date	Dec 20, 2025 16:42
Game Time	2h 42m 14s
Real Time	40m 33s
Tier	5
Wave	319
Killed By	Fast
Coins earned	2.00M
Coins per hour	2.95M
Cash earned	$5.10M
Interest earned	$630.08K
Gem Blocks Tapped	1
Cells Earned	6
Reroll Shards Earned	52
Combat
Damage dealt	159.38T
Damage Taken	746.88M
Damage Taken Wall	77.54M
Damage Taken While Berserked	912.38M
Damage Gain From Berserk	x8.00
Death Defy	1
Lifesteal	12.07M
Projectiles Damage	28.99T
Projectiles Count	50.56K
Thorn damage	150.24B
Orb Damage	17.77T
Enemies Hit by Orbs	1.17K
Land Mine Damage	2.64T
Land Mines Spawned	5389
Rend Armor Damage	0
Death Ray Damage	0
Smart Missile Damage	181.42B
Inner Land Mine Damage	0
Chain Lightning Damage	109.57T
Death Wave Damage	25.68B
Tagged by Deathwave	1171
Swamp Damage	0
Black Hole Damage	0
Electrons Damage	0
Utility
Waves Skipped	0
Recovery Packages	205
Free Attack Upgrade	152
Free Defense Upgrade	161
Free Utility Upgrade	162
HP From Death Wave	0.00
Coins From Death Wave	7.47K
Cash From Golden Tower	$1.54M
Coins From Golden Tower	252.55K
Coins From Black Hole	0
Coins From Spotlight	5.65K
Coins From Orb	0
Coins from Coin Upgrade	1.10M
Coins from Coin Bonuses	595.51K
Enemies Destroyed
Total Enemies	18462
Basic	13302
Fast	1921
Tank	1951
Ranged	1186
Boss	39
Protector	31
Total Elites	2
Vampires	0
Rays	1
Scatters	1
Saboteur	0
Commander	0
Overcharge	0
Destroyed By Orbs	1171
Destroyed by Thorns	5
Destroyed by Death Ray	0
Destroyed by Land Mine	1004
Destroyed in Spotlight	1862
Bots
Flame Bot Damage	32.25B
Thunder Bot Stuns	114
Golden Bot Coins Earned	2.65K
Destroyed in Golden Bot	155
Guardian
Damage	26.88B
Summoned enemies	0
Guardian coins stolen	0
Coins Fetched	1.52K
Gems	0
Medals	1
Reroll Shards	0
Cannon Shards	0
Armor Shards	0
Generator Shards	0
Core Shards	0
Common Modules	0
Rare Modules	0

### Sample 3

Battle Report
Battle Date	Dec 17, 2025 18:55
Game Time	10h 28m 53s
Real Time	2h 37m 13s
Tier	8
Wave	1081
Killed By	Boss
Coins earned	26.78M
Coins per hour	10.22M
Cash earned	$38.60M
Interest earned	$2.15M
Gem Blocks Tapped	3
Cells Earned	205
Reroll Shards Earned	384
Combat
Damage dealt	39.77q
Damage Taken	11.05B
Damage Taken Wall	2.42B
Damage Taken While Berserked	0
Damage Gain From Berserk	x0.00
Death Defy	1
Lifesteal	156.21M
Projectiles Damage	2.57q
Projectiles Count	255.71K
Thorn damage	87.62T
Orb Damage	1.19q
Enemies Hit by Orbs	1.18K
Land Mine Damage	276.20T
Land Mines Spawned	22145
Rend Armor Damage	0
Death Ray Damage	0
Smart Missile Damage	43.81T
Inner Land Mine Damage	0
Chain Lightning Damage	35.54q
Death Wave Damage	1.97T
Tagged by Deathwave	4944
Swamp Damage	0
Black Hole Damage	0
Electrons Damage	0
Utility
Waves Skipped	0
Recovery Packages	384
Free Attack Upgrade	547
Free Defense Upgrade	540
Free Utility Upgrade	524
HP From Death Wave	0.00
Coins From Death Wave	154.75K
Cash From Golden Tower	$15.24M
Coins From Golden Tower	2.91M
Coins From Black Hole	0
Coins From Spotlight	54.81K
Coins From Orb	0
Coins from Coin Upgrade	9.88M
Coins from Coin Bonuses	13.42M
Enemies Destroyed
Total Enemies	74902
Basic	46945
Fast	9854
Tank	10082
Ranged	7293
Boss	108
Protector	124
Total Elites	50
Vampires	15
Rays	20
Scatters	15
Saboteur	0
Commander	0
Overcharge	0
Destroyed By Orbs	1181
Destroyed by Thorns	11
Destroyed by Death Ray	0
Destroyed by Land Mine	3830
Destroyed in Spotlight	7740
Bots
Flame Bot Damage	39.79T
Thunder Bot Stuns	633
Golden Bot Coins Earned	19.53K
Destroyed in Golden Bot	565
Guardian
Damage	13.28T
Summoned enemies	0
Guardian coins stolen	0
Coins Fetched	19.94K
Gems	1
Medals	2
Reroll Shards	9
Cannon Shards	6
Armor Shards	3
Generator Shards	0
Core Shards	0
Common Modules	0
Rare Modules	0
