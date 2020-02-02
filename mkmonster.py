import json
import argparse
from functools import reduce


# Stat class definitions
# ------------------------
class Count:
    RANGES = {
        # Key: Label
        # Value: Tuple range (inclusive) of valid counts (None is +/-INF)
        #        followed by default/average
        'solo': (1, 1, 1),
        'pair': (2, 2, 2),
        'party': (3, 5, 4),
        'gang': (7, 10, 8),
        'mob': (11, 20, 16),
        'army': (21, None, None)
    }

    def __init__(self, size_label: str, count: int):
        self._label = size_label.lower()
        self._int = count

    def __str__(self) -> str:
        r = Count.RANGES[self._label]
        label = self._label[0].upper() + self._label[1:]

        if r[0] is None:
            return f'{label} (<{r[1]})'
        elif r[1] is None:
            return f'{label} ({r[0]}+)'
        elif r[0] == r[1]:
            return f'{label} ({r[0]})'

        return f'{label} ({r[0]}-{r[1]})'

    def __int__(self) -> int:
        return self._int

    @classmethod
    def from_int(cls, count: int) -> 'Count':
        for k in Count.RANGES:
            r = Count.RANGES[k]

            if r[0] is None:
                r = (count, r[1])
            if r[1] is None:
                r = (r[0], count)

            if r[0] <= count <= r[1]:
                return cls(k, count)

        return None

    @classmethod
    def from_label(cls, label: str) -> 'Count':
        label = label.lower()
        r = Count.RANGES[label]

        return cls(label, r[2])


class Stat:
    @classmethod
    def from_json(cls, obj: dict):
        raise NotImplementedError


class StatRange(Stat):
    def __init__(self, min: int, max: int):
        self.min = min
        self.max = max

    def __contains__(self, level: int) -> bool:
        return self.min <= level <= self.max

    @classmethod
    def from_json(cls, obj):
        return StatRange(
            obj['min'],
            obj['max']
        )


class QualityStat(Stat):
    def __init__(self, poor: int, average: int, good: int):
        self.poor = poor
        self.average = average
        self.good = good

    @classmethod
    def from_json(cls, obj):
        return QualityStat(
            obj['poor'],
            obj['average'],
            obj['good']
        )


class SizedStat(Stat):
    def __init__(self, solo: QualityStat, pair: QualityStat, party: QualityStat, gang: QualityStat, mob: QualityStat):
        self.solo = solo
        self.pair = pair
        self.party = party
        self.gang = gang
        self.mob = mob

    def from_size(self, size: int) -> QualityStat:
        if size == 1:
            return self.solo
        elif size == 2:
            return self.pair
        elif 3 <= size <= 6:
            return self.party
        elif 7 <= size <= 10:
            return self.gang
        elif 11 <= size <= 20:
            return self.mob
        else:
            return QualityStat(1, 1, 1)

    @classmethod
    def from_json(cls, obj):
        return SizedStat(
            QualityStat.from_json(obj['solo']),
            QualityStat.from_json(obj['pair']),
            QualityStat.from_json(obj['party']),
            QualityStat.from_json(obj['gang']),
            QualityStat.from_json(obj['mob'])
        )


class Tier(StatRange):
    def __init__(self, min: int, max: int, name: str, prof: int):
        super().__init__(min, max)
        self.name = name
        self.prof = prof

    def __str__(self):
        return f'{self.name} ({self.min}-{self.max})'

    def __eq__(self, value):
        if isinstance(value, str):
            return self.name.lower() == value.lower()

    @classmethod
    def from_json(cls, obj):
        stat_range = StatRange.from_json(obj['levels'])
        return Tier(
            stat_range.min, stat_range.max,
            obj['tier'],
            obj['prof']
        )


class TierStat(Stat):
    def __init__(self, tier: Tier, ac: QualityStat, hp: SizedStat, atk: QualityStat, dc: QualityStat, dmg: SizedStat):
        self.tier = tier
        self.ac = ac
        self.hp = hp
        self.atk = atk
        self.dc = dc
        self.dmg = dmg

    @classmethod
    def from_json(cls, obj: dict):
        return TierStat(
            Tier.from_json(obj),
            QualityStat.from_json(obj['ac']),
            SizedStat.from_json(obj['hp']),
            QualityStat.from_json(obj['atk']),
            QualityStat.from_json(obj['dc']),
            SizedStat.from_json(obj['dmg'])
        )

    def __contains__(self, level: int) -> bool:
        return level in self.tier


class Monster:
    THREAT_STATS = ['ac', 'hp', 'atk', 'dc', 'dmg']

    def __init__(self, base_tier: TierStat, size: Count, name: str = None):
        self._base_tier = base_tier
        self._size = size
        self._name = name

        self._tier = self._base_tier.tier
        self._ac = self._base_tier.ac.average
        self._hp = self._base_tier.hp.from_size(int(self._size)).average
        self._atk = self._base_tier.atk.average
        self._dc = self._base_tier.dc.average
        self._dmg = self._base_tier.dmg.from_size(int(self._size)).average

        self._threats = {k: 0 for k in Monster.THREAT_STATS}

    @property
    def name(self) -> str:
        return self._name

    @name.setter
    def name(self, val):
        self._name = val

    @property
    def tier(self) -> Tier:
        return self._tier

    @tier.setter
    def tier(self, val):
        self._tier = val

    @property
    def ac(self) -> int:
        return self._ac

    @ac.setter
    def ac(self, val):
        self._ac = val

    @property
    def hp(self) -> int:
        return self._hp

    @hp.setter
    def hp(self, val):
        self._hp = val

    @property
    def atk(self) -> int:
        return self._atk

    @atk.setter
    def atk(self, val):
        self._atk = val

    @property
    def dc(self) -> int:
        return self._dc

    @dc.setter
    def dc(self, val):
        self._dc = val

    @property
    def dmg(self) -> int:
        return self._dmg

    @dmg.setter
    def dmg(self, val):
        self._dmg = val

    def __str__(self) -> str:
        vr = u' \u2502 '
        hr = u'\u2501'
        center_str = u'%s\u252F%s' % (hr, hr)

        label_width = 5
        val_width = 3

        left_val_width = val_width
        right_val_width = val_width

        hr_left_len = label_width + val_width
        total_width = hr_left_len * 2 + len(center_str)
        hr_right_len = total_width - hr_left_len - len(center_str)

        centered_fmt = f'{{:^{total_width}}}\n'

        txt = ''

        if self.name is not None:
            if len(self.name) > total_width:
                total_width = len(self.name)

                centered_fmt = f'{{:^{total_width}}}\n'

                hr_left_len = (total_width - len(center_str)) // 2
                hr_right_len = total_width - hr_left_len - len(center_str)

                left_val_width = hr_left_len - label_width
                right_val_width = hr_right_len - label_width

            txt += centered_fmt.format(self.name)
            txt += hr * total_width
            txt += '\n'


        tier_str = centered_fmt.format(str(self.tier))
        txt += tier_str

        size_str = centered_fmt.format(self.size_str)
        txt += size_str

        threat_str = centered_fmt.format(self.threat_str)
        txt += threat_str

        txt += hr * hr_left_len
        txt += center_str
        txt += hr * hr_right_len
        txt += '\n'

        fmt = f'{{:<{label_width}}}{{:>{left_val_width}}}{vr}{{:<{label_width}}}{{:>{right_val_width}}}\n'

        txt += fmt.format('Prof:', f'+{self.tier.prof}', 'DC:', f'{self.dc}')
        txt += fmt.format('AC:', f'{self.ac}', 'HP:', f'{self.hp}')
        txt += fmt.format('Atk:', f'+{self.atk}', 'Dmg:', f'{self.dmg}')

        return txt

    def _stat_from_str(self, stat_str: str) -> int:
        pass

    def _set_stat_from_str(self, stat_str: str, val):
        if stat_str in self._threats:
            if stat_str == 'ac':
                self.ac = val
            elif stat_str == 'hp':
                self.hp = val
            elif stat_str == 'atk':
                self.atk = val
            elif stat_str == 'dc':
                self.dc = val
            elif stat_str == 'dmg':
                self.dmg = val

    def _get_base_stat_from_str(self, stat_str: str):
        if stat_str in self._threats:
            if stat_str == 'ac':
                return self._base_tier.ac
            elif stat_str == 'hp':
                return self._base_tier.hp.from_size(self._size)
            elif stat_str == 'atk':
                return self._base_tier.atk
            elif stat_str == 'dc':
                return self._base_tier.dc
            elif stat_str == 'dmg':
                return self._base_tier.dmg.from_size(self._size)
            else:
                return None

    def poor(self, stat_str: str) -> None:
        if stat_str not in self._threats:
            return

        if self._threats[stat_str] != -1:
            base = self._get_base_stat_from_str(stat_str)
            if base is not None:
                self._set_stat_from_str(stat_str, base.poor)
                self._threats[stat_str] = -1

    def good(self, stat_str: str) -> None:
        if stat_str not in self._threats:
            return

        if self._threats[stat_str] != 1:
            base = self._get_base_stat_from_str(stat_str)
            if base is not None:
                self._set_stat_from_str(stat_str, base.good)
                self._threats[stat_str] = 1

    @property
    def threat(self) -> int:
        s = reduce(lambda acc, k: acc + self._threats[k], self._threats, 0)
        if self._threats['atk'] ==  self._threats['dc']:
            s -= self._threats['dc']
        return s

    @property
    def threat_str(self) -> str:
        threat = self.threat
        if threat < -3:
            return f'Trivial threat ({threat})'
        elif -3 <= threat <= -2:
            return f'Low threat ({threat})'
        elif -1 <= threat <= 1:
            return f'Medium threat ({threat})'
        elif 2 <= threat <= 3:
            return f'High threat ({threat})'
        elif 3 < threat:
            return f'Extreme threat ({threat})'
        else:
            return f'Unknown threat ({threat})'

    @property
    def size_str(self) -> str:
        count = self._size

        if count is None:
            return 'Uncountable (err)'
        else:
            return str(count)


# Decorator GoF Pattern Class Definitions
# ---------------------------------------

class AdjustedMonster(Monster):
    def __init__(self, base: Monster):
        super().__init__(base._base_tier, base._size, base._name)
        self._base = base
        self._threats = base._threats

    @property
    def name(self) -> str:
        return self._base.name

    @name.setter
    def name(self, val):
        self._base.name = val

    @property
    def tier(self) -> Tier:
        return self._base.tier

    @tier.setter
    def tier(self, val):
        self._base.tier = val

    @property
    def ac(self) -> int:
        return self._base.ac

    @ac.setter
    def ac(self, val):
        self._base.ac = val

    @property
    def hp(self) -> int:
        return self._base.hp

    @hp.setter
    def hp(self, val):
        self._base.hp = val

    @property
    def atk(self) -> int:
        return self._base.atk

    @atk.setter
    def atk(self, val):
        self._base.atk = val

    @property
    def dc(self) -> int:
        return self._base.dc

    @dc.setter
    def dc(self, val):
        self._base.dc = val

    @property
    def dmg(self) -> int:
        return self._base.dmg

    @dmg.setter
    def dmg(self, val):
        self._base.dmg = val


class AtksPerRoundAdjustment(AdjustedMonster):
    def __init__(self, base: Monster, apr: int):
        super().__init__(base)
        self._apr = apr

    @property
    def dmg(self) -> int:
        return self._base.dmg // self._apr


class ResistantAdjustment(AdjustedMonster):
    def __init__(self, base: Monster):
        super().__init__(base)

    @property
    def hp(self) -> int:
        return self._base.hp // 2


# Load in statistical data
# --------------------------

fname = 'stats.json'

with open(fname, 'r') as fin:
    stats_json_list = json.load(fin)

stats = list(map(lambda obj: TierStat.from_json(obj), stats_json_list))


# Define and parse arguments
# ----------------------------

def tier_arg(arg: str) -> TierStat:
    for tier in stats:
        if tier.tier == arg:
            return tier

    raise argparse.ArgumentTypeError(f'Unrecognized tier: {arg}')


def level_arg(arg: str) -> TierStat:
    try:
        level = int(arg)

        for tier in stats:
            if level in tier.tier:
                return tier

        raise argparse.ArgumentTypeError(f'Level "{level}" not in range')

    except ValueError as ve:
        raise argparse.ArgumentTypeError(str(ve))


def tier_or_level_arg(arg: str) -> TierStat:
    if arg.isnumeric():
        return level_arg(arg)
    else:
        return tier_arg(arg)


def count_label_arg(arg: str) -> Count:
    arg = arg.lower()

    for label in Count.RANGES:
        if label.lower() == arg:
            return Count.from_label(label)

    raise argparse.ArgumentTypeError(f'Unrecognized count label: {arg}')


def count_num_arg(arg: str) -> Count:
    try:
        count = int(arg)
        return Count.from_int(count)

    except ValueError as ve:
        raise argparse.ArgumentTypeError(str(ve))


def count_arg(arg: str) -> Count:
    if arg.isnumeric():
        return count_num_arg(arg)
    else:
        return count_label_arg(arg)


def apr_arg(arg: str) -> int:
    if arg.isnumeric():
        return int(arg)

    arg = arg.lower()
    if arg == 'area':
        return 2
    elif arg == 'dot':  # Damage Over Time
        return 1


valid_stats_desc = ', '.join(map(lambda e: e.upper(), Monster.THREAT_STATS))
valid_tiers_desc = ', '.join(map(lambda e: e.tier.name, stats))
valid_count_desc = ', '.join(map(lambda e: e.upper(), filter(lambda e: Count.RANGES[e][2] is not None, Count.RANGES)))

parser = argparse.ArgumentParser(formatter_class=argparse.RawTextHelpFormatter,
    description=(
        f'STAT values:  {valid_stats_desc}\n'
        f'TIER values:  {valid_tiers_desc}\n'
        f'COUNT values: {valid_count_desc}\n'
        f'    (STAT, TIER, and COUNT values are case-insensitive)\n'
        ))
parser.add_argument('tier', metavar='tier|level', type=tier_or_level_arg,
    help="Monster's level (int) or TIER (see above)")
parser.add_argument('size', metavar='count', type=count_arg,
    help='Number of monsters to appear together (int or COUNT - see above)')
parser.add_argument('name', type=str, nargs='?',
    help='Monster name')
parser.add_argument('--good', '-g', metavar='STAT', action='append', default=[],
    help='Boost a STAT to good quality (may be specified multiple times)')
parser.add_argument('--poor', '-p', metavar='STAT', action='append', default=[],
    help='Reduce a STAT to poor quality (may be specified multiple times)')
parser.add_argument('--apr', '-a', type=apr_arg, default=1, help='Attacks per round. Must be an int, "area", or "dot" (damage over time)')
parser.add_argument('--resist', '-r', action='store_true', help='Flag to indicate significant defensive abilities or many resistances')

args = parser.parse_args()

# Make monster
# --------------

monster = AdjustedMonster(Monster(args.tier, args.size, args.name))

for stat in args.good:
    monster.good(stat)

for stat in args.poor:
    monster.poor(stat)

monster = AtksPerRoundAdjustment(monster, args.apr)

if args.resist:
    monster = ResistantAdjustment(monster)

print(monster)
