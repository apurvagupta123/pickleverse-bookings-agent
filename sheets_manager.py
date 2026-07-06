"""Google Sheets Manager for LiveKit Pickleball Booking Agent"""

import os
import json
import base64
from google.oauth2.service_account import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from datetime import datetime
from typing import List, Dict, Optional

class GoogleSheetsManager:
      """Manages all interactions with Google Sheets for pickleball court bookings."""

    def __init__(self, spreadsheet_id: str, sheet_name: str = "Sheet1"):
              """Initialize Google Sheets Manager with credentials."""
              self.spreadsheet_id = spreadsheet_id
              self.sheet_name = sheet_name
              self.service = self._initialize_service()

    def _initialize_service(self):
              """Initialize Google Sheets API service using service account credentials."""
              # Get credentials from environment variable (base64 encoded JSON)
              credentials_json = os.getenv("GOOGLE_SHEETS_CREDENTIALS")

        if not credentials_json:
                      raise ValueError("GOOGLE_SHEETS_CREDENTIALS environment variable not set")

        # Decode base64 credentials
        credentials_data = json.loads(base64.b64decode(credentials_json))

        # Create credentials object
        credentials = Credentials.from_service_account_info(
                      credentials_data,
                      scopes=['https://www.googleapis.com/auth/spreadsheets']
        )

        # Build service
        service = build('sheets', 'v4', credentials=credentials)
        return service

    def add_booking(self, booking_data: Dict) -> bool:
              """Add a new booking to the Google Sheet."""
              try:
                            # Prepare row data with all required columns
                            row = [
                                              booking_data.get('customer_name', ''),
                                              booking_data.get('phone_number', ''),
                                              booking_data.get('booking_date', ''),
                                              booking_data.get('booking_time', ''),
                                              booking_data.get('number_of_courts', ''),
                                              booking_data.get('location', ''),
                                              booking_data.get('preference', ''),
                                              booking_data.get('special_requests', ''),
                                              booking_data.get('price_per_court', 800),
                                              booking_data.get('total_price', ''),
                                              booking_data.get('booking_status', 'Pending'),
                                              datetime.now().isoformat()  # Timestamp
                            ]

            # Append row to sheet
                  self.service.spreadsheets().values().append(
                                    spreadsheetId=self.spreadsheet_id,
                                    range=f"{self.sheet_name}!A1",
                                    valueInputOption="RAW",
                                    body={"values": [row]}
                  ).execute()

            return True
except Exception as e:
            print(f"Error adding booking: {str(e)}")
            return False

    def check_availability(self, booking_date: str, booking_time: str, location: str) -> bool:
              """Check if courts are available for the requested date, time, and location."""
        try:
                      # Get all bookings from sheet
                      result = self.service.spreadsheets().values().get(
                                        spreadsheetId=self.spreadsheet_id,
                                        range=f"{self.sheet_name}!A2:L"
                      ).execute()

            rows = result.get('values', [])

            # Check for conflicting bookings (same date, time, and location with 'Confirmed' status)
            for row in rows:
                              if len(row) >= 12:
                                                    if (row[2] == booking_date and 
                                                                                row[3] == booking_time and 
                                                                                row[5] == location and
                                                                                row[10] == 'Confirmed'):
                                                                                                          return False

                                            return True
except Exception as e:
            print(f"Error checking availability: {str(e)}")
            return True  # Assume available if error occurs

    def get_bookings(self, filters: Optional[Dict] = None) -> List[Dict]:
              """Retrieve bookings from the sheet with optional filtering."""
        try:
                      result = self.service.spreadsheets().values().get(
                                        spreadsheetId=self.spreadsheet_id,
                                        range=f"{self.sheet_name}!A2:L"
                      ).execute()

            rows = result.get('values', [])
            bookings = []

            headers = [
                              'customer_name', 'phone_number', 'booking_date', 'booking_time',
                              'number_of_courts', 'location', 'preference', 'special_requests',
                              'price_per_court', 'total_price', 'booking_status', 'timestamp'
            ]

            for row in rows:
                              if len(row) >= 12:
                                                    booking = dict(zip(headers, row))

                    # Apply filters if provided
                    if filters:
                                              if not self._apply_filters(booking, filters):
                                                                            continue

                                          bookings.append(booking)

            return bookings
except Exception as e:
            print(f"Error retrieving bookings: {str(e)}")
            return []

    def update_booking_status(self, booking_index: int, new_status: str) -> bool:
              """Update the booking status (Pending, Confirmed, Cancelled)."""
        try:
                      # Update status column (column K, index 10)
                      self.service.spreadsheets().values().update(
                                        spreadsheetId=self.spreadsheet_id,
                                        range=f"{self.sheet_name}!K{booking_index + 2}",
                                        valueInputOption="RAW",
                                        body={"values": [[new_status]]}
                      ).execute()

            return True
except Exception as e:
            print(f"Error updating booking status: {str(e)}")
            return False

    def _apply_filters(self, booking: Dict, filters: Dict) -> bool:
              """Apply filters to a booking record."""
        for key, value in filters.items():
                      if booking.get(key) != value:
                                        return False
                                return True
