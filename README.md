# D&D 5e Alternative Monster Maker

## Overview

This program is designed to generate a simple stat block for a custom D&D 5e NPC or monster, based on some context.

## Inspiration

_Based on [this article](https://www.worldanvil.com/w/erdos-memberoftheorder/a/better-encounter-balancing-article),
which was inspired by [this article](https://theangrygm.com/f-cr-theres-a-better-way-part-1/)._

Summary: In D&D 5e, encounter balancing is obnoxious at best due to an alarming abundance of numbers and math.
Worse yet, some of those numbers only work in context, but that context is missing or implicit.
However, there are only a few, easy numbers that actually affect combat difficulty, which require far less math.
In fact, thanks to The Angry GM, there is very little math left, there is instead a Big Ol' Table of Numbers (and Context).

> Q: Why make this into a python script?
> A: Because I'm insane and enjoy using scripts (rolling lots of dice, doing path, etc.) to make my DM-life easier.

## Requirements

Python3.6+

## Usage

Run the script with `-h` or `--help` for help text. Here is some extra information (i.e. context) for clarity.

### Stats and Threat

Only 6 stats are useful (listed below), and each of these stats can be marked good (`--good|-g`) or poor (`--poor|-p`) -
otherwise they are assumed to be average.

| Stat | Abbrev. |
|:-----|:--------|
| Armor Class | `AC` |
| Health Points | `HP` |
| Attack | `ATK` |
| Difficulty Class<br/>(for forcing saving throws) | `DC` |
| Average Damage | `DMG` |

Each good stat increases the monster's "threat" by 1, and each poor stat decreases it by 1.
A monster's threat is a minor adjustment within its tier.
Threat is normally either low, medium, or high.

| Threat Level | Threat Score |
|:------------:|:------------:|
| Trivial* | -4 or less |
| Low | -3 to -2 |
| Medium | -1 to 1 |
| High | 2 to 3 |
| Extreme* | 4 or more |

_*Monsters marked as a trivial or extreme threat should probably be adjusted in tier rather than threat._

### Tiers

While levels as numbers (1-20) can be used, it is recommended that users become comfortable with the concept of tiers instead.
While Player Characters (PCs) progress smoothly through levels 1-20, the challenges they face create a "see-saw" effect:
at the beginning of a "tier", the monsters are harder thus giving the PCs a sense of challenge;
at the end of a "tier", the monsters do not progress (though the players do) thus giving the PCs a sense of progress;
once the PCs swith tiers, the see-saw begins again, thus the challenges become more challenging once again.

| Tier | Level Range |
|:----:|:-----------:|
| Apprentice | 1-2 |
| Journeyman | 3-5 |
| Adventurer | 6-8 |
| Veteran | 9-11 |
| Champion | 12-14 |
| Heroic | 15-17 |
| Legendary | 18-20 |

### Count

Remember what I said about missing context?
That mainly refers to the idea that some monsters were designed to appear in larger groups than others:
some are meant to appear in mobs (2 or more monster for each PC) whereas some are meant to appear solo.

Thus, when generating a new monster, include the number of monsters that should appear together (1-20 work best).
Think of it this way: each PC creates a monster slot.
A solo (1) monster will fill about 4 slots,
a pair (2) of monsters will fill about 2 slots each,
a party (3-6) will fill about 1 slot each, etc.
Thus, if two completely different monsters are meant to appear together,
set the `count` as the number of monsters this monster is meant to stand-in for.

E.g. a Black Knight and its Nightmare steed. Even though we intend to use only 1 of each monster,
each should be generated using a `count` of `2` or `Pair`.

| Count Level | Count |
|:-----------:|:-----:|
| Solo | 1 |
| Pair | 2 |
| Party | 3-6 |
| Gang | 7-10 |
| Mob | 11-20 |
| Army* | 20+ |

_*D&D is meant to emphasize individual adventuring. Fighting too many monsters at once is either a different game with rules
better suited to battles between armies, or should be handled as a set of skill checks rather than as combat._

### Adjustments

#### Multiple Attacks

Whether multiple attacks or the ability to attack multiple targets at once, the ability to damage multiple opponents greatly
affects a combatant's usefulness. The average damage (`Dmg`) stat represents __total__ average damage dealt among _all_ opponents.
Thus, the ability to target multiple opponents will reduce the `Dmg` stat.

The `--apr|-a` (for __A__ttacks-__p__er-__r__ound) option accepts either a number representing the number off separate attacks
the monster can make in a round (including significant reactions such as the Hellish Rebuke spell).
It can also be "area" which assumes 3 opponents will be hit (and is equivalent to `--apr 3`),
or "dot" (__d__amage __o__ver __t__ime, which assumes the ability will deal damage once on average before being resisted).

#### Defenses

A monster with significant defenses - e.g. flying (at lower tiers), many significant resistances or immunities, etc. - 
should be noted with the `--resist|-r`. This will reduce the monster's HP to maintain balance (while allowing for flavor).

### Name
Finally, every monster needs a good name. Although this parameter is techinically optional, it is greatly encouraged
to choose a meaningful name for your monster - it will appreciate it.
