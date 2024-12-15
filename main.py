"""
Mega Millions Lottery Simulator

This module simulates playing the Mega Millions lottery game with configurable
number of tickets. It tracks wins, calculates probabilities, and provides
statistical analysis of the results.

The rules and odds are based on the official Mega Millions game:
https://www.megamillions.com/How-to-Play.aspx
"""

import logging
import os
import random
from dataclasses import dataclass
from typing import Tuple, List, TypeAlias, Dict

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class WinData:
    count: int = 0
    prize: int = 0
    total: int = 0
    odds: float = 0.0


TicketNumbers: TypeAlias = Tuple[List[int], int]
WinSummary: TypeAlias = Dict[str, WinData]


class MegaMillions:
    JACKPOT_AMOUNT = 1_000_000_000
    DEFAULT_TICKET_COST = 2.00
    WHITE_BALL_MAX = 71
    MEGA_BALL_MAX = 26

    def __init__(self) -> None:
        self.white_ball_range = range(1, self.WHITE_BALL_MAX)
        self.mega_ball_range = range(1, self.MEGA_BALL_MAX)
        self.ticket_cost = self.DEFAULT_TICKET_COST

    def generate_numbers(self) -> TicketNumbers:
        try:
            white_balls = sorted(random.sample(self.white_ball_range, 5))
            mega_ball = random.choice(self.mega_ball_range)
            return white_balls, mega_ball
        except ValueError as e:
            raise ValueError("Failed to generate numbers") from e

    @staticmethod
    def check_win(ticket: TicketNumbers, winning_numbers: TicketNumbers) -> int:
        white_matches = len(set(ticket[0]) & set(winning_numbers[0]))
        mega_matches = ticket[1] == winning_numbers[1]

        prize_structure = {
            (5, True): 1_000_000_000,
            (5, False): 1_000_000,
            (4, True): 10_000,
            (4, False): 500,
            (3, True): 200,
            (3, False): 10,
            (2, True): 10,
            (1, True): 4,
            (0, True): 2,
        }
        return prize_structure.get((white_matches, mega_matches), 0)

    @staticmethod
    def get_match_description(ticket: TicketNumbers, winning_numbers: TicketNumbers) -> str:
        white_matches = len(set(ticket[0]) & set(winning_numbers[0]))
        mega_matches = ticket[1] == winning_numbers[1]

        return (
            "Mega Ball only" if white_matches == 0 and mega_matches else
            f"{white_matches} number{'s' if white_matches != 1 else ''} + Mega Ball" if mega_matches else
            f"{white_matches} number{'s' if white_matches != 1 else ''}"
        )


def initialize_win_summary() -> WinSummary:
    return {
        "5 + Mega Ball": WinData(prize=MegaMillions.JACKPOT_AMOUNT, odds=1 / 302575350),
        "5": WinData(prize=1_000_000, odds=1 / 12607306),
        "4 + Mega Ball": WinData(prize=10_000, odds=1 / 931001),
        "4": WinData(prize=500, odds=1 / 38792),
        "3 + Mega Ball": WinData(prize=200, odds=1 / 14547),
        "3": WinData(prize=10, odds=1 / 606),
        "2 + Mega Ball": WinData(prize=10, odds=1 / 693),
        "1 + Mega Ball": WinData(prize=4, odds=1 / 89),
        "Mega Ball only": WinData(prize=2, odds=1 / 37)
    }


def print_summary(num_tickets: int, total_spent: float, total_won: int) -> None:
    print(f"\nResults Summary:\n"
          f"Total tickets purchased: {num_tickets}\n"
          f"Total spent: ${total_spent:.2f}\n"
          f"Total won: ${total_won:,}\n"
          f"Net profit/loss: ${(total_won - total_spent):,.2f}\n"
          f"Return on spend: {(total_won / total_spent * 100):.2f}%")


def print_probability_analysis(win_summary: WinSummary, num_tickets: int) -> None:
    print("\nProbability Analysis:")
    print("-" * 95)
    print(f"{'Match Type':<15} {'Expected':<10} {'Actual':<10} {'Diff %':<10} {'Within 2σ':<10}")
    print("-" * 95)

    for match_type, data in win_summary.items():
        _print_probability_row(match_type, data, num_tickets)


def _print_probability_row(match_type: str, data: WinData, num_tickets: int) -> None:
    expected = num_tickets * data.odds
    actual = data.count
    std_dev = (num_tickets * data.odds * (1 - data.odds)) ** 0.5
    diff_percent = ((actual - expected) / expected) * 100 if expected > 0 else 0
    within_2sigma = abs(actual - expected) <= 2 * std_dev

    print(f"{match_type:<15} {expected:>9.1f} {actual:>9} {diff_percent:>9.1f}% {'Yes' if within_2sigma else 'No':>9}")


def main() -> None:
    try:
        random.seed(os.urandom(8))
        logger.info("Starting Mega Millions simulation")

        game = MegaMillions()
        num_tickets = 10
        total_spent = num_tickets * game.ticket_cost
        total_won = 0
        win_summary = initialize_win_summary()

        winning_numbers = game.generate_numbers()
        print(f"\nMega Millions Simulator - {num_tickets} Tickets")
        print(f"Winning numbers: {winning_numbers[0]} Mega Ball: {winning_numbers[1]}")

        for _ in range(num_tickets):
            ticket = game.generate_numbers()
            prize = game.check_win(ticket, winning_numbers)
            total_won += prize

            if prize > 0:
                match_desc = game.get_match_description(ticket, winning_numbers)
                key = match_desc if "Mega Ball only" in match_desc else (
                    "5 + Mega Ball" if "5" in match_desc and "Mega Ball" in match_desc
                    else match_desc.split()[0] + (" + Mega Ball" if "Mega Ball" in match_desc else "")
                )
                win_summary[key].count += 1
                win_summary[key].total += prize

        print_summary(num_tickets, total_spent, total_won)
        print_probability_analysis(win_summary, num_tickets)

        logger.info("Simulation completed successfully")
    except Exception as e:
        logger.error("Simulation failed: %s", str(e))
        raise


if __name__ == "__main__":
    main()