CHARACTERS = "ABCDEFGHJKLMNPQRSTUVWXYZ23456789"
import random
import msvcrt
def generate_ticket_id():
    def part():
        return "".join(random.choice(CHARACTERS) for _ in range(5))
    return f"{part()}-{part()}-{part()}-{part()}"

if __name__ == "__main__":
    ticket_id = generate_ticket_id()
    print(ticket_id)
    msvcrt.getch()