"""
Full Library Management System (CLI + JSON + 12 Menu Options)
Coded By: Syed Asad Hussain Kazmi
"""

import json
import os
from datetime import datetime, timedelta

BOOKS_FILE = "books.json"
MEMBERS_FILE = "members.json"
DATE_FORMAT = "%Y-%m-%d"
DEFAULT_BORROW_DAYS = 14


def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def input_non_empty(prompt: str) -> str:
    while True:
        s = input(prompt).strip()
        if s:
            return s
        print("Input cannot be empty.")


class Book:
    def __init__(self, book_id, title, author, total_copies=1):
        self.book_id = book_id
        self.title = title
        self.author = author
        self.total_copies = total_copies
        self.borrowed_records = []  # list of dicts

    @property
    def available_copies(self):
        return self.total_copies - len(self.borrowed_records)

    def to_dict(self):
        return {
            "book_id": self.book_id,
            "title": self.title,
            "author": self.author,
            "total_copies": self.total_copies,
            "borrowed_records": [
                {
                    "member_id": r["member_id"],
                    "borrow_date": r["borrow_date"].strftime(DATE_FORMAT),
                    "due_date": r["due_date"].strftime(DATE_FORMAT),
                }
                for r in self.borrowed_records
            ],
        }

    @classmethod
    def from_dict(cls, d):
        b = cls(d["book_id"], d["title"], d["author"], d["total_copies"])
        for r in d.get("borrowed_records", []):
            b.borrowed_records.append(
                {
                    "member_id": r["member_id"],
                    "borrow_date": datetime.strptime(r["borrow_date"], DATE_FORMAT),
                    "due_date": datetime.strptime(r["due_date"], DATE_FORMAT),
                }
            )
        return b


class Member:
    def __init__(self, member_id, name, contact=""):
        self.member_id = member_id
        self.name = name
        self.contact = contact
        self.borrowed_books = []  # list of dicts

    def to_dict(self):
        return {
            "member_id": self.member_id,
            "name": self.name,
            "contact": self.contact,
            "borrowed_books": self.borrowed_books,
        }

    @classmethod
    def from_dict(cls, d):
        m = cls(d["member_id"], d["name"], d.get("contact", ""))
        m.borrowed_books = d.get("borrowed_books", [])
        return m


class Library:
    def __init__(self):
        self.books = {}
        self.members = {}
        self.load_data()
        if not self.books:
            self._add_sample_books()
        if not self.members:
            self._add_sample_members()

    # ---------- Persistence ----------
    def load_data(self):
        if os.path.exists(BOOKS_FILE):
            with open(BOOKS_FILE, "r", encoding="utf-8") as f:
                for b in json.load(f):
                    self.books[b["book_id"]] = Book.from_dict(b)

        if os.path.exists(MEMBERS_FILE):
            with open(MEMBERS_FILE, "r", encoding="utf-8") as f:
                for m in json.load(f):
                    self.members[m["member_id"]] = Member.from_dict(m)

    def save_data(self):
        with open(BOOKS_FILE, "w", encoding="utf-8") as f:
            json.dump([b.to_dict() for b in self.books.values()], f, indent=2)
        with open(MEMBERS_FILE, "w", encoding="utf-8") as f:
            json.dump([m.to_dict() for m in self.members.values()], f, indent=2)

    # ---------- Helper Methods ----------
    def _generate_book_id(self):
        num = len(self.books) + 1
        return f"B{num:04d}"

    def _generate_member_id(self):
        num = len(self.members) + 1
        return f"M{num:04d}"

    def _add_sample_books(self):
        samples = [
            ("Python Basics", "John Smith", 4),
            ("Data Structures", "Mark Allen", 3),
            ("AI Fundamentals", "Andrew Ng", 2),
            ("Machine Learning", "Tom Mitchell", 5),
            ("Cybersecurity 101", "Jane Doe", 3),
            ("Database Systems", "Ramakrishnan", 2),
            ("Java Programming", "James Gosling", 3),
            ("Operating Systems", "Silberschatz", 2),
            ("Networks Explained", "Tanenbaum", 2),
            ("Cloud Computing", "Rajkumar Buyya", 3),
        ]
        for title, author, copies in samples:
            book = Book(self._generate_book_id(), title, author, copies)
            self.books[book.book_id] = book
        self.save_data()

    def _add_sample_members(self):
        names = [
            "Ali Khan", "Sara Ahmed", "Syed Asad", "Fahad Ali", "Ayesha Bano",
            "Bilal Shaikh", "Hassan Raza", "Usman Tariq", "Zainab Fatima",
            "Nida Noor", "Ahmed Ali", "Maha Iqbal"
        ]
        for name in names:
            m = Member(self._generate_member_id(), name, f"{name.split()[0].lower()}@email.com")
            self.members[m.member_id] = m
        self.save_data()

    # ---------- Core Functionalities ----------
    def add_book(self, title, author, total_copies=1):
        book = Book(self._generate_book_id(), title, author, total_copies)
        self.books[book.book_id] = book
        self.save_data()
        print(f"Book '{title}' added successfully!")

    def add_member(self, name, contact):
        member = Member(self._generate_member_id(), name, contact)
        self.members[member.member_id] = member
        self.save_data()
        print(f"Member '{name}' added successfully!")

    def borrow_book(self, member_id, book_id, days=DEFAULT_BORROW_DAYS):
        member = self.members.get(member_id)
        book = self.books.get(book_id)
        if not member or not book:
            print("❌ Member or Book not found!")
            return
        if book.available_copies <= 0:
            print("❌ No available copies.")
            return
        borrow_date = datetime.now()
        due_date = borrow_date + timedelta(days=days)
        book.borrowed_records.append({
            "member_id": member_id,
            "borrow_date": borrow_date,
            "due_date": due_date,
        })
        member.borrowed_books.append({
            "book_id": book_id,
            "borrow_date": borrow_date.strftime(DATE_FORMAT),
            "due_date": due_date.strftime(DATE_FORMAT),
        })
        self.save_data()
        print(f"✅ '{book.title}' borrowed by {member.name} till {due_date.strftime(DATE_FORMAT)}.")

    def return_book(self, member_id, book_id):
        member = self.members.get(member_id)
        book = self.books.get(book_id)
        if not member or not book:
            print("❌ Member or Book not found!")
            return
        book.borrowed_records = [r for r in book.borrowed_records if r["member_id"] != member_id]
        member.borrowed_books = [r for r in member.borrowed_books if r["book_id"] != book_id]
        self.save_data()
        print(f"✅ '{book.title}' returned successfully.")

    def search_book(self, keyword):
        print(f"\nSearch results for '{keyword}':")
        for b in self.books.values():
            if keyword.lower() in b.title.lower() or keyword.lower() in b.author.lower():
                print(f"{b.book_id} - {b.title} by {b.author} (Available: {b.available_copies})")

    def remove_book(self, book_id):
        if book_id in self.books:
            del self.books[book_id]
            self.save_data()
            print("Book removed successfully.")
        else:
            print("Book not found!")

    def view_all_books(self):
        print("\nAll Books:")
        print(f"{'BookID':<8} | {'Title':<25} | {'Author':<20} | {'Avail':<6} | {'Total':<5}")
        print("-" * 70)
        for b in self.books.values():
            print(f"{b.book_id:<8} | {b.title:<25} | {b.author:<20} | {b.available_copies:<6} | {b.total_copies:<5}")

    def view_all_members(self):
        print("\nAll Members:")
        print(f"{'MemberID':<8} | {'Name':<20} | {'Contact':<25}")
        print("-" * 60)
        for m in self.members.values():
            print(f"{m.member_id:<8} | {m.name:<20} | {m.contact:<25}")

    def view_borrow_summary(self):
        print("\nBorrow Summary (Member wise):")
        print(f"{'MemberID':<8} | {'Name':<20} | {'Borrowed Books':<5}")
        print("-" * 45)
        for m in self.members.values():
            print(f"{m.member_id:<8} | {m.name:<20} | {len(m.borrowed_books):<5}")

    def view_member_books(self, member_id):
        m = self.members.get(member_id)
        if not m:
            print("Member not found.")
            return
        print(f"\nBooks borrowed by {m.name}:")
        if not m.borrowed_books:
            print("No books borrowed.")
            return
        for b in m.borrowed_books:
            print(f"BookID: {b['book_id']} | Borrowed: {b['borrow_date']} | Due: {b['due_date']}")


# ---------- CLI ----------
def main_menu():
    lib = Library()
    while True:
        print("\n========== LIBRARY MANAGEMENT ==========")
        print("1. View All Books")
        print("2. View All Members")
        print("3. Add New Book")
        print("4. Add New Member")
        print("5. Borrow Book")
        print("6. Return Book")
        print("7. Search Book")
        print("8. Remove Book")
        print("9. View Member Borrowed Books")
        print("10. View Borrow Summary (All Members)")
        print("11. Save Data")
        print("12. Exit")
        print("========================================")

        choice = input("Enter choice: ").strip()
        clear_screen()

        if choice == "1":
            lib.view_all_books()
        elif choice == "2":
            lib.view_all_members()
        elif choice == "3":
            title = input_non_empty("Enter book title: ")
            author = input_non_empty("Enter author name: ")
            copies = int(input("Total copies: ") or 1)
            lib.add_book(title, author, copies)
        elif choice == "4":
            name = input_non_empty("Enter member name: ")
            contact = input_non_empty("Enter contact/email: ")
            lib.add_member(name, contact)
        elif choice == "5":
            mem = input_non_empty("Enter Member ID: ")
            book = input_non_empty("Enter Book ID: ")
            lib.borrow_book(mem, book)
        elif choice == "6":
            mem = input_non_empty("Enter Member ID: ")
            book = input_non_empty("Enter Book ID: ")
            lib.return_book(mem, book)
        elif choice == "7":
            keyword = input_non_empty("Enter keyword: ")
            lib.search_book(keyword)
        elif choice == "8":
            book = input_non_empty("Enter Book ID to remove: ")
            lib.remove_book(book)
        elif choice == "9":
            mem = input_non_empty("Enter Member ID: ")
            lib.view_member_books(mem)
        elif choice == "10":
            lib.view_borrow_summary()
        elif choice == "11":
            lib.save_data()
            print("Data saved successfully.")
        elif choice == "12":
            lib.save_data()
            print("Goodbye!")
            break
        else:
            print("Invalid option.")

        input("\nPress Enter to continue...")
        clear_screen()


if __name__ == "__main__":
    main_menu()