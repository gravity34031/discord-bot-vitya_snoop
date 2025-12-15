import os
import asyncio
import traceback
from datetime import datetime, timedelta
from dotenv import load_dotenv
from mpmath import mp
import random
import json

import discord
from discord.ext import commands
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

# Настройки
mp.dps = 61
deerday_chance = 12
my_utc = 5



def add_hours_weekday(day: str, hour: int, minute: int, add_h: int):
    """
    day: 'mon'..'sun'
    hour, minute: время
    add_h: сколько часов добавить
    """
    weekdays = ['mon', 'tue', 'wed', 'thu', 'fri', 'sat', 'sun']
    base_weekday = weekdays.index(day)

    # Берём произвольную "базовую" неделю
    base_date = datetime(2025, 1, 6 + base_weekday, hour, minute)
    new_dt = base_date + timedelta(hours=add_h)

    return (
        weekdays[new_dt.weekday()],
        new_dt.hour,
        new_dt.minute
    )
    
def add_hours_monthday(month: int, day: int, hour: int, minute: int, add_h: int, year: int = 2025):
    base_dt = datetime(year, month, day, hour, minute)
    new_dt = base_dt + timedelta(hours=add_h)
    return (new_dt.month, new_dt.day, new_dt.hour, new_dt.minute)
    

def load_json_data(path):    
    with open(path, "r", encoding="utf-8") as f:
        schedules = json.load(f)
    res = []
    utc_offset = datetime.now().astimezone().utcoffset().total_seconds() // 3600
    for item in schedules:
        day, month = map(int, item["date"].split("-"))
        hour, minute = map(int, item["time"].split(":"))
        f_month, f_day, f_hour, f_minute = add_hours_monthday(month, day, hour, minute, add_h=utc_offset-my_utc)
        message = item["message"]
        image = item["image"]
        res.append({"day": f_day, "month": f_month, "hour": f_hour, "minute": f_minute, "message": message, "image": image})
    return res
    

class Schedule:
    def __init__(self, bot, channel_name='основной', day="fri", hour=10, minute=0):
        self.bot = bot
        self.channel = discord.utils.get(bot.guild.text_channels, name=channel_name)
        self.media_path = 'media/friday/'
        
        utc_offset = datetime.now().astimezone().utcoffset().total_seconds() // 3600
        fin_day, fin_hour, fin_minute = add_hours_weekday(day, hour, minute, add_h=utc_offset-my_utc)
        
        self.day = fin_day
        self.hour = fin_hour
        self.minute = fin_minute
        self.scheduler = AsyncIOScheduler()
        self._started = False  # <--- repeat control
        
    def start(self):
        if self._started:
            print("Планировщик уже запущен. Пропускаем повторный запуск.")
            return
        self._started = True
        print("\nЗапуск планировщика...")
        # start friday
        day, hour, minute = self.day, self.hour, self.minute
        # self.scheduler.add_job(self._post_photo, CronTrigger(day_of_week=day, hour=hour, minute=minute))  # Локальное время
        job = self.scheduler.add_job(
            self._post_photo, CronTrigger(hour=hour, minute=minute),
            id=f"job_{day}_{hour}_{minute}",
            replace_existing=True
            )  # Локальное время
        self.scheduler.start()
        print(f"Job added. Next run at: {job.next_run_time}", flush=True)
        print(f"Планировщик запущен. на {day} в {hour}:{minute}\n")
        
        # start custom schedule
        schedules = load_json_data(os.path.join(self.media_path, "data.json"))
        print("Запуск кастомного планировщика...")
        print(schedules)
        print("Загрузка следующего расписания:", *schedules)
        for item in schedules:
            trigger = CronTrigger(month=item["month"], day=item["day"], hour=item["hour"], minute=item["minute"])
            job = self.scheduler.add_job(
                self._post_custom_photo, trigger,
                kwargs= {"item": item},
                id=f"customjob_{item['day']}_{item['month']}_{item['hour']}_{item['minute']}",
                replace_existing=True
            )
            print(f"Job added. Next run at: {job.next_run_time}", flush=True)
        
        
        
    async def _post_photo(self):
        try:
            now = datetime.now()
            day, month, year = now.day, now.month, now.year
            
            # december deerday
            if month == 12:
                print("Оленятница!")
                message = "Сегодня оленятница!"
                rand_num = random.choice([1, 2])
                photo_name = f'deerday{rand_num}.png'
                photo_path = os.path.join(self.media_path, photo_name)
                await self._send_photo(photo_path, message)
                return
            
            pi_modifier = int(str(mp.pi)[14:][day])
            sum_ = day + month + year + pi_modifier
            rand_num = sum_ % deerday_chance

            if rand_num == min(5, deerday_chance - 1):
                print("Лосятница!")
                message = "Сегодня лосятница!"
                photo_path = os.path.join(self.media_path, 'moose.jpg')
            else:
                print("Свинятница!")
                message = "Сегодня пятница!"
                photo_path = os.path.join(self.media_path, 'pigday.jpg')

            await self._send_photo(photo_path, message)

        except Exception as e:
            print(f"Ошибка в post_photo: {e}\n{traceback.format_exc()}")
       

    async def _post_custom_photo(self, item:dict):
        try:
            message = item["message"]
            image = item["image"]
            photo_path = os.path.join(self.media_path, image)
            await self._send_photo(photo_path, message)
        except Exception as e:
            print(f"Ошибка в _post_custom_photo: {e}")
        

    async def _send_photo(self, photo_path: str, message: str): 
        try:
            channel = self.channel
            if channel:
                file = discord.File(photo_path)
                await channel.send(content=f"@everyone, {message}", file=file)
                print("Photo sent successfully.")
            else:
                print("Channel not found.")
        except Exception as e:
            print(f"Ошибка при отправке фото: {e}\n{traceback.format_exc()}")
            
            
            
                   
