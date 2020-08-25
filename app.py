from datetime import datetime, timedelta
import pytz
# import argparse
import countries
import tzcache
import json
import re
import tkinter as tk
from tkinter import ttk
import geopy
import timezonefinder

class Clock():
    def __init__(self, parent, tz, row, col, city):
        self.tz = tz
        self.time = datetime.now(self.tz)
        self.label = tk.Label(parent, text=self.time.strftime('%H:%M:%S'), font=("Courier", 20))
        self.label.after(1000, self.tick)
        # self.label.grid(row=row, column=col, padx=30)
        self.city_label = tk.Label(parent, text=city + ', ' + self.time.strftime('%Y-%m-%d'))
        # self.city_label.grid(row=row+1, column=col, padx=30, pady=4)

    def tick(self):
        new_time = datetime.now(self.tz).strftime('%H:%M:%S')
        if new_time != self.time:
            self.time = new_time
            self.label.config(text=self.time)
        self.label.after(1000, self.tick)

class Timeutils():
    
    def __init__(self):
        self.window = tk.Tk()
        self.window.title("non-exe timeapp")
        self.window.update()
        self.label = tk.Label(self.window,text="Timeapp", font=("Courier", 23))
        self.label.grid(row=0, column=0)
        self.default = tzcache.cache
        self.scroll_bar = tk.Scrollbar(self.window, orient=tk.VERTICAL)
        self.default_clocks(1, 2)
        self.selected_place(5, 0)
        self.what_time(1, 0)
        self.new_clock(3, 0)
        self.window.mainloop()

    def new_clock(self, r, c):
        tk.Label(self.window, text="Enter Place").grid(row=r, column=c)
        intime = tk.Entry(self.window)
        intime.grid(row=r, column=c+1)
        tk.Button(self.window, text='Add Clock', command=lambda: self.add_clock(intime)).grid(row=r+1, column=c+1, pady=2)
        tk.Button(self.window, text='Remove Clock', command=lambda: self.remove_clock(intime)).grid(row=r+1, column=c, pady=2)

    def add_clock(self, inp):
        con = inp.get()
        tz = next((c for c in countries.countries if c['name'].lower() == con.lower()), None)
        if not tz is None:
            self.default[con] = tz['timezones'][0]
        elif tz is None:
            geolocator = geopy.geocoders.Nominatim(user_agent="timeapp")
            location = geolocator.geocode(con.lower())
            latitude, longitude = (location.latitude, location.longitude)

            tf = timezonefinder.TimezoneFinder()
            tz = tf.timezone_at(lng=longitude, lat=latitude)
            self.default[con] = tz

        inp.delete(0, tk.END)
        with open('./tzcache.py', 'w') as file:
            file.write('cache = ')
            json.dump(self.default, file)
        self.default_clocks(1, 2)
    
    def remove_clock(self, inp):
        con = inp.get()
        del self.default[con]
        with open('./tzcache.py', 'w') as file:
            file.write('cache = ')
            json.dump(self.default, file)
        self.default_clocks(1, 2)
            
    def default_clocks(self, r, c):
        
        tk.Label(self.window, text='Current Time', font=("Courier", 20)).grid(row=r, column=c, padx=30)
        
        self.scroll_bar.grid(column=c+1, rowspan=5, sticky=tk.N+tk.S) 
        lb = tk.Text(self.window, height=10, width=10, padx=10, yscrollcommand = self.scroll_bar.set)
        lb.config(font=('Verdana', 10))
        r += 1
        row = r
        for city in self.default:
            lb.insert(tk.END, Clock(self.window, pytz.timezone(self.default.get(city)), r, c, city).label.cget('text') + '\n')
            lb.insert(tk.END, city + ', ' + datetime.now(pytz.timezone(self.default.get(city))).strftime('%Y-%m-%d') + '\n\n')
            r += 2

        lb.grid(row=row, column=c, rowspan=5, columnspan=1, sticky=tk.N+tk.E+tk.S+tk.W)     
        self.scroll_bar.config(command=lb.yview)

    def selected_place(self, r, c):
        tk.Label(self.window, text="Enter Place").grid(row=r, column=0)
        inp = tk.Entry(self.window)
        inp.grid(row=r, column=c+1)
        time_text = tk.StringVar()
        city_text = tk.StringVar()
        tk.Button(self.window, text='Get Current Time', command=lambda: self.get_time(inp, time_text, city_text)).grid(row=r+1, column=c+1, pady=2)
        display_t = tk.Label(self.window, textvariable=time_text, font=("Courier", 20))
        display_t.grid(row=r+2, column=c+1)
        display_c = tk.Label(self.window, textvariable=city_text)
        display_c.grid(row=r+3, column=c+1, pady=4)

    def get_time(self, inp, time_text, city_text):    
        con = inp.get()
        tz = next((c for c in countries.countries if c['name'].lower() == con.lower()), None)
        if not tz is None:
            # Clock(self.window, pytz.timezone(tz['timezones'][0]), 7, 1, con)
            d = datetime.now(pytz.timezone(tz['timezones'][0]))            
            time_text.set(d.strftime('%H:%M:%S'))
            city_text.set(con)
        elif tz is None:
            time_text.set('Please enter a valid name!')
            geolocator = geopy.geocoders.Nominatim(user_agent="timeapp")
            location = geolocator.geocode(con.lower())
            latitude, longitude = (location.latitude, location.longitude)

            tf = timezonefinder.TimezoneFinder()
            tz = tf.timezone_at(lng=longitude, lat=latitude)
            d = datetime.now(pytz.timezone(tz))
            time_text.set(d.strftime('%H:%M:%S'))
            city_text.set(con)
            # Clock(self.window, pytz.timezone(tz), 7, 1, con)

        inp.delete(0, tk.END)

    def get_relative_time(self, r, c, intime):
        con = intime.get()
        match = re.match('[0-9]+:[0-9]+', con)
        if match:
            con_time = datetime.strptime(con, '%H:%M')
            src = datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%H:%M')
            src = datetime.strptime(src, '%H:%M')
            tk.Label(self.window, text='Relative Time', font=("Courier", 20)).grid(row=r-1, column=c, padx=30)
            self.scroll_bar = tk.Scrollbar(self.window, orient=tk.VERTICAL)
            self.scroll_bar.grid(row=r, column=c+1, rowspan=5, sticky=tk.N+tk.S) 
            lb = tk.Text(self.window, height=10, width=10, padx=10, yscrollcommand = self.scroll_bar.set)
            lb.config(font=('Verdana', 10))
            row = r
            for city in self.default:
                t = datetime.now(pytz.timezone(self.default.get(city)))
                tar = t.strftime('%H:%M')
                tar = datetime.strptime(tar, '%H:%M')
                diff = src - tar
                time_there = con_time - diff
                lb.insert(tk.END, time_there.time().strftime('%H:%M') + '\n')
                lb.insert(tk.END, city + '\n\n')
                # display_time = tk.Label(text=time_there.time().strftime('%H:%M'), font=("Courier", 20))
                # display_city = tk.Label(text=city)
                # lb.grid(row=r, column=c, padx=30)
                # display_city.grid(row=r+1, column=c, padx=30, pady=4)
                r += 2

            lb.grid(row=row, column=c, rowspan=5, columnspan=1, sticky=tk.N+tk.E+tk.S+tk.W)     
            self.scroll_bar.config(command=lb.yview)

    def what_time(self, r, c):
        tk.Label(self.window, text="Enter Time\nin hh:mm").grid(row=r, column=c)
        t = tk.StringVar()
        intime = ttk.Combobox(self.window, textvariable = t)
        intime['values'] = ('00:00', '00:30', '01:00', '01:30', '02:00', '02:30', '03:00', '03:30', '04:00', '04:30', '05:00', 
                            '05:30', '06:00', '06:30', '07:00', '07:30', '08:00', '08:30', '09:00', '09:30', '10:00', '10:30', 
                            '11:00', '11:30', '12:00', '12:30', '13:00', '13:30', '14:00', '14:30', '15:00', '15:30', '16:00', 
                            '16:30', '17:00', '17:30', '18:00', '18:30', '19:00', '19:30', '20:00', '20:30', '21:00', '21:30', 
                            '22:00', '22:30', '23:00', '23:30')
        intime.grid(row=r, column=c+1)
        tk.Button(self.window, text='Get Relative Time', command=lambda: self.get_relative_time(r+1, c+4, intime)).grid(row=r+1, column=c+1, pady=2)

def main():
    ta = Timeutils()

if __name__ == '__main__':
    main()


