# S.T.A.L.K.E.R.: Story

## Table of Contents
- [Purpose](#purpose)  
- [Notes](#notes)
- [CLI/Legacy](#clilegacy)
- [Inspiration: Based on S.T.A.L.K.E.R.](#inspiration-based-on-stalker)  
- [High-level Design Goals](#high-level-design-goals)  
- [Core Systems & Features (Terminal & Python-focused)](#core-systems--features-terminal--python-focused)  
- [Art, Audio, Narrative & Worldbuilding Goals (Text-first)](#art-audio-narrative--worldbuilding-goals-text-first)  
- [Technical Goals & Constraints (Python CLI)](#technical-goals--constraints-python-cli)  
- [Milestones for a Complete Game](#milestones-for-a-complete-game)  
- [Non-goals & Legal Notes](#non-goals--legal-notes)
- [Official Installation](#official-installation)
- [☢️ S.T.A.L.K.E.R. Lore Timeline](#️-stalker-lore-timeline)


## Purpose
Document the vision, scope, and design goals for STALKER_STORY as a single-player, terminal-based text narrative/survival game implemented in Python. This document outlines systems, architecture patterns, and practical implementation and release targets for a playable CLI experience.

## Notes
While mainly origination as a CLI program, it has moved to basic gui, it is still text based, but GUI allows easier binary distribution and compatibility across operating systems. With this, a basic gui map was also added, being a simple dot on a grid, better showing where the player is located. It still runs simply and can still be launched through CLI with `$ python3 main.py`.

## CLI/Legacy
Want the original terminal based version? Click [here](https://raw.githubusercontent.com/AvaCaine/Stalker-Story/refs/heads/main/legacy.py) to access the file, then on your keyboard, type/press `ctrl+s` to save it.

## Inspiration: Based on S.T.A.L.K.E.R.
- High-level inspiration: atmosphere, tension, exploration, emergent encounters — translated into text-driven mechanics and procedural events.
- All content and writing are original; mechanics and tone are influenced by the S.T.A.L.K.E.R. family without using proprietary material.
- Aim: capture systemic emergent storytelling in a text-first interface.

## High-level Design Goals
- Deliver an immersive, low-dependency CLI experience that emphasizes choice, risk-reward, and exploration through descriptive text.
- Keep controls simple and keyboard-first; support replayability via procedural encounters and branching narrative.
- Minimize micromanagement while preserving survival tension (resources, hazards, reputation).
- Make content data-driven so community mods (text files, JSON/YAML) can extend the game.

## Core Systems & Features (Terminal & Python-focused)
- World model: zone graph (nodes = locations). Locations described in text, with POIs and short ASCII/ANSI art optional.
- Anomaly system: textual descriptions, clear cues, predictable mechanics (timers, prox triggers) implemented as deterministic/semi-random events.
- Inventory & items: simple item objects stored in JSON-compatible formats; weight, uses, degradation handled in Python.
- Encounters: dynamic event spawner that schedules procedural or scripted text encounters to produce emergent stories.
- NPC factions & reputation: numeric faction scores influencing available dialogue/actions and procedural mission offers.
- Combat & tactics: turn-based text encounters with choices (shoot, hide, throw item, use environment) and RNG for tension.
- Survival loop: hunger, fatigue, contamination; textual feedback and simple status effects that influence options.
- Quest system: mixed scripted narrative missions plus procedurally-generated gigs (data-driven).
- Save/load: portable JSON or SQLite save format; autosave and manual save slots.
- Input parsing: command-based interface with clear verbs (go, examine, use, talk, inventory). Support hotkeys and short commands.
- Accessibility: clear text layout, adjustable colors/contrast, optional verbose/concise modes.
- Testing hooks: deterministic seeds for reproducible procedural runs and automated tests.

## Art, Audio, Narrative & Worldbuilding Goals (Text-first)
- Visual: focus on evocative prose and minimal ASCII/ANSI art for mood; no high-fidelity assets required.
- Audio: optional short sound cues via cross-platform Python audio libs; always optional and fallback to silent mode.
- Worldbuilding: reveal lore via environmental descriptions, notes, NPC dialogue, and emergent event outcomes.
- Writing: concise, atmospheric text prioritized over large scripted cinematic scenes; branching lines for key characters.

## Technical Goals & Constraints (Python CLI)
- Language: Python 3.9+; prefer wide compatibility (Linux, macOS, Windows consoles).
- Recommended libs: prompt_toolkit or rich for input/UI, click/argparse for CLI options, tinydb or sqlite for structured data, pytest for tests.
- Architecture: separation of core engine (game loop, state, RNG) from presentation layer (terminal renderer). CLI renderer should be replaceable for future GUIs.
- Data-driven content: JSON/YAML/CSV definitions for items, factions, events, quests, and dialogue. Scripted events expressed in a simple domain-specific format (YAML/JSON).
- Packaging: distributable as a pip package and standalone executable via PyInstaller for non-dev users.
- Performance: lightweight; single-process, low memory footprint. Deterministic RNG seed for reproducibility and testing.
- Modding: support a mods/ directory where JSON/YAML overrides or additions are loaded at runtime. Provide a simple mod loader and schema validation.
- Logging & debugging: configurable logging levels; developer mode with verbose state dumps and reproducible seeds.
- Internationalization: plan for UTF-8 text support; externalized strings for future translation.

## Milestones for a Complete Game
- Prototype (vertical slice): playable zone, core loop (move/examine/encounter/save), simple inventory, one faction, and one anomaly type.
- Alpha: multiple zones, faction interactions, procedural encounters, quest framework, save/load, CLI polish.
- Beta: expanded content, mod support, deterministic testing suite, packaging, basic accessibility options.
- Release: complete narrative arc, polished writing, documentation, modding examples, installers or wheels.
- Post-release: community content hub, curated mods, optional audio packs.

## Non-goals & Legal Notes
- No use of proprietary S.T.A.L.K.E.R. assets, story text, or trademarks.
- The project is original IP that channels similar systems and tone; avoid copying trademarked content.
- Do not include copyrighted text from other works in shipped content.

---

If desired next steps:
- Create a minimal repo layout (src/, data/, mods/, tests/, docs/).
- Draft a simple event schema (YAML) and one example mod.
- Implement a vertical-slice prototype using prompt_toolkit + pytest.

## Official Installation
[Click here to download.](https://github.com/AvaCaine/Stalker-Story/releases/tag/V1.0.0)

## ☢️ S.T.A.L.K.E.R. Lore Timeline

This timeline details the key events in the lore of the *S.T.A.L.K.E.R.* series, focusing on the history of the **Chernobyl Exclusion Zone** and the clandestine research that led to its anomalous state.

---

### Pre-Disaster Events (Unknown - 1986)

| Year | Event | Notes |
| :--- | :--- | :--- |
| **Unknown** | **Limansk is founded** as a closed city for scientists working on **mind-affecting radio-waves**. | Notoriety spreads among neighboring villages. |
| **1960s** | The **Institute of Crop Selection and Genetics** is established as a cover for **Soviet consciousness control research**. | |
| **1966** | **Project IRCD-1** (Individual Remote Communication Device), or **"FIBER-1P"**, begins, then is suspended. | Led by Associate Prof. Sakharov. |
| **1976** | Dr. Orlov completes a test of the **Duga array** aimed at **mapping the Noosphere**. | Information stored at the lab under Promin CMD Factory. |
| **1981** | Construction begins on the science center that would become the **Dark Valley** lab. | |

---

### The First Disaster and Immediate Aftermath (1986 - 2005)

| Year | Date/Period | Event | Notes |
| :--- | :--- | :--- | :--- |
| **1986** | April 26 | **Chernobyl Disaster**: Reactor Four of the **CNPP explodes** around 1:23 AM. | Releases dangerous radioactive materials. |
| | April 28 | **Pripyat** and other settlements are **evacuated**. | Liquidators build the **Sarcophagus**. The **Chernobyl Exclusion Zone** is cordoned off. |
| | **Post-Disaster** | The Institute of Crop Selection and Genetics is shut down. The **Skadovsk** is grounded in **Zaton**. | Military facility blueprints moved to the Prometheus Movie Theater. |
| **1987-1989** | | Institute re-established as the **Agroprom Research Institute**. | A vehicle factory is set up near Agroprom. |
| **1989** | | **C-Consciousness Project begins**, led by scientists from **The Group**. | **FIBER-1P** is successfully tested; **psi-radiation** linked to an external information field. |
| **1991** | December 26 | **Soviet Union collapses**. Many clandestine projects lose state funding, but researchers continue operations. | The Group receives funding from the Regulatory Board. |
| | **Post-Collapse** | Ideas drafted to grow a **giant brain at Lab X-16** to create a psi-radiation source. **Beta Psi radiation** discovered. | |
| **1993** | | First test of **Raduga** (Rainbow) fails; deadly to sentient beings due to Noosphere interference. | Suggested modification to an aggression-supressing device. |
| **1995** | | First **Caribbean Experiment** at **Lab X-6** accidentally creates the first **Alpha Artifact**. | Occurs at a receiving vessel in the Caribbean Sea. |
| **1996** | Fall | Dr. Kaymanov tests the first pod at Orbita Station. Valentyn Dalin plans the **eight-pod system** for a **Common Consciousness**. | |
| **1998** | March 6 | Engineers claim **six field Generators** have been built deep in the Zone. | Speculation on psychic tests abounds. |
| | September | Scouting for the **C-Consciousness installation** (**Laboratory X7**) site is underway. | Azimuth Station, Sphere, and Krug antenna complex used to probe the Noosphere. |
| **1999** | February 22 | Ukrainian government launches an official investigation into illegal experiments in the Zone. | Security Service of Ukraine (SSU) sends a special commission. Disturbing memos by O. O. Dobrynin uncovered. |
| **2001** | | Zone begins to attract attention. **Pripyat** is a hot spot for strange phenomena. **Zone is completely sealed off** after a bus of tourists disappears. | The 1st generation **Exoskeleton** test prototype is assembled. |
| **2003** | March | Final assembly of the **C-Consciousness installation (Lab X7)** is underway. **Lab X11** is being built to house the **Alpha Artifact**. | Agroprom Research Institute begins working for The Group. |
| **2004** | | Top secret **electromagnetic rifle project** (Gauss rifle) at the **Jupiter factory is cancelled**. | |
| **2005** | | Unnatural forces influence a wider area; significant changes in weather, including **hurricane winds and tremors**. | |

---

### The Second Disaster and the Rise of Stalkers (2006 - 2011)

| Year | Date/Period | Event | Notes |
| :--- | :--- | :--- | :--- |
| **2006** | January | Rift forms between C-Consciousness scientists. Dr. Kaymanov is replaced by a **Variometer** in the eighth pod. | |
| | March 4 | A phenomena of **blinding light** illuminates the sky above the CNPP for two hours. | |
| | April 12, 14:33 +2 GMT | The phenomena repeats, followed by a **tremendous thunderous crash** and a **6.9 magnitude earthquake**. This is the **"Second Disaster."** | Deadly energy disturbances rage; center of the explosion is $\ge 1$ km from CNPP. |
| | May 21 | Prof. Dvupalov experiments with controlling mutants with a **Leash**. | |
| | June 10 | The Zone abruptly grows **five kilometers bigger** (the **"Second Disaster"**). **New Zone manifests** with defiance of scientific laws. | Most Military and lab staff perish. |
| | **Post-Disaster** | Ukrainian Military's nuclear attempt fails; troops are scattered. Captain Tachenko's survivors form **Duty**. Dr. Kaymanov flees, assumes identity of **Doctor**. | |
| **2007** | | Scientists are unable to explain the Second Disaster. Expeditions fail. Survivors speak of **mutated animals**. | |
| **2008** | | **VPC Mirror facility** (used to study induced illusions) shuts down. | |
| **2009** | September 28 | Kiev scientists create a special device for **detecting anomalous activity**. Winter expedition travels 1km into the Zone. | Strelok, Fang, and Ghost wander into Doctor's swamp and make first contact. |
| **2010** | August 17 | Expeditions penetrate further. First artifacts located, and first **blowouts** observed. | **Strelok** brings the **Heart of Chornobyl** to Doctor. |
| **2011** | **Early** | Second Military raid to the CNPP fails, triggering a serious **emission** that destroys much of the force. **Zvyagintsev** is one of the few survivors. | |
| | **One Month Later** | Zvyagintsev and other Military survivors are absorbed into **Duty**, significantly boosting its manpower. | |
| | **Growing Presence** | **Stalkers** (amateur researchers, scavengers, adventurers) begin entering the Zone for 'artifacts.' SSU initially ignores, but later re-evaluates policy. | Stalkers report **'zombies'**. |
| | February 4 | Ukrainian government retaliates against 'illegal' Stalkers; many arrested and trading posts closed. | |
| | Summer | **Strelok's group** reaches the **Sarcophagus** and the **Wish Granter**. Strelok is gravely wounded and nursed back to health by Doctor. | |
| | Early September | Large group of Stalkers disappears near the **Brain Scorcher** and re-emerges as the heavily-armed, radicalized **Monolith** faction. | Monolith establishes HQ at the CNPP, guarding the Wish Granter. |
| | | Strelok, Fang, and Ghost successfully penetrate the Brain Scorcher. The Zone triggers an **extremely severe emission**, reshaping the entire landscape. | Paths change, anomalies become invisible. Military presence at Army Warehouses almost eradicated. |
| | **Post-Emission** | Bandits under **Yoga** take over the **Garbage** and establish a punitive order, demanding 'taxes' from Stalkers. Loners eventually execute the corrupt Major Khaletskiy at the Cordon Outpost. | **Freedom** relocates its main base to the **Army Warehouses**. |
| | September 3 | E. F. Kalancha receives orders to observe Noosphere fluctuations. | |
| | September 10 | **Clear Sky begins** - Scar, caught in the blowout, is tasked with eliminating Strelok's group. | N. A. Lebedev receives orders to accept Scar as agent A:MS-017 and eliminate Strelok, agent A:LS-013. |
| | October 25 | Ukrainian government authorizes a **shoot-on-sight policy** towards Stalkers. | |
| | Late | Duty and Freedom reach **Limansk**, leading to a battle for control. Aggressive Stalkers dressed like Monolith sighted near the Brain Scorcher. | Clear Sky's operation to penetrate the CNPP in pursuit of Strelok is annihilated by another severe emission. |

---

### Game Events and Later History (2012 - 2021)

| Year | Date/Period | Event | Notes |
| :--- | :--- | :--- | :--- |
| **2012** | May 1, 5:30 +2 GMT | ***Shadow of Chernobyl*** **begins** - **Strelok** (the **Marked One**) awakes at Sidorovich's bunker. | |
| | May 12-25 | Captain Maksimenko investigates the Agroprom Research Institute, revealing it as a front for The Group. | |
| | **Mid** | **Strelok disables the Brain Scorcher**, opening the path to the center of the Zone. | Military stages **Operation Monolith** to reclaim CNPP, which fails due to an emission. |
| | **Late** | **Strelok reaches the CNPP and destroys the C-Consciousness**. | Zone becomes more unstable; Monolith weakens; Strider and his squad are released from Monolith control. |
| | **Post-CNPP** | **Beard** and Grouse establish a camp at the grounded ship **Skadovsk** in **Zaton**. Sultan and his Bandits also entrench themselves there. | Garry discovers a path to **Jupiter**; a camp is established at **Yanov Station**. |
| | | Loki (Freedom) and Shulga (Duty) forces clash at Yanov. Zulu senses an emission, leading to a **ceasefire** and Yanov being declared **neutral territory**. | Zulu later retires from Duty. |
| | | Ukrainian government executes **Operation Fairway** to restore control; it immediately results in disaster. | |
| | August 3, 9:00 +2GMT | ***Call of Pripyat*** **begins** - SBU agent **Major Degtyarev** is dispatched undercover to investigate Operation Fairway's failure. | |
| | **Late** | Degtyarev assembles a squad, links up with Fairway survivors in Pripyat, and salvages the operation, re-establishing comms. | **Strelok** joins the group for evacuation. Degtyarev helps **Strider** form **Noontide**. |
| **2013** | | **D4 Treaty** is signed. | Proxy war begins between Duty and Freedom in the Garbage. |
| | | **Operation Zenith** to shut down the Generators is executed, resulting in **total failure**. | |
| **2014** | **Sometime 2014-2015**| Duty cedes **Rostok** to Freedom. Freedom abandons Army Warehouses and moves to Rostok. Duty moves to the Cement factory. | |
| | | Sultan and his bandits stage a successful coup, taking the *Skadovsk* from Beard. The ship is renamed the *Sultansk*. | Beard leaves Zaton and joins Degtyarev in Pripyat. |
| | February 17 | **Cpt. Sukhin** is admitted to a military hospital with partial **retrograde amnesia** after an alleged shootout with Monolith. | |
| **2016** | November | The **4th generation Exoskeleton project** begins at **SIRCAA**. | |
| **2017** | March 3 | **Strelok records a message to himself** due to failing memory, recalling his attempt to **sabotage Laboratory X-11**. | |
| **2018** | October | **4th generation Exoskeleton** is unveiled. | |
| **2019** | | The second **Caribbean Experiment** is attempted at **Laboratory X-11**, resulting in **total failure**. | |
| **2020** | | Beard leaves Pripyat and returns to **Zaton**, setting up aboard the **Shevchenko**. | |
| **2021** | | **Skif's apartment is destroyed by an anomaly**. He finds a dummy Alpha Artifact. | |
| | **Current** | ***Heart of Chornobyl*** **begins** - **Skif** enters the Zone to investigate the Alpha Artifact. | |