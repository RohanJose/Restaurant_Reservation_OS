class BookingManager:
    def __init__(self):
        self.tables = {
            1: {"total_seats": 4, "booked_seats": []},
            2: {"total_seats": 6, "booked_seats": []},
            3: {"total_seats": 2, "booked_seats": []},
        }
        self.bookings = [] 

    def get_available_seats(self, date, start_time, end_time, num_guests, algorithm):
        available_seats = []
        for table_id, info in self.tables.items():
            total_seats = info["total_seats"]
            booked_seats = len(info["booked_seats"])
            remaining_seats = total_seats - booked_seats

            if remaining_seats >= num_guests:
                available_seats.append({
                    "table_id": table_id,
                    "remaining_seats": remaining_seats,
                    "total_seats": total_seats,
                })

        if algorithm == "first_fit":
            return self.first_fit(available_seats, num_guests)
        elif algorithm == "best_fit":
            return self.best_fit(available_seats, num_guests)

    def first_fit(self, available_seats, num_guests):
        for seat in available_seats:
            if seat["remaining_seats"] >= num_guests:
                seat["chosen_seats"] = num_guests
                seat["not_chosen_seats"] = seat["remaining_seats"] - num_guests
                return seat  
        return None

    def best_fit(self, available_seats, num_guests):
        best_fit_seat = None
        for seat in available_seats:
            if seat["remaining_seats"] >= num_guests:
                if best_fit_seat is None or seat["remaining_seats"] < best_fit_seat["remaining_seats"]:
                    best_fit_seat = seat
        if best_fit_seat:
            best_fit_seat["chosen_seats"] = num_guests
            best_fit_seat["not_chosen_seats"] = best_fit_seat["remaining_seats"] - num_guests
        return best_fit_seat


    def book_seat(self, table_id, date, start_time, end_time, num_guests):
        if table_id in self.tables:
            table_info = self.tables[table_id]
            if len(table_info["booked_seats"]) + num_guests <= table_info["total_seats"]:
                # Update booked seats
                table_info["booked_seats"].extend([{
                    "date": date,
                    "start_time": start_time,
                    "end_time": end_time,
                    "num_guests": num_guests,
                }] * num_guests)  # Add number of guests booked
                self.bookings.append({
                "table_id": table_id,
                "date": date,
                "start_time": start_time,
                "end_time": end_time,
                "num_guests": num_guests,
                "remaining_seats": self.tables[table_id]["total_seats"] - len(self.tables[table_id]["booked_seats"]),
            })
                return True  
        return False  

    def get_bookings_summary(self):
        return self.bookings
    

    def get_not_chosen_tables(self):
        not_chosen_tables = []
        for table_id, info in self.tables.items():
            if not info["booked_seats"]: 
                not_chosen_tables.append({
                    "table_id": table_id,
                    "total_seats": info["total_seats"],
                    "booked_seats": 0,
                    "remaining_seats": info["total_seats"],
                })
            else:
                booked_count = len(info["booked_seats"])
                not_chosen_tables.append({
                    "table_id": table_id,
                    "total_seats": info["total_seats"],
                    "booked_seats": booked_count,
                    "remaining_seats": info["total_seats"] - booked_count,
                })
        return not_chosen_tables