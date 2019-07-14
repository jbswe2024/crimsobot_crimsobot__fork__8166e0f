import random
from collections import Counter
from datetime import datetime
from typing import List, Tuple

from crimsobot.utils import tools as c
from crimsobot.utils.tools import CrimsoBOTUser


def emojistring() -> str:
    emojis = []
    for line in open(c.clib_path_join('games', 'emojilist.txt'), encoding='utf-8', errors='ignore'):
        line = line.replace('\n', '')
        emojis.append(line)

    emoji_string = random.sample(emojis, random.randint(3, 5))

    return ' '.join(emoji_string)


def tally(ballots: List[str]) -> Tuple[str, int]:
    counter = Counter(sorted(ballots))
    winner = counter.most_common(1)[0]

    return winner


def winner_list(winners: List[str]) -> str:
    if len(winners) > 1:
        winners_ = ', '.join(winners[:-1])
        winners_ = winners_ + ' & ' + winners[-1]  # winner, winner & winner
    else:
        winners_ = winners[0]

    return winners_


def get_story() -> str:
    story = open(
        c.clib_path_join('games', 'madlibs.txt'),
        encoding='utf-8',
        errors='ignore'
    ).readlines()

    story = [line[:-1] for line in story]
    story = [line.replace('\\n', '\n') for line in story]

    return random.choice(story)


def get_keys(format_string: str) -> List[str]:
    """format_string is a format string with embedded dictionary keys.
    Return a set containing all the keys from the format string."""

    keys = []
    end = 0
    repetitions = format_string.count('{')
    for _ in range(repetitions):
        start = format_string.find('{', end) + 1  # pass the '{'
        end = format_string.find('}', start)
        key = format_string[start:end]
        keys.append(key)  # may add duplicates

    # find indices of marked tags (to be used more than once)
    ind = [i for i, s in enumerate(keys) if '#' in s]

    # isolate the marked tags and keep one instance each
    mults = []
    for ele in ind:
        mults.append(keys[ele])
    mults = list(set(mults))

    # delete all marked tags from original list
    for ele in sorted(ind, reverse=True):
        del keys[ele]

    # ...and add back one instance each
    keys = keys + mults

    return keys


def win(user_id: int, amount: float) -> None:
    # make sure amount is numeric
    try:
        if not isinstance(amount, float):
            raise ValueError
    except ValueError:
        amount = float(amount)

    # get user
    user = CrimsoBOTUser.get(user_id)

    # add coin
    user.coin += amount

    # force round
    user.coin = round(user.coin, 2)
    user.save()


def daily(user_id: int, lucky_number: int) -> str:
    # fetch user
    user = CrimsoBOTUser.get(user_id)

    # get current time
    now = datetime.utcnow()

    # arbitrary "last date collected" and reset time (midnight UTC)
    reset = datetime(1969, 7, 20, 0, 0, 0)  # ymd required but will not be used

    last = user.daily

    # check if dates are same
    if last.strftime('%Y-%m-%d') == now.strftime('%Y-%m-%d'):
        hours = (reset - now).seconds / 3600
        minutes = (hours - int(hours)) * 60
        award_string = 'Daily award resets at midnight UTC, {}h{}m from now.'.format(int(hours), int(minutes + 1))
    else:
        winning_number = random.randint(1, 100)
        if winning_number == lucky_number:
            daily_award = 500
            jackpot = '**JACKPOT!** '
        else:
            daily_award = 10
            jackpot = 'The winning number this time was **{}**, but no worries: '.format(
                winning_number) if lucky_number != 0 else ''

        # update daily then save
        user.daily = now
        user.save()

        # update their balance now (will repoen and reclose user)
        win(user_id, daily_award)
        award_string = '{}You have been awarded your daily **\u20A2{:.2f}**!'.format(jackpot, daily_award)

    return award_string


def check_balance(user_id: int) -> float:
    """ input: discord user ID
       output: float"""

    user = CrimsoBOTUser.get(user_id)
    # force round and close
    return round(user.coin, 2)


def guess_economy(n: int) -> Tuple[float, float]:
    """ input: integer
       output: float, float"""

    # winnings for each n=0,...,20
    winnings = [0, 7, 2, 4, 7, 11, 15, 20, 25, 30, 36, 42, 49, 56, 64, 72, 80, 95, 120, 150, 200]

    # variables for cost function
    const = 0.0095  # dampener multiplier
    sweet = 8  # sweet spot for guess
    favor = 1.3  # favor to player (against house) at sweet spot

    # conditionals
    if n > 2:
        cost = winnings[n] / n - (-const * (n - sweet) ** 2 + favor)
    else:
        cost = 0.00

    return winnings[n], cost


def guess_luck(user_id: int, n: int, win: bool) -> None:
    user = CrimsoBOTUser.get(user_id)

    user.guess_plays += 1
    user.guess_expected += 1 / n
    user.guess_wins += win
    user.guess_luck = user.guess_wins / user.guess_expected

    user.save()


def guess_luck_balance(user_id: int) -> Tuple[float, int]:
    user = CrimsoBOTUser.get(user_id)

    return user.guess_luck, user.guess_plays


def guesslist() -> str:
    output = [' n  ·   cost   ·   payout',
              '·························']
    for i in range(2, 21):
        spc = '\u2002' if i < 10 else ''
        w, c = guess_economy(i)
        output.append('{}{:>d}  ·  \u20A2{:>5.2f}  ·  \u20A2{:>6.2f}'.format(spc, i, c, w))

    return '\n'.join(output)

# def slot_helper(bets: int) -> str:
#     machine = [':arrow_lower_right:│:blank:│:blank:│:blank:│:five:\n' +
#                ':arrow_two:│11│12│13│:two:\n' +
#                ':arrow_right:│21│22│23│:one:\n' +
#                ':arrow_three:│31│32│33│:three:\n' +
#                ':arrow_upper_right:│:blank:│:blank:│:blank:│:four:']
