import tkinter as tk
from tkinter import messagebox


class Room:
    def __init__(self, room_id, room_type, price_per_night):
        self.room_id = room_id
        self.room_type = room_type
        self.price_per_night = price_per_night
        self.is_booked = False
        self.booked_by = None  # Stores the user object who booked the room

    def calculate_price(self, nights):
        discount_rate = 0.05 if nights >= 5 else 0.0  # 5% discount for stays of 5+ nights
        tax_rate = 0.10  # 10% tax
        base_price = self.price_per_night * nights
        discount = base_price * discount_rate
        tax = (base_price - discount) * tax_rate
        total_price = base_price - discount + tax
        return total_price, discount, tax

    def book(self, user):
        self.is_booked = True
        self.booked_by = user

    def cancel_booking(self):
        self.is_booked = False
        self.booked_by = None


class User:
    def __init__(self, name, email, phone_number):
        self.name = name
        self.email = email
        self.phone_number = phone_number


class Hotel:
    def __init__(self, name):
        self.name = name
        self.rooms = []
        self.reservations = []

    def add_room(self, room):
        self.rooms.append(room)

    def show_available_rooms(self):
        available_rooms = [room for room in self.rooms if not room.is_booked]
        return available_rooms

    def book_room(self, room_id, user, nights):
        for room in self.rooms:
            if room.room_id == room_id:
                if not room.is_booked:
                    room.book(user)
                    total_price, discount, tax = room.calculate_price(nights)
                    self.reservations.append({"user": user, "room": room, "nights": nights})
                    return True, total_price, discount, tax
                else:
                    return False, None, None, None
        return False, None, None, None

    def cancel_reservation(self, room_id):
        for reservation in self.reservations:
            if reservation["room"].room_id == room_id:
                room = reservation["room"]
                room.cancel_booking()
                self.reservations.remove(reservation)
                return True
        return False

    def show_reservations(self):
        return self.reservations

    def calculate_revenue(self):
        total_revenue = 0
        for reservation in self.reservations:
            room = reservation["room"]
            nights = reservation["nights"]
            total_price, _, _ = room.calculate_price(nights)
            total_revenue += total_price
        return total_revenue

    def calculate_average_room_price(self):
        if not self.rooms:
            return 0
        total_price = sum(room.price_per_night for room in self.rooms)
        return total_price / len(self.rooms)


class HotelApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Hotel Reservation System")
        
        self.hotel = Hotel("Grand Plaza")
        self.hotel.add_room(Room("101", "Single", 100))
        self.hotel.add_room(Room("102", "Double", 150))
        self.hotel.add_room(Room("103", "Suite", 250))

        self.user = None

        # Main menu frame
        self.main_frame = tk.Frame(root)
        self.main_frame.pack()

        self.user_name_label = tk.Label(self.main_frame, text="Enter your name:")
        self.user_name_label.pack()

        self.user_name_entry = tk.Entry(self.main_frame)
        self.user_name_entry.pack()

        self.start_button = tk.Button(self.main_frame, text="Start", command=self.start)
        self.start_button.pack()

    def start(self):
        user_name = self.user_name_entry.get()
        if user_name:
            self.user = User(user_name, "", "")
            self.main_frame.destroy()
            self.show_menu()
        else:
            messagebox.showerror("Error", "Please enter your name.")

    def show_menu(self):
        self.menu_frame = tk.Frame(self.root)
        self.menu_frame.pack()

        tk.Button(self.menu_frame, text="Show Available Rooms", command=self.show_available_rooms).pack()
        tk.Button(self.menu_frame, text="Book a Room", command=self.book_room).pack()
        tk.Button(self.menu_frame, text="Cancel a Reservation", command=self.cancel_reservation).pack()
        tk.Button(self.menu_frame, text="Show Reservations", command=self.show_reservations).pack()
        tk.Button(self.menu_frame, text="Show Total Revenue", command=self.show_total_revenue).pack()
        tk.Button(self.menu_frame, text="Show Average Room Price", command=self.show_average_room_price).pack()
        tk.Button(self.menu_frame, text="Exit", command=self.root.quit).pack()

    def show_available_rooms(self):
        available_rooms = self.hotel.show_available_rooms()
        rooms_list = "\n".join([f"Room {room.room_id}: {room.room_type}, RM {room.price_per_night}/night"
                                for room in available_rooms])
        messagebox.showinfo("Available Rooms", rooms_list if rooms_list else "No rooms available.")

    def book_room(self):
        book_window = tk.Toplevel(self.root)
        book_window.title("Book a Room")

        tk.Label(book_window, text="Room ID:").pack()
        room_id_entry = tk.Entry(book_window)
        room_id_entry.pack()

        tk.Label(book_window, text="Number of nights:").pack()
        nights_entry = tk.Entry(book_window)
        nights_entry.pack()

        def book():
            room_id = room_id_entry.get()
            nights = int(nights_entry.get())
            success, total_price, discount, tax = self.hotel.book_room(room_id, self.user, nights)
            if success:
                messagebox.showinfo("Booking Successful", f"Room {room_id} booked for {nights} nights.\n"
                                                         f"Total Price: RM {total_price:.2f}\nDiscount: RM {discount:.2f}\nTax: RM {tax:.2f}")
                book_window.destroy()
            else:
                messagebox.showerror("Booking Failed", "Room not available or invalid room ID.")

        tk.Button(book_window, text="Book Room", command=book).pack()

    def cancel_reservation(self):
        cancel_window = tk.Toplevel(self.root)
        cancel_window.title("Cancel Reservation")

        tk.Label(cancel_window, text="Enter Room ID to cancel:").pack()
        room_id_entry = tk.Entry(cancel_window)
        room_id_entry.pack()

        def cancel():
            room_id = room_id_entry.get()
            success = self.hotel.cancel_reservation(room_id)
            if success:
                messagebox.showinfo("Cancellation Successful", f"Reservation for Room {room_id} has been cancelled.")
                cancel_window.destroy()
            else:
                messagebox.showerror("Cancellation Failed", f"No reservation found for Room {room_id}.")

        tk.Button(cancel_window, text="Cancel Reservation", command=cancel).pack()

    def show_reservations(self):
        reservations = self.hotel.show_reservations()
        if reservations:
            reservations_list = "\n".join([f"User: {reservation['user'].name}, Room: {reservation['room'].room_id}, Nights: {reservation['nights']}"
                                          for reservation in reservations])
            messagebox.showinfo("Current Reservations", reservations_list)
        else:
            messagebox.showinfo("Current Reservations", "No reservations found.")

    def show_total_revenue(self):
        revenue = self.hotel.calculate_revenue()
        messagebox.showinfo("Total Revenue", f"Total Revenue: RM {revenue:.2f}")

    def show_average_room_price(self):
        average_price = self.hotel.calculate_average_room_price()
        messagebox.showinfo("Average Room Price", f"Average Room Price: RM {average_price:.2f}")


if __name__ == "__main__":
    root = tk.Tk()
    app = HotelApp(root)
    root.mainloop()
